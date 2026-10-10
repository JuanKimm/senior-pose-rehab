import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import api from "../../libs/api";

import volumeIcon from "../../assets/icons/icon=Volume2.svg";
import volumeOffIcon from "../../assets/icons/icon=VolumeX.svg";
import circleCheckIcon from "../../assets/icons/icon=CircleCheck.svg";
import alertErrorIcon from "../../assets/icons/icon=TriangleAlertError.svg";
import cameraIcon from "../../assets/icons/icon=camera.svg";
import cameraOffIcon from "../../assets/icons/icon=cameraOff.svg";

import "../../styles/ExercisePage.css";

const EXERCISE_CONFIG = {
  shoulder: {
    title: "어깨 운동",
    exerciseTypeId: 1,
    exerciseCode: "shoulder_open_close",
    videoSrc: "/videos/shoulder_open_close.mp4",
  },

  upper: {
    title: "상체 운동",
    exerciseTypeId: 2,
    exerciseCode: "gaze_pull",
    videoSrc: "/videos/gaze_pull.mp4",
  },
};

let exerciseSessionPromise = null;

const createExerciseSession = (exerciseTypeId) => {
  const savedSessionId = sessionStorage.getItem("exerciseSessionId");

  if (savedSessionId) {
    return Promise.resolve(Number(savedSessionId));
  }

  if (!exerciseSessionPromise) {
    exerciseSessionPromise = api
      .post("/api/exercise/session/start", {
        exerciseTypeId,
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
  const [searchParams] = useSearchParams();

  const exerciseType = searchParams.get("type") || "shoulder";

  const exerciseConfig =
    EXERCISE_CONFIG[exerciseType] || EXERCISE_CONFIG.shoulder;
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

  /* =========================
     피드백 표시 제어
  ========================= */

  const feedbackLockRef = useRef(false);
  const pendingFeedbackRef = useRef("");
  const feedbackTimerRef = useRef(null);

  const displayedFeedbackRef = useRef("카메라 연결을 기다리고 있어요.");

  const [targetCount] = useState(12);

  /* =========================
     카메라 상태
  ========================= */

  const [cameraStatus, setCameraStatus] = useState("idle");

  const [cameraError, setCameraError] =
    useState("카메라 사용 권한을 허용해주세요.");

  /* =========================
     음성 안내
  ========================= */

  const [isVoiceOn, setIsVoiceOn] = useState(true);

  const isVoiceOnRef = useRef(true);

  // 현재 우리 음성이 재생 중인지
  const isSpeakingRef = useRef(false);

  // 음성 재생 중 새 피드백이 들어오면
  // 가장 최근 문구 하나만 저장
  const pendingSpeechRef = useRef("");

  // 같은 문장을 불필요하게 연속 재생하지 않기 위해 저장
  const lastSpokenTextRef = useRef("");

  const speak = (text) => {
    if (!text) {
      return;
    }

    if (!isVoiceOnRef.current) {
      return;
    }

    if (!("speechSynthesis" in window)) {
      console.warn("이 브라우저에서는 음성 안내를 지원하지 않습니다.");
      return;
    }

    // 항상 가장 최신 문구로 갱신
    pendingSpeechRef.current = text;

    // 현재 음성을 읽고 있다면
    // 지금 음성은 끊지 않고 끝날 때까지 기다림
    if (isSpeakingRef.current) {
      return;
    }

    const playNextSpeech = () => {
      if (!isVoiceOnRef.current) {
        pendingSpeechRef.current = "";
        return;
      }

      const nextText = pendingSpeechRef.current;

      if (!nextText) {
        return;
      }

      pendingSpeechRef.current = "";

      // 방금 읽은 문장과 완전히 동일하면 다시 읽지 않음
      if (nextText === lastSpokenTextRef.current) {
        return;
      }

      const utterance = new SpeechSynthesisUtterance(nextText);

      utterance.lang = "ko-KR";
      utterance.rate = 0.95;
      utterance.pitch = 1;
      utterance.volume = 1;

      isSpeakingRef.current = true;
      lastSpokenTextRef.current = nextText;

      const handleSpeechEnd = () => {
        isSpeakingRef.current = false;

        if (!isVoiceOnRef.current) {
          pendingSpeechRef.current = "";
          return;
        }

        // 읽는 동안 새 피드백이 들어왔다면
        // 가장 최신 문구 하나만 이어서 읽음
        const latestText = pendingSpeechRef.current;

        if (latestText && latestText !== lastSpokenTextRef.current) {
          playNextSpeech();
        }
      };

      utterance.onend = handleSpeechEnd;

      utterance.onerror = (event) => {
        // 사용자가 음성 OFF 또는 페이지 이동으로 cancel한 경우도
        // error 이벤트가 발생할 수 있음
        if (event.error !== "canceled") {
          console.warn("음성 안내 재생 오류:", event.error);
        }

        handleSpeechEnd();
      };

      window.speechSynthesis.speak(utterance);
    };

    playNextSpeech();
  };

  const stopVoice = () => {
    pendingSpeechRef.current = "";
    isSpeakingRef.current = false;

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  };

  const handleVoiceToggle = () => {
    const nextValue = !isVoiceOn;

    setIsVoiceOn(nextValue);
    isVoiceOnRef.current = nextValue;

    if (!nextValue) {
      stopVoice();
      return;
    }

    // 다시 켰을 때 현재 화면의 안내를 한 번 읽음
    if (cameraStatus === "connected") {
      // OFF 동안 읽었던 것으로 처리된 문구도
      // 다시 들을 수 있도록 초기화
      lastSpokenTextRef.current = "";

      speak(displayedFeedbackRef.current);
    }
  };

  const [showEndModal, setShowEndModal] = useState(false);

  const progress = Math.min(
    Math.round((currentCount / targetCount) * 100),
    100,
  );

  /* =========================
     AI 피드백 업데이트
  ========================= */

  const updateFeedback = (nextFeedback) => {
    if (!nextFeedback) {
      return;
    }

    pendingFeedbackRef.current = nextFeedback;

    // 현재 피드백을 보여주는 중이면
    // 최신 피드백만 기억
    if (feedbackLockRef.current) {
      return;
    }

    // 이미 같은 문구가 표시되어 있으면 변경하지 않음
    if (nextFeedback === displayedFeedbackRef.current) {
      return;
    }

    displayedFeedbackRef.current = nextFeedback;

    setAiFeedback(nextFeedback);

    // 화면에 새롭게 표시되는 피드백을 음성으로 안내
    speak(nextFeedback);

    feedbackLockRef.current = true;

    feedbackTimerRef.current = setTimeout(() => {
      feedbackLockRef.current = false;

      const latestFeedback = pendingFeedbackRef.current;

      // 1.5초 동안 새로운 피드백이 들어왔다면
      // 가장 최근 문구를 다음에 표시
      if (latestFeedback && latestFeedback !== displayedFeedbackRef.current) {
        updateFeedback(latestFeedback);
      }
    }, 1500);
  };

  /* =========================
     운동 시간
  ========================= */

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);

    return () => {
      clearInterval(timer);
    };
  }, []);

  /* =========================
     페이지 종료 시 정리
  ========================= */

  useEffect(() => {
    return () => {
      if (feedbackTimerRef.current) {
        clearTimeout(feedbackTimerRef.current);
      }

      stopVoice();
    };
  }, []);

  /* =========================
     AI WebSocket 연결
  ========================= */

  useEffect(() => {
    let isActive = true;
    let socket = null;

    const connectAi = async () => {
      try {
        const sessionId = await createExerciseSession(
          exerciseConfig.exerciseTypeId,
        );

        if (!isActive) {
          return;
        }

        sessionIdRef.current = sessionId;

        console.log("운동 세션 준비 완료:", sessionId);

        socket = new WebSocket(
          `ws://127.0.0.1:8000/ws/exercise/${sessionId}?exercise_code=${exerciseConfig.exerciseCode}`,
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

          /* =========================
             AI 스켈레톤 이미지
          ========================= */

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

                updateFeedback(data.feedback);

                break;

              case "summary":
                console.log("AI 운동 종료 요약:", data);

                setAiStatus("summary");

                sessionStorage.setItem("exerciseSummary", JSON.stringify(data));

                /* 비회원 운동 세션 임시 보관 */
                const finishedSessionId = sessionIdRef.current;
                const accessToken = localStorage.getItem("accessToken");

                if (!accessToken && finishedSessionId) {
                  sessionStorage.setItem(
                    "pendingExerciseSessionId",
                    String(finishedSessionId),
                  );

                  console.log("비회원 운동 세션 임시 보관:", finishedSessionId);
                }
                /* 로그인 회원은 운동 완료 후 결과 알림 발송 */
                if (accessToken && finishedSessionId && data.backend_sent) {
                  api
                    .post(
                      `/api/exercise/result/${finishedSessionId}/share-token`,
                    )
                    .then(() => {
                      console.log("운동 결과 문자 발송 완료");
                    })
                    .catch((error) => {
                      console.error("운동 결과 문자 발송 실패:", error);
                    });
                }

                /* 카메라 종료 */

                if (streamRef.current) {
                  streamRef.current
                    .getTracks()
                    .forEach((track) => track.stop());
                }

                /* 음성 종료 */

                stopVoice();

                /* 다음 운동을 위해 세션 초기화 */

                sessionStorage.removeItem("exerciseSessionId");

                exerciseSessionPromise = null;
                sessionIdRef.current = null;

                /* AI 이미지 URL 정리 */

                if (aiFrameUrlRef.current) {
                  URL.revokeObjectURL(aiFrameUrlRef.current);

                  aiFrameUrlRef.current = null;
                }

                navigate(`/result?type=${exerciseType}`);

                break;

              case "error":
                console.error("AI 서버 오류:", data);

                setAiStatus("error");

                updateFeedback(
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

      displayedFeedbackRef.current = "자세를 확인하고 있어요.";

      setAiFeedback("자세를 확인하고 있어요.");

      /* =========================
         첫 음성 안내
      ========================= */

      lastSpokenTextRef.current = "";

      speak("화면의 동작을 천천히 따라 해보세요.");
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

  /* =========================
     페이지 종료 시 카메라 정리

     자동으로 startCamera() 호출하지 않음
  ========================= */

  useEffect(() => {
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

      stopVoice();

      socket.send(
        JSON.stringify({
          type: "stop",
        }),
      );

      setShowEndModal(false);

      return;
    }

    stopVoice();

    console.log("AI 연결이 없어 결과 화면으로 바로 이동");

    navigate(`/result?type=${exerciseType}`);
  };

  return (
    <div className="exercisePage">
      <main className="exerciseContainer">
        {/* =========================
            제목 + 음성 안내
        ========================= */}

        <div className="exerciseTitleRow">
          <div className="exercisePageTitle">
            <h1>{exerciseConfig.title}</h1>

            <p>화면의 동작을 천천히 따라 해보세요.</p>
          </div>

          <button
            type="button"
            className={`voiceGuideButton ${isVoiceOn ? "active" : ""}`}
            onClick={handleVoiceToggle}
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
                src={exerciseConfig.videoSrc}
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
                  style={{
                    width: `${progress}%`,
                  }}
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

                {/* AI 자세 분석 화면 */}

                {aiFrameUrl && (
                  <img
                    src={aiFrameUrl}
                    className="aiFrameImage"
                    alt="AI 자세 분석 화면"
                  />
                )}

                {/* 카메라 연결 전 */}

                {cameraStatus === "idle" && (
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
