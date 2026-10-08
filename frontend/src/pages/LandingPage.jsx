import React, { useState } from "react";
import { 
  GraduationCap, 
  Users, 
  Sparkles, 
  ArrowRight, 
  ShieldCheck, 
  Compass, 
  Layers, 
  Cpu,
  Lock,
  ChevronRight,
  KeyRound
} from "lucide-react";

export default function LandingPage({ onSelectStudentMode, onSelectParentMode, currentUser, onGoToDashboard }) {
  const [selectedMode, setSelectedMode] = useState(null); // 'student' | 'parent' | null

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "3rem", paddingBottom: "3rem" }}>
      {/* Hero Header */}
      <section style={{ textAlign: "center", paddingTop: "2.5rem" }}>
        <div style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "0.5rem",
          padding: "0.35rem 1.15rem",
          borderRadius: "var(--radius-full)",
          background: "rgba(99, 102, 241, 0.12)",
          border: "1px solid rgba(99, 102, 241, 0.3)",
          color: "#a5b4fc",
          fontSize: "0.85rem",
          fontWeight: 600,
          marginBottom: "1.5rem"
        }}>
          <Sparkles size={16} /> Autonomous AI Agent Architecture • B.Tech Capstone Project
        </div>

        <h1 style={{ 
          fontSize: "2.75rem", 
          lineHeight: 1.2, 
          marginBottom: "1.25rem", 
          maxWidth: "920px", 
          margin: "0 auto 1.25rem",
          fontWeight: 800,
          letterSpacing: "-0.02em"
        }}>
          AI-POWERED AGENTIC <br />
          <span className="gradient-text">CAREER GUIDANCE SYSTEM</span>
        </h1>

        <p style={{ 
          fontSize: "1.15rem", 
          color: "var(--text-secondary)", 
          maxWidth: "720px", 
          margin: "0 auto 2.5rem",
          lineHeight: 1.6
        }}>
          A multi-agent autonomous framework helping school, college, and postgraduate students discover their strengths through deep conversational AI interviews, psychometric skill mapping, and multi-factor career recommendations.
        </p>

        {currentUser && (
          <div style={{ marginBottom: "2rem" }}>
            <button 
              onClick={onGoToDashboard} 
              className="btn btn-primary"
              style={{ padding: "0.85rem 2rem", fontSize: "1.05rem" }}
            >
              Resume Session: Go to Student Dashboard <ArrowRight size={18} />
            </button>
          </div>
        )}

        {/* ─── PRIMARY SELECTION: STUDENT MODE vs PARENT MODE ─── */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "1.75rem",
          maxWidth: "860px",
          margin: "0 auto",
          textAlign: "left"
        }}>
          {/* STUDENT MODE CARD */}
          <div 
            onClick={() => {
              setSelectedMode("student");
              onSelectStudentMode();
            }}
            className="glass-card"
            style={{
              cursor: "pointer",
              padding: "2rem",
              borderRadius: "var(--radius-lg)",
              border: selectedMode === "student" ? "2px solid var(--primary)" : "1px solid var(--border-card)",
              background: "rgba(15, 23, 42, 0.75)",
              transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
              position: "relative",
              overflow: "hidden"
            }}
          >
            <div style={{
              width: "56px",
              height: "56px",
              borderRadius: "14px",
              background: "rgba(99, 102, 241, 0.15)",
              color: "var(--primary)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: "1.25rem",
              border: "1px solid rgba(99, 102, 241, 0.3)"
            }}>
              <GraduationCap size={28} />
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
              <h3 style={{ fontSize: "1.45rem", fontWeight: 700, margin: 0, color: "#fff" }}>
                STUDENT MODE
              </h3>
              <span className="badge badge-primary">Interactive</span>
            </div>

            <p style={{ color: "var(--text-secondary)", fontSize: "0.925rem", lineHeight: 1.5, marginBottom: "1.5rem" }}>
              Complete the deep conversational self-discovery interview, view your 10-dimension personality profile, and explore tailored career directions.
            </p>

            <div style={{
              display: "flex",
              gap: "0.75rem",
              borderTop: "1px solid var(--border-card)",
              paddingTop: "1.25rem"
            }}>
              <button 
                onClick={(e) => { e.stopPropagation(); onSelectStudentMode("login"); }}
                className="btn btn-primary"
                style={{ flex: 1, padding: "0.6rem 1rem", fontSize: "0.9rem" }}
              >
                Login
              </button>
              <button 
                onClick={(e) => { e.stopPropagation(); onSelectStudentMode("register"); }}
                className="btn btn-outline"
                style={{ flex: 1, padding: "0.6rem 1rem", fontSize: "0.9rem" }}
              >
                Create Account
              </button>
            </div>
          </div>

          {/* PARENT MODE CARD */}
          <div 
            onClick={() => {
              setSelectedMode("parent");
              onSelectParentMode();
            }}
            className="glass-card"
            style={{
              cursor: "pointer",
              padding: "2rem",
              borderRadius: "var(--radius-lg)",
              border: selectedMode === "parent" ? "2px solid #10b981" : "1px solid var(--border-card)",
              background: "rgba(15, 23, 42, 0.75)",
              transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
              position: "relative",
              overflow: "hidden"
            }}
          >
            <div style={{
              width: "56px",
              height: "56px",
              borderRadius: "14px",
              background: "rgba(16, 185, 129, 0.15)",
              color: "#10b981",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: "1.25rem",
              border: "1px solid rgba(16, 185, 129, 0.3)"
            }}>
              <Users size={28} />
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
              <h3 style={{ fontSize: "1.45rem", fontWeight: 700, margin: 0, color: "#fff" }}>
                PARENT MODE
              </h3>
              <span className="badge" style={{ background: "rgba(16, 185, 129, 0.15)", color: "#10b981", border: "1px solid rgba(16, 185, 129, 0.3)" }}>
                READ ONLY
              </span>
            </div>

            <p style={{ color: "var(--text-secondary)", fontSize: "0.925rem", lineHeight: 1.5, marginBottom: "1.5rem" }}>
              Securely view your child's assessment progress, personality breakdown, and top career matches without modifying student answers.
            </p>

            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              borderTop: "1px solid var(--border-card)",
              paddingTop: "1.25rem"
            }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "0.35rem" }}>
                <KeyRound size={15} /> Requires Parent ID &amp; PIN
              </span>
              <button 
                onClick={(e) => { e.stopPropagation(); onSelectParentMode(); }}
                className="btn btn-secondary"
                style={{ padding: "0.6rem 1.25rem", fontSize: "0.9rem" }}
              >
                Access Portal <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Highlights */}
      <section style={{ maxWidth: "1060px", margin: "1rem auto 0", width: "100%" }}>
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <h2 style={{ fontSize: "1.85rem", fontWeight: 700, marginBottom: "0.5rem" }}>
            Multi-Agent Architecture Overview
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
            The system combines specialized agents into a unified career guidance pipeline.
          </p>
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "1.25rem"
        }}>
          <div className="glass-card" style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.75rem" }}>
              <div style={{ padding: "0.5rem", borderRadius: "8px", background: "rgba(99, 102, 241, 0.15)", color: "var(--primary)" }}>
                <Cpu size={20} />
              </div>
              <h4 style={{ margin: 0, fontSize: "1.05rem" }}>Self-Assessment Agent</h4>
            </div>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", lineHeight: 1.5 }}>
              Conducts 25-40 deep conversational interactions adapting across school, college, and working professionals with memory persistence.
            </p>
            <span className="badge badge-success" style={{ marginTop: "0.5rem" }}>Fully Implemented</span>
          </div>

          <div className="glass-card" style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.75rem" }}>
              <div style={{ padding: "0.5rem", borderRadius: "8px", background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8" }}>
                <Layers size={20} />
              </div>
              <h4 style={{ margin: 0, fontSize: "1.05rem" }}>Student &amp; Parent Separation</h4>
            </div>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", lineHeight: 1.5 }}>
              Generates unique Parent ID and secure hashed PIN. Provides read-only mirrored dashboards ensuring Student-First guidance.
            </p>
            <span className="badge badge-success" style={{ marginTop: "0.5rem" }}>Fully Implemented</span>
          </div>

          <div className="glass-card" style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.75rem" }}>
              <div style={{ padding: "0.5rem", borderRadius: "8px", background: "rgba(245, 158, 11, 0.15)", color: "#f59e0b" }}>
                <Compass size={20} />
              </div>
              <h4 style={{ margin: 0, fontSize: "1.05rem" }}>Future Agent Pipeline</h4>
            </div>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", lineHeight: 1.5 }}>
              Standardized CareerAgent architecture ready for Market Intelligence (Tavily), Skill Gap Analyst, Roadmap, and Feasibility agents.
            </p>
            <span className="badge" style={{ marginTop: "0.5rem", background: "rgba(245, 158, 11, 0.15)", color: "#f59e0b" }}>Architecture Ready</span>
          </div>
        </div>
      </section>
    </div>
  );
}
