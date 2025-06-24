# ProdWatch

A faster, safer way to log and debug live code.

## Installation & Setup

You can install `prodwatch` using pip:

```bash
pip install prodwatch
```

### Prerequisites

- Python >= 3.13.
- A live monitoring server (host your own, or use [ours](https://getprodwatch.com)).
- Environment variables:
  - `PRODWATCH_API_TOKEN`: Authentication for the monitoring server.
  - `PRODWATCH_API_URL`: Base URL (optional) for the monitoring server (yours or [ours](https://getprodwatch.com)).

### Basic Usage

```python
from prodwatch import start_prodwatch

# Your application code
def some_function(a, b):
    return a + b

if __name__ == "__main__":
    start_prodwatch()

    # Hover over this function in your editor, and click to turn on logging.
    # ProdWatch will start logging these function calls immediately.
    # Wait a few moments, and you'll start seeing logs.
    # No added logging code, no config changes, no deploy required!
    some_function(4, 2)
```

## Configuration

### Environment Variables

#### Required for ProdWatch Operation

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PRODWATCH_API_TOKEN` | Authentication token for monitoring server | None | Yes |
| `PRODWATCH_API_URL` | Base URL of monitoring server | https://getprodwatch.com | No |

#### Optional for ProdWatch Internal Logging

These control how ProdWatch logs its own behavior (not your application's logs):

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PRODWATCH_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO | No |
| `PRODWATCH_LOG_FORMAT` | Log output format (text, json) | text | No |
| `PRODWATCH_LOG_FILE` | Path to log file (enables file logging) | None | No |

### ProdWatch Internal Logging Configuration

You can configure logging for ProdWatch itself (as mentioned above, this is not to be confused with the logging ProdWatch does for _your_ code).

#### Configuration Files
Place a `prodwatch_logging.json` file in your project root for custom logging setup:

```json
{
  "version": 1,
  "formatters": {
    "standard": {
      "format": "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
    },
    "json": {
      "()": "prodwatch.logging_config.StructuredFormatter"
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "formatter": "standard"
    },
    "file": {
      "class": "logging.handlers.RotatingFileHandler",
      "filename": "prodwatch.log",
      "formatter": "json",
      "maxBytes": 10485760,
      "backupCount": 5
    }
  },
  "loggers": {
    "prodwatch": {
      "level": "DEBUG",
      "handlers": ["console", "file"]
    }
  }
}
```

#### Environment-Based Configuration
- `PRODWATCH_LOG_FORMAT=json` enables JSON structured logging
- `PRODWATCH_LOG_FILE=app.log` enables file logging with rotation

### Server Endpoints

The monitoring server should implement the following endpoints:

- `GET /pending-function-names?process_id={id}`: Returns list of functions to monitor.
- `POST /events`: Receives monitoring events (process registration, function calls, confirmations).

## API Reference

### Just One Function!

#### `start_prodwatch()`
Initializes and starts ProdWatch.

**Behavior:**
- Creates Manager instance with monitoring server URL
- Checks server connection
- Starts polling loop in a background thread
- Listens for requests (from VS Code) to monitor specific functions.
- Sends function-call data to the monitoring server.

### Exception Classes

#### `ProdwatchError`
Base exception for all Prodwatch-related errors.

#### `TokenError`
Raised when API token is missing or invalid.

