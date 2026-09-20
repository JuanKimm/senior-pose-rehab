"""AI 분석 결과와 녹화 영상 경로를 백엔드에 전달합니다.

- BACKEND_ENABLED=False이면 요청을 보내지 않습니다.
- 회차별 점수는 actionNo와 actionScore로 변환합니다.
- angleDiff는 협의 전까지 전송하지 않습니다.
- 영상 파일 자체가 아니라 videoPath 문자열만 전달합니다.

주의:
현재 백엔드는 angleDiff를 필수값으로 검사합니다.
백엔드에서 해당 조건을 변경하기 전에는 점수 요청이 거절됩니다.
"""

from collections.abc import Sequence
from math import isfinite
from pathlib import Path

import httpx

from core.config import BACKEND_BASE_URL, BACKEND_ENABLED


class BackendClient:
    def __init__(self) -> None:
        self.enabled = BACKEND_ENABLED
        self.base_url = BACKEND_BASE_URL.strip().rstrip("/")

    def _validate_request(self, session_id: int) -> None:
        """백엔드 요청에 필요한 기본값을 검증합니다."""
        if (
            isinstance(session_id, bool)
            or not isinstance(session_id, int)
            or session_id <= 0
        ):
            raise ValueError(
                "백엔드 세션 ID는 백엔드에서 발급한 1 이상의 정수여야 합니다."
            )

        if not self.base_url:
            raise RuntimeError("BACKEND_BASE_URL이 설정되지 않았습니다.")

    async def send_scores(
        self,
        session_id: int,
        rep_scores: Sequence[float],
    ) -> bool:
        """완료된 세션의 회차별 점수를 한 번에 전송합니다.

        actionNo:
            rep_scores의 순서대로 1부터 부여하는 완료 동작 번호.

        actionScore:
            AI의 회차별 자세 유사도(0~100).
            백엔드 Integer 타입에 맞춰 정수로 반올림합니다.
            Python round()는 정확히 .5일 때 가까운 짝수로 반올림합니다.

        반환값:
            연동 비활성화 시 False, 전송 성공 시 True.

        오류:
            잘못된 입력은 ValueError,
            HTTP 오류와 통신 오류는 httpx 예외로 호출자에게 전달합니다.

        주의:
            현재 백엔드는 점수를 추가 저장하므로 같은 전체 목록을 반복 전송하면
            중복 저장될 수 있습니다. 자동 재시도는 수행하지 않습니다.
        """
        if not self.enabled:
            return False

        self._validate_request(session_id)

        if len(rep_scores) == 0:
            raise ValueError("전송할 회차별 점수가 없습니다.")

        scores: list[dict[str, int]] = []

        for action_no, score in enumerate(rep_scores, start=1):
            numeric_score = float(score)

            if (
                not isfinite(numeric_score)
                or not 0.0 <= numeric_score <= 100.0
            ):
                raise ValueError(
                    "회차별 점수는 0~100 사이의 유한한 값이어야 합니다."
                )

            scores.append(
                {
                    "actionNo": action_no,
                    "actionScore": round(numeric_score),
                }
            )

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.base_url}/api/exercise/session/{session_id}/score",
                json={"scores": scores},
            )
            response.raise_for_status()

        return True

    async def send_video_path(
        self,
        session_id: int,
        video_path: str | Path,
    ) -> bool:
        """영상 경로 또는 URL을 JSON으로 전달합니다.

        실제 MP4 파일을 업로드하거나 복사하지 않습니다.
        전달한 경로의 파일에 다른 서버가 접근할 수 있는지는 별도 문제입니다.

        반환값:
            연동 비활성화 시 False, 전송 성공 시 True.

        HTTP 오류와 통신 오류는 httpx 예외로 호출자에게 전달합니다.
        """
        if not self.enabled:
            return False

        self._validate_request(session_id)

        if not isinstance(video_path, (str, Path)):
            raise ValueError("영상 경로는 문자열 또는 Path여야 합니다.")

        video_path_text = str(video_path).strip()

        if not video_path_text or video_path_text == ".":
            raise ValueError("전송할 영상 경로가 비어 있습니다.")

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.base_url}/api/exercise/session/{session_id}/video-upload",
                json={"videoPath": video_path_text},
            )
            response.raise_for_status()

        return True