# Generated-by: Cursor (Claude Sonnet 4.5)
"""Global state management for PHD2 exporter."""

import copy
from threading import Lock
from typing import Any

# Application states from PHD2
APP_STATES = [
    "Stopped",  # PHD is idle
    "Selected",  # A star is selected but PHD is neither looping exposures, calibrating, or guiding
    "Calibrating",  # PHD is calibrating
    "Guiding",  # PHD is guiding
    "LostLock",  # PHD is guiding, but the frame was dropped
    "Paused",  # PHD is paused
    "Looping",  # PHD is looping exposures
]


class PHD2State:
    """Global state for PHD2 exporter."""

    def __init__(self) -> None:
        """Initialize PHD2 state."""
        self.phd_state = ""
        self.phd_settling = False
        self.phd_rms_samples = 15
        self.phd_rms_data: dict[str, list[float]] = {}
        self.pixel_scale = 0.0
        self.jrpc_callbacks: dict[int, Any] = {}
        self.mutex = Lock()
        self.global_labels: dict[str, Any] | None = None
        self.debug = False

    def set_global_labels(self, host: str, inst: int) -> None:
        """Set global labels from PHD2 event."""
        self.global_labels = {
            "host": host.lower(),
            "inst": inst,
        }

    def get_global_labels_deepcopy(self) -> dict[str, Any]:
        """Get a copy of global labels."""
        if self.global_labels is None:
            return {}
        return copy.deepcopy(self.global_labels)

    def reset_rms_data(self) -> None:
        """Reset RMS data."""
        self.phd_rms_data = {}


# Global state instance
_state = PHD2State()


def get_state() -> PHD2State:
    """Get the global state instance."""
    return _state
