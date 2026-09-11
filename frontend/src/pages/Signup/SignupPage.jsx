import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../../libs/api";

import eyeIcon from "../../assets/icons/24/icon=eye, size=24, color=default.svg";
import eyeOffIcon from "../../assets/icons/24/icon=eyeOff, size=24, color=default.svg";

import "./SignupPage.css";

function SignupPage() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [tel, setTel] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

  const [agreed, setAgreed] = useState(false);
  const [errors, setErrors] = useState({});

  const [signupComplete, setSignupComplete] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();

    const nextErrors = {};
    const cleanTel = tel.replaceAll("-", "");

    if (!name.trim()) {
      nextErrors.name = "이름을 입력해주세요.";
    }

    if (!cleanTel) {
      nextErrors.tel = "전화번호를 입력해주세요.";
    } else if (!/^010\d{8}$/.test(cleanTel)) {
      nextErrors.tel = "전화번호를 다시 확인해주세요.";
    }

    if (!password) {
      nextErrors.password = "비밀번호를 입력해주세요.";
    } else if (!/^\d{6}$/.test(password)) {
      nextErrors.password = "비밀번호는 숫자 6자리로 입력해주세요.";
    }

    if (!passwordConfirm) {
      nextErrors.passwordConfirm = "비밀번호를 다시 입력해주세요.";
    } else if (password !== passwordConfirm) {
      nextErrors.passwordConfirm =
        "비밀번호가 서로 같지 않아요. 다시 확인해주세요.";
    }

    if (!agreed) {
      nextErrors.agreed = "이용약관과 개인정보 처리 방침에 동의해주세요.";
    }

    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    try {
      await api.post("/api/auth/signup", {
        name: name.trim(),
        tel: cleanTel,
        password,
        guardianTel: "",
      });

      setSignupComplete(true);
    } catch (error) {
      console.error("회원가입 실패:", error);

      setErrors({
        submit: "회원가입에 실패했습니다. 입력 정보를 다시 확인해주세요.",
      });
    }
  };

  if (signupComplete) {
    return (
      <main className="signupPage">
        <section className="signupSuccessCard">
          <div className="signupSuccessIcon">✓</div>

          <h1>회원가입이 완료되었어요.</h1>

          <p>
            포즈온의 회원이 되신 걸 환영합니다.
            <br />
            이제 로그인하고 운동을 시작해보세요.
          </p>

          <button
            type="button"
            className="signupSubmitButton"
            onClick={() => navigate("/login")}
          >
            로그인하러 가기
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="signupPage">
      <section className="signupCard">
        <div className="signupTitleArea">
          <h1>회원가입</h1>
          <p>간단한 정보만 입력하면 포즈온을 사용할 수 있어요.</p>
        </div>

        <form className="signupForm" onSubmit={handleSignup}>
          <div className="signupField">
            <label htmlFor="name">이름</label>

            <input
              id="name"
              type="text"
              placeholder="이름을 입력해주세요."
              value={name}
              onChange={(e) => setName(e.target.value)}
              className={errors.name ? "inputError" : ""}
            />

            {errors.name && <p className="signupErrorMessage">{errors.name}</p>}
          </div>

          <div className="signupField">
            <label htmlFor="tel">전화번호</label>

            <input
              id="tel"
              type="tel"
              placeholder="010-1234-5678"
              value={tel}
              onChange={(e) => setTel(e.target.value)}
              className={errors.tel ? "inputError" : ""}
            />

            {errors.tel && <p className="signupErrorMessage">{errors.tel}</p>}
          </div>

          <div className="signupField">
            <label htmlFor="signupPassword">비밀번호</label>

            <div className="signupPasswordWrap">
              <input
                id="signupPassword"
                type={showPassword ? "text" : "password"}
                placeholder="비밀번호를 입력해주세요."
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={errors.password ? "inputError" : ""}
              />

              <button
                type="button"
                className="signupPasswordToggle"
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

            <p className="signupHelperText">숫자 6자리 입력해주세요.</p>

            {errors.password && (
              <p className="signupErrorMessage">{errors.password}</p>
            )}
          </div>

          <div className="signupField">
            <label htmlFor="passwordConfirm">비밀번호 확인</label>

            <div className="signupPasswordWrap">
              <input
                id="passwordConfirm"
                type={showPasswordConfirm ? "text" : "password"}
                placeholder="비밀번호를 한번 더 입력해주세요."
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                className={errors.passwordConfirm ? "inputError" : ""}
              />

              <button
                type="button"
                className="signupPasswordToggle"
                onClick={() => setShowPasswordConfirm((prev) => !prev)}
                aria-label={
                  showPasswordConfirm ? "비밀번호 숨기기" : "비밀번호 보기"
                }
              >
                <img
                  src={showPasswordConfirm ? eyeOffIcon : eyeIcon}
                  alt=""
                  aria-hidden="true"
                />
              </button>
            </div>

            {errors.passwordConfirm && (
              <p className="signupErrorMessage">{errors.passwordConfirm}</p>
            )}
          </div>

          <label className="agreementRow">
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
            />

            <span>[필수] 이용약관 및 개인정보 처리방침에 동의합니다.</span>
          </label>

          {errors.agreed && (
            <p className="signupErrorMessage">{errors.agreed}</p>
          )}

          {errors.submit && (
            <p className="signupErrorMessage">{errors.submit}</p>
          )}

          <button type="submit" className="signupSubmitButton">
            회원가입하기
          </button>
        </form>

        <div className="loginGuide">
          <span>이미 가입하셨나요?</span>

          <button type="button" onClick={() => navigate("/login")}>
            로그인하기
          </button>
        </div>
      </section>
    </main>
  );
}

export default SignupPage;
