import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { Login } from "./pages/Login";
import { Layout } from "./components/Layout";
import { Vacancies } from "./pages/Vacancies";
import { Candidates } from "./pages/Candidates";
import { TestTasks } from "./pages/TestTasks";
import { Interviews } from "./pages/Interviews";
import { Offers } from "./pages/Offers";
import { Administration } from "./pages/Administration";
import { CandidateDetail } from "./pages/CandidateDetail";
import { VacancyDetail } from "./pages/VacancyDetail";
import { InterviewDetail } from "./pages/InterviewDetail";
import { OfferDetail } from "./pages/OfferDetail";
import "./styles/App.css";

// Временная проверка авторизации
const getCurrentUser = () => {
  const userStr = localStorage.getItem("user");
  return userStr ? JSON.parse(userStr) : null;
};

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const user = getCurrentUser();
  if (!user) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="bottom-right" richColors />
      <Routes>
        <Route path="/" element={<Login />} />
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route
            path="/dashboard"
            element={<Navigate to="/vacancies" replace />}
          />
          <Route path="/vacancies" element={<Vacancies />} />
          <Route path="/candidates" element={<Candidates />} />
          <Route path="/test-assignments" element={<TestTasks />} />
          <Route path="/interviews" element={<Interviews />} />
          <Route path="/offers" element={<Offers />} />
          <Route path="/administration" element={<Administration />} />
          <Route path="/candidates/:id" element={<CandidateDetail />} />
          <Route path="/vacancies/:id" element={<VacancyDetail />} />
          <Route path="/interviews/:id" element={<InterviewDetail />} />
          <Route path="/offers/:id" element={<OfferDetail />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
