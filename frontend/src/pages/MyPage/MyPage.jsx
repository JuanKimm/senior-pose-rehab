
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../libs/api";
import "./MyPage.css";

const clean = (value) => String(value ?? "").replace(/\D/g, "");

const showPhone = (value) => {
  const number = clean(value);
  return number.length === 11
    ? number.replace(/(\d{3})(\d{4})(\d{4})/, "$1-$2-$3")
    : value || "-";
};

const errorText = (error, fallback) =>
  error?.response?.data?.error ||
  error?.response?.data?.message ||
  fallback;

const emptyProfile = { name: "", tel: "", guardianTel: "" };

const emptyPassword = {
  currentPassword: "",
  newPassword: "",
  confirmPassword: "",
};

function MyInfoRow({ label, value, action }) {
  return (
    <div className="myInfoRow">
      <div className="myInfoRowContent">
        <dt>{label}</dt>
        <dd>{value}</dd>
      </div>
      {action}
    </div>
  );
}

export default function MyPage() {
  const navigate = useNavigate();
  const dialogRef = useRef(null);

  const [profile, setProfile] = useState(emptyProfile);
  const [edit, setEdit] = useState(emptyProfile);
  const [password, setPassword] = useState(emptyPassword);
  const [withdrawPassword, setWithdrawPassword] = useState("");

  const [smsCode, setSmsCode] = useState("");
  const [smsSentTel, setSmsSentTel] = useState("");
  const [verifiedTel, setVerifiedTel] = useState("");

  const [modal, setModal] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const [loadError, setLoadError] = useState("");
  const [formError, setFormError] = useState("");
  const [notice, setNotice] = useState("");

  // 회원정보 다시 조회
  const loadProfile = async () => {
    setLoading(true);
    setLoadError("");

    try {
      const { data } = await api.get("/api/user/me");

      setProfile({
        name: data.name ?? "",
        tel: data.tel ?? "",
        guardianTel: data.guardianTel ?? "",
      });
    } catch (error) {
      setLoadError(
        errorText(error, "회원 정보를 불러오지 못했어요.")
      );
    } finally {
      setLoading(false);
    }
  };

  // 페이지 최초 진입
  useEffect(() => {
    if (!localStorage.getItem("accessToken")) {
      navigate("/login", { replace: true });
      return;
    }

    let active = true;

    api.get("/api/user/me")
      .then(({ data }) => {
        if (active) {
          setProfile({
            name: data.name ?? "",
            tel: data.tel ?? "",
            guardianTel: data.guardianTel ?? "",
          });
        }
      })
      .catch((error) => {
        if (active) {
          setLoadError(
            errorText(error, "회원 정보를 불러오지 못했어요.")
          );
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [navigate]);

  // ESC로 팝업 닫기
  useEffect(() => {
    if (!modal) return;

    dialogRef.current?.focus();

    const onKeyDown = (event) => {
      if (event.key === "Escape" && !busy) {
        setModal("");
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [modal, busy]);

  const open = (type) => {
    setEdit({ ...profile });
    setPassword({ ...emptyPassword });
    setWithdrawPassword("");

    setSmsCode("");
    setSmsSentTel("");
    setVerifiedTel("");

    setFormError("");
    setNotice("");
    setModal(type);
  };

  const close = () => {
    if (busy) return;
    setModal("");
    setWithdrawPassword("");
    setFormError("");
  };

  const logout = () => {
    [
      "accessToken",
      "refreshToken",
      "userId",
      "name",
      "role",
    ].forEach((key) => localStorage.removeItem(key));

    window.dispatchEvent(new Event("poseon:user-updated"));
    navigate("/login", { replace: true });
  };

  const changeEdit = (field, value) => {
    setEdit((prev) => ({ ...prev, [field]: value }));
    setFormError("");

    if (field === "tel") {
      setSmsCode("");
      setSmsSentTel("");
      setVerifiedTel("");
    }
  };

  const changedPhone = clean(edit.tel) !== clean(profile.tel);

  // 새 전화번호 문자 인증번호 발송
  const sendCode = async () => {
    const tel = clean(edit.tel);

    if (!/^010\d{8}$/.test(tel)) {
      setFormError("새 전화번호를 11자리로 입력해주세요.");
      return;
    }

    setBusy(true);
    setFormError("");

    try {
      const { data } = await api.get(
        `/api/auth/check-phone/${tel}`
      );

      // 백엔드 DTO의 실제 필드명: avilable
      if (data.avilable === false) {
        setFormError("이미 사용 중인 전화번호입니다.");
        return;
      }

      await api.post("/api/auth/sms/send", { tel });

      setSmsSentTel(tel);
      setSmsCode("");
    } catch (error) {
      setFormError(
        errorText(error, "인증번호 발송에 실패했어요.")
      );
    } finally {
      setBusy(false);
    }
  };

  // 인증번호 확인
  const verifyCode = async () => {
    const tel = clean(edit.tel);

    if (smsSentTel !== tel || !/^\d{6}$/.test(smsCode)) {
      setFormError("인증번호 6자리를 입력해주세요.");
      return;
    }

    setBusy(true);
    setFormError("");

    try {
      await api.post("/api/auth/sms/verify", {
        tel,
        code: smsCode,
      });

      setVerifiedTel(tel);
    } catch (error) {
      setFormError(
        errorText(
          error,
          "인증번호가 일치하지 않거나 만료되었어요."
        )
      );
    } finally {
      setBusy(false);
    }
  };

  // 내 정보 수정
  const saveInfo = async (event) => {
    event.preventDefault();

    const name = edit.name.trim();
    const tel = clean(edit.tel);
    const guardianTel = clean(edit.guardianTel);

    if (!name) {
      setFormError("이름을 입력해주세요.");
      return;
    }

    if (!/^010\d{8}$/.test(tel)) {
      setFormError(
        "전화번호는 010으로 시작하는 11자리여야 해요."
      );
      return;
    }

    if (guardianTel && !/^010\d{8}$/.test(guardianTel)) {
      setFormError("보호자 연락처를 확인해주세요.");
      return;
    }

    if (changedPhone && verifiedTel !== tel) {
      setFormError(
        "새 전화번호의 문자 인증을 먼저 완료해주세요."
      );
      return;
    }

    setBusy(true);
    setFormError("");

    try {
      const { data } = await api.put("/api/user/me", {
        name,
        tel,
        guardianTel,
      });

      setProfile({
        name: data.name,
        tel: data.tel,
        guardianTel: data.guardianTel ?? "",
      });

      localStorage.setItem("name", data.name);

      window.dispatchEvent(
        new Event("poseon:user-updated")
      );

      setModal("");
      setNotice("내 정보가 수정되었어요.");

      if (changedPhone) {
        alert(
          "전화번호가 변경되었어요. 새 전화번호로 다시 로그인해주세요."
        );
        logout();
      }
    } catch (error) {
      setFormError(
        errorText(error, "정보 수정에 실패했어요.")
      );
    } finally {
      setBusy(false);
    }
  };

  // 비밀번호 변경
  const savePassword = async (event) => {
    event.preventDefault();

    const {
      currentPassword,
      newPassword,
      confirmPassword,
    } = password;

    if (!/^\d{6}$/.test(currentPassword)) {
      setFormError(
        "현재 비밀번호 6자리를 입력해주세요."
      );
      return;
    }

    if (!/^\d{6}$/.test(newPassword)) {
      setFormError(
        "새 비밀번호는 숫자 6자리여야 해요."
      );
      return;
    }

    if (newPassword !== confirmPassword) {
      setFormError("새 비밀번호가 일치하지 않아요.");
      return;
    }

    if (newPassword === currentPassword) {
      setFormError(
        "현재 비밀번호와 다른 번호를 사용해주세요."
      );
      return;
    }

    setBusy(true);
    setFormError("");

    try {
      await api.put("/api/user/password", {
        currentPassword,
        newPassword,
      });

      setPassword({ ...emptyPassword });
      setModal("");
      setNotice("비밀번호가 변경되었어요.");
    } catch (error) {
      setFormError(
        errorText(error, "비밀번호 변경에 실패했어요.")
      );
    } finally {
      setBusy(false);
    }
  };

  // 회원 탈퇴
  const withdraw = async () => {
    if (!withdrawPassword.trim()) {
      setFormError("현재 비밀번호를 입력해주세요.");
      return;
    }

    setBusy(true);
    setFormError("");

    try {
      await api.delete("/api/user/me", {
        data: { password: withdrawPassword },
      });

      setWithdrawPassword("");
      setModal("");

      alert("회원 탈퇴가 완료되었어요.");
      logout();
    } catch (error) {
      setFormError(
        errorText(error, "회원 탈퇴에 실패했어요.")
      );
    } finally {
      setBusy(false);
    }
  };

  const formInput = (field, value) => {
    setPassword((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <main className="myInfoPage">
      <div className="myInfoContainer">

        <div className="myInfoHeading">
          <h1>내 정보</h1>
          <p>
            회원 정보를 확인하고 필요한 내용을
            변경할 수 있어요.
          </p>
        </div>

        <section
          className="myInfoCard"
          aria-label="회원 정보"
        >
          {loading && (
            <p className="myInfoLoading">
              회원 정보를 불러오는 중이에요...
            </p>
          )}

          {loadError && (
            <div
              className="myInfoLoadError"
              role="alert"
            >
              <p>{loadError}</p>
              <button
                type="button"
                onClick={loadProfile}
              >
                다시 시도
              </button>
            </div>
          )}

          {notice && (
            <p className="myInfoSuccess" role="status">
              {notice}
            </p>
          )}

          <dl className="myInfoList">
            <MyInfoRow
              label="이름"
              value={profile.name || "-"}
            />

            <MyInfoRow
              label="전화번호 (아이디)"
              value={showPhone(profile.tel)}
            />

            <MyInfoRow
              label="비밀번호"
              value={
                <span className="myInfoPasswordDots">
                  ●●●●●●
                </span>
              }
              action={
                <button
                  type="button"
                  className="myInfoSmallButton"
                  onClick={() => open("password")}
                >
                  변경
                </button>
              }
            />

            <MyInfoRow
              label="보호자 연락처"
              value={
                profile.guardianTel
                  ? showPhone(profile.guardianTel)
                  : "등록된 연락처가 없어요."
              }
            />
          </dl>

          <div className="myInfoEditArea">
            <button
              type="button"
              className="myInfoPrimaryButton"
              disabled={loading || Boolean(loadError)}
              onClick={() => open("edit")}
            >
              내 정보 수정
            </button>
          </div>
        </section>

        <button
          type="button"
          className="myInfoWithdrawLink"
          onClick={() => open("withdraw")}
        >
          회원 탈퇴
        </button>
      </div>

      {modal && (
        <div className="myInfoModalOverlay">
          <section
            className="myInfoModal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="myInfoModalTitle"
            tabIndex={-1}
            ref={dialogRef}
          >
            <div className="myInfoModalHeader">
              <h2 id="myInfoModalTitle">
                {modal === "edit"
                  ? "내 정보 수정"
                  : modal === "password"
                    ? "비밀번호 변경"
                    : "회원 탈퇴"}
              </h2>

              <button
                type="button"
                className="myInfoCloseButton"
                aria-label="닫기"
                disabled={busy}
                onClick={close}
              >
                ×
              </button>
            </div>

            {/* 내 정보 수정 */}
            {modal === "edit" && (
              <form
                className="myInfoModalForm"
                onSubmit={saveInfo}
              >
                <label className="myInfoField">
                  <span>이름</span>
                  <input
                    value={edit.name}
                    autoComplete="name"
                    onChange={(e) =>
                      changeEdit("name", e.target.value)
                    }
                    required
                    maxLength={30}
                  />
                </label>

                <label className="myInfoField">
                  <span>전화번호 (아이디)</span>
                  <input
                    type="tel"
                    inputMode="numeric"
                    value={edit.tel}
                    placeholder="010-1234-5678"
                    onChange={(e) =>
                      changeEdit("tel", e.target.value)
                    }
                    required
                    maxLength={13}
                  />
                </label>

                {changedPhone && (
                  <>
                    <p className="myInfoHelper">
                      전화번호를 바꾸려면 새로운
                      번호로 문자 인증이 필요해요.
                    </p>

                    {verifiedTel === clean(edit.tel) ? (
                      <p className="myInfoSuccess">
                        전화번호 인증 완료
                      </p>
                    ) : (
                      <>
                        <button
                          type="button"
                          className="myInfoSmallButton"
                          disabled={busy}
                          onClick={sendCode}
                        >
                          인증번호 발송
                        </button>

                        {smsSentTel === clean(edit.tel) && (
                          <>
                            <label className="myInfoField">
                              <span>인증번호</span>
                              <input
                                value={smsCode}
                                inputMode="numeric"
                                placeholder="문자 인증번호 6자리"
                                onChange={(e) =>
                                  setSmsCode(
                                    clean(e.target.value)
                                      .slice(0, 6)
                                  )
                                }
                              />
                            </label>

                            <button
                              type="button"
                              className="myInfoSmallButton"
                              disabled={busy}
                              onClick={verifyCode}
                            >
                              인증번호 확인
                            </button>
                          </>
                        )}
                      </>
                    )}
                  </>
                )}

                <label className="myInfoField">
                  <span>
                    보호자 연락처 <small>(선택)</small>
                  </span>
                  <input
                    type="tel"
                    inputMode="numeric"
                    value={edit.guardianTel ?? ""}
                    placeholder="010-1234-5678"
                    onChange={(e) =>
                      changeEdit(
                        "guardianTel",
                        e.target.value
                      )
                    }
                    maxLength={13}
                  />
                </label>

                {formError && (
                  <p
                    className="myInfoFormError"
                    role="alert"
                  >
                    {formError}
                  </p>
                )}

                <div className="myInfoModalActions">
                  <button
                    type="button"
                    className="myInfoSecondaryButton"
                    onClick={close}
                    disabled={busy}
                  >
                    취소
                  </button>

                  <button
                    type="submit"
                    className="myInfoPrimaryButton"
                    disabled={busy}
                  >
                    {busy ? "저장 중..." : "수정"}
                  </button>
                </div>
              </form>
            )}

            {/* 비밀번호 변경 */}
            {modal === "password" && (
              <form
                className="myInfoModalForm"
                onSubmit={savePassword}
              >
                {[
                  [
                    "currentPassword",
                    "현재 비밀번호",
                    "current-password",
                  ],
                  [
                    "newPassword",
                    "새 비밀번호",
                    "new-password",
                  ],
                  [
                    "confirmPassword",
                    "새 비밀번호 확인",
                    "new-password",
                  ],
                ].map(([key, title, autoComplete]) => (
                  <label
                    className="myInfoField"
                    key={key}
                  >
                    <span>{title}</span>
                    <input
                      type="password"
                      inputMode="numeric"
                      autoComplete={autoComplete}
                      maxLength={6}
                      required
                      placeholder="숫자 6자리"
                      value={password[key]}
                      onChange={(e) =>
                        formInput(
                          key,
                          clean(e.target.value).slice(0, 6)
                        )
                      }
                    />
                  </label>
                ))}

                {formError && (
                  <p
                    className="myInfoFormError"
                    role="alert"
                  >
                    {formError}
                  </p>
                )}

                <div className="myInfoModalActions">
                  <button
                    type="button"
                    className="myInfoSecondaryButton"
                    onClick={close}
                    disabled={busy}
                  >
                    취소
                  </button>

                  <button
                    type="submit"
                    className="myInfoPrimaryButton"
                    disabled={busy}
                  >
                    {busy ? "변경 중..." : "변경"}
                  </button>
                </div>
              </form>
            )}

            {/* 회원 탈퇴 */}
            {modal === "withdraw" && (
              <div className="myInfoModalForm">
                <p className="myInfoWithdrawMessage">
                  정말 회원 탈퇴하시겠어요?
                </p>

                <p className="myInfoHelper">
                  탈퇴 후에는 로그인할 수 없어요.
                  탈퇴하려면 현재 비밀번호를 입력해주세요.
                </p>

                <label className="myInfoField">
                  <span>현재 비밀번호</span>
                  <input
                    type="password"
                    autoComplete="current-password"
                    value={withdrawPassword}
                    onChange={(e) =>
                      setWithdrawPassword(e.target.value)
                    }
                    placeholder="비밀번호 입력"
                  />
                </label>

                {formError && (
                  <p
                    className="myInfoFormError"
                    role="alert"
                  >
                    {formError}
                  </p>
                )}

                <div className="myInfoModalActions">
                  <button
                    type="button"
                    className="myInfoSecondaryButton"
                    disabled={busy}
                    onClick={close}
                  >
                    취소
                  </button>

                  <button
                    type="button"
                    className="myInfoDangerButton"
                    disabled={busy}
                    onClick={withdraw}
                  >
                    {busy ? "처리 중..." : "회원 탈퇴"}
                  </button>
                </div>
              </div>
            )}
          </section>
        </div>
      )}
    </main>
  );
}
