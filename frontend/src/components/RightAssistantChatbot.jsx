import React, { useState, useEffect, useRef } from "react";
import { api } from "../services/api";
import {
  Bot,
  MessageSquare,
  X,
  Minimize2,
  Send,
  Sparkles,
  User,
  Users,
  GraduationCap,
  RefreshCw,
  ChevronRight,
  Shield,
  Lightbulb
} from "lucide-react";

export default function RightAssistantChatbot({ activeTab, currentUser, parentSession }) {
  const [isOpen, setIsOpen] = useState(false);
  // Mode can be 'student' or 'parent'. Detect from active parent session or default to student
  const [mode, setMode] = useState(parentSession ? "parent" : "student");
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Sync mode if parent session or activeTab changes
  useEffect(() => {
    if (activeTab === "parent" || parentSession) {
      setMode("parent");
    } else {
      setMode("student");
    }
  }, [activeTab, parentSession]);

  // Initial welcome message based on mode
  useEffect(() => {
    if (messages.length === 0) {
      resetWelcome(mode);
    }
  }, [mode]);

  const resetWelcome = (selectedMode) => {
    if (selectedMode === "parent") {
      setMessages([
        {
          id: 1,
          sender: "assistant",
          text: "Hello! I am your **ACGS Parent Advisory Assistant**. I can help you understand your child's assessment results, explain modern tech careers in plain language, discuss job opportunities in Kerala & India, and guide you on supporting your child's career journey without pressure.",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } else {
      setMessages([
        {
          id: 1,
          sender: "assistant",
          text: "Hey! I'm your **ACGS Career Guidance Companion**. Ask me anything about the self-assessment interview, top skills to learn, career paths in AI/Software, higher studies (GATE/MS/MBA), or tech companies in Kerala (Technopark & Infopark).",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, loading, isOpen]);

  const handleSendMessage = async (textToSend) => {
    const query = (textToSend || inputText).trim();
    if (!query || loading) return;

    const userMsg = {
      id: Date.now(),
      sender: "user",
      text: query,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setLoading(true);

    // Format recent message history (up to last 8 turns) to maintain conversational context
    const recentHistory = messages
      .filter((m) => m.sender === "user" || m.sender === "assistant")
      .slice(-8)
      .map((m) => ({
        role: m.sender === "user" ? "user" : "assistant",
        text: m.text,
      }));

    try {
      const extraContext = {
        student_name: currentUser?.name || currentUser?.full_name || parentSession?.student_name,
        education_level: currentUser?.education_level,
        current_page: activeTab,
        history: recentHistory,
      };

      // Use the new authenticated chat endpoint when a token is available.
      // Falls back to legacy /assistant/chat for unauthenticated sessions (parent mode).
      const storedToken = localStorage.getItem("career_token");
      let replyText = "";
      let source = "system_fallback";

      if (storedToken) {
        try {
          const chatRes = await api.gemini.chat(query, mode, storedToken, {
            current_page: activeTab,
          });
          replyText = chatRes.reply || "";
          source = chatRes.source || "gemini";
        } catch (chatErr) {
          // If auth_required or service down, fall back to legacy endpoint
          if (chatErr.message !== "auth_required") throw chatErr;
          const res = await api.askAssistant(query, mode, extraContext);
          replyText = res.reply || res.message || "";
          source = res.source || "system_fallback";
        }
      } else {
        // No token — use legacy unauthenticated endpoint
        const res = await api.askAssistant(query, mode, extraContext);
        replyText = res.reply || res.message || "";
        source = res.source || "system_fallback";
      }

      const aiMsg = {
        id: Date.now() + 1,
        sender: "assistant",
        text: replyText || "I am processing your query. Feel free to explore the assessment or ask another question!",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        source,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: "assistant",
          text: "I am having trouble connecting to the career service right now. Please try again or ask another question.",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (newMode) => {
    setMode(newMode);
    resetWelcome(newMode);
  };

  const studentChips = [
    "How does the self-assessment work?",
    "Tell me about tech jobs in Kerala (Technopark)",
    "What skills should I learn first?",
    "GATE vs Campus Placements?",
  ];

  const parentChips = [
    "Why is Parent access read-only?",
    "What are the job prospects in AI/Data?",
    "How do I interpret personality scores?",
    "How can I best support my child?",
  ];

  return (
    <>
      {/* ─── FLOATING LAUNCHER BUTTON (Bottom-Right) ─── */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={{
            position: "fixed",
            bottom: "26px",
            right: "26px",
            zIndex: 999,
            display: "flex",
            alignItems: "center",
            gap: "0.65rem",
            padding: "0.85rem 1.35rem",
            borderRadius: "var(--radius-full)",
            background: "var(--gradient-brand)",
            color: "#fff",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            boxShadow: "0 8px 24px rgba(99, 102, 241, 0.45)",
            cursor: "pointer",
            fontWeight: 700,
            fontSize: "0.925rem",
            transition: "all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "translateY(-3px) scale(1.02)";
            e.currentTarget.style.boxShadow = "0 12px 30px rgba(99, 102, 241, 0.6)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "translateY(0) scale(1)";
            e.currentTarget.style.boxShadow = "0 8px 24px rgba(99, 102, 241, 0.45)";
          }}
        >
          <div style={{ position: "relative", display: "flex" }}>
            <Bot size={22} />
            <span style={{
              position: "absolute",
              top: "-2px",
              right: "-2px",
              width: "8px",
              height: "8px",
              background: "#10b981",
              borderRadius: "50%",
              boxShadow: "0 0 6px #10b981"
            }} />
          </div>
          <span>AI Assistant</span>
          <span style={{
            fontSize: "0.7rem",
            padding: "0.15rem 0.5rem",
            background: "rgba(255,255,255,0.2)",
            borderRadius: "10px",
            textTransform: "uppercase",
            letterSpacing: "0.03em"
          }}>
            {mode === "parent" ? "Parent" : "Student"}
          </span>
        </button>
      )}

      {/* ─── EXPANDED RIGHT-SIDE CHATBOT DRAWER ─── */}
      {isOpen && (
        <div style={{
          position: "fixed",
          bottom: "20px",
          right: "20px",
          width: "390px",
          maxWidth: "calc(100vw - 30px)",
          height: "600px",
          maxHeight: "calc(100vh - 40px)",
          zIndex: 1000,
          background: "rgba(15, 23, 42, 0.94)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(99, 102, 241, 0.35)",
          borderRadius: "20px",
          boxShadow: "0 16px 40px rgba(0, 0, 0, 0.6), 0 0 25px rgba(99, 102, 241, 0.2)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          animation: "fadeIn 0.25s ease-out"
        }}>
          {/* Header */}
          <div style={{
            padding: "1rem 1.25rem",
            background: "rgba(30, 41, 59, 0.8)",
            borderBottom: "1px solid var(--border-card)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <div style={{
                width: "38px",
                height: "38px",
                borderRadius: "12px",
                background: mode === "parent" ? "rgba(16, 185, 129, 0.2)" : "rgba(99, 102, 241, 0.2)",
                color: mode === "parent" ? "#10b981" : "var(--primary)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                border: mode === "parent" ? "1px solid rgba(16, 185, 129, 0.4)" : "1px solid rgba(99, 102, 241, 0.4)"
              }}>
                {mode === "parent" ? <Users size={20} /> : <Bot size={20} />}
              </div>
              <div>
                <div style={{ fontWeight: 800, fontSize: "0.95rem", color: "#fff", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  ACGS Assistant
                  <Sparkles size={14} style={{ color: mode === "parent" ? "#10b981" : "#818cf8" }} />
                </div>
                <div style={{ fontSize: "0.725rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                  <span style={{
                    width: "6px",
                    height: "6px",
                    borderRadius: "50%",
                    background: "#10b981",
                    display: "inline-block"
                  }} />
                  {mode === "parent" ? "Parent Advisory Mode" : "Student Guidance Mode"}
                </div>
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
              <button
                onClick={() => setIsOpen(false)}
                title="Close Assistant"
                style={{
                  background: "transparent",
                  border: "none",
                  color: "var(--text-muted)",
                  padding: "0.4rem",
                  cursor: "pointer",
                  borderRadius: "6px",
                  display: "flex",
                  alignItems: "center"
                }}
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Mode Selector Toggle Pill */}
          <div style={{
            padding: "0.5rem 1rem",
            background: "rgba(0, 0, 0, 0.25)",
            borderBottom: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: "0.775rem"
          }}>
            <span style={{ color: "var(--text-muted)" }}>Perspective:</span>
            <div style={{ display: "flex", gap: "0.3rem" }}>
              <button
                onClick={() => switchMode("student")}
                style={{
                  padding: "0.25rem 0.6rem",
                  borderRadius: "6px",
                  border: "none",
                  background: mode === "student" ? "var(--primary)" : "transparent",
                  color: mode === "student" ? "#fff" : "var(--text-muted)",
                  fontSize: "0.75rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.3rem"
                }}
              >
                <GraduationCap size={13} /> Student
              </button>
              <button
                onClick={() => switchMode("parent")}
                style={{
                  padding: "0.25rem 0.6rem",
                  borderRadius: "6px",
                  border: "none",
                  background: mode === "parent" ? "#10b981" : "transparent",
                  color: mode === "parent" ? "#fff" : "var(--text-muted)",
                  fontSize: "0.75rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.3rem"
                }}
              >
                <Users size={13} /> Parent
              </button>
            </div>
          </div>

          {/* Messages Stream */}
          <div style={{
            flex: 1,
            padding: "1rem",
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: "0.9rem"
          }}>
            {messages.map((m) => {
              const isAi = m.sender === "assistant";
              return (
                <div
                  key={m.id}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: isAi ? "flex-start" : "flex-end"
                  }}
                >
                  <div style={{
                    maxWidth: "88%",
                    padding: "0.75rem 1rem",
                    borderRadius: isAi ? "4px 14px 14px 14px" : "14px 4px 14px 14px",
                    background: isAi ? "rgba(30, 41, 59, 0.9)" : "var(--primary)",
                    color: "#fff",
                    fontSize: "0.875rem",
                    lineHeight: 1.5,
                    border: isAi ? "1px solid var(--border-card)" : "none",
                    whiteSpace: "pre-line"
                  }}>
                    {m.text}
                  </div>
                  <span style={{ fontSize: "0.675rem", color: "var(--text-muted)", marginTop: "0.25rem", padding: "0 0.25rem" }}>
                    {m.time}
                  </span>
                </div>
              );
            })}

            {loading && (
              <div style={{
                alignSelf: "flex-start",
                padding: "0.6rem 0.9rem",
                borderRadius: "4px 14px 14px 14px",
                background: "rgba(30, 41, 59, 0.9)",
                color: "#a5b4fc",
                fontSize: "0.8rem",
                display: "flex",
                alignItems: "center",
                gap: "0.45rem",
                border: "1px solid var(--border-card)"
              }}>
                <RefreshCw size={14} className="spin" /> Formulating response...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompt Chips */}
          <div style={{
            padding: "0.45rem 0.85rem",
            background: "rgba(0, 0, 0, 0.2)",
            borderTop: "1px solid var(--border-subtle)",
            display: "flex",
            gap: "0.35rem",
            overflowX: "auto",
            scrollbarWidth: "none"
          }}>
            {(mode === "parent" ? parentChips : studentChips).map((chip, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleSendMessage(chip)}
                style={{
                  whiteSpace: "nowrap",
                  padding: "0.3rem 0.65rem",
                  borderRadius: "14px",
                  background: "rgba(255, 255, 255, 0.06)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  color: "#cbd5e1",
                  fontSize: "0.725rem",
                  cursor: "pointer",
                  transition: "all 0.15s"
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = mode === "parent" ? "rgba(16, 185, 129, 0.2)" : "rgba(99, 102, 241, 0.2)";
                  e.currentTarget.style.color = "#fff";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)";
                  e.currentTarget.style.color = "#cbd5e1";
                }}
              >
                {chip}
              </button>
            ))}
          </div>

          {/* Input Footer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            style={{
              padding: "0.75rem",
              background: "rgba(15, 23, 42, 0.95)",
              borderTop: "1px solid var(--border-card)",
              display: "flex",
              alignItems: "flex-end",
              gap: "0.5rem"
            }}
          >
            <textarea
              rows={1}
              placeholder={mode === "parent" ? "Ask parent advisory question... (Shift+Enter for newline)" : "Ask student career question... (Shift+Enter for newline)"}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              disabled={loading}
              style={{
                flex: 1,
                background: "rgba(0, 0, 0, 0.3)",
                border: "1px solid var(--border-card)",
                borderRadius: "10px",
                color: "#fff",
                padding: "0.6rem 0.85rem",
                fontSize: "0.875rem",
                outline: "none",
                resize: "none",
                maxHeight: "100px",
                fontFamily: "inherit"
              }}
            />
            <button
              type="submit"
              disabled={!inputText.trim() || loading}
              className="btn btn-primary"
              style={{
                padding: "0.6rem 0.9rem",
                borderRadius: "10px",
                background: mode === "parent" ? "#10b981" : "var(--primary)",
                height: "38px"
              }}
            >
              <Send size={16} />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
