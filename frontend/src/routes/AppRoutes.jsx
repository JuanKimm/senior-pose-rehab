import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "../components/Header";
import MainPage from "../pages/Main/MainPage";
import ExercisePage from "../pages/Exercise/ExercisePage";
import ResultPage from "../pages/Result/ResultPage";
import DashboardPage from "../pages/Dashboard/DashboardPage";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Header />

      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/exercise" element={<ExercisePage />} />
        <Route path="/result" element={<ResultPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;
