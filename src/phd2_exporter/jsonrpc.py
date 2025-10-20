# Generated-by: Cursor (Claude Sonnet 4.5)
"""JSONRPC request handling for PHD2."""

import json
import random
import socket
from collections.abc import Callable
from typing import Any

from .state import get_state
from .utils import utility_set


def random_jrpc_request_id() -> int:
    """Generate a random unique JSONRPC request ID."""
    state = get_state()
    request_id = -1
    # only need mutex when claiming a request ID
    state.mutex.acquire()
    while True:
        request_id = random.randint(1, 50000)
        if request_id not in state.jrpc_callbacks:
            break
    # claim the request id
    state.jrpc_callbacks[request_id] = request_id
    state.mutex.release()
    return request_id


def callback_request_pixel_scale(data: dict[str, Any]) -> None:
    """Callback for pixel scale request."""
    state = get_state()
    state.pixel_scale = data["result"]
    if state.global_labels is not None:
        utility_set("phd2_pixel_scale", state.pixel_scale, state.global_labels)
    if "id" in data:
        # unregister the callback, work is done
        state.jrpc_callbacks.pop(data["id"])


def callback_request_connected(data: dict[str, Any]) -> None:
    """Callback for connected request."""
    state = get_state()
    connected = data["result"]
    if state.global_labels is not None:
        utility_set("phd2_connected", connected, state.global_labels)
    if "id" in data:
        # unregister the callback, work is done
        state.jrpc_callbacks.pop(data["id"])


def callback_request_current_equipment(data: dict[str, Any]) -> None:
    """Callback for current equipment request."""
    state = get_state()
    if state.global_labels is None:
        return

    equipment = data["result"]
    # structure: key is the type of equipment. value is object. object has boolean property "connected" and string "name".
    for key in equipment:
        eq = equipment[key]
        connected = False
        # NOTE do not collect 'name' as the value will change when device is connected and is not worth cardinality hit.
        if "connected" in eq:
            connected = eq["connected"]
        labels = state.get_global_labels_deepcopy()
        labels.update({"device": key})
        utility_set("phd2_current_equipment", connected, labels)


def request_pixel_scale(s: socket.socket) -> None:
    """Request pixel scale from PHD2."""
    state = get_state()
    # socket exception handling done in main loop
    # send request
    request_id = random_jrpc_request_id()
    request = {
        "method": "get_pixel_scale",
        "id": request_id,
    }
    state.jrpc_callbacks[request_id] = callback_request_pixel_scale
    s.sendall((json.dumps(request) + "\r\n").encode("utf-8"))


def request_connected(s: socket.socket) -> None:
    """Request connected status from PHD2."""
    state = get_state()
    # socket exception handling done in main loop
    # send request
    request_id = random_jrpc_request_id()
    request = {
        "method": "get_connected",
        "id": request_id,
    }
    state.jrpc_callbacks[request_id] = callback_request_connected
    s.sendall((json.dumps(request) + "\r\n").encode("utf-8"))


def request_current_equipment(s: socket.socket) -> None:
    """Request current equipment from PHD2."""
    state = get_state()
    # socket exception handling done in main loop
    # send request
    request_id = random_jrpc_request_id()
    request = {
        "method": "get_current_equipment",
        "id": request_id,
    }
    state.jrpc_callbacks[request_id] = callback_request_current_equipment
    s.sendall((json.dumps(request) + "\r\n").encode("utf-8"))


def handle_jsonrpc_response(data: dict[str, Any]) -> None:
    """Handle JSONRPC response by calling registered callback."""
    state = get_state()
    if "id" in data and data["id"] in state.jrpc_callbacks:
        callback: Callable[[dict[str, Any]], None] = state.jrpc_callbacks[data["id"]]
        callback(data)
