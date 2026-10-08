import React from "react";
import { 
  Compass, 
  UserCheck, 
  Award, 
  BarChart3, 
  GitFork, 
  Search, 
  LogOut, 
  User, 
  Sparkles,
  Users,
  LayoutDashboard,
  Layers,
  GraduationCap
} from "lucide-react";

export default function Navbar({ activeTab, setActiveTab, currentUser, parentSession, onLogout }) {
  const navItems = [
    { id: "landing", label: "Overview", icon: Sparkles },
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "assessment", label: "Self-Assessment", icon: UserCheck },
    { id: "parent", label: "Parent Mode", icon: Users },
    { id: "recommendations", label: "Careers", icon: Award },
    { id: "skillgap", label: "Skill Gap", icon: Layers },
    { id: "roadmap", label: "Roadmap", icon: GitFork },
    { id: "rag", label: "RAG Explorer", icon: Search },
  ];

  return (
    <header style={{
      background: "rgba(15, 23, 42, 0.88)",
      backdropFilter: "blur(16px)",
      borderBottom: "1px solid var(--border-card)",
      position: "sticky",
      top: 0,
      zIndex: 50,
      padding: "0.75rem 1.5rem"
    }}>
      <div style={{
        maxWidth: "1320px",
        margin: "0 auto",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "1rem"
      }}>
        {/* Brand */}
        <div 
          onClick={() => setActiveTab("landing")}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
            cursor: "pointer",
            userSelect: "none"
          }}
        >
          <div style={{
            background: "var(--gradient-brand)",
            width: "38px",
            height: "38px",
            borderRadius: "10px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#fff",
            boxShadow: "0 0 15px var(--primary-glow)"
          }}>
            <Compass size={22} />
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: "1.05rem", letterSpacing: "-0.01em" }}>
              Career<span style={{ color: "var(--primary)" }}>AI</span>
            </div>
            <div style={{ fontSize: "0.675rem", color: "var(--text-muted)", fontWeight: 500 }}>
              AI-Powered Agentic Career Guidance System
            </div>
          </div>
        </div>

        {/* Nav Links */}
        <nav style={{ display: "flex", alignItems: "center", gap: "0.25rem", overflowX: "auto" }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.45rem",
                  padding: "0.5rem 0.85rem",
                  borderRadius: "var(--radius-md)",
                  border: "none",
                  background: isActive ? "rgba(99, 102, 241, 0.15)" : "transparent",
                  color: isActive ? "#a5b4fc" : "var(--text-secondary)",
                  fontWeight: isActive ? 600 : 500,
                  fontSize: "0.85rem",
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  whiteSpace: "nowrap"
                }}
              >
                <Icon size={16} color={isActive ? "#818cf8" : "currentColor"} />
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* User Badge / Auth Status */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {currentUser ? (
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <div 
                onClick={() => setActiveTab("dashboard")}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  padding: "0.35rem 0.75rem",
                  background: "rgba(255, 255, 255, 0.05)",
                  border: "1px solid var(--border-card)",
                  borderRadius: "var(--radius-md)",
                  cursor: "pointer"
                }}
              >
                <div style={{
                  width: "24px",
                  height: "24px",
                  borderRadius: "50%",
                  background: "var(--primary)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  color: "#fff"
                }}>
                  {(currentUser.name || currentUser.full_name || "S")[0].toUpperCase()}
                </div>
                <div style={{ fontSize: "0.825rem", fontWeight: 600, color: "#fff" }}>
                  {currentUser.name || currentUser.full_name || "Student"}
                </div>
              </div>

              <button
                onClick={onLogout}
                title="Logout"
                style={{
                  background: "rgba(239, 68, 68, 0.12)",
                  border: "1px solid rgba(239, 68, 68, 0.3)",
                  borderRadius: "var(--radius-sm)",
                  color: "#fca5a5",
                  padding: "0.45rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "all 0.2s"
                }}
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : parentSession ? (
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <span className="badge" style={{ background: "rgba(16, 185, 129, 0.15)", color: "#10b981" }}>
                Parent Mode (Read Only)
              </span>
              <button
                onClick={onLogout}
                title="Exit Parent Mode"
                className="btn btn-outline"
                style={{ fontSize: "0.75rem", padding: "0.3rem 0.6rem" }}
              >
                Exit
              </button>
            </div>
          ) : (
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                onClick={() => setActiveTab("auth")}
                className="btn btn-primary"
                style={{ padding: "0.45rem 1rem", fontSize: "0.85rem" }}
              >
                Student Login
              </button>
              <button
                onClick={() => setActiveTab("parent")}
                className="btn btn-outline"
                style={{ padding: "0.45rem 0.85rem", fontSize: "0.85rem", borderColor: "#10b981", color: "#10b981" }}
              >
                Parent Mode
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
