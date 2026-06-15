import threading
import time


class AIMetrics:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self.start_ts = time.time()
            self.calls_attempted = 0
            self.calls_succeeded = 0
            self.calls_failed = 0
            self.calls_sampled = 0

    def incr_attempt(self):
        with self._lock:
            self.calls_attempted += 1

    def incr_success(self):
        with self._lock:
            self.calls_succeeded += 1

    def incr_failed(self):
        with self._lock:
            self.calls_failed += 1

    def incr_sampled(self):
        with self._lock:
            self.calls_sampled += 1

    def snapshot(self):
        with self._lock:
            return {
                "start_ts": self.start_ts,
                "uptime_seconds": int(time.time() - self.start_ts),
                "calls_attempted": self.calls_attempted,
                "calls_succeeded": self.calls_succeeded,
                "calls_failed": self.calls_failed,
                "calls_sampled": self.calls_sampled,
            }


# module-level singleton
metrics = AIMetrics()
