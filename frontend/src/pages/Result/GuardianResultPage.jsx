import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "../../styles/ResultPage.css";

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
   날짜 변환
========================= */

const formatDate = (date) => {
  if (!date) return "-";

  const parsedDate = new Date(date);

  if (Number.isNaN(parsedDate.getTime())) {
    return date;
  }

  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(parsedDate);
};

function GuardianResultPage() {
  const { token } = useParams();

  const [resultData, setResultData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  /* =========================
     공유 운동 결과 불러오기
  ========================= */

  useEffect(() => {
    const fetchSharedResult = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `http://localhost:8080/api/exercise/result/share/${encodeURIComponent(
            token,
          )}`,
        );

        if (!response.ok) {
          throw new Error("공유 운동 결과 조회 실패");
        }

        const data = await response.json();

        setResultData({
          exerciseName: data.bodyPart ? `${data.bodyPart} 운동` : "운동",
          date: formatDate(data.exerciseDate),
          totalCount: data.totalCount ?? 0,
          duration: formatDuration(data.durationSec ?? 0),
          accuracy: Math.round(data.accuracy ?? 0),
        });
      } catch (error) {
        console.error("보호자 운동 결과 조회 실패:", error);
        setError("유효하지 않거나 만료된 링크입니다.");
      } finally {
        setLoading(false);
      }
    };

    if (!token) {
      setError("유효하지 않은 링크입니다.");
      setLoading(false);
      return;
    }

    fetchSharedResult();
  }, [token]);

  /* =========================
     로딩 화면
  ========================= */

  if (loading) {
    return (
      <div className="resultPage">
        <main className="resultContainer">
          <section className="resultCard">
            <h1>운동 결과를 불러오고 있어요.</h1>

            <p className="guardianMessage">잠시만 기다려 주세요.</p>
          </section>
        </main>
      </div>
    );
  }

  /* =========================
     오류 화면
  ========================= */

  if (error) {
    return (
      <div className="resultPage">
        <main className="resultContainer">
          <section className="resultCard">
            <div className="completeIcon">!</div>

            <h1>운동 결과를 확인할 수 없어요.</h1>

            <p className="guardianMessage">{error}</p>
          </section>
        </main>
      </div>
    );
  }

  return (
    <div className="resultPage">
      <main className="resultContainer">
        <section className="resultCard">
          {/* 완료 아이콘 */}
          <div className="completeIcon">✓</div>

          {/* 제목 */}
          <h1>운동을 완료했어요.</h1>

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

          {/* 보호자 안내 */}
          <p className="guardianNotice">
            해당 운동 결과는 링크 발급 후 24시간 동안 확인할 수 있습니다.
          </p>
        </section>
      </main>
    </div>
  );
}

export default GuardianResultPage;
