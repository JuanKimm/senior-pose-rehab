import { useNavigate } from "react-router-dom";
import "../../styles/ResultPage.css";

function ResultPage() {
  const navigate = useNavigate();

  /* =========================
     AI 운동 결과 불러오기
  ========================= */

  const savedSummary = sessionStorage.getItem("exerciseSummary");

  let summary = null;

  if (savedSummary) {
    try {
      summary = JSON.parse(savedSummary);
    } catch (error) {
      console.error("운동 결과 불러오기 실패:", error);
    }
  }

  /* =========================
     운동 시간 변환
  ========================= */

  const formatDuration = (seconds = 0) => {
    const minute = Math.floor(seconds / 60);
    const second = seconds % 60;

    return `${String(minute).padStart(2, "0")}:${String(second).padStart(
      2,
      "0",
    )}`;
  };

  /* =========================
     오늘 날짜
  ========================= */

  const today = new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date());

  /* =========================
     결과 데이터
  ========================= */

  const resultData = {
    exerciseName: "어깨 운동",
    date: today,
    totalCount: summary?.rep_count ?? 0,
    duration: formatDuration(summary?.duration_sec ?? 0),
    accuracy: Math.round(summary?.accuracy ?? 0),
  };

  const handleRetry = () => {
    navigate("/exercise");
  };

  const handleGoDashboard = () => {
    navigate("/dashboard");
  };

  return (
    <div className="resultPage">
      <main className="resultContainer">
        <section className="resultCard">
          {/* 완료 아이콘 */}
          <div className="completeIcon">✓</div>

          {/* 제목 */}
          <h1>오늘도 운동을 완료했어요.</h1>

          {/* 운동 정보 */}
          <div className="resultExerciseInfo">
            <strong>{resultData.exerciseName}</strong>
            <span>{resultData.date}</span>
          </div>

          {/* 운동 결과 */}
          <div className="resultStats">
            <div className="resultStat">
              <strong>{resultData.totalCount}회</strong>
              <span>총 수행 횟수</span>
            </div>

            <div className="resultStat">
              <strong>{resultData.duration}</strong>
              <span>운동 시간</span>
            </div>

            <div className="resultStat">
              <strong>{resultData.accuracy}%</strong>
              <span>평균 정확도</span>
            </div>
          </div>

          {/* 버튼 */}
          <div className="resultButtons">
            <button
              type="button"
              className="recordButton"
              onClick={handleGoDashboard}
            >
              운동 기록 보기
            </button>

            <button type="button" className="retryButton" onClick={handleRetry}>
              다시 운동하기
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default ResultPage;