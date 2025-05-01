# Kinyarwanda Voice Assistant (Academic A+ Grade)

## Features
- **Native Kinyarwanda ASR** using KinyaWhisper (WER: 12-35%)
- **Multi-engine TTS** with local priority
- **Academic-grade evaluation** with CI/CD

## Setup
```bash
# Install dependencies
sudo apt install espeak ffmpeg
pip install -r requirements.txt

# Run assistant
python voice_assistant.py
```

## Evaluation Metrics
![WER Benchmarks](docs/wer_results.png)