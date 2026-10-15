import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import api from "../../libs/api";

import eyeIcon from "../../assets/icons/icon=eye.svg";
import eyeOffIcon from "../../assets/icons/icon=eyeOff.svg";
import circleXIcon from "../../assets/icons/icon=CircleX.svg";

import "./LoginPage.css";

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const [tel, setTel] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMessage("");

    if (!tel.trim()) {
      setErrorMessage("전화번호를 입력해주세요.");
      return;
    }

    if (!password.trim()) {
      setErrorMessage("비밀번호를 입력해주세요.");
      return;
    }

    try {
      const response = await api.post("/api/auth/login", {
        tel: tel.replaceAll("-", ""),
        password,
      });

      const { accessToken, userId, name, role } = response.data;

      localStorage.setItem("accessToken", accessToken);
      localStorage.setItem("userId", userId);
      localStorage.setItem("name", name);
      localStorage.setItem("role", role);

      /* 비회원 운동 기록 연결 */
      const pendingSessionId = sessionStorage.getItem(
        "pendingExerciseSessionId",
      );

      if (pendingSessionId) {
        try {
          await api.post("/api/exercise/result", {
            sessionId: Number(pendingSessionId),
          });

          console.log("비회원 운동 기록 연결 완료:", pendingSessionId);

          sessionStorage.removeItem("pendingExerciseSessionId");

          try {
            await api.post(
              `/api/exercise/result/${pendingSessionId}/share-token`,
            );

            console.log("운동 결과 문자 발송 완료:", pendingSessionId);
          } catch (error) {
            console.error("운동 결과 문자 발송 실패:", error);
          }
        } catch (error) {
          console.error("비회원 운동 기록 연결 실패:", error);
        }
      }

      if (location.state?.fromExerciseResult === true) {
        navigate("/dashboard");
      } else {
        navigate("/");
      }
    } catch (error) {
      console.error("로그인 실패:", error);
      setErrorMessage("전화번호 또는 비밀번호를 다시 확인해주세요.");
    }
  };

  return (
    <main className="loginPage">
      <section className="loginCard">
        <div className="loginTitleArea">
          <h1>로그인</h1>
          <p>운동 기록을 이어서 확인해보세요.</p>
        </div>

        <form className="loginForm" onSubmit={handleLogin}>
          <div className="loginField">
            <label htmlFor="tel">전화번호</label>
            <input
              id="tel"
              type="tel"
              placeholder="010-1234-5678"
              value={tel}
              onChange={(e) => setTel(e.target.value)}
            />
          </div>

          <div className="loginField">
            <label htmlFor="password">비밀번호</label>

            <div className="passwordInputWrap">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="비밀번호를 입력해주세요."
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />

              <button
                type="button"
                className="passwordToggleButton"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={showPassword ? "비밀번호 숨기기" : "비밀번호 보기"}
              >
                <img
                  src={showPassword ? eyeOffIcon : eyeIcon}
                  alt=""
                  aria-hidden="true"
                />
              </button>
            </div>
          </div>

          {errorMessage && (
            <div className="loginErrorMessage">
              <img src={circleXIcon} alt="" aria-hidden="true" />
              <span>{errorMessage}</span>
            </div>
          )}

          <button type="submit" className="loginSubmitButton">
            로그인하기
          </button>
        </form>

        <div className="signupGuide">
          <span>처음이신가요?</span>
          <button type="button" onClick={() => navigate("/signup")}>
            회원가입하기
          </button>
        </div>

        <div className="loginDivider">
          <span />
          <p>또는</p>
          <span />
        </div>

        <button
          type="button"
          className="guestStartButton"
          onClick={() => navigate("/")}
        >
          운동 먼저 체험하기
        </button>
      </section>
    </main>
  );
}

export default LoginPage;
