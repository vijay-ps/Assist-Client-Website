import pyaudiowpatch as pyaudio
import wave
import keyboard
import random
import re
from faster_whisper import WhisperModel
from pathlib import Path
from google import genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

Path("recordings").mkdir(exist_ok=True)
Path("transcriptions").mkdir(exist_ok=True)
Path("outputs").mkdir(exist_ok=True)

num = str(random.randint(0, 100))

def clean_llm_output(text: str) -> str:
    if not text:
        return ""

    # Remove markdown bullets (*, -, •)
    text = re.sub(r'^[\s*\-•]+', '', text, flags=re.MULTILINE)

    # Remove remaining asterisks used for emphasis
    text = text.replace("*", "")

    # Remove markdown headings
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

    # Collapse multiple newlines into one
    text = re.sub(r'\n{2,}', '\n', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text

def record():
    chunk_size = 512
    dev_format = pyaudio.paInt16
    channels = 2
    p = pyaudio.PyAudio()
    device_index = 13
    sample_rate = int(p.get_device_info_by_index(device_index)['defaultSampleRate'])
    frames = []
    stream = p.open(format=dev_format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=chunk_size)
    print("Start recording...")
    while True:
        data = stream.read(chunk_size, exception_on_overflow=False)
        frames.append(data)
        if keyboard.is_pressed('esc'):
            break
    if not frames:
        print("No frames recorded.")
        return
    print("Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    filename = "recordings/test_audio" + num + ".wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(dev_format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe():
    model_size = "base"
    model = WhisperModel(model_size)
    file = "recordings/test_audio" + num + ".wav"
    segments, info = model.transcribe(file)
    with open("transcriptions/test_audio" + num + ".txt", "w") as f:
        for segment in segments:
            f.write(segment.text + "\n")
    print("Transcription completed.")

def fetch_result():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    text = ""
    with open("transcriptions/test_audio" + num + ".txt", "r") as f:
        text = f.read()
    print("Fetching result...")
    contents = """
    You are a senior corporate professional with strong communication skills.

    Your responses are:
    - bullet points
    - Clear and concise
    - Calm and confident
    - Professional and diplomatic
    - Free of filler words

    Explain the project to the other team members.

    Recent conversation:""" + text
    response = client.models.generate_content(model="gemini-2.5-flash", contents=contents)
    with open("outputs/test_audio" + num + ".json", "w",encoding="utf-8") as f:
        json.dump(clean_llm_output(response.text), f, ensure_ascii=False)   
    print("Result fetched.")

record()
transcribe()
fetch_result()
