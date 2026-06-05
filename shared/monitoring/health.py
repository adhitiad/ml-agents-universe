"""Health Monitor dengan Circuit Breaker Pattern."""

import time


class HealthMonitor:
    """Melacak status kegagalan komponen eksternal/internal."""

    def __init__(self, failure_threshold: int = 3, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._failures = 0
        self._last_failure_time: float = 0.0
        self._state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_failure(self):
        """Mencatat terjadinya sebuah kegagalan dan berpotensi membuka sirkuit (OPEN) jika melebihi ambang batas."""
        self._failures += 1
        self._last_failure_time = time.time()
        if self._failures >= self.failure_threshold:
            self._state = "OPEN"

    def record_success(self):
        """Mencatat keberhasilan operasi dan menutup sirkuit (CLOSED), meng-reset penghitung kegagalan."""
        self._failures = 0
        self._state = "CLOSED"

    def is_healthy(self) -> bool:
        """Memeriksa apakah komponen masih dianggap sehat atau sedang diisolasi (Circuit OPEN)."""
        if self._state == "OPEN":
            if time.time() - self._last_failure_time > self.reset_timeout:
                self._state = "HALF_OPEN"
                return True  # Izinkan 1 test request
            return False
        return True
