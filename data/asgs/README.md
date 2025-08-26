# ASGS Boundary Data

This directory contains Australian Statistical Geography Standard (ASGS) 2021 boundary files.

## Download Instructions

The boundary files are too large for git and must be downloaded separately from the [Australian Bureau of Statistics](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files).

### Required Files

Download and place the following files in this directory:

**GeoPackage format (preferred):**
```
SA1_2021_AUST_GDA2020.gpkg
SA2_2021_AUST_GDA2020.gpkg  
SA3_2021_AUST_GDA2020.gpkg
SA4_2021_AUST_GDA2020.gpkg
GCCSA_2021_AUST_GDA2020.gpkg
STE_2021_AUST_GDA2020.gpkg
```

**OR Shapefile format:**
```
SA1_2021_AUST_SHP_GDA2020/
SA2_2021_AUST_SHP_GDA2020/
SA3_2021_AUST_SHP_GDA2020/
SA4_2021_AUST_SHP_GDA2020/
GCCSA_2021_AUST_SHP_GDA2020/
STE_2021_AUST_SHP_GDA2020/
```

### Download Links

- **Digital Boundary Files**: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files
- **Specific SA1 Download**: Search for "SA1 2021" on the ABS website

### File Sizes

Note: These files are large (typically 50-200MB each) and are excluded from git.

- SA1: ~200MB (most detailed boundaries)
- SA2: ~50MB  
- SA3: ~10MB
- SA4: ~5MB
- GCCSA: ~2MB
- STE: ~1MB

### Minimum Requirements

For basic functionality, you only need **SA1_2021_AUST_GDA2020.gpkg** (or the Shapefile equivalent), as it contains all hierarchical information (SA2, SA3, SA4, GCCSA, State).