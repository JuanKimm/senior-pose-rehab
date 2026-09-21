import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import volumeIcon from "../../assets/icons/icon=Volume2.svg";
import volumeOffIcon from "../../assets/icons/icon=VolumeX.svg";
import circleCheckIcon from "../../assets/icons/icon=CircleCheck.svg";
import alertErrorIcon from "../../assets/icons/icon=TriangleAlertError.svg";
import cameraIcon from "../../assets/icons/icon=camera.svg";
import cameraOffIcon from "../../assets/icons/icon=cameraOff.svg";

import "../../styles/ExercisePage.css";

function ExercisePage() {
  const navigate = useNavigate();

  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const [elapsedTime, setElapsedTime] = useState(0);
  const [currentCount] = useState(4);
  const [targetCount] = useState(12);

  const [cameraStatus, setCameraStatus] = useState("connecting");
  const [cameraError, setCameraError] = useState("");

  const [isVoiceOn, setIsVoiceOn] = useState(true);
  const [showEndModal, setShowEndModal] = useState(false);

  const progress = Math.round((currentCount / targetCount) * 100);

  /* =========================
     운동 시간
  ========================= */

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  /* =========================
     카메라 연결
  ========================= */

  const startCamera = async () => {
    setCameraStatus("connecting");
    setCameraError("");

    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error("이 브라우저에서는 카메라를 사용할 수 없습니다.");
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      setCameraStatus("connected");
    } catch (error) {
      console.error("카메라 연결 실패:", error);

      if (
        error.name === "NotAllowedError" ||
        error.name === "PermissionDeniedError"
      ) {
        setCameraStatus("permissionDenied");
        setCameraError("카메라 사용 권한을 허용해주세요.");
      } else {
        setCameraStatus("error");
        setCameraError(
          "카메라를 확인하기 어려워요. 잠시 후 다시 시도해주세요.",
        );
      }
    }
  };

  useEffect(() => {
    startCamera();

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  /* =========================
     시간 표시
  ========================= */

  const formatTime = (seconds) => {
    const minute = Math.floor(seconds / 60);
    const second = seconds % 60;

    return `${String(minute).padStart(2, "0")}:${String(second).padStart(
      2,
      "0",
    )}`;
  };

  /* =========================
     운동 종료
  ========================= */

  const handleEndButtonClick = () => {
    setShowEndModal(true);
  };

  const handleContinueExercise = () => {
    setShowEndModal(false);
  };

  const handleEndExercise = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }

    navigate("/result");
  };

  return (
    <div className="exercisePage">
      <main className="exerciseContainer">
        {/* =========================
            제목 + 음성 안내
        ========================= */}

        <div className="exerciseTitleRow">
          <div className="exercisePageTitle">
            <h1>어깨 운동</h1>
            <p>화면의 동작을 천천히 따라 해보세요.</p>
          </div>

          <button
            type="button"
            className={`voiceGuideButton ${isVoiceOn ? "active" : ""}`}
            onClick={() => setIsVoiceOn((prev) => !prev)}
          >
            <img
              src={isVoiceOn ? volumeIcon : volumeOffIcon}
              alt=""
              aria-hidden="true"
            />

            {isVoiceOn ? "음성 안내 켜짐" : "음성 안내 켜기"}
          </button>
        </div>

        {/* =========================
            운동 화면
        ========================= */}

        <div className="exerciseMainGrid">
          {/* 왼쪽 - 따라 할 동작 */}

          <section className="referencePanel">
            <h2>따라 할 동작</h2>

            <div className="referenceVideo">
              <span>기준 영상</span>
            </div>
          </section>

          {/* 오른쪽 */}

          <div className="exerciseSideColumn">
            {/* 운동 진행 */}

            <section className="progressPanel">
              <h2>운동 진행</h2>

              <div className="countText">
                <strong>{currentCount}</strong>
                <span> / {targetCount}회</span>
              </div>

              <div className="exerciseProgressBar">
                <div
                  className="exerciseProgressValue"
                  style={{ width: `${progress}%` }}
                />
              </div>

              <p>운동 시간&nbsp; {formatTime(elapsedTime)}</p>
            </section>

            {/* 내 모습 */}

            <section className="cameraPanel">
              <h2>내 모습</h2>

              <div className="cameraBox">
                {/* 실제 웹캠 */}

                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className={
                    cameraStatus === "connected"
                      ? "webcamVideo visible"
                      : "webcamVideo"
                  }
                />

                {/* 카메라 연결 중 */}

                {cameraStatus === "connecting" && (
                  <div className="cameraState">
                    <img
                      src={cameraIcon}
                      className="cameraStateIcon"
                      alt=""
                      aria-hidden="true"
                    />

                    <strong>카메라를 연결하고 있어요.</strong>
                  </div>
                )}

                {/* 카메라 권한 없음 */}

                {cameraStatus === "permissionDenied" && (
                  <div className="cameraState">
                    <img
                      src={cameraOffIcon}
                      className="cameraStateIcon"
                      alt=""
                      aria-hidden="true"
                    />

                    <strong>{cameraError}</strong>

                    <button
                      type="button"
                      className="cameraRetryButton"
                      onClick={startCamera}
                    >
                      카메라 연결하기
                    </button>
                  </div>
                )}

                {/* 카메라 오류 */}

                {cameraStatus === "error" && (
                  <div className="cameraState cameraErrorState">
                    <img
                      src={alertErrorIcon}
                      className="cameraStateIcon"
                      alt=""
                      aria-hidden="true"
                    />

                    <strong>{cameraError}</strong>

                    <button
                      type="button"
                      className="cameraRetryButton"
                      onClick={startCamera}
                    >
                      다시 시도하기
                    </button>
                  </div>
                )}
              </div>
            </section>
          </div>
        </div>

        {/* =========================
            자세 피드백
        ========================= */}

        <div className="exerciseFeedback">
          <img
            src={circleCheckIcon}
            className="feedbackIcon"
            alt=""
            aria-hidden="true"
          />

          <strong>좋아요. 자세가 안정적입니다.</strong>
        </div>

        {/* =========================
            운동 종료
        ========================= */}

        <button
          type="button"
          className="endExerciseButton"
          onClick={handleEndButtonClick}
        >
          운동 종료하기
        </button>
      </main>

      {/* =========================
          운동 종료 확인 팝업
      ========================= */}

      {showEndModal && (
        <div className="exerciseModalBackdrop">
          <div className="exerciseEndModal">
            <strong>운동을 종료하시겠어요?</strong>

            <div className="exerciseModalButtons">
              <button
                type="button"
                className="continueExerciseButton"
                onClick={handleContinueExercise}
              >
                계속 운동하기
              </button>

              <button
                type="button"
                className="confirmEndButton"
                onClick={handleEndExercise}
              >
                종료하기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ExercisePage;
