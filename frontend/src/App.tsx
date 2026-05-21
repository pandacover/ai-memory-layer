import { useEffect, useRef, useState } from "react";
import type { FormEvent, KeyboardEvent } from "react";
import "./App.css";

type Role = "human" | "ai" | "system";

type ChatMessage = {
  id: string;
  role: Role;
  content: string;
  isStreaming?: boolean;
};

const API_URL =
  import.meta.env.VITE_CHAT_API_URL ?? "http://localhost:8000/chat/stream";

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

function parseStreamLine(line: string): string {
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

function getRoleLabel(role: Role) {
  if (role === "human") return "YOU";
  if (role === "system") return "OMEN";
  return "ORACLE";
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [prompt, setPrompt] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSubmit(event?: FormEvent) {
    event?.preventDefault();

    const content = prompt.trim();
    if (!content || isSending) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "human",
      content,
    };
    const assistantId = crypto.randomUUID();

    setPrompt("");
    setError("");
    setIsSending(true);
    setMessages((current) => [
      ...current,
      userMessage,
      { id: assistantId, role: "ai", content: "", isStreaming: true },
    ]);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, userMessage]
            .filter((message) => message.role !== "system")
            .map(({ role, content, id }) => ({ id, role, content })),
        }),
      });

      if (!response.ok)
        throw new Error(`Request failed with status ${response.status}`);
      if (!response.body)
        throw new Error("The browser could not read the stream.");

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
          if (!text) continue;

          setMessages((current) =>
            current.map((message) =>
              message.id === assistantId
                ? { ...message, content: message.content + text }
                : message,
            ),
          );
        }
      }

      const finalText = parseStreamLine(buffer);
      if (finalText) {
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantId
              ? { ...message, content: message.content + finalText }
              : message,
          ),
        );
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong.";
      setError(message);
      setMessages((current) =>
        current.map((chatMessage) =>
          chatMessage.id === assistantId
            ? {
                ...chatMessage,
                content: "No signal from the backend shrine.",
                role: "system",
              }
            : chatMessage,
        ),
      );
    } finally {
      setIsSending(false);
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantId
            ? { ...message, isStreaming: false }
            : message,
        ),
      );
    }
  }

  function handlePromptKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSubmit();
    }
  }

  return (
    <main className="oracle-shell">
      <div className="myth-backdrop" aria-hidden="true" />

      <section className="oracle-frame" aria-label="Mnemosyne chat interface">
        <div className="floating-mark" aria-hidden="true">
          <span>ΜΝ</span>
          <b>Oracle</b>
          <em>{isSending ? "receiving" : "awake"}</em>
        </div>

        <section
          className="conversation"
          aria-live="polite"
          aria-label="Chat messages"
        >
          {messages.length === 0 && (
            <div className="empty-inscription" aria-hidden="true">
              <span>ΜΝΗΜΗ WAITS</span>
              <p>Write something worth remembering.</p>
            </div>
          )}
          {messages.map((message, index) => (
            <article key={message.id} className={`line ${message.role}`}>
              <div className="line-meta">
                <span>{String(index + 1).padStart(2, "0")}</span>
                <b>{getRoleLabel(message.role)}</b>
              </div>
              <div className="line-body">
                {message.content || (
                  <span className="typing">smoke gathering</span>
                )}
                {message.isStreaming && <span className="cursor" />}
              </div>
            </article>
          ))}
          <div ref={messagesEndRef} />
        </section>

        {error && <p className="error">OMEN / {error}</p>}

        <form className="command-line" onSubmit={handleSubmit}>
          <label className="sr-only" htmlFor="oracle-prompt">Ask Oracle</label>
          <div className="composer">
            <textarea
              id="oracle-prompt"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              onKeyDown={handlePromptKeyDown}
              placeholder="Write the memory. Ask the oracle."
              rows={3}
              disabled={isSending}
            />
            <button type="submit" disabled={!prompt.trim() || isSending}>
              SEND
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

export default App;
