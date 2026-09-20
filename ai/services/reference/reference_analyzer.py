# 선택한 영상 구간에서 특징을 추출하여 운동별 끝 자세와 판정 임계값을 계산합니다.
# 어깨는 손-귀 거리로 준비 자세를 거르고, 시선당기기는 얼굴과 양팔 추적을 확인합니다.
from pathlib import Path
from statistics import mean, pstdev

import cv2

from core.config import (
    POSE_MODEL_VARIANT,
    REFERENCE_SEQUENCE_FPS,
)
from core.exercise_catalog import get_exercise
from models.reference_profile import (
    FeatureTolerances,
    PhaseTarget,
    PhaseThresholds,
    ReferenceProfile,
    ReferenceSample,
)
from services.analysis.smoother import FeatureSmoother
from services.exercises.registry import create_analyzer
from services.pose.base import PoseEstimator
from services.reference.gaze_profile_builder import build_gaze_profile
from services.reference.reference_repository import file_sha256


class ReferenceAnalyzer:
    def __init__(
        self,
        pose_estimator: PoseEstimator,
        exercise_code: str = "shoulder_open_close",
        start_sec: float | None = None,
        end_sec: float | None = None,
    ) -> None:
        self.pose_estimator = pose_estimator
        self.spec = get_exercise(exercise_code)
        self.exercise_analyzer = create_analyzer(exercise_code)
        self.start_sec = self.spec.start_sec if start_sec is None else start_sec
        self.end_sec = self.spec.end_sec if end_sec is None else end_sec
        if (
            self.start_sec < 0
            or self.end_sec < 0
            or (self.end_sec and self.end_sec <= self.start_sec)
        ):
            raise ValueError("기준 구간은 0 <= start < end여야 합니다. end=0은 영상 끝입니다.")

    @staticmethod
    def _phase_target(samples: list[ReferenceSample]) -> PhaseTarget:
        return PhaseTarget(
            elbow_spread_ratio=mean(sample.features.elbow_spread_ratio for sample in samples),
            head_lift_ratio=mean(sample.features.head_lift_ratio for sample in samples),
            wrist_ear_ratio=mean(sample.features.wrist_ear_ratio for sample in samples),
            elbow_angle_deg=mean(sample.features.elbow_angle_deg for sample in samples),
            symmetry_ratio=mean(sample.features.symmetry_ratio for sample in samples),
        )

    @staticmethod
    def _spread(values: list[float], minimum: float) -> float:
        if len(values) < 2:
            return minimum
        return max(minimum, 2.0 * pstdev(values))

    @staticmethod
    def _count_repetitions(
        samples: list[ReferenceSample],
        thresholds: PhaseThresholds,
    ) -> int:
        state = "waiting_closed"
        count = 0
        for sample in samples:
            value = sample.features.elbow_spread_ratio
            if state == "waiting_closed" and value <= thresholds.closed_elbow_ratio:
                state = "closed"
            elif state == "closed" and value >= thresholds.open_elbow_ratio:
                state = "open"
            elif state == "open" and value <= thresholds.closed_elbow_ratio:
                count += 1
                state = "closed"
        return count

    def build_profile_from_samples(
        self,
        samples: list[ReferenceSample],
        source_video: str,
        source_sha256: str,
        source_fps: float,
    ) -> ReferenceProfile:
        if self.spec.code == "gaze_pull":
            profile = build_gaze_profile(
                samples, source_video, source_sha256, source_fps, POSE_MODEL_VARIANT
            )
            profile.start_sec, profile.end_sec = self.start_sec, self.end_sec
            return profile
        if len(samples) < 30:
            raise ValueError(
                "기준 자세로 판단되는 프레임이 너무 적습니다. "
                "양손과 상체가 모두 보이는 정면 영상을 사용하세요."
            )

        ordered = sorted(samples, key=lambda item: item.features.elbow_spread_ratio)
        extreme_count = max(5, int(len(ordered) * 0.12))
        closed_samples = ordered[:extreme_count]
        open_samples = ordered[-extreme_count:]
        closed_target = self._phase_target(closed_samples)
        open_target = self._phase_target(open_samples)

        span = open_target.elbow_spread_ratio - closed_target.elbow_spread_ratio
        if span < 0.35:
            raise ValueError(
                "기준 영상에서 팔꿈치를 펼치고 오므리는 범위가 충분히 확인되지 않습니다."
            )

        thresholds = PhaseThresholds(
            closed_elbow_ratio=closed_target.elbow_spread_ratio + 0.15 * span,
            open_elbow_ratio=closed_target.elbow_spread_ratio + 0.85 * span,
        )
        all_extremes = closed_samples + open_samples
        tolerances = FeatureTolerances(
            elbow_spread_ratio=max(0.10, 0.12 * span),
            head_lift_ratio=max(
                0.04,
                0.25 * abs(open_target.head_lift_ratio - closed_target.head_lift_ratio),
            ),
            wrist_ear_ratio=self._spread(
                [sample.features.wrist_ear_ratio for sample in all_extremes], 0.10
            ),
            elbow_angle_deg=self._spread(
                [sample.features.elbow_angle_deg for sample in all_extremes], 8.0
            ),
            symmetry_ratio=self._spread(
                [sample.features.symmetry_ratio for sample in all_extremes], 0.08
            ),
        )

        return ReferenceProfile(
            start_sec=self.start_sec,
            end_sec=self.end_sec,
            source_video=source_video,
            source_sha256=source_sha256,
            model_variant=POSE_MODEL_VARIANT,
            source_fps=source_fps,
            valid_frame_count=len(samples),
            reference_rep_count=self._count_repetitions(samples, thresholds),
            closed_target=closed_target,
            open_target=open_target,
            thresholds=thresholds,
            tolerances=tolerances,
            sequence=samples,
        )

    def analyze(self, video_path: Path) -> ReferenceProfile:
        if not video_path.exists():
            raise FileNotFoundError(f"기준 영상이 없습니다: {video_path}")

        capture = cv2.VideoCapture(str(video_path))
        if not capture.isOpened():
            raise RuntimeError(f"기준 영상을 열 수 없습니다: {video_path}")

        source_fps = float(capture.get(cv2.CAP_PROP_FPS) or 24.0)
        sample_step = max(1, round(source_fps / REFERENCE_SEQUENCE_FPS))
        smoother = FeatureSmoother(window_size=5, ema_alpha=0.55)
        samples: list[ReferenceSample] = []
        frame_index = 0

        try:
            while True:
                ok, frame = capture.read()
                if not ok:
                    break

                timestamp_ms = int(round(frame_index * 1000.0 / source_fps))
                timestamp_sec = timestamp_ms / 1000.0
                if timestamp_sec < self.start_sec:
                    frame_index += 1
                    continue
                if self.end_sec > 0.0 and timestamp_sec > self.end_sec:
                    break

                pose = self.pose_estimator.detect(frame, timestamp_ms)
                if pose is not None:
                    features = self.exercise_analyzer.extract_features(pose)
                    if features is not None:
                        features = smoother.update(features)
                        is_reference_pose = (
                            self.exercise_analyzer.is_reference_pose(features)
                            if self.spec.code == "gaze_pull"
                            else features.hands_near_ears and features.wrist_ear_ratio <= 1.10
                        )
                        if is_reference_pose and frame_index % sample_step == 0:
                            samples.append(
                                ReferenceSample(
                                    timestamp_ms=timestamp_ms,
                                    features=features,
                                )
                            )
                frame_index += 1
        finally:
            capture.release()

        return self.build_profile_from_samples(
            samples=samples,
            source_video=video_path.name,
            source_sha256=file_sha256(video_path),
            source_fps=source_fps,
        )
