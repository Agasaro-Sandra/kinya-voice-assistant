"""Main package for Kinyarwanda Voice Assistant."""
from .voice_assistant import VoiceAssistant  # Makes VoiceAssistant importable from package root

__version__ = "1.0.0"
__all__ = ['VoiceAssistant']  # Controls what gets imported with `from kinya_voice_assistant import *`