import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def read_locations_file(path: Path, required_columns: list[str] | None = None) -> pd.DataFrame:
    """Read and validate a locations file (CSV or TXT).

    Args:
        path: Path to the CSV or TXT file
        required_columns: List of required column names (only for CSV)

    Returns:
        DataFrame with validated location data (CHC column)

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If required columns are missing
    """
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    logger.info(f"Reading locations from: {path}")

    try:
        # Handle .txt files (raw locality names)
        if path.suffix.lower() == ".txt":
            with open(path, encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            # Convert to qualified names with NT, Australia, but preserve original
            qualified_names = [f"{name}, NT, Australia" for name in lines]
            df = pd.DataFrame(
                {
                    "CHC": qualified_names,
                    "Original_CHC": lines,  # Preserve original names
                }
            )
            logger.info(f"Converted {len(lines)} raw locality names to qualified format")

        # Handle .csv files
        else:
            df = pd.read_csv(path)

            # Validate required columns
            if required_columns:
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(
                        f"Missing required columns: {missing_columns}. "
                        f"Available columns: {list(df.columns)}"
                    )

        logger.info(f"Loaded {len(df)} locations")

        # Remove rows with empty location names
        if "CHC" in df.columns:
            initial_count = len(df)
            df = df.dropna(subset=["CHC"])
            df = df[df["CHC"].str.strip() != ""]
            if len(df) < initial_count:
                logger.info(f"Removed {initial_count - len(df)} rows with empty location names")

        return df

    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        raise


def restore_original_names(df: pd.DataFrame) -> pd.DataFrame:
    """Restore original CHC names in the final output.

    Args:
        df: DataFrame with processed results

    Returns:
        DataFrame with original CHC names restored
    """
    if "Original_CHC" in df.columns:
        # Replace CHC column with original names and drop the Original_CHC column
        result_df = df.copy()
        result_df["CHC"] = result_df["Original_CHC"]
        result_df = result_df.drop(columns=["Original_CHC"])
        logger.info("Restored original CHC names in output")
        return result_df
    else:
        # No original names to restore
        return df


def write_output_csv(df: pd.DataFrame, path: Path = Path("outputs/chc_classified.csv")) -> None:
    """Write results to CSV file.

    Args:
        df: DataFrame to write
        path: Output file path
    """
    # Ensure output directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Writing {len(df)} results to: {path}")

    try:
        df.to_csv(path, index=False)
        logger.info(f"Successfully wrote output to {path}")

    except Exception as e:
        logger.error(f"Error writing CSV file {path}: {e}")
        raise


def validate_geocoded_data(df: pd.DataFrame, min_success_rate: float = 0.8) -> bool:
    """Validate geocoded data meets quality requirements.

    Args:
        df: DataFrame with geocoding results
        min_success_rate: Minimum required success rate

    Returns:
        True if validation passes, False otherwise
    """
    total_locations = len(df)
    if total_locations == 0:
        logger.error("No locations to validate")
        return False

    # Check geocoding success rate
    geocoded_count = df[["Latitude", "Longitude"]].notna().all(axis=1).sum()
    success_rate = geocoded_count / total_locations

    logger.info(f"Geocoding success rate: {success_rate:.1%} ({geocoded_count}/{total_locations})")

    if success_rate < min_success_rate:
        logger.warning(
            f"Geocoding success rate {success_rate:.1%} is below minimum {min_success_rate:.1%}"
        )
        return False

    # Check for obviously invalid coordinates (outside Australia)
    # Australia bounding box: roughly -44 to -10 latitude, 113 to 154 longitude
    if geocoded_count > 0:
        valid_coords = df.dropna(subset=["Latitude", "Longitude"])
        invalid_coords = valid_coords[
            (valid_coords["Latitude"] < -44)
            | (valid_coords["Latitude"] > -10)
            | (valid_coords["Longitude"] < 113)
            | (valid_coords["Longitude"] > 154)
        ]

        if len(invalid_coords) > 0:
            logger.warning(f"Found {len(invalid_coords)} coordinates outside Australia bounds")
            for _, row in invalid_coords.iterrows():
                logger.warning(
                    f"  {row.get('CHC', 'Unknown')}: "
                    f"({row['Latitude']:.4f}, {row['Longitude']:.4f})"
                )

    logger.info("Geocoded data validation passed")
    return True


def print_results_preview(df: pd.DataFrame, max_rows: int = 20) -> None:
    """Print a preview of the results.

    Args:
        df: DataFrame to preview
        max_rows: Maximum number of rows to display
    """
    logger.info(f"Results preview (showing up to {max_rows} rows):")

    # Select key columns for display
    display_columns = ["CHC", "Latitude", "Longitude", "Address"]

    # Add ABS classification columns if present
    abs_columns = [
        "SA1",
        "SA2_CODE",
        "SA2_NAME",
        "SA3_NAME",
        "SA4_NAME",
        "GCCSA_NAME",
        "STATE_NAME",
    ]
    available_abs_cols = [col for col in abs_columns if col in df.columns and df[col].notna().any()]
    display_columns.extend(available_abs_cols)

    # Filter to available columns
    available_display_cols = [col for col in display_columns if col in df.columns]

    preview_df = df[available_display_cols].head(max_rows)
    print("\n" + preview_df.to_string(index=False, max_colwidth=40))

    if len(df) > max_rows:
        print(f"\n... and {len(df) - max_rows} more rows")


def load_existing_cache(cache_path: Path) -> pd.DataFrame:
    """Load existing processed results from cache file.

    Args:
        cache_path: Path to the cache file (usually the output CSV)

    Returns:
        DataFrame with previously processed locations, or empty DataFrame if no cache
    """
    if not cache_path.exists():
        logger.info(f"No existing cache found at {cache_path}")
        return pd.DataFrame()

    try:
        cache_df = pd.read_csv(cache_path)
        logger.info(f"Loaded cache with {len(cache_df)} locations from {cache_path}")
        return cache_df
    except Exception as e:
        logger.warning(f"Failed to load cache from {cache_path}: {e}")
        return pd.DataFrame()


def is_location_complete(row: pd.Series) -> bool:
    """Check if a location has complete geocoding and classification data.

    Args:
        row: DataFrame row to check

    Returns:
        True if location has coordinates and SA1 classification
    """
    return (
        pd.notna(row.get("Latitude"))
        and pd.notna(row.get("Longitude"))
        and pd.notna(row.get("SA1"))
    )


def is_location_geocoded(row: pd.Series) -> bool:
    """Check if a location has geocoding data (coordinates).

    Args:
        row: DataFrame row to check

    Returns:
        True if location has coordinates
    """
    return pd.notna(row.get("Latitude")) and pd.notna(row.get("Longitude"))


def merge_with_cache(
    input_df: pd.DataFrame, cache_df: pd.DataFrame, rebuild_mode: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Merge input locations with cached results and determine what needs processing.

    Args:
        input_df: New locations to process
        cache_df: Previously processed locations from cache
        rebuild_mode: If True, ignore cache and process everything

    Returns:
        Tuple of (to_geocode_df, to_classify_df, already_complete_df)
        - to_geocode_df: Locations needing geocoding + classification
        - to_classify_df: Locations needing only classification (already geocoded)
        - already_complete_df: Locations completely processed (from cache)
    """
    if rebuild_mode or cache_df.empty:
        # Rebuild mode or no cache - process everything
        mode = "Rebuild mode" if rebuild_mode else "No cache"
        logger.info(f"{mode}: processing all {len(input_df)} locations")
        return input_df.copy(), pd.DataFrame(), pd.DataFrame()

    # Find matches between input and cache based on CHC name
    cache_dict = {row["CHC"]: row for _, row in cache_df.iterrows()}

    to_geocode_list = []
    to_classify_list = []
    already_complete_list = []

    for _, input_row in input_df.iterrows():
        chc_name = input_row["CHC"]

        if chc_name in cache_dict:
            cached_row = cache_dict[chc_name]

            if is_location_complete(cached_row):
                # Complete - use cached result
                already_complete_list.append(cached_row)
            elif is_location_geocoded(cached_row):
                # Geocoded but not classified - needs classification only
                # Create row with geocoding data for classification
                row_for_classification = input_row.copy()
                row_for_classification["Latitude"] = cached_row["Latitude"]
                row_for_classification["Longitude"] = cached_row["Longitude"]
                row_for_classification["Address"] = cached_row.get("Address", "")
                to_classify_list.append(row_for_classification)
            else:
                # Incomplete - needs full processing
                to_geocode_list.append(input_row)
        else:
            # Not in cache - needs full processing
            to_geocode_list.append(input_row)

    to_geocode_df = (
        pd.DataFrame(to_geocode_list) if to_geocode_list else pd.DataFrame(columns=input_df.columns)
    )
    to_classify_df = (
        pd.DataFrame(to_classify_list)
        if to_classify_list
        else pd.DataFrame(columns=input_df.columns)
    )
    already_complete_df = (
        pd.DataFrame(already_complete_list) if already_complete_list else pd.DataFrame()
    )

    logger.info(
        f"Cache analysis: {len(already_complete_df)} complete, "
        f"{len(to_classify_df)} need classification only, "
        f"{len(to_geocode_df)} need full processing"
    )

    return to_geocode_df, to_classify_df, already_complete_df


def create_sample_locations_file(output_path: Path) -> None:
    """Create a sample locations CSV file for testing.

    Args:
        output_path: Path where to create the sample file
    """
    sample_locations = [
        "Adelaide River CHC, NT, Australia",
        "Ali Curung CHC, NT, Australia",
        "Alpurrurulam CHC, NT, Australia",
        "Ampilatwatja CHC, NT, Australia",
        "Amunturrngu CHC, NT, Australia",
        "Angurugu CHC, NT, Australia",
        "Aputula CHC, NT, Australia",
        "Areyonga CHC, NT, Australia",
        "Atitjere CHC, NT, Australia",
        "Batchelor CHC, NT, Australia",
    ]

    df = pd.DataFrame({"CHC": sample_locations})

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write CSV with proper quoting for locations with commas
    df.to_csv(output_path, index=False, quoting=1)  # QUOTE_ALL
    logger.info(f"Created sample locations file: {output_path}")
