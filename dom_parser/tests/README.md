# DOM Parser Tests

This directory contains various test suites for the DOM Parser project.

## Test Structure

- **`playground/`** - Integration tests for real websites (Google, Amazon, YouTube, etc.)
- **`replay_tests/`** - Golden value tests for regression testing
- **`test_*.py`** - Unit tests for individual components

## Running Tests

### Prerequisites

1. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Set PYTHONPATH:**
   ```bash
   export PYTHONPATH=/Users/rachitapradeep/dom-parser:$PYTHONPATH
   ```

### Basic Test Execution

#### Unit Tests
```bash
# Run all unit tests
pytest dom_parser/tests/test_*.py -v

# Run specific unit test
pytest dom_parser/tests/test_idle_watcher.py -v
```

#### Integration Tests (Playground)
```bash
# Run all playground tests
pytest dom_parser/tests/playground/test_*.py -v

# Run specific integration test
pytest dom_parser/tests/playground/test_page_analyzer_integration_google.py -v
```

#### Golden Value Tests
```bash
# Run golden value tests
PYTHONPATH=. pytest dom_parser/tests/replay_tests/test_golden_replay.py -v
```

### Direct Python Execution

You can also run tests directly with Python:

```bash
# Run specific integration test
python dom_parser/tests/playground/test_page_analyzer_integration_google.py

# Run golden value generation
python dom_parser/tests/replay_tests/golden_values/generate_golden_example_com.py
```

## Streaming Logs to Text Files

### Method 1: Using pytest with output redirection

```bash
# Run test and save all output to file
pytest dom_parser/tests/playground/test_page_analyzer_integration_google.py -v -s > /tmp/test_output.txt 2>&1

# Run with more verbose output
pytest dom_parser/tests/playground/test_page_analyzer_integration_google.py -v -s --tb=long > /tmp/detailed_output.txt 2>&1
```

### Method 2: Using Python with output redirection

```bash
# Run Python test and save output
python dom_parser/tests/playground/test_page_analyzer_integration_google.py > /tmp/python_test_output.txt 2>&1

# Run with timestamp
python dom_parser/tests/playground/test_page_analyzer_integration_google.py | tee /tmp/test_$(date +%Y%m%d_%H%M%S).txt
```

### Method 3: Using pytest with log file

```bash
# Run with pytest logging
pytest dom_parser/tests/playground/test_page_analyzer_integration_google.py -v -s --log-file=/tmp/pytest.log --log-level=DEBUG
```

## Test Categories

### 1. Playground Tests (Integration)
These tests interact with real websites:

- **`test_page_analyzer_integration_google.py`** - Google search functionality
- **`test_page_analyzer_integration_amazon.py`** - Amazon product search
- **`test_page_analyzer_integration_youtube.py`** - YouTube navigation
- **`test_page_analyzer_integration_pinterest.py`** - Pinterest browsing
- **`test_page_analyzer_integration_airbnb.py`** - Airbnb search
- **`test_page_analyzer_integration_google_flights.py`** - Google Flights search
- **`test_page_analyzer_integration_google_forms.py`** - Google Forms interaction
- **`test_page_analyzer_integration_new_balance.py`** - New Balance website
- **`test_page_analyzer_integration_ny_times.py`** - New York Times website
- **`test_page_analyzer_integration_screenshot.py`** - Screenshot functionality

### 2. Replay Tests (Regression)
These tests compare against golden values:

- **`test_golden_replay.py`** - Compares parsed output against saved golden files
- **`generate_golden_example_com.py`** - Generates new golden files for comparison

### 3. Unit Tests
These test individual components:

- **`test_action_executor.py`** - Action execution functionality
- **`test_action_executor_config.py`** - Action executor configuration
- **`test_dom_parser_args.py`** - DOM parser argument handling
- **`test_forms.py`** - Form detection and handling
- **`test_idle_watcher.py`** - Page idle detection
- **`test_integration.py`** - Basic integration tests
- **`test_parser.py`** - Core parsing functionality

## Useful pytest Options

```bash
# Verbose output
-v

# Show print statements
-s

# Show local variables in tracebacks
-l

# Stop on first failure
-x

# Run tests in parallel (requires pytest-xdist)
-n auto

# Generate coverage report
--cov=dom_parser

# Show slowest tests
--durations=10
```

## Debugging Tests

### Enable Debug Logging
```bash
# Set debug environment variable
export DEBUG=pw:api

# Run test with debug output
pytest dom_parser/tests/playground/test_page_analyzer_integration_google.py -v -s
```

### View Screenshots
Integration tests save screenshots to `/tmp/`:
```bash
# List screenshots
ls -la /tmp/*.png

# Open latest screenshot
open /tmp/01_after_navigation.png
```

### Check Test Results
```bash
# View test output
cat /tmp/test_output.txt

# Search for errors
grep -i error /tmp/test_output.txt

# Search for warnings
grep -i warning /tmp/test_output.txt
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure PYTHONPATH is set correctly
2. **Browser Issues**: Tests use non-headless mode by default; ensure display is available
3. **Network Issues**: Integration tests require internet connection
4. **Permission Issues**: Ensure write permissions for `/tmp/` directory

### Reset Test Environment
```bash
# Clear temporary files
rm -f /tmp/*.png /tmp/test_*.txt

# Clear pytest cache
pytest --cache-clear
```

## Contributing

When adding new tests:

1. Follow the naming convention: `test_*.py`
2. Use descriptive test names
3. Add appropriate docstrings
4. Include screenshots for integration tests
5. Update this README if adding new test categories
