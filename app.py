import streamlit as st
import requests
import tempfile
import os
from pydub import AudioSegment
import sounddevice as sd
import scipy.io.wavfile as wav
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Get API key from environment or Streamlit secrets
API_KEY = os.getenv("API_KEY") or st.secrets.get("API_KEY")
API_URL = "https://api.nvidia.com/tao/tts/parakeet-1.1b-rnnt-multilingual-asr"  # Replace with actual endpoint

st.set_page_config(page_title="Multilingual ASR", layout="centered")
st.title("🎙️ NVIDIA Parakeet Multilingual Speech-to-Text")

# --- UI Controls ---
languages = [
    "English", "Hindi", "Spanish", "French", "German", "Arabic", "Portuguese", "Russian", "Japanese", "Korean"
]
lang = st.selectbox("🌍 Select Language (for context):", languages)

input_mode = st.radio("🎧 Choose input mode:", ["Upload Audio File", "Record Using Microphone"])
audio_file = None

if input_mode == "Upload Audio File":
    uploaded_file = st.file_uploader("📁 Upload a WAV file (16kHz mono)", type=["wav"])
    if uploaded_file:
        audio_file = uploaded_file
        st.audio(uploaded_file, format="audio/wav")

else:
    duration = st.slider("⏱️ Recording duration (seconds):", 2, 15, 5)
    if st.button("🎤 Start Recording"):
        st.info("Recording...")
        fs = 16000
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
        sd.wait()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wav.write(f.name, fs, recording)
            audio_file = open(f.name, "rb")
            st.audio(f.name, format="audio/wav")
            st.success("Recording complete!")

# --- Transcription ---
if audio_file and st.button("📝 Transcribe"):
    if not API_KEY:
        st.error("❌ API Key not found. Please set it in .env or Streamlit Secrets.")
    else:
        st.info("Sending to NVIDIA Parakeet API...")

        headers = {"Authorization": f"Bearer {API_KEY}"}
        files = {
            "file": (getattr(audio_file, 'name', "recording.wav"), audio_file, "audio/wav")
        }

        try:
            response = requests.post(API_URL, headers=headers, files=files)
            response.raise_for_status()
            result = response.json()

            st.success("🗒️ Transcription:")
            st.text_area("Transcribed Text", result.get("text", "No transcription"), height=200)

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error: {e}")
