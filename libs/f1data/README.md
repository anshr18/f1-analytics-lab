# F1 Data Clients

Shared library for accessing F1 data from multiple sources.

## Data Sources

- **FastF1**: Primary source for lap timing, telemetry, and historical data
- **OpenF1**: Real-time data and live streaming
- **Jolpica**: Historical race metadata (Ergast API replacement)

## Usage

```python
from f1data.clients import FastF1Client
from f1data.parsers import FastF1Parser

# Initialize client
client = FastF1Client(cache_dir="/path/to/cache")

# Load session
session = client.get_session(2024, 1, "Race")

# Parse data
parser = FastF1Parser()
laps = parser.parse_laps(session)
stints = parser.parse_stints(session)
```

## Installation

```bash
cd libs/f1data
uv pip install -e ".[dev]"
```
