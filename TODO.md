# PHD2 Exporter - TODOs and Future Enhancements

## Completed ✅

- [x] GitHub workflows for CI/CD (test, lint, coverage)
- [x] Makefile with modular structure
- [x] Unit tests with 81% coverage (exceeds 80% target)
- [x] Documentation (requirements.md, test_plan.md)
- [x] Code restructuring into proper Python package
- [x] Linting and formatting setup (ruff, mypy)
- [x] pyproject.toml configuration
- [x] Development dependencies setup

## Current Coverage: 81%

Coverage breakdown by module:
- `src/phd2_exporter/__init__.py`: 100%
- `src/phd2_exporter/state.py`: 100%
- `src/phd2_exporter/utils.py`: 100%
- `src/phd2_exporter/rms.py`: 100%
- `src/phd2_exporter/jsonrpc.py`: 99%
- `src/phd2_exporter/events.py`: 94%
- `src/phd2_exporter/main.py`: 32% (low due to main loop being difficult to unit test)

## Future Enhancements

### Testing
- [ ] Integration tests with PHD2 mock/simulator
- [ ] Increase main.py coverage (requires mocking socket operations)
- [ ] Performance/stress tests for high event rates
- [ ] Thread safety tests

### Features
- [ ] Configuration file support (YAML/TOML)
- [ ] Additional metrics (rates, histograms)
- [ ] Grafana dashboard examples
- [ ] Docker container
- [ ] Prometheus alerting examples

### Documentation
- [ ] User guide with examples
- [ ] Grafana dashboard setup guide
- [ ] Troubleshooting guide
- [ ] API documentation

### Quality
- [ ] Mutation testing
- [ ] Security audit
- [ ] Performance profiling
- [ ] Memory leak testing

## Notes

The main.py file has lower coverage (32%) because the main event loop is difficult to unit test without extensive mocking of socket operations. This is acceptable for now, as the core business logic (events, jsonrpc, rms, state, utils) all have excellent coverage (94-100%).

Future work could focus on integration tests that actually connect to a PHD2 instance or simulator to improve main.py coverage.

