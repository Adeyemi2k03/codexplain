"use server";

export type ExplainState = {
  success: true;
  data: {
    explanation: string;
    language: string;
    tokens: number | null;
  };
} | {
  success: false;
  error: string;
} | null;

export async function explain(
  prevState: ExplainState,
  formData: FormData
): Promise<ExplainState> {
  const code = formData.get("code") as string | null;
  const language = formData.get("language") as string | null;

  if (!code || code.trim().length === 0) {
    return { success: false, error: "Please paste some code before submitting." };
  }

  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

    // Step 1 — Submit the code
    const res = await fetch(`${baseUrl}/explanations/explain/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: code.trim(), language }),
    });

    const data = await res.json();

    if (!res.ok) {
      return { success: false, error: data?.error || `Server error (${res.status})` };
    }

    const taskId = data.task_id;

    // Step 2 — Poll for the result
    for (let i = 0; i < 30; i++) {
      await new Promise(r => setTimeout(r, 1000)); // wait 1 second

      const pollRes = await fetch(`${baseUrl}/explanations/${taskId}/`, {
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      });

      const pollData = await pollRes.json();

      if (pollData.status === "COMPLETED") {
        return {
          success: true,
          data: {
            explanation: pollData.explanation,
            language: pollData.language,
            tokens: pollData.tokens_used,
          },
        };
      }

      if (pollData.status === "FAILED") {
        return { success: false, error: pollData.error_message || "Explanation failed." };
      }
    }

    return { success: false, error: "Request timed out. Please try again." };

  } catch (err) {
    const error = err as Error;
    return {
      success: false,
      error: error?.name === "TypeError"
        ? "Could not reach the server. Is it running?"
        : `Unexpected error: ${error?.message}`,
    };
  }
}