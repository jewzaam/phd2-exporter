# PHD2 Exporter Test Plan

## Test Strategy

This document outlines the comprehensive test plan for the PHD2 Exporter project. The testing strategy focuses on unit tests with a target of 80%+ code coverage.

## Test Coverage Goals

| Component | Coverage Target | Priority |
|-----------|----------------|----------|
| Event Handling | 90%+ | High |
| State Management | 90%+ | High |
| RMS Calculation | 95%+ | High |
| Label Generation | 85%+ | Medium |
| JSONRPC Handling | 85%+ | Medium |
| Utility Functions | 80%+ | Medium |
| Main Loop | 70%+ | Low (integration-heavy) |

## Unit Tests

### Event Handling Tests

**Module:** `test_event_handling.py`

1. **test_handle_version_event**
   - Verify GLOBAL_LABELS initialization
   - Validate host lowercasing
   - Check instance ID handling

2. **test_handle_app_state_event**
   - Test state transitions
   - Verify status metric updates
   - Check settling state reset

3. **test_handle_loop_events**
   - Test LoopingExposures state change
   - Test LoopingExposuresStopped state change
   - Verify RMS data reset

4. **test_handle_calibration_events**
   - Test StartCalibration state change
   - Test Calibrating event with labels
   - Verify calibration metrics

5. **test_handle_guide_step_event**
   - Test state change to Guiding
   - Verify all GuideStep metrics
   - Test RMS data collection
   - Test RMS calculation trigger

6. **test_handle_lock_position_events**
   - Test LockPositionSet state and metrics
   - Test StarSelected metrics

7. **test_handle_settling_events**
   - Test SettleBegin state change
   - Test Settling metrics
   - Test SettleDone metrics and state

8. **test_handle_star_lost_event**
   - Test state change to LostLock
   - Verify error metrics

9. **test_handle_dither_event**
   - Test GuidingDithered metrics

10. **test_handle_unknown_event**
    - Verify graceful handling of unknown events

### State Management Tests

**Module:** `test_state_management.py`

1. **test_initial_state**
   - Verify empty initial state

2. **test_state_transitions**
   - Test all valid state transitions
   - Verify state persistence

3. **test_status_metrics**
   - Test status metric for each state
   - Verify only one state active at a time
   - Test settling as additional state

4. **test_rms_data_reset**
   - Verify RMS data cleared on stop
   - Test RMS data persistence during guiding

### RMS Calculation Tests

**Module:** `test_rms_calculation.py`

1. **test_rms_data_collection**
   - Test data append to RMS arrays
   - Test array size limiting
   - Test skipping during settling

2. **test_rms_calculation_insufficient_data**
   - Verify no calculation with < N samples

3. **test_rms_calculation_exact_samples**
   - Test calculation with exactly N samples
   - Verify math correctness

4. **test_rms_calculation_with_pixel_scale**
   - Test arcsec conversion
   - Verify both px and arcsec metrics

5. **test_rms_total_distance**
   - Test hypotenuse calculation
   - Verify Raw and Guide totals

6. **test_rms_metric_export**
   - Verify all RMS metrics exported
   - Test label structure

### Label Generation Tests

**Module:** `test_label_generation.py`

1. **test_make_labels_all_present**
   - Test with all labels in data

2. **test_make_labels_missing_keys**
   - Test default value (0) for missing keys

3. **test_make_labels_empty_keys**
   - Test with no keys requested

4. **test_global_labels**
   - Test GLOBAL_LABELS structure
   - Verify host lowercasing

5. **test_label_copying**
   - Verify deep copy prevents mutation

### JSONRPC Handling Tests

**Module:** `test_jsonrpc.py`

1. **test_random_request_id**
   - Test ID uniqueness
   - Test ID range (1-50000)
   - Test thread safety (mutex)

2. **test_callback_registration**
   - Test callback storage
   - Test callback cleanup

3. **test_pixel_scale_request**
   - Test request format
   - Test callback handling

4. **test_connected_request**
   - Test request format
   - Test callback handling

5. **test_current_equipment_request**
   - Test request format
   - Test response parsing
   - Test device metrics

### Utility Function Tests

**Module:** `test_utilities.py`

1. **test_utility_set_success**
   - Test successful metric set

2. **test_utility_set_error**
   - Test error handling and logging

3. **test_utility_inc_success**
   - Test successful metric increment

4. **test_utility_inc_error**
   - Test error handling and logging

5. **test_debug_enabled**
   - Test debug output when enabled

6. **test_debug_disabled**
   - Test no output when disabled

### Metric Creation Tests

**Module:** `test_metrics.py`

1. **test_create_event_metrics**
   - Test metric creation for various keys
   - Test boolean conversion (True=1, False=0)
   - Test missing keys

2. **test_event_counter_increment**
   - Test event counter increments
   - Verify labels

3. **test_error_counter_increment**
   - Test error type tracking

## Integration Tests (Future)

### End-to-End Tests

1. **test_phd2_connection**
   - Test connection to PHD2 mock
   - Test reconnection logic
   - Test timeout handling

2. **test_metrics_export**
   - Test Prometheus endpoint
   - Verify metric format
   - Test scraping

3. **test_full_guiding_session**
   - Simulate complete guiding session
   - Verify all metrics updated correctly

## Test Execution

### Running Tests

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run with coverage
make coverage

# Run specific test file
make test ARGS="tests/unit/test_event_handling.py"

# Run specific test
make test ARGS="tests/unit/test_event_handling.py::test_handle_version_event"
```

### Coverage Reporting

```bash
# Generate coverage report
make coverage-report

# View HTML coverage report
open htmlcov/index.html

# Check coverage threshold
make coverage-verify
```

## Test Data

### Sample Events

Test data should include realistic PHD2 events:

- Version event with host and instance
- AppState with various states
- GuideStep with all fields
- Calibrating events
- Settling events
- StarLost events
- Equipment change events

### Edge Cases

- Malformed JSON
- Missing fields
- Unexpected data types
- Very large/small numeric values
- Empty strings
- Null values

## Continuous Integration

### GitHub Actions

- Run tests on Python 3.10, 3.11, 3.12
- Run lint checks
- Generate and upload coverage reports
- Fail on lint errors
- Report coverage but don't fail on threshold (warning only)

## Test Maintenance

### Adding New Tests

1. Create test file in appropriate directory
2. Follow naming convention: `test_*.py`
3. Use descriptive test names
4. Include docstrings
5. Update this test plan

### Updating Tests

1. Keep tests synchronized with code changes
2. Update test data for new fields
3. Maintain coverage targets
4. Document any coverage exceptions

## Known Limitations

1. Main loop is difficult to unit test (requires mocking socket)
2. Thread safety testing requires complex setup
3. Timing-dependent tests may be flaky
4. External dependency (metrics-utility) not mocked

## Future Test Enhancements

1. Add integration tests with PHD2 simulator
2. Add performance tests
3. Add stress tests (high event rates)
4. Add thread safety tests
5. Mock metrics-utility for pure unit tests
6. Add mutation testing


