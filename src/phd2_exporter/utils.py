# Generated-by: Cursor (Claude Sonnet 4.5)
"""Utility functions for PHD2 exporter."""

from typing import Any

import metrics_utility

from .state import get_state


def debug(message: str) -> None:
    """Print debug message if debug is enabled."""
    state = get_state()
    if state.debug:
        print(message)


def utility_set(name: str, value: Any, label_dict: dict[str, Any]) -> None:
    """Set a metric value with error handling."""
    try:
        metrics_utility.set(name, value, label_dict)
    except Exception:
        print(f"ERROR: metrics_utility.set({name}, {value}, {label_dict})")
        raise


def utility_inc(name: str, label_dict: dict[str, Any]) -> None:
    """Increment a metric with error handling."""
    try:
        metrics_utility.inc(name, label_dict)
    except Exception:
        print(f"ERROR: metrics_utility.inc({name}, {label_dict})")
        raise


def make_labels(data: dict[str, Any], label_keys: list[str]) -> dict[str, Any]:
    """Create labels dictionary from data."""
    labels = {}

    for label_key in label_keys:
        # default to 0 else future labels will be invalid (must have same labels always)
        labels[label_key] = data.get(label_key, 0)

    return labels


def create_event_metrics(
    data: dict[str, Any], labels: dict[str, Any], metric_keys: list[str]
) -> None:
    """Create metrics for event data."""
    for metric_key in metric_keys:
        if metric_key in data:
            value = data[metric_key]
            if isinstance(value, bool):
                value = 1 if value else 0
            utility_set(f"phd2_{data['Event']}_{metric_key}", value, labels)
