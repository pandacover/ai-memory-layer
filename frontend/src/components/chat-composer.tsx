import { useState } from "react";
import type { FormEvent, KeyboardEvent } from "react";

type ChatComposerProps = {
  disabled?: boolean;
  onSubmit: (prompt: string) => void;
};

export function ChatComposer({ disabled = false, onSubmit }: ChatComposerProps) {
  const [prompt, setPrompt] = useState("");
  const canSubmit = Boolean(prompt.trim()) && !disabled;

  function submitPrompt(event?: FormEvent) {
    event?.preventDefault();
    const content = prompt.trim();
    if (!content || disabled) return;

    setPrompt("");
    onSubmit(content);
  }

  function handlePromptKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitPrompt();
    }
  }

  return (
    <form className="command-line" onSubmit={submitPrompt}>
      <label className="sr-only" htmlFor="oracle-prompt">
        Ask Oracle
      </label>
      <div className="composer">
        <textarea
          id="oracle-prompt"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          onKeyDown={handlePromptKeyDown}
          placeholder="Write the memory. Ask the oracle."
          rows={3}
          disabled={disabled}
        />
        <button type="submit" disabled={!canSubmit}>
          SEND
        </button>
      </div>
    </form>
  );
}
