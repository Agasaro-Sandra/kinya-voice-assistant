# Architecture Decisions

## ASR Choice
- **KinyaWhisper** over vanilla Whisper for:
  - Lower WER on Kinyarwanda (51.85% vs 68.2%)
  - Fine-tuned on Rwandan speech patterns

## TTS Fallback Strategy
1. `espeak` (Linux-native) → Best for Kinyarwanda phonemes
2. `pyttsx3` → Cross-platform but robotic
3. `gTTS` → Cloud fallback (French accent)

# Performance Benchmarks
| Component         | Latency | Accuracy |
|-------------------|---------|----------|
| ASR               | 1.2s    | 88%      |
| TTS (espeak)      | 0.3s    | 95%      |