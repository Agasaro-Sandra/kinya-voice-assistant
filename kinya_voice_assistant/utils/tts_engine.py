import os
import subprocess
from typing import Optional
import pyttsx3
from gtts import gTTS
import simpleaudio as sa
from pydub import AudioSegment


class KinyarwandaTTS:
    def __init__(self):
        self.engines = [
            self._espeak_tts,
            self._pyttsx3_tts,
            self._gtts_fallback
        ]

    def speak(self, text):
        for engine in self.engines:
            if engine(text):
                return True
        return False

    def _espeak_tts(self, text):
        try:
            import subprocess
            subprocess.run(["espeak", "-v", "rw", text], check=True)
            return True
        except:
            return False

    def _pyttsx3_tts(self, text):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return True
        except:
            return False

    def _gtts_fallback(self, text):
        try:
            from gtts import gTTS
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".mp3") as fp:
                tts = gTTS(text=text, lang='fr')
                tts.save(fp.name)
                return True
        except:
            return False