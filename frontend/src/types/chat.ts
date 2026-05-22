export type ChatRole = "human" | "ai" | "system";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  isStreaming?: boolean;
};

export type ChatRequestMessage = Pick<ChatMessage, "id" | "role" | "content">;
