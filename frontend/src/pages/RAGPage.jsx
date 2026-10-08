import React, { useState } from "react";
import { api } from "../services/api";
import { 
  Search, Sparkles, Database, MessageSquare, 
  AlertCircle, Loader, ChevronDown, ChevronUp, Cpu
} from "lucide-react";

const SAMPLE_QUERIES = [
  "What skills do I need to become a Data Scientist?",
  "Compare Machine Learning Engineer vs AI Engineer roles",
  "What is the salary range for a Cloud Architect?",
  "What are the prerequisites for becoming a DevOps Engineer?",
  "How do I transition from Data Analyst to Data Scientist?",
  "What programming languages are needed for Full Stack development?",
];

export default function RAGPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showContext, setShowContext] = useState(false);
  const [history, setHistory] = useState([]);

  const handleSearch = async (searchQuery) => {
    const q = searchQuery || query;
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await api.queryRAG(q.trim(), 3);
      setResult(data);
      setHistory(prev => [{ query: q, result: data }, ...prev.slice(0, 4)]);
    } catch (err) {
      setError(err.message || "RAG query failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      {/* Header */}
      <div style={{ textAlign: "center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", padding: "0.35rem 1rem", borderRadius: "var(--radius-full)", background: "rgba(56, 189, 248, 0.12)", border: "1px solid rgba(56, 189, 248, 0.3)", color: "#7dd3fc", fontSize: "0.85rem", fontWeight: 600, marginBottom: "1rem" }}>
          <Cpu size={14} /> Grounded RAG Pipeline
        </div>
        <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>RAG Career Knowledge Explorer</h1>
        <p style={{ color: "var(--text-secondary)" }}>
          Ask anything about careers — powered by TF-IDF vector retrieval + Gemini LLM for grounded, factual answers.
        </p>
      </div>

      {/* Search Box */}
      <div className="glass-card">
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "flex-end" }}>
          <div style={{ flex: 1 }}>
            <label className="form-label">Career Query</label>
            <div style={{ position: "relative" }}>
              <Search size={16} style={{ position: "absolute", left: "0.85rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="e.g. What skills do I need for Machine Learning?"
                className="form-input"
                style={{ paddingLeft: "2.5rem" }}
              />
            </div>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => handleSearch()}
            disabled={loading || !query.trim()}
            style={{ padding: "0.7rem 1.5rem" }}
          >
            {loading ? <Loader size={16} style={{ animation: "spin 1s linear infinite" }} /> : <Search size={16} />}
            {loading ? "Searching..." : "Query RAG"}
          </button>
        </div>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>

        {/* Sample Queries */}
        <div style={{ marginTop: "1rem" }}>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginBottom: "0.5rem" }}>Quick sample queries:</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
            {SAMPLE_QUERIES.map((q, i) => (
              <button
                key={i}
                onClick={() => { setQuery(q); handleSearch(q); }}
                style={{ fontSize: "0.75rem", padding: "0.25rem 0.65rem", borderRadius: "var(--radius-full)", background: "rgba(56, 189, 248, 0.08)", border: "1px solid rgba(56, 189, 248, 0.2)", color: "#7dd3fc", cursor: "pointer", transition: "all 0.2s" }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{ background: "var(--danger-bg)", border: "1px solid rgba(239,68,68,0.3)", color: "#fca5a5", padding: "0.85rem 1rem", borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <AlertCircle size={16} /> {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Query echo */}
          <div style={{ display: "flex", gap: "0.75rem", alignItems: "flex-start" }}>
            <div style={{ background: "rgba(99, 102, 241, 0.15)", border: "1px solid rgba(99,102,241,0.3)", width: "36px", height: "36px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <MessageSquare size={16} color="#818cf8" />
            </div>
            <div className="glass-card" style={{ flex: 1, padding: "1rem" }}>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.3rem" }}>Your Query</div>
              <p style={{ color: "var(--text-secondary)" }}>{result.query}</p>
            </div>
          </div>

          {/* AI Response */}
          <div style={{ display: "flex", gap: "0.75rem", alignItems: "flex-start" }}>
            <div style={{ background: "rgba(56, 189, 248, 0.15)", border: "1px solid rgba(56,189,248,0.3)", width: "36px", height: "36px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <Sparkles size={16} color="#38bdf8" />
            </div>
            <div className="glass-card" style={{ flex: 1 }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                <div style={{ fontSize: "0.8rem", color: "#7dd3fc", fontWeight: 600 }}>AI Response (Gemini + RAG)</div>
                <span className="badge badge-info">Grounded</span>
              </div>
              <div style={{ color: "var(--text-main)", lineHeight: 1.7, fontSize: "0.95rem", whiteSpace: "pre-wrap" }}>
                {result.response}
              </div>
            </div>
          </div>

          {/* Retrieved Careers */}
          {result.retrieved_careers && result.retrieved_careers.length > 0 && (
            <div className="glass-card">
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                <Database size={16} color="#10b981" />
                <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>Retrieved from Knowledge Base</span>
                <span className="badge badge-success">{result.retrieved_careers.length} careers matched</span>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                {result.retrieved_careers.map((c, i) => (
                  <span key={i} style={{ fontSize: "0.82rem", padding: "0.3rem 0.75rem", borderRadius: "var(--radius-full)", background: "rgba(16, 185, 129, 0.12)", border: "1px solid rgba(16, 185, 129, 0.25)", color: "#6ee7b7" }}>
                    {c}
                  </span>
                ))}
              </div>

              {/* Sources with Scores */}
              {result.sources && result.sources.length > 0 && (
                <div style={{ marginTop: "0.75rem", display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
                  {result.sources.map((s, i) => (
                    <div key={i} style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                      {s.career}: <span style={{ color: "#10b981", fontWeight: 600 }}>{(s.score * 100).toFixed(0)}% match</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* RAG Context Toggle */}
          {result.context && (
            <div className="glass-card" style={{ background: "rgba(15, 23, 42, 0.8)" }}>
              <button
                onClick={() => setShowContext(!showContext)}
                style={{ display: "flex", alignItems: "center", gap: "0.5rem", background: "transparent", border: "none", color: "var(--text-secondary)", cursor: "pointer", fontSize: "0.85rem", fontWeight: 600, padding: 0 }}
              >
                {showContext ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                {showContext ? "Hide" : "Show"} RAG Retrieved Context (TF-IDF Vector Search)
              </button>
              {showContext && (
                <pre style={{ marginTop: "1rem", fontSize: "0.78rem", color: "var(--text-muted)", whiteSpace: "pre-wrap", fontFamily: "monospace", maxHeight: "300px", overflowY: "auto", padding: "0.75rem", background: "rgba(0,0,0,0.3)", borderRadius: "var(--radius-sm)" }}>
                  {result.context}
                </pre>
              )}
            </div>
          )}
        </div>
      )}

      {/* Query History */}
      {history.length > 1 && (
        <div>
          <h3 style={{ fontSize: "1rem", marginBottom: "0.75rem", color: "var(--text-secondary)" }}>Recent Queries</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {history.slice(1).map((h, i) => (
              <button
                key={i}
                onClick={() => { setQuery(h.query); setResult(h.result); }}
                style={{ textAlign: "left", padding: "0.6rem 1rem", borderRadius: "var(--radius-md)", background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-subtle)", color: "var(--text-secondary)", cursor: "pointer", fontSize: "0.875rem" }}
              >
                <Search size={13} style={{ marginRight: "0.5rem", opacity: 0.6 }} />
                {h.query}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Technical Info */}
      <div className="glass-card" style={{ background: "rgba(15, 23, 42, 0.6)" }}>
        <h3 style={{ fontSize: "0.95rem", marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Cpu size={16} color="#38bdf8" /> RAG Pipeline Architecture
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1rem" }}>
          {[
            { step: "1. Embed", desc: "TF-IDF vectorizes query and career documents", color: "#6366f1" },
            { step: "2. Retrieve", desc: "Cosine similarity finds top-k matching careers", color: "#38bdf8" },
            { step: "3. Format", desc: "Retrieved context is structured for LLM prompt", color: "#10b981" },
            { step: "4. Generate", desc: "Gemini LLM generates grounded response", color: "#f59e0b" },
          ].map((s, i) => (
            <div key={i}>
              <div style={{ fontWeight: 700, fontSize: "0.85rem", color: s.color, marginBottom: "0.2rem" }}>{s.step}</div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>{s.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
