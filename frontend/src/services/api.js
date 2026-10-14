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

  // Rich AI-personalized career recommendations from the conversational assessment
  getAIRecommendations: async (token) => {
    const res = await fetch(`${API_BASE}/career/ai-recommendations`, {
      headers: getHeaders(token),
    });
    if (!res.ok) {
      if (res.status === 404) return null; // No AI profile yet
      throw new Error("Failed to fetch AI career recommendations");
    }
    return res.json();
  },

  getSkillGap: async (arg1, arg2, arg3) => {
    // Flexible signature: (token, careerId, studentId) or (studentId, careerId, token)
    let token = null;
    let careerId = null;
    let studentId = 1;

    if (typeof arg1 === "string" && arg1.length > 30) {
      token = arg1;
      careerId = arg2;
      studentId = arg3 || 1;
    } else {
      studentId = arg1 || 1;
      careerId = arg2;
      token = arg3;
    }

    const res = await fetch(`${API_BASE}/career/skill-gap`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({ career_id: careerId, student_id: studentId }),
    });
    if (!res.ok) throw new Error("Failed to compute skill gap");
    return res.json();
  },

  getRoadmap: async (arg1, arg2, arg3) => {
    // Flexible signature: (token, careerId, studentId) or (studentId, careerId, token)
    let token = null;
    let careerId = null;
    let studentId = 1;

    if (typeof arg1 === "string" && arg1.length > 30) {
      token = arg1;
      careerId = arg2;
      studentId = arg3 || 1;
    } else {
      studentId = arg1 || 1;
      careerId = arg2;
      token = arg3;
    }

    const res = await fetch(`${API_BASE}/career/roadmap`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({ career_id: careerId, student_id: studentId }),
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
        history: extraContext.history || [],
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Assistant service unavailable");
    }
    return res.json();
  },

  // ─── Live Five-Agent Services ───
  getMarketAnalysis: async (careerTitle, location = "Kerala, India", token = null) => {
    const res = await fetch(`${API_BASE}/market-analysis`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({ career_title: careerTitle, location }),
    });
    if (!res.ok) throw new Error("Failed to fetch market analysis");
    return res.json();
  },

  getFeasibilityEvaluation: async (careerTitle, careerId = null, educationLevel = "College Student", token = null) => {
    const res = await fetch(`${API_BASE}/feasibility`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({ career_title: careerTitle, career_id: careerId, education_level: educationLevel }),
    });
    if (!res.ok) throw new Error("Failed to evaluate feasibility");
    return res.json();
  },

  // ─── Career Ecosystem & Quality Services ───
  getCareerMyths: async (category = null) => {
    const url = category ? `${API_BASE}/myths?category=${encodeURIComponent(category)}` : `${API_BASE}/myths`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch career myths");
    return res.json();
  },

  getScholarships: async (educationLevel = null) => {
    const url = educationLevel ? `${API_BASE}/scholarships?education_level=${encodeURIComponent(educationLevel)}` : `${API_BASE}/scholarships`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch scholarships");
    return res.json();
  },

  getExams: async (careerId = null) => {
    const url = careerId ? `${API_BASE}/exams?career_id=${careerId}` : `${API_BASE}/exams`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch exams and certifications");
    return res.json();
  },

  runEvaluationBenchmark: async () => {
    const res = await fetch(`${API_BASE}/evaluation/run`);
    if (!res.ok) throw new Error("Failed to run evaluation benchmark");
    return res.json();
  },

  // ─── Gemini LLM Powered Career Guidance ───
  gemini: {
    getStatus: async () => {
      const res = await fetch(`${API_BASE}/api/v1/gemini/status`);
      if (!res.ok) throw new Error("Failed to fetch Gemini status");
      return res.json();
    },

    getRecommendations: async (data) => {
      const res = await fetch(`${API_BASE}/api/v1/gemini/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to generate AI recommendations");
      }
      return res.json();
    },

    getRoadmap: async (data) => {
      const res = await fetch(`${API_BASE}/api/v1/gemini/roadmap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to generate AI roadmap");
      }
      return res.json();
    },

    getSkillGapAnalysis: async (data) => {
      const res = await fetch(`${API_BASE}/api/v1/gemini/skill-gap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to analyze skill gap");
      }
      return res.json();
    },

    askQuestion: async (data) => {
      const res = await fetch(`${API_BASE}/api/v1/gemini/qa`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to get AI career answer");
      }
      return res.json();
    },

    clarifyMyths: async (data) => {
      const res = await fetch(`${API_BASE}/api/v1/gemini/myth-buster`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to clarify career myths");
      }
      return res.json();
    },

    /**
     * Single-turn authenticated Gemini chat.
     * Stores history server-side; token required.
     */
    chat: async (message, mode = "student", token = null, extraOpts = {}) => {
      const storedToken = token || localStorage.getItem("career_token");
      const res = await fetch(`${API_BASE}/api/v1/gemini/chat`, {
        method: "POST",
        headers: getHeaders(storedToken),
        body: JSON.stringify({ message, mode, ...extraOpts }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        if (res.status === 401) throw new Error("auth_required");
        throw new Error(err.detail || "Chat service unavailable");
      }
      return res.json(); // { reply, source, had_market_context, session_id }
    },

    /**
     * SSE streaming chat. Returns a ReadableStream.
     * Usage: for await (const chunk of stream) { ... }
     */
    chatStream: async (message, mode = "student", token = null, extraOpts = {}) => {
      const storedToken = token || localStorage.getItem("career_token");
      const res = await fetch(`${API_BASE}/api/v1/gemini/chat/stream`, {
        method: "POST",
        headers: getHeaders(storedToken),
        body: JSON.stringify({ message, mode, ...extraOpts }),
      });
      if (!res.ok) {
        if (res.status === 401) throw new Error("auth_required");
        throw new Error("Stream chat service unavailable");
      }
      return res.body; // Caller reads SSE chunks
    },

    /**
     * Retrieve persisted chat history for the current user.
     */
    getChatHistory: async (mode = "student", token = null) => {
      const storedToken = token || localStorage.getItem("career_token");
      const res = await fetch(
        `${API_BASE}/api/v1/gemini/chat/history?mode=${encodeURIComponent(mode)}`,
        { headers: getHeaders(storedToken) }
      );
      if (!res.ok) throw new Error("Failed to fetch chat history");
      return res.json(); // { session_id, mode, messages: [] }
    },

    /**
     * Clear server-side chat history for the current user.
     */
    clearChatHistory: async (mode = "student", token = null) => {
      const storedToken = token || localStorage.getItem("career_token");
      const res = await fetch(
        `${API_BASE}/api/v1/gemini/chat/history?mode=${encodeURIComponent(mode)}`,
        { method: "DELETE", headers: getHeaders(storedToken) }
      );
      if (!res.ok) throw new Error("Failed to clear chat history");
      return res.json();
    },
  },
};


