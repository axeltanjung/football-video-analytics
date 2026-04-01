from __future__ import annotations

import logging
from collections import defaultdict
from typing import Optional

import numpy as np

from app.models.schemas import (
    FrameDetections,
    MatchAnalytics,
    MatchEvent,
    PossessionSegment,
)

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    def __init__(self, match_id: str, fps: float = 30.0):
        self.match_id = match_id
        self.fps = fps

        self._possession_frames: dict[int, int] = defaultdict(int)
        self._total_frames = 0
        self._possession_timeline: list[dict] = []
        self._timeline_interval = 30

        self._passes: dict[int, int] = defaultdict(int)
        self._successful_passes: dict[int, int] = defaultdict(int)
        self._shots: dict[int, int] = defaultdict(int)
        self._shots_on_target: dict[int, int] = defaultdict(int)

        self._player_positions: dict[int, list[tuple[float, float]]] = defaultdict(list)
        self._events: list[MatchEvent] = []

        self._possession_segments: list[PossessionSegment] = []
        self._current_possession_team: Optional[int] = None
        self._possession_start_frame = 0
        self._possession_start_time = 0.0

        self._interval_frames: dict[int, int] = defaultdict(int)

    def process_frame(
        self,
        frame_data: FrameDetections,
        possession_team: Optional[int],
        frame_events: list[MatchEvent],
    ):
        self._total_frames += 1

        if possession_team is not None:
            self._possession_frames[possession_team] += 1
            self._interval_frames[possession_team] += 1

            if self._current_possession_team != possession_team:
                if self._current_possession_team is not None:
                    self._possession_segments.append(PossessionSegment(
                        team_id=self._current_possession_team,
                        start_frame=self._possession_start_frame,
                        end_frame=frame_data.frame_number,
                        start_time=self._possession_start_time,
                        end_time=frame_data.timestamp,
                    ))
                self._current_possession_team = possession_team
                self._possession_start_frame = frame_data.frame_number
                self._possession_start_time = frame_data.timestamp

        if self._total_frames % self._timeline_interval == 0:
            total = sum(self._interval_frames.values()) or 1
            snapshot = {
                "timestamp": round(frame_data.timestamp, 1),
                "frame": frame_data.frame_number,
            }
            for team_id, count in self._interval_frames.items():
                snapshot[f"team_{team_id}"] = round(count / total * 100, 1)
            self._possession_timeline.append(snapshot)
            self._interval_frames.clear()

        for player in frame_data.players:
            self._player_positions[player.track_id].append(player.center)

        for event in frame_events:
            self._events.append(event)

            if event.event_type == "pass" and event.team_id is not None:
                self._passes[event.team_id] += 1
                if event.metadata.get("distance", 999) < 200:
                    self._successful_passes[event.team_id] += 1

            elif event.event_type == "shot" and event.team_id is not None:
                self._shots[event.team_id] += 1
                if event.metadata.get("speed", 0) > 20:
                    self._shots_on_target[event.team_id] += 1

    def compute_analytics(self) -> MatchAnalytics:
        total_possession_frames = sum(self._possession_frames.values()) or 1
        possession = {
            team: round(count / total_possession_frames * 100, 1)
            for team, count in self._possession_frames.items()
        }

        pass_accuracy = {}
        for team in self._passes:
            total = self._passes[team]
            successful = self._successful_passes.get(team, 0)
            pass_accuracy[team] = round(successful / max(total, 1) * 100, 1)

        duration = self._total_frames / max(self.fps, 1)

        heatmaps = {}
        for player_id, positions in self._player_positions.items():
            sampled = positions[::max(1, len(positions) // 200)]
            heatmaps[player_id] = sampled

        analytics = MatchAnalytics(
            match_id=self.match_id,
            total_frames_processed=self._total_frames,
            duration_seconds=duration,
            possession=possession,
            possession_timeline=self._possession_timeline,
            total_passes=dict(self._passes),
            pass_accuracy=pass_accuracy,
            shots=dict(self._shots),
            shots_on_target=dict(self._shots_on_target),
            player_heatmaps=heatmaps,
            events=self._events,
            possession_segments=self._possession_segments,
        )

        return analytics

    def generate_heatmap_data(self, team_id: Optional[int] = None) -> list[tuple[float, float]]:
        points = []
        for player_id, positions in self._player_positions.items():
            points.extend(positions)
        return points

    def reset(self):
        self._possession_frames.clear()
        self._total_frames = 0
        self._possession_timeline.clear()
        self._passes.clear()
        self._successful_passes.clear()
        self._shots.clear()
        self._shots_on_target.clear()
        self._player_positions.clear()
        self._events.clear()
        self._possession_segments.clear()
        self._current_possession_team = None
        self._interval_frames.clear()
