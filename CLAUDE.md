# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Python-based Community Health Centre (CHC) geocoding and Australian Bureau of Statistics (ABS) classification system. The application converts CHC locations in the Northern Territory, Australia to coordinates and classifies them into statistical areas.

## Running the Application

### Modern CLI Interface

Run the main application:
```bash
uv run python -m src.app
```

Run with custom input/output:
```bash
uv run python -m src.app --input-csv data/input/locations.csv --output-csv outputs/results.csv
```

Check system configuration:
```bash
uv run python -m src.app info
```

### Development Commands

Common development tasks:
```bash
uv pip install -e ".[dev]"              # Install dependencies
uv run pytest tests/ -v                 # Run test suite
uv run ruff check src/ tests/           # Run code linting with ruff
uv run ruff format src/ tests/          # Auto-format code
uv run ruff check src/ tests/ && uv run pytest tests/  # Run all quality checks
rm -rf build/ dist/ *.egg-info/         # Clean up generated files
```

## Dependencies and Environment

### Setup Environment
```bash
uv venv && uv pip install -e ".[dev]"
```

### Key Dependencies
- **Core processing**: pandas, geopandas, shapely, pyproj, fiona
- **Geocoding**: geopy (Nominatim API with rate limiting)
- **CLI interface**: typer, rich (for beautiful terminal output)
- **Configuration**: python-dotenv
- **Development**: pytest, ruff

## Code Architecture

This is a modular Python package with the following structure:

### Core Modules

- **`src/app.py`**: Modern CLI application using typer with rich progress indicators
- **`src/geocode.py`**: Geocoding functionality with retry logic and rate limiting
- **`src/classify.py`**: ABS statistical area classification using spatial joins
- **`src/io_utils.py`**: File I/O utilities with validation and error handling
- **`src/settings.py`**: Configuration management with environment variable support

### Data Flow

1. **Input**: CSV file with CHC locations (`data/input/locations.csv`)
2. **Geocoding**: Nominatim API with CHC token normalization and fallback
3. **Classification**: Spatial joins with ASGS boundary data (SA1-SA4, GCCSA, STE)
4. **Output**: Enhanced CSV with coordinates and statistical area classifications

### Testing

Comprehensive test suite with:
- Unit tests for all modules (`tests/test_*.py`)
- Mocked external API calls
- Synthetic geometry testing for spatial operations
- File I/O validation testing

## Configuration

### Environment Variables

Configure via `.env` file or environment:
```bash
NOMINATIM_USER_AGENT=chc_geocoder
GEOCODE_MIN_DELAY_SEC=1.0
ASGS_SA1_PATH=data/asgs/SA1_2021_AUST_GDA2020.gpkg
# ... additional ASGS file paths
```

### ASGS Boundary Data

For full ABS classification, place ASGS 2021 boundary files in `data/asgs/`:
- SA1, SA2, SA3, SA4 statistical areas
- GCCSA (Greater Capital City Statistical Areas) 
- STE (State/Territory) boundaries

Download from: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files

## Key Features

- **Rate limiting**: Respects Nominatim ToS (1 req/sec)
- **Retry logic**: Exponential backoff for API failures
- **CRS handling**: Automatic coordinate system transformations
- **Progress indicators**: Rich terminal UI with real-time progress
- **Validation**: Quality checks for geocoding success rates
- **Error handling**: Graceful degradation when ASGS files unavailable

## Code Quality Standards

- **Linting**: ruff with line-length=100
- **Testing**: pytest with coverage reporting
- **Type hints**: Throughout codebase
- **Documentation**: Comprehensive docstrings
- **Error handling**: Structured logging and user-friendly messages

## Development Workflow

1. Create virtual environment: `uv venv`
2. Install dependencies: `uv pip install -e ".[dev]"`
3. Make code changes
4. Run tests: `uv run pytest tests/ -v`
5. Check code quality: `uv run ruff check src/ tests/ && uv run pytest tests/`
6. Run application: `uv run python -m src.app`

This modular architecture provides better maintainability, testing, and extensibility compared to the original monolithic approach.