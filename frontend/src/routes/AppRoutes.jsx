import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "../components/Header";
import MainPage from "../pages/Main/MainPage";
import ExercisePage from "../pages/Exercise/ExercisePage";
import ResultPage from "../pages/Result/ResultPage";
import DashboardPage from "../pages/Dashboard/DashboardPage";
import LoginPage from "../pages/Login/LoginPage";
import SignupPage from "../pages/Signup/SignupPage";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Header />

      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/exercise" element={<ExercisePage />} />
        <Route path="/result" element={<ResultPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;
