import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/MainPage.css";

function MainPage() {
  const navigate = useNavigate();
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
    const exerciseSection = document.getElementById("exercise-section");
    const headerHeight = document.querySelector(".header")?.offsetHeight || 76;

    if (exerciseSection) {
      const targetPosition =
        exerciseSection.getBoundingClientRect().top +
        window.scrollY -
        headerHeight;

      window.scrollTo({
        top: targetPosition,
        behavior: "smooth",
      });
    }
  };

  const scrollToExercise = () => {
    scrollDown();
  };

  const goToExercise = () => {
    navigate("/exercise");
  };

  return (
    <div className="home">
      <main>
        {/* 메인 영역 */}
        <section className="heroSection">
          <div className="heroImagePlaceholder">
            <span>메인 이미지 준비 중</span>
          </div>

          <div className="heroText">
            <p className="smallTitle">카메라만 있으면 바로 시작할 수 있어요</p>

            <h1>
              오늘도 편안하게
              <br />
              재활 운동을 시작해보세요.
            </h1>

            <p className="description">
              카메라로 운동 자세를 확인하고,
              <br />
              자세 안내를 받으며 천천히 운동해보세요!
            </p>

            <button
              type="button"
              className="startButton"
              onClick={scrollToExercise}
            >
              운동 선택하기 <span>→</span>
            </button>
          </div>
        </section>

        {/* 운동 선택 영역 */}
        <section id="exercise-section" className="exerciseSection">
          <div className="exerciseTitle">
            <p>집중 운동 영역</p>
            <h2>오늘 운동하고 싶은 부위를 선택하세요.</h2>
          </div>

          <div className="cardWrap">
            <article className="exerciseCard">
              <div className="cardImagePlaceholder">
                <span>상체 운동 이미지</span>
              </div>

              <div className="cardContent">
                <h3>상체 운동</h3>
                <p>팔과 가슴을 천천히 움직이며 상체를 풀어보세요.</p>

                <button
                  type="button"
                  className="cardButton"
                  onClick={goToExercise}
                >
                  운동 보기 <span>→</span>
                </button>
              </div>
            </article>

            <article className="exerciseCard">
              <div className="cardImagePlaceholder">
                <span>어깨 운동 이미지</span>
              </div>

              <div className="cardContent">
                <h3>어깨 운동</h3>
                <p>어깨와 팔을 부드럽게 움직이며 따라해보세요.</p>

                <button
                  type="button"
                  className="cardButton"
                  onClick={goToExercise}
                >
                  운동 보기 <span>→</span>
                </button>
              </div>
            </article>

            <article className="exerciseCard">
              <div className="cardImagePlaceholder">
                <span>하체 운동 이미지</span>
              </div>

              <div className="cardContent">
                <h3>하체 운동</h3>
                <p>다리와 무릎을 천천히 움직이며 하체를 단련해보세요.</p>

                <button
                  type="button"
                  className="cardButton"
                  onClick={goToExercise}
                >
                  운동 보기 <span>→</span>
                </button>
              </div>
            </article>
          </div>
        </section>
      </main>

      {showScrollArrow && (
        <button
          type="button"
          className="scrollArrow"
          onClick={scrollDown}
          aria-label="운동 영역으로 이동"
        >
          ˅
        </button>
      )}
    </div>
  );
}

export default MainPage;
