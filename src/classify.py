import logging
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from .settings import get_settings

logger = logging.getLogger(__name__)


def load_layer(path: Path, cols: list[str]) -> gpd.GeoDataFrame:
    """Load a spatial layer keeping only necessary columns.

    Args:
        path: Path to the spatial data file (GeoPackage, Shapefile, etc.)
        cols: List of column names to keep (using standardized names)

    Returns:
        GeoDataFrame with specified columns and geometry (columns renamed to standard format)
    """
    if not path.exists():
        raise FileNotFoundError(f"ASGS file not found: {path}")

    logger.info(f"Loading spatial layer: {path}")

    try:
        # Load the full dataset first
        gdf = gpd.read_file(path)

        # Create mapping from standard names to actual column names
        column_mapping = {}
        for std_col in cols:
            # Try different naming conventions
            candidates = [
                std_col,  # Standard name
                f"{std_col}_2021",  # GeoPackage format
                f"{std_col}21",  # Shapefile format
                f"{std_col.replace('GCCSA', 'GCC')}",  # GCCSA -> GCC variation
                f"{std_col.replace('GCCSA', 'GCC')}21",  # GCCSA -> GCC21 variation
                f"{std_col.replace('STE', 'STE')}21",  # STE21 variation
            ]
            
            for candidate in candidates:
                if candidate in gdf.columns:
                    column_mapping[std_col] = candidate
                    break
        
        if not column_mapping:
            logger.warning(f"No specified columns found in {path}. "
                         f"Requested: {cols}, Available: {list(gdf.columns)}")
            return gdf

        # Select columns and rename to standard format
        cols_to_keep = list(column_mapping.values()) + ["geometry"]
        gdf_filtered = gdf[cols_to_keep].copy()
        
        # Rename columns to standard format
        rename_dict = {v: k for k, v in column_mapping.items()}
        gdf_filtered = gdf_filtered.rename(columns=rename_dict)

        logger.info(f"Loaded {len(gdf_filtered)} features with columns: {list(column_mapping.keys())}")
        return gdf_filtered

    except Exception as e:
        logger.error(f"Error loading {path}: {e}")
        raise


def classify_points(df_points: pd.DataFrame) -> pd.DataFrame:
    """Classify geocoded points into Australian statistical areas.

    Args:
        df_points: DataFrame with Latitude and Longitude columns

    Returns:
        DataFrame with additional ABS classification columns
    """
    settings = get_settings()

    # Initialize result with original data and add ABS columns early
    result_df = df_points.copy()
    abs_columns = [
        "SA1",
        "SA2_CODE",
        "SA2_NAME",
        "SA3_NAME",
        "SA4_NAME",
        "GCCSA_NAME",
        "STATE_NAME",
    ]
    for col in abs_columns:
        result_df[col] = None

    # Filter out rows without coordinates
    valid_points = df_points.dropna(subset=["Latitude", "Longitude"]).copy()
    if len(valid_points) == 0:
        logger.warning("No valid coordinates found for classification")
        return result_df

    logger.info(f"Classifying {len(valid_points)} points into ABS statistical areas")

    # Convert to GeoDataFrame
    geometry = [
        Point(lon, lat) for lon, lat in zip(valid_points["Longitude"], valid_points["Latitude"])
    ]
    points_gdf = gpd.GeoDataFrame(valid_points, geometry=geometry, crs=settings.default_crs)

    # Use SA1 boundaries which contain all hierarchical information
    if settings.asgs_sa1_path is None or not settings.asgs_sa1_path.exists():
        logger.warning("SA1 boundaries not found - skipping ABS classification")
        return result_df

    try:
        # Load SA1 boundaries with all hierarchical columns
        hierarchy_columns = [
            "SA1_CODE", "SA2_CODE", "SA2_NAME", "SA3_CODE", "SA3_NAME", 
            "SA4_CODE", "SA4_NAME", "GCC_CODE", "GCC_NAME", "STE_CODE", "STE_NAME"
        ]
        sa1_gdf = load_layer(settings.asgs_sa1_path, hierarchy_columns)

        # Ensure CRS matches
        if sa1_gdf.crs != points_gdf.crs:
            logger.info(f"Reprojecting SA1 boundaries from {sa1_gdf.crs} to {points_gdf.crs}")
            sa1_gdf = sa1_gdf.to_crs(points_gdf.crs)

        # Perform single spatial join to get all hierarchical data
        joined = gpd.sjoin(points_gdf, sa1_gdf, how="left", predicate="within")

        # Map hierarchical columns to result DataFrame
        hierarchy_mapping = {
            "SA1": "SA1_CODE",
            "SA2_CODE": "SA2_CODE", 
            "SA2_NAME": "SA2_NAME",
            "SA3_NAME": "SA3_NAME",
            "SA4_NAME": "SA4_NAME",
            "GCCSA_NAME": "GCC_NAME",
            "STATE_NAME": "STE_NAME",
        }

        # Update only the rows that had valid coordinates
        valid_indices = valid_points.index
        for result_col, source_col in hierarchy_mapping.items():
            if source_col in joined.columns:
                result_df.loc[valid_indices, result_col] = joined[source_col].values

        logger.info("Successfully classified points using SA1 hierarchical boundaries")

    except Exception as e:
        logger.error(f"Error processing SA1 hierarchical classification: {e}")
        return result_df

    # Log classification success rate
    classified_count = result_df[abs_columns].notna().any(axis=1).sum()
    total_valid = len(valid_points)
    logger.info(f"Classification complete: {classified_count}/{total_valid} points classified")

    return result_df


def get_classification_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Generate a summary of the classification results.

    Args:
        df: DataFrame with classification results

    Returns:
        Dictionary with summary statistics
    """
    total_points = len(df)
    geocoded_points = df[["Latitude", "Longitude"]].notna().all(axis=1).sum()

    abs_columns = [
        "SA1",
        "SA2_CODE",
        "SA2_NAME",
        "SA3_NAME",
        "SA4_NAME",
        "GCCSA_NAME",
        "STATE_NAME",
    ]
    available_abs_columns = [col for col in abs_columns if col in df.columns]

    if available_abs_columns:
        classified_points = df[available_abs_columns].notna().any(axis=1).sum()
    else:
        classified_points = 0

    # Count classifications by state
    state_counts = df["STATE_NAME"].value_counts().to_dict() if "STATE_NAME" in df.columns else {}

    return {
        "total_locations": total_points,
        "geocoded_successfully": geocoded_points,
        "classified_successfully": classified_points,
        "geocoding_success_rate": geocoded_points / total_points if total_points > 0 else 0,
        "classification_success_rate": classified_points / geocoded_points
        if geocoded_points > 0
        else 0,
        "states_distribution": state_counts,
    }
