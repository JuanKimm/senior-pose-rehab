# MediaPipe Pose Landmarker를 BlazePose 추정기 인터페이스로 감쌉니다.
# 영상과 웹캠 프레임 모두 동일한 VIDEO 모드로 처리합니다.
from pathlib import Path

import cv2
import numpy as np

from services.pose.base import LandmarkPoint, PoseEstimator, PoseResult


class BlazePoseEstimator(PoseEstimator):
    def __init__(
        self,
        model_path: Path,
        min_detection_confidence: float = 0.5,
        min_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        if not model_path.exists():
            raise FileNotFoundError(
                f"Pose Landmarker 모델이 없습니다: {model_path}. "
                "먼저 python -m scripts.download_pose_model 을 실행하세요."
            )

        try:
            import mediapipe as mp
        except ImportError as exc:
            raise RuntimeError(
                "mediapipe가 설치되지 않았습니다. pip install -r requirements.txt를 실행하세요."
            ) from exc

        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=min_detection_confidence,
            min_pose_presence_confidence=min_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_segmentation_masks=False,
        )
        self._mp = mp
        self._landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)

    @staticmethod
    def _convert_landmarks(landmarks: list[object]) -> list[LandmarkPoint]:
        converted: list[LandmarkPoint] = []
        for landmark in landmarks:
            converted.append(
                LandmarkPoint(
                    x=float(landmark.x),
                    y=float(landmark.y),
                    z=float(landmark.z),
                    visibility=float(landmark.visibility or 0.0),
                    presence=float(landmark.presence or 0.0),
                )
            )
        return converted

    def detect(self, frame_bgr: np.ndarray, timestamp_ms: int) -> PoseResult | None:
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=frame_rgb)
        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)

        if not result.pose_landmarks:
            return None

        normalized = self._convert_landmarks(result.pose_landmarks[0])
        world = (
            self._convert_landmarks(result.pose_world_landmarks[0])
            if result.pose_world_landmarks
            else []
        )
        return PoseResult(
            normalized=normalized,
            world=world,
            image_width=frame_bgr.shape[1],
            image_height=frame_bgr.shape[0],
        )

    def close(self) -> None:
        self._landmarker.close()
