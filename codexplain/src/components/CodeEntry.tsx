import Header from "./Header.tsx";
import CodeExplainForm from "./forms/CodeExplainForm.tsx";

const CodeEntry = () => {
  return (
    <div style={{
      position: "relative", minHeight: "100dvh",
      display: "flex", flexDirection: "column",
      alignItems: "center", padding: "40px 16px 60px", zIndex: 1,
    }}>
      {/* Ambient glow */}
      <div style={{
        position: "fixed", top: "5%", left: "50%", transform: "translateX(-50%)",
        width: 600, height: 300, borderRadius: "50%",
        background: "radial-gradient(ellipse, rgba(59,130,246,0.06) 0%, transparent 70%)",
        pointerEvents: "none", zIndex: 0,
      }} />

      <Header />

      {/* Hero */}
      <div className="slide-up delay-1" style={{ textAlign: "center", marginBottom: 40, maxWidth: 600 }}>
        <h1 style={{
          fontFamily: "var(--font-ui)", fontWeight: 800,
          fontSize: "clamp(2rem, 5vw, 3.2rem)",
          letterSpacing: "-0.04em", lineHeight: 1.1, marginBottom: 14,
        }}>
          Understand any code,{" "}
          <span style={{ color: "var(--accent)" }}>instantly</span>
        </h1>

        <p style={{
          fontFamily: "var(--font-ui)", fontWeight: 400,
          fontSize: "clamp(0.9rem, 2vw, 1.05rem)",
          color: "var(--text-2)", lineHeight: 1.6, marginBottom: 28,
        }}>
          Paste a snippet, pick a language, and get a structured AI explanation — overview, breakdown, and key concepts.
        </p>
      </div>

      <CodeExplainForm />

      <footer className="slide-up delay-4" style={{
        marginTop: 48, fontFamily: "var(--font-code)", fontSize: "0.65rem",
        color: "var(--text-3)", letterSpacing: "0.05em", textAlign: "center", lineHeight: 1.8,
      }}>
        <span style={{ opacity: 0.9 }}>Open source · No data stored</span>
      </footer>
    </div>
  );
};

export default CodeEntry;