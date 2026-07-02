"use server";

interface ExplainSuccess {
  success: true;
  data: {
    explanation: string;
    language: string;
    tokens: number | null;
  };
}

interface ExplainError {
  success: false;
  error: string;
}

export type ExplainState = ExplainSuccess | ExplainError | null;

export async function explain(
  prevState: ExplainState,
  formData: FormData
): Promise<ExplainState> {
  const code = formData.get("code") as string | null;
  const language = formData.get("language") as string | null;

  if (!code || code.trim().length === 0) {
    return { success: false, error: "Please paste some code before submitting." };
  }

  console.log(`[action] Generating explanation for: ${language}`);

  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:3002/api";

    const res = await fetch(`${baseUrl}/explain-code`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: code.trim(), language }),
    });

    const data = await res.json();

    if (!res.ok) {
      return { success: false, error: data?.error || `Server error (${res.status})` };
    }

    return { success: true, data };
  } catch (err) {
    const error = err as Error;
    console.error("[action] fetch error:", error);
    return {
      success: false,
      error:
        error?.name === "TypeError"
          ? "Could not reach the server. Is it running?"
          : `Unexpected error: ${error?.message}`,
    };
  }
}
