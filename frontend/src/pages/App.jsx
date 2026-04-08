import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage   from "./pages/LoginPage";
import Dashboard   from "./pages/Dashboard";
import NGOPage     from "./pages/NGOPage";
import MapPage     from "./pages/MapPage";
import QualityPage from "./pages/QualityPage";
import ProfilePage from "./pages/ProfilePage";

function PrivateRoute({ children, role }) {
  const token    = localStorage.getItem("token");
  const userRole = localStorage.getItem("role");
  if (!token) return <Navigate to="/" replace />;
  if (role && userRole !== role) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"          element={<LoginPage />} />
        <Route path="/dashboard" element={<PrivateRoute role="donor">   <Dashboard />   </PrivateRoute>} />
        <Route path="/ngo"       element={<PrivateRoute role="receiver"><NGOPage />     </PrivateRoute>} />
        <Route path="/map"       element={<PrivateRoute>                <MapPage />     </PrivateRoute>} />
        <Route path="/quality"   element={<PrivateRoute>                <QualityPage /> </PrivateRoute>} />
        <Route path="/profile"   element={<PrivateRoute>                <ProfilePage /> </PrivateRoute>} />
        <Route path="*"          element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}