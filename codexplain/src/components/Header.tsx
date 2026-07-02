import { useEffect, useState } from "react";

type ApiStatus = "loading" | "online" | "offline";
type Theme = "dark" | "light";

const MoonIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
  </svg>
);

const SunIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="5"/>
    <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
    <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
  </svg>
);

const Header = () => {
  const [apiStatus, setApiStatus] = useState<ApiStatus>("loading");
  const [model, setModel] = useState<string | null>(null);
  const [theme, setTheme] = useState<Theme>(() => {
    return (localStorage.getItem("theme") as Theme) ?? "dark";
  });

  // Apply theme class to <html> on mount and on change
  useEffect(() => {
    const root = document.documentElement;
    if (theme === "light") {
      root.classList.add("light");
    } else {
      root.classList.remove("light");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => t === "dark" ? "light" : "dark");

  useEffect(() => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:3002/api";
    fetch(`${baseUrl.replace("/api", "")}/api/health`)
      .then(r => r.json())
      .then((d: { status: string; hasApiKey: boolean; model?: string }) => {
        setApiStatus(d.status === "healthy" && d.hasApiKey ? "online" : "offline");
        setModel(d.model ?? null);
      })
      .catch(() => setApiStatus("offline"));
  }, []);

  return (
    <header
      className="slide-up w-full max-w-4xl mb-12 flex items-center justify-between"
      style={{ position: "relative", zIndex: 10 }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div style={{
          width: 38, height: 38,
          borderRadius: "var(--radius)",
          background: "linear-gradient(135deg, #1d4ed8 0%, var(--accent) 100%)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "1rem", fontWeight: 700,
          fontFamily: "var(--font-code)",
          color: "#fff", flexShrink: 0,
          boxShadow: "0 0 24px rgba(59,130,246,0.35)",
        }}>
          {"<>"}
        </div>
        <div>
          <div style={{ fontFamily: "var(--font-ui)", fontWeight: 800, fontSize: "1.1rem", letterSpacing: "-0.025em", lineHeight: 1 }}>
            Code<span style={{ color: "var(--accent)" }}>Xplain</span>
          </div>
          <div style={{ fontFamily: "var(--font-code)", fontSize: "0.65rem", color: "var(--text-3)", marginTop: 2, letterSpacing: "0.05em" }}>
            AI CODE EXPLAINER
          </div>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {model && (
          <div
            className="sm:block"
            style={{
              fontFamily: "var(--font-code)", fontSize: "0.7rem", color: "var(--text-3)",
              background: "var(--surface)", border: "1px solid var(--border)",
              borderRadius: "var(--radius-sm)", padding: "4px 10px", display: "none",
            }}
          >
            {model}
          </div>
        )}

        {/* Theme toggle */}
        <button onClick={toggleTheme} className="theme-toggle" title="Toggle theme">
          {theme === "dark" ? <SunIcon /> : <MoonIcon />}
          {theme === "dark" ? "LIGHT" : "DARK"}
        </button>

        {/* API status */}
        <div style={{
          display: "flex", alignItems: "center", gap: 6,
          fontFamily: "var(--font-code)", fontSize: "0.7rem",
          padding: "5px 12px", borderRadius: "var(--radius-sm)",
          border: "1px solid var(--border)",
          background: apiStatus === "online" ? "var(--green-lo)" : apiStatus === "offline" ? "var(--red-lo)" : "var(--surface)",
          color: apiStatus === "online" ? "var(--green)" : apiStatus === "offline" ? "var(--red)" : "var(--text-3)",
          letterSpacing: "0.08em",
        }}>
          <span className={`status-dot ${apiStatus}`} />
          {apiStatus === "loading" ? "CONNECTING" : apiStatus === "online" ? "API LIVE" : "API DOWN"}
        </div>
      </div>
    </header>
  );
};

export default Header;
