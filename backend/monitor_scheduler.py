"""Opt-in, single-process scheduler for regulatory monitoring."""
import logging
import threading

from . import config
from .monitor import run_monitor_cycle

log = logging.getLogger(__name__)
_started = False
_lock = threading.Lock()

def start_monitor_scheduler() -> None:
    """Start one daemon loop only when ENABLE_REGULATORY_MONITOR is true."""
    global _started
    with _lock:
        if _started or not config.ENABLE_REGULATORY_MONITOR:
            return
        _started = True

    def loop() -> None:
        while True:
            try:
                run_monitor_cycle()
            except Exception:
                log.exception("Regulatory monitor cycle failed")
            threading.Event().wait(config.MONITOR_INTERVAL_MINUTES * 60)

    threading.Thread(target=loop, name="regulatory-monitor", daemon=True).start()
