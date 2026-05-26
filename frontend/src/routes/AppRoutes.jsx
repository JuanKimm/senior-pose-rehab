import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "../components/Header";
import MainPage from "../pages/Main/MainPage";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Header />

      <Routes>
        <Route path="/" element={<MainPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;