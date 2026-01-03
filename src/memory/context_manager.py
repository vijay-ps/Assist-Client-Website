import time
from collections import deque
from threading import Lock

class ContextBuffer:
    def __init__(self, window_seconds=60):
        self.window_seconds = window_seconds
        self.buffer = deque()
        self.lock = Lock()

    def add_segment(self, text: str, timestamp: float = None):
        if not text:
            return

        if timestamp is None:
            timestamp = time.time()

        with self.lock:
            content = {"timestamp": timestamp, "text": text}
            self.buffer.append(content)
            self.prune()

    def prune(self):
        now = time.time()
        cutoff = now - self.window_seconds
        
        while self.buffer and self.buffer[0]["timestamp"] < cutoff:
            self.buffer.popleft()

    def get_snapshot(self) -> str:
        with self.lock:
            self.prune()
            return " ".join(entry["text"] for entry in self.buffer)

c = ContextBuffer()
c.add_segment("Hello")
c.add_segment("World")
print(c.buffer[1])
