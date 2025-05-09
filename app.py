
import streamlit as st
import requests
import tempfile
import os
from pydub import AudioSegment
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

uploaded_file = st.file_uploader("📁 Upload a WAV file (16kHz mono)", type=["wav"])
audio_file = None

if uploaded_file:
    audio_file = uploaded_file
    st.audio(uploaded_file, format="audio/wav")

# --- Transcription ---
if audio_file and st.button("📝 Transcribe"):
    if not API_KEY:
        st.error("❌ API Key not found. Please set it in .env or Streamlit Secrets.")
    else:
        st.info("Sending to NVIDIA Parakeet API...")

        headers = {"Authorization": f"Bearer {API_KEY}"}
        files = {
            "file": (getattr(audio_file, 'name', "audio.wav"), audio_file, "audio/wav")
        }

        try:
            response = requests.post(API_URL, headers=headers, files=files)
            response.raise_for_status()
            result = response.json()

            st.success("🗒️ Transcription:")
            st.text_area("Transcribed Text", result.get("text", "No transcription"), height=200)

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error: {e}")
