import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { 
  Award, Sparkles, TrendingUp, Star, CheckCircle2, 
  AlertCircle, ChevronRight, BarChart3, GitFork, Loader
} from "lucide-react";

const SCORE_COLOR = (score) => {
  if (score >= 80) return "#10b981";
  if (score >= 65) return "#f59e0b";
  return "#ef4444";
};

function ScoreBar({ label, value, color }) {
  return (
    <div style={{ marginBottom: "0.6rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", marginBottom: "0.2rem" }}>
        <span style={{ color: "var(--text-secondary)" }}>{label}</span>
        <span style={{ color, fontWeight: 600 }}>{Math.round(value)}%</span>
      </div>
      <div style={{ height: "5px", background: "rgba(255,255,255,0.07)", borderRadius: "3px" }}>
        <div style={{ height: "100%", width: `${Math.min(value, 100)}%`, background: color, borderRadius: "3px", transition: "width 0.8s ease" }} />
      </div>
    </div>
  );
}

export default function RecommendationsPage({ currentUser, token, onCareerSelected, setActiveTab }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedId, setSelectedId] = useState(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const studentId = currentUser?.id || 1;
      const data = await api.getRecommendations(token, studentId);
      setRecommendations(data);
    } catch (err) {
      setError(err.message || "Failed to load recommendations. Please complete the assessment first.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleSelect = (rec) => {
    setSelectedId(rec.career_id);
    onCareerSelected(rec.career_id);
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "5rem 0" }}>
        <Loader size={48} color="var(--primary)" style={{ animation: "spin 1s linear infinite", marginBottom: "1.5rem" }} />
        <h2 style={{ color: "var(--text-secondary)" }}>Career Recommendation Agent Running...</h2>
        <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>Analyzing your profile and matching careers...</p>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: "600px", margin: "3rem auto", textAlign: "center" }}>
        <div className="glass-card" style={{ background: "rgba(239, 68, 68, 0.08)", border: "1px solid rgba(239,68,68,0.25)" }}>
          <AlertCircle size={44} color="#ef4444" style={{ marginBottom: "1rem" }} />
          <h2 style={{ marginBottom: "0.5rem" }}>Recommendations Unavailable</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>{error}</p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
            <button className="btn btn-secondary" onClick={() => setActiveTab("assessment")}>
              Go to Assessment
            </button>
            <button className="btn btn-primary" onClick={fetchRecommendations}>
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      {/* Header */}
      <div style={{ textAlign: "center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", padding: "0.35rem 1rem", borderRadius: "var(--radius-full)", background: "rgba(245, 158, 11, 0.12)", border: "1px solid rgba(245, 158, 11, 0.3)", color: "#fcd34d", fontSize: "0.85rem", fontWeight: 600, marginBottom: "1rem" }}>
          <Sparkles size={14} /> Career Recommendation Agent
        </div>
        <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
          Your Top Career Matches
        </h1>
        <p style={{ color: "var(--text-secondary)" }}>
          Ranked by AI-computed suitability score based on your profile, skills, interests, and goals.
        </p>
      </div>

      {recommendations.length === 0 && !loading && (
        <div style={{ textAlign: "center", padding: "3rem" }}>
          <Award size={48} color="var(--text-muted)" style={{ marginBottom: "1rem" }} />
          <p style={{ color: "var(--text-secondary)" }}>No recommendations yet. Complete the assessment first.</p>
          <button className="btn btn-primary" style={{ marginTop: "1rem" }} onClick={() => setActiveTab("assessment")}>
            Start Assessment
          </button>
        </div>
      )}

      {/* Recommendation Cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {recommendations.slice(0, 5).map((rec, idx) => {
          const score = Math.round(rec.match_score || 0);
          const scoreColor = SCORE_COLOR(score);
          const isSelected = selectedId === rec.career_id;
          const career = rec.career || {};
          const reasons = rec.reasons || [];

          return (
            <div
              key={rec.id || idx}
              className="glass-card"
              style={{
                border: isSelected ? "2px solid var(--primary)" : undefined,
                background: isSelected ? "rgba(99, 102, 241, 0.08)" : undefined,
                transition: "all 0.3s"
              }}
            >
              <div style={{ display: "flex", gap: "1.5rem", alignItems: "flex-start", flexWrap: "wrap" }}>
                {/* Rank + Score */}
                <div style={{ textAlign: "center", minWidth: "80px" }}>
                  <div style={{ fontSize: "2.5rem", fontWeight: 800, background: "var(--gradient-brand)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                    #{rec.rank || idx + 1}
                  </div>
                  <div style={{ fontSize: "1.5rem", fontWeight: 800, color: scoreColor }}>{score}%</div>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Match</div>
                </div>

                {/* Career Info */}
                <div style={{ flex: 1, minWidth: "200px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap", marginBottom: "0.5rem" }}>
                    <h2 style={{ fontSize: "1.35rem" }}>{rec.career_title || career.title}</h2>
                    {idx === 0 && <span className="badge badge-success"><Star size={11} /> Best Match</span>}
                    {career.industry && <span className="badge badge-info">{career.industry}</span>}
                  </div>
                  
                  {career.description && (
                    <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
                      {career.description}
                    </p>
                  )}

                  {/* Score Breakdown */}
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.5rem 2rem" }}>
                    <ScoreBar label="Interest Match" value={rec.interest_match || 0} color="#6366f1" />
                    <ScoreBar label="Skill Match" value={rec.skill_match || 0} color="#10b981" />
                    <ScoreBar label="Education Match" value={rec.education_match || 0} color="#38bdf8" />
                    <ScoreBar label="Goal Alignment" value={rec.goal_match || 0} color="#f59e0b" />
                  </div>

                  {/* Reasons */}
                  {reasons.length > 0 && (
                    <div style={{ marginTop: "0.75rem", display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                      {reasons.slice(0, 3).map((r, i) => (
                        <span key={i} style={{ fontSize: "0.75rem", padding: "0.2rem 0.6rem", borderRadius: "var(--radius-full)", background: "rgba(255,255,255,0.06)", color: "var(--text-secondary)", border: "1px solid var(--border-subtle)" }}>
                          {r}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Salary & Skills */}
                  <div style={{ display: "flex", gap: "1.5rem", marginTop: "0.75rem", flexWrap: "wrap" }}>
                    {career.salary_range && (
                      <div style={{ fontSize: "0.82rem" }}>
                        <span style={{ color: "var(--text-muted)" }}>Salary: </span>
                        <span style={{ color: "#10b981", fontWeight: 600 }}>{career.salary_range}</span>
                      </div>
                    )}
                    {career.growth_potential && (
                      <div style={{ fontSize: "0.82rem" }}>
                        <span style={{ color: "var(--text-muted)" }}>Growth: </span>
                        <span style={{ color: "#f59e0b", fontWeight: 600 }}>{career.growth_potential}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem", minWidth: "140px" }}>
                  <button
                    className="btn btn-primary"
                    onClick={() => handleSelect(rec)}
                    style={{ padding: "0.6rem 0.9rem", fontSize: "0.85rem" }}
                  >
                    {isSelected ? <CheckCircle2 size={15} /> : <BarChart3 size={15} />}
                    {isSelected ? "Selected" : "Skill Gap"}
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={() => { onCareerSelected(rec.career_id); setTimeout(() => setActiveTab("roadmap"), 50); }}
                    style={{ padding: "0.6rem 0.9rem", fontSize: "0.85rem" }}
                  >
                    <GitFork size={15} /> Roadmap
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {recommendations.length > 0 && (
        <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
          <button className="btn btn-secondary" onClick={fetchRecommendations}>
            <Sparkles size={16} /> Re-run Recommendation Agent
          </button>
        </div>
      )}
    </div>
  );
}
