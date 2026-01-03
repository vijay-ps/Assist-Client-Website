let supabase = null;
let currentCode = null;

const loginScreen = document.getElementById("login-screen");
const chatScreen = document.getElementById("chat-screen");
const statusMsg = document.getElementById("status-msg");
const connectionIndicator = document.getElementById("connection-status");
const messagesContainer = document.getElementById("messages");
const pairingInput = document.getElementById("pairing-code");

// Initialize Supabase
async function init() {
  try {
    // Try fetching from Vercel Serverless Function first
    const response = await fetch("/api/config");
    if (response.ok) {
      const config = await response.json();
      if (config.url && config.key) {
        supabase = window.supabase.createClient(config.url, config.key);
        console.log("Supabase initialized via Vercel Env Vars");
        return;
      }
    }
  } catch (e) {
    console.log(
      "Not running on Vercel or API failed, checking local config.js..."
    );
  }

  // Fallback to local config.js
  if (
    typeof SUPABASE_CONFIG !== "undefined" &&
    SUPABASE_CONFIG.url &&
    SUPABASE_CONFIG.key
  ) {
    if (!SUPABASE_CONFIG.url.includes("YOUR_SUPABASE")) {
      supabase = window.supabase.createClient(
        SUPABASE_CONFIG.url,
        SUPABASE_CONFIG.key
      );
      console.log("Supabase initialized via local config.js");
    } else {
      showError("Please configure Supabase credentials");
    }
  } else {
    showError("Missing Supabase Configuration");
  }
}

init();

// Allow Enter key to submit
pairingInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    attemptLogin();
  }
});

async function attemptLogin() {
  if (!supabase) {
    showError("Supabase not initialized. Check config.js");
    return;
  }

  const code = pairingInput.value;
  if (code.length < 4) {
    showError("Please enter a valid 4-digit code.");
    return;
  }

  statusMsg.textContent = "Verifying...";
  statusMsg.style.color = "#bb86fc";

  // Check if session exists
  const { data, error } = await supabase
    .from("sessions")
    .select("*")
    .eq("id", code)
    .single();

  if (error || !data) {
    showError("Invalid code or session not started.");
    return;
  }

  currentCode = code;
  showChatScreen();
  startRealtimeSubscription();
}

function showError(msg) {
  statusMsg.textContent = msg;
  statusMsg.style.color = "#cf6679";
}

function showChatScreen() {
  loginScreen.style.display = "none";
  chatScreen.style.display = "flex";
}

function startRealtimeSubscription() {
  connectionIndicator.classList.add("connected");

  const channel = supabase
    .channel("schema-db-changes")
    .on(
      "postgres_changes",
      {
        event: "UPDATE",
        schema: "public",
        table: "sessions",
        filter: `id=eq.${currentCode}`,
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
        connectionIndicator.classList.add("connected");
        connectionIndicator.classList.remove("disconnected");
      } else if (status === "CLOSED" || status === "CHANNEL_ERROR") {
        connectionIndicator.classList.remove("connected");
        connectionIndicator.classList.add("disconnected");
      }
    });
}

function addMessage(text, timestamp) {
  // Remove the "Waiting..." placeholder if it exists
  if (
    messagesContainer.children.length > 0 &&
    messagesContainer.children[0].style.fontStyle === "italic"
  ) {
    messagesContainer.innerHTML = "";
  }

  const msgDiv = document.createElement("div");
  msgDiv.className = "message";

  const timeSpan = document.createElement("span");
  timeSpan.className = "timestamp";
  timeSpan.textContent = timestamp || new Date().toLocaleTimeString();

  const contentDiv = document.createElement("div");
  contentDiv.textContent = text;

  msgDiv.appendChild(timeSpan);
  msgDiv.appendChild(contentDiv);

  messagesContainer.appendChild(msgDiv);

  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  // Vibrate device for feedback (if supported)
  if (navigator.vibrate) {
    navigator.vibrate(50);
  }
}
