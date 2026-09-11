import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/ExercisePage.css";

function ExercisePage() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const [elapsedTime, setElapsedTime] = useState(0);
  const [currentCount] = useState(4);
  const [targetCount] = useState(12);

  const [cameraError, setCameraError] = useState("");
  const [isVoiceOn, setIsVoiceOn] = useState(true);

  const progress = Math.round((currentCount / targetCount) * 100);

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });

        streamRef.current = stream;

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (error) {
        console.error("카메라 연결 실패:", error);
        setCameraError(
          "카메라 연결에 실패했습니다. 카메라 권한을 확인해주세요.",
        );
      }
    };

    startCamera();

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const formatTime = (seconds) => {
    const minute = Math.floor(seconds / 60);
    const second = seconds % 60;

    return `${String(minute).padStart(2, "0")}:${String(second).padStart(
      2,
      "0",
    )}`;
  };

  const handleEndExercise = () => {
    navigate("/result");
  };

  return (
    <div className="exercisePage">
      <main className="exerciseContainer">
        <div className="exerciseTop">
          <div className="exerciseInfo">
            <div className="infoItem">
              <span className="infoLabel">운동 부위</span>
              <strong>상체</strong>
            </div>

            <div className="infoItem">
              <span className="infoLabel">진행 시간</span>
              <strong>{formatTime(elapsedTime)}</strong>
            </div>

            <div className="infoItem">
              <span className="infoLabel">진행 횟수</span>
              <strong>
                {currentCount}/{targetCount}
              </strong>
            </div>

            <div className="infoItem progressItem">
              <span className="infoLabel">진행률</span>

              <div className="progressBar">
                <div
                  className="progressValue"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          </div>

          <button
            type="button"
            className={`voiceButton ${isVoiceOn ? "active" : ""}`}
            onClick={() => setIsVoiceOn((prev) => !prev)}
          >
            음성 안내 {isVoiceOn ? "ON" : "OFF"}
          </button>
        </div>

        <div className="exerciseVideoArea">
          <section className="referenceArea">
            <div className="videoLabel">기준 영상</div>

            <div className="referenceVideo">기준 운동 영상</div>
          </section>

          <section className="webcamArea">
            <div className="videoLabel">실시간 웹캠</div>

            <div className="webcamBox">
              {cameraError ? (
                <div className="cameraError">
                  <strong>카메라를 사용할 수 없습니다.</strong>
                  <p>{cameraError}</p>
                </div>
              ) : (
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="webcamVideo"
                />
              )}
            </div>
          </section>
        </div>

        <div className="feedbackBox">
          <strong>자세를 확인하고 있어요.</strong>
          <span>기준 영상을 따라 천천히 움직여주세요.</span>
        </div>

        <button
          type="button"
          className="endExerciseButton"
          onClick={handleEndExercise}
        >
          운동 종료하기
        </button>
      </main>
    </div>
  );
}

export default ExercisePage;
