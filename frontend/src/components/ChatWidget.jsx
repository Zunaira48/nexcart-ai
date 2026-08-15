import { useState } from "react";
import api from "../services/api";
import "./ChatWidget.css";

function ChatWidget() {
  const isLocal = window.location.hostname === "localhost";
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [history, setHistory] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  if (!isLocal) return null; // sirf localhost pe dikhega, live site pe nahi

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages((m) => [...m, { role: "user", content: userMsg }]);
    setInput("");
    setLoading(true);
    try {
      const { data } = await api.post("/chat/assistant", { message: userMsg, history });
      setHistory(data.history);
      setMessages((m) => [...m, { role: "assistant", content: data.reply }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Assistant abhi available nahi hai." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-widget">
      {open ? (
        <div className="chat-panel">
          <div className="chat-header">
            🤖 Shopping Assistant
            <button onClick={() => setOpen(false)}>✕</button>
          </div>
          <div className="chat-messages">
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg chat-msg-${m.role}`}>
                {m.content}
              </div>
            ))}
            {loading && <div className="chat-msg chat-msg-assistant">Soch rahi hoon...</div>}
          </div>
          <div className="chat-input-row">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Kuch pooch lo..."
            />
            <button onClick={sendMessage}>➤</button>
          </div>
        </div>
      ) : (
        <button className="chat-fab" onClick={() => setOpen(true)}>
          💬
        </button>
      )}
    </div>
  );
}

export default ChatWidget;