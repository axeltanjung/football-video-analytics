from __future__ import annotations

import logging
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class HeatmapGenerator:
    def __init__(
        self,
        pitch_width: int = 1050,
        pitch_height: int = 680,
        sigma: float = 15.0,
    ):
        self.pitch_width = pitch_width
        self.pitch_height = pitch_height
        self.sigma = sigma

    def generate(
        self,
        positions: list[tuple[float, float]],
        frame_width: int,
        frame_height: int,
    ) -> np.ndarray:
        heatmap = np.zeros((self.pitch_height, self.pitch_width), dtype=np.float64)

        for x, y in positions:
            px = int(x / max(frame_width, 1) * self.pitch_width)
            py = int(y / max(frame_height, 1) * self.pitch_height)

            px = np.clip(px, 0, self.pitch_width - 1)
            py = np.clip(py, 0, self.pitch_height - 1)

            y_grid, x_grid = np.ogrid[
                max(0, py - 30):min(self.pitch_height, py + 30),
                max(0, px - 30):min(self.pitch_width, px + 30),
            ]
            gauss = np.exp(-((x_grid - px) ** 2 + (y_grid - py) ** 2) / (2 * self.sigma ** 2))
            heatmap[
                max(0, py - 30):min(self.pitch_height, py + 30),
                max(0, px - 30):min(self.pitch_width, px + 30),
            ] += gauss

        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()

        return heatmap

    def render(
        self,
        positions: list[tuple[float, float]],
        frame_width: int,
        frame_height: int,
        colormap: int = cv2.COLORMAP_JET,
    ) -> np.ndarray:
        heatmap = self.generate(positions, frame_width, frame_height)
        heatmap_uint8 = (heatmap * 255).astype(np.uint8)
        colored = cv2.applyColorMap(heatmap_uint8, colormap)

        pitch = self._draw_pitch_lines(colored)
        return pitch

    def _draw_pitch_lines(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        color = (255, 255, 255)
        thickness = 1

        cv2.rectangle(image, (0, 0), (w - 1, h - 1), color, thickness)
        cv2.line(image, (w // 2, 0), (w // 2, h), color, thickness)
        cv2.circle(image, (w // 2, h // 2), int(h * 0.13), color, thickness)
        cv2.circle(image, (w // 2, h // 2), 3, color, -1)

        box_w = int(w * 0.16)
        box_h = int(h * 0.40)
        y_off = (h - box_h) // 2
        cv2.rectangle(image, (0, y_off), (box_w, y_off + box_h), color, thickness)
        cv2.rectangle(image, (w - box_w, y_off), (w - 1, y_off + box_h), color, thickness)

        small_w = int(w * 0.06)
        small_h = int(h * 0.20)
        sy_off = (h - small_h) // 2
        cv2.rectangle(image, (0, sy_off), (small_w, sy_off + small_h), color, thickness)
        cv2.rectangle(image, (w - small_w, sy_off), (w - 1, sy_off + small_h), color, thickness)

        return image

    def save(
        self,
        positions: list[tuple[float, float]],
        frame_width: int,
        frame_height: int,
        output_path: str,
    ) -> str:
        img = self.render(positions, frame_width, frame_height)
        cv2.imwrite(output_path, img)
        logger.info(f"Heatmap saved to {output_path}")
        return output_path
