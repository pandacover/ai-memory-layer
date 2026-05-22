import { useEffect, useRef } from "react";

import type { ChatMessage } from "../types/chat";

type ConversationProps = {
  messages: ChatMessage[];
};

function getRoleLabel(role: ChatMessage["role"]) {
  if (role === "ai") return "Oracle";
  if (role === "system") return "Omen";
  return "Seeker";
}

export function Conversation({ messages }: ConversationProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  return (
    <div className="conversation" aria-live="polite">
      {messages.length === 0 && <EmptyConversation />}

      {messages.map((message) => (
        <MessageLine key={message.id} message={message} />
      ))}

      <div ref={endRef} />
    </div>
  );
}

function EmptyConversation() {
  return (
    <div className="empty-inscription">
      <span>NO MEMORY THREAD</span>
      <p>Invoke a memory, ask a question, or confess a signal.</p>
    </div>
  );
}

type MessageLineProps = {
  message: ChatMessage;
};

function MessageLine({ message }: MessageLineProps) {
  return (
    <article className={`line ${message.role}`}>
      <header className="line-meta">
        <span>{message.role.toUpperCase()}</span>
        <b>{getRoleLabel(message.role)}</b>
        {message.isStreaming && <em>receiving</em>}
      </header>
      <div className="line-body">
        {message.content ? (
          message.content
        ) : (
          <span className="typing">waiting for signal</span>
        )}
        {message.isStreaming && <span className="cursor" aria-hidden="true" />}
      </div>
    </article>
  );
}
