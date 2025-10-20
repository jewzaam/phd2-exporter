# Generated-by: Cursor (Claude Sonnet 4.5)
"""RMS calculation for PHD2 guide data."""

import math
from typing import Any

from .state import get_state
from .utils import utility_set

# Constants for metric names and label keys
METRIC_PHD2_RMS = "phd2_rms"

LABEL_SOURCE = "source"
LABEL_SCALE = "scale"

SCALE_PX = "px"
SCALE_ARCSEC = "arcsec"

# Constants for data keys
KEY_DEC_RAW = "DECDistanceRaw"
KEY_DEC_GUIDE = "DECDistanceGuide"
KEY_RA_RAW = "RADistanceRaw"
KEY_RA_GUIDE = "RADistanceGuide"

KEY_TOTAL_RAW = "TotalDistanceRaw"
KEY_TOTAL_GUIDE = "TotalDistanceGuide"

# Constant keys used for RMS collection from GuideStep events
RMS_KEYS = [KEY_DEC_RAW, KEY_DEC_GUIDE, KEY_RA_RAW, KEY_RA_GUIDE]


def collect_rms_data(data: dict[str, Any]) -> bool:
    """
    Collect RMS data from guide step.

    Returns True if enough data is available to calculate RMS.
    """
    state = get_state()
    calculate_rms = True

    for key in RMS_KEYS:
        if key not in data:
            calculate_rms = False
            continue
        if key not in state.phd_rms_data:
            state.phd_rms_data[key] = []
        if len(state.phd_rms_data[key]) >= state.phd_rms_samples:
            state.phd_rms_data[key].pop(0)
        else:
            calculate_rms = False
        state.phd_rms_data[key].append(data[key])

    return calculate_rms


def calculate_and_export_rms() -> None:
    """Calculate and export RMS metrics."""
    state = get_state()

    # fabricate data for "total" as hypotenuse of each DEC/RA {Raw, Guide} tuple
    state.phd_rms_data[KEY_TOTAL_RAW] = []
    state.phd_rms_data[KEY_TOTAL_GUIDE] = []
    for i in range(state.phd_rms_samples):
        state.phd_rms_data[KEY_TOTAL_RAW].append(
            math.sqrt(
                math.pow(state.phd_rms_data[KEY_DEC_RAW][i], 2)
                + math.pow(state.phd_rms_data[KEY_RA_RAW][i], 2)
            )
        )
        state.phd_rms_data[KEY_TOTAL_GUIDE].append(
            math.sqrt(
                math.pow(state.phd_rms_data[KEY_DEC_GUIDE][i], 2)
                + math.pow(state.phd_rms_data[KEY_RA_GUIDE][i], 2)
            )
        )

    # do the math for RMS and export metrics
    for key in state.phd_rms_data:
        rms_sum_of_squares = 0.0
        # do the sum of squares bit
        for value in state.phd_rms_data[key]:
            rms_sum_of_squares += math.pow(value, 2)
        # then divide and sqrt
        rms_px = math.sqrt(rms_sum_of_squares / state.phd_rms_samples)
        utility_set(METRIC_PHD2_RMS, rms_px, {LABEL_SOURCE: key, LABEL_SCALE: SCALE_PX})

        # calculate for arcsec if we have pixel scale
        if state.pixel_scale > 0:
            rms_arcsec = rms_px * state.pixel_scale
            utility_set(
                METRIC_PHD2_RMS,
                rms_arcsec,
                {LABEL_SOURCE: key, LABEL_SCALE: SCALE_ARCSEC},
            )
