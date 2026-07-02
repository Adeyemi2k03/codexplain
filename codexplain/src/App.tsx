import { ErrorBoundary, type FallbackProps } from "react-error-boundary";
import CodeEntry from "./components/CodeEntry.tsx";

const Fallback = ({ error, resetErrorBoundary }: FallbackProps) => (
  <div style={{
    minHeight: "100vh", display: "flex", flexDirection: "column",
    alignItems: "center", justifyContent: "center",
    background: "var(--bg)", color: "var(--text)",
    fontFamily: "var(--font-code)", padding: 24, textAlign: "center",
  }}>
    <p style={{ fontSize: "2rem", marginBottom: 12 }}>💥</p>
    <p style={{ fontWeight: 700, fontSize: "1rem", marginBottom: 6 }}>Something went wrong</p>
    <p style={{ color: "var(--text-3)", fontSize: "0.78rem", marginBottom: 20, maxWidth: 360 }}>
      {(error as Error)?.message}
    </p>
    <button
      onClick={resetErrorBoundary}
      style={{
        background: "var(--surface)", border: "1px solid var(--border-hi)",
        color: "var(--text)", borderRadius: "var(--radius)", padding: "8px 20px",
        cursor: "pointer", fontFamily: "var(--font-code)", fontSize: "0.78rem",
      }}
    >
      Try again
    </button>
  </div>
);

function App() {
  return (
    <ErrorBoundary FallbackComponent={Fallback}>
      <CodeEntry />
    </ErrorBoundary>
  );
}

export default App;
