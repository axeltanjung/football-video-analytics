from __future__ import annotations

import logging
from typing import Optional

import numpy as np
from sklearn.cluster import KMeans

from app.models.schemas import TrackedObject

logger = logging.getLogger(__name__)


class TeamClassifier:
    def __init__(self, n_teams: int = 2):
        self.n_teams = n_teams
        self._kmeans: Optional[KMeans] = None
        self._color_samples: list[np.ndarray] = []
        self._calibrated = False
        self._min_samples_for_calibration = 20

    def extract_jersey_color(self, frame: np.ndarray, player: TrackedObject) -> np.ndarray:
        bbox = player.bbox
        x1 = max(0, int(bbox.x1))
        y1 = max(0, int(bbox.y1))
        x2 = min(frame.shape[1], int(bbox.x2))
        y2 = min(frame.shape[0], int(bbox.y2))

        if x2 <= x1 or y2 <= y1:
            return np.zeros(3)

        crop = frame[y1:y2, x1:x2]
        h = crop.shape[0]
        torso = crop[int(h * 0.15):int(h * 0.5), :]

        if torso.size == 0:
            return np.zeros(3)

        try:
            import cv2
            hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)
            avg_color = np.mean(hsv.reshape(-1, 3), axis=0)
        except Exception:
            avg_color = np.mean(torso.reshape(-1, 3), axis=0)

        return avg_color

    def calibrate(self, frame: np.ndarray, players: list[TrackedObject]):
        colors = []
        for p in players:
            color = self.extract_jersey_color(frame, p)
            if np.any(color > 0):
                colors.append(color)

        if len(colors) < self._min_samples_for_calibration:
            self._color_samples.extend(colors)
            if len(self._color_samples) >= self._min_samples_for_calibration:
                self._fit_kmeans(np.array(self._color_samples))
            return

        self._color_samples.extend(colors)
        self._fit_kmeans(np.array(self._color_samples[-200:]))

    def _fit_kmeans(self, colors: np.ndarray):
        try:
            self._kmeans = KMeans(n_clusters=self.n_teams, random_state=42, n_init=10)
            self._kmeans.fit(colors)
            self._calibrated = True
            logger.info(f"Team classifier calibrated with {len(colors)} samples")
            logger.info(f"Cluster centers: {self._kmeans.cluster_centers_}")
        except Exception as e:
            logger.warning(f"KMeans fitting failed: {e}")

    def classify(self, frame: np.ndarray, player: TrackedObject) -> int:
        if not self._calibrated or self._kmeans is None:
            return hash(player.track_id) % self.n_teams

        color = self.extract_jersey_color(frame, player)
        if np.all(color == 0):
            return hash(player.track_id) % self.n_teams

        team = int(self._kmeans.predict(color.reshape(1, -1))[0])
        return team

    def classify_batch(self, frame: np.ndarray, players: list[TrackedObject]) -> list[int]:
        if not self._calibrated or self._kmeans is None:
            return [hash(p.track_id) % self.n_teams for p in players]

        colors = []
        valid_indices = []
        for i, p in enumerate(players):
            c = self.extract_jersey_color(frame, p)
            if np.any(c > 0):
                colors.append(c)
                valid_indices.append(i)

        teams = [hash(p.track_id) % self.n_teams for p in players]

        if colors:
            predictions = self._kmeans.predict(np.array(colors))
            for idx, pred in zip(valid_indices, predictions):
                teams[idx] = int(pred)

        return teams

    @property
    def is_calibrated(self) -> bool:
        return self._calibrated
