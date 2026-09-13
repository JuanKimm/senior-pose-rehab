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
  const [verificationCode, setVerificationCode] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

  const [verificationSent, setVerificationSent] = useState(false);
  const [isPhoneVerified, setIsPhoneVerified] = useState(false);

  const [agreed, setAgreed] = useState(false);
  const [errors, setErrors] = useState({});

  const [signupComplete, setSignupComplete] = useState(false);

  const cleanTel = tel.replaceAll("-", "");

  // 전화번호가 바뀌면 인증 상태 초기화
  const handleTelChange = (e) => {
    setTel(e.target.value);
    setVerificationSent(false);
    setIsPhoneVerified(false);
    setVerificationCode("");

    setErrors((prev) => ({
      ...prev,
      tel: "",
      verification: "",
    }));
  };

  // 인증번호 발송
  const handleSendCode = async () => {
    if (!/^010\d{8}$/.test(cleanTel)) {
      setErrors((prev) => ({
        ...prev,
        tel: "전화번호를 다시 확인해주세요.",
      }));
      return;
    }

    try {
      // 전화번호 중복 확인
      const checkResponse = await api.get(`/api/auth/check-phone/${cleanTel}`);

      if (!checkResponse.data.avilable) {
        setErrors((prev) => ({
          ...prev,
          tel: "이미 가입된 전화번호입니다.",
        }));
        return;
      }

      // 인증번호 발송
      await api.post("/api/auth/sms/send", {
        tel: cleanTel,
      });

      setVerificationSent(true);

      setErrors((prev) => ({
        ...prev,
        tel: "",
        verification: "",
      }));

      alert("인증번호를 발송했습니다.");
    } catch (error) {
      console.error("인증번호 발송 실패:", error);

      setErrors((prev) => ({
        ...prev,
        verification:
          error.response?.data?.error || "인증번호 발송에 실패했습니다.",
      }));
    }
  };

  // 인증번호 확인
  const handleVerifyCode = async () => {
    if (!/^\d{6}$/.test(verificationCode)) {
      setErrors((prev) => ({
        ...prev,
        verification: "인증번호 6자리를 입력해주세요.",
      }));
      return;
    }

    try {
      await api.post("/api/auth/sms/verify", {
        tel: cleanTel,
        code: verificationCode,
      });

      setIsPhoneVerified(true);

      setErrors((prev) => ({
        ...prev,
        verification: "",
      }));

      alert("전화번호 인증이 완료되었습니다.");
    } catch (error) {
      console.error("인증번호 확인 실패:", error);

      setIsPhoneVerified(false);

      setErrors((prev) => ({
        ...prev,
        verification:
          error.response?.data?.error || "인증번호가 올바르지 않습니다.",
      }));
    }
  };

  // 회원가입
  const handleSignup = async (e) => {
    e.preventDefault();

    const nextErrors = {};

    if (!name.trim()) {
      nextErrors.name = "이름을 입력해주세요.";
    }

    if (!cleanTel) {
      nextErrors.tel = "전화번호를 입력해주세요.";
    } else if (!/^010\d{8}$/.test(cleanTel)) {
      nextErrors.tel = "전화번호를 다시 확인해주세요.";
    }

    if (!isPhoneVerified) {
      nextErrors.verification = "전화번호 인증을 완료해주세요.";
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
      nextErrors.agreed = "이용약관과 개인정보 처리방침에 동의해주세요.";
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

      setErrors((prev) => ({
        ...prev,
        submit:
          error.response?.data?.error ||
          "회원가입에 실패했습니다. 입력 정보를 다시 확인해주세요.",
      }));
    }
  };

  // 회원가입 성공 화면
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
          {/* 이름 */}
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

          {/* 전화번호 */}
          <div className="signupField">
            <label htmlFor="tel">전화번호</label>

            <div className="phoneInputRow">
              <input
                id="tel"
                type="tel"
                placeholder="010-1234-5678"
                value={tel}
                onChange={handleTelChange}
                className={errors.tel ? "inputError" : ""}
                disabled={isPhoneVerified}
              />

              <button
                type="button"
                className="verificationButton"
                onClick={handleSendCode}
                disabled={isPhoneVerified}
              >
                {verificationSent ? "재발송" : "인증번호 받기"}
              </button>
            </div>

            {errors.tel && <p className="signupErrorMessage">{errors.tel}</p>}
          </div>

          {/* 인증번호 */}
          {verificationSent && (
            <div className="signupField">
              <label htmlFor="verificationCode">인증번호</label>

              <div className="phoneInputRow">
                <input
                  id="verificationCode"
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  placeholder="6자리 인증번호"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  disabled={isPhoneVerified}
                />

                <button
                  type="button"
                  className="verificationButton"
                  onClick={handleVerifyCode}
                  disabled={isPhoneVerified}
                >
                  {isPhoneVerified ? "인증 완료" : "인증 확인"}
                </button>
              </div>

              {isPhoneVerified && (
                <p className="verificationSuccess">
                  전화번호 인증이 완료되었습니다.
                </p>
              )}

              {errors.verification && (
                <p className="signupErrorMessage">{errors.verification}</p>
              )}
            </div>
          )}

          {/* 비밀번호 */}
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

          {/* 비밀번호 확인 */}
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

          {/* 약관 */}
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
