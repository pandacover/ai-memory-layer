function getStreamText(event: unknown): string {
  if (!event || typeof event !== "object") return "";

  const value = event as Record<string, unknown>;

  if (typeof value.content === "string") return value.content;
  if (typeof value.text === "string") return value.text;
  if (typeof value.token === "string") return value.token;

  const messages = value.messages;
  if (Array.isArray(messages)) {
    const last = messages.at(-1) as Record<string, unknown> | undefined;
    if (typeof last?.content === "string") return last.content;
  }

  const chunk = value.chunk as Record<string, unknown> | undefined;
  if (typeof chunk?.content === "string") return chunk.content;

  const data = value.data as Record<string, unknown> | undefined;
  if (typeof data?.content === "string") return data.content;
  if (typeof data?.text === "string") return data.text;

  return "";
}

export function parseStreamLine(line: string): string {
  const trimmed = line.trim();
  if (!trimmed || trimmed === "data: [DONE]" || trimmed === "[DONE]") return "";

  const payload = trimmed.startsWith("data:")
    ? trimmed.slice(5).trim()
    : trimmed;

  try {
    const parsed = JSON.parse(payload);
    return getStreamText(parsed);
  } catch {
    return payload;
  }
}
