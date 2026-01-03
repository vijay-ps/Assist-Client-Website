import React, { useEffect, useState, useRef } from "react";

export default function ChatScreen({ supabase, pairingCode }) {
  const [messages, setMessages] = useState([]);
  const [connected, setConnected] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const channel = supabase
      .channel("schema-db-changes")
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "sessions",
          filter: `id=eq.${pairingCode}`,
        },
        (payload) => {
          if (payload.new && payload.new.response) {
            addMessage(payload.new.response, payload.new.timestamp);
          }
        }
      )
      .subscribe((status) => {
        if (status === "SUBSCRIBED") {
          setConnected(true);
        } else if (status === "CLOSED" || status === "CHANNEL_ERROR") {
          setConnected(false);
        }
      });

    return () => {
      supabase.removeChannel(channel);
    };
  }, [supabase, pairingCode]);

  const addMessage = (text, timestamp) => {
    setMessages((prev) => [
      ...prev,
      {
        text,
        timestamp:
          timestamp ||
          new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
      },
    ]);
    if (navigator.vibrate) navigator.vibrate(50);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        background: "var(--bg-color)",
      }}
    >
      {/* Header */}
      <div
        className="glass-panel"
        style={{
          padding: "1rem 1.5rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          zIndex: 10,
          borderRadius: 0,
          borderBottom: "1px solid rgba(255,255,255,0.05)",
          borderTop: "none",
          borderLeft: "none",
          borderRight: "none",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div
            style={{
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              background: connected
                ? "var(--success-color)"
                : "var(--error-color)",
              boxShadow: connected ? "0 0 10px var(--success-color)" : "none",
              transition: "all 0.3s",
            }}
          />
          <span style={{ fontWeight: "600", fontSize: "1.1rem" }}>
            Live Feed
          </span>
        </div>
        <div
          style={{
            fontSize: "0.8rem",
            color: "var(--text-secondary)",
            background: "var(--surface-color)",
            padding: "0.25rem 0.75rem",
            borderRadius: "var(--radius-full)",
          }}
        >
          #{pairingCode}
        </div>
      </div>

      {/* Messages Area */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "1.5rem",
          display: "flex",
          flexDirection: "column",
          gap: "1.5rem",
          scrollBehavior: "smooth",
        }}
      >
        {messages.length === 0 ? (
          <div
            className="fade-in"
            style={{
              textAlign: "center",
              color: "var(--text-secondary)",
              marginTop: "auto",
              marginBottom: "auto",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "1rem",
              opacity: 0.7,
            }}
          >
            <div
              style={{
                fontSize: "3rem",
                animation: "pulse 2s infinite",
              }}
            >
              📡
            </div>
            <p>Waiting for AI responses...</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className="fade-in"
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
                maxWidth: "90%",
                alignSelf: "flex-start",
                animationDelay: `${idx * 0.05}s`,
              }}
            >
              <div
                style={{
                  background: "var(--surface-color)",
                  padding: "1rem 1.25rem",
                  borderRadius:
                    "0 var(--radius-lg) var(--radius-lg) var(--radius-lg)",
                  boxShadow: "var(--shadow-sm)",
                  lineHeight: "1.6",
                  color: "var(--text-primary)",
                  border: "1px solid rgba(255,255,255,0.05)",
                  position: "relative",
                }}
              >
                {msg.text}
              </div>
              <span
                style={{
                  fontSize: "0.75rem",
                  color: "var(--text-secondary)",
                  marginTop: "0.4rem",
                  marginLeft: "0.5rem",
                }}
              >
                {msg.timestamp}
              </span>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
