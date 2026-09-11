import { useNavigate } from "react-router-dom";
import "../../styles/ResultPage.css";

function ResultPage() {
  const navigate = useNavigate();

  const resultData = {
    exerciseName: "팔 재활 운동",
    date: "2026년 4월 2일",
    totalCount: 10,
    part: "상체",
    duration: 12,
    accuracy: 82,
  };

  const handleRetry = () => {
    navigate("/exercise");
  };

  const handleGoDashboard = () => {
    navigate("/dashboard");
  };

  const handleGoHome = () => {
    navigate("/");
  };

  return (
    <div className="resultPage">
      <main className="resultContainer">
        <section className="resultCard">
          <div className="completeIcon">✓</div>

          <h1>오늘 운동 완료!</h1>

          <p className="resultSubText">
            {resultData.exerciseName} · {resultData.date}
          </p>

          <div className="resultStats">
            <div className="resultStatCard">
              <div className="resultValue">
                {resultData.totalCount}
                <span>회</span>
              </div>
              <p>총 수행 횟수</p>
            </div>

            <div className="resultStatCard">
              <div className="resultValue">{resultData.part}</div>
              <p>운동 부위</p>
            </div>

            <div className="resultStatCard">
              <div className="resultValue">
                {resultData.duration}
                <span>분</span>
              </div>
              <p>운동 시간</p>
            </div>

            <div className="resultStatCard">
              <div className="resultValue">
                {resultData.accuracy}
                <span>%</span>
              </div>
              <p>평균 정확도</p>
            </div>
          </div>

          <div className="resultButtons">
            <button type="button" onClick={handleRetry}>
              다시 하기
            </button>

            <button type="button" onClick={handleGoDashboard}>
              운동 기록 보기
            </button>

            <button type="button" onClick={handleGoHome}>
              홈으로
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default ResultPage;
