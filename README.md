# phd2-exporter
Uses PHD2 event monitoring to export metrics.

# Setup

Nothing to do, just fire up PHD2.  It serves traffic on port 4400.  Subsequent instances are on a 4401, 4402, etc.

## Usage

Simply run the exporter with a port and the config you've created / edited

```shell
python src\phd2-exporter.py --port 8012
```

Optional arguments are document in `--help`.

## Verify

In your favorite browser look at the metrics endpoint.  If it's local, you can use http://localhost:8012
