# Generated-by: Cursor (Claude Sonnet 4.5)
"""Unit tests for event handling."""

from unittest.mock import MagicMock, patch

from phd2_exporter.events import handle_event
from phd2_exporter.state import PHD2State


def test_handle_event_version():
    """Test handling Version event."""
    state = PHD2State()
    mock_socket = MagicMock()

    with (
        patch("phd2_exporter.events.get_state", return_value=state),
        patch("phd2_exporter.events.request_pixel_scale"),
    ):
        data = {"Event": "Version", "Host": "TestHost", "Inst": 1}
        handle_event(mock_socket, data)

        assert state.global_labels == {"host": "testhost", "inst": 1}


def test_handle_event_app_state():
    """Test handling AppState event."""
    state = PHD2State()
    mock_socket = MagicMock()

    with (
        patch("phd2_exporter.events.get_state", return_value=state),
        patch("phd2_exporter.events.request_pixel_scale"),
        patch("phd2_exporter.events.request_connected"),
        patch("phd2_exporter.events.request_current_equipment"),
        patch("phd2_exporter.events.utility_set"),
        patch("phd2_exporter.events.utility_inc"),
    ):
        data = {"Event": "AppState", "Host": "TestHost", "Inst": 1, "State": "Looping"}
        handle_event(mock_socket, data)

        assert state.phd_state == "Looping"
        assert state.phd_settling is False


def test_handle_event_looping_exposures_stopped():
    """Test handling LoopingExposuresStopped event."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)
    state.phd_rms_data = {"test": [1, 2, 3]}
    mock_socket = MagicMock()

    with (
        patch("phd2_exporter.events.get_state", return_value=state),
        patch("phd2_exporter.events.request_connected"),
        patch("phd2_exporter.events.request_current_equipment"),
        patch("phd2_exporter.events.utility_set"),
        patch("phd2_exporter.events.utility_inc"),
    ):
        data = {"Event": "LoopingExposuresStopped"}
        handle_event(mock_socket, data)

        assert state.phd_state == "Stopped"
        assert state.phd_rms_data == {}


def test_handle_event_lock_position_set():
    """Test handling LockPositionSet event."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)
    mock_socket = MagicMock()

    with (
        patch("phd2_exporter.events.get_state", return_value=state),
        patch("phd2_exporter.events.utility_set"),
        patch("phd2_exporter.events.utility_inc"),
    ):
        data = {"Event": "LockPositionSet", "X": 100, "Y": 200}
        handle_event(mock_socket, data)

        assert state.phd_state == "Selected"


def test_handle_event_guide_step():
    """Test handling GuideStep event."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)
    state.phd_rms_samples = 3
    mock_socket = MagicMock()

    with (
        patch("phd2_exporter.events.get_state", return_value=state),
        patch("phd2_exporter.events.collect_rms_data", return_value=False),
        patch("phd2_exporter.events.utility_set"),
        patch("phd2_exporter.events.utility_inc"),
    ):
        data = {
            "Event": "GuideStep",
            "dx": 1.0,
            "dy": 2.0,
            "RADistanceRaw": 0.5,
            "DECDistanceRaw": 0.6,
            "RADistanceGuide": 0.7,
            "DECDistanceGuide": 0.8,
            "StarMass": 1000,
            "SNR": 10.5,
            "HFD": 2.5,
            "AvgDist": 1.2,
            "ErrorCode": 0,
            "RADirection": "W",
            "RALimited": False,
            "RADuration": 100,
            "DECDirection": "N",
            "DecLimited": False,
            "DECDuration": 50,
        }
        handle_event(mock_socket, data)

        assert state.phd_state == "Guiding"


def test_handle_event_guide_step_settling():
    """Test that GuideStep doesn't collect RMS during settling."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)
    state.phd_settling = True
    mock_socket = MagicMock()

    with (
        patch("phd2_exporter.events.get_state", return_value=state),
        patch("phd2_exporter.events.collect_rms_data") as mock_collect,
        patch("phd2_exporter.events.utility_set"),
        patch("phd2_exporter.events.utility_inc"),
    ):
        data = {
            "Event": "GuideStep",
            "dx": 1.0,
            "dy": 2.0,
            "RADistanceRaw": 0.5,
            "DECDistanceRaw": 0.6,
            "RADistanceGuide": 0.7,
            "DECDistanceGuide": 0.8,
        }
        handle_event(mock_socket, data)

        # Should not collect RMS during settling
        mock_collect.assert_not_called()


def test_handle_event_star_lost():
    """Test handling StarLost event."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)
    mock_socket = MagicMock()

    with (
        patch("phd2_exporter.events.get_state", return_value=state),
        patch("phd2_exporter.events.utility_set"),
        patch("phd2_exporter.events.utility_inc"),
    ):
        data = {
            "Event": "StarLost",
            "StarMass": 500,
            "SNR": 3.0,
            "AvgDist": 5.0,
            "ErrorCode": 1,
        }
        handle_event(mock_socket, data)

        assert state.phd_state == "LostLock"


def test_handle_event_settling():
    """Test handling Settling events."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)
    mock_socket = MagicMock()

    with (
        patch("phd2_exporter.events.get_state", return_value=state),
        patch("phd2_exporter.events.utility_set"),
        patch("phd2_exporter.events.utility_inc"),
    ):
        data = {"Event": "SettleBegin"}
        handle_event(mock_socket, data)
        assert state.phd_settling is True

        data = {
            "Event": "SettleDone",
            "Status": 0,
            "TotalFrames": 10,
            "DroppedFrames": 0,
        }
        handle_event(mock_socket, data)
        assert state.phd_settling is False


def test_handle_event_calibrating():
    """Test handling Calibrating event."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)
    mock_socket = MagicMock()

    with (
        patch("phd2_exporter.events.get_state", return_value=state),
        patch("phd2_exporter.events.utility_set"),
        patch("phd2_exporter.events.utility_inc"),
    ):
        data = {
            "Event": "Calibrating",
            "dir": "N",
            "dist": 10.5,
            "dx": 1.0,
            "dy": 2.0,
            "step": 5,
        }
        handle_event(mock_socket, data)

        assert state.phd_state == "Calibrating"


def test_handle_event_paused():
    """Test handling Paused event."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)
    mock_socket = MagicMock()

    with (
        patch("phd2_exporter.events.get_state", return_value=state),
        patch("phd2_exporter.events.utility_set"),
        patch("phd2_exporter.events.utility_inc"),
    ):
        data = {"Event": "Paused"}
        handle_event(mock_socket, data)

        assert state.phd_state == "Paused"


def test_handle_event_no_event_key():
    """Test handling data without Event key."""
    state = PHD2State()
    mock_socket = MagicMock()

    with patch("phd2_exporter.events.get_state", return_value=state):
        data = {"notanevent": "test"}
        handle_event(mock_socket, data)  # Should not raise


def test_handle_event_status_metrics():
    """Test that status metrics are exported for all states."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)
    state.phd_state = "Guiding"
    mock_socket = MagicMock()

    with (
        patch("phd2_exporter.events.get_state", return_value=state),
        patch("phd2_exporter.events.utility_set") as mock_set,
        patch("phd2_exporter.events.utility_inc"),
    ):
        data = {"Event": "GuideStep"}
        handle_event(mock_socket, data)

        # Should set status for all APP_STATES + Settling
        status_calls = [
            call for call in mock_set.call_args_list if call[0][0] == "phd2_status"
        ]
        assert len(status_calls) == 8  # 7 APP_STATES + Settling
