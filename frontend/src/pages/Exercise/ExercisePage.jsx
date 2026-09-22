import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../../libs/api";

import volumeIcon from "../../assets/icons/icon=Volume2.svg";
import volumeOffIcon from "../../assets/icons/icon=VolumeX.svg";
import circleCheckIcon from "../../assets/icons/icon=CircleCheck.svg";
import alertErrorIcon from "../../assets/icons/icon=TriangleAlertError.svg";
import cameraIcon from "../../assets/icons/icon=camera.svg";
import cameraOffIcon from "../../assets/icons/icon=cameraOff.svg";

import "../../styles/ExercisePage.css";

let exerciseSessionPromise = null;

const createExerciseSession = () => {
  const savedSessionId = sessionStorage.getItem("exerciseSessionId");

  if (savedSessionId) {
    return Promise.resolve(Number(savedSessionId));
  }

  if (!exerciseSessionPromise) {
    exerciseSessionPromise = api
      .post("/api/exercise/session/start", {
        exerciseTypeId: 1,
      })
      .then((response) => {
        const sessionId = response.data.sessionId;

        sessionStorage.setItem("exerciseSessionId", String(sessionId));

        return sessionId;
      })
      .catch((error) => {
        exerciseSessionPromise = null;
        throw error;
      });
  }

  return exerciseSessionPromise;
};

function ExercisePage() {
  const navigate = useNavigate();

  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const socketRef = useRef(null);
  const sessionIdRef = useRef(null);

  const [elapsedTime, setElapsedTime] = useState(0);
  const [currentCount, setCurrentCount] = useState(0);
  const [aiStatus, setAiStatus] = useState("connecting");
  const [aiFeedback, setAiFeedback] =
    useState("카메라 연결을 기다리고 있어요.");
  const [aiAccuracy, setAiAccuracy] = useState(0);
  const [aiFrameUrl, setAiFrameUrl] = useState(null);
  const aiFrameUrlRef = useRef(null);
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
   AI WebSocket 연결
  ========================= */

  useEffect(() => {
    let isActive = true;
    let socket = null;

    const connectAi = async () => {
      try {
        // 1. 백엔드에서 실제 운동 세션 생성
        const sessionId = await createExerciseSession();

        if (!isActive) {
          return;
        }

        sessionIdRef.current = sessionId;

        console.log("운동 세션 준비 완료:", sessionId);

        // 2. 백엔드에서 받은 sessionId로 AI WebSocket 연결
        socket = new WebSocket(
          `ws://127.0.0.1:8000/ws/exercise/${sessionId}?exercise_code=shoulder_open_close`,
        );

        socketRef.current = socket;

        socket.onopen = () => {
          if (!isActive) {
            socket.close();
            return;
          }

          console.log("AI WebSocket 연결 성공");
        };

        socket.onmessage = (event) => {
          if (!isActive) {
            return;
          }

          // AI가 보내는 스켈레톤 JPEG 처리
          if (typeof event.data !== "string") {
            if (event.data instanceof Blob) {
              const nextFrameUrl = URL.createObjectURL(event.data);

              if (aiFrameUrlRef.current) {
                URL.revokeObjectURL(aiFrameUrlRef.current);
              }

              aiFrameUrlRef.current = nextFrameUrl;
              setAiFrameUrl(nextFrameUrl);
            }

            return;
          }

          try {
            const data = JSON.parse(event.data);

            switch (data.type) {
              case "ready":
                console.log("AI 준비 완료:", data);
                setAiStatus("ready");
                break;

              case "analysis":
                console.log("AI 분석 결과:", data);

                setAiStatus("analysis");
                setCurrentCount(data.rep_count ?? 0);
                setAiAccuracy(data.accuracy ?? 0);
                setAiFeedback(data.feedback || "자세를 확인하고 있어요.");
                break;

              case "summary":
                console.log("AI 운동 종료 요약:", data);

                setAiStatus("summary");

                sessionStorage.setItem("exerciseSummary", JSON.stringify(data));

                if (streamRef.current) {
                  streamRef.current
                    .getTracks()
                    .forEach((track) => track.stop());
                }

                // 다음 운동에서는 새 백엔드 세션을 만들도록 초기화
                sessionStorage.removeItem("exerciseSessionId");
                exerciseSessionPromise = null;
                sessionIdRef.current = null;

                if (aiFrameUrlRef.current) {
                  URL.revokeObjectURL(aiFrameUrlRef.current);
                  aiFrameUrlRef.current = null;
                }

                navigate("/result");
                break;

              case "error":
                console.error("AI 서버 오류:", data);
                setAiStatus("error");
                setAiFeedback(
                  data.message || "AI 분석 중 오류가 발생했습니다.",
                );
                break;

              default:
                console.log("알 수 없는 AI 메시지:", data);
            }
          } catch (error) {
            console.error("AI 메시지 처리 실패:", error);
          }
        };

        socket.onerror = (error) => {
          if (!isActive) {
            return;
          }

          console.error("AI WebSocket 오류:", error);
        };

        socket.onclose = () => {
          if (!isActive) {
            return;
          }

          console.log("AI WebSocket 연결 종료");
        };
      } catch (error) {
        if (!isActive) {
          return;
        }

        console.error("운동 세션 생성 또는 AI 연결 실패:", error);

        setAiStatus("error");
        setAiFeedback("운동을 시작하지 못했어요.");
      }
    };

    connectAi();

    return () => {
      isActive = false;

      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }

      if (socketRef.current === socket) {
        socketRef.current = null;
      }
    };
  }, [navigate]);

  /* =========================
   웹캠 프레임 → AI 전송
  ========================= */

  useEffect(() => {
    if (cameraStatus !== "connected") {
      return;
    }

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");

    if (!context) {
      return;
    }

    const frameTimer = setInterval(() => {
      const video = videoRef.current;
      const socket = socketRef.current;

      if (
        !video ||
        !socket ||
        socket.readyState !== WebSocket.OPEN ||
        video.readyState < 2
      ) {
        return;
      }

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      if (!canvas.width || !canvas.height) {
        return;
      }

      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(
        (blob) => {
          if (!blob) {
            return;
          }

          if (socket.readyState === WebSocket.OPEN) {
            socket.send(blob);
          }
        },
        "image/jpeg",
        0.8,
      );
    }, 200);

    return () => {
      clearInterval(frameTimer);
    };
  }, [cameraStatus]);

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
    const socket = socketRef.current;

    if (socket && socket.readyState === WebSocket.OPEN) {
      console.log("AI에 운동 종료 요청 전송");
      socket.send(JSON.stringify({ type: "stop" }));
      setShowEndModal(false);
      return;
    }

    console.log("AI 연결이 없어 결과 화면으로 바로 이동");
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
              <video
                src="/videos/shoulder_open_close.mp4"
                autoPlay
                loop
                muted
                playsInline
                className="referenceVideoPlayer"
              />
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

                {aiFrameUrl && (
                  <img
                    src={aiFrameUrl}
                    className="aiFrameImage"
                    alt="AI 자세 분석 화면"
                  />
                )}

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

          <strong>{aiFeedback}</strong>
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
