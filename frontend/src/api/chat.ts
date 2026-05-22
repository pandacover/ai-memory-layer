import { CHAT_API_URL } from "../config";
import type { ChatRequestMessage } from "../types/chat";
import { parseStreamLine } from "../utils/stream";

type StreamChatOptions = {
  messages: ChatRequestMessage[];
  onToken: (token: string) => void;
};

export async function streamChat({ messages, onToken }: StreamChatOptions) {
  const response = await fetch(CHAT_API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  if (!response.body) {
    throw new Error("The browser could not read the stream.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const text = parseStreamLine(line);
      if (text) onToken(text);
    }
  }

  const finalText = parseStreamLine(buffer);
  if (finalText) onToken(finalText);
}
