import os
import time
from datetime import datetime
from scipy.io.wavfile import read, write
from transformers import WhisperForConditionalGeneration, WhisperProcessor
import sounddevice as sd
import numpy as np
from huggingface_hub import login
from dotenv import load_dotenv
import simpleaudio as sa
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import torch

# 1. Setup -------------------------------------------------------------------
load_dotenv()
os.makedirs("audio_samples/raw", exist_ok=True)
os.makedirs("debug", exist_ok=True)

# 2. Authentication ----------------------------------------------------------
try:
    login(token=os.getenv("HF_TOKEN"))
except Exception as e:
    print(f"Authentication failed: {e}")
    exit(1)

# 3. Model Initialization ----------------------------------------------------
try:
    model = WhisperForConditionalGeneration.from_pretrained("benax-rw/KinyaWhisper")
    processor = WhisperProcessor.from_pretrained("benax-rw/KinyaWhisper")
    # Force clear any problematic default configs
    model.generation_config.forced_decoder_ids = None
except Exception as e:
    print(f"Model loading failed: {e}")
    exit(1)

# 4. Kinyarwanda QA Pairs ----------------------------------------------------
QA_PAIRS = {
    "muraho": "Muraho, murakomeye?",
    "amakuru": "Ni meza, ayanyu se?!",
    "witwa nde": "Nitwa Keza Kamaliza.",
    "ukora iki": "Ndi umuganga ku bitaro by'akarere",
    "uvuye he": "Nari ndi hano ntahantu nagiye."
}


# 5. Audio Processing Functions ----------------------------------------------
def trim_silence(audio_path, silence_thresh=-40):
    """Trim silence from both ends of audio"""
    try:
        audio = AudioSegment.from_wav(audio_path)
        nonsilent = detect_nonsilent(
            audio,
            min_silence_len=300,
            silence_thresh=silence_thresh
        )
        if len(nonsilent) > 0:
            start = nonsilent[0][0]
            end = nonsilent[-1][1]
            trimmed = audio[start:end]
            trimmed.export(audio_path, format="wav")
    except Exception as e:
        print(f"Silence trimming warning: {e}")


def record_audio(duration=3):
    """Record audio with visual feedback"""
    print("\nSpeak now...", end="", flush=True)
    audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1, dtype='float32')
    sd.wait()
    print(" Done recording.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = f"audio_samples/raw/recording_{timestamp}.wav"
    write(raw_path, 16000, audio)

    trim_silence(raw_path, silence_thresh=-30)
    return raw_path


# 6. Speech Synthesis ------------------------------------------------------
def speak(text):
    """Text-to-speech using system's speech dispatcher"""
    try:
        # Create temporary WAV file
        from gtts import gTTS
        try:
            # First try with French (closest supported to Kinyarwanda)
            tts = gTTS(text=text, lang='fr')
        except:
            # Fallback to English if French fails
            tts = gTTS(text=text, lang='en')

        mp3_path = "temp_response.mp3"
        wav_path = "temp_response.wav"
        tts.save(mp3_path)

        # Convert to WAV format
        sound = AudioSegment.from_mp3(mp3_path)
        sound.export(wav_path, format="wav")

        # Play audio
        wave_obj = sa.WaveObject.from_wave_file(wav_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()

    except Exception as e:
        print(f"Could not generate speech: {e}")
    finally:
        # Clean up temporary files
        for f in [mp3_path, wav_path]:
            try:
                os.remove(f)
            except:
                pass


# 7. Transcription ----------------------------------------------------------
def transcribe_audio(audio_path):
    """Robust audio transcription with clean config"""
    try:
        fs, audio = read(audio_path)
        if len(audio) == 0:
            print("Empty audio file")
            return None

        inputs = processor(audio, sampling_rate=fs, return_tensors="pt")

        # Clean generation config with no conflicting parameters
        predicted_ids = model.generate(
            inputs["input_features"],
            max_length=64,
            num_beams=3,
            early_stopping=True,
            suppress_tokens=None,  # Explicitly disable suppression
            forced_decoder_ids=None  # Explicitly disable forced ids
        )

        text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].lower()
        return text.strip()

    except Exception as e:
        print(f"Transcription error: {e}")
        return None


# 8. Main Interaction Loop -------------------------------------------------
def main():
    print("\n=== Kinyarwanda Voice Assistant ===")
    print("Available commands: " + ", ".join(QA_PAIRS.keys()))

    while True:
        try:
            # Record user audio
            audio_path = record_audio()
            if not audio_path:
                continue

            # Transcribe
            text = transcribe_audio(audio_path)
            if not text:
                speak("Sinzisobanura")
                continue

            print(f"You said: {text}")

            # Get and speak response
            response = QA_PAIRS.get(text, "Sinzi icyo ushaka")
            print(f"Assistant: {response}")
            speak(response)

        except KeyboardInterrupt:
            print("\nProgram ended")
            break


if __name__ == "__main__":
    main()