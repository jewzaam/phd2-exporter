# Generated-by: Cursor (Claude Sonnet 4.5)
"""PHD2 event handling."""

import socket
from typing import Any

from .jsonrpc import request_connected, request_current_equipment, request_pixel_scale
from .rms import calculate_and_export_rms, collect_rms_data
from .state import APP_STATES, get_state
from .utils import create_event_metrics, make_labels, utility_inc, utility_set


def handle_event(s: socket.socket, data: dict[str, Any]) -> None:
    """Handle a PHD2 event."""
    state = get_state()

    if "Event" not in data:
        return

    event = data["Event"]

    # use global PHD_STATE to get an updated state, which is then updated at the end of the function

    if event in ["Version", "AppState"]:
        # initialize global labels
        state.set_global_labels(data["Host"], data["Inst"])

    # update state based on event
    if event in ["LoopingExposuresStopped"]:
        state.phd_state = "Stopped"
        # reset RMS data
        state.reset_rms_data()
    elif event in ["LockPositionSet"]:
        state.phd_state = "Selected"
    elif event in ["StartCalibration", "Calibrating"]:
        state.phd_state = "Calibrating"
    elif event in ["GuideStep"]:
        state.phd_state = "Guiding"
    elif event in ["StarLost"]:
        state.phd_state = "LostLock"
    elif event in ["Paused"]:
        state.phd_state = "Paused"
    elif event in ["LoopingExposures"]:
        state.phd_state = "Looping"
    elif event == "AppState" and "State" in data:
        state.phd_state = data["State"]
        state.phd_settling = False
    elif event in ["SettleBegin", "Settling"]:
        state.phd_settling = True
    elif event in ["SettleDone"]:
        state.phd_settling = False

    # Export status metrics
    if state.global_labels is not None:
        for status in APP_STATES:
            value = int(state.phd_state == status)
            labels = state.get_global_labels_deepcopy()
            labels.update({"status": status})
            utility_set("phd2_status", value, labels)

        # set settling status, which can be true while other states are true
        value = int(state.phd_settling)
        labels = state.get_global_labels_deepcopy()
        labels.update({"status": "Settling"})
        utility_set("phd2_status", value, labels)

    # very chatty with GuideStep events
    # print("EVENT: " + event)

    # did equipment change? get pixel scale! uses callback so reading is handled in main loop
    if event in ["AppState", "ConfigurationChange"]:
        # get updated pixel scale
        request_pixel_scale(s)

    # check for equipment connection changes at key events
    # note, could stop guiding because equipment disconnects.  there is no event if equipment is disconnected :(
    if event in ["AppState", "ConfigurationChange", "LoopingExposuresStopped"]:
        # get updated connected state
        request_connected(s)
        # get updated equipment list
        request_current_equipment(s)

    if state.global_labels is None:
        return

    # Handle event-specific metrics
    if event in ["LockPositionSet", "StarSelected"]:
        create_event_metrics(data, state.global_labels, ["X", "Y"])
    elif event == "Calibrating":
        labels = state.get_global_labels_deepcopy()
        labels.update(make_labels(data, ["dir"]))
        create_event_metrics(data, labels, ["dist", "dx", "dy", "step"])
    elif event == "Settling":
        create_event_metrics(
            data, state.global_labels, ["Distance", "Time", "SettleTime", "StarLocked"]
        )
    elif event == "SettleDone":
        # TODO consider if should flip "Status" from 0==success to 1==success....
        create_event_metrics(
            data, state.global_labels, ["Status", "TotalFrames", "DroppedFrames"]
        )
    elif event == "StarLost":
        create_event_metrics(
            data, state.global_labels, ["StarMass", "SNR", "AvgDist", "ErrorCode"]
        )
    elif event == "GuideStep":
        # general metrics
        create_event_metrics(
            data,
            state.global_labels,
            [
                "dx",
                "dy",
                "RADistanceRaw",
                "DECDistanceRaw",
                "RADistanceGuide",
                "DECDistanceGuide",
                "StarMass",
                "SNR",
                "HFD",
                "AvgDist",
                "ErrorCode",
            ],
        )

        # RA pulse metric
        l_ra = state.get_global_labels_deepcopy()
        l_ra.update(make_labels(data, ["RADirection", "RALimited"]))
        create_event_metrics(data, l_ra, ["RADuration"])

        # DEC pulse metric
        l_dec = state.get_global_labels_deepcopy()
        l_dec.update(make_labels(data, ["DECDirection", "DecLimited"]))
        create_event_metrics(data, l_dec, ["DECDuration"])

        # skip RMS if settling
        if not state.phd_settling:
            # collect data for RMS
            calculate_rms = collect_rms_data(data)

            if calculate_rms:
                calculate_and_export_rms()

    elif event == "GuidingDithered":
        create_event_metrics(data, state.global_labels, ["dx", "dy"])

    utility_inc(f"phd2_{event}", state.global_labels)
