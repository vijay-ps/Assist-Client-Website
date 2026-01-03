from faster_whisper import WhisperModel

class WhisperASR:
    def __init__(self, model_size="base"):
        self.model = WhisperModel(model_size, compute_type="int8")

    def transcribe(self, audio):
        segments, _ = self.model.transcribe(
            audio,
            language="en",
            vad_filter=True
        )
        return [segment.text for segment in segments]
