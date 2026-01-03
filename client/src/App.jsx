import React, { useState } from "react";
import LoginScreen from "./components/LoginScreen";
import ChatScreen from "./components/ChatScreen";

function App() {
  const [supabase, setSupabase] = useState(null);
  const [pairingCode, setPairingCode] = useState(null);

  const handleLogin = (code, supabaseClient) => {
    setPairingCode(code);
    setSupabase(supabaseClient);
  };

  return (
    <>
      {!supabase ? (
        <LoginScreen onLogin={handleLogin} />
      ) : (
        <ChatScreen supabase={supabase} pairingCode={pairingCode} />
      )}
    </>
  );
}

export default App;
