import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import logo from "../assets/logo/logo.svg";
import chevronDown from "../assets/icons/icon=ChevronDown.svg";
import chevronUp from "../assets/icons/icon=ChevronUp.svg";

function Header() {
  const navigate = useNavigate();
  const location = useLocation();

  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const accessToken = localStorage.getItem("accessToken");
  const name = localStorage.getItem("name");

  const isLoggedIn = Boolean(accessToken);

  const isAuthPage =
    location.pathname === "/login" || location.pathname === "/signup";

  const goHome = () => {
    setIsMenuOpen(false);
    navigate("/");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleExerciseRecord = () => {
    setIsMenuOpen(false);
    navigate("/dashboard");
  };

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("userId");
    localStorage.removeItem("name");
    localStorage.removeItem("role");

    setIsMenuOpen(false);
    navigate("/");
  };

  return (
    <header className="header">
      <div className="logoText" onClick={goHome}>
        <img src={logo} alt="Pose-ON" className="headerLogo" />
      </div>

      {!isAuthPage &&
        (isLoggedIn ? (
          <div className="userMenuWrap">
            <button
              className={`userButton ${isMenuOpen ? "open" : ""}`}
              type="button"
              onClick={() => setIsMenuOpen((prev) => !prev)}
            >
              <span>{name || "사용자"}님</span>

              <img
                src={isMenuOpen ? chevronUp : chevronDown}
                alt=""
                className="userChevron"
              />
            </button>

            {isMenuOpen && (
              <div className="userDropdown">
                <button type="button" className="dropdownItem">
                  내 정보
                </button>

                <button
                  type="button"
                  className="dropdownItem"
                  onClick={handleExerciseRecord}
                >
                  운동 기록
                </button>

                <button
                  type="button"
                  className="dropdownItem"
                  onClick={handleLogout}
                >
                  로그아웃
                </button>
              </div>
            )}
          </div>
        ) : (
          <button
            className="authText"
            type="button"
            onClick={() => navigate("/login")}
          >
            로그인/회원가입
          </button>
        ))}
    </header>
  );
}

export default Header;
