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
cp .env.example .env
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