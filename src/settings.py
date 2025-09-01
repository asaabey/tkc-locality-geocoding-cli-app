import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """Application configuration settings."""

    # Nominatim API settings
    nominatim_user_agent: str = "chc_geocoder"
    nominatim_url: str = "https://nominatim.openstreetmap.org"
    geocode_min_delay_sec: float = 1.0

    # ASGS (Australian Statistical Geography Standard) file paths
    asgs_sa1_path: Path | None = None
    asgs_sa2_path: Path | None = None
    asgs_sa3_path: Path | None = None
    asgs_sa4_path: Path | None = None
    asgs_gccsa_path: Path | None = None
    asgs_ste_path: Path | None = None
    asgs_iare_path: Path | None = None

    # Coordinate reference system
    default_crs: str = "EPSG:4326"

    # Data directories
    data_dir: Path = Path("data")
    output_dir: Path = Path("outputs")

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables."""
        return cls(
            nominatim_user_agent=os.getenv("NOMINATIM_USER_AGENT", "chc_geocoder"),
            nominatim_url=os.getenv("NOMINATIM_URL", "https://nominatim.openstreetmap.org"),
            geocode_min_delay_sec=float(os.getenv("GEOCODE_MIN_DELAY_SEC", "1.0")),
            asgs_sa1_path=cls._path_from_env("ASGS_SA1_PATH"),
            asgs_sa2_path=cls._path_from_env("ASGS_SA2_PATH"),
            asgs_sa3_path=cls._path_from_env("ASGS_SA3_PATH"),
            asgs_sa4_path=cls._path_from_env("ASGS_SA4_PATH"),
            asgs_gccsa_path=cls._path_from_env("ASGS_GCCSA_PATH"),
            asgs_ste_path=cls._path_from_env("ASGS_STE_PATH"),
            asgs_iare_path=cls._path_from_env("ASGS_IARE_PATH"),
            default_crs=os.getenv("DEFAULT_CRS", "EPSG:4326"),
            data_dir=Path(os.getenv("DATA_DIR", "data")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "outputs")),
        )

    @staticmethod
    def _path_from_env(env_var: str) -> Path | None:
        """Convert environment variable to Path if set."""
        value = os.getenv(env_var)
        return Path(value) if value else None

    def get_asgs_paths(self) -> dict[str, Path | None]:
        """Get all ASGS file paths as a dictionary."""
        return {
            "SA1": self.asgs_sa1_path,
            "SA2": self.asgs_sa2_path,
            "SA3": self.asgs_sa3_path,
            "SA4": self.asgs_sa4_path,
            "GCCSA": self.asgs_gccsa_path,
            "STE": self.asgs_ste_path,
            "IARE": self.asgs_iare_path,
        }

    def set_default_asgs_paths(self, asgs_dir: Path) -> None:
        """Set default ASGS paths based on a directory containing ASGS files."""
        # Try GeoPackage format first
        gpkg_files = {
            "sa1": asgs_dir / "SA1_2021_AUST_GDA2020.gpkg",
            "sa2": asgs_dir / "SA2_2021_AUST_GDA2020.gpkg",
            "sa3": asgs_dir / "SA3_2021_AUST_GDA2020.gpkg",
            "sa4": asgs_dir / "SA4_2021_AUST_GDA2020.gpkg",
            "gccsa": asgs_dir / "GCCSA_2021_AUST_GDA2020.gpkg",
            "ste": asgs_dir / "STE_2021_AUST_GDA2020.gpkg",
            "iare": asgs_dir / "IARE_2021_AUST_GDA2020.gpkg",
        }

        # Try Shapefile format as fallback (both in subdirectories and loose files)
        shp_files = {
            "sa1": asgs_dir / "SA1_2021_AUST_SHP_GDA2020" / "SA1_2021_AUST_GDA2020.shp",
            "sa2": asgs_dir / "SA2_2021_AUST_SHP_GDA2020" / "SA2_2021_AUST_GDA2020.shp",
            "sa3": asgs_dir / "SA3_2021_AUST_SHP_GDA2020" / "SA3_2021_AUST_GDA2020.shp",
            "sa4": asgs_dir / "SA4_2021_AUST_SHP_GDA2020" / "SA4_2021_AUST_GDA2020.shp",
            "gccsa": asgs_dir / "GCCSA_2021_AUST_SHP_GDA2020" / "GCCSA_2021_AUST_GDA2020.shp",
            "ste": asgs_dir / "STE_2021_AUST_SHP_GDA2020" / "STE_2021_AUST_GDA2020.shp",
            "iare": asgs_dir / "IARE_2021_AUST_GDA2020_SHP" / "IARE_2021_AUST_GDA2020.shp",
        }

        # Try loose shapefile format (files directly in asgs directory)
        loose_shp_files = {
            "sa1": asgs_dir / "SA1_2021_AUST_GDA2020.shp",
            "sa2": asgs_dir / "SA2_2021_AUST_GDA2020.shp",
            "sa3": asgs_dir / "SA3_2021_AUST_GDA2020.shp",
            "sa4": asgs_dir / "SA4_2021_AUST_GDA2020.shp",
            "gccsa": asgs_dir / "GCCSA_2021_AUST_GDA2020.shp",
            "ste": asgs_dir / "STE_2021_AUST_GDA2020.shp",
            "iare": asgs_dir / "IARE_2021_AUST_GDA2020.shp",
        }

        # Set paths, preferring existing files in order: gpkg > shp in subdirs > loose shp
        def _get_existing_path(key):
            if gpkg_files[key].exists():
                return gpkg_files[key]
            elif shp_files[key].exists():
                return shp_files[key]
            elif loose_shp_files[key].exists():
                return loose_shp_files[key]
            else:
                return None

        self.asgs_sa1_path = _get_existing_path("sa1")
        self.asgs_sa2_path = _get_existing_path("sa2")
        self.asgs_sa3_path = _get_existing_path("sa3")
        self.asgs_sa4_path = _get_existing_path("sa4")
        self.asgs_gccsa_path = _get_existing_path("gccsa")
        self.asgs_ste_path = _get_existing_path("ste")
        self.asgs_iare_path = _get_existing_path("iare")


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass  # dotenv is optional

        _settings = Settings.from_env()

        # Set default ASGS paths if not configured
        asgs_dir = _settings.data_dir / "asgs"
        if asgs_dir.exists() and not any(_settings.get_asgs_paths().values()):
            _settings.set_default_asgs_paths(asgs_dir)

    return _settings


def update_settings(**kwargs) -> None:
    """Update global settings (mainly for testing)."""
    global _settings
    if _settings is None:
        _settings = get_settings()

    for key, value in kwargs.items():
        if hasattr(_settings, key):
            setattr(_settings, key, value)
