from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from app.config import YOLO_MODEL_PATH, YOLO_CONFIDENCE_THRESHOLD, YOLO_IOU_THRESHOLD
from app.models.schemas import BoundingBox

logger = logging.getLogger(__name__)

COCO_PERSON_CLASS = 0
COCO_SPORTS_BALL_CLASS = 32

CLASS_MAP = {
    COCO_PERSON_CLASS: "player",
    COCO_SPORTS_BALL_CLASS: "ball",
}


class ObjectDetector:
    def __init__(
        self,
        model_path: str = YOLO_MODEL_PATH,
        confidence: float = YOLO_CONFIDENCE_THRESHOLD,
        iou_threshold: float = YOLO_IOU_THRESHOLD,
    ):
        self.model_path = model_path
        self.confidence = confidence
        self.iou_threshold = iou_threshold
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                from ultralytics import YOLO
                self._model = YOLO(self.model_path)
                logger.info(f"YOLO model loaded: {self.model_path}")
            except ImportError:
                logger.warning("ultralytics not installed, using mock detector")
                self._model = None
        return self._model

    def detect(self, frame: np.ndarray) -> list[BoundingBox]:
        if self.model is None:
            return self._mock_detect(frame)

        results = self.model(
            frame,
            conf=self.confidence,
            iou=self.iou_threshold,
            classes=[COCO_PERSON_CLASS, COCO_SPORTS_BALL_CLASS],
            verbose=False,
        )

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for i in range(len(boxes)):
                xyxy = boxes.xyxy[i].cpu().numpy()
                conf = float(boxes.conf[i].cpu().numpy())
                cls = int(boxes.cls[i].cpu().numpy())

                if cls not in CLASS_MAP:
                    continue

                detections.append(
                    BoundingBox(
                        x1=float(xyxy[0]),
                        y1=float(xyxy[1]),
                        x2=float(xyxy[2]),
                        y2=float(xyxy[3]),
                        confidence=conf,
                        class_id=cls,
                        class_name=CLASS_MAP[cls],
                    )
                )

        return detections

    def detect_batch(self, frames: list[np.ndarray]) -> list[list[BoundingBox]]:
        if self.model is None:
            return [self._mock_detect(f) for f in frames]

        results = self.model(
            frames,
            conf=self.confidence,
            iou=self.iou_threshold,
            classes=[COCO_PERSON_CLASS, COCO_SPORTS_BALL_CLASS],
            verbose=False,
        )

        all_detections = []
        for result in results:
            frame_dets = []
            boxes = result.boxes
            if boxes is not None:
                for i in range(len(boxes)):
                    xyxy = boxes.xyxy[i].cpu().numpy()
                    conf = float(boxes.conf[i].cpu().numpy())
                    cls = int(boxes.cls[i].cpu().numpy())
                    if cls in CLASS_MAP:
                        frame_dets.append(
                            BoundingBox(
                                x1=float(xyxy[0]),
                                y1=float(xyxy[1]),
                                x2=float(xyxy[2]),
                                y2=float(xyxy[3]),
                                confidence=conf,
                                class_id=cls,
                                class_name=CLASS_MAP[cls],
                            )
                        )
            all_detections.append(frame_dets)

        return all_detections

    @staticmethod
    def _mock_detect(frame: np.ndarray) -> list[BoundingBox]:
        h, w = frame.shape[:2]
        rng = np.random.default_rng(42)
        detections = []

        for _ in range(rng.integers(8, 16)):
            cx = rng.uniform(0.1, 0.9) * w
            cy = rng.uniform(0.2, 0.8) * h
            bw = rng.uniform(20, 50)
            bh = rng.uniform(40, 90)
            detections.append(
                BoundingBox(
                    x1=cx - bw / 2,
                    y1=cy - bh / 2,
                    x2=cx + bw / 2,
                    y2=cy + bh / 2,
                    confidence=rng.uniform(0.5, 0.95),
                    class_id=COCO_PERSON_CLASS,
                    class_name="player",
                )
            )

        ball_x = rng.uniform(0.2, 0.8) * w
        ball_y = rng.uniform(0.3, 0.7) * h
        ball_r = rng.uniform(5, 12)
        detections.append(
            BoundingBox(
                x1=ball_x - ball_r,
                y1=ball_y - ball_r,
                x2=ball_x + ball_r,
                y2=ball_y + ball_r,
                confidence=rng.uniform(0.4, 0.8),
                class_id=COCO_SPORTS_BALL_CLASS,
                class_name="ball",
            )
        )

        return detections
