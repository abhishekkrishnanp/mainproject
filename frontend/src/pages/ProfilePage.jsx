import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { User, BookOpen, Wrench, Heart, Save, CheckCircle2, AlertCircle } from "lucide-react";

export default function ProfilePage({ currentUser, token, onProfileUpdate }) {
  const [formData, setFormData] = useState({
    full_name: currentUser?.full_name || "",
    college: currentUser?.college || "National Institute of Technology",
    education_level: currentUser?.education_level || "B.Tech 3rd Year",
    course_degree: currentUser?.course_degree || "Artificial Intelligence & Data Science",
    current_skills: currentUser?.current_skills || "Python, SQL, Statistics, Data Analysis",
    interests: currentUser?.interests || "Machine Learning, Artificial Intelligence, Cloud",
    preferred_work_env: currentUser?.preferred_work_env || "Hybrid",
    location: currentUser?.location || "Bengaluru, India",
    career_preferences: currentUser?.career_preferences || "Machine Learning Engineer, Data Scientist"
  });

  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState(null);

  useEffect(() => {
    if (currentUser) {
      setFormData({
        full_name: currentUser.full_name || "",
        college: currentUser.college || "",
        education_level: currentUser.education_level || "",
        course_degree: currentUser.course_degree || "",
        current_skills: currentUser.current_skills || "",
        interests: currentUser.interests || "",
        preferred_work_env: currentUser.preferred_work_env || "Hybrid",
        location: currentUser.location || "",
        career_preferences: currentUser.career_preferences || ""
      });
    }
  }, [currentUser]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMsg(null);
    try {
      const studentId = currentUser?.id || 1;
      const updated = await api.updateProfile(studentId, formData, token);
      if (onProfileUpdate) onProfileUpdate(updated);
      setMsg({ type: "success", text: "Profile successfully saved to PostgreSQL database!" });
    } catch (err) {
      setMsg({ type: "error", text: err.message || "Failed to update profile" });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Header Banner */}
      <div className="glass-card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <div style={{
            width: "56px",
            height: "56px",
            borderRadius: "50%",
            background: "var(--gradient-brand)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#fff",
            fontSize: "1.4rem",
            fontWeight: 700
          }}>
            {formData.full_name?.charAt(0) || "S"}
          </div>
          <div>
            <h2 style={{ fontSize: "1.4rem" }}>{formData.full_name || "Student Profile"}</h2>
            <div style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              Student ID: <span style={{ color: "var(--primary)", fontWeight: 600 }}>#{currentUser?.id || 1}</span> • Database: <span style={{ color: "var(--success)", fontWeight: 600 }}>PostgreSQL</span>
            </div>
          </div>
        </div>
        <span className="badge badge-primary" style={{ padding: "0.45rem 0.85rem" }}>
          Active Session
        </span>
      </div>

      {msg && (
        <div style={{
          padding: "0.85rem 1rem",
          borderRadius: "var(--radius-md)",
          background: msg.type === "success" ? "var(--success-bg)" : "var(--danger-bg)",
          border: `1px solid ${msg.type === "success" ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)"}`,
          color: msg.type === "success" ? "#6ee7b7" : "#fca5a5",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
          fontSize: "0.9rem"
        }}>
          {msg.type === "success" ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          {msg.text}
        </div>
      )}

      {/* Profile Form */}
      <form onSubmit={handleSave} className="glass-card">
        <h3 style={{ fontSize: "1.15rem", marginBottom: "1.25rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <BookOpen size={18} color="var(--primary)" /> Academic & Educational Background
        </h3>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1rem" }}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">College / University</label>
            <input
              type="text"
              name="college"
              value={formData.college}
              onChange={handleChange}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Education Level / Year</label>
            <input
              type="text"
              name="education_level"
              value={formData.education_level}
              onChange={handleChange}
              className="form-input"
              placeholder="e.g. B.Tech 3rd Year"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Branch / Major</label>
            <input
              type="text"
              name="course_degree"
              value={formData.course_degree}
              onChange={handleChange}
              className="form-input"
              placeholder="e.g. AI & Data Science"
            />
          </div>
        </div>

        <h3 style={{ fontSize: "1.15rem", margin: "1.75rem 0 1.25rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Wrench size={18} color="var(--secondary)" /> Technical Skills & Competencies
        </h3>

        <div className="form-group">
          <label className="form-label">Current Technical Skills (Comma-separated)</label>
          <input
            type="text"
            name="current_skills"
            value={formData.current_skills}
            onChange={handleChange}
            className="form-input"
            placeholder="Python, SQL, Machine Learning, Git"
          />
          <div style={{ display: "flex", gap: "0.35rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
            {formData.current_skills?.split(",").map((s, i) => s.trim() && (
              <span key={i} className="badge badge-primary">{s.trim()}</span>
            ))}
          </div>
        </div>

        <h3 style={{ fontSize: "1.15rem", margin: "1.75rem 0 1.25rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Heart size={18} color="var(--accent)" /> Career Preferences & Aspirations
        </h3>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1rem" }}>
          <div className="form-group">
            <label className="form-label">Interests & Specializations</label>
            <input
              type="text"
              name="interests"
              value={formData.interests}
              onChange={handleChange}
              className="form-input"
              placeholder="Computer Vision, NLP, Big Data"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Preferred Work Style</label>
            <select
              name="preferred_work_env"
              value={formData.preferred_work_env}
              onChange={handleChange}
              className="form-select"
            >
              <option value="Hybrid">Hybrid</option>
              <option value="Remote">Remote</option>
              <option value="Office">Office / On-site</option>
              <option value="Research Lab">Research Lab</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Preferred Career Targets</label>
          <input
            type="text"
            name="career_preferences"
            value={formData.career_preferences}
            onChange={handleChange}
            className="form-input"
            placeholder="Machine Learning Engineer, Data Scientist"
          />
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "1.5rem" }}>
          <button type="submit" disabled={saving} className="btn btn-primary" style={{ padding: "0.75rem 1.5rem" }}>
            <Save size={18} /> {saving ? "Saving Changes..." : "Save Student Profile"}
          </button>
        </div>
      </form>
    </div>
  );
}
