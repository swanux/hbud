import time

# Based on https://github.com/ravener/stopwatch.py

class Stopwatch:
    def __init__(self):
        self._start = time.perf_counter()
        self._end = None

    @property
    def duration(self):
        return self._end - self._start if self._end else time.perf_counter() - self._start

    @property
    def running(self):
        return not self._end

    def restart(self):
        self._start = time.perf_counter()
        self._end = None
        return self
    
    def restart_at(self, value):
        self._start = time.perf_counter() - value
        self._end = None
        return self

    def reset(self):
        self._start = time.perf_counter()
        self._end = self._start
        return self

    def start(self):
        if not self.running:
            self._start = time.perf_counter() - self.duration
            self._end = None
        return self

    def stop(self):
        if self.running:
            self._end = time.perf_counter()
        return self

    def __str__(self):
        time = self.duration * 1000
        if time >= 1000:
            return "{:.2f}s".format(time / 1000)
        if time >= 1:
            return "{:.2f}ms".format(time)
        return "{:.2f}μs".format(time * 1000)