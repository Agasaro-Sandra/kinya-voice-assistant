from pathlib import Path
import pytest


@pytest.fixture
def assistant():
    from kinya_voice_assistant.voice_assistant import VoiceAssistant
    return VoiceAssistant()


def test_transcription(assistant, tmp_path):
    """Test config loading with temporary files"""
    # Create test config directory
    test_config = Path(tmp_path) / "config"
    test_config.mkdir()

    # Create minimal default.yaml
    (test_config / "default.yaml").write_text("""
    whisper:
      model: "test_model"
    audio:
      sample_rate: 16000
    """)

    # Create minimal prompts.yaml
    (test_config / "prompts.yaml").write_text("""
    kinyarwanda:
      test: "test_response"
    """)

    # Test loading
    assistant._load_config(config_dir=str(test_config))

    # Verify configs loaded
    assert assistant.config["whisper"]["model"] == "test_model"
    assert assistant.qa_pairs["test"] == "test_response"