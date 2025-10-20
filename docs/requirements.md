# PHD2 Exporter Requirements

## Overview

PHD2 Exporter is a Prometheus metrics exporter for PHD2 guiding data. It connects to PHD2's event monitoring interface and exports guiding metrics for monitoring and analysis.

## Functional Requirements

### Core Functionality

1. **PHD2 Connection**
   - Connect to PHD2 event monitoring port (default: 4400)
   - Maintain persistent connection with automatic reconnection on failure
   - Support configurable host and port

2. **Metrics Export**
   - Export metrics via Prometheus HTTP endpoint
   - Support configurable metrics port (default: 9753)
   - Provide standard Prometheus text format

3. **Event Handling**
   - Parse PHD2 JSONRPC events
   - Track application state (Stopped, Selected, Calibrating, Guiding, LostLock, Paused, Looping, Settling)
   - Calculate RMS metrics from guide steps
   - Handle calibration events
   - Track equipment connection status

4. **Metrics**
   - `phd2_connected` - Equipment connection status
   - `phd2_current_equipment` - Device connection states (camera, mount, etc.)
   - `phd2_status` - Application state indicator
   - `phd2_pixel_scale` - Camera pixel scale
   - `phd2_rms` - RMS error metrics (RA/DEC, Raw/Guide, px/arcsec)
   - Event-specific metrics for GuideStep, Calibrating, Settling, etc.
   - Error counters

## Non-Functional Requirements

### Performance

- Minimal latency in metrics updates
- Efficient memory usage for RMS calculation
- Handle PHD2 event rates without backpressure

### Reliability

- Automatic reconnection on connection failure
- Graceful handling of malformed events
- No data loss on transient errors

### Maintainability

- Modular, testable code structure
- Comprehensive unit test coverage (target: 80%+)
- Type hints for Python 3.10+
- Code formatting with ruff
- Linting with ruff and mypy

### Compatibility

- Python 3.10, 3.11, 3.12
- PHD2 event monitoring protocol
- Prometheus text exposition format

## Configuration

### Command Line Arguments

- `--phd2host` - PHD2 host (default: 127.0.0.1)
- `--phd2port` - PHD2 port (default: 4400)
- `--port` - Metrics export port (default: 9753)
- `--rms_samples` - Number of samples for RMS calculation (default: 10)

## Dependencies

### Runtime Dependencies

- `metrics-utility` - Prometheus metrics library
- Python standard library (argparse, socket, json, time, threading, math, random, copy)

### Development Dependencies

- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `mypy` - Type checking
- `ruff` - Linting and formatting

## Testing Requirements

### Unit Tests

- Event parsing and handling
- State management
- RMS calculation
- Label generation
- JSONRPC callback handling
- Metric creation

### Integration Tests

- (Future) End-to-end connection tests
- (Future) Prometheus scrape validation

### Coverage Target

- Minimum: 80%
- Goal: 90%+

## Build and Development

### Make Targets

- `make help` - Display available targets
- `make venv` - Create virtual environment
- `make requirements` - Install runtime dependencies
- `make requirements-dev` - Install dev dependencies
- `make test` - Run unit tests
- `make lint` - Run linting and type checking
- `make format` - Format code
- `make coverage` - Run tests with coverage report
- `make clean` - Remove temporary files

### CI/CD

- GitHub Actions workflows for:
  - Test (Python 3.10, 3.11, 3.12)
  - Lint
  - Coverage

## Future Enhancements

- Configuration file support
- Additional metrics (total counts, rates)
- Grafana dashboard examples
- Docker container
- Integration tests with PHD2 simulator


