from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text
from app.database import Base


class MatchStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    DETECTING = "detecting"
    TRACKING = "tracking"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    status = Column(String, default=MatchStatus.UPLOADED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    duration_seconds = Column(Float, nullable=True)
    total_frames = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    analytics_json = Column(JSON, nullable=True)
    events_json = Column(JSON, nullable=True)
    heatmap_path = Column(String, nullable=True)
    annotated_video_path = Column(String, nullable=True)
    progress = Column(Float, default=0.0)
