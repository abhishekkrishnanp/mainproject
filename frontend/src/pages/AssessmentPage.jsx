import React, { useState } from "react";
import { api } from "../services/api";
import { 
  ClipboardList, ChevronRight, ChevronLeft, CheckCircle2, 
  AlertCircle, Brain, Sparkles, Cpu, Target
} from "lucide-react";

const QUESTIONS = [
  // Section 1: Interests & Passion
  { id: "q1", section: "Interests & Passion", question: "Which domain excites you the most?", 
    options: ["Artificial Intelligence / Machine Learning", "Web Development / Full Stack", "Data Engineering / Analytics", "Cloud & DevOps / Infrastructure", "Cybersecurity / Networking", "Research / Academia"] },
  { id: "q2", section: "Interests & Passion", question: "What kind of problems do you enjoy solving?",
    options: ["Building predictive models from data", "Creating user interfaces and experiences", "Designing scalable data pipelines", "Managing and deploying cloud systems", "Solving complex algorithmic problems", "Doing research and writing papers"] },
  { id: "q3", section: "Interests & Passion", question: "How much do you enjoy mathematics and statistics?",
    options: ["Love it – it's my strength", "Like it – comfortable with it", "Neutral – can manage when needed", "Dislike it – prefer other areas"] },

  // Section 2: Technical Skills
  { id: "q4", section: "Technical Skills", question: "Rate your Python programming proficiency:",
    options: ["Expert (5+ projects, libraries, APIs)", "Intermediate (2-4 projects)", "Beginner (basic syntax only)", "No experience"] },
  { id: "q5", section: "Technical Skills", question: "Your experience with data manipulation (SQL, Pandas, NumPy)?",
    options: ["Advanced – complex queries, optimization", "Intermediate – standard operations", "Beginner – basic usage", "No experience"] },
  { id: "q6", section: "Technical Skills", question: "Experience with Machine Learning frameworks (TensorFlow, PyTorch, sklearn)?",
    options: ["Built and deployed real models", "Completed academic/personal projects", "Done tutorials and labs only", "No experience yet"] },
  { id: "q7", section: "Technical Skills", question: "Cloud and DevOps familiarity (AWS, GCP, Docker, CI/CD)?",
    options: ["Experienced – deployed production systems", "Moderate – used in projects", "Basic – aware of concepts", "No experience"] },

  // Section 3: Work Style & Personality
  { id: "q8", section: "Work Style", question: "How do you prefer to work?",
    options: ["Independently on deep technical problems", "In a collaborative team environment", "Mix of both – flexible", "Leading and coordinating people"] },
  { id: "q9", section: "Work Style", question: "What describes your ideal work output?",
    options: ["Cutting-edge AI models and research", "Scalable software products users love", "Reliable data infrastructure", "Insights and reports driving decisions"] },
  { id: "q10", section: "Work Style", question: "How comfortable are you with ambiguity and research?",
    options: ["Very comfortable – I enjoy open problems", "Somewhat comfortable", "Prefer clear, well-defined tasks", "Need structured guidance"] },

  // Section 4: Career Goals
  { id: "q11", section: "Career Goals", question: "What's your primary career goal?",
    options: ["Work at a top tech company (Google, Microsoft, Meta)", "Join an AI/ML startup", "Pursue higher education (M.Tech/PhD/MS)", "Become a freelance consultant", "Start my own tech company"] },
  { id: "q12", section: "Career Goals", question: "Expected salary range (5 years from now)?",
    options: ["15-25 LPA (solid stable income)", "25-40 LPA (high-growth role)", "40+ LPA (specialized expert)", "Variable (research/startup equity)"] },
  { id: "q13", section: "Career Goals", question: "How important is societal/research impact in your work?",
    options: ["Very important – I want to solve real-world problems", "Somewhat important", "Not a priority – business impact first", "Neutral"] },
];

const SECTION_COLORS = {
  "Interests & Passion": "#6366f1",
  "Technical Skills": "#10b981",
  "Work Style": "#f59e0b",
  "Career Goals": "#ec4899",
};

export default function AssessmentPage({ currentUser, token, onAssessmentDone }) {
  const [answers, setAnswers] = useState({});
  const [currentIdx, setCurrentIdx] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);

  const currentQ = QUESTIONS[currentIdx];
  const totalQ = QUESTIONS.length;
  const progress = Math.round(((currentIdx) / totalQ) * 100);
  const allAnswered = QUESTIONS.every(q => answers[q.id]);

  const handleSelect = (option) => {
    setAnswers(prev => ({ ...prev, [currentQ.id]: option }));
    if (currentIdx < totalQ - 1) {
      setTimeout(() => setCurrentIdx(i => i + 1), 300);
    }
  };

  const handleAutoFill = () => {
    const preset = {
      q1: "Artificial Intelligence & Machine Learning",
      q2: "Deep Learning (CNNs, Transformers, LLMs)",
      q3: "Python",
      q4: "Advanced (can train & fine-tune ML/DL models)",
      q5: "Mathematical foundations & algorithm design",
      q6: "Linear Algebra & Calculus (vectors, matrices, gradients)",
      q7: "PyTorch or TensorFlow",
      q8: "Solo deep-focus technical work",
      q9: "Cutting-edge AI models and research",
      q10: "Very comfortable – I enjoy open problems",
      q11: "Work at a top tech company (Google, Microsoft, Meta)",
      q12: "25-40 LPA (high-growth role)",
      q13: "Very important – I want to solve real-world problems"
    };
    setAnswers(preset);
    setCurrentIdx(totalQ - 1);
  };

  const handleSubmit = async () => {
    if (!allAnswered) {
      setError("Please answer all questions before submitting.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const answersArray = Object.entries(answers).map(([questionId, answer]) => {
        const qDef = QUESTIONS.find(q => q.id === questionId);
        return {
          question_key: questionId,
          question_id: questionId,
          answer_value: typeof answer === "number" ? answer : 3,
          answer: typeof answer === "number" ? answer : 3,
          category: qDef?.category || "interest",
          question_text: qDef?.question || "",
        };
      });
      const studentId = currentUser?.id || 1;
      const res = await api.submitAssessment(answersArray, token, studentId);
      setResult(res);
      setSubmitted(true);
    } catch (err) {
      setError(err.message || "Assessment submission failed.");
    } finally {
      setLoading(false);
    }
  };

  if (submitted && result) {
    const topInterest = result.top_interests?.[0] || "AI & Data Science";
    const topSkills = Object.entries(result.skill_scores || {}).sort((a, b) => b[1] - a[1]).slice(0, 4);
    const topCareers = result.recommended_careers?.slice(0, 3) || [];

    return (
      <div style={{ maxWidth: "860px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {/* Success Banner */}
        <div className="glass-card" style={{ background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.3)", textAlign: "center", padding: "2rem" }}>
          <CheckCircle2 size={52} color="#10b981" style={{ marginBottom: "1rem" }} />
          <h2 style={{ fontSize: "1.75rem", marginBottom: "0.5rem" }}>Assessment Complete!</h2>
          <p style={{ color: "var(--text-secondary)" }}>
            Your profile has been analyzed by the Self-Assessment Agent and stored in the database.
          </p>
        </div>

        {/* Profile Summary */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.25rem" }}>
          {/* Top Interests */}
          <div className="glass-card">
            <h3 style={{ fontSize: "1rem", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Sparkles size={16} color="#6366f1" /> Detected Interests
            </h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
              {(result.top_interests || ["Machine Learning", "AI"]).map((i, idx) => (
                <span key={idx} className="badge badge-primary">{i}</span>
              ))}
            </div>
          </div>

          {/* Skill Scores */}
          <div className="glass-card">
            <h3 style={{ fontSize: "1rem", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Brain size={16} color="#10b981" /> Skill Profile
            </h3>
            {topSkills.map(([skill, score]) => (
              <div key={skill} style={{ marginBottom: "0.75rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.25rem" }}>
                  <span style={{ textTransform: "capitalize" }}>{skill.replace(/_/g, " ")}</span>
                  <span style={{ color: "var(--primary)", fontWeight: 600 }}>{Math.round(score)}%</span>
                </div>
                <div style={{ height: "6px", background: "rgba(255,255,255,0.08)", borderRadius: "3px" }}>
                  <div style={{ height: "100%", width: `${score}%`, background: "var(--gradient-brand)", borderRadius: "3px", transition: "width 1s ease" }} />
                </div>
              </div>
            ))}
          </div>

          {/* Suggested Careers */}
          {topCareers.length > 0 && (
            <div className="glass-card">
              <h3 style={{ fontSize: "1rem", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Target size={16} color="#f59e0b" /> Preliminary Career Fits
              </h3>
              {topCareers.map((c, i) => (
                <div key={i} style={{ padding: "0.5rem 0", borderBottom: "1px solid var(--border-subtle)", fontSize: "0.9rem" }}>
                  <span style={{ color: "#f59e0b", fontWeight: 700, marginRight: "0.5rem" }}>#{i + 1}</span>
                  {c}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* CTA */}
        <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
          <button className="btn btn-primary" style={{ padding: "0.85rem 2rem" }} onClick={onAssessmentDone}>
            <Cpu size={18} /> View Career Recommendations →
          </button>
        </div>
      </div>
    );
  }

  const sectionColor = SECTION_COLORS[currentQ.section] || "var(--primary)";

  return (
    <div style={{ maxWidth: "780px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Header */}
      <div style={{ textAlign: "center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", padding: "0.35rem 1rem", borderRadius: "var(--radius-full)", background: "rgba(99, 102, 241, 0.12)", border: "1px solid rgba(99, 102, 241, 0.3)", color: "#a5b4fc", fontSize: "0.85rem", fontWeight: 600, marginBottom: "1rem" }}>
          <ClipboardList size={14} /> Self-Assessment Agent
        </div>
        <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>Career Interest Profile</h1>
        <p style={{ color: "var(--text-secondary)", display: "flex", alignItems: "center", justifyContent: "center", gap: "1rem", flexWrap: "wrap" }}>
          <span>Question {currentIdx + 1} of {totalQ} &nbsp;•&nbsp; Section: {currentQ.section}</span>
          <button 
            type="button" 
            className="btn btn-secondary" 
            style={{ fontSize: "0.78rem", padding: "0.25rem 0.75rem", borderRadius: "var(--radius-full)", borderColor: "rgba(99,102,241,0.4)", color: "#a5b4fc" }}
            onClick={handleAutoFill}
          >
            ⚡ Auto-Fill Sample (AI & DS)
          </button>
        </p>
      </div>

      {/* Progress Bar */}
      <div style={{ height: "6px", background: "rgba(255,255,255,0.08)", borderRadius: "3px", overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${progress}%`, background: "var(--gradient-brand)", borderRadius: "3px", transition: "width 0.4s ease" }} />
      </div>

      {/* Question Card */}
      <div className="glass-card" style={{ minHeight: "340px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
          <span style={{ background: `${sectionColor}20`, color: sectionColor, padding: "0.25rem 0.7rem", borderRadius: "var(--radius-full)", fontSize: "0.78rem", fontWeight: 600 }}>
            {currentQ.section}
          </span>
        </div>

        <h2 style={{ fontSize: "1.35rem", marginBottom: "1.75rem", lineHeight: 1.4 }}>
          {currentQ.question}
        </h2>

        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {currentQ.options.map((option, i) => {
            const isSelected = answers[currentQ.id] === option;
            return (
              <button
                key={i}
                onClick={() => handleSelect(option)}
                style={{
                  textAlign: "left",
                  padding: "0.85rem 1.1rem",
                  borderRadius: "var(--radius-md)",
                  border: isSelected ? `2px solid ${sectionColor}` : "1px solid var(--border-subtle)",
                  background: isSelected ? `${sectionColor}15` : "rgba(255,255,255,0.03)",
                  color: isSelected ? "#f8fafc" : "var(--text-secondary)",
                  fontWeight: isSelected ? 600 : 400,
                  cursor: "pointer",
                  transition: "all 0.2s",
                  fontSize: "0.925rem",
                }}
              >
                <span style={{ color: sectionColor, fontWeight: 700, marginRight: "0.65rem" }}>
                  {String.fromCharCode(65 + i)}.
                </span>
                {option}
              </button>
            );
          })}
        </div>
      </div>

      {/* Navigation */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <button
          className="btn btn-secondary"
          onClick={() => setCurrentIdx(i => Math.max(0, i - 1))}
          disabled={currentIdx === 0}
          style={{ padding: "0.6rem 1.2rem" }}
        >
          <ChevronLeft size={18} /> Previous
        </button>

        {/* Dots */}
        <div style={{ display: "flex", gap: "6px" }}>
          {QUESTIONS.map((q, i) => (
            <div
              key={i}
              onClick={() => setCurrentIdx(i)}
              style={{
                width: answers[q.id] ? "8px" : "6px",
                height: answers[q.id] ? "8px" : "6px",
                borderRadius: "50%",
                background: answers[q.id] ? sectionColor : i === currentIdx ? "#a5b4fc" : "rgba(255,255,255,0.15)",
                cursor: "pointer",
                transition: "all 0.2s",
                marginTop: answers[q.id] ? 0 : "1px"
              }}
            />
          ))}
        </div>

        {currentIdx < totalQ - 1 ? (
          <button
            className="btn btn-primary"
            onClick={() => setCurrentIdx(i => i + 1)}
            style={{ padding: "0.6rem 1.2rem" }}
          >
            Next <ChevronRight size={18} />
          </button>
        ) : (
          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={loading || !allAnswered}
            style={{ padding: "0.6rem 1.4rem" }}
          >
            {loading ? "Analyzing..." : "Submit Assessment →"}
          </button>
        )}
      </div>

      {error && (
        <div style={{ background: "var(--danger-bg)", border: "1px solid rgba(239,68,68,0.3)", color: "#fca5a5", padding: "0.75rem 1rem", borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.875rem" }}>
          <AlertCircle size={16} /> {error}
        </div>
      )}

      {/* Answered count */}
      <div style={{ textAlign: "center", color: "var(--text-muted)", fontSize: "0.82rem" }}>
        {Object.keys(answers).length} / {totalQ} questions answered
        {allAnswered && <span style={{ color: "var(--success)", marginLeft: "0.5rem" }}>• All done! Click Submit.</span>}
      </div>
    </div>
  );
}
