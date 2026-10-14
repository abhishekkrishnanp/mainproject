import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import {
  Award, Sparkles, TrendingUp, Star, CheckCircle2,
  AlertCircle, ChevronRight, BarChart3, GitFork, Loader,
  Brain, Layers, Target, BookOpen, Code, ArrowRight, ChevronDown, ChevronUp,
  Lightbulb, Zap, Shield
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

function RoadmapPreview({ stages }) {
  if (!stages || stages.length === 0) return null;
  const COLORS = ["#6366f1", "#8b5cf6", "#ec4899"];
  return (
    <div style={{ marginTop: "0.75rem" }}>
      <div style={{ fontSize: "0.825rem", fontWeight: 600, color: "#a78bfa", marginBottom: "0.5rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
        <GitFork size={13} /> Learning Roadmap Preview
      </div>
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        {stages.slice(0, 3).map((stage, i) => (
          <div key={i} style={{
            flex: "1 1 120px",
            background: `${COLORS[i % COLORS.length]}12`,
            border: `1px solid ${COLORS[i % COLORS.length]}30`,
            borderRadius: "6px",
            padding: "0.6rem",
            fontSize: "0.75rem"
          }}>
            <div style={{ color: COLORS[i % COLORS.length], fontWeight: 700, marginBottom: "0.2rem" }}>
              Stage {stage.stage_number || i + 1}
            </div>
            <div style={{ color: "var(--text-secondary)", lineHeight: 1.4 }}>
              {stage.stage_title || `Stage ${i + 1}`}
            </div>
            {stage.estimated_duration && (
              <div style={{ color: "var(--text-muted)", marginTop: "0.2rem", fontSize: "0.7rem" }}>
                ⏱ {stage.estimated_duration}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function AIPersonalizedCard({ rec, idx, isSelected, onSelect, onRoadmap }) {
  const [expanded, setExpanded] = useState(idx === 0);
  const score = Math.round(rec.match_score || 0);
  const scoreColor = SCORE_COLOR(score);

  return (
    <div
      className="glass-card"
      style={{
        border: isSelected ? "2px solid var(--primary)" : "1px solid var(--border-card)",
        background: isSelected ? "rgba(99, 102, 241, 0.08)" : undefined,
        transition: "all 0.3s",
        borderLeft: `4px solid ${scoreColor}`,
      }}
    >
      {/* Header row */}
      <div
        style={{ display: "flex", gap: "1.5rem", alignItems: "flex-start", flexWrap: "wrap", cursor: "pointer" }}
        onClick={() => setExpanded(!expanded)}
      >
        {/* Rank + Score */}
        <div style={{ textAlign: "center", minWidth: "72px" }}>
          <div style={{ fontSize: "2.2rem", fontWeight: 800, background: "var(--gradient-brand)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            #{idx + 1}
          </div>
          <div style={{ fontSize: "1.4rem", fontWeight: 800, color: scoreColor }}>{score}%</div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Match</div>
        </div>

        {/* Title + badges */}
        <div style={{ flex: 1, minWidth: "200px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap", marginBottom: "0.4rem" }}>
            <h2 style={{ fontSize: "1.25rem", margin: 0 }}>{rec.career_title || rec.career_name}</h2>
            {idx === 0 && <span className="badge badge-success"><Star size={11} /> Best Match</span>}
            <span style={{
              fontSize: "0.72rem", padding: "0.2rem 0.6rem", borderRadius: "var(--radius-full)",
              background: "rgba(99, 102, 241, 0.15)", color: "#a5b4fc", border: "1px solid rgba(99,102,241,0.3)", fontWeight: 600
            }}>
              ✦ AI Personalized
            </span>
          </div>

          {/* Reason */}
          <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: 1.55, margin: 0 }}>
            {rec.reason}
          </p>
        </div>

        {/* Expand toggle */}
        <div style={{ alignSelf: "center" }}>
          {expanded ? <ChevronUp size={18} color="var(--text-muted)" /> : <ChevronDown size={18} color="var(--text-muted)" />}
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div style={{ marginTop: "1.25rem", paddingTop: "1.25rem", borderTop: "1px solid var(--border-subtle)" }}>

          {/* Supporting evidence */}
          {rec.supporting_evidence && rec.supporting_evidence.length > 0 && (
            <div style={{ marginBottom: "1rem" }}>
              <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#a5b4fc", marginBottom: "0.4rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <Brain size={13} /> Supporting Evidence from Interview
              </div>
              <ul style={{ margin: 0, paddingLeft: "1.2rem", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                {rec.supporting_evidence.map((ev, i) => (
                  <li key={i} style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>{ev}</li>
                ))}
              </ul>
            </div>
          )}

          {/* 2-column grid: skills_needed + suggested_projects */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem", marginBottom: "1rem" }}>

            {rec.skills_needed && rec.skills_needed.length > 0 && (
              <div>
                <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#f59e0b", marginBottom: "0.4rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <Zap size={13} /> Key Skills to Develop
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                  {rec.skills_needed.map((sk, i) => (
                    <span key={i} style={{
                      fontSize: "0.78rem", padding: "0.2rem 0.55rem", borderRadius: "var(--radius-full)",
                      background: "rgba(245, 158, 11, 0.1)", color: "#fcd34d", border: "1px solid rgba(245,158,11,0.3)"
                    }}>{sk}</span>
                  ))}
                </div>
              </div>
            )}

            {rec.suggested_projects && rec.suggested_projects.length > 0 && (
              <div>
                <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#38bdf8", marginBottom: "0.4rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <Code size={13} /> Recommended Portfolio Projects
                </div>
                <ul style={{ margin: 0, paddingLeft: "1.2rem", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                  {rec.suggested_projects.map((proj, i) => (
                    <li key={i} style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{proj}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Concerns */}
          {rec.concerns && rec.concerns.length > 0 && (
            <div style={{ marginBottom: "1rem" }}>
              <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#fca5a5", marginBottom: "0.4rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <Shield size={13} /> Considerations & Challenges
              </div>
              <ul style={{ margin: 0, paddingLeft: "1.2rem", display: "flex", flexDirection: "column", gap: "0.2rem" }}>
                {rec.concerns.map((cn, i) => (
                  <li key={i} style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{cn}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Immediate next steps */}
          {rec.immediate_next_steps && rec.immediate_next_steps.length > 0 && (
            <div style={{ marginBottom: "1rem" }}>
              <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#34d399", marginBottom: "0.4rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <Target size={13} /> Immediate Next Actions
              </div>
              <ol style={{ margin: 0, paddingLeft: "1.4rem", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                {rec.immediate_next_steps.map((step, i) => (
                  <li key={i} style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{step}</li>
                ))}
              </ol>
            </div>
          )}

          {/* Roadmap stages preview */}
          <RoadmapPreview stages={rec.roadmap_stages} />

          {/* Action buttons */}
          <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.25rem", flexWrap: "wrap" }}>
            <button
              className="btn btn-primary"
              onClick={(e) => { e.stopPropagation(); onSelect(rec); }}
              style={{ padding: "0.55rem 1rem", fontSize: "0.85rem" }}
            >
              {isSelected ? <><CheckCircle2 size={14} /> Selected</> : <><BarChart3 size={14} /> View Skill Gap</>}
            </button>
            <button
              className="btn btn-secondary"
              onClick={(e) => { e.stopPropagation(); onRoadmap(rec); }}
              style={{ padding: "0.55rem 1rem", fontSize: "0.85rem" }}
            >
              <GitFork size={14} /> View Roadmap
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function StaticRecommendationCard({ rec, idx, isSelected, onSelect, onRoadmap }) {
  const score = Math.round(rec.match_score || 0);
  const scoreColor = SCORE_COLOR(score);
  const career = rec.career || {};
  const reasons = rec.reasons || [];

  return (
    <div
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
        </div>

        {/* Actions */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem", minWidth: "140px" }}>
          <button
            className="btn btn-primary"
            onClick={() => onSelect(rec)}
            style={{ padding: "0.6rem 0.9rem", fontSize: "0.85rem" }}
          >
            {isSelected ? <CheckCircle2 size={15} /> : <BarChart3 size={15} />}
            {isSelected ? "Selected" : "Skill Gap"}
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => onRoadmap(rec)}
            style={{ padding: "0.6rem 0.9rem", fontSize: "0.85rem" }}
          >
            <GitFork size={15} /> Roadmap
          </button>
        </div>
      </div>
    </div>
  );
}

export default function RecommendationsPage({ currentUser, token, onCareerSelected, setActiveTab }) {
  const [recommendations, setRecommendations] = useState([]);
  const [isAIPersonalized, setIsAIPersonalized] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedId, setSelectedId] = useState(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const studentId = currentUser?.id || 1;
      const data = await api.getRecommendations(token, studentId);
      if (Array.isArray(data) && data.length > 0) {
        setRecommendations(data);
        setIsAIPersonalized(!!data[0]?.is_ai_personalized);
      } else {
        setRecommendations([]);
        setIsAIPersonalized(false);
      }
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
    const careerId = rec.career_id || rec.career?.id;
    setSelectedId(careerId);
    if (onCareerSelected) onCareerSelected(careerId);
  };

  const handleRoadmap = (rec) => {
    const careerId = rec.career_id || rec.career?.id;
    if (onCareerSelected) onCareerSelected(careerId);
    setTimeout(() => setActiveTab("roadmap"), 50);
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
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", padding: "0.35rem 1rem", borderRadius: "var(--radius-full)", background: isAIPersonalized ? "rgba(99, 102, 241, 0.12)" : "rgba(245, 158, 11, 0.12)", border: isAIPersonalized ? "1px solid rgba(99,102,241,0.3)" : "1px solid rgba(245, 158, 11, 0.3)", color: isAIPersonalized ? "#a5b4fc" : "#fcd34d", fontSize: "0.85rem", fontWeight: 600, marginBottom: "1rem" }}>
          <Sparkles size={14} />
          {isAIPersonalized ? "AI-Personalized Career Results" : "Career Recommendation Agent"}
        </div>
        <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
          Your Top Career Matches
        </h1>
        <p style={{ color: "var(--text-secondary)" }}>
          {isAIPersonalized
            ? "Deeply personalized results generated from your conversational assessment interview — unique to you."
            : "Ranked by AI-computed suitability score based on your profile, skills, interests, and goals."}
        </p>
        {!isAIPersonalized && recommendations.length > 0 && (
          <div style={{ marginTop: "0.75rem", padding: "0.6rem 1rem", borderRadius: "8px", background: "rgba(245, 158, 11, 0.08)", border: "1px solid rgba(245,158,11,0.2)", fontSize: "0.83rem", color: "#fcd34d", display: "inline-block" }}>
            💡 Complete the <strong>Conversational Assessment</strong> to unlock deeply personalized AI career results with project ideas and roadmaps.
          </div>
        )}
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
          const careerId = rec.career_id || rec.career?.id;
          const isSelected = selectedId === careerId;

          return isAIPersonalized ? (
            <AIPersonalizedCard
              key={rec.id || idx}
              rec={rec}
              idx={idx}
              isSelected={isSelected}
              onSelect={handleSelect}
              onRoadmap={handleRoadmap}
            />
          ) : (
            <StaticRecommendationCard
              key={rec.id || idx}
              rec={rec}
              idx={idx}
              isSelected={isSelected}
              onSelect={handleSelect}
              onRoadmap={handleRoadmap}
            />
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
