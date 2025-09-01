# IARE (Indigenous Areas) Classification Feature Implementation

## Overview

Successfully added IARE (Indigenous Areas) classification as a new spatial classification method to the CHC geocoding system. This feature enables the classification of Community Health Centre locations into Indigenous statistical areas alongside the existing ABS Statistical Areas (SA1-SA4, GCCSA, STE) classification.

## Original Task Request

**User Request**: "i want to add a new feature. IARE @data/asgs/IARE_2021_AUST_GDA2020_SHP/README.md has another set shapefiles, allowing classification into IARE region. can you look at adding this as another spaitial classification to the existing methods."

## Implementation Assessment

### IARE Data Analysis
- **Source**: `data/asgs/IARE_2021_AUST_GDA2020_SHP/IARE_2021_AUST_GDA2020.shp`
- **Coverage**: 431 Indigenous Areas across Australia (64 in Northern Territory across 9 Indigenous Regions)
- **Key Fields**:
  - `IAR_CODE21`: IARE identifier (6-digit codes like "703001")
  - `IAR_NAME21`: IARE names (e.g., "Darwin - Inner Suburbs")
  - `IRE_CODE21`: Indigenous Region codes (3-digit like "703")
  - `IRE_NAME21`: Indigenous Region names (e.g., "Darwin")
- **CRS**: EPSG:7844 (GDA2020)
- **Hierarchical Structure**: Australia → State/Territory → Indigenous Region → Indigenous Area

### System Integration Strategy
The implementation follows the existing modular architecture pattern:
- **Configuration**: Extended `settings.py` with IARE path management
- **Classification Logic**: Enhanced `classify.py` with spatial join functionality
- **Workflow Integration**: Leveraged existing `app.py` ASGS file handling
- **Testing**: Added comprehensive test coverage

## Technical Implementation

### 1. Settings Configuration (`src/settings.py`)
- Added `asgs_iare_path: Path | None = None` to Settings dataclass
- Extended `from_env()` method with `ASGS_IARE_PATH` environment variable support
- Updated `get_asgs_paths()` to include IARE in file path dictionary
- Enhanced `set_default_asgs_paths()` with multi-format IARE file detection:
  - GeoPackage: `IARE_2021_AUST_GDA2020.gpkg`
  - Shapefile in subdirectory: `IARE_2021_AUST_GDA2020_SHP/IARE_2021_AUST_GDA2020.shp`
  - Loose shapefile: `IARE_2021_AUST_GDA2020.shp`

### 2. Classification Logic (`src/classify.py`)
- Extended ABS columns list with IARE fields: `["IARE_CODE", "IARE_NAME", "IREG_CODE", "IREG_NAME"]`
- Added IARE classification section after SA1 hierarchical processing:
  - Loads IARE boundaries using existing `load_layer()` function
  - Handles CRS transformation from EPSG:7844 (GDA2020) to EPSG:4326
  - Performs spatial join with geocoded points
  - Maps IARE columns to standardized output format
- Updated `get_classification_summary()` to include IARE columns in success metrics

### 3. Application Workflow (`src/app.py`)
- No changes required - automatically handles IARE through existing `settings.get_asgs_paths()` pattern
- IARE files detected and displayed in `info` command status table

### 4. Comprehensive Test Suite (`tests/test_classify.py`)
Added extensive test coverage:
- **IARE Classification Success**: Tests successful IARE boundary loading, CRS transformation, and point classification
- **IARE Files Not Available**: Tests graceful degradation when IARE files are missing
- **Classification Summary with IARE**: Tests summary statistics including IARE data
- **Mock Data Integration**: Uses realistic Darwin/NT geographic coordinates and IARE codes

## Testing Results

### Test Coverage
```
tests/test_classify.py::TestClassifyPoints::test_classify_points_iare_success PASSED
tests/test_classify.py::TestClassifyPoints::test_classify_points_no_iare_files PASSED  
tests/test_classify.py::TestGetClassificationSummary::test_get_classification_summary_with_iare PASSED
```

### Live Application Test
Tested with 5 NT CHC locations:
- **Ali Curung**: IARE "707001 Ali Curung" in Region "707 Tennant Creek"
- **Alice Springs**: IARE "708001 Alice exc. Town Camps" in Region "708 Alice Springs"  
- **Darwin**: IARE "703005 Darwin - Inner Suburbs" in Region "703 Darwin"
- **Katherine**: IARE "705005 Katherine Town" in Region "705 Katherine"
- **Tennant Creek**: IARE "707005 Tennant Creek Town" in Region "707 Tennant Creek"

### Output Verification
The enhanced CSV output now includes 4 additional columns:
```csv
CHC,Latitude,Longitude,Address,SA1,SA2_CODE,SA2_NAME,SA3_NAME,SA4_NAME,GCCSA_NAME,STATE_NAME,IARE_CODE,IARE_NAME,IREG_CODE,IREG_NAME
DARWIN,-12.46044,130.8410469,"Darwin, City of Darwin, Northern Territory, 0800, Australia",70101100228,701011002,Darwin City,Darwin City,Darwin,Greater Darwin,Northern Territory,703005,Darwin - Inner Suburbs,703,Darwin
```

## Key Technical Features

### CRS Handling
- **Automatic Transformation**: IARE boundaries (EPSG:7844) automatically transformed to system default (EPSG:4326)
- **CRS Compatibility**: Seamless integration with existing coordinate system workflow

### Performance Considerations
- **Spatial Efficiency**: Uses optimized spatial joins with proper indexing
- **Memory Management**: Processes only required columns to minimize memory usage
- **NT Optimization**: Framework ready for NT-specific filtering if performance optimization needed

### Error Handling
- **Graceful Degradation**: IARE classification fails gracefully if files unavailable
- **Logging Integration**: Comprehensive logging of IARE processing steps
- **Validation**: Maintains existing data quality validation standards

### File Format Support
- **Multi-format Detection**: Supports GeoPackage (.gpkg) and Shapefile (.shp) formats
- **Flexible Path Management**: Handles various directory structures (subdirectories, loose files)
- **Environment Configuration**: Configurable via `ASGS_IARE_PATH` environment variable

## Validation and Quality Assurance

### Code Quality
- **Linting**: All code passes ruff linting with 100-character line limit
- **Type Hints**: Comprehensive type annotations throughout implementation
- **Documentation**: Detailed docstrings and inline comments
- **Error Handling**: Structured exception handling with user-friendly messages

### Integration Testing  
- **Existing Functionality**: All existing SA1-SA4 classification tests continue to pass
- **New Functionality**: Comprehensive IARE-specific test coverage
- **End-to-End**: Successful live testing with real NT CHC location data

## Usage Instructions

### Configuration
Set IARE file path via environment variable:
```bash
export ASGS_IARE_PATH="data/asgs/IARE_2021_AUST_GDA2020_SHP/IARE_2021_AUST_GDA2020.shp"
```

Or place IARE files in `data/asgs/` directory for automatic detection.

### Running with IARE Classification
```bash
uv run python -m src.app --input-csv data/input/locations.csv --output-csv outputs/results.csv
```

### Checking IARE Status
```bash
uv run python -m src.app info
```

## Project Impact

### Enhanced Geographic Coverage
- **Indigenous Communities**: Provides Indigenous-specific geographic classification essential for CHC locations serving Indigenous communities
- **Northern Territory Focus**: Particularly valuable for NT CHC locations where many serve Indigenous populations
- **Complementary Classification**: Works alongside existing ABS Statistical Areas for comprehensive geographic analysis

### Maintainability
- **Modular Design**: Seamlessly integrated with existing architecture patterns
- **Extensibility**: Framework ready for additional ASGS boundary types
- **Documentation**: Comprehensive implementation documentation for future maintenance

### Data Quality
- **Hierarchical Consistency**: IARE data maintains geographic hierarchy integrity
- **Coordinate Accuracy**: Proper CRS handling ensures spatial accuracy
- **Validation Standards**: Maintains existing data quality validation frameworks

This implementation successfully extends the CHC geocoding system with Indigenous Areas classification capability while maintaining code quality, test coverage, and architectural consistency.