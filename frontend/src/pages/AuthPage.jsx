import React, { useState } from "react";
import { api } from "../services/api";
import { 
  LogIn, 
  UserPlus, 
  Sparkles, 
  CheckCircle, 
  AlertCircle, 
  Lock, 
  User, 
  Mail, 
  Phone, 
  ShieldCheck, 
  KeyRound, 
  Copy, 
  ArrowRight,
  GraduationCap
} from "lucide-react";

export default function AuthPage({ onAuthSuccess, initialMode = "login" }) {
  const [isRegister, setIsRegister] = useState(initialMode === "register");
  const [formData, setFormData] = useState({
    user_id: "",
    name: "",
    email: "",
    password: "",
    confirm_password: "",
    phone: "",
    parent_whatsapp: "",
    education_level: "College Student",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [registrationSuccessData, setRegistrationSuccessData] = useState(null);
  const [copiedPin, setCopiedPin] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handlePreFill = (situation) => {
    const randomSuffix = Math.floor(1000 + Math.random() * 9000);
    if (situation === "college") {
      setFormData({
        user_id: `rohit_${randomSuffix}`,
        name: "Rohit Verma",
        email: `rohit.${randomSuffix}@btech.edu`,
        password: "Password123!",
        confirm_password: "Password123!",
        phone: "9876543210",
        parent_whatsapp: "9876543211",
        education_level: "College Student",
      });
      setIsRegister(true);
    } else if (situation === "school") {
      setFormData({
        user_id: `ananya_${randomSuffix}`,
        name: "Ananya Nair",
        email: `ananya.${randomSuffix}@school.edu`,
        password: "Password123!",
        confirm_password: "Password123!",
        phone: "9847123456",
        parent_whatsapp: "9847123457",
        education_level: "School Student",
      });
      setIsRegister(true);
    } else if (situation === "working") {
      setFormData({
        user_id: `arjun_${randomSuffix}`,
        name: "Arjun K",
        email: `arjun.${randomSuffix}@techcorp.com`,
        password: "Password123!",
        confirm_password: "Password123!",
        phone: "9745123456",
        parent_whatsapp: "",
        education_level: "Working Professional",
      });
      setIsRegister(true);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isRegister) {
        if (formData.password !== formData.confirm_password) {
          throw new Error("Passwords do not match.");
        }
        const data = await api.registerStudent(formData);
        // Show success credentials modal
        setRegistrationSuccessData(data);
      } else {
        const data = await api.loginStudent({
          user_id: formData.user_id,
          password: formData.password,
        });
        onAuthSuccess(data);
      }
    } catch (err) {
      setError(err.message || "Authentication failed. Check credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCredentials = () => {
    if (!registrationSuccessData) return;
    const text = `Student ID: ${registrationSuccessData.student_id}\nParent ID: ${registrationSuccessData.parent_id}\nParent PIN: ${registrationSuccessData.parent_pin}`;
    navigator.clipboard.writeText(text);
    setCopiedPin(true);
    setTimeout(() => setCopiedPin(false), 2500);
  };

  // If newly registered, render Registration Credentials Screen
  if (registrationSuccessData) {
    return (
      <div style={{ maxWidth: "560px", margin: "2rem auto" }}>
        <div className="glass-card" style={{ padding: "2.5rem", textAlign: "center" }}>
          <div style={{
            width: "64px",
            height: "64px",
            borderRadius: "50%",
            background: "rgba(16, 185, 129, 0.15)",
            color: "#10b981",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 1.5rem",
            border: "1px solid rgba(16, 185, 129, 0.3)"
          }}>
            <CheckCircle size={36} />
          </div>

          <h2 style={{ fontSize: "1.75rem", fontWeight: 700, marginBottom: "0.5rem" }}>
            Account Created Successfully!
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", marginBottom: "1.75rem" }}>
            Welcome, <strong>{registrationSuccessData.name}</strong>. Your Student ID and unique Parent credentials have been securely generated.
          </p>

          <div style={{
            background: "rgba(0, 0, 0, 0.3)",
            border: "1px solid var(--border-card)",
            borderRadius: "var(--radius-md)",
            padding: "1.5rem",
            textAlign: "left",
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
            marginBottom: "1.75rem"
          }}>
            <div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                Student ID
              </div>
              <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--primary)", fontFamily: "monospace" }}>
                {registrationSuccessData.student_id}
              </div>
            </div>

            <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: "0.75rem" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                Unique Parent ID
              </div>
              <div style={{ fontSize: "1.15rem", fontWeight: 700, color: "#38bdf8", fontFamily: "monospace" }}>
                {registrationSuccessData.parent_id}
              </div>
            </div>

            <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: "0.75rem" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                Secure Parent PIN (6-Digit)
              </div>
              <div style={{ fontSize: "1.35rem", fontWeight: 800, color: "#10b981", letterSpacing: "3px", fontFamily: "monospace" }}>
                {registrationSuccessData.parent_pin}
              </div>
            </div>

            <div style={{
              background: "rgba(99, 102, 241, 0.08)",
              border: "1px solid rgba(99, 102, 241, 0.2)",
              borderRadius: "var(--radius-sm)",
              padding: "0.75rem",
              fontSize: "0.8rem",
              color: "#c7d2fe",
              display: "flex",
              gap: "0.5rem",
              alignItems: "flex-start"
            }}>
              <ShieldCheck size={16} style={{ flexShrink: 0, marginTop: "2px" }} />
              <div>
                Please share the <strong>Parent ID</strong> and <strong>Parent PIN</strong> with your parents. Their access is strictly read-only and will never alter your personal guidance answers.
              </div>
            </div>
          </div>

          <div style={{ display: "flex", gap: "1rem" }}>
            <button
              onClick={handleCopyCredentials}
              className="btn btn-outline"
              style={{ flex: 1, padding: "0.75rem" }}
            >
              <Copy size={16} /> {copiedPin ? "Copied!" : "Copy Details"}
            </button>
            <button
              onClick={() => onAuthSuccess(registrationSuccessData)}
              className="btn btn-primary"
              style={{ flex: 1, padding: "0.75rem" }}
            >
              Proceed to Dashboard <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "560px", margin: "2rem auto" }}>
      <div className="glass-card">
        {/* Toggle Mode */}
        <div style={{
          display: "flex",
          gap: "0.5rem",
          marginBottom: "1.75rem",
          background: "rgba(0,0,0,0.25)",
          padding: "0.3rem",
          borderRadius: "var(--radius-md)"
        }}>
          <button
            type="button"
            onClick={() => { setIsRegister(false); setError(null); }}
            style={{
              flex: 1,
              padding: "0.65rem",
              borderRadius: "var(--radius-sm)",
              border: "none",
              background: !isRegister ? "var(--primary)" : "transparent",
              color: "#fff",
              fontWeight: 600,
              fontSize: "0.9rem",
              cursor: "pointer",
              transition: "all 0.2s"
            }}
          >
            <LogIn size={16} style={{ display: "inline", verticalAlign: "middle", marginRight: "6px" }} />
            Student Login
          </button>

          <button
            type="button"
            onClick={() => { setIsRegister(true); setError(null); }}
            style={{
              flex: 1,
              padding: "0.65rem",
              borderRadius: "var(--radius-sm)",
              border: "none",
              background: isRegister ? "var(--primary)" : "transparent",
              color: "#fff",
              fontWeight: 600,
              fontSize: "0.9rem",
              cursor: "pointer",
              transition: "all 0.2s"
            }}
          >
            <UserPlus size={16} style={{ display: "inline", verticalAlign: "middle", marginRight: "6px" }} />
            Create Account
          </button>
        </div>

        {/* Demo Fast-Fill Buttons */}
        {isRegister && (
          <div style={{
            marginBottom: "1.5rem",
            padding: "0.85rem",
            background: "rgba(99, 102, 241, 0.08)",
            borderRadius: "var(--radius-md)",
            border: "1px dashed rgba(99, 102, 241, 0.3)"
          }}>
            <div style={{ fontSize: "0.8rem", color: "#a5b4fc", fontWeight: 600, marginBottom: "0.5rem", display: "flex", alignItems: "center", gap: "0.35rem" }}>
              <Sparkles size={14} /> Quick Demo Profiles:
            </div>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              <button
                type="button"
                onClick={() => handlePreFill("college")}
                style={{
                  fontSize: "0.75rem",
                  padding: "0.3rem 0.65rem",
                  background: "rgba(99, 102, 241, 0.2)",
                  border: "1px solid rgba(99, 102, 241, 0.4)",
                  borderRadius: "var(--radius-sm)",
                  color: "#e0e7ff",
                  cursor: "pointer"
                }}
              >
                College (B.Tech)
              </button>
              <button
                type="button"
                onClick={() => handlePreFill("school")}
                style={{
                  fontSize: "0.75rem",
                  padding: "0.3rem 0.65rem",
                  background: "rgba(16, 185, 129, 0.2)",
                  border: "1px solid rgba(16, 185, 129, 0.4)",
                  borderRadius: "var(--radius-sm)",
                  color: "#d1fae5",
                  cursor: "pointer"
                }}
              >
                School Student
              </button>
              <button
                type="button"
                onClick={() => handlePreFill("working")}
                style={{
                  fontSize: "0.75rem",
                  padding: "0.3rem 0.65rem",
                  background: "rgba(245, 158, 11, 0.2)",
                  border: "1px solid rgba(245, 158, 11, 0.4)",
                  borderRadius: "var(--radius-sm)",
                  color: "#fef3c7",
                  cursor: "pointer"
                }}
              >
                Working Professional
              </button>
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.1rem" }}>
          {error && (
            <div style={{
              padding: "0.75rem 1rem",
              borderRadius: "var(--radius-sm)",
              background: "rgba(239, 68, 68, 0.12)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              color: "#fca5a5",
              fontSize: "0.85rem",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem"
            }}>
              <AlertCircle size={16} /> {error}
            </div>
          )}

          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.35rem" }}>
              User ID / Username *
            </label>
            <div style={{ position: "relative" }}>
              <input
                type="text"
                name="user_id"
                value={formData.user_id}
                onChange={handleChange}
                placeholder={isRegister ? "Choose a unique User ID" : "Enter your User ID or Email"}
                required
                className="input"
              />
            </div>
          </div>

          {isRegister && (
            <>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.35rem" }}>
                  Student Full Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="e.g. Kavya Nair"
                  required
                  className="input"
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.35rem" }}>
                  Email Address *
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="student@example.com"
                  required
                  className="input"
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.35rem" }}>
                  Current Academic Situation
                </label>
                <select
                  name="education_level"
                  value={formData.education_level}
                  onChange={handleChange}
                  className="input"
                  style={{ background: "#0f172a", color: "#fff" }}
                >
                  <option value="School Student">School Student (10th / 11th / 12th)</option>
                  <option value="College Student">College Student (Undergraduate B.Tech/B.Sc/B.Com)</option>
                  <option value="Post Graduate">Post Graduate (M.Tech/M.Sc/MCA/MBA)</option>
                  <option value="Working Professional">Working Professional</option>
                </select>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.35rem" }}>
                    Student Phone (Optional)
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    placeholder="10-digit number"
                    className="input"
                  />
                </div>
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.35rem" }}>
                    Parent WhatsApp (Optional)
                  </label>
                  <input
                    type="tel"
                    name="parent_whatsapp"
                    value={formData.parent_whatsapp}
                    onChange={handleChange}
                    placeholder="Parent mobile number"
                    className="input"
                  />
                </div>
              </div>
            </>
          )}

          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.35rem" }}>
              Password *
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
              className="input"
            />
          </div>

          {isRegister && (
            <div>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.35rem" }}>
                Confirm Password *
              </label>
              <input
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                className="input"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: "100%", padding: "0.8rem", fontSize: "1rem", marginTop: "0.5rem" }}
          >
            {loading ? "Processing..." : isRegister ? "Create Student Account" : "Login to Student Mode"}
          </button>
        </form>
      </div>
    </div>
  );
}
