import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { 
  Users, 
  ShieldAlert, 
  Lock, 
  CheckCircle, 
  AlertCircle, 
  Sparkles, 
  Brain, 
  Award, 
  TrendingUp, 
  BookOpen, 
  ArrowLeft,
  KeyRound,
  Eye,
  Info
} from "lucide-react";

export default function ParentDashboardPage({ onBackToHome, parentSession, onParentLoginSuccess }) {
  const [parentLogin, setParentLogin] = useState({ parent_id: "", parent_pin: "" });
  const [token, setToken] = useState(parentSession?.access_token || null);
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // If token is present, load summary
  useEffect(() => {
    if (token) {
      loadSummary(token);
    }
  }, [token]);

  const loadSummary = async (tok) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getParentStudentSummary(tok);
      setSummaryData(data);
    } catch (err) {
      setError(err.message || "Failed to load student summary.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.loginParent(parentLogin);
      setToken(res.access_token);
      if (onParentLoginSuccess) onParentLoginSuccess(res);
      await loadSummary(res.access_token);
    } catch (err) {
      setError(err.message || "Parent authentication failed. Check Parent ID and PIN.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setSummaryData(null);
    if (onBackToHome) onBackToHome();
  };

  // If not authenticated as parent yet, show Parent Login Form
  if (!token || !summaryData) {
    return (
      <div style={{ maxWidth: "520px", margin: "2rem auto", padding: "0 1rem" }}>
        <button 
          onClick={onBackToHome}
          className="btn btn-outline"
          style={{ marginBottom: "1.5rem", padding: "0.5rem 1rem", fontSize: "0.85rem" }}
        >
          <ArrowLeft size={16} /> Back to Overview
        </button>

        <div className="glass-card" style={{ padding: "2.25rem" }}>
          <div style={{
            width: "52px",
            height: "52px",
            borderRadius: "12px",
            background: "rgba(16, 185, 129, 0.15)",
            color: "#10b981",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: "1.25rem",
            border: "1px solid rgba(16, 185, 129, 0.3)"
          }}>
            <Users size={26} />
          </div>

          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <h2 style={{ fontSize: "1.6rem", fontWeight: 700, margin: 0 }}>
              Parent Access Portal
            </h2>
            <span className="badge" style={{ background: "rgba(16, 185, 129, 0.15)", color: "#10b981", border: "1px solid rgba(16, 185, 129, 0.3)" }}>
              READ ONLY
            </span>
          </div>

          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: 1.5, marginBottom: "1.5rem" }}>
            Enter the unique <strong>Parent ID</strong> and 6-digit <strong>Parent PIN</strong> generated from your student's account to view their career discovery progress.
          </p>

          {error && (
            <div style={{
              padding: "0.75rem 1rem",
              borderRadius: "var(--radius-sm)",
              background: "rgba(239, 68, 68, 0.12)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              color: "#fca5a5",
              fontSize: "0.85rem",
              marginBottom: "1.25rem",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem"
            }}>
              <AlertCircle size={16} /> {error}
            </div>
          )}

          <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "1.1rem" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.35rem" }}>
                Parent ID
              </label>
              <input
                type="text"
                placeholder="e.g. ACGS-PAR-8F29K"
                value={parentLogin.parent_id}
                onChange={(e) => setParentLogin({ ...parentLogin, parent_id: e.target.value })}
                required
                className="input"
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.35rem" }}>
                Parent PIN (6-Digits)
              </label>
              <input
                type="password"
                placeholder="••••••"
                maxLength={10}
                value={parentLogin.parent_pin}
                onChange={(e) => setParentLogin({ ...parentLogin, parent_pin: e.target.value })}
                required
                className="input"
              />
            </div>

            <div style={{
              background: "rgba(99, 102, 241, 0.08)",
              border: "1px solid rgba(99, 102, 241, 0.2)",
              borderRadius: "var(--radius-sm)",
              padding: "0.75rem",
              fontSize: "0.8rem",
              color: "#c7d2fe",
              display: "flex",
              gap: "0.5rem"
            }}>
              <Info size={16} style={{ flexShrink: 0, marginTop: "2px" }} />
              <div>
                Parent access is strictly <strong>READ ONLY</strong>. You will be able to view reports and progress, but cannot alter student answers or recommendations.
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: "100%", padding: "0.8rem", fontSize: "1rem", marginTop: "0.5rem" }}
            >
              {loading ? "Authenticating..." : "Enter Parent Dashboard"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Authenticated Read-Only Parent Dashboard
  return (
    <div style={{ maxWidth: "1080px", margin: "1rem auto 3rem", padding: "0 1rem" }}>
      {/* Read-Only Alert Banner */}
      <div style={{
        background: "rgba(16, 185, 129, 0.12)",
        border: "1px solid rgba(16, 185, 129, 0.35)",
        borderRadius: "var(--radius-md)",
        padding: "1rem 1.25rem",
        marginBottom: "2rem",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "1rem"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div style={{ background: "rgba(16, 185, 129, 0.2)", padding: "0.45rem", borderRadius: "8px", color: "#10b981" }}>
            <Eye size={20} />
          </div>
          <div>
            <div style={{ fontWeight: 700, color: "#10b981", fontSize: "0.95rem" }}>
              PARENT VIEW — STRICTLY READ ONLY
            </div>
            <div style={{ color: "#a7f3d0", fontSize: "0.825rem" }}>
              Recommendations are student-first. As a parent, you can view your child's progress, but cannot modify answers or change career paths.
            </div>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="btn btn-outline"
          style={{ fontSize: "0.825rem", padding: "0.4rem 0.85rem" }}
        >
          Exit Parent Mode
        </button>
      </div>

      {/* Student Profile Overview Card */}
      <div className="glass-card" style={{ padding: "1.75rem", marginBottom: "2rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
              Student Profile
            </div>
            <h2 style={{ fontSize: "1.85rem", fontWeight: 800, margin: "0.25rem 0 0.5rem", color: "#fff" }}>
              {summaryData.student_name}
            </h2>
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
              <span className="badge badge-primary">ID: {summaryData.student_id}</span>
              {summaryData.education_level && <span className="badge badge-accent">{summaryData.education_level}</span>}
              {summaryData.stream_or_branch && <span className="badge" style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8" }}>{summaryData.stream_or_branch}</span>}
            </div>
          </div>

          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Parent Portal ID</div>
            <div style={{ fontFamily: "monospace", fontWeight: 700, color: "#38bdf8", fontSize: "1.05rem" }}>
              {summaryData.parent_id}
            </div>
          </div>
        </div>

        {/* Progress Tracker */}
        <div style={{ marginTop: "1.5rem", borderTop: "1px solid var(--border-card)", paddingTop: "1.25rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem", fontSize: "0.875rem" }}>
            <span style={{ fontWeight: 600, color: "var(--text-secondary)" }}>
              Self-Assessment Status: <strong style={{ color: summaryData.assessment_status === "completed" ? "#10b981" : "#f59e0b" }}>
                {summaryData.assessment_status === "completed" ? "Completed" : "In Progress"}
              </strong>
            </span>
            <span style={{ color: "var(--text-muted)" }}>
              {summaryData.assessment_progress?.percent_complete}% Complete ({summaryData.assessment_progress?.current_question} questions answered)
            </span>
          </div>
          <div style={{ height: "8px", background: "rgba(255,255,255,0.1)", borderRadius: "4px", overflow: "hidden" }}>
            <div style={{
              height: "100%",
              width: `${summaryData.assessment_progress?.percent_complete || 0}%`,
              background: "var(--gradient-brand)",
              borderRadius: "4px",
              transition: "width 0.4s ease"
            }} />
          </div>
        </div>
      </div>

      {/* 10-Dimension Personality Profile (If available) */}
      {summaryData.personality_profile && (
        <div className="glass-card" style={{ padding: "1.75rem", marginBottom: "2rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.35rem" }}>
            <Brain size={22} style={{ color: "var(--accent)" }} />
            <h3 style={{ fontSize: "1.35rem", fontWeight: 700, margin: 0 }}>
              10-Dimension Personality &amp; Work Style Profile
            </h3>
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: "0.825rem", marginBottom: "1.25rem" }}>
            * This is a career guidance profile reflecting preferred working styles, not a medical or psychological diagnosis.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem" }}>
            {Object.entries(summaryData.personality_profile)
              .filter(([k]) => k !== "disclaimer")
              .map(([dimension, score]) => (
                <div key={dimension} style={{ background: "rgba(0,0,0,0.2)", padding: "0.85rem", borderRadius: "8px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.35rem", fontSize: "0.875rem" }}>
                    <span style={{ fontWeight: 600 }}>{dimension}</span>
                    <span style={{ color: "var(--primary)", fontWeight: 700 }}>{score}%</span>
                  </div>
                  <div style={{ height: "6px", background: "rgba(255,255,255,0.1)", borderRadius: "3px", overflow: "hidden" }}>
                    <div style={{
                      height: "100%",
                      width: `${score}%`,
                      background: "var(--primary)",
                      borderRadius: "3px"
                    }} />
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Top Career Recommendations (If available) */}
      {summaryData.career_recommendations && summaryData.career_recommendations.length > 0 ? (
        <div className="glass-card" style={{ padding: "1.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.5rem" }}>
            <Award size={22} style={{ color: "#f59e0b" }} />
            <h3 style={{ fontSize: "1.35rem", fontWeight: 700, margin: 0 }}>
              Preliminary Career Recommendations (Top 5 Matches)
            </h3>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", marginBottom: "1.5rem" }}>
            Generated autonomously by the Self-Assessment Agent based on your student's cognitive preferences, strengths, and goals.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            {summaryData.career_recommendations.map((rec, idx) => (
              <div 
                key={idx}
                style={{
                  border: "1px solid var(--border-card)",
                  borderRadius: "var(--radius-md)",
                  padding: "1.25rem",
                  background: "rgba(0, 0, 0, 0.25)"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                    <span style={{
                      background: "var(--primary)",
                      color: "#fff",
                      borderRadius: "50%",
                      width: "26px",
                      height: "26px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "0.8rem",
                      fontWeight: 700
                    }}>
                      #{idx + 1}
                    </span>
                    <h4 style={{ margin: 0, fontSize: "1.15rem", fontWeight: 700 }}>{rec.career_name}</h4>
                  </div>
                  <span className="badge badge-success" style={{ fontSize: "0.85rem", padding: "0.3rem 0.65rem" }}>
                    {rec.match_score}% Match
                  </span>
                </div>

                <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: 1.5, marginBottom: "0.85rem" }}>
                  {rec.reason}
                </p>

                {rec.supporting_evidence && rec.supporting_evidence.length > 0 && (
                  <div style={{ marginBottom: "0.75rem" }}>
                    <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#a5b4fc", marginBottom: "0.25rem" }}>
                      Supporting Evidence from Assessment:
                    </div>
                    <ul style={{ margin: 0, paddingLeft: "1.25rem", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                      {rec.supporting_evidence.map((ev, i) => <li key={i}>{ev}</li>)}
                    </ul>
                  </div>
                )}

                {rec.skills_needed && rec.skills_needed.length > 0 && (
                  <div>
                    <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-muted)", marginBottom: "0.35rem" }}>
                      Key Skills to Develop:
                    </div>
                    <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                      {rec.skills_needed.map((sk, i) => (
                        <span key={i} style={{ fontSize: "0.75rem", padding: "0.2rem 0.5rem", borderRadius: "4px", background: "rgba(255,255,255,0.08)" }}>
                          {sk}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="glass-card" style={{ padding: "2rem", textAlign: "center", color: "var(--text-muted)" }}>
          <Sparkles size={32} style={{ margin: "0 auto 0.75rem", opacity: 0.6 }} />
          <h4>Career Recommendations Pending</h4>
          <p style={{ fontSize: "0.9rem", maxWidth: "450px", margin: "0 auto" }}>
            Your student is currently completing their deep self-assessment discovery interview. Once completed, their top 5 career matches will automatically populate here.
          </p>
        </div>
      )}
    </div>
  );
}
