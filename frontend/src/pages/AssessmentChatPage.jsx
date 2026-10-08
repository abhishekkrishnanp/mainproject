import React, { useState, useEffect, useRef } from "react";
import { api } from "../services/api";
import { 
  Bot, 
  Send, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  ArrowRight, 
  User, 
  Brain, 
  Award,
  Layers,
  HelpCircle
} from "lucide-react";

export default function AssessmentChatPage({ currentUser, token, onAssessmentComplete, onGoToDashboard }) {
  const [messages, setMessages] = useState([]); // [{ sender: 'ai' | 'user', text: '', options?: [], questionId?: '' }]
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [assessmentId, setAssessmentId] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [totalSteps, setTotalSteps] = useState(26);
  const [isCompleted, setIsCompleted] = useState(false);
  const [completedProfile, setCompletedProfile] = useState(null);
  const [customText, setCustomText] = useState("");
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState(null);
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, thinking]);

  // Initialize or resume assessment on load
  useEffect(() => {
    initAssessment();
  }, [token]);

  const initAssessment = async () => {
    if (!token) return;
    setThinking(true);
    setError(null);
    try {
      // Check status and history first
      const statusRes = await api.getAssessmentStatus(token);
      if (statusRes.status === "completed" && statusRes.has_profile) {
        // Load finished profile
        const profRes = await api.getCareerProfile(token);
        setIsCompleted(true);
        setCompletedProfile(profRes);
        setThinking(false);
        return;
      }

      // Start or resume session
      const startRes = await api.startDeepAssessment(token);
      setAssessmentId(startRes.assessment_id);
      setTotalSteps(startRes.total_questions || 26);

      // Load previous history if any to restore conversation
      const histRes = await api.getAssessmentHistory(token);
      const restored = [];

      // Welcome AI intro
      restored.push({
        sender: "ai",
        text: "Hello! I am your autonomous Career Discovery Agent. Over the next series of questions, I will conduct a deep personalized interview to understand your academic background, passions, cognitive strengths, and work values.",
      });

      if (histRes.responses && histRes.responses.length > 0) {
        histRes.responses.forEach((r) => {
          restored.push({ sender: "ai", text: r.question_text });
          restored.push({ sender: "user", text: r.answer });
        });
        setCurrentStep(histRes.responses.length);
      }

      // Set current question
      if (startRes.current_question) {
        setCurrentQuestion(startRes.current_question);
        restored.push({
          sender: "ai",
          text: startRes.current_question.question_text,
          options: startRes.current_question.options || [],
          questionId: startRes.current_question.question_id,
        });
      }

      setMessages(restored);
    } catch (err) {
      setError("We're having trouble loading your assessment session. Please retry.");
    } finally {
      setThinking(false);
    }
  };

  const handleSendAnswer = async (answerText) => {
    if (!answerText || !answerText.trim() || thinking) return;
    const cleanAnswer = answerText.trim();
    setError(null);

    // 1. Immediately render User message in chat
    const updatedMessages = [
      ...messages,
      { sender: "user", text: cleanAnswer }
    ];
    setMessages(updatedMessages);
    setCustomText("");
    setThinking(true);

    try {
      const qDef = currentQuestion;
      const res = await api.sendAssessmentMessage(
        {
          assessment_id: assessmentId,
          answer: cleanAnswer,
          question_id: qDef?.question_id,
          question_text: qDef?.question_text,
        },
        token
      );

      setCurrentStep(res.current_step);
      setTotalSteps(res.total_steps || 26);

      if (res.is_completed) {
        setIsCompleted(true);
        setCompletedProfile(res.profile);
        if (onAssessmentComplete) onAssessmentComplete(res.profile);

        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: "Congratulations! Your deep career self-assessment discovery interview is now complete. I have synthesized your 10-dimension personality profile, interest map, and top 5 preliminary career directions.",
          }
        ]);
      } else if (res.next_question) {
        setCurrentQuestion(res.next_question);
        const prefix = res.conversational_prefix ? `${res.conversational_prefix} ` : "";
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: `${prefix}${res.next_question.question_text}`,
            options: res.next_question.options || [],
            questionId: res.next_question.question_id,
          }
        ]);
      }
    } catch (err) {
      setError("We're having trouble processing that response. Please try again.");
    } finally {
      setThinking(false);
    }
  };

  const progressPct = Math.min(100, Math.round((currentStep / Math.max(totalSteps, 1)) * 100));

  // If already completed, render Results Summary & Transition
  if (isCompleted && completedProfile) {
    const personality = completedProfile.personality_profile || {};
    const recs = completedProfile.career_recommendations || [];

    return (
      <div style={{ maxWidth: "960px", margin: "1.5rem auto 3rem", padding: "0 1rem" }}>
        <div className="glass-card" style={{ padding: "2.5rem", textAlign: "center", marginBottom: "2rem" }}>
          <div style={{
            width: "68px",
            height: "68px",
            borderRadius: "50%",
            background: "rgba(16, 185, 129, 0.15)",
            color: "#10b981",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 1.25rem",
            border: "1px solid rgba(16, 185, 129, 0.3)"
          }}>
            <CheckCircle2 size={38} />
          </div>

          <span className="badge badge-success" style={{ marginBottom: "0.75rem" }}>
            Discovery Interview Completed
          </span>

          <h2 style={{ fontSize: "2rem", fontWeight: 800, margin: "0.25rem 0 0.5rem" }}>
            Initial Career &amp; Personality Profile Generated
          </h2>

          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", maxWidth: "650px", margin: "0 auto 2rem" }}>
            Based on your responses across academic preferences, cognitive problem solving, and work values, the Self-Assessment Agent has formulated your guidance profile.
          </p>

          <button
            onClick={onGoToDashboard}
            className="btn btn-primary"
            style={{ padding: "0.85rem 2rem", fontSize: "1.05rem" }}
          >
            Open Full Student Dashboard <ArrowRight size={18} />
          </button>
        </div>

        {/* 10-Dimension Personality Profile */}
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
            {Object.entries(personality)
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

        {/* Top 5 Preliminary Career Matches */}
        <div className="glass-card" style={{ padding: "2rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.5rem" }}>
            <Award size={22} style={{ color: "#f59e0b" }} />
            <h3 style={{ fontSize: "1.35rem", fontWeight: 700, margin: 0 }}>
              Top 5 Preliminary Career Directions
            </h3>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
            These preliminary matches represent initial suggestions based on your responses, not absolute prescriptions.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            {recs.map((rec, idx) => (
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

                <p style={{ color: "var(--text-secondary)", fontSize: "0.925rem", lineHeight: 1.5, marginBottom: "1rem" }}>
                  {rec.reason}
                </p>

                {rec.supporting_evidence && rec.supporting_evidence.length > 0 && (
                  <div style={{ marginBottom: "0.85rem" }}>
                    <div style={{ fontSize: "0.825rem", fontWeight: 600, color: "#a5b4fc", marginBottom: "0.3rem" }}>
                      Supporting Evidence from Interview:
                    </div>
                    <ul style={{ margin: 0, paddingLeft: "1.25rem", fontSize: "0.875rem", color: "var(--text-secondary)" }}>
                      {rec.supporting_evidence.map((ev, i) => <li key={i}>{ev}</li>)}
                    </ul>
                  </div>
                )}

                {rec.concerns && rec.concerns.length > 0 && (
                  <div style={{ marginBottom: "0.85rem" }}>
                    <div style={{ fontSize: "0.825rem", fontWeight: 600, color: "#fca5a5", marginBottom: "0.3rem" }}>
                      Considerations &amp; Potential Gaps:
                    </div>
                    <ul style={{ margin: 0, paddingLeft: "1.25rem", fontSize: "0.875rem", color: "var(--text-secondary)" }}>
                      {rec.concerns.map((cn, i) => <li key={i}>{cn}</li>)}
                    </ul>
                  </div>
                )}

                {rec.skills_needed && rec.skills_needed.length > 0 && (
                  <div>
                    <div style={{ fontSize: "0.825rem", fontWeight: 600, color: "var(--text-muted)", marginBottom: "0.4rem" }}>
                      Key Skills to Develop:
                    </div>
                    <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
                      {rec.skills_needed.map((sk, i) => (
                        <span key={i} style={{ fontSize: "0.8rem", padding: "0.25rem 0.6rem", borderRadius: "4px", background: "rgba(255,255,255,0.08)" }}>
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
      </div>
    );
  }

  // Active Chat Session
  return (
    <div style={{ maxWidth: "860px", margin: "1rem auto 3rem", padding: "0 1rem" }}>
      {/* Top Header & Progress Indicator */}
      <div className="glass-card" style={{ padding: "1.25rem 1.75rem", marginBottom: "1.25rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
          <div>
            <span style={{ fontSize: "0.8rem", color: "var(--primary)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Deep Career Discovery Interview
            </span>
            <h3 style={{ margin: "0.15rem 0 0", fontSize: "1.2rem", fontWeight: 700 }}>
              Self-Assessment Agent
            </h3>
          </div>
          <div style={{ textAlign: "right" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--text-secondary)" }}>
              Question {currentStep} of ~{totalSteps}
            </span>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
              {progressPct}% Completed
            </div>
          </div>
        </div>

        <div style={{ height: "6px", background: "rgba(255,255,255,0.1)", borderRadius: "3px", overflow: "hidden" }}>
          <div style={{
            height: "100%",
            width: `${progressPct}%`,
            background: "var(--gradient-brand)",
            borderRadius: "3px",
            transition: "width 0.3s ease"
          }} />
        </div>
      </div>

      {/* Chat Messages Stream */}
      <div 
        className="glass-card" 
        style={{
          padding: "1.5rem",
          minHeight: "420px",
          maxHeight: "520px",
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: "1.25rem",
          marginBottom: "1.25rem"
        }}
      >
        {messages.map((msg, idx) => {
          const isAi = msg.sender === "ai";
          return (
            <div
              key={idx}
              style={{
                display: "flex",
                gap: "0.85rem",
                alignItems: "flex-start",
                justifyContent: isAi ? "flex-start" : "flex-end"
              }}
            >
              {isAi && (
                <div style={{
                  width: "36px",
                  height: "36px",
                  borderRadius: "10px",
                  background: "var(--gradient-brand)",
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0
                }}>
                  <Bot size={20} />
                </div>
              )}

              <div style={{
                maxWidth: "80%",
                padding: "0.9rem 1.2rem",
                borderRadius: isAi ? "4px 16px 16px 16px" : "16px 4px 16px 16px",
                background: isAi ? "rgba(30, 41, 59, 0.85)" : "var(--primary)",
                color: "#fff",
                fontSize: "0.95rem",
                lineHeight: 1.5,
                border: isAi ? "1px solid var(--border-card)" : "none",
                boxShadow: isAi ? "0 2px 8px rgba(0,0,0,0.2)" : "0 2px 10px rgba(99, 102, 241, 0.3)"
              }}>
                {msg.text}
              </div>

              {!isAi && (
                <div style={{
                  width: "36px",
                  height: "36px",
                  borderRadius: "10px",
                  background: "rgba(255,255,255,0.15)",
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0
                }}>
                  <User size={18} />
                </div>
              )}
            </div>
          );
        })}

        {/* Thinking Indicator */}
        {thinking && (
          <div style={{ display: "flex", gap: "0.85rem", alignItems: "center" }}>
            <div style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "var(--gradient-brand)",
              color: "#fff",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}>
              <Bot size={20} />
            </div>
            <div style={{
              padding: "0.75rem 1.25rem",
              borderRadius: "4px 16px 16px 16px",
              background: "rgba(30, 41, 59, 0.85)",
              color: "#a5b4fc",
              fontSize: "0.875rem",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              border: "1px solid var(--border-card)"
            }}>
              <RefreshCw size={15} className="spin" /> Thinking &amp; formulating next discovery question...
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {error && (
        <div style={{
          padding: "0.75rem 1rem",
          borderRadius: "var(--radius-sm)",
          background: "rgba(239, 68, 68, 0.12)",
          border: "1px solid rgba(239, 68, 68, 0.3)",
          color: "#fca5a5",
          fontSize: "0.85rem",
          marginBottom: "1rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <AlertCircle size={16} /> {error}
          </div>
          <button 
            onClick={() => handleSendAnswer(customText || "Continue")}
            className="btn btn-outline"
            style={{ fontSize: "0.75rem", padding: "0.25rem 0.65rem" }}
          >
            Retry
          </button>
        </div>
      )}

      {/* ─── INTERACTIVE QUESTION OPTIONS SECTION ─── */}
      {currentQuestion && currentQuestion.options && currentQuestion.options.length > 0 && !thinking && (
        <div style={{ marginBottom: "1.25rem" }}>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.6rem", fontWeight: 600 }}>
            Select an option below:
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "0.65rem" }}>
            {currentQuestion.options.map((optionText, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSendAnswer(optionText)}
                disabled={thinking}
                style={{
                  textAlign: "left",
                  padding: "0.9rem 1.25rem",
                  borderRadius: "var(--radius-md)",
                  background: "rgba(30, 41, 59, 0.8)",
                  border: "1px solid rgba(99, 102, 241, 0.25)",
                  color: "#fff",
                  fontSize: "0.925rem",
                  fontWeight: 500,
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between"
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "rgba(99, 102, 241, 0.18)";
                  e.currentTarget.style.borderColor = "var(--primary)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "rgba(30, 41, 59, 0.8)";
                  e.currentTarget.style.borderColor = "rgba(99, 102, 241, 0.25)";
                }}
              >
                <span>{optionText}</span>
                <ArrowRight size={16} style={{ color: "var(--primary)", flexShrink: 0, marginLeft: "0.5rem" }} />
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Free-Text Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendAnswer(customText);
        }}
        style={{
          display: "flex",
          gap: "0.75rem",
          background: "rgba(15, 23, 42, 0.85)",
          padding: "0.5rem",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-card)"
        }}
      >
        <input
          type="text"
          value={customText}
          onChange={(e) => setCustomText(e.target.value)}
          placeholder="Type your own answer or explain in detail..."
          disabled={thinking}
          style={{
            flex: 1,
            background: "transparent",
            border: "none",
            color: "#fff",
            padding: "0.6rem 0.85rem",
            fontSize: "0.95rem",
            outline: "none"
          }}
        />
        <button
          type="submit"
          disabled={!customText.trim() || thinking}
          className="btn btn-primary"
          style={{ padding: "0.6rem 1.25rem", borderRadius: "var(--radius-sm)" }}
        >
          <Send size={16} /> Send
        </button>
      </form>
    </div>
  );
}
