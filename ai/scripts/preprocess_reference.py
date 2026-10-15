# storage/reference_videos의 기준 영상을 한 번 분석해 기준 프로필 JSON을 생성합니다.
# 실시간 운동에서는 이 JSON을 불러와 영상 재분석 없이 단계별 자세를 비교합니다.
from core.config import (
    POSE_MODEL_PATH,
    ensure_directories,
)
from core.exercise_cli import parse_exercise_args
from services.pose.blazepose_estimator import BlazePoseEstimator
from services.reference.reference_analyzer import ReferenceAnalyzer
from services.reference.reference_repository import ReferenceRepository


def main() -> None:
    spec, start, end = parse_exercise_args("운동 기준 영상 전처리")
    ensure_directories()
    estimator = BlazePoseEstimator(POSE_MODEL_PATH)
    try:
        profile = ReferenceAnalyzer(estimator, spec.code, start, end).analyze(spec.video_path)
    finally:
        estimator.close()

    ReferenceRepository(spec.profile_path).save(profile)
    print(f"기준 영상: {spec.video_path}")
    print(f"기준 프로필: {spec.profile_path}")
    print(f"유효 프레임: {profile.valid_frame_count}")
    print(f"기준 반복 횟수: {profile.reference_rep_count}")
    if spec.code == "gaze_pull":
        for side in ("left", "right"):
            ref = getattr(profile.gaze_pull, side)
            print(f"{side} 손 높이: 아래 {ref.low.height:.3f}, 위 {ref.high.height:.3f}")
        print(
            f"좌/우 반복: {profile.gaze_pull.left_reference_reps}/{profile.gaze_pull.right_reference_reps}"
        )
        print(f"사용 구간: {start:.1f}~{end:.1f}초")
        return
    print(
        "팔꿈치 간격 기준: "
        f"닫힘 {profile.closed_target.elbow_spread_ratio:.3f}, "
        f"펼침 {profile.open_target.elbow_spread_ratio:.3f}"
    )
    print(
        "고개 높이 기준: "
        f"숙임 {profile.closed_target.head_lift_ratio:.3f}, "
        f"들기 {profile.open_target.head_lift_ratio:.3f}"
    )


if __name__ == "__main__":
    main()
