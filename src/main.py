import time
import json
import keyboard
import threading
import random
import logging
import sys
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Ensure we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio.audio_stream import AudioStream
from asr.whisper_asr import WhisperASR
from memory.context_manager import ContextBuffer
from llm.gemini_client import ask_gemini

# Supabase Client
from supabase import create_client, Client

# Configuration
WINDOW_SECONDS = 60

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Main")

running = True
website_mode = False
supabase: Client = None
pairing_code = None

def init_supabase():
    url = os.environ.get("VITE_SUPABASE_URL")
    key = os.environ.get("VITE_SUPABASE_KEY")
    if not url or not key:
        logger.error("Supabase credentials missing in .env")
        print("\n[ERROR] Supabase credentials missing in .env file!")
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to init Supabase: {e}")
        return None

def transcription_worker(audio_stream, asr, context_buffer):
    import numpy as np
    buffer = []
    buffer_duration = 0.0
    
    logger.info("Transcription worker started.")
    
    while running:
        try:
            chunk = audio_stream.get_chunk()
            if chunk is not None:
                # Calculate RMS to check for silence
                rms = np.sqrt(np.mean(chunk**2))
                
                buffer.append(chunk)
                buffer_duration += len(chunk) / audio_stream.target_rate
                
                # Process when we have ~1 second of audio
                if buffer_duration >= 1.0:
                    full_audio = np.concatenate(buffer)
                    texts = asr.transcribe(full_audio)
                    for text in texts:
                        print(f"📝 Transcribed: {text}")
                        context_buffer.add_segment(text)
                    
                    # Reset buffer
                    buffer = []
                    buffer_duration = 0.0
            else:
                time.sleep(0.01)
        except Exception as e:
            logger.error(f"Error in transcription worker: {e}")
            time.sleep(1)

def main():
    global running, website_mode, supabase, pairing_code
    
    print("\n" + "="*50)
    print(" AI MEETING ASSISTANT ".center(50, "="))
    print("="*50 + "\n")

    print("Select Mode:")
    print("1. Normal Mode (Console Output)")
    print("2. Website Mode (Supabase Realtime)")
    
    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == '1':
            website_mode = False
            break
        elif choice == '2':
            website_mode = True
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    if website_mode:
        supabase = init_supabase()
        if not supabase:
            print("Falling back to Normal Mode due to Supabase error.")
            website_mode = False
        else:
            # Generate Pairing Code
            pairing_code = str(random.randint(1000, 9999))
            
            # Create session in DB
            try:
                # Upsert session
                data = {
                    "id": pairing_code,
                    "response": "Waiting for AI...",
                    "timestamp": time.strftime("%H:%M:%S")
                }
                supabase.table("sessions").upsert(data).execute()
                
                print("\n" + "*"*50)
                print(f" WEBSITE MODE ACTIVE ".center(50, "*"))
                print(f" PAIRING CODE: {pairing_code} ".center(50, " "))
                print(f" Open your Vercel App and enter this code. ".center(50, " "))
                print("*"*50 + "\n")
                
            except Exception as e:
                logger.error(f"Supabase Error: {e}")
                print(f"Error creating session: {e}")
                website_mode = False

    try:
        audio_stream = AudioStream()
        asr = WhisperASR()
        context_buffer = ContextBuffer(WINDOW_SECONDS)
        
        print("Initializing Audio Stream...")
        t = threading.Thread(target=transcription_worker, args=(audio_stream, asr, context_buffer))
        t.daemon = True
        
        with audio_stream.start():
            t.start()
            print("Listening... Press ESC to trigger AI")
            
            while True:
                if keyboard.is_pressed("esc"):
                    print("\nTriggered! Generating response...")
                    try:
                        snapshot = context_buffer.get_snapshot()
                        if not snapshot.strip():
                            print("Buffer empty, nothing to send.")
                            time.sleep(0.5)
                            continue

                        ai_response = ask_gemini(snapshot)
                        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        
                        # Save to file
                        file_ts = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
                        random_suffix = random.randint(1000, 9999)
                        filename = f"outputs/response_{file_ts}_{random_suffix}.json"

                        output = {
                            "timestamp": timestamp_str,
                            "window_seconds": WINDOW_SECONDS,
                            "context": snapshot,
                            "response": ai_response,
                            "provider": "gemini"
                        }

                        with open(filename, "w", encoding="utf-8") as f:
                            json.dump(output, f, indent=2, ensure_ascii=False)

                        print(f"\nAI RESPONSE:\n{ai_response}")
                        print(f"\nSaved to {filename}")

                        if website_mode and supabase:
                            try:
                                supabase.table("sessions").update({
                                    "response": ai_response,
                                    "timestamp": timestamp_str
                                }).eq("id", pairing_code).execute()
                                print("Sent to Supabase.")
                            except Exception as e:
                                logger.error(f"Failed to send to Supabase: {e}")
                            
                    except Exception as e:
                        logger.error(f"Error during trigger: {e}")
                        print(f"Error: {e}")
                    
                    # Debounce
                    time.sleep(0.5)
                
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        print(f"\nFatal Error: {e}")
    finally:
        running = False
        print("Exited.")

if __name__ == "__main__":
    main()
