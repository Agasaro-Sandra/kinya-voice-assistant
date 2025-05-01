import os
import logging
from typing import Dict, Optional
import yaml
from black import datetime
from dotenv import load_dotenv
from transformers import WhisperForConditionalGeneration, WhisperProcessor
import torch
import numpy as np
import sounddevice as sd
from .utils.audio_processor import AudioProcessor
from .utils.tts_engine import KinyarwandaTTS
from scipy.io.wavfile import write, read
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceAssistant:
    def __init__(self):
        load_dotenv()
        self._load_config()
        self._init_models()
        self.tts = KinyarwandaTTS()
        self.audio_processor = AudioProcessor()

    def _load_config(self, config_dir="config"):
        """Load configuration with error handling"""
        config_path = Path(config_dir)

        try:
            with open(config_path / "default.yaml") as f:
                self.config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            self.config = {"whisper": {"model": "test_model"}}
            print("Warning: Using default config")

        try:
            with open(config_path / "prompts.yaml") as f:
                self.qa_pairs = yaml.safe_load(f).get("kinyarwanda", {})
        except FileNotFoundError:
            self.qa_pairs = {"test": "test_response"}
            print("Warning: Using test prompts")

    def _init_models(self) -> None:
        """Initialize ASR models with error handling"""
        try:
            self.processor = WhisperProcessor.from_pretrained(
                self.config["whisper"]["model"]
            )
            self.model = WhisperForConditionalGeneration.from_pretrained(
                self.config["whisper"]["model"],
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            ).to("cuda" if torch.cuda.is_available() else "cpu")
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            raise

    def record_audio(self, duration: float = 5.0) -> Optional[str]:
        """Professional-grade audio recording"""
        try:
            samplerate = self.config["audio"]["sample_rate"]
            audio = sd.rec(
                int(duration * samplerate),
                samplerate=samplerate,
                channels=1,
                dtype='float32'
            )
            sd.wait()

            os.makedirs("../audio_samples/raw", exist_ok=True)
            filename = f"audio_samples/raw/recording_{datetime.now().isoformat()}.wav"
            write(filename, samplerate, audio)

            return self.audio_processor.process(filename)
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            return None

    def transcribe(self, audio_path: str) -> Optional[str]:
        """Optimized transcription pipeline"""
        try:
            sr, audio = read(audio_path)
            inputs = self.processor(
                audio,
                sampling_rate=sr,
                return_tensors="pt"
            ).to(self.model.device)

            outputs = self.model.generate(
                **inputs,
                **self.config["whisper"]["generation"]
            )

            return self.processor.batch_decode(
                outputs,
                skip_special_tokens=True
            )[0].lower()
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None

    def run(self):
        """Main interaction loop"""
        print("=== Kinyarwanda Voice Assistant ===")
        while True:
            try:
                if audio_path := self.record_audio():
                    if text := self.transcribe(audio_path):
                        response = self.qa_pairs.get(text, "Sinzi icyo ushaka")
                        print(f"You: {text}\nBot: {response}")
                        self.tts.speak(response)
            except KeyboardInterrupt:
                logger.info("Session ended by user")
                break


if __name__ == "__main__":
    VoiceAssistant().run()