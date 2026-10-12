# phd2-exporter
Uses PHD2 event monitoring to export metrics.

# Setup

PHD2 needs no configuration. It serves events on port 4400; subsequent instances use 4401, 4402, etc.

## Install

Requires Python 3.10+ and git.

```shell
python -m pip install git+https://github.com/jewzaam/phd2-exporter.git
```

Or from a local clone: `python -m pip install .`

This installs a `phd2-exporter` command (on Windows, `phd2-exporter.exe` in Python's `Scripts\` directory).

## Usage

```shell
phd2-exporter
```

If `Scripts\` is not on `PATH`, use `python -m phd2_exporter.main`.

| Flag | Default | Description |
|------|---------|-------------|
| `--phd2host` | `127.0.0.1` | Host PHD2 is serving events on |
| `--phd2port` | `4400` | Port PHD2 is serving events on |
| `--port` | `9753` | Port to export metrics on |
| `--rms_samples` | `10` | Number of samples used to calculate RMS |

## Verify

Open http://localhost:9753 in a browser.

# Metrics

* `phd2_connected` - only true if all configured equipment is connected
* `phd2_current_equipment` - device is 'camera', 'mount', etc and value indicates which device is connected (or not)
