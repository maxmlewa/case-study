import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { getAIMessage } from "../api/api";
import { marked } from "marked";

function ProductCard({ card, onAction }) {
  return (
    <div
      className="product-card"
      style={{
        display: "flex",
        gap: 12,
        padding: 12,
        border: "1px solid #e5e7eb",
        borderRadius: 12,
        marginTop: 8,
        background: "white",
      }}
    >
      <img
        src={card.image_url || "/parts/placeholder.png"}
        alt={card.title}
        onError={(e) => { e.currentTarget.src = "/parts/placeholder.png"; }}
        style={{ width: 72, height: 72, objectFit: "cover", borderRadius: 10 }}
      />
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600 }}>{card.title}</div>
        <div style={{ fontSize: 12, opacity: 0.8 }}>Part: {card.part_number}</div>
        <div style={{ marginTop: 6 }}>
          <span style={{ fontWeight: 600 }}>${Number(card.price).toFixed(2)}</span>
          <span style={{ marginLeft: 10, fontSize: 12, opacity: 0.8 }}>
            {card.availability}
          </span>
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
          {Array.isArray(card.actions) &&
            card.actions.map((a, idx) => (
              <button
                key={idx}
                onClick={() => onAction(a)}
                style={{
                  padding: "6px 10px",
                  borderRadius: 10,
                  border: "1px solid #d1d5db",
                  background: "#f9fafb",
                  cursor: "pointer",
                }}
              >
                {a.label}
              </button>
            ))}
          {card.url && (
            <a
              href={card.url}
              target="_blank"
              rel="noreferrer"
              style={{ alignSelf: "center", fontSize: 12 }}
            >
              View on PartSelect
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

function ChatWindow() {
  const defaultMessage = [
    {
      role: "assistant",
      content: "Hi, how can I help you today?",
    },
  ];

  const [messages, setMessages] = useState(defaultMessage);
  const [input, setInput] = useState("");

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text) => {
    if (typeof text !== "string") return;
    if (text.trim() === "") return;

    // user bubble
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");

    // backend call returns { message, cards }
    const { message, cards } = await getAIMessage(text);

    // attach cards to assistant message
    setMessages((prev) => [...prev, { ...message, cards }]);
  };

  return (
    <div className="messages-container">
      {messages.map((message, index) => (
        <div key={index} className={`${message.role}-message-container`}>
          {message.content && (
            <div className={`message ${message.role}-message`}>
              <div
                dangerouslySetInnerHTML={{
                  __html: marked(message.content).replace(/<p>|<\/p>/g, ""),
                }}
              ></div>
            </div>
          )}

          {/* ADDING CARDS */}
          {Array.isArray(message.cards) &&
            message.cards.map((card, cIdx) =>
              card.type === "product" ? (
                <ProductCard
                  key={cIdx}
                  card={card}
                  onAction={(action) => {
                    const pn = action?.payload?.part_number;
                    if (action.action === "INSTALL" && pn) handleSend(`INSTALL ${pn}`);
                    else if (action.action === "COMPATIBILITY" && pn)
                      handleSend(`COMPATIBILITY ${pn}`);
                    else handleSend(`${action.action} ${pn || ""}`.trim());
                  }}
                />
              ) : null
            )}
        </div>
      ))}

      <div ref={messagesEndRef} />

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          onKeyPress={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              handleSend(input);
              e.preventDefault();
            }
          }}
          rows="3"
        />
        {/* Fix button: pass input, not click event */}
        <button className="send-button" onClick={() => handleSend(input)}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;
