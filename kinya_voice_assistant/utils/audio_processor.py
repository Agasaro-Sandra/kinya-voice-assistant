import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from typing import Optional


class AudioProcessor:
    """Professional audio preprocessing"""

    def process(self, audio_path: str, output_dir: str = "audio_samples/processed") -> Optional[str]:
        """
        Trim silence and normalize audio.
        Returns path to processed file.
        """
        try:
            audio = AudioSegment.from_wav(audio_path)

            # Voice Activity Detection
            nonsilent = detect_nonsilent(
                audio,
                min_silence_len=300,
                silence_thresh=-40
            )

            if not nonsilent:
                return None

            # Trim and export
            trimmed = audio[nonsilent[0][0]:nonsilent[-1][1]]
            os.makedirs(output_dir, exist_ok=True)
            output_path = f"{output_dir}/{os.path.basename(audio_path)}"

            # Normalize loudness
            trimmed = trimmed.normalize(headroom=0.1)
            trimmed.export(output_path, format="wav")

            return output_path

        except Exception as e:
            print(f"Audio processing failed: {e}")
            return None