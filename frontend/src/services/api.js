/**
 * API Service for AI Powered Agentic Career Guidance System (ACGS)
 */
const API_BASE = "http://127.0.0.1:8000";

const getHeaders = (token) => {
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

export const api = {
  // ─── Health / Status ───
  getStatus: async () => {
    const res = await fetch(`${API_BASE}/`);
    return res.json();
  },

  // ─── Student Mode Authentication ───
  registerStudent: async (studentData) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(studentData),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Student registration failed");
    }
    return res.json();
  },

  loginStudent: async (credentials) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Student login failed");
    }
    return res.json();
  },

  // Legacy alias for register/login
  register: async (userData) => {
    // If incoming object matches new student schema or legacy
    const payload = {
      user_id: userData.user_id || (userData.email ? userData.email.split("@")[0] : `user_${Date.now()}`),
      name: userData.name || userData.full_name || "Student",
      email: userData.email,
      password: userData.password,
      confirm_password: userData.confirm_password || userData.password,
      phone: userData.phone || null,
      parent_whatsapp: userData.parent_whatsapp || null,
      education_level: userData.education_level || "College Student",
      branch: userData.course_degree || userData.branch || null,
      university: userData.college || userData.university || null,
    };
    return api.registerStudent(payload);
  },

  login: async (credentials) => {
    const payload = {
      user_id: credentials.user_id || credentials.email,
      password: credentials.password,
    };
    return api.loginStudent(payload);
  },

  // ─── Student Profile ───
  getStudentProfile: async (token) => {
    const res = await fetch(`${API_BASE}/student/profile`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error("Failed to fetch student profile");
    return res.json();
  },

  updateStudentProfile: async (updateData, token) => {
    const res = await fetch(`${API_BASE}/student/profile`, {
      method: "PUT",
      headers: getHeaders(token),
      body: JSON.stringify(updateData),
    });
    if (!res.ok) throw new Error("Failed to update student profile");
    return res.json();
  },

  getProfile: async (studentId, token) => {
    const res = await fetch(`${API_BASE}/profile/${studentId}`, {
      headers: getHeaders(token),
    });
    if (!res.ok) return api.getStudentProfile(token);
    return res.json();
  },

  updateProfile: async (studentId, updateData, token) => {
    const res = await fetch(`${API_BASE}/profile/${studentId}`, {
      method: "PUT",
      headers: getHeaders(token),
      body: JSON.stringify(updateData),
    });
    if (!res.ok) return api.updateStudentProfile(updateData, token);
    return res.json();
  },

  // ─── Parent Mode Authentication & Read-Only Dashboard ───
  loginParent: async (parentCredentials) => {
    const res = await fetch(`${API_BASE}/parent/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(parentCredentials),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Parent authentication failed. Check Parent ID and PIN.");
    }
    return res.json();
  },

  getParentStudentSummary: async (parentToken) => {
    const res = await fetch(`${API_BASE}/parent/student-summary`, {
      headers: getHeaders(parentToken),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to retrieve parent student summary");
    }
    return res.json();
  },

  // ─── Deep Conversational Self-Assessment Chatbot ───
  startDeepAssessment: async (token) => {
    const res = await fetch(`${API_BASE}/assessment/start`, {
      method: "POST",
      headers: getHeaders(token),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to start assessment");
    }
    return res.json();
  },

  sendAssessmentMessage: async (payload, token) => {
    const res = await fetch(`${API_BASE}/assessment/message`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to process assessment response");
    }
    return res.json();
  },

  getAssessmentStatus: async (token) => {
    const res = await fetch(`${API_BASE}/assessment/status`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error("Failed to fetch assessment status");
    return res.json();
  },

  getAssessmentHistory: async (token) => {
    const res = await fetch(`${API_BASE}/assessment/history`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error("Failed to fetch assessment history");
    return res.json();
  },

  getCareerProfile: async (token) => {
    const res = await fetch(`${API_BASE}/career-profile`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error("Failed to fetch career profile");
    return res.json();
  },

  // ─── Legacy Assessment & Recommendations (Preserved) ───
  submitAssessment: async (answers, token, studentId) => {
    const res = await fetch(`${API_BASE}/assessment`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({ answers, student_id: studentId }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Assessment submission failed");
    }
    return res.json();
  },

  getAssessment: async (studentId, token) => {
    const res = await fetch(`${API_BASE}/assessment/${studentId}`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error("Assessment not found");
    return res.json();
  },

  getAllCareers: async () => {
    const res = await fetch(`${API_BASE}/api/v1/career`);
    if (!res.ok) throw new Error("Failed to fetch careers");
    return res.json();
  },

  getRecommendations: async (token, studentId) => {
    const res = await fetch(`${API_BASE}/career/recommend`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({ student_id: studentId || 1 }),
    });
    if (!res.ok) throw new Error("Failed to fetch recommendations");
    return res.json();
  },

  getSkillGap: async (token, careerId, studentId) => {
    const res = await fetch(`${API_BASE}/career/skill-gap`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({ career_id: careerId, student_id: studentId || 1 }),
    });
    if (!res.ok) throw new Error("Failed to compute skill gap");
    return res.json();
  },

  getRoadmap: async (token, careerId, studentId) => {
    const res = await fetch(`${API_BASE}/career/roadmap`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({ career_id: careerId, student_id: studentId || 1 }),
    });
    if (!res.ok) throw new Error("Failed to generate roadmap");
    return res.json();
  },

  ragQuery: async (query, topK = 3) => {
    const res = await fetch(`${API_BASE}/rag/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: topK }),
    });
    if (!res.ok) throw new Error("RAG query failed");
    return res.json();
  },

  // ─── Dual-Mode Assistant Chatbot (Student & Parent) ───
  askAssistant: async (message, mode = "student", extraContext = {}) => {
    const res = await fetch(`${API_BASE}/assistant/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        mode,
        student_name: extraContext.student_name,
        education_level: extraContext.education_level,
        current_page: extraContext.current_page,
      }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Assistant service unavailable");
    }
    return res.json();
  },
};

