from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.geocode import batch_geocode, geocode_name, strip_chc_token


class TestStripChcToken:
    """Test the CHC token stripping function."""

    def test_strip_chc_from_simple_name(self):
        """Test stripping CHC from a simple location name."""
        result = strip_chc_token("Adelaide River CHC, NT, Australia")
        assert result == "Adelaide River, NT, Australia"

    def test_strip_chc_case_insensitive(self):
        """Test that CHC stripping is case insensitive."""
        result = strip_chc_token("Adelaide River chc, NT, Australia")
        assert result == "Adelaide River, NT, Australia"

    def test_strip_chc_multiple_spaces(self):
        """Test that multiple spaces are collapsed after CHC removal."""
        result = strip_chc_token("Adelaide  River  CHC, NT, Australia")
        assert result == "Adelaide River, NT, Australia"

    def test_no_chc_token(self):
        """Test that strings without CHC are unchanged."""
        original = "Adelaide River, NT, Australia"
        result = strip_chc_token(original)
        assert result == original

    def test_chc_not_standalone(self):
        """Test that CHC is only stripped when it's a standalone word."""
        original = "Adelaide CHC-River, NT, Australia"
        result = strip_chc_token(original)
        assert result == original

    def test_single_part_name(self):
        """Test stripping CHC from a single part name."""
        result = strip_chc_token("Adelaide CHC")
        assert result == "Adelaide"


class TestGeocodeName:
    """Test the geocoding function."""

    @patch("src.geocode.get_settings")
    @patch("src.geocode.Nominatim")
    @patch("src.geocode.RateLimiter")
    def test_successful_geocoding(self, mock_rate_limiter, mock_nominatim, mock_get_settings):
        """Test successful geocoding of a location."""
        # Setup mocks
        mock_settings = Mock()
        mock_settings.nominatim_user_agent = "test_agent"
        mock_settings.geocode_min_delay_sec = 1.0
        mock_get_settings.return_value = mock_settings

        mock_location = Mock()
        mock_location.latitude = -12.6454
        mock_location.longitude = 131.3875
        mock_location.address = "Adelaide River, Northern Territory, Australia"

        mock_geocoder = Mock()
        mock_nominatim.return_value = mock_geocoder

        mock_rate_limited_geocode = Mock()
        mock_rate_limited_geocode.return_value = mock_location
        mock_rate_limiter.return_value = mock_rate_limited_geocode

        # Test geocoding
        result = geocode_name("Adelaide River CHC, NT, Australia")

        # Assertions
        assert result["name"] == "Adelaide River CHC, NT, Australia"
        assert result["lat"] == -12.6454
        assert result["lon"] == 131.3875
        assert result["address"] == "Adelaide River, Northern Territory, Australia"
        assert result["source"] == "nominatim"

        # Verify geocoder was called with normalized name
        mock_rate_limited_geocode.assert_called_with(
            "Adelaide River, NT, Australia", country_codes="au"
        )

    @patch("src.geocode.get_settings")
    @patch("src.geocode.Nominatim")
    @patch("src.geocode.RateLimiter")
    def test_geocoding_with_fallback(self, mock_rate_limiter, mock_nominatim, mock_get_settings):
        """Test geocoding that succeeds on fallback to original string."""
        # Setup mocks
        mock_settings = Mock()
        mock_settings.nominatim_user_agent = "test_agent"
        mock_settings.geocode_min_delay_sec = 1.0
        mock_get_settings.return_value = mock_settings

        mock_location = Mock()
        mock_location.latitude = -12.6454
        mock_location.longitude = 131.3875
        mock_location.address = "Adelaide River CHC, Northern Territory, Australia"

        mock_geocoder = Mock()
        mock_nominatim.return_value = mock_geocoder

        mock_rate_limited_geocode = Mock()
        # First call returns None, second call returns location
        mock_rate_limited_geocode.side_effect = [None, mock_location]
        mock_rate_limiter.return_value = mock_rate_limited_geocode

        # Test geocoding
        result = geocode_name("Adelaide River CHC, NT, Australia")

        # Assertions
        assert result["lat"] == -12.6454
        assert result["lon"] == 131.3875

        # Verify both calls were made
        assert mock_rate_limited_geocode.call_count == 2

    @patch("src.geocode.get_settings")
    @patch("src.geocode.Nominatim")
    @patch("src.geocode.RateLimiter")
    def test_geocoding_failure(self, mock_rate_limiter, mock_nominatim, mock_get_settings):
        """Test geocoding when no results are found."""
        # Setup mocks
        mock_settings = Mock()
        mock_settings.nominatim_user_agent = "test_agent"
        mock_settings.geocode_min_delay_sec = 1.0
        mock_get_settings.return_value = mock_settings

        mock_geocoder = Mock()
        mock_nominatim.return_value = mock_geocoder

        mock_rate_limited_geocode = Mock()
        mock_rate_limited_geocode.return_value = None
        mock_rate_limiter.return_value = mock_rate_limited_geocode

        # Test geocoding
        result = geocode_name("Nonexistent Location CHC, NT, Australia")

        # Assertions
        assert result["name"] == "Nonexistent Location CHC, NT, Australia"
        assert result["lat"] is None
        assert result["lon"] is None
        assert result["address"] is None
        assert result["source"] == "nominatim"

    @patch("src.geocode.get_settings")
    @patch("src.geocode.Nominatim")
    @patch("src.geocode.RateLimiter")
    @patch("src.geocode.time.sleep")
    def test_geocoding_with_retry(
        self, mock_sleep, mock_rate_limiter, mock_nominatim, mock_get_settings
    ):
        """Test geocoding retry logic with exponential backoff."""
        # Setup mocks
        mock_settings = Mock()
        mock_settings.nominatim_user_agent = "test_agent"
        mock_settings.geocode_min_delay_sec = 1.0
        mock_get_settings.return_value = mock_settings

        mock_geocoder = Mock()
        mock_nominatim.return_value = mock_geocoder

        mock_rate_limited_geocode = Mock()
        # First two calls raise exceptions, third succeeds
        mock_location = Mock()
        mock_location.latitude = -12.6454
        mock_location.longitude = 131.3875
        mock_location.address = "Adelaide River, Northern Territory, Australia"

        mock_rate_limited_geocode.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            mock_location,
        ]
        mock_rate_limiter.return_value = mock_rate_limited_geocode

        # Test geocoding
        result = geocode_name("Adelaide River CHC, NT, Australia")

        # Assertions
        assert result["lat"] == -12.6454
        assert result["lon"] == 131.3875

        # Verify retry logic
        assert mock_rate_limited_geocode.call_count == 3
        assert mock_sleep.call_count == 2  # Two retries

        # Verify exponential backoff
        mock_sleep.assert_any_call(1.0)  # First retry: 1 * 1.0
        mock_sleep.assert_any_call(2.0)  # Second retry: 2 * 1.0


class TestBatchGeocode:
    """Test the batch geocoding function."""

    @patch("src.geocode.geocode_name")
    def test_batch_geocode_success(self, mock_geocode_name):
        """Test successful batch geocoding."""
        # Setup test data
        df = pd.DataFrame(
            {"CHC": ["Location 1 CHC", "Location 2 CHC"], "Other_Column": ["Value 1", "Value 2"]}
        )

        # Mock geocoding results
        mock_geocode_name.side_effect = [
            {
                "name": "Location 1 CHC",
                "lat": -12.0,
                "lon": 131.0,
                "address": "Location 1, NT, Australia",
                "source": "nominatim",
            },
            {
                "name": "Location 2 CHC",
                "lat": -13.0,
                "lon": 132.0,
                "address": "Location 2, NT, Australia",
                "source": "nominatim",
            },
        ]

        # Test batch geocoding
        result = batch_geocode(df)

        # Assertions
        assert len(result) == 2
        assert list(result.columns) == ["CHC", "Other_Column", "Latitude", "Longitude", "Address"]

        # Check first row
        assert result.iloc[0]["CHC"] == "Location 1 CHC"
        assert result.iloc[0]["Latitude"] == -12.0
        assert result.iloc[0]["Longitude"] == 131.0
        assert result.iloc[0]["Address"] == "Location 1, NT, Australia"

        # Check second row
        assert result.iloc[1]["CHC"] == "Location 2 CHC"
        assert result.iloc[1]["Latitude"] == -13.0
        assert result.iloc[1]["Longitude"] == 132.0
        assert result.iloc[1]["Address"] == "Location 2, NT, Australia"

    def test_batch_geocode_missing_column(self):
        """Test batch geocoding with missing CHC column."""
        df = pd.DataFrame({"Location": ["Location 1", "Location 2"]})

        with pytest.raises(ValueError, match="Column 'CHC' not found"):
            batch_geocode(df)

    @patch("src.geocode.geocode_name")
    def test_batch_geocode_with_failures(self, mock_geocode_name):
        """Test batch geocoding with some failures."""
        # Setup test data
        df = pd.DataFrame({"CHC": ["Good Location CHC", "Bad Location CHC"]})

        # Mock geocoding results - one success, one failure
        mock_geocode_name.side_effect = [
            {
                "name": "Good Location CHC",
                "lat": -12.0,
                "lon": 131.0,
                "address": "Good Location, NT, Australia",
                "source": "nominatim",
            },
            {
                "name": "Bad Location CHC",
                "lat": None,
                "lon": None,
                "address": None,
                "source": "nominatim",
            },
        ]

        # Test batch geocoding
        result = batch_geocode(df)

        # Assertions
        assert len(result) == 2

        # Check successful geocoding
        assert result.iloc[0]["Latitude"] == -12.0
        assert result.iloc[0]["Address"] == "Good Location, NT, Australia"

        # Check failed geocoding
        assert pd.isna(result.iloc[1]["Latitude"])
        assert pd.isna(result.iloc[1]["Longitude"])
        assert result.iloc[1]["Address"] == "Not found"
