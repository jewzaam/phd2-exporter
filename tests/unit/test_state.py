# Generated-by: Cursor (Claude Sonnet 4.5)
"""Unit tests for state module."""

from phd2_exporter.state import PHD2State, get_state


def test_phd2_state_initialization():
    """Test PHD2State initialization."""
    state = PHD2State()
    assert state.phd_state == ""
    assert state.phd_settling is False
    assert state.phd_rms_samples == 15
    assert state.phd_rms_data == {}
    assert state.pixel_scale == 0.0
    assert state.jrpc_callbacks == {}
    assert state.global_labels is None
    assert state.debug is False


def test_set_global_labels():
    """Test setting global labels."""
    state = PHD2State()
    state.set_global_labels("TestHost", 1)
    assert state.global_labels == {"host": "testhost", "inst": 1}


def test_set_global_labels_lowercase():
    """Test that host is lowercased."""
    state = PHD2State()
    state.set_global_labels("UPPERCASE", 2)
    assert state.global_labels["host"] == "uppercase"


def test_get_global_labels():
    """Test getting global labels."""
    state = PHD2State()
    state.set_global_labels("TestHost", 1)
    labels = state.get_global_labels_deepcopy()
    assert labels == {"host": "testhost", "inst": 1}


def test_get_global_labels_copy():
    """Test that get_global_labels returns a copy."""
    state = PHD2State()
    state.set_global_labels("TestHost", 1)
    labels = state.get_global_labels_deepcopy()
    labels["modified"] = True
    assert "modified" not in state.global_labels


def test_get_global_labels_none():
    """Test getting global labels when None."""
    state = PHD2State()
    labels = state.get_global_labels_deepcopy()
    assert labels == {}


def test_reset_rms_data():
    """Test resetting RMS data."""
    state = PHD2State()
    state.phd_rms_data = {"test": [1, 2, 3]}
    state.reset_rms_data()
    assert state.phd_rms_data == {}


def test_get_state():
    """Test getting the global state instance."""
    state1 = get_state()
    state2 = get_state()
    assert state1 is state2  # Should be the same instance
