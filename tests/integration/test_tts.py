import pytest
from unittest.mock import Mock
from kinya_voice_assistant.utils.tts_engine import KinyarwandaTTS


@pytest.fixture
def tts():
    return KinyarwandaTTS()


def test_tts_priority(tts, mocker):
    """Test engine fallback sequence"""
    # Mock all engines to fail except pyttsx3
    mocker.patch.object(tts, '_espeak_tts', return_value=False)
    mocker.patch.object(tts, '_pyttsx3_tts', return_value=True)
    mocker.patch.object(tts, '_gtts_fallback', return_value=False)

    assert tts.speak("test") is True
    tts._espeak_tts.assert_called_once_with("test")
    tts._pyttsx3_tts.assert_called_once_with("test")
    tts._gtts_fallback.assert_not_called()


def test_all_engines_fail(tts, mocker):
    """Test behavior when all engines fail"""
    mocker.patch.object(tts, '_espeak_tts', return_value=False)
    mocker.patch.object(tts, '_pyttsx3_tts', return_value=False)
    mocker.patch.object(tts, '_gtts_fallback', return_value=False)

    assert tts.speak("test") is False