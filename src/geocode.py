import logging
import re
import time
from typing import Any

import pandas as pd
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

from .settings import get_settings

logger = logging.getLogger(__name__)


def strip_chc_token(place: str) -> str:
    """Remove the standalone token 'CHC' from the first segment of the place string.

    Example: "Adelaide River CHC, NT, Australia" -> "Adelaide River, NT, Australia"
    """
    parts = place.split(",", 1)
    # Only remove CHC if it's a standalone word (surrounded by spaces or at beginning/end)
    first = re.sub(r"(?:^|\s)CHC(?=\s|$)", "", parts[0], flags=re.IGNORECASE).strip()
    # Collapse multiple spaces possibly left after removal
    first = re.sub(r"\s{2,}", " ", first)
    if len(parts) > 1:
        return f"{first}, {parts[1].lstrip()}"
    return first


def geocode_name(name: str, max_retries: int = 3) -> dict[str, Any]:
    """Geocode a single location name with retry logic.

    Args:
        name: Location name to geocode
        max_retries: Maximum number of retry attempts

    Returns:
        Dictionary with name, lat, lon, address, and source
    """
    settings = get_settings()

    # Setup geocoder with rate limiting
    geolocator = Nominatim(user_agent=settings.nominatim_user_agent, timeout=10)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=settings.geocode_min_delay_sec)

    # Normalize by stripping CHC token
    normalized = strip_chc_token(name)

    result = {"name": name, "lat": None, "lon": None, "address": None, "source": "nominatim"}

    for attempt in range(max_retries):
        try:
            logger.info(
                f"Geocoding attempt {attempt + 1}/{max_retries}: "
                f"original='{name}' normalized='{normalized}'"
            )

            location = None

            # Try normalized name first (with Australia bias)
            location = geocode(normalized, country_codes="au")

            # Fallback to original string if nothing found
            if not location and normalized != name:
                location = geocode(name, country_codes="au")

            if location:
                result.update(
                    {
                        "lat": location.latitude,
                        "lon": location.longitude,
                        "address": location.address,
                    }
                )
                logger.info(f"Successfully geocoded: {result}")
                return result
            else:
                logger.warning(f"No geocoding result found for '{name}'")
                return result

        except Exception as e:
            logger.warning(f"Geocoding error for '{name}' (attempt {attempt + 1}): {e}")

            if attempt < max_retries - 1:
                # Exponential backoff
                delay = (2**attempt) * settings.geocode_min_delay_sec
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Max retries exceeded for '{name}'")
                return result

    return result


def batch_geocode(df: pd.DataFrame, location_column: str = "CHC") -> pd.DataFrame:
    """Geocode multiple locations in a DataFrame.

    Args:
        df: DataFrame containing locations to geocode
        location_column: Name of column containing location strings

    Returns:
        DataFrame with additional Latitude, Longitude, Address columns
    """
    if location_column not in df.columns:
        raise ValueError(f"Column '{location_column}' not found in DataFrame")

    results = []

    for _, row in df.iterrows():
        location_name = row[location_column]
        geocode_result = geocode_name(location_name)

        # Combine original row data with geocoding results
        result_row = row.to_dict()
        result_row.update(
            {
                "Latitude": geocode_result["lat"],
                "Longitude": geocode_result["lon"],
                "Address": geocode_result["address"] or "Not found",
            }
        )

        results.append(result_row)

    return pd.DataFrame(results)
