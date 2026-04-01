from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str

    @property
    def center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        return self.width * self.height

    def to_tlwh(self) -> list[float]:
        return [self.x1, self.y1, self.width, self.height]

    def to_xyxy(self) -> list[float]:
        return [self.x1, self.y1, self.x2, self.y2]


@dataclass
class TrackedObject:
    track_id: int
    bbox: BoundingBox
    class_name: str
    team_id: Optional[int] = None
    velocity: tuple[float, float] = (0.0, 0.0)
    positions_history: list[tuple[float, float]] = field(default_factory=list)

    @property
    def center(self) -> tuple[float, float]:
        return self.bbox.center

    @property
    def speed(self) -> float:
        return float(np.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2))


@dataclass
class FrameDetections:
    frame_number: int
    timestamp: float
    players: list[TrackedObject] = field(default_factory=list)
    ball: Optional[TrackedObject] = None
    raw_detections: list[BoundingBox] = field(default_factory=list)


@dataclass
class MatchEvent:
    event_type: str
    frame_number: int
    timestamp: float
    player_id: Optional[int] = None
    team_id: Optional[int] = None
    position: Optional[tuple[float, float]] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class PossessionSegment:
    team_id: int
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    duration: float = 0.0

    def __post_init__(self):
        self.duration = self.end_time - self.start_time


@dataclass
class MatchAnalytics:
    match_id: str
    total_frames_processed: int
    duration_seconds: float
    possession: dict[int, float] = field(default_factory=dict)
    possession_timeline: list[dict] = field(default_factory=list)
    total_passes: dict[int, int] = field(default_factory=dict)
    pass_accuracy: dict[int, float] = field(default_factory=dict)
    shots: dict[int, int] = field(default_factory=dict)
    shots_on_target: dict[int, int] = field(default_factory=dict)
    player_heatmaps: dict[int, list[tuple[float, float]]] = field(default_factory=dict)
    events: list[MatchEvent] = field(default_factory=list)
    possession_segments: list[PossessionSegment] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "total_frames_processed": self.total_frames_processed,
            "duration_seconds": self.duration_seconds,
            "possession": {str(k): round(v, 1) for k, v in self.possession.items()},
            "possession_timeline": self.possession_timeline,
            "total_passes": {str(k): v for k, v in self.total_passes.items()},
            "pass_accuracy": {str(k): round(v, 1) for k, v in self.pass_accuracy.items()},
            "shots": {str(k): v for k, v in self.shots.items()},
            "shots_on_target": {str(k): v for k, v in self.shots_on_target.items()},
            "events": [
                {
                    "event_type": e.event_type,
                    "frame_number": e.frame_number,
                    "timestamp": round(e.timestamp, 2),
                    "player_id": e.player_id,
                    "team_id": e.team_id,
                    "position": e.position,
                    "metadata": e.metadata,
                }
                for e in self.events
            ],
            "player_heatmaps": {
                str(k): [(round(x, 1), round(y, 1)) for x, y in v]
                for k, v in self.player_heatmaps.items()
            },
        }
