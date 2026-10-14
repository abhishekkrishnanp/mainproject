import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { 
  User, 
  Brain, 
  Award, 
  Sparkles, 
  KeyRound, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  BarChart3, 
  Globe, 
  TrendingUp, 
  Compass, 
  BookOpen, 
  HelpCircle, 
  ShieldCheck, 
  Lightbulb,
  Briefcase
} from "lucide-react";

export default function StudentDashboardPage({ currentUser, token, onStartAssessment, onSelectCareer }) {
  const [profile, setProfile] = useState(null);
  const [assessmentStatus, setAssessmentStatus] = useState(null);
  const [careerProfile, setCareerProfile] = useState(null);
  const [showParentPin, setShowParentPin] = useState(false);
  const [parentPinValue, setParentPinValue] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [token]);

  const loadDashboardData = async () => {
    if (!token) return;
    setLoading(true);
    try {
      // 1. Load Student Profile
      const profRes = await api.getStudentProfile(token);
      setProfile(profRes);

      // 2. Load Assessment Status
      const statRes = await api.getAssessmentStatus(token);
      setAssessmentStatus(statRes);

      // 3. Load Career Profile if available
      if (statRes.has_profile || statRes.status === "completed") {
        try {
          const cpRes = await api.getCareerProfile(token);
          setCareerProfile(cpRes);
        } catch {
          /* ignore */
        }
      }

      // Check if localStorage has stored parent PIN from registration
      const savedUser = localStorage.getItem("career_user");
      if (savedUser) {
        try {
          const parsed = JSON.parse(savedUser);
          if (parsed.parent_pin) {
            setParentPinValue(parsed.parent_pin);
          }
        } catch {
          /* ignore */
        }
      }
    } catch (err) {
      console.error("Dashboard data load error:", err);
    } finally {
      setLoading(false);
    }
  };

  const studentName = profile?.name || currentUser?.full_name || currentUser?.name || "Student";
  const studentId = profile?.student_id || currentUser?.student_id || "ACGS-STU-001";
  const parentId = profile?.parent_id || currentUser?.parent_id || "ACGS-PAR-8F29K";

  const isCompleted = assessmentStatus?.status === "completed";
  const progressPct = assessmentStatus ? Math.round((assessmentStatus.current_step / Math.max(assessmentStatus.total_steps, 1)) * 100) : 0;

  const futureFeatures = [
    { title: "Market Intelligence Agent", desc: "Live Tavily search, job opening trends, Kerala IT & global demand.", phase: "Phase 2" },
    { title: "Skill Gap Analyst Agent", desc: "Deep curriculum mapping identifying exact missing competencies.", phase: "Phase 3" },
    { title: "Career Roadmap Generator", desc: "12-24 month milestone planner with courses, projects, and certifications.", phase: "Phase 4" },
    { title: "Feasibility Evaluator Agent", desc: "Realistic competition, difficulty, and transition effort evaluation.", phase: "Phase 5" },
    { title: "Career Myth Buster", desc: "Fact-checks salary exaggerations and AI replacement misconceptions.", phase: "Phase 6" },
    { title: "University & College Scout", desc: "Evaluates Tier-1/Tier-2 Indian institutes and global universities.", phase: "Phase 7" },
    { title: "Scholarship Finder", desc: "Identifies government and private scholarship opportunities.", phase: "Phase 8" },
    { title: "Career Simulator", desc: "Simulates 10-year career progression with financial milestones.", phase: "Phase 9" },
    { title: "AI Twin / Future Self", desc: "Interact with an AI agent trained to model your future career trajectory.", phase: "Phase 10" },
  ];

  return (
    <div style={{ maxWidth: "1120px", margin: "1rem auto 3rem", padding: "0 1rem" }}>
      {/* Welcome Banner */}
      <div className="glass-card" style={{ padding: "2rem", marginBottom: "2rem", position: "relative" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.4rem",
              fontSize: "0.8rem",
              fontWeight: 600,
              color: "var(--primary)",
              marginBottom: "0.4rem"
            }}>
              <Sparkles size={14} /> Student Dashboard
            </div>
            <h1 style={{ fontSize: "2rem", fontWeight: 800, margin: "0 0 0.4rem" }}>
              Welcome back, {studentName}
            </h1>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", margin: 0 }}>
              AI-Powered Agentic Career Guidance System • Personalized Guidance Portal
            </p>
          </div>

          <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
            <span className="badge badge-primary" style={{ padding: "0.4rem 0.8rem", fontSize: "0.85rem" }}>
              Student ID: {studentId}
            </span>
            {profile?.education_level && (
              <span className="badge badge-accent" style={{ padding: "0.4rem 0.8rem", fontSize: "0.85rem" }}>
                {profile.education_level}
              </span>
            )}
          </div>
        </div>

        {/* Assessment Progress Status Sub-card */}
        <div style={{
          marginTop: "1.75rem",
          background: "rgba(0,0,0,0.25)",
          borderRadius: "var(--radius-md)",
          padding: "1.25rem 1.5rem",
          border: "1px solid var(--border-subtle)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "1rem"
        }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.35rem" }}>
              <span style={{ fontWeight: 700, fontSize: "1.05rem" }}>
                Self-Assessment Status:
              </span>
              <span style={{
                color: isCompleted ? "#10b981" : "#f59e0b",
                fontWeight: 700,
                fontSize: "0.95rem"
              }}>
                {isCompleted ? "Completed" : progressPct > 0 ? "In Progress" : "Not Started"}
              </span>
            </div>
            <div style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
              {isCompleted 
                ? "Full multi-dimensional assessment completed. Personality and Career profile synthesized."
                : `${progressPct}% completed (${assessmentStatus?.current_step || 0} questions answered).`}
            </div>
          </div>

          <button
            onClick={onStartAssessment}
            className="btn btn-primary"
            style={{ padding: "0.65rem 1.25rem", fontSize: "0.925rem" }}
          >
            {isCompleted ? "Retake Discovery Interview" : progressPct > 0 ? "Continue Interview" : "Start Discovery Interview"} <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* Grid: Education Summary & Parent Access Card */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.5rem", marginBottom: "2rem" }}>
        {/* Education Profile Card */}
        <div className="glass-card" style={{ padding: "1.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
            <BookOpen size={20} style={{ color: "var(--primary)" }} />
            <h3 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700 }}>Academic Background</h3>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", fontSize: "0.9rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "0.5rem" }}>
              <span style={{ color: "var(--text-muted)" }}>Level / Situation:</span>
              <span style={{ fontWeight: 600 }}>{profile?.education_level || "Undergraduate"}</span>
            </div>
            {profile?.branch && (
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "0.5rem" }}>
                <span style={{ color: "var(--text-muted)" }}>Branch / Stream:</span>
                <span style={{ fontWeight: 600 }}>{profile.branch}</span>
              </div>
            )}
            {profile?.university && (
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "0.5rem" }}>
                <span style={{ color: "var(--text-muted)" }}>University:</span>
                <span style={{ fontWeight: 600 }}>{profile.university}</span>
              </div>
            )}
            {profile?.cgpa_percentage && (
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "0.5rem" }}>
                <span style={{ color: "var(--text-muted)" }}>CGPA / Score:</span>
                <span style={{ fontWeight: 600 }}>{profile.cgpa_percentage}</span>
              </div>
            )}
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--text-muted)" }}>Email:</span>
              <span style={{ fontWeight: 600 }}>{profile?.email || currentUser?.email}</span>
            </div>
          </div>
        </div>

        {/* Parent Access Status Card */}
        <div className="glass-card" style={{ padding: "1.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
            <KeyRound size={20} style={{ color: "#10b981" }} />
            <h3 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700 }}>Parent Access Portal</h3>
          </div>

          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", lineHeight: 1.5, marginBottom: "1rem" }}>
            Parents can view your progress in <strong>Read-Only Mode</strong>. They cannot edit your answers or modify career recommendations.
          </p>

          <div style={{
            background: "rgba(0, 0, 0, 0.25)",
            padding: "1rem",
            borderRadius: "var(--radius-sm)",
            border: "1px solid var(--border-subtle)",
            marginBottom: "0.75rem"
          }}>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
              Parent ID
            </div>
            <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#38bdf8", fontFamily: "monospace" }}>
              {parentId}
            </div>

            <div style={{ borderTop: "1px solid var(--border-subtle)", marginTop: "0.6rem", paddingTop: "0.6rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                  Parent PIN
                </div>
                <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "#10b981", letterSpacing: "2px", fontFamily: "monospace" }}>
                  {showParentPin ? (parentPinValue || "••••••") : "••••••"}
                </div>
              </div>

              <button
                type="button"
                onClick={() => setShowParentPin(!showParentPin)}
                className="btn btn-outline"
                style={{ fontSize: "0.75rem", padding: "0.3rem 0.65rem" }}
              >
                {showParentPin ? <><EyeOff size={14} /> Hide</> : <><Eye size={14} /> Reveal PIN</>}
              </button>
            </div>
          </div>

          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            * Parent PIN is hidden by default for security. Reveal only when sharing with your parents.
          </div>
        </div>
      </div>

      {/* Initial Career & Personality Profile (If available) */}
      {careerProfile && (
        <div style={{ marginBottom: "2.5rem" }}>
          {/* Personality Breakdown */}
          {careerProfile.personality_profile && (
            <div className="glass-card" style={{ padding: "2rem", marginBottom: "2rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.35rem" }}>
                <Brain size={22} style={{ color: "var(--primary)" }} />
                <h3 style={{ fontSize: "1.35rem", fontWeight: 700, margin: 0 }}>
                  10-Dimension Personality &amp; Working Style Profile
                </h3>
              </div>
              <p style={{ color: "var(--text-muted)", fontSize: "0.825rem", marginBottom: "1.5rem" }}>
                * Career guidance profile, not a medical or psychological diagnosis.
              </p>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem" }}>
                {Object.entries(careerProfile.personality_profile)
                  .filter(([k]) => k !== "disclaimer")
                  .map(([dimension, score]) => (
                    <div key={dimension} style={{ background: "rgba(0,0,0,0.25)", padding: "0.85rem", borderRadius: "8px" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.35rem", fontSize: "0.875rem" }}>
                        <span style={{ fontWeight: 600 }}>{dimension}</span>
                        <span style={{ color: "var(--primary)", fontWeight: 700 }}>{score}%</span>
                      </div>
                      <div style={{ height: "6px", background: "rgba(255,255,255,0.1)", borderRadius: "3px", overflow: "hidden" }}>
                        <div style={{
                          height: "100%",
                          width: `${score}%`,
                          background: "var(--gradient-brand)",
                          borderRadius: "3px"
                        }} />
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Top 5 Preliminary Career Matches */}
          {careerProfile.career_recommendations && careerProfile.career_recommendations.length > 0 && (
            <div className="glass-card" style={{ padding: "2rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.5rem" }}>
                <Award size={22} style={{ color: "#f59e0b" }} />
                <h3 style={{ fontSize: "1.35rem", fontWeight: 700, margin: 0 }}>
                  Top 5 Preliminary Career Matches
                </h3>
              </div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
                Formulated by the Self-Assessment Agent based on your responses.
              </p>

              <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
                {careerProfile.career_recommendations.map((rec, idx) => (
                  <div 
                    key={idx}
                    style={{
                      border: "1px solid var(--border-card)",
                      borderRadius: "var(--radius-md)",
                      padding: "1.5rem",
                      background: "rgba(0,0,0,0.25)"
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                        <span style={{
                          background: "var(--primary)",
                          color: "#fff",
                          borderRadius: "50%",
                          width: "28px",
                          height: "28px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: "0.85rem",
                          fontWeight: 700
                        }}>
                          #{idx + 1}
                        </span>
                        <h4 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700 }}>{rec.career_name}</h4>
                      </div>
                      <span className="badge badge-success" style={{ fontSize: "0.9rem", padding: "0.35rem 0.75rem" }}>
                        {rec.match_score}% Match
                      </span>
                    </div>

                    <p style={{ color: "var(--text-secondary)", fontSize: "0.925rem", lineHeight: 1.5, marginBottom: "0.85rem" }}>
                      {rec.reason}
                    </p>

                    {rec.supporting_evidence && rec.supporting_evidence.length > 0 && (
                      <div style={{ marginBottom: "0.75rem" }}>
                        <div style={{ fontSize: "0.825rem", fontWeight: 600, color: "#a5b4fc", marginBottom: "0.25rem" }}>
                          Supporting Evidence:
                        </div>
                        <ul style={{ margin: 0, paddingLeft: "1.25rem", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                          {rec.supporting_evidence.map((ev, i) => <li key={i}>{ev}</li>)}
                        </ul>
                      </div>
                    )}

                    {rec.concerns && rec.concerns.length > 0 && (
                      <div style={{ marginBottom: "0.75rem" }}>
                        <div style={{ fontSize: "0.825rem", fontWeight: 600, color: "#fca5a5", marginBottom: "0.25rem" }}>
                          Areas to Watch &amp; Considerations:
                        </div>
                        <ul style={{ margin: 0, paddingLeft: "1.25rem", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                          {rec.concerns.map((cn, i) => <li key={i}>{cn}</li>)}
                        </ul>
                      </div>
                    )}

                    {rec.skills_needed && rec.skills_needed.length > 0 && (
                      <div>
                        <div style={{ fontSize: "0.825rem", fontWeight: 600, color: "var(--text-muted)", marginBottom: "0.35rem" }}>
                          Skills to Develop:
                        </div>
                        <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                          {rec.skills_needed.map((sk, i) => (
                            <span key={i} style={{ fontSize: "0.75rem", padding: "0.2rem 0.55rem", borderRadius: "4px", background: "rgba(255,255,255,0.08)" }}>
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
          )}
        </div>
      )}

      {/* Interactive Career Ecosystem & Live Agents Section */}
      <div style={{ marginBottom: "2.5rem" }}>
        <div style={{ marginBottom: "1.25rem" }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem", color: "var(--primary)", fontWeight: 600, fontSize: "0.85rem", marginBottom: "0.3rem" }}>
            <Sparkles size={16} /> Autonomous Intelligence Ecosystem
          </div>
          <h3 style={{ fontSize: "1.45rem", fontWeight: 700, margin: "0 0 0.35rem" }}>
            Career Exploration &amp; Real-Time Market Intelligence
          </h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", margin: 0 }}>
            Interact with live market analysis, myth busters, verified scholarships, entrance exams, and evaluation benchmarks:
          </p>
        </div>

        {/* Feature Tabs / Modals Trigger */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "1.25rem",
          marginBottom: "1.5rem"
        }}>
          {/* Card 1: Market Intelligence */}
          <div className="glass-card" style={{ padding: "1.35rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <TrendingUp size={20} style={{ color: "#38bdf8" }} />
                  <h4 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700 }}>Market Intelligence</h4>
                </div>
                <span className="badge badge-success" style={{ fontSize: "0.75rem" }}>Live Agent</span>
              </div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", lineHeight: 1.5, margin: "0 0 1rem" }}>
                Kerala IT clusters (Technopark, Infopark), national salary trends, and verified source citations.
              </p>
            </div>
            <button
              onClick={async () => {
                const target = careerProfile?.career_recommendations?.[0]?.career_name || "Machine Learning Engineer";
                const res = await api.getMarketAnalysis(target, "Kerala, India", token);
                alert(`[Agent 2: Market Intelligence]\nCareer: ${res.career_title}\nGeographic: ${res.geographic_focus}\nSources: ${res.provenance_count} verified citations.\n\nSummary:\n${res.market_summary}\n\nKerala Hubs: ${res.kerala_opportunities?.primary_hubs?.join(', ')}\nEntry Band: ${res.kerala_opportunities?.entry_salary_band_kerala}`);
              }}
              className="btn btn-outline"
              style={{ fontSize: "0.825rem", padding: "0.45rem 0.85rem", width: "100%" }}
            >
              Analyze Market Evidence <ArrowRight size={14} />
            </button>
          </div>

          {/* Card 2: Career Myth Buster */}
          <div className="glass-card" style={{ padding: "1.35rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <Lightbulb size={20} style={{ color: "#f59e0b" }} />
                  <h4 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700 }}>Career Myth Buster</h4>
                </div>
                <span className="badge badge-primary" style={{ fontSize: "0.75rem" }}>Verified Facts</span>
              </div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", lineHeight: 1.5, margin: "0 0 1rem" }}>
                Debunk common misconceptions regarding salaries, college pedigree, gender, and AI replacement.
              </p>
            </div>
            <button
              onClick={async () => {
                const myths = await api.getCareerMyths();
                const sample = myths.slice(0, 3).map((m, i) => `Myth ${i+1}: "${m.myth}"\nReality: ${m.reality}`).join("\n\n");
                alert(`[Career Myth Buster - Verified Insights]\n\n${sample}`);
              }}
              className="btn btn-outline"
              style={{ fontSize: "0.825rem", padding: "0.45rem 0.85rem", width: "100%" }}
            >
              Explore Myth Buster <ArrowRight size={14} />
            </button>
          </div>

          {/* Card 3: Scholarships & Funding */}
          <div className="glass-card" style={{ padding: "1.35rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <Award size={20} style={{ color: "#10b981" }} />
                  <h4 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700 }}>Scholarships Finder</h4>
                </div>
                <span className="badge badge-accent" style={{ fontSize: "0.75rem" }}>Govt &amp; Private</span>
              </div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", lineHeight: 1.5, margin: "0 0 1rem" }}>
                Government fellowships (KVPY, Post-Matric) and corporate CSR support for economically constrained students.
              </p>
            </div>
            <button
              onClick={async () => {
                const ships = await api.getScholarships();
                const list = ships.slice(0, 3).map((s) => `• ${s.name} (${s.provider})\n  Amount: ${s.amount}\n  Eligibility: ${s.eligibility}`).join("\n\n");
                alert(`[Verified Scholarships]\n\n${list}`);
              }}
              className="btn btn-outline"
              style={{ fontSize: "0.825rem", padding: "0.45rem 0.85rem", width: "100%" }}
            >
              View Verified Scholarships <ArrowRight size={14} />
            </button>
          </div>

          {/* Card 4: Evaluation Benchmark */}
          <div className="glass-card" style={{ padding: "1.35rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <BarChart3 size={20} style={{ color: "#a855f7" }} />
                  <h4 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700 }}>Quality Benchmarks</h4>
                </div>
                <span className="badge badge-primary" style={{ fontSize: "0.75rem" }}>100 Synthetic Profiles</span>
              </div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", lineHeight: 1.5, margin: "0 0 1rem" }}>
                Reproducible evaluation metrics: Career Match Hit-Rate, Skill Gap F1, and Roadmap Actionability.
              </p>
            </div>
            <button
              onClick={async () => {
                const evalData = await api.runEvaluationBenchmark();
                const m = evalData.metrics;
                alert(`[Section 11 Reproducible Quality Evaluation]\nProfiles Tested: ${evalData.synthetic_profiles_tested}\n\n• Career Match Top-3 Hit Rate: ${m.career_match_relevance.top_3_hit_rate_pct}%\n• Skill Gap Mean F1 Score: ${m.skill_gap_accuracy.mean_f1_score_pct}%\n• Roadmap Actionability Rubric: ${m.roadmap_actionability.mean_rubric_score_out_of_100}/100\n• Execution Latency (P95): ${m.operational_performance.p95_latency_ms} ms\n• Pipeline Completion Rate: ${m.operational_performance.pipeline_completion_rate_pct}%\n\nNotice: ${evalData.label_validation_notice}`);
              }}
              className="btn btn-primary"
              style={{ fontSize: "0.825rem", padding: "0.45rem 0.85rem", width: "100%" }}
            >
              Run Benchmark Evaluation <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
