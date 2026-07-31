from __future__ import annotations

import threading
import time
from collections.abc import Callable


class RateLimiter:
    """
    Controla o intervalo mínimo entre
    requisições feitas a um provedor.

    O controle é seguro para múltiplas
    threads dentro do mesmo processo.
    """

    def __init__(
        self,
        requests_per_minute: int,
        *,
        clock: Callable[[], float] = (
            time.monotonic
        ),
        sleeper: Callable[[float], None] = (
            time.sleep
        ),
    ) -> None:
        if requests_per_minute <= 0:
            raise ValueError(
                "requests_per_minute deve "
                "ser maior que zero."
            )

        self.requests_per_minute = (
            requests_per_minute
        )

        self.minimum_interval_seconds = (
            60.0
            / requests_per_minute
        )

        self._clock = clock
        self._sleeper = sleeper

        self._lock = threading.Lock()

        self._last_request_at: (
            float | None
        ) = None

    def acquire(
        self,
    ) -> None:
        """
        Aguarda até que uma nova requisição
        possa ser realizada.
        """

        with self._lock:
            current_time = self._clock()

            if self._last_request_at is not None:
                elapsed_seconds = (
                    current_time
                    - self._last_request_at
                )

                remaining_seconds = (
                    self.minimum_interval_seconds
                    - elapsed_seconds
                )

                if remaining_seconds > 0:
                    self._sleeper(
                        remaining_seconds
                    )

            self._last_request_at = (
                self._clock()
            )