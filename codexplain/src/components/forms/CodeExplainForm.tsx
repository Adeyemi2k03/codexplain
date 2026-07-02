import { useActionState } from "react";
import { explain, type ExplainState } from "../../actions/index.ts";
import CodeExplanation from "../CodeExplanation.tsx";
import Error from "../Error.tsx";

interface Language {
  value: string;
  label: string;
  icon: string;
}

const LANGUAGES: Language[] = [
  { value: "javascript", label: "JavaScript", icon: "JS" },
  { value: "typescript", label: "TypeScript", icon: "TS" },
  { value: "python",     label: "Python",     icon: "PY" },
  { value: "java",       label: "Java",       icon: "JV" },
  { value: "go",         label: "Go",         icon: "GO" },
  { value: "rust",       label: "Rust",       icon: "RS" },
  { value: "cpp",        label: "C++",        icon: "C+" },
  { value: "csharp",     label: "C#",         icon: "C#" },
  { value: "php",        label: "PHP",        icon: "PHP" },
  { value: "ruby",       label: "Ruby",       icon: "RB" },
  { value: "swift",      label: "Swift",      icon: "SW" },
  { value: "kotlin",     label: "Kotlin",     icon: "KT" },
  { value: "sql",        label: "SQL",        icon: "SQL" },
  { value: "bash",       label: "Bash",       icon: "SH" },
  { value: "html",       label: "HTML",       icon: "HT" },
  { value: "css",        label: "CSS",        icon: "CSS" },
];

interface SpinnerProps {
  size?: number;
}

const Spinner = ({ size = 16 }: SpinnerProps) => (
  <div style={{
    width: size, height: size, borderRadius: "50%",
    border: "2px solid rgba(255,255,255,0.15)",
    borderTopColor: "currentColor",
    animation: "spin 0.7s linear infinite",
    flexShrink: 0,
  }} />
);

const CodeExplainForm = () => {
  const [formState, formAction, isPending] = useActionState<ExplainState, FormData>(explain, null);

  return (
    <div className="slide-up delay-2 w-full max-w-4xl">

      {/* Main card */}
      <div style={{
        background: "var(--card)",
        border: "1px solid var(--border-hi)",
        borderRadius: "var(--radius-xl)",
        overflow: "hidden",
        boxShadow: "0 8px 48px rgba(0,0,0,0.5)",
      }}>
        {/* Title bar */}
        <div style={{
          display: "flex", alignItems: "center", gap: 10,
          padding: "13px 20px",
          borderBottom: "1px solid var(--border)",
          background: "var(--surface)",
        }}>
          
          <span style={{ fontFamily: "var(--font-code)", fontSize: "0.68rem", color: "var(--text-3)", letterSpacing: "0.06em" }}>
            codeXplain — paste code, get answers
          </span>
        </div>

        <form action={formAction} style={{ padding: "24px 24px 20px" }}>

          {/* Language selector */}
          <div style={{ marginBottom: 18 }}>
            <label style={{
              display: "block", marginBottom: 8,
              fontFamily: "var(--font-code)", fontSize: "0.65rem",
              letterSpacing: "0.1em", color: "var(--text-3)",
            }}>
              LANGUAGE
            </label>
            <div style={{ position: "relative" }}>
              <select
                name="language"
                id="language"
                className="focus-ring"
                style={{
                  width: "100%", appearance: "none",
                  background: "var(--surface)", border: "1px solid var(--border-hi)",
                  borderRadius: "var(--radius)", color: "var(--text)",
                  fontFamily: "var(--font-code)", fontSize: "0.82rem",
                  padding: "10px 36px 10px 14px", cursor: "pointer",
                  transition: "border-color 0.2s, box-shadow 0.2s",
                }}
              >
                {LANGUAGES.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-3)", pointerEvents: "none" }}>
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </div>
          </div>

          {/* Code textarea */}
          <div style={{ marginBottom: 18 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
              <label htmlFor="code" style={{
                fontFamily: "var(--font-code)", fontSize: "0.65rem",
                letterSpacing: "0.1em", color: "var(--text-3)",
              }}>
                CODE
              </label>
              <span style={{ fontFamily: "var(--font-code)", fontSize: "0.62rem", color: "var(--text-3)" }}>
                max 20,000 chars
              </span>
            </div>
            <div style={{ position: "relative" }}>
              {/* Line number gutter */}
              <div style={{
                position: "absolute", left: 0, top: 0, bottom: 0, width: 40,
                background: "var(--surface)", borderRight: "1px solid var(--border)",
                borderRadius: "var(--radius) 0 0 var(--radius)",
                display: "flex", flexDirection: "column", alignItems: "center",
                paddingTop: 14, gap: 5.5, pointerEvents: "none", overflow: "hidden",
              }}>
                {Array.from({ length: 18 }).map((_, i) => (
                  <span key={i} style={{ fontFamily: "var(--font-code)", fontSize: "0.62rem", color: "var(--text-3)", opacity: 0.4, lineHeight: 1 }}>
                    {i + 1}
                  </span>
                ))}
              </div>
              <textarea
                id="code"
                name="code"
                required
                rows={14}
                placeholder={"// Paste your code here...\n// Select language above, then click Explain ↓"}
                className="focus-ring"
                style={{
                  width: "100%", background: "var(--surface)",
                  border: "1px solid var(--border-hi)", borderRadius: "var(--radius)",
                  color: "var(--text)", fontFamily: "var(--font-code)",
                  fontSize: "0.82rem", lineHeight: 1.75,
                  padding: "12px 14px 12px 54px",
                  resize: "vertical", minHeight: 240,
                  transition: "border-color 0.2s, box-shadow 0.2s",
                }}
              />
            </div>
          </div>

          {/* Submit row */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
            <p style={{ fontFamily: "var(--font-code)", fontSize: "0.68rem", color: "var(--text-3)" }}>
              Powered by <span style={{ color: "var(--accent)" }}>Groq</span> · llama-3.3-70b
            </p>
            <button
              type="submit"
              disabled={isPending}
              style={{
                display: "flex", alignItems: "center", gap: 8,
                fontFamily: "var(--font-ui)", fontWeight: 600, fontSize: "0.875rem",
                padding: "10px 24px", borderRadius: "var(--radius)", border: "none",
                cursor: isPending ? "not-allowed" : "pointer",
                transition: "all 0.2s",
                background: isPending ? "var(--raised)" : "linear-gradient(135deg, #1d4ed8 0%, var(--accent) 100%)",
                color: isPending ? "var(--text-3)" : "#000",
                boxShadow: isPending ? "none" : "0 0 24px rgba(59,130,246,0.35)",
                letterSpacing: "-0.01em",
              }}
            >
              {isPending ? (
                <>
                  <Spinner size={14} />
                  Explaining…
                </>
              ) : (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                  Explain Code
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Loading */}
      {isPending && (
        <div className="slide-up" style={{
          marginTop: 16, background: "var(--card)",
          border: "1px solid var(--border)", borderRadius: "var(--radius-lg)",
          padding: "18px 22px", display: "flex", alignItems: "center", gap: 14,
        }}>
          <Spinner size={18} />
          <div>
            <p style={{ fontFamily: "var(--font-ui)", fontWeight: 600, fontSize: "0.875rem", color: "var(--text)" }}>
              Analysing your code
            </p>
            <p style={{ fontFamily: "var(--font-code)", fontSize: "0.7rem", color: "var(--text-3)", marginTop: 3 }}>
              Groq inference typically completes in 1–3s
            </p>
          </div>
        </div>
      )}

      {/* Results */}
      {!isPending && formState?.success === true && (
        <CodeExplanation
          explanation={formState.data.explanation}
          language={formState.data.language}
          tokens={formState.data.tokens}
        />
      )}
      {!isPending && formState?.success === false && (
        <Error error={formState.error} />
      )}
    </div>
  );
};

export default CodeExplainForm;
