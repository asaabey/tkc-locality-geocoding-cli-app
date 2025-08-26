from pathlib import Path
from unittest.mock import Mock, patch

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Polygon

from src.classify import classify_points, get_classification_summary, load_layer


class TestLoadLayer:
    """Test the spatial layer loading function."""

    def test_load_layer_file_not_found(self):
        """Test loading a non-existent file."""
        path = Path("nonexistent_file.gpkg")
        with pytest.raises(FileNotFoundError):
            load_layer(path, ["CODE", "NAME"])

    @patch("src.classify.Path.exists")
    @patch("geopandas.read_file")
    def test_load_layer_success(self, mock_read_file, mock_exists):
        """Test successful layer loading with column filtering."""
        # Mock file existence
        mock_exists.return_value = True

        # Mock GeoDataFrame
        mock_gdf = gpd.GeoDataFrame(
            {
                "CODE": ["001", "002", "003"],
                "NAME": ["Area 1", "Area 2", "Area 3"],
                "EXTRA_COL": ["X", "Y", "Z"],
                "geometry": [
                    Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                    Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
                    Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),
                ],
            }
        )
        mock_read_file.return_value = mock_gdf

        # Test loading
        path = Path("test_file.gpkg")
        result = load_layer(path, ["CODE", "NAME"])

        # Assertions
        assert len(result) == 3
        assert list(result.columns) == ["CODE", "NAME", "geometry"]
        assert "EXTRA_COL" not in result.columns

    @patch("src.classify.Path.exists")
    @patch("geopandas.read_file")
    def test_load_layer_missing_columns(self, mock_read_file, mock_exists):
        """Test loading layer when requested columns don't exist."""
        # Mock file existence
        mock_exists.return_value = True

        # Mock GeoDataFrame without requested columns
        mock_gdf = gpd.GeoDataFrame(
            {
                "DIFFERENT_COL": ["X", "Y", "Z"],
                "geometry": [
                    Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                    Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
                    Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),
                ],
            }
        )
        mock_read_file.return_value = mock_gdf

        # Test loading - should return original data when no columns match
        path = Path("test_file.gpkg")
        result = load_layer(path, ["NONEXISTENT_COL"])

        # Should return the full original GeoDataFrame
        assert len(result) == 3
        assert "DIFFERENT_COL" in result.columns


class TestClassifyPoints:
    """Test the point classification function."""

    def test_classify_points_no_valid_coordinates(self):
        """Test classification with no valid coordinates."""
        df = pd.DataFrame(
            {
                "CHC": ["Location 1", "Location 2"],
                "Latitude": [None, None],
                "Longitude": [None, None],
            }
        )

        result = classify_points(df)

        # Should return original dataframe with empty classification columns
        assert len(result) == 2
        assert "SA1" in result.columns
        assert result["SA1"].isna().all()

    @patch("src.classify.get_settings")
    def test_classify_points_no_asgs_files(self, mock_get_settings):
        """Test classification when no ASGS files are available."""
        # Mock settings with no ASGS files
        mock_settings = Mock()
        mock_settings.default_crs = "EPSG:4326"
        mock_settings.asgs_sa1_path = None
        mock_settings.asgs_sa2_path = None
        mock_settings.asgs_sa3_path = None
        mock_settings.asgs_sa4_path = None
        mock_settings.asgs_gccsa_path = None
        mock_settings.asgs_ste_path = None
        mock_get_settings.return_value = mock_settings

        df = pd.DataFrame({"CHC": ["Location 1"], "Latitude": [-12.0], "Longitude": [131.0]})

        result = classify_points(df)

        # Should have classification columns but they should be empty
        assert "SA1" in result.columns
        assert "STATE_NAME" in result.columns
        assert result["SA1"].isna().all()

    @patch("src.classify.load_layer")
    @patch("src.classify.get_settings")
    def test_classify_points_success(self, mock_get_settings, mock_load_layer):
        """Test successful point classification."""
        # Mock settings
        mock_settings = Mock()
        mock_settings.default_crs = "EPSG:4326"

        # Create mock file paths that exist
        mock_sa1_path = Mock()
        mock_sa1_path.exists.return_value = True
        mock_sa2_path = Mock()
        mock_sa2_path.exists.return_value = True

        mock_settings.asgs_sa1_path = mock_sa1_path
        mock_settings.asgs_sa2_path = mock_sa2_path
        mock_settings.asgs_sa3_path = None
        mock_settings.asgs_sa4_path = None
        mock_settings.asgs_gccsa_path = None
        mock_settings.asgs_ste_path = None
        mock_get_settings.return_value = mock_settings

        # Create test point
        df = pd.DataFrame({"CHC": ["Location 1"], "Latitude": [-12.0], "Longitude": [131.0]})

        # Mock boundary layers
        sa1_boundary = gpd.GeoDataFrame(
            {
                "SA1_CODE_2021": ["123456"],
                "geometry": [
                    Polygon([(130.5, -12.5), (131.5, -12.5), (131.5, -11.5), (130.5, -11.5)])
                ],
            },
            crs="EPSG:4326",
        )

        sa2_boundary = gpd.GeoDataFrame(
            {
                "SA2_CODE_2021": ["789"],
                "SA2_NAME_2021": ["Test SA2"],
                "geometry": [
                    Polygon([(130.5, -12.5), (131.5, -12.5), (131.5, -11.5), (130.5, -11.5)])
                ],
            },
            crs="EPSG:4326",
        )

        # Configure mock_load_layer to return different boundaries based on columns requested
        def load_layer_side_effect(path, columns):
            if "SA1_CODE_2021" in columns:
                return sa1_boundary[columns + ["geometry"]]
            elif "SA2_CODE_2021" in columns:
                return sa2_boundary[columns + ["geometry"]]
            else:
                return gpd.GeoDataFrame()

        mock_load_layer.side_effect = load_layer_side_effect

        # Test classification
        result = classify_points(df)

        # Assertions
        assert len(result) == 1
        assert "SA1" in result.columns
        assert "SA2_CODE" in result.columns
        assert "SA2_NAME" in result.columns

        # Check that point was classified correctly
        assert result.iloc[0]["SA1"] == "123456"
        assert result.iloc[0]["SA2_CODE"] == "789"
        assert result.iloc[0]["SA2_NAME"] == "Test SA2"

    @patch("src.classify.load_layer")
    @patch("src.classify.get_settings")
    def test_classify_points_crs_mismatch(self, mock_get_settings, mock_load_layer):
        """Test classification with CRS mismatch between points and boundaries."""
        # Mock settings
        mock_settings = Mock()
        mock_settings.default_crs = "EPSG:4326"

        mock_sa1_path = Mock()
        mock_sa1_path.exists.return_value = True
        mock_settings.asgs_sa1_path = mock_sa1_path
        mock_settings.asgs_sa2_path = None
        mock_settings.asgs_sa3_path = None
        mock_settings.asgs_sa4_path = None
        mock_settings.asgs_gccsa_path = None
        mock_settings.asgs_ste_path = None
        mock_get_settings.return_value = mock_settings

        # Create test point
        df = pd.DataFrame({"CHC": ["Location 1"], "Latitude": [-12.0], "Longitude": [131.0]})

        # Mock boundary layer in different CRS
        sa1_boundary = gpd.GeoDataFrame(
            {
                "SA1_CODE_2021": ["123456"],
                "geometry": [
                    Polygon([(130.5, -12.5), (131.5, -12.5), (131.5, -11.5), (130.5, -11.5)])
                ],
            },
            crs="EPSG:3577",
        )  # Different CRS

        # Mock to_crs to return the same data but with EPSG:4326
        sa1_boundary_reprojected = sa1_boundary.copy()
        sa1_boundary_reprojected.crs = "EPSG:4326"
        sa1_boundary.to_crs = Mock(return_value=sa1_boundary_reprojected)

        mock_load_layer.return_value = sa1_boundary

        # Test classification
        classify_points(df)

        # Should have attempted CRS reprojection
        sa1_boundary.to_crs.assert_called_once_with("EPSG:4326")


class TestGetClassificationSummary:
    """Test the classification summary function."""

    def test_get_classification_summary_basic(self):
        """Test basic classification summary."""
        df = pd.DataFrame(
            {
                "CHC": ["Loc1", "Loc2", "Loc3"],
                "Latitude": [-12.0, -13.0, None],
                "Longitude": [131.0, 132.0, None],
                "SA1": ["123", "456", None],
                "STATE_NAME": ["NT", "NT", None],
            }
        )

        summary = get_classification_summary(df)

        assert summary["total_locations"] == 3
        assert summary["geocoded_successfully"] == 2
        assert summary["classified_successfully"] == 2
        assert summary["geocoding_success_rate"] == 2 / 3
        assert summary["classification_success_rate"] == 1.0  # 2/2 geocoded points were classified
        assert summary["states_distribution"] == {"NT": 2}

    def test_get_classification_summary_empty(self):
        """Test summary with empty dataframe."""
        df = pd.DataFrame({"CHC": [], "Latitude": [], "Longitude": []})

        summary = get_classification_summary(df)

        assert summary["total_locations"] == 0
        assert summary["geocoded_successfully"] == 0
        assert summary["classified_successfully"] == 0
        assert summary["geocoding_success_rate"] == 0
        assert summary["classification_success_rate"] == 0

    def test_get_classification_summary_no_classifications(self):
        """Test summary with geocoded points but no classifications."""
        df = pd.DataFrame(
            {
                "CHC": ["Loc1", "Loc2"],
                "Latitude": [-12.0, -13.0],
                "Longitude": [131.0, 132.0],
                "SA1": [None, None],
                "STATE_NAME": [None, None],
            }
        )

        summary = get_classification_summary(df)

        assert summary["total_locations"] == 2
        assert summary["geocoded_successfully"] == 2
        assert summary["classified_successfully"] == 0
        assert summary["geocoding_success_rate"] == 1.0
        assert summary["classification_success_rate"] == 0.0
