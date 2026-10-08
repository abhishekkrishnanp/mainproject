import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { 
  GitFork, CheckCircle2, AlertCircle, BookOpen, 
  Code, Layers, Clock, Loader, ChevronDown, ChevronUp, ExternalLink
} from "lucide-react";

const STAGE_COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#ef4444", "#f59e0b", "#10b981", "#38bdf8"];

function StageCard({ item, idx }) {
  const [expanded, setExpanded] = useState(idx === 0);
  const color = STAGE_COLORS[idx % STAGE_COLORS.length];

  return (
    <div
      className="glass-card"
      style={{ borderLeft: `4px solid ${color}`, cursor: "pointer" }}
    >
      <div
        onClick={() => setExpanded(!expanded)}
        style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem" }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <div style={{ background: `${color}20`, color, width: "40px", height: "40px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: "1rem", flexShrink: 0 }}>
            {item.stage_number || idx + 1}
          </div>
          <div>
            <h3 style={{ fontSize: "1.1rem" }}>{item.stage_title || `Stage ${idx + 1}`}</h3>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.2rem" }}>
              <Clock size={12} color="var(--text-muted)" />
              <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>{item.estimated_duration || "4-6 weeks"}</span>
            </div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {(item.skills || []).slice(0, 2).map((s, i) => (
            <span key={i} className="badge badge-primary" style={{ fontSize: "0.72rem" }}>{s}</span>
          ))}
          {expanded ? <ChevronUp size={16} color="var(--text-muted)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: "1.25rem", paddingTop: "1.25rem", borderTop: "1px solid var(--border-subtle)" }}>
          {item.description && (
            <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "1.25rem" }}>
              {item.description}
            </p>
          )}

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
            {/* Skills */}
            {(item.skills || []).length > 0 && (
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.6rem", fontSize: "0.82rem", fontWeight: 600, color }}>
                  <Layers size={14} /> Skills to Learn
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                  {(item.skills || []).map((s, i) => (
                    <span key={i} style={{ fontSize: "0.78rem", padding: "0.2rem 0.55rem", borderRadius: "var(--radius-full)", background: `${color}15`, color, border: `1px solid ${color}40` }}>{s}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Topics */}
            {(item.topics || []).length > 0 && (
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.6rem", fontSize: "0.82rem", fontWeight: 600, color: "#38bdf8" }}>
                  <BookOpen size={14} /> Topics to Cover
                </div>
                <ul style={{ paddingLeft: "1rem", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                  {(item.topics || []).map((t, i) => (
                    <li key={i} style={{ fontSize: "0.83rem", color: "var(--text-secondary)" }}>{t}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Projects */}
            {(item.projects || []).length > 0 && (
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.6rem", fontSize: "0.82rem", fontWeight: 600, color: "#10b981" }}>
                  <Code size={14} /> Hands-on Projects
                </div>
                <ul style={{ paddingLeft: "1rem", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                  {(item.projects || []).map((p, i) => (
                    <li key={i} style={{ fontSize: "0.83rem", color: "var(--text-secondary)" }}>{p}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Resources */}
            {(item.resources || []).length > 0 && (
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.6rem", fontSize: "0.82rem", fontWeight: 600, color: "#f59e0b" }}>
                  <ExternalLink size={14} /> Recommended Resources
                </div>
                <ul style={{ paddingLeft: "1rem", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                  {(item.resources || []).map((r, i) => (
                    <li key={i} style={{ fontSize: "0.83rem", color: "#a5b4fc" }}>{r}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function RoadmapPage({ currentUser, token, selectedCareerId }) {
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRoadmap = async () => {
    setLoading(true);
    setError(null);
    try {
      const studentId = currentUser?.id || 1;
      const data = await api.getRoadmap(studentId, selectedCareerId || null, token);
      setRoadmap(data);
    } catch (err) {
      setError(err.message || "Failed to generate roadmap. Please complete the assessment first.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoadmap();
  }, [selectedCareerId]);

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "5rem 0" }}>
        <Loader size={48} color="var(--primary)" style={{ animation: "spin 1s linear infinite", marginBottom: "1.5rem" }} />
        <h2 style={{ color: "var(--text-secondary)" }}>Roadmap Agent Generating Your Plan...</h2>
        <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>Building personalized learning stages based on your skill gaps...</p>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: "600px", margin: "3rem auto", textAlign: "center" }}>
        <div className="glass-card" style={{ background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.25)" }}>
          <AlertCircle size={44} color="#ef4444" style={{ marginBottom: "1rem" }} />
          <h2 style={{ marginBottom: "0.5rem" }}>Roadmap Unavailable</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>{error}</p>
          <button className="btn btn-primary" onClick={fetchRoadmap}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      {/* Header */}
      <div style={{ textAlign: "center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", padding: "0.35rem 1rem", borderRadius: "var(--radius-full)", background: "rgba(16, 185, 129, 0.12)", border: "1px solid rgba(16, 185, 129, 0.3)", color: "#6ee7b7", fontSize: "0.85rem", fontWeight: 600, marginBottom: "1rem" }}>
          <GitFork size={14} /> Dynamic Roadmap Agent
        </div>
        <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
          {roadmap ? `Your Roadmap: ${roadmap.career_title}` : "Personalized Learning Roadmap"}
        </h1>
        <p style={{ color: "var(--text-secondary)" }}>
          Stage-by-stage learning plan tailored to your skill gaps and career goal.
        </p>
      </div>

      {roadmap && (
        <>
          {/* Summary Banner */}
          <div className="glass-card" style={{ display: "flex", justifyContent: "center", gap: "3rem", flexWrap: "wrap", padding: "1.5rem" }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--primary)" }}>{roadmap.total_stages || 0}</div>
              <div style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>Total Stages</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: "#f59e0b" }}>
                {(roadmap.total_stages || 0) * 5} weeks
              </div>
              <div style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>Est. Duration</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: "#10b981" }}>{roadmap.completed_stages || 0}</div>
              <div style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>Completed</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: "#38bdf8" }}>
                {roadmap.career_title?.split(" ").slice(0, 2).join(" ")}
              </div>
              <div style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>Target Role</div>
            </div>
          </div>

          {/* Roadmap Stages */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {(roadmap.items || []).map((item, idx) => (
              <StageCard key={item.id || idx} item={item} idx={idx} />
            ))}
          </div>

          {/* CTA */}
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
            <button className="btn btn-secondary" onClick={fetchRoadmap}>
              <GitFork size={16} /> Regenerate Roadmap
            </button>
          </div>
        </>
      )}

      {!roadmap && !loading && !error && (
        <div style={{ textAlign: "center", padding: "3rem" }}>
          <GitFork size={48} color="var(--text-muted)" style={{ marginBottom: "1rem" }} />
          <p style={{ color: "var(--text-secondary)" }}>No roadmap generated yet. Select a career first.</p>
        </div>
      )}
    </div>
  );
}
