import { useNavigate } from "react-router-dom";

function Header() {
  const navigate = useNavigate();

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
        LOGO
      </div>

      <div className="authText">로그인 / 회원가입</div>
    </header>
  );
}

export default Header;