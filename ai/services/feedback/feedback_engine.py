# 운동 판정 코드를 한국어 문구로 바꾸고 같은 문구의 과도한 반복을 막습니다.
# 로그/WebSocket 이벤트에만 쿨다운을 적용합니다. 로컬 화면은 current_feedback으로 매번 판정합니다.
from core.config import FEEDBACK_COOLDOWN_MS
from models.session_state import SessionState

FEEDBACK_MESSAGES = {
    "GAZE_ONE_ARM": "한 번에 한쪽 팔만 올려주세요.",
    "GAZE_SWITCH_SIDE": "반대쪽 팔로 번갈아 진행해주세요.",
    "GAZE_REACH_HIGHER": "손을 대각선 위로 조금 더 올려주세요.",
    "GAZE_REACH_DIAGONALLY": "손을 반대쪽 대각선 방향으로 뻗어주세요.",
    "GAZE_EXTEND_ELBOW": "팔꿈치를 조금 더 펴주세요.",
    "GAZE_LOWER_HAND": "손을 자기 쪽 아래로 조금 더 내려주세요.",
    "GAZE_LOWER_TO_OWN_SIDE": "손을 자기 쪽 바깥 아래로 내려주세요.",
    "GAZE_FOLLOW_HAND": "고개가 손의 방향을 따라가도록 해주세요.",
    "GAZE_CHECK_HEAD_HEIGHT": "기준 동작의 고개 높이를 확인해주세요.",
    "": "",
    "POSE_NOT_DETECTED": "카메라에 상체 전체가 보이도록 위치를 조정해주세요.",
    "START_WITH_ELBOWS_CLOSED": "양손을 귀에 대고 팔꿈치를 앞쪽으로 모아주세요.",
    "KEEP_HANDS_BY_EARS": "운동하는 동안 양손을 귀 옆에 유지해주세요.",
    "OPEN_ELBOWS_MORE": "팔꿈치를 양옆으로 조금 더 펼쳐주세요.",
    "CLOSE_ELBOWS_MORE": "팔꿈치를 얼굴 앞쪽으로 조금 더 모아주세요.",
    "LIFT_HEAD_MORE": "팔꿈치를 펼칠 때 고개도 기준 자세만큼 천천히 들어주세요.",
    "LOWER_HEAD_MORE": "팔꿈치를 모을 때 고개도 함께 천천히 숙여주세요.",
    "MOVE_SYMMETRICALLY": "양쪽 팔꿈치를 같은 속도와 범위로 움직여주세요.",
    "GOOD_REP": "한 회를 완료했습니다. 다음 동작을 이어가세요.",
}

FEEDBACK_PRIORITY = (
    "GAZE_ONE_ARM",
    "GAZE_SWITCH_SIDE",
    "GAZE_REACH_HIGHER",
    "GAZE_REACH_DIAGONALLY",
    "GAZE_EXTEND_ELBOW",
    "GAZE_LOWER_HAND",
    "GAZE_LOWER_TO_OWN_SIDE",
    "GAZE_FOLLOW_HAND",
    "GAZE_CHECK_HEAD_HEIGHT",
    "POSE_NOT_DETECTED",
    "KEEP_HANDS_BY_EARS",
    "START_WITH_ELBOWS_CLOSED",
    "MOVE_SYMMETRICALLY",
    "OPEN_ELBOWS_MORE",
    "CLOSE_ELBOWS_MORE",
    "LIFT_HEAD_MORE",
    "LOWER_HEAD_MORE",
    "GOOD_REP",
)


class FeedbackEngine:
    def select(
        self,
        codes: list[str],
        state: SessionState,
        timestamp_ms: int,
    ) -> tuple[str, str]:
        if not codes:
            return "", ""

        code = next((item for item in FEEDBACK_PRIORITY if item in codes), codes[0])
        is_good = code == "GOOD_REP"
        within_cooldown = (
            code == state.last_feedback_code
            and timestamp_ms - state.last_feedback_at_ms < FEEDBACK_COOLDOWN_MS
        )
        if within_cooldown and not is_good:
            return "", ""

        state.last_feedback_code = code
        state.last_feedback_at_ms = timestamp_ms
        return code, FEEDBACK_MESSAGES.get(code, code)
