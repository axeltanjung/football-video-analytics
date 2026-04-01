from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Optional, Callable

import cv2
import numpy as np

from app.config import BATCH_SIZE, OUTPUT_DIR
from app.models.schemas import FrameDetections, MatchAnalytics
from app.pipeline.video_ingestion import VideoIngestion
from app.pipeline.detection import ObjectDetector
from app.pipeline.tracking import ObjectTracker
from app.pipeline.team_classifier import TeamClassifier
from app.pipeline.event_detection import EventDetector
from app.pipeline.analytics import AnalyticsEngine
from app.pipeline.heatmap import HeatmapGenerator

logger = logging.getLogger(__name__)


class MatchPipeline:
    def __init__(
        self,
        match_id: str,
        video_path: str,
        progress_callback: Optional[Callable] = None,
    ):
        self.match_id = match_id
        self.video_path = video_path
        self.progress_callback = progress_callback

        self.ingestion = VideoIngestion(video_path)
        self.detector = ObjectDetector()
        self.tracker = ObjectTracker()
        self.team_classifier = TeamClassifier()
        self.event_detector = EventDetector()
        self.analytics = AnalyticsEngine(match_id, fps=self.ingestion.metadata.get("fps", 30.0))
        self.heatmap_gen = HeatmapGenerator()

    async def run(self) -> MatchAnalytics:
        metadata = self.ingestion.metadata
        total_frames = metadata["total_frames"]
        fps = metadata["fps"]
        width = metadata["width"]
        height = metadata["height"]

        logger.info(f"Starting pipeline for match {self.match_id}")
        logger.info(f"Video: {total_frames} frames, {fps} fps, {width}x{height}")

        frame_batch = []
        frame_meta = []
        processed = 0
        calibration_done = False

        for frame_idx, timestamp, frame in self.ingestion.extract_frames():
            frame_batch.append(frame)
            frame_meta.append((frame_idx, timestamp))

            if len(frame_batch) >= BATCH_SIZE:
                await self._process_batch(frame_batch, frame_meta, width, height)
                processed += len(frame_batch)

                if not calibration_done and processed > 50:
                    calibration_done = True

                if self.progress_callback:
                    progress = min(processed / max(total_frames, 1) * 100, 99)
                    await self.progress_callback(self.match_id, "processing", progress)

                frame_batch.clear()
                frame_meta.clear()

                await asyncio.sleep(0)

        if frame_batch:
            await self._process_batch(frame_batch, frame_meta, width, height)

        analytics = self.analytics.compute_analytics()

        all_positions = self.analytics.generate_heatmap_data()
        if all_positions:
            heatmap_path = str(OUTPUT_DIR / f"{self.match_id}_heatmap.png")
            self.heatmap_gen.save(all_positions, width, height, heatmap_path)
            logger.info(f"Heatmap generated: {heatmap_path}")

        if self.progress_callback:
            await self.progress_callback(self.match_id, "completed", 100)

        logger.info(
            f"Pipeline complete: {analytics.total_frames_processed} frames, "
            f"{len(analytics.events)} events detected"
        )

        return analytics

    async def _process_batch(
        self,
        frames: list[np.ndarray],
        meta: list[tuple[int, float]],
        width: int,
        height: int,
    ):
        all_detections = self.detector.detect_batch(frames)

        for i, (frame, detections) in enumerate(zip(frames, all_detections)):
            frame_idx, timestamp = meta[i]
            tracked = self.tracker.update(detections, frame)

            players = [t for t in tracked if t.class_name == "player"]
            ball = next((t for t in tracked if t.class_name == "ball"), None)

            if not self.team_classifier.is_calibrated and len(players) >= 6:
                self.team_classifier.calibrate(frame, players)

            if self.team_classifier.is_calibrated:
                teams = self.team_classifier.classify_batch(frame, players)
                for p, team in zip(players, teams):
                    p.team_id = team
            else:
                for p in players:
                    p.team_id = hash(p.track_id) % 2

            frame_data = FrameDetections(
                frame_number=frame_idx,
                timestamp=timestamp,
                players=players,
                ball=ball,
                raw_detections=detections,
            )

            events = self.event_detector.detect_events(frame_data)
            _, possession_team = self.event_detector.get_possession_state()

            self.analytics.process_frame(frame_data, possession_team, events)


class AnnotatedVideoWriter:
    TEAM_COLORS = {
        0: (0, 120, 255),
        1: (255, 100, 0),
    }
    BALL_COLOR = (0, 255, 0)

    def __init__(self, output_path: str, fps: float, width: int, height: int):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        self.output_path = output_path

    def write_frame(self, frame: np.ndarray, frame_data: FrameDetections):
        annotated = frame.copy()

        for player in frame_data.players:
            bbox = player.bbox
            team = player.team_id or 0
            color = self.TEAM_COLORS.get(team, (200, 200, 200))

            cv2.rectangle(
                annotated,
                (int(bbox.x1), int(bbox.y1)),
                (int(bbox.x2), int(bbox.y2)),
                color,
                2,
            )

            label = f"P{player.track_id}"
            if player.team_id is not None:
                label = f"T{player.team_id}-P{player.track_id}"

            cv2.putText(
                annotated,
                label,
                (int(bbox.x1), int(bbox.y1) - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
            )

        if frame_data.ball:
            bx, by = frame_data.ball.center
            cv2.circle(annotated, (int(bx), int(by)), 8, self.BALL_COLOR, -1)
            cv2.circle(annotated, (int(bx), int(by)), 10, self.BALL_COLOR, 2)

        self.writer.write(annotated)

    def release(self):
        self.writer.release()
