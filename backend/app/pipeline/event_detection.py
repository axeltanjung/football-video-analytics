from __future__ import annotations

import logging
from collections import deque
from typing import Optional

import numpy as np

from app.config import (
    GOAL_AREA_X_THRESHOLD,
    SHOT_VELOCITY_THRESHOLD,
    PASS_PROXIMITY_THRESHOLD,
    POSSESSION_RADIUS_PX,
)
from app.models.schemas import FrameDetections, MatchEvent, TrackedObject

logger = logging.getLogger(__name__)


class EventDetector:
    def __init__(self):
        self._ball_history: deque[tuple[int, float, float, float]] = deque(maxlen=60)
        self._possession_holder: Optional[int] = None
        self._possession_team: Optional[int] = None
        self._last_possessor: Optional[int] = None
        self._pass_cooldown: int = 0
        self._shot_cooldown: int = 0

    def detect_events(self, frame_data: FrameDetections) -> list[MatchEvent]:
        events = []

        if self._pass_cooldown > 0:
            self._pass_cooldown -= 1
        if self._shot_cooldown > 0:
            self._shot_cooldown -= 1

        if frame_data.ball is None:
            return events

        ball = frame_data.ball
        ball_cx, ball_cy = ball.center
        self._ball_history.append((
            frame_data.frame_number,
            frame_data.timestamp,
            ball_cx,
            ball_cy,
        ))

        closest_player, closest_dist = self._find_closest_player(ball, frame_data.players)

        if closest_player is not None and closest_dist < POSSESSION_RADIUS_PX:
            new_holder = closest_player.track_id
            new_team = closest_player.team_id

            if (
                self._possession_holder is not None
                and new_holder != self._possession_holder
                and self._possession_team == new_team
                and self._pass_cooldown == 0
            ):
                events.append(MatchEvent(
                    event_type="pass",
                    frame_number=frame_data.frame_number,
                    timestamp=frame_data.timestamp,
                    player_id=self._possession_holder,
                    team_id=self._possession_team,
                    position=ball.center,
                    metadata={
                        "from_player": self._possession_holder,
                        "to_player": new_holder,
                        "distance": round(closest_dist, 1),
                    },
                ))
                self._pass_cooldown = 15

            if (
                self._possession_holder is not None
                and new_holder != self._possession_holder
                and self._possession_team is not None
                and new_team != self._possession_team
            ):
                events.append(MatchEvent(
                    event_type="tackle",
                    frame_number=frame_data.frame_number,
                    timestamp=frame_data.timestamp,
                    player_id=new_holder,
                    team_id=new_team,
                    position=ball.center,
                    metadata={
                        "from_player": self._possession_holder,
                        "from_team": self._possession_team,
                    },
                ))

            self._last_possessor = self._possession_holder
            self._possession_holder = new_holder
            self._possession_team = new_team

        shot_event = self._detect_shot(frame_data)
        if shot_event:
            events.append(shot_event)

        return events

    def _find_closest_player(
        self,
        ball: TrackedObject,
        players: list[TrackedObject],
    ) -> tuple[Optional[TrackedObject], float]:
        if not players:
            return None, float("inf")

        ball_cx, ball_cy = ball.center
        min_dist = float("inf")
        closest = None

        for p in players:
            px, py = p.center
            dist = np.sqrt((px - ball_cx) ** 2 + (py - ball_cy) ** 2)
            if dist < min_dist:
                min_dist = dist
                closest = p

        return closest, min_dist

    def _detect_shot(self, frame_data: FrameDetections) -> Optional[MatchEvent]:
        if self._shot_cooldown > 0 or len(self._ball_history) < 5:
            return None

        ball = frame_data.ball
        ball_speed = ball.speed if ball else 0.0

        if ball_speed < SHOT_VELOCITY_THRESHOLD:
            return None

        recent = list(self._ball_history)[-5:]
        x_positions = [p[2] for p in recent]
        frame_w = max(x_positions) if x_positions else 1.0

        normalized_x = x_positions[-1] / max(frame_w, 1.0) if frame_w > 0 else 0

        x_movement = x_positions[-1] - x_positions[0]
        moving_toward_goal = abs(normalized_x) > GOAL_AREA_X_THRESHOLD or abs(x_movement) > 80

        if not moving_toward_goal:
            return None

        self._shot_cooldown = 30

        return MatchEvent(
            event_type="shot",
            frame_number=frame_data.frame_number,
            timestamp=frame_data.timestamp,
            player_id=self._possession_holder,
            team_id=self._possession_team,
            position=ball.center,
            metadata={
                "speed": round(ball_speed, 1),
                "direction": "right" if x_movement > 0 else "left",
            },
        )

    def get_possession_state(self) -> tuple[Optional[int], Optional[int]]:
        return self._possession_holder, self._possession_team

    def reset(self):
        self._ball_history.clear()
        self._possession_holder = None
        self._possession_team = None
        self._last_possessor = None
        self._pass_cooldown = 0
        self._shot_cooldown = 0
