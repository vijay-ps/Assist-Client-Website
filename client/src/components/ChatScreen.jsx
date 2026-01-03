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
          console.log("Change received!", payload);
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
      { text, timestamp: timestamp || new Date().toLocaleTimeString() },
    ]);
    if (navigator.vibrate) navigator.vibrate(50);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div id="chat-screen" style={{ display: "flex" }}>
      <div id="header">
        <span style={{ fontWeight: "bold" }}>Live Feed</span>
        <div
          id="connection-status"
          title={connected ? "Connected" : "Disconnected"}
          className={connected ? "connected" : "disconnected"}
        />
      </div>
      <div id="messages">
        {messages.length === 0 ? (
          <div
            style={{
              textAlign: "center",
              color: "var(--secondary-text)",
              marginTop: "50px",
              fontStyle: "italic",
            }}
          >
            Waiting for AI responses...
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className="message">
              <span className="timestamp">{msg.timestamp}</span>
              <div>{msg.text}</div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
