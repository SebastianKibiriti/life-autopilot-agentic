"""Background Taskmaster trigger.

Evaluates every student that has stored commitments on an interval.
Disabled by default so unit tests do not start a worker thread.
"""
from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from typing import Callable

logger = logging.getLogger(__name__)

Clock = Callable[[], datetime]
Tick = Callable[[datetime], None]


class AgentScheduler:
    def __init__(
        self,
        *,
        interval_seconds: int,
        tick: Tick,
        clock: Clock | None = None,
    ) -> None:
        if interval_seconds < 1:
            raise ValueError("interval_seconds must be at least 1")
        self.interval_seconds = interval_seconds
        self._tick = tick
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.run_count = 0
        self.last_run_at: datetime | None = None
        self.last_error: str | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def run_once(self) -> None:
        now = self._clock()
        try:
            self._tick(now)
            self.last_error = None
        except Exception as exc:
            self.last_error = str(exc)
            logger.exception("Agent scheduler tick failed")
            raise
        finally:
            self.run_count += 1
            self.last_run_at = now

    def start(self) -> None:
        if self.running:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="agent-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None

    def status(self) -> dict:
        return {
            "running": self.running,
            "interval_seconds": self.interval_seconds,
            "run_count": self.run_count,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "last_error": self.last_error,
        }

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.run_once()
            except Exception:
                pass
            self._stop.wait(self.interval_seconds)
