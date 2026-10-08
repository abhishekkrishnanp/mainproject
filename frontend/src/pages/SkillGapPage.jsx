import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { 
  BarChart3, CheckCircle2, AlertCircle, TrendingUp, 
  Zap, Target, GitFork, Loader, BookOpen
} from "lucide-react";

export default function SkillGapPage({ currentUser, token, selectedCareerId, setActiveTab }) {
  const [gapData, setGapData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSkillGap = async () => {
    setLoading(true);
    setError(null);
    try {
      const studentId = currentUser?.id || 1;
      const data = await api.getSkillGap(studentId, selectedCareerId || null, token);
      setGapData(data);
    } catch (err) {
      setError(err.message || "Skill gap analysis failed. Ensure you have completed the assessment.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkillGap();
  }, [selectedCareerId]);

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "5rem 0" }}>
        <Loader size={48} color="var(--primary)" style={{ animation: "spin 1s linear infinite", marginBottom: "1.5rem" }} />
        <h2 style={{ color: "var(--text-secondary)" }}>Skill Gap Agent Running...</h2>
        <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>Comparing your skills against career requirements...</p>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: "600px", margin: "3rem auto", textAlign: "center" }}>
        <div className="glass-card" style={{ background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.25)" }}>
          <AlertCircle size={44} color="#ef4444" style={{ marginBottom: "1rem" }} />
          <h2 style={{ marginBottom: "0.5rem" }}>Skill Gap Unavailable</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>{error}</p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
            <button className="btn btn-secondary" onClick={() => setActiveTab("assessment")}>Complete Assessment</button>
            <button className="btn btn-primary" onClick={fetchSkillGap}>Retry</button>
          </div>
        </div>
      </div>
    );
  }

  const readiness = gapData?.overall_readiness || 0;
  const readinessColor = readiness >= 70 ? "#10b981" : readiness >= 50 ? "#f59e0b" : "#ef4444";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      {/* Header */}
      <div style={{ textAlign: "center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", padding: "0.35rem 1rem", borderRadius: "var(--radius-full)", background: "rgba(139, 92, 246, 0.12)", border: "1px solid rgba(139, 92, 246, 0.3)", color: "#c4b5fd", fontSize: "0.85rem", fontWeight: 600, marginBottom: "1rem" }}>
          <BarChart3 size={14} /> Skill Gap Analysis Agent
        </div>
        <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
          {gapData ? `Skill Gap: ${gapData.career_title}` : "Skill Gap Analysis"}
        </h1>
        <p style={{ color: "var(--text-secondary)" }}>
          Identifies which skills you have, need to improve, and still need to acquire.
        </p>
      </div>

      {gapData && (
        <>
          {/* Overall Readiness */}
          <div className="glass-card" style={{ textAlign: "center", padding: "2rem" }}>
            <div style={{ fontSize: "4rem", fontWeight: 900, color: readinessColor, lineHeight: 1 }}>
              {Math.round(readiness)}%
            </div>
            <div style={{ fontSize: "1.1rem", fontWeight: 600, marginTop: "0.5rem", marginBottom: "1rem" }}>
              Overall Career Readiness
            </div>
            <div style={{ maxWidth: "400px", margin: "0 auto" }}>
              <div style={{ height: "12px", background: "rgba(255,255,255,0.08)", borderRadius: "6px", overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${readiness}%`, background: readinessColor, borderRadius: "6px", transition: "width 1.2s ease" }} />
              </div>
            </div>
            <p style={{ marginTop: "1rem", color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              {readiness >= 70 ? "🎉 Great news! You're well-prepared for this career path." 
                : readiness >= 50 ? "📚 You're on track — focus on the skills below to bridge the gap." 
                : "🚀 Significant skill building required — but that's what the roadmap is for!"}
            </p>
          </div>

          {/* Three Columns */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.25rem" }}>
            {/* Strong Skills */}
            <div className="glass-card" style={{ border: "1px solid rgba(16, 185, 129, 0.25)" }}>
              <h3 style={{ fontSize: "1rem", marginBottom: "1.25rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <CheckCircle2 size={18} color="#10b981" /> Strong Skills
                <span className="badge badge-success" style={{ marginLeft: "auto" }}>{(gapData.strong_skills || []).length}</span>
              </h3>
              {(gapData.strong_skills || []).length === 0 ? (
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Build more skills to see strengths here.</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                  {(gapData.strong_skills || []).map((skill, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.5rem 0.75rem", background: "rgba(16, 185, 129, 0.08)", borderRadius: "var(--radius-sm)", border: "1px solid rgba(16, 185, 129, 0.2)" }}>
                      <Zap size={13} color="#10b981" />
                      <span style={{ fontSize: "0.875rem", textTransform: "capitalize" }}>{typeof skill === "string" ? skill : skill.skill || skill}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Skills to Improve */}
            <div className="glass-card" style={{ border: "1px solid rgba(245, 158, 11, 0.25)" }}>
              <h3 style={{ fontSize: "1rem", marginBottom: "1.25rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <TrendingUp size={18} color="#f59e0b" /> Needs Improvement
                <span className="badge badge-warning" style={{ marginLeft: "auto" }}>{(gapData.skills_to_improve || []).length}</span>
              </h3>
              {(gapData.skills_to_improve || []).length === 0 ? (
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>No improvement areas detected.</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                  {(gapData.skills_to_improve || []).map((skill, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.5rem 0.75rem", background: "rgba(245, 158, 11, 0.08)", borderRadius: "var(--radius-sm)", border: "1px solid rgba(245, 158, 11, 0.2)" }}>
                      <Target size={13} color="#f59e0b" />
                      <span style={{ fontSize: "0.875rem", textTransform: "capitalize" }}>{typeof skill === "string" ? skill : skill.skill || skill}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Missing Skills */}
            <div className="glass-card" style={{ border: "1px solid rgba(239, 68, 68, 0.25)" }}>
              <h3 style={{ fontSize: "1rem", marginBottom: "1.25rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <BookOpen size={18} color="#ef4444" /> Missing Skills
                <span className="badge badge-danger" style={{ marginLeft: "auto" }}>{(gapData.missing_skills || []).length}</span>
              </h3>
              {(gapData.missing_skills || []).length === 0 ? (
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>No critical skill gaps!</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                  {(gapData.missing_skills || []).map((skill, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.5rem 0.75rem", background: "rgba(239, 68, 68, 0.08)", borderRadius: "var(--radius-sm)", border: "1px solid rgba(239, 68, 68, 0.2)" }}>
                      <AlertCircle size={13} color="#ef4444" />
                      <span style={{ fontSize: "0.875rem", textTransform: "capitalize" }}>{typeof skill === "string" ? skill : skill.skill || skill}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* CTA */}
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
            <button className="btn btn-secondary" onClick={fetchSkillGap}>
              <BarChart3 size={16} /> Re-analyze Skill Gap
            </button>
            <button className="btn btn-primary" style={{ padding: "0.85rem 2rem" }} onClick={() => setActiveTab("roadmap")}>
              <GitFork size={18} /> Generate Learning Roadmap →
            </button>
          </div>
        </>
      )}

      {!gapData && !loading && !error && (
        <div style={{ textAlign: "center", padding: "3rem" }}>
          <BarChart3 size={48} color="var(--text-muted)" style={{ marginBottom: "1rem" }} />
          <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
            Select a career from Recommendations to run skill gap analysis.
          </p>
          <button className="btn btn-primary" onClick={() => setActiveTab("recommendations")}>
            View Recommendations
          </button>
        </div>
      )}
    </div>
  );
}
