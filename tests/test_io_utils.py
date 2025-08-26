import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.io_utils import (
    create_sample_locations_file,
    read_locations_csv,
    validate_geocoded_data,
    write_output_csv,
)


class TestReadLocationsCsv:
    """Test the CSV reading function."""

    def test_read_locations_csv_file_not_found(self):
        """Test reading non-existent file."""
        path = Path("nonexistent_file.csv")
        with pytest.raises(FileNotFoundError):
            read_locations_csv(path)

    def test_read_locations_csv_success(self):
        """Test successful CSV reading."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("CHC,Extra_Column\n")
            f.write("Location 1 CHC,Value 1\n")
            f.write("Location 2 CHC,Value 2\n")
            temp_path = Path(f.name)

        try:
            df = read_locations_csv(temp_path, required_columns=["CHC"])

            assert len(df) == 2
            assert list(df.columns) == ["CHC", "Extra_Column"]
            assert df.iloc[0]["CHC"] == "Location 1 CHC"
            assert df.iloc[1]["CHC"] == "Location 2 CHC"
        finally:
            os.unlink(temp_path)

    def test_read_locations_csv_missing_required_column(self):
        """Test reading CSV with missing required columns."""
        # Create temporary CSV file without CHC column
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Location,Extra_Column\n")
            f.write("Location 1,Value 1\n")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Missing required columns: \\['CHC'\\]"):
                read_locations_csv(temp_path, required_columns=["CHC"])
        finally:
            os.unlink(temp_path)

    def test_read_locations_csv_remove_empty_rows(self):
        """Test that empty location names are removed."""
        # Create temporary CSV file with empty values
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("CHC\n")
            f.write("Location 1 CHC\n")
            f.write("\n")  # Empty row
            f.write("   \n")  # Whitespace only
            f.write("Location 2 CHC\n")
            temp_path = Path(f.name)

        try:
            df = read_locations_csv(temp_path, required_columns=["CHC"])

            assert len(df) == 2
            assert df.iloc[0]["CHC"] == "Location 1 CHC"
            assert df.iloc[1]["CHC"] == "Location 2 CHC"
        finally:
            os.unlink(temp_path)


class TestWriteOutputCsv:
    """Test the CSV writing function."""

    def test_write_output_csv_success(self):
        """Test successful CSV writing."""
        df = pd.DataFrame(
            {
                "CHC": ["Location 1", "Location 2"],
                "Latitude": [-12.0, -13.0],
                "Longitude": [131.0, 132.0],
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output.csv"
            write_output_csv(df, output_path)

            # Verify file was written
            assert output_path.exists()

            # Read back and verify content
            df_read = pd.read_csv(output_path)
            assert len(df_read) == 2
            assert list(df_read.columns) == ["CHC", "Latitude", "Longitude"]

    def test_write_output_csv_creates_directory(self):
        """Test that output directory is created if it doesn't exist."""
        df = pd.DataFrame({"CHC": ["Location 1"], "Latitude": [-12.0], "Longitude": [131.0]})

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "subdir" / "test_output.csv"
            write_output_csv(df, output_path)

            # Verify directory and file were created
            assert output_path.parent.exists()
            assert output_path.exists()


class TestValidateGeocodedData:
    """Test the data validation function."""

    def test_validate_geocoded_data_success(self):
        """Test validation with good data."""
        df = pd.DataFrame(
            {
                "CHC": ["Loc1", "Loc2", "Loc3"],
                "Latitude": [-12.0, -13.0, -14.0],
                "Longitude": [131.0, 132.0, 133.0],
            }
        )

        result = validate_geocoded_data(df, min_success_rate=0.8)
        assert result is True

    def test_validate_geocoded_data_low_success_rate(self):
        """Test validation with low success rate."""
        df = pd.DataFrame(
            {
                "CHC": ["Loc1", "Loc2", "Loc3"],
                "Latitude": [-12.0, None, None],
                "Longitude": [131.0, None, None],
            }
        )

        result = validate_geocoded_data(df, min_success_rate=0.8)
        assert result is False

    def test_validate_geocoded_data_empty_dataframe(self):
        """Test validation with empty dataframe."""
        df = pd.DataFrame({"CHC": [], "Latitude": [], "Longitude": []})

        result = validate_geocoded_data(df)
        assert result is False

    def test_validate_geocoded_data_coordinates_outside_australia(self):
        """Test validation with coordinates outside Australia."""
        # Coordinates in Europe (outside Australia bounds)
        df = pd.DataFrame(
            {
                "CHC": ["Loc1", "Loc2"],
                "Latitude": [48.8566, -12.0],  # Paris latitude, valid AU latitude
                "Longitude": [2.3522, 131.0],  # Paris longitude, valid AU longitude
            }
        )

        # Should still pass validation but log warnings
        result = validate_geocoded_data(df, min_success_rate=0.5)
        assert result is True

    def test_validate_geocoded_data_partial_coordinates(self):
        """Test validation with partial coordinate data."""
        df = pd.DataFrame(
            {
                "CHC": ["Loc1", "Loc2", "Loc3"],
                "Latitude": [-12.0, -13.0, None],
                "Longitude": [131.0, 132.0, 133.0],  # Longitude without latitude
            }
        )

        # Only first two rows should count as successfully geocoded
        result = validate_geocoded_data(df, min_success_rate=0.6)
        assert result is True

        result = validate_geocoded_data(df, min_success_rate=0.8)
        assert result is False


class TestCreateSampleLocationsFile:
    """Test the sample file creation function."""

    def test_create_sample_locations_file(self):
        """Test creating sample locations file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "sample_locations.csv"
            create_sample_locations_file(output_path)

            # Verify file was created
            assert output_path.exists()

            # Read and verify content
            df = pd.read_csv(output_path)
            assert len(df) == 10
            assert "CHC" in df.columns
            assert all("CHC" in location for location in df["CHC"])

            # Verify some expected locations
            expected_locations = [
                "Adelaide River CHC, NT, Australia",
                "Batchelor CHC, NT, Australia",
            ]
            for expected in expected_locations:
                assert expected in df["CHC"].values

    def test_create_sample_locations_file_creates_directory(self):
        """Test that parent directories are created if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "data" / "input" / "sample_locations.csv"
            create_sample_locations_file(output_path)

            # Verify directory structure and file were created
            assert output_path.parent.exists()
            assert output_path.exists()

            # Verify content
            df = pd.read_csv(output_path)
            assert len(df) == 10
