import { useEffect, useState } from "react";
import ExerciseCard from "../../components/ExerciseCard";
import "../../styles/MainPage.css";

function MainPage() {
  const [showScrollArrow, setShowScrollArrow] = useState(true);

  useEffect(() => {
    const checkScroll = () => {
      const scrollTop = window.scrollY;
      const windowHeight = window.innerHeight;
      const fullHeight = document.documentElement.scrollHeight;

      if (scrollTop + windowHeight >= fullHeight - 10) {
        setShowScrollArrow(false);
      } else {
        setShowScrollArrow(true);
      }
    };

    checkScroll();

    window.addEventListener("scroll", checkScroll);
    window.addEventListener("resize", checkScroll);

    return () => {
      window.removeEventListener("scroll", checkScroll);
      window.removeEventListener("resize", checkScroll);
    };
  }, []);

  const scrollDown = () => {
    window.scrollBy({
      top: window.innerHeight - 76,
      behavior: "smooth",
    });
  };

  const scrollToExercise = () => {
  const exerciseSection = document.getElementById("exercise-section");
  const headerHeight = document.querySelector(".header")?.offsetHeight || 76;

  if (exerciseSection) {
    const targetPosition =
      exerciseSection.getBoundingClientRect().top + window.scrollY - headerHeight;

    window.scrollTo({
      top: targetPosition,
      behavior: "smooth",
    });
  }
};
  const isLoggedIn = false;

  return (
    <div className="home">
      <main>
        <section className="heroSection">
          <div className="imageBox">
            큰 이미지 / <br />
            운동 영상 소스
          </div>

          <div className="heroText">
            <p className="smallTitle">재활 운동을 더 쉽고 정확하게</p>

            <h1>
              오늘도 건강하게
              <br />
              재활 운동 시작해요
            </h1>

            <p className="description">
              척추관절과 근육을 센서값으로 측정하고, 피드백을 제공합니다.
              <br />
              로그인 없이도 바로 운동을 시작해보세요!
            </p>

            <button className="startButton" onClick={scrollToExercise}>운동 바로 시작 →</button>
          </div>
        </section>

        <section id="exercise-section" className="exerciseSection">
          <h2>오늘 운동하고 싶은 부위를 선택하세요</h2>

          <div className="cardWrap">
            <ExerciseCard
              title="상체 운동"
              description={
                <>
                  어깨, 팔, 가슴 운동 등
                  <br />
                  상체 중심 운동을 진행합니다.
                </>
              }
            />

            <ExerciseCard
              title="어깨 운동"
              description={
                <>
                  어깨 관절과 팔 운동을 돕고
                  <br />
                  균형을 맞춰줍니다.
                </>
              }
            />

            <ExerciseCard
              title="하체 운동"
              description={
                <>
                  골반, 무릎과 발목 등
                  <br />
                  하체 근력을 관리합니다.
                </>
              }
            />
          </div>
        </section>
      </main>
      {showScrollArrow && (
        <button className="scrollArrow" onClick={scrollDown}>
            ˅
        </button>
      )}
    </div>
  );
}

export default MainPage;