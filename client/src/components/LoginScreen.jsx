import React, { useState } from "react";
import { initSupabase } from "../utils/supabase";

export default function LoginScreen({ onLogin }) {
  const [code, setCode] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (code.length < 4) {
      setStatus("Please enter a valid 4-digit code.");
      return;
    }

    setLoading(true);
    setStatus("Verifying...");

    try {
      const supabase = await initSupabase();

      const { data, error } = await supabase
        .from("sessions")
        .select("*")
        .eq("id", code)
        .single();

      if (error || !data) {
        setStatus("Invalid code or session not started.");
      } else {
        onLogin(code, supabase);
      }
    } catch (e) {
      console.error(e);
      setStatus(e.message || "Connection failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100%",
        padding: "2rem",
        background: "radial-gradient(circle at top right, #1e1b4b, #0f172a)",
      }}
    >
      <div
        className="glass-panel fade-in"
        style={{
          padding: "2.5rem",
          borderRadius: "var(--radius-lg)",
          width: "100%",
          maxWidth: "400px",
          textAlign: "center",
          display: "flex",
          flexDirection: "column",
          gap: "1.5rem",
        }}
      >
        <div>
          <h1
            style={{
              fontSize: "2rem",
              marginBottom: "0.5rem",
              background: "linear-gradient(to right, #a78bfa, #38bdf8)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            AI Sync
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
            Enter the pairing code from your desktop
          </p>
        </div>

        <div style={{ position: "relative" }}>
          <input
            type="number"
            placeholder="0000"
            maxLength={4}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleLogin()}
            style={{
              width: "100%",
              padding: "1rem",
              fontSize: "1.5rem",
              textAlign: "center",
              letterSpacing: "0.5rem",
              borderRadius: "var(--radius-md)",
              border: "2px solid var(--surface-hover)",
              background: "var(--bg-color)",
              color: "var(--text-primary)",
              outline: "none",
              transition: "all 0.2s",
            }}
            onFocus={(e) =>
              (e.target.style.borderColor = "var(--primary-color)")
            }
            onBlur={(e) =>
              (e.target.style.borderColor = "var(--surface-hover)")
            }
          />
        </div>

        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            width: "100%",
            padding: "1rem",
            borderRadius: "var(--radius-md)",
            border: "none",
            background:
              "linear-gradient(135deg, var(--primary-color), var(--accent-color))",
            color: "white",
            fontWeight: "600",
            fontSize: "1rem",
            cursor: loading ? "wait" : "pointer",
            opacity: loading ? 0.7 : 1,
            transform: loading ? "scale(0.98)" : "scale(1)",
            transition: "all 0.2s",
            boxShadow: "0 4px 12px rgba(139, 92, 246, 0.3)",
          }}
        >
          {loading ? "Connecting..." : "Connect Device"}
        </button>

        {status && (
          <div
            className="fade-in"
            style={{
              color: status.includes("Verifying")
                ? "var(--accent-color)"
                : "var(--error-color)",
              fontSize: "0.9rem",
              marginTop: "0.5rem",
            }}
          >
            {status}
          </div>
        )}
      </div>
    </div>
  );
}
