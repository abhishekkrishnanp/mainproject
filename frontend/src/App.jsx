import { useState, useEffect } from "react";
import "./index.css";
import Navbar from "./components/Navbar";
import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/AuthPage";
import StudentDashboardPage from "./pages/StudentDashboardPage";
import ParentDashboardPage from "./pages/ParentDashboardPage";
import AssessmentChatPage from "./pages/AssessmentChatPage";
import ProfilePage from "./pages/ProfilePage";
import RecommendationsPage from "./pages/RecommendationsPage";
import SkillGapPage from "./pages/SkillGapPage";
import RoadmapPage from "./pages/RoadmapPage";
import RAGPage from "./pages/RAGPage";
import RightAssistantChatbot from "./components/RightAssistantChatbot";

export default function App() {
  const [activeTab, setActiveTab] = useState("landing");
  const [authMode, setAuthMode] = useState("login"); // "login" | "register"
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(null);
  const [parentSession, setParentSession] = useState(null);
  const [selectedCareerId, setSelectedCareerId] = useState(null);

  // Restore session from localStorage
  useEffect(() => {
    try {
      const savedUser = localStorage.getItem("career_user");
      const savedToken = localStorage.getItem("career_token");
      const savedParent = localStorage.getItem("career_parent");
      if (savedUser && savedToken) {
        setCurrentUser(JSON.parse(savedUser));
        setToken(savedToken);
      }
      if (savedParent) {
        setParentSession(JSON.parse(savedParent));
      }
    } catch {
      /* ignore */
    }
  }, []);

  const handleAuthSuccess = (data) => {
    const user = data.user || data;
    const tok = data.access_token || null;
    setCurrentUser(user);
    setToken(tok);
    localStorage.setItem("career_user", JSON.stringify(user));
    if (tok) localStorage.setItem("career_token", tok);
    setActiveTab("dashboard");
  };

  const handleParentLoginSuccess = (parentData) => {
    setParentSession(parentData);
    localStorage.setItem("career_parent", JSON.stringify(parentData));
    setActiveTab("parent");
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setToken(null);
    setParentSession(null);
    setSelectedCareerId(null);
    localStorage.removeItem("career_user");
    localStorage.removeItem("career_token");
    localStorage.removeItem("career_parent");
    setActiveTab("landing");
  };

  const handleProfileUpdate = (updatedUser) => {
    setCurrentUser(updatedUser);
    localStorage.setItem("career_user", JSON.stringify(updatedUser));
  };

  const handleCareerSelected = (careerId) => {
    setSelectedCareerId(careerId);
    setActiveTab("skillgap");
  };

  const requireAuth = (tab) => {
    const protected_tabs = ["dashboard", "profile", "assessment", "recommendations", "skillgap", "roadmap"];
    if (!currentUser && protected_tabs.includes(tab)) {
      setAuthMode("login");
      setActiveTab("auth");
    } else {
      setActiveTab(tab);
    }
  };

  const renderPage = () => {
    switch (activeTab) {
      case "landing":
        return (
          <LandingPage
            onSelectStudentMode={(mode = "login") => {
              if (currentUser) {
                setActiveTab("dashboard");
              } else {
                setAuthMode(mode);
                setActiveTab("auth");
              }
            }}
            onSelectParentMode={() => setActiveTab("parent")}
            currentUser={currentUser}
            onGoToDashboard={() => setActiveTab("dashboard")}
          />
        );

      case "auth":
        return (
          <AuthPage 
            onAuthSuccess={handleAuthSuccess}
            initialMode={authMode}
          />
        );

      case "dashboard":
        return (
          <StudentDashboardPage
            currentUser={currentUser}
            token={token}
            onStartAssessment={() => setActiveTab("assessment")}
            onSelectCareer={handleCareerSelected}
          />
        );

      case "assessment":
        return (
          <AssessmentChatPage
            currentUser={currentUser}
            token={token}
            onAssessmentComplete={() => {}}
            onGoToDashboard={() => setActiveTab("dashboard")}
          />
        );

      case "parent":
        return (
          <ParentDashboardPage
            parentSession={parentSession}
            onParentLoginSuccess={handleParentLoginSuccess}
            onBackToHome={() => setActiveTab("landing")}
          />
        );

      case "profile":
        return (
          <ProfilePage
            currentUser={currentUser}
            token={token}
            onProfileUpdate={handleProfileUpdate}
          />
        );

      case "recommendations":
        return (
          <RecommendationsPage
            currentUser={currentUser}
            token={token}
            onCareerSelected={handleCareerSelected}
            setActiveTab={setActiveTab}
          />
        );

      case "skillgap":
        return (
          <SkillGapPage
            currentUser={currentUser}
            token={token}
            selectedCareerId={selectedCareerId}
            setActiveTab={setActiveTab}
          />
        );

      case "roadmap":
        return (
          <RoadmapPage
            currentUser={currentUser}
            token={token}
            selectedCareerId={selectedCareerId}
          />
        );

      case "rag":
        return <RAGPage />;

      default:
        return (
          <LandingPage
            onSelectStudentMode={() => setActiveTab("auth")}
            onSelectParentMode={() => setActiveTab("parent")}
            currentUser={currentUser}
            onGoToDashboard={() => setActiveTab("dashboard")}
          />
        );
    }
  };

  return (
    <div className="app-container">
      <Navbar
        activeTab={activeTab}
        setActiveTab={requireAuth}
        currentUser={currentUser}
        parentSession={parentSession}
        onLogout={handleLogout}
      />
      <main className="main-content">
        {renderPage()}
      </main>
      <footer style={{
        borderTop: "1px solid var(--border-subtle)",
        padding: "1.25rem 1.5rem",
        textAlign: "center",
        color: "var(--text-muted)",
        fontSize: "0.8rem"
      }}>
        AI-Powered Agentic Career Guidance System (ACGS) &nbsp;&bull;&nbsp; Autonomous Multi-Agent Architecture &nbsp;&bull;&nbsp; Phase 1 (35–40% Scope)
      </footer>
      <RightAssistantChatbot
        activeTab={activeTab}
        currentUser={currentUser}
        parentSession={parentSession}
      />
    </div>
  );
}
