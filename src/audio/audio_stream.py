import pyaudiowpatch as pyaudio
import numpy as np
import queue
import scipy.signal

class AudioStream:
    def __init__(self, device_index=13, target_rate=16000, channels=2, chunk_size=512):
        self.device_index = device_index
        self.target_rate = target_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.queue = queue.Queue()
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.native_rate = int(self.p.get_device_info_by_index(device_index)["defaultSampleRate"])

    def _callback(self, in_data, frame_count, time_info, status):
        self.queue.put(in_data)
        return (in_data, pyaudio.paContinue)

    def start(self):
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.native_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._callback
        )
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def stop(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def get_chunk(self):
        try:
            data = self.queue.get_nowait()
            audio_np = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            
            if self.channels > 1:
                audio_np = audio_np.reshape(-1, self.channels).mean(axis=1)
            
            if self.native_rate != self.target_rate:
                num_samples = int(len(audio_np) * self.target_rate / self.native_rate)
                audio_np = scipy.signal.resample(audio_np, num_samples)
                
            return audio_np
        except queue.Empty:
            return None
