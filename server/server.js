import "dotenv/config";
import express from "express";
import cors from "cors";
import OpenAI from "openai";
import rateLimit from "express-rate-limit";
import helmet from "helmet";

// ─── Express 5 + OpenAI SDK v6 + Groq ──────────────────────────────────────

const app = express();

// Security middleware
app.use(
  cors({
    origin: [
      process.env.FRONTEND_URL || "http://localhost:5173",
      "http://localhost:5173",
      /\.vercel\.app$/,
    ],
    credentials: true,
  })
);
app.use(express.json({ limit: "10mb" }));

// Rate limiting (v7+ API)
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 100,
  standardHeaders: "draft-8",
  legacyHeaders: false,
  message: { error: "Too many requests from this IP, please try again later." },
});
app.use(limiter);

const API_KEY = process.env.GROQ_API_KEY;

if (!API_KEY) {
  console.warn("⚠️  WARNING: GROQ_API_KEY is not set in environment variables.");
}

// Groq — OpenAI-compatible API via OpenAI SDK v6
const client = new OpenAI({
  baseURL: "https://api.groq.com/openai/v1",
  apiKey: API_KEY || "missing-key",
});

const SUPPORTED_LANGUAGES = [
  "javascript", "typescript", "python", "java", "go",
  "rust", "c", "cpp", "csharp", "php", "ruby", "swift",
  "kotlin", "sql", "bash", "html", "css",
];

// ─── POST /api/explain-code ─────────────────────────────────────────────────
app.post("/api/explain-code", async (req, res) => {
  const { code, language } = req.body;

  if (!code || typeof code !== "string" || code.trim().length === 0) {
    return res.status(400).json({ error: "code is required and must be a non-empty string." });
  }
  if (code.length > 20000) {
    return res.status(400).json({ error: "Code exceeds maximum length of 20,000 characters." });
  }

  const lang = language && SUPPORTED_LANGUAGES.includes(language.toLowerCase())
    ? language.toLowerCase()
    : "";

  const messages = [
    {
      role: "system",
      content:
        "You are an expert software engineer and teacher. Explain code clearly and accurately. " +
        "Use markdown: headings, bullets, and inline code blocks. " +
        "Structure: 1) Overview (what it does), 2) Step-by-step breakdown, 3) Key concepts.",
    },
    {
      role: "user",
      content: `Explain this${lang ? ` ${lang}` : ""} code:\n\n\`\`\`${lang}\n${code.trim()}\n\`\`\``,
    },
  ];

  try {
    const response = await client.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      messages,
      temperature: 0.3,
      max_tokens: 1200,
    });

    const explanation = response?.choices?.[0]?.message?.content;
    if (!explanation) {
      return res.status(500).json({ error: "AI returned an empty response. Please try again." });
    }

    return res.json({
      explanation,
      language: lang || "unknown",
      tokens: response.usage?.total_tokens ?? null,
    });
  } catch (err) {
    console.error("Code Explain API Error:", err);
    if (err?.status === 401) return res.status(500).json({ error: "Invalid API key. Check GROQ_API_KEY." });
    if (err?.status === 429) return res.status(429).json({ error: "AI service rate limit hit. Try again shortly." });
    return res.status(500).json({
      error: "An unexpected server error occurred.",
      details: process.env.NODE_ENV === "development" ? err.message : undefined,
    });
  }
});

// ─── GET /api/health ────────────────────────────────────────────────────────
app.get("/api/health", (_req, res) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    hasApiKey: !!API_KEY,
    uptime: Math.round(process.uptime()),
    node: process.version,
    provider: "Groq",
    model: "llama-3.3-70b-versatile",
  });
});

// ─── Error handler ───────────────────────────────────────────────────────────
app.use((err, _req, res, _next) => {
  console.error("Unhandled error:", err);
  res.status(500).json({ error: "Internal server error" });
});

// ─── 404 ────────────────────────────────────────────────────────────────────
app.use((_req, res) => {
  res.status(404).json({ error: "Route not found" });
});

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
  console.log(`\n🚀 CodeSplain API  →  http://localhost:${PORT}`);
  console.log(`   Health check   →  http://localhost:${PORT}/api/health`);
  console.log(`   Provider       →  Groq (llama-3.3-70b-versatile)`);
  console.log(`   API Key        →  ${API_KEY ? "✅ configured" : "❌ MISSING — set GROQ_API_KEY"}\n`);
});
