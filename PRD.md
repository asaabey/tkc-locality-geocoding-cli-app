🛠 Build Plan for VSCode Agent
0) Project Scaffold

Create repo: chc-abs-classifier/

Structure:

chc-abs-classifier/
  ├─ README.md
  ├─ pyproject.toml
  ├─ src/
  │   ├─ app.py
  │   ├─ geocode.py
  │   ├─ classify.py
  │   ├─ io_utils.py
  │   └─ settings.py
  ├─ data/
  │   ├─ input/locations.csv
  │   └─ asgs/   # shapefiles/GeoPackages go here
  ├─ outputs/
  │   └─ chc_classified.csv
  ├─ tests/
  │   ├─ test_geocode.py
  │   └─ test_classify.py
  └─ Makefile

1) Environment & Dependencies

Use Python 3.10+

Add pyproject.toml (PEP 621) with deps:

pandas, geopy, geopandas, shapely, pyproj, fiona, requests, python-dotenv, typer[all]

Dev deps: pytest, ruff

Make targets:

make venv – create and activate venv

make install – install deps

make lint – ruff check

make test – pytest

make run – run CLI (python -m src.app)

2) Configuration

src/settings.py

Read env vars: NOMINATIM_USER_AGENT, NOMINATIM_URL (default https://nominatim.openstreetmap.org), GEOCODE_MIN_DELAY_SEC=1.0

ASGS paths:

ASGS_SA1_PATH, ASGS_SA2_PATH, ASGS_SA3_PATH, ASGS_SA4_PATH, ASGS_GCCSA_PATH, ASGS_STE_PATH

Default CRS: EPSG:4326

3) Input Seed Data

data/input/locations.csv with column CHC and 10 rows:

CHC
Adelaide River CHC
Ali Curung CHC
Alpurrurulam CHC
Ampilatwatja CHC
Amunturrngu CHC
Angurugu CHC
Aputula CHC
Areyonga CHC
Atitjere CHC
Batchelor CHC

4) Geocoding Module

src/geocode.py

Function geocode_name(name: str) -> dict:

Query Nominatim with f"{name}, NT, Australia", throttle using time.sleep(GEOCODE_MIN_DELAY_SEC)

Return { "name": name, "lat": float|None, "lon": float|None, "address": str|None, "source": "nominatim" }

Function batch_geocode(df: pd.DataFrame) -> pd.DataFrame:

Map over df["CHC"], collect results into new columns Latitude, Longitude, Address

Robustness:

Handle HTTP errors, 429, None results gracefully

Optional retry w/ exponential backoff (max 3 attempts)

5) ABS Classification Module

src/classify.py

Helper load_layer(path: str, cols: list[str]) -> gpd.GeoDataFrame (only keep necessary columns)

classify_points(df_points: pd.DataFrame) -> pd.DataFrame:

Convert to GeoDataFrame with geometry=Point(lon, lat), CRS EPSG:4326

For each layer (SA1, SA2, SA3, SA4, GCCSA, STE):

Load polygons into GeoDataFrame

Ensure CRS match; if not, reproject to EPSG:4326

Spatial join gpd.sjoin(points, polygons, how="left", predicate="within")

Select and rename key fields:

SA1: code (e.g., SA1_CODE_2021)

SA2: code + name (e.g., SA2_CODE_2021, SA2_NAME_2021)

SA3: name

SA4: name

GCCSA: name

STE (state/territory): name/abbrev

Return merged DataFrame with columns:

CHC | Latitude | Longitude | Address |
SA1 | SA2_CODE | SA2_NAME | SA3_NAME | SA4_NAME | GCCSA_NAME | STATE_NAME

6) IO Utilities

src/io_utils.py

read_locations_csv(path) -> pd.DataFrame

write_output_csv(df, path="outputs/chc_classified.csv")

Validate required columns

7) CLI App

src/app.py using typer

main(input_csv: str = "data/input/locations.csv", output_csv: str = "outputs/chc_classified.csv")

Read locations

Batch geocode

Filter out rows with missing lat/lon (warn + keep with empty classifications)

Run ABS classification (only for valid points)

Merge back to original order

Save CSV and print a preview (df.head(20).to_string(index=False))

if __name__ == "__main__": app()

8) Shapefiles Acquisition (Agent task)

Download ASGS 2021 (or latest) boundaries from ABS (GeoPackage or Shapefile) and place under data/asgs/. Required layers:

SA1, SA2, SA3, SA4, GCCSA, STE (state)

Name files in settings or document actual filenames in README.

(If zipped) auto-unzip via Makefile rule or simple Python script.

9) Tests

tests/test_geocode.py

Mock Nominatim HTTP call; assert schema and throttle logic

tests/test_classify.py

Create two synthetic points and a dummy polygon; assert join assigns expected area fields

pytest -q should pass

10) Lint & CI (optional)

Ruff config in pyproject.toml (line-length=100, basic rules)

GitHub Actions:

python - setup, install, ruff, pytest

11) README.md (usage)

Quickstart:

make venv && make install

Put ASGS layers into data/asgs/ and set paths in .env or settings.py

make run (or python -m src.app --input_csv data/input/locations.csv --output_csv outputs/chc_classified.csv)

Notes:

Respect Nominatim ToS (1 req/sec)

How to change to Google Maps later (interface contract remains the same)

Acceptance Criteria

Running the CLI on the provided 10 CHCs produces outputs/chc_classified.csv with:

Non-empty Latitude, Longitude, Address for ≥8/10

Valid ABS fields (SA1, SA2_CODE, SA2_NAME, SA3_NAME, SA4_NAME, GCCSA_NAME, STATE_NAME) populated for all rows that have coordinates

No unhandled exceptions; graceful messages for misses

Code passes make test and make lint