import { useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface CodeExplanationProps {
  explanation: string;
  language: string;
  tokens: number | null;
}

const CopyIcon = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const LANG_COLORS: Record<string, string> = {
  javascript: "#f7df1e", typescript: "#3178c6", python: "#3776ab",
  java: "#ed8b00", go: "#00add8", rust: "#ce412b", cpp: "#00599c",
  csharp: "#9b4f96", php: "#777bb4", ruby: "#cc342d", swift: "#f05138",
  kotlin: "#7f52ff", sql: "#e38c00", bash: "#4eaa25", html: "#e34f26", css: "#1572b6",
};

const CodeExplanation = ({ explanation, language, tokens }: CodeExplanationProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(explanation).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const langColor = LANG_COLORS[language] ?? "var(--accent)";

  return (
    <div
      className="slide-up w-full mt-5"
      style={{
        background: "var(--card)",
        border: "1px solid var(--border-hi)",
        borderRadius: "var(--radius-lg)",
        overflow: "hidden",
      }}
    >
      {/* Top accent line */}
      <div style={{ height: 2, background: `linear-gradient(90deg, ${langColor}, var(--accent), transparent)` }} />

      {/* Header */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "12px 18px",
        borderBottom: "1px solid var(--border)",
        background: "var(--surface)",
      }}>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {tokens != null && (
            <div style={{
              fontFamily: "var(--font-code)", fontSize: "0.65rem", color: "var(--text-3)",
              background: "var(--raised)", border: "1px solid var(--border)",
              borderRadius: "var(--radius-sm)", padding: "3px 8px",
              display: "flex", alignItems: "center", gap: 5,
            }}>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
              </svg>
              {tokens.toLocaleString()} tokens
            </div>
          )}

          {language && language !== "unknown" && (
            <div style={{
              fontFamily: "var(--font-code)", fontSize: "0.68rem",
              background: `${langColor}18`, color: langColor,
              border: `1px solid ${langColor}30`,
              borderRadius: "var(--radius-sm)", padding: "3px 9px", fontWeight: 500,
            }}>
              {language}
            </div>
          )}

          <button
            onClick={handleCopy}
            style={{
              display: "flex", alignItems: "center", gap: 5,
              fontFamily: "var(--font-code)", fontSize: "0.68rem",
              color: copied ? "var(--green)" : "var(--text-3)",
              background: copied ? "var(--green-lo)" : "var(--raised)",
              border: `1px solid ${copied ? "rgba(74,222,128,0.25)" : "var(--border)"}`,
              borderRadius: "var(--radius-sm)", padding: "4px 10px",
              cursor: "pointer", transition: "all 0.2s",
            }}
          >
            {copied ? <CheckIcon /> : <CopyIcon />}
            {copied ? "COPIED" : "COPY"}
          </button>
        </div>
      </div>

      {/* Body */}
      <div style={{ padding: "24px 28px" }}>
        <div className="prose">
          <Markdown remarkPlugins={[remarkGfm]}>{explanation}</Markdown>
        </div>
      </div>
    </div>
  );
};

export default CodeExplanation;
