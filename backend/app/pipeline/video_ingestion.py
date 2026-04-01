from __future__ import annotations

import logging
from pathlib import Path
from typing import Generator

import cv2
import numpy as np

from app.config import FRAME_SKIP

logger = logging.getLogger(__name__)


class VideoIngestion:
    def __init__(self, video_path: str | Path, frame_skip: int = FRAME_SKIP):
        self.video_path = str(video_path)
        self.frame_skip = frame_skip
        self._cap = None
        self._metadata: dict | None = None

    @property
    def metadata(self) -> dict:
        if self._metadata is None:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {self.video_path}")
            self._metadata = {
                "fps": cap.get(cv2.CAP_PROP_FPS),
                "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / max(cap.get(cv2.CAP_PROP_FPS), 1),
            }
            cap.release()
        return self._metadata

    def extract_frames(self) -> Generator[tuple[int, float, np.ndarray], None, None]:
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {self.video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_idx = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % self.frame_skip == 0:
                    timestamp = frame_idx / fps
                    yield frame_idx, timestamp, frame

                frame_idx += 1
        finally:
            cap.release()

        logger.info(f"Extracted {frame_idx} frames from {self.video_path}")

    def extract_frame_at(self, frame_number: int) -> np.ndarray | None:
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None

    def get_frame_count(self) -> int:
        return self.metadata["total_frames"]
