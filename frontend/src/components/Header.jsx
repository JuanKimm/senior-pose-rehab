import { useLocation, useNavigate } from "react-router-dom";
import logo from "../assets/logo/logo.svg";

function Header() {
  const navigate = useNavigate();
  const location = useLocation();

  const isAuthPage =
    location.pathname === "/login" || location.pathname === "/signup";

  const goHome = () => {
    navigate("/");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <header className="header">
      <div className="logoText" onClick={goHome}>
        <img src={logo} alt="Pose-ON" className="headerLogo" />
      </div>

      {!isAuthPage && (
        <div className="authText" onClick={() => navigate("/login")}>
          로그인 / 회원가입
        </div>
      )}
    </header>
  );
}

export default Header;
