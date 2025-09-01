# CHC ABS Classifier

Community Health Centre geocoding and Australian Bureau of Statistics (ABS) statistical area classification system.

## Overview

This tool geocodes Community Health Centre (CHC) locations in the Northern Territory, Australia and classifies them into Australian Statistical Geography Standard (ASGS) areas including SA1, SA2, SA3, SA4, GCCSA, State/Territory boundaries, and Indigenous Areas (IARE).

## Quick Start

1. **Setup environment and install dependencies:**
   ```bash
   uv venv && uv pip install -e ".[dev]"
   ```

2. **Run with TKC localities:**
   ```bash
   uv run python -m src.app --input-csv data/input/tkc-localities.txt --output-csv outputs/tkc-classified.csv
   ```

3. **Check results:**
   ```bash
   cat outputs/tkc-classified.csv
   ```

## Features

- **Geocoding**: Nominatim API with rate limiting and retry logic
- **ABS Classification**: Complete statistical hierarchy from SA1 boundaries
- **Indigenous Areas**: IARE classification for Indigenous communities
- **Smart Caching**: Skip already processed locations, add `--rebuild` to force refresh
- **Modern CLI**: Rich terminal interface with progress indicators
- **Robust**: Comprehensive error handling and testing

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Dependencies

```bash
uv pip install -e ".[dev]"
```

Core dependencies: pandas, geopandas, geopy, typer, rich

## Usage

### Command Line Interface

Basic usage:
```bash
uv run python -m src.app
```

With custom input/output:
```bash
uv run python -m src.app --input-csv data/my-localities.txt --output-csv results/output.csv
```

Skip ABS classification (geocoding only):
```bash
uv run python -m src.app --skip-classification
```

Force rebuild (ignore cache):
```bash
uv run python -m src.app --input-csv data/input/tkc-localities.txt --rebuild
```

Create sample input file:
```bash
uv run python -m src.app --create-sample --input-csv data/my_sample.csv
```

### Configuration

Optional `.env` file configuration:

```bash
NOMINATIM_USER_AGENT=my_geocoder_app
GEOCODE_MIN_DELAY_SEC=1.0
ASGS_SA1_PATH=data/asgs/SA1_2021_AUST_SHP_GDA2020/SA1_2021_AUST_GDA2020.shp
ASGS_IARE_PATH=data/asgs/IARE_2021_AUST_GDA2020_SHP/IARE_2021_AUST_GDA2020.shp
```

### Check Configuration

```bash
uv run python -m src.app info
```

## Data Requirements

### Input Format

**Simple text file** with locality names (one per line):
```
ALI CURUNG
CANTEEN CREEK  
ELLIOTT
TENNANT CREEK
ALICE SPRINGS
```

Or **CSV file** with CHC column:
```csv
CHC
Adelaide River CHC, NT, Australia
Ali Curung CHC, NT, Australia
```

The app automatically converts raw locality names to qualified format (adds "NT, Australia").

### ASGS Boundary Data

**Required**: Download SA1 boundaries (~200MB) from ABS as it contains all hierarchical statistical area data.

Download: [SA1_2021_AUST_SHP_GDA2020.zip](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/SA1_2021_AUST_SHP_GDA2020.zip)

**Optional**: Download Indigenous Areas (IARE) boundaries for Indigenous communities classification.

Download: [IARE_2021_AUST_GDA2020_SHP.zip](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/IARE_2021_AUST_GDA2020_SHP.zip)

Extract both to `data/asgs/` directory:
```
data/asgs/
├── SA1_2021_AUST_SHP_GDA2020/
│   ├── SA1_2021_AUST_GDA2020.shp
│   ├── SA1_2021_AUST_GDA2020.dbf
│   ├── SA1_2021_AUST_GDA2020.prj
│   └── SA1_2021_AUST_GDA2020.shx
└── IARE_2021_AUST_GDA2020_SHP/
    ├── IARE_2021_AUST_GDA2020.shp
    ├── IARE_2021_AUST_GDA2020.dbf
    ├── IARE_2021_AUST_GDA2020.prj
    └── IARE_2021_AUST_GDA2020.shx
```

## Output

CSV with geocoded coordinates and complete ABS statistical hierarchy:

- **CHC**: Original location name
- **Latitude**, **Longitude**: Geocoded coordinates  
- **Address**: Full address from geocoding
- **SA1**: Statistical Area Level 1 code
- **SA2_CODE**, **SA2_NAME**: Statistical Area Level 2
- **SA3_NAME**, **SA4_NAME**: Statistical Area Levels 3-4
- **GCCSA_NAME**: Greater Capital City Statistical Area
- **STATE_NAME**: State/Territory
- **IARE_CODE**, **IARE_NAME**: Indigenous Area classification
- **IREG_CODE**, **IREG_NAME**: Indigenous Region classification

## Development

### Code Quality

Run linting:
```bash
uv run ruff check src/ tests/
```

Format code:
```bash
uv run ruff format src/ tests/
```

Run all quality checks:
```bash
uv run ruff check src/ tests/ && uv run pytest tests/
```

### Testing

Run tests:
```bash
uv run pytest tests/ -v
```

Run tests with coverage:
```bash
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Project Structure

```
├── src/
│   ├── app.py          # Main CLI application
│   ├── geocode.py      # Geocoding functionality
│   ├── classify.py     # ABS classification
│   ├── io_utils.py     # File I/O utilities
│   └── settings.py     # Configuration management
├── data/
│   ├── input/          # Input CSV files
│   └── asgs/           # ASGS boundary files
├── outputs/            # Generated results
├── tests/              # Unit tests
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

## Performance

- **Geocoding Success**: ≥80% of locations successfully geocoded
- **Rate Limiting**: Respects Nominatim Usage Policy (≤1 req/sec)
- **Classification**: 100% success for valid coordinates using hierarchical SA1 data

## Troubleshooting

- **No geocoding results**: Check internet connectivity and location name accuracy
- **Missing classifications**: Download SA1 boundaries to `data/asgs/`
- **Missing Indigenous Areas**: Download IARE boundaries to `data/asgs/` for Indigenous classification
- **Import errors**: Run `uv pip install -e ".[dev]"` and use `uv run` prefix

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `uv run ruff check src/ tests/ && uv run pytest tests/` to verify code quality
5. Submit a pull request