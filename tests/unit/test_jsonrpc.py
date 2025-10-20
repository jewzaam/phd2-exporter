# Generated-by: Cursor (Claude Sonnet 4.5)
"""Unit tests for JSONRPC handling."""

from unittest.mock import MagicMock, patch

from phd2_exporter.jsonrpc import (
    callback_request_connected,
    callback_request_current_equipment,
    callback_request_pixel_scale,
    handle_jsonrpc_response,
    random_jrpc_request_id,
    request_connected,
    request_current_equipment,
    request_pixel_scale,
)
from phd2_exporter.state import PHD2State


def test_random_jrpc_request_id():
    """Test random request ID generation."""
    state = PHD2State()
    with patch("phd2_exporter.jsonrpc.get_state", return_value=state):
        id1 = random_jrpc_request_id()
        id2 = random_jrpc_request_id()

        # IDs should be in range
        assert 1 <= id1 <= 50000
        assert 1 <= id2 <= 50000

        # IDs should be unique
        assert id1 != id2


def test_random_jrpc_request_id_registration():
    """Test that request IDs are registered in callbacks."""
    state = PHD2State()
    with patch("phd2_exporter.jsonrpc.get_state", return_value=state):
        request_id = random_jrpc_request_id()
        assert request_id in state.jrpc_callbacks


def test_callback_request_pixel_scale():
    """Test pixel scale callback."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)

    with (
        patch("phd2_exporter.jsonrpc.get_state", return_value=state),
        patch("phd2_exporter.jsonrpc.utility_set") as mock_set,
    ):
        data = {"result": 2.5, "id": 123}
        state.jrpc_callbacks[123] = 123

        callback_request_pixel_scale(data)

        assert state.pixel_scale == 2.5
        mock_set.assert_called_once()
        assert 123 not in state.jrpc_callbacks  # Should be unregistered


def test_callback_request_connected():
    """Test connected callback."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)

    with (
        patch("phd2_exporter.jsonrpc.get_state", return_value=state),
        patch("phd2_exporter.jsonrpc.utility_set") as mock_set,
    ):
        data = {"result": True, "id": 123}
        state.jrpc_callbacks[123] = 123

        callback_request_connected(data)

        mock_set.assert_called_once_with("phd2_connected", True, state.global_labels)
        assert 123 not in state.jrpc_callbacks


def test_callback_request_current_equipment():
    """Test current equipment callback."""
    state = PHD2State()
    state.set_global_labels("testhost", 1)

    with (
        patch("phd2_exporter.jsonrpc.get_state", return_value=state),
        patch("phd2_exporter.jsonrpc.utility_set") as mock_set,
    ):
        data = {
            "result": {
                "camera": {"connected": True, "name": "TestCamera"},
                "mount": {"connected": False, "name": "TestMount"},
            }
        }

        callback_request_current_equipment(data)

        assert mock_set.call_count == 2


def test_request_pixel_scale():
    """Test pixel scale request."""
    state = PHD2State()
    mock_socket = MagicMock()

    with patch("phd2_exporter.jsonrpc.get_state", return_value=state):
        request_pixel_scale(mock_socket)

        # Should send JSON request
        mock_socket.sendall.assert_called_once()
        sent_data = mock_socket.sendall.call_args[0][0].decode("utf-8")
        assert "get_pixel_scale" in sent_data


def test_request_connected():
    """Test connected request."""
    state = PHD2State()
    mock_socket = MagicMock()

    with patch("phd2_exporter.jsonrpc.get_state", return_value=state):
        request_connected(mock_socket)

        mock_socket.sendall.assert_called_once()
        sent_data = mock_socket.sendall.call_args[0][0].decode("utf-8")
        assert "get_connected" in sent_data


def test_request_current_equipment():
    """Test current equipment request."""
    state = PHD2State()
    mock_socket = MagicMock()

    with patch("phd2_exporter.jsonrpc.get_state", return_value=state):
        request_current_equipment(mock_socket)

        mock_socket.sendall.assert_called_once()
        sent_data = mock_socket.sendall.call_args[0][0].decode("utf-8")
        assert "get_current_equipment" in sent_data


def test_handle_jsonrpc_response():
    """Test JSONRPC response handling."""
    state = PHD2State()
    callback = MagicMock()
    state.jrpc_callbacks[123] = callback

    with patch("phd2_exporter.jsonrpc.get_state", return_value=state):
        data = {"jsonrpc": "2.0", "id": 123, "result": "test"}
        handle_jsonrpc_response(data)

        callback.assert_called_once_with(data)


def test_handle_jsonrpc_response_no_id():
    """Test JSONRPC response without ID."""
    state = PHD2State()

    with patch("phd2_exporter.jsonrpc.get_state", return_value=state):
        data = {"jsonrpc": "2.0", "result": "test"}
        handle_jsonrpc_response(data)  # Should not raise


def test_handle_jsonrpc_response_unknown_id():
    """Test JSONRPC response with unknown ID."""
    state = PHD2State()

    with patch("phd2_exporter.jsonrpc.get_state", return_value=state):
        data = {"jsonrpc": "2.0", "id": 999, "result": "test"}
        handle_jsonrpc_response(data)  # Should not raise
