import "./app.css";

import { BrandMark } from "./components/brand-mark";
import { ChatComposer } from "./components/chat-composer";
import { Conversation } from "./components/conversation";
import { useChat } from "./hooks/use-chat";

function App() {
  const { error, isSending, messages, sendMessage } = useChat();

  return (
    <main className="oracle-shell">
      <div className="myth-backdrop" aria-hidden="true" />

      <section className="oracle-frame" aria-label="Mnemosyne chat interface">
        <BrandMark status={isSending ? "receiving" : "awake"} />
        <Conversation messages={messages} />

        {error && <p className="error">OMEN / {error}</p>}
        <ChatComposer disabled={isSending} onSubmit={sendMessage} />
      </section>
    </main>
  );
}

export default App;
