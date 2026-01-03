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
    <div id="login-screen">
      <h1>AI Assistant Sync</h1>
      <p style={{ color: "var(--secondary-text)", marginBottom: "20px" }}>
        Enter the code from your computer
      </p>
      <input
        type="number"
        placeholder="0000"
        maxLength={4}
        value={code}
        onChange={(e) => setCode(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleLogin()}
      />
      <button onClick={handleLogin} disabled={loading}>
        {loading ? "Connecting..." : "Connect"}
      </button>
      <div
        className="status-msg"
        style={{ color: status.includes("Verifying") ? "#bb86fc" : "#cf6679" }}
      >
        {status}
      </div>
    </div>
  );
}
