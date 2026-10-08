# AI-Powered Agentic Career Guidance System

An intelligent, multi-agent career counseling and guidance platform built with a FastAPI backend and a modern React + Vite frontend. The platform leverages coordinated AI agents to provide comprehensive career assessments, personalized recommendations, market trend analysis, and step-by-step learning roadmaps.

## Architecture & Features

- **Multi-Agent Architecture**:
  - **Assessment Agent**: Evaluates user skills, interests, and background.
  - **Career Matching Agent**: Maps profiles to suitable career paths.
  - **Market Intelligence Agent**: Analyzes industry demands, salaries, and growth potential.
  - **Roadmap & Learning Agent**: Builds structured milestones and actionable preparation steps.
  - **Coordinator Agent**: Orchestrates data flow between specialized agents.
- **Backend**: FastAPI, SQLite / SQLAlchemy, Pydantic, JWT authentication, Uvicorn.
- **Frontend**: React 18, Vite, Lucide icons, responsive and interactive modern UI.
- **Visuals**: Architecture diagram included (`system_architecture.jpg`).

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── agents/          # Multi-agent implementations & coordinator
│   │   ├── api/             # API endpoints (auth, assessment, career, roadmap)
│   │   ├── core/            # Config, security, database session
│   │   ├── models/          # SQLAlchemy database models
│   │   └── schemas/         # Pydantic request/response schemas
│   ├── main.py              # Server entry point
│   ├── requirements.txt     # Python dependencies
│   └── test_backend.py      # Automated tests
├── frontend/
│   ├── src/                 # React components, pages, context, and styles
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
├── start_project.bat        # 1-click startup script for Windows
├── .env.example             # Sample environment variables
└── system_architecture.jpg  # System architecture overview
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1-Click Run (Windows)
Double-click `start_project.bat` or run:
```cmd
start_project.bat
```

### Manual Setup

#### 1. Backend
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
Backend API will be running at `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`).

#### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend will be running at `http://localhost:5173`.
