interface ErrorProps {
  error: string | null | undefined;
}

const Error = ({ error }: ErrorProps) => {
  if (!error) return null;
  return (
    <div
      className="slide-up flex items-start gap-3 mt-5 p-4 rounded-lg text-sm"
      style={{
        background: "var(--red-lo)",
        border: "1px solid rgba(248,113,113,0.25)",
        color: "var(--red)",
        fontFamily: "var(--font-code)",
        fontSize: "0.8rem",
        lineHeight: 1.6,
      }}
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0, marginTop: 1 }}>
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <span>{error}</span>
    </div>
  );
};

export default Error;
