import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "./components/ui/sonner";

// Components
import Landing from "./components/landing/Landing";
import Login from "./components/auth/Login";
import AuthCallback from "./components/auth/AuthCallback";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import MapWorkspace from "./components/map/MapWorkspace";
import ProtocolLab from "./components/protocol/ProtocolLab";

// Router wrapper to handle OAuth callback
const AppRouter = () => {
  const location = useLocation();
  
  // Check URL fragment for session_id synchronously during render
  // This prevents race conditions with ProtectedRoute
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/protocol" element={<ProtocolLab />} />
      <Route
        path="/map"
        element={
          <ProtectedRoute>
            <MapWorkspace />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
};

function App() {
  return (
    <div className="App dark">
      <AuthProvider>
        <BrowserRouter>
          <AppRouter />
          <Toaster position="bottom-right" />
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;
