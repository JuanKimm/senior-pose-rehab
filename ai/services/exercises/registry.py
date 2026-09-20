"""프로필의 운동 코드에 맞는 분석기를 생성합니다."""

from services.exercises.base import ExerciseAnalyzer
from services.exercises.gaze_pull import GazePullAnalyzer
from services.exercises.shoulder_open_close import ShoulderOpenCloseAnalyzer


def create_analyzer(exercise_code: str) -> ExerciseAnalyzer:
    if exercise_code == "shoulder_open_close":
        return ShoulderOpenCloseAnalyzer()
    if exercise_code == "gaze_pull":
        return GazePullAnalyzer()
    raise ValueError(f"지원하지 않는 운동입니다: {exercise_code}")
