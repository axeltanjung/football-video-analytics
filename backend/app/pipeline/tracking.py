from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from app.config import DEEPSORT_MAX_AGE, DEEPSORT_N_INIT, DEEPSORT_MAX_COSINE_DISTANCE
from app.models.schemas import BoundingBox, TrackedObject

logger = logging.getLogger(__name__)


class ObjectTracker:
    def __init__(
        self,
        max_age: int = DEEPSORT_MAX_AGE,
        n_init: int = DEEPSORT_N_INIT,
        max_cosine_distance: float = DEEPSORT_MAX_COSINE_DISTANCE,
    ):
        self.max_age = max_age
        self.n_init = n_init
        self.max_cosine_distance = max_cosine_distance
        self._tracker = None
        self._prev_positions: dict[int, tuple[float, float]] = {}

    @property
    def tracker(self):
        if self._tracker is None:
            try:
                from deep_sort_realtime.deepsort_tracker import DeepSort
                self._tracker = DeepSort(
                    max_age=self.max_age,
                    n_init=self.n_init,
                    max_cosine_distance=self.max_cosine_distance,
                )
                logger.info("DeepSORT tracker initialized")
            except ImportError:
                logger.warning("deep-sort-realtime not installed, using simple tracker")
                self._tracker = SimpleTracker()
        return self._tracker

    def update(
        self,
        detections: list[BoundingBox],
        frame: np.ndarray,
    ) -> list[TrackedObject]:
        players = [d for d in detections if d.class_name == "player"]
        balls = [d for d in detections if d.class_name == "ball"]

        tracked_objects = []

        if players:
            player_tracks = self._track_objects(players, frame, "player")
            tracked_objects.extend(player_tracks)

        if balls:
            best_ball = max(balls, key=lambda b: b.confidence)
            ball_track = TrackedObject(
                track_id=-1,
                bbox=best_ball,
                class_name="ball",
            )
            if -1 in self._prev_positions:
                prev = self._prev_positions[-1]
                curr = best_ball.center
                ball_track.velocity = (curr[0] - prev[0], curr[1] - prev[1])
            self._prev_positions[-1] = best_ball.center
            tracked_objects.append(ball_track)

        return tracked_objects

    def _track_objects(
        self,
        detections: list[BoundingBox],
        frame: np.ndarray,
        class_name: str,
    ) -> list[TrackedObject]:
        if isinstance(self.tracker, SimpleTracker):
            return self.tracker.update(detections, class_name)

        det_list = []
        for d in detections:
            det_list.append(([d.x1, d.y1, d.width, d.height], d.confidence, class_name))

        tracks = self.tracker.update_tracks(det_list, frame=frame)
        tracked = []

        for track in tracks:
            if not track.is_confirmed():
                continue

            ltrb = track.to_ltrb()
            track_id = track.track_id

            bbox = BoundingBox(
                x1=float(ltrb[0]),
                y1=float(ltrb[1]),
                x2=float(ltrb[2]),
                y2=float(ltrb[3]),
                confidence=track.det_conf if track.det_conf else 0.0,
                class_id=0,
                class_name=class_name,
            )

            velocity = (0.0, 0.0)
            if track_id in self._prev_positions:
                prev = self._prev_positions[track_id]
                curr = bbox.center
                velocity = (curr[0] - prev[0], curr[1] - prev[1])
            self._prev_positions[track_id] = bbox.center

            obj = TrackedObject(
                track_id=int(track_id) if isinstance(track_id, (int, float)) else hash(track_id) % 10000,
                bbox=bbox,
                class_name=class_name,
                velocity=velocity,
            )
            obj.positions_history.append(bbox.center)
            tracked.append(obj)

        return tracked

    def reset(self):
        self._tracker = None
        self._prev_positions.clear()


class SimpleTracker:
    def __init__(self, max_distance: float = 100.0):
        self.max_distance = max_distance
        self._tracks: dict[int, tuple[float, float]] = {}
        self._next_id = 1
        self._prev_positions: dict[int, tuple[float, float]] = {}

    def update(self, detections: list[BoundingBox], class_name: str) -> list[TrackedObject]:
        det_centers = [d.center for d in detections]
        tracked = []

        if not self._tracks:
            for i, det in enumerate(detections):
                tid = self._next_id
                self._next_id += 1
                self._tracks[tid] = det.center
                tracked.append(TrackedObject(track_id=tid, bbox=det, class_name=class_name))
            return tracked

        assigned_tracks = {}
        assigned_dets = set()

        for tid, prev_center in self._tracks.items():
            best_dist = float("inf")
            best_idx = -1
            for idx, center in enumerate(det_centers):
                if idx in assigned_dets:
                    continue
                dist = np.sqrt((center[0] - prev_center[0]) ** 2 + (center[1] - prev_center[1]) ** 2)
                if dist < best_dist and dist < self.max_distance:
                    best_dist = dist
                    best_idx = idx

            if best_idx >= 0:
                assigned_tracks[tid] = best_idx
                assigned_dets.add(best_idx)

        new_tracks = {}
        for tid, idx in assigned_tracks.items():
            det = detections[idx]
            velocity = (0.0, 0.0)
            if tid in self._prev_positions:
                prev = self._prev_positions[tid]
                velocity = (det.center[0] - prev[0], det.center[1] - prev[1])
            self._prev_positions[tid] = det.center
            new_tracks[tid] = det.center
            obj = TrackedObject(track_id=tid, bbox=det, class_name=class_name, velocity=velocity)
            obj.positions_history.append(det.center)
            tracked.append(obj)

        for idx, det in enumerate(detections):
            if idx not in assigned_dets:
                tid = self._next_id
                self._next_id += 1
                new_tracks[tid] = det.center
                self._prev_positions[tid] = det.center
                tracked.append(TrackedObject(track_id=tid, bbox=det, class_name=class_name))

        self._tracks = new_tracks
        return tracked
