# Generated-by: Cursor (Claude Sonnet 4.5)
"""Main entry point for PHD2 exporter."""

import argparse
import json
import socket
import time

import metrics_utility

from .events import handle_event
from .jsonrpc import handle_jsonrpc_response
from .state import get_state
from .utils import utility_inc


def parse_args() -> dict:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Export PHD2 events as prometheus metrics."
    )
    parser.add_argument(
        "--phd2port",
        type=int,
        help="the port PHD2 is exposing events on, default: 4400",
    )
    parser.add_argument(
        "--phd2host",
        type=str,
        help="the host PHD2 is exposing events on, default: 127.0.0.1",
    )
    parser.add_argument(
        "--port", type=int, help="the port to export metrics on, default: 9753"
    )
    parser.add_argument(
        "--rms_samples",
        type=int,
        help="number of samples used to calculate RMS, default: 10",
    )

    # treat args parsed as a dictionary
    return vars(parser.parse_args())


def get_config(args: dict) -> tuple[str, int, int, int]:
    """Extract configuration from parsed arguments."""
    phd2port = 4400
    if args.get("phd2port"):
        phd2port = args["phd2port"]
    phd2host = "127.0.0.1"
    if args.get("phd2host"):
        phd2host = args["phd2host"]
    port = 9753
    if args.get("port"):
        port = args["port"]
    rms_samples = 10
    if args.get("rms_samples"):
        rms_samples = args["rms_samples"]

    return phd2host, phd2port, port, rms_samples


def run_exporter_loop(phd2host: str, phd2port: int) -> None:
    """Run the main exporter loop."""
    state = get_state()
    print_connect_error = True

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((phd2host, phd2port))
                print_connect_error = True
                s.setblocking(False)
                s.settimeout(2.0)
                while True:
                    try:
                        raw = s.recv(1024)
                        if len(raw) == 0:
                            # empty response without a timeout, server is down
                            # break the loop, which triggers a reconnect
                            break
                        # keep a count (inc / total) for everything
                        if state.global_labels is not None:
                            utility_inc("phd2", state.global_labels)
                    except TimeoutError:
                        # this is fine, just nothing to read.  PHD2 idle.  No metric so it's not confused as an error
                        # keep a count (inc / total) for everything
                        if state.global_labels is not None:
                            utility_inc("phd2", state.global_labels)
                        continue
                    except Exception as e:
                        # non-timeout error, this is bad.  break the loop, which will trigger reconnect
                        utility_inc("phd2_error", {"type": type(e).__name__})
                        print(f"Exception: {e}")
                        break
                    lines = raw.decode()
                    for line in lines.split("\r\n"):
                        if len(line) > 0:
                            data = json.loads(line)
                            if "Event" in data:
                                handle_event(s, data)
                            elif "jsonrpc" in data and "id" in data:
                                handle_jsonrpc_response(data)
        except OSError as e:
            utility_inc("phd2_error", {"type": type(e).__name__})
            # Connection refused error code - don't log these, it's spammy
            connection_refused_errno = 10061
            if e.errno == connection_refused_errno:
                if print_connect_error:
                    print(
                        "Failed to connect to PHD2.  Server is down or unreachable.  Retrying silently..."
                    )
                    print_connect_error = False
            else:
                print(f"socket.error: {e}")
        except Exception as e:
            utility_inc("phd2_error", {"type": type(e).__name__})
            print(f"Exception: {e}")

        # something went wrong.  try again in a little bit...
        time.sleep(2)


def main() -> int:
    """Main entry point."""
    args = parse_args()
    phd2host, phd2port, port, rms_samples = get_config(args)

    state = get_state()
    state.phd_rms_samples = rms_samples

    # Start up the server to expose the metrics.
    metrics_utility.metrics(port)

    run_exporter_loop(phd2host, phd2port)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
