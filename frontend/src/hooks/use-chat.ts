import { useState } from "react";

import { streamChat } from "../api/chat";
import type { ChatMessage, ChatRequestMessage } from "../types/chat";

function createMessage(content: string): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role: "human",
    content,
  };
}

function toRequestMessages(messages: ChatMessage[]): ChatRequestMessage[] {
  return messages
    .filter((message) => message.role !== "system")
    .map(({ id, role, content }) => ({ id, role, content }));
}

function appendToMessage(
  messages: ChatMessage[],
  messageId: string,
  content: string,
): ChatMessage[] {
  return messages.map((message) =>
    message.id === messageId
      ? { ...message, content: message.content + content }
      : message,
  );
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  async function sendMessage(content: string) {
    const trimmedContent = content.trim();
    if (!trimmedContent || isSending) return;

    const userMessage = createMessage(trimmedContent);
    const assistantId = crypto.randomUUID();
    const nextMessages: ChatMessage[] = [
      ...messages,
      userMessage,
      { id: assistantId, role: "ai", content: "", isStreaming: true },
    ];

    setError("");
    setIsSending(true);
    setMessages(nextMessages);

    try {
      await streamChat({
        messages: toRequestMessages([...messages, userMessage]),
        onToken: (token) => {
          setMessages((current) => appendToMessage(current, assistantId, token));
        },
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong.";
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

  return {
    error,
    isSending,
    messages,
    sendMessage,
  };
}
