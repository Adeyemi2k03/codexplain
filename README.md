# 🧠 CodeXplain — AI-Powered Code Explainer

Paste any code snippet and get a clear, structured explanation powered by **Groq AI**. Built with a modern full-stack TypeScript setup: **React 19 + Vite 8** on the frontend, **Node.js + Express 5** on the backend.

---

## ✨ Features

- 🔍 Explains code in 16 languages (JavaScript, TypeScript, Python, Go, Rust, and more)
- 📝 Structured markdown output — overview, step-by-step breakdown, and key concepts
- ⚡ React 19 `useActionState` for form handling
- 🌗 Light / Dark mode with `localStorage` persistence
- 🔒 Rate limiting, CORS, and Helmet security headers on the backend
- 📡 Live API health status indicator in the header
- 📋 Copy explanation to clipboard
- 🎨 Cobalt blue theme with IBM Plex Mono + Outfit fonts

---

## 🗂️ Project Structure

codexplain/
├── codexplain/
│   ├── src/
│   │   ├── actions/index.ts
│   │   ├── components/
│   │   │   ├── forms/CodeExplainForm.tsx
│   │   │   ├── CodeEntry.tsx
│   │   │   ├── CodeExplanation.tsx
│   │   │   ├── Error.tsx
│   │   │   └── Header.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   └── vite-env.d.ts
│   ├── .env.example
│   ├── tsconfig.json
│   └── vite.config.ts
└── server/
    ├── server.js
    ├── .env.example
    └── package.json

    ---

## 🛠️ Tech Stack

### Frontend
| Tool | Version | Purpose |
|---|---|---|
| React | 19.x | UI + useActionState |
| Vite | 8.x | Build tool & dev server |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Styling |
| react-markdown | latest | Render AI markdown output |
| react-error-boundary | latest | Error fallback |

### Backend
| Tool | Version | Purpose |
|---|---|---|
| Node.js | 22.x | Runtime |
| Express | 5.x | HTTP framework |
| OpenAI SDK | 6.x | Groq API client |
| Helmet | 8.x | Security headers |
| express-rate-limit | 7.x | Rate limiting |

---

## 🚀 Getting Started

### 1 — Clone
```bash
git clone https://github.com/YOUR_USERNAME/codexplain.git
cd codexplain
```

### 2 — Backend
```bash
cd server
cp .env.example .env
npm install
npm run dev
```

### 3 — Frontend
```bash
cd ../codexplain
cp .env.example .env# 🧠 CodeXplain — AI-Powered Code Explainer

Paste any code snippet and get a clear, structured explanation powered by **Groq AI**. Built with a modern full-stack setup: **React 19 + TypeScript** on the frontend, **Django REST Framework** on the backend.

---

## ✨ Features

- 🔍 Explains code in 16 languages (JavaScript, TypeScript, Python, Go, Rust, and more)
- 📝 Structured markdown output — overview, step-by-step breakdown, and key concepts
- ⚡ React 19 `useActionState` for form handling with async polling
- 🌗 Light / Dark mode with `localStorage` persistence
- 🔒 DRF throttling, CORS, and token authentication
- 📡 Live API health status indicator in the header
- 📋 Copy explanation to clipboard
- 🎨 Cobalt blue theme with IBM Plex Mono + Outfit fonts
- 🗄️ PostgreSQL explanation history per user/session
- ⚙️ Redis caching — identical code served instantly without API call
- 🔄 Celery async tasks — Groq calls offloaded from the web server
- 📖 Auto-generated Swagger UI at `/api/schema/swagger-ui/`

---

## 🗂️ Project Structure

```
codexplain/
├── codexplain/          # Frontend — React 19 + Vite 8 + Tailwind CSS 4 + TypeScript
│   ├── src/
│   │   ├── actions/index.ts
│   │   ├── components/
│   │   │   ├── forms/CodeExplainForm.tsx
│   │   │   ├── CodeEntry.tsx
│   │   │   ├── CodeExplanation.tsx
│   │   │   ├── Error.tsx
│   │   │   └── Header.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   └── vite-env.d.ts
│   ├── .env.example
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── backend/             # Backend — Django REST Framework
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── wsgi.py
│   ├── explainer/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── tasks.py
│   │   └── urls.py
│   ├── core/
│   │   └── exceptions.py
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
│
└── server/              # Legacy Express backend (replaced by Django)
```

---

## 🛠️ Tech Stack

### Frontend
| Tool | Version | Purpose |
|---|---|---|
| React | 19.x | UI + useActionState |
| Vite | 8.x | Build tool & dev server |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Styling |
| react-markdown | latest | Render AI markdown output |
| react-error-boundary | latest | Error fallback |

### Backend
| Tool | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Runtime |
| Django | 5.x | Web framework |
| Django REST Framework | 3.15.x | API layer |
| PostgreSQL | 16 | Explanation history persistence |
| Redis | 7 | Caching + Celery broker |
| Celery | 5.4.x | Async task queue for Groq calls |
| Groq SDK | latest | LLM API client |
| drf-spectacular | 0.27.x | Auto Swagger/OpenAPI docs |
| structlog | 24.x | Structured JSON logging |
| Docker | latest | Local PostgreSQL + Redis containers |

---

## 🚀 Getting Started

### Prerequisites
- Node.js 20+
- Python 3.10+
- Docker Desktop
- A free [Groq](https://groq.com) API key

### 1 — Clone
```bash
git clone https://github.com/Adeyemi2k03/codexplain.git
cd codexplain
```

### 2 — Backend setup
```bash
cd backend

# Start PostgreSQL and Redis
docker compose up -d

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run migrations
python manage.py migrate

# Start Django server
python manage.py runserver
```

### 3 — Start Celery worker (new terminal)
```bash
cd backend
source venv/Scripts/activate
celery -A config worker --loglevel=info --pool=solo
```

### 4 — Frontend setup (new terminal)
```bash
cd codexplain
cp .env.example .env
npm install
npm run dev
```

Visit **http://localhost:5173** — header should show **API LIVE**.

API docs available at **http://127.0.0.1:8000/api/schema/swagger-ui/**

---

## ⚙️ Environment Variables

### `backend/.env`
| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | *(required)* | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `GROQ_API_KEY` | *(required)* | Groq API key |
| `GROQ_MODEL` | `qwen/qwen3.6-27b` | Groq model to use |
| `DB_NAME` | `codexplain` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | *(required)* | PostgreSQL password |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `REDIS_URL` | `redis://127.0.0.1:6379/0` | Redis connection URL |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |

### `codexplain/.env`
| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000/api` | Django backend URL |

---

## 📡 Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register/` | Register a new user |
| `POST` | `/api/auth/login/` | Login and get token |
| `POST` | `/api/auth/logout/` | Invalidate token |
| `GET` | `/api/auth/me/` | Get current user |
| `POST` | `/api/explanations/explain/` | Submit code for explanation |
| `GET` | `/api/explanations/{id}/` | Poll for explanation result |
| `GET` | `/api/explanations/` | List explanation history |
| `GET` | `/api/health/` | API health check |
| `GET` | `/api/schema/swagger-ui/` | Swagger UI docs |

---

## 🔑 Getting a Groq API Key

1. Sign up free at [https://groq.com](https://groq.com)
2. Go to **API Keys** in your dashboard
3. Create a key and add it to `backend/.env` as `GROQ_API_KEY`

---

## 🏗️ Architecture

```
Frontend → POST /api/explanations/explain/
         → DRF Throttle check
         → Cache check (Redis SHA-256 hash lookup)
              ↓ Cache HIT → return instantly
              ↓ Cache MISS → Celery task dispatched
                           → Worker calls Groq API
                           → Result saved to PostgreSQL
                           → Result cached in Redis
                           → Client polls GET /api/explanations/{id}/
```
npm install
npm run dev
```

Visit **http://localhost:5173** — header should show **API LIVE**.

---

## ⚙️ Environment Variables

### `server/.env`
| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | *(required)* | Groq API key |
| `PORT` | `3002` | Server port |
| `FRONTEND_URL` | `http://localhost:5173` | CORS origin |
| `NODE_ENV` | `development` | Error detail level |

### `codexplain/.env`
| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:3002/api` | Backend URL |

---

## 🔑 Getting a Groq API Key

1. Sign up free at [https://groq.com](https://groq.com)
2. Go to **API Keys** in your dashboard
3. Create a key and add it to `server/.env`