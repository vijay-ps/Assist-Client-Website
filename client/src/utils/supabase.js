import { createClient } from "@supabase/supabase-js";

let supabase = null;

export const initSupabase = async () => {
  if (supabase) return supabase;

  let url = import.meta.env.VITE_SUPABASE_URL;
  let key = import.meta.env.VITE_SUPABASE_KEY;

  // Try fetching from Vercel API if env vars are missing (e.g. not built with them)
  if (!url || !key) {
    try {
      const res = await fetch("/api/config");
      if (res.ok) {
        const config = await res.json();
        url = config.url;
        key = config.key;
      }
    } catch (e) {
      console.warn("Failed to fetch config from API", e);
    }
  }

  // Fallback to manual config if still missing (could be local dev without env)
  if (!url || !key) {
    // Check for a global config object if user added one manually
    if (window.SUPABASE_CONFIG) {
      url = window.SUPABASE_CONFIG.url;
      key = window.SUPABASE_CONFIG.key;
    }
  }

  if (url && key) {
    supabase = createClient(url, key);
    return supabase;
  }

  throw new Error("Missing Supabase Credentials");
};

export const getSupabase = () => supabase;
