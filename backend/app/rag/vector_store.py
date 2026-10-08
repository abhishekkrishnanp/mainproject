"""
Vector Store and RAG Pipeline for Career Knowledge Base
────────────────────────────────────────────────────────────────────────────
Implements:
1. Retrieval: Vector similarity search (TF-IDF Vector Space Model & Cosine Similarity)
2. Context: Structured context formatting from retrieved career documents
3. LLM Generation: Grounded response generation using Gemini API via HTTPX
   (with deterministic fallback when no API key is configured)
"""
from __future__ import annotations
import math
import re
import logging
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into clean words."""
    text = text.lower()
    tokens = re.findall(r"\b[a-z0-9_+#.-]+\b", text)
    stopwords = {
        "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with",
        "of", "by", "as", "is", "are", "was", "were", "be", "been", "that",
        "this", "it", "from", "which", "who", "whom", "will", "can", "should"
    }
    return [t for t in tokens if t not in stopwords and len(t) > 1]


class CareerVectorStore:
    """
    In-memory vector store indexing career knowledge items.
    Enables semantic / keyword similarity retrieval using Cosine Similarity.
    """

    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.doc_vectors: List[Dict[str, float]] = []
        self.idf: Dict[str, float] = {}
        self.vocab: set = set()

    def build_index(self, careers: List[Any]):
        """Index all careers from the knowledge base."""
        self.documents = []
        for c in careers:
            # Extract fields whether dict or ORM object
            if hasattr(c, "id"):
                cid = c.id
                title = c.title
                desc = c.description or ""
                req_skills = c.required_skills or []
                opt_skills = c.optional_skills or []
                degree = c.required_degree or ""
                roles = c.job_roles or []
                industries = c.industries or []
                growth = c.career_growth or ""
                sal_beg = getattr(c, "salary_beginner", None)
                sal_sen = getattr(c, "salary_senior", None)
            else:
                cid = c.get("id", 0)
                title = c.get("title", "")
                desc = c.get("description", "")
                req_skills = c.get("required_skills", [])
                opt_skills = c.get("optional_skills", [])
                degree = c.get("required_degree", "")
                roles = c.get("job_roles", [])
                industries = c.get("industries", [])
                growth = c.get("career_growth", "")
                sal_beg = c.get("salary_beginner")
                sal_sen = c.get("salary_senior")

            full_text = (
                f"Career: {title}. "
                f"Description: {desc}. "
                f"Required Skills: {', '.join(req_skills)}. "
                f"Preferred Skills: {', '.join(opt_skills)}. "
                f"Education: {degree}. "
                f"Job Roles: {', '.join(roles)}. "
                f"Industries: {', '.join(industries)}. "
                f"Growth: {growth}."
            )

            doc_entry = {
                "id": cid,
                "title": title,
                "description": desc,
                "required_skills": req_skills,
                "optional_skills": opt_skills,
                "required_degree": degree,
                "job_roles": roles,
                "industries": industries,
                "growth": growth,
                "salary_beginner": sal_beg,
                "salary_senior": sal_sen,
                "full_text": full_text,
                "tokens": _tokenize(full_text),
            }
            self.documents.append(doc_entry)

        # Compute IDF
        total_docs = len(self.documents)
        if total_docs == 0:
            return

        df: Dict[str, int] = {}
        for doc in self.documents:
            unique_tokens = set(doc["tokens"])
            for t in unique_tokens:
                df[t] = df.get(t, 0) + 1
                self.vocab.add(t)

        self.idf = {
            t: math.log((1 + total_docs) / (1 + count)) + 1.0
            for t, count in df.items()
        }

        # Compute TF-IDF vector for each document
        self.doc_vectors = []
        for doc in self.documents:
            vec = self._vectorize(doc["tokens"])
            self.doc_vectors.append(vec)

        logger.info(f"[CareerVectorStore] Indexed {len(self.documents)} career documents.")

    def _vectorize(self, tokens: List[str]) -> Dict[str, float]:
        """Convert list of tokens to normalized TF-IDF vector."""
        if not tokens:
            return {}
        tf: Dict[str, float] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0.0) + 1.0

        vec: Dict[str, float] = {}
        for t, count in tf.items():
            if t in self.idf:
                vec[t] = count * self.idf[t]

        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vec.values()))
        if norm > 0:
            return {k: v / norm for k, v in vec.items()}
        return vec

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve top_k career documents matching the query.
        Returns list of dicts with document data and similarity score.
        """
        if not self.documents:
            return []

        q_tokens = _tokenize(query)
        if not q_tokens:
            return self.documents[:top_k]

        q_vec = self._vectorize(q_tokens)
        if not q_vec:
            return self.documents[:top_k]

        scores = []
        for i, doc_vec in enumerate(self.doc_vectors):
            # Cosine similarity between q_vec and doc_vec
            sim = sum(q_vec[k] * doc_vec.get(k, 0.0) for k in q_vec if k in doc_vec)
            scores.append((sim, self.documents[i]))

        scores.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, doc in scores[:top_k]:
            results.append({
                "score": round(score, 4),
                "career": doc,
                "context_chunk": doc["full_text"],
            })
        return results


# Global in-memory vector store instance
vector_store = CareerVectorStore()


class RAGPipeline:
    """
    RAG Pipeline clearly separating:
    1. Retrieval: vector_store.search()
    2. Context: format_context()
    3. LLM Generation: generate_grounded_response()
    """

    @staticmethod
    def retrieve(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Step 1: Retrieve relevant documents from vector store."""
        return vector_store.search(query, top_k=top_k)

    @staticmethod
    def format_context(retrieved_items: List[Dict[str, Any]]) -> str:
        """Step 2: Format retrieved documents into grounded context."""
        context_parts = []
        for idx, item in enumerate(retrieved_items, 1):
            c = item["career"]
            score = item.get("score", 0.0)
            chunk = (
                f"[Document {idx} - Relevancy: {score*100:.1f}%]\n"
                f"Career Title: {c['title']}\n"
                f"Description: {c['description']}\n"
                f"Required Degree: {c['required_degree']}\n"
                f"Required Skills: {', '.join(c['required_skills'])}\n"
                f"Preferred Skills: {', '.join(c['optional_skills'])}\n"
                f"Related Job Roles: {', '.join(c['job_roles'])}\n"
                f"Salary Range: ₹{c.get('salary_beginner', 'N/A')} LPA (Beginner) to ₹{c.get('salary_senior', 'N/A')} LPA (Senior)\n"
                f"Market Growth: {c.get('growth', 'High')}\n"
            )
            context_parts.append(chunk)
        return "\n\n".join(context_parts)

    @staticmethod
    def generate(query: str, context: str, retrieved_items: List[Dict[str, Any]]) -> str:
        """
        Step 3: Grounded response generation.
        Uses Gemini API if key is configured, or grounded fallback template.
        """
        gemini_api_key = settings.GEMINI_API_KEY

        if gemini_api_key and gemini_api_key.strip():
            try:
                # Call Gemini 1.5 Flash via REST API
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
                prompt = (
                    "You are the AI Career Guidance Assistant for an AI-Powered Career Guidance System.\n"
                    "Use ONLY the following retrieved career knowledge base context to answer the student's question.\n"
                    "Ground your advice strictly on these facts. Do not hallucinate external career titles or unverified claims.\n\n"
                    f"--- RETRIEVED CAREER CONTEXT ---\n{context}\n\n"
                    f"--- STUDENT QUERY ---\n{query}\n\n"
                    "Provide a structured, encouraging, and actionable response highlighting relevant careers, essential skills, and next steps."
                )

                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 800}
                }

                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            return candidates[0]["content"]["parts"][0]["text"].strip()
                    else:
                        logger.warning(f"[RAG] Gemini API returned {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"[RAG] Gemini generation failed: {e}. Falling back to grounded template.")

        # Grounded Deterministic Generation
        return RAGPipeline._grounded_template_response(query, retrieved_items)

    @staticmethod
    def _grounded_template_response(query: str, retrieved_items: List[Dict[str, Any]]) -> str:
        """Deterministic grounded response generated strictly from the retrieved knowledge chunks."""
        if not retrieved_items:
            return (
                "Based on our Career Knowledge Base, no exact career matches were found for your query. "
                "Please explore our standard tech paths such as Data Scientist, Machine Learning Engineer, "
                "Software Developer, or Cloud Engineer."
            )

        top_item = retrieved_items[0]
        top_career = top_item["career"]
        top_title = top_career["title"]
        top_desc = top_career["description"]
        req_skills = ", ".join(top_career["required_skills"])
        opt_skills = ", ".join(top_career["optional_skills"])
        roles = ", ".join(top_career["job_roles"])

        other_careers = [item["career"]["title"] for item in retrieved_items[1:]]
        other_text = f" Also consider related paths: {', '.join(other_careers)}." if other_careers else ""

        response = (
            f"### Grounded Guidance: {top_title}\n\n"
            f"**Overview**: {top_desc}\n\n"
            f"**Key Requirements from Knowledge Base**:\n"
            f"- **Required Skills**: {req_skills}\n"
            f"- **Recommended Tools & Technologies**: {opt_skills}\n"
            f"- **Eligible Degrees**: {top_career.get('required_degree', 'B.Tech / B.E. in relevant disciplines')}\n"
            f"- **Typical Job Roles**: {roles}\n"
            f"- **Compensation Outlook**: Entry-level begins around ₹{top_career.get('salary_beginner', 6.0)} LPA, scaling up to ₹{top_career.get('salary_senior', 35.0)}+ LPA.\n\n"
            f"**Career Strategy**:\n"
            f"Focus on mastering the core competencies ({req_skills}). Build hands-on projects and align your coursework with the listed tools.{other_text}"
        )
        return response
