import logging
from pathlib import Path

import pandas as pd
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .classify import classify_points, get_classification_summary
from .geocode import batch_geocode
from .io_utils import (
    load_existing_cache,
    merge_with_cache,
    print_results_preview,
    read_locations_file,
    restore_original_names,
    validate_geocoded_data,
    write_output_csv,
)
from .settings import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("chc_geocoding.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Rich console for pretty output
console = Console()

# Typer app
app = typer.Typer(
    name="chc-classifier", help="Community Health Centre geocoding and ABS classification tool"
)


def setup_sample_data() -> None:
    """Create sample data if it doesn't exist."""
    from .io_utils import create_sample_locations_file

    settings = get_settings()
    sample_file = settings.data_dir / "input" / "locations.csv"

    if not sample_file.exists():
        console.print(f"[yellow]Creating sample data file: {sample_file}[/yellow]")
        create_sample_locations_file(sample_file)


def main_process(
    input_csv: str, output_csv: str, skip_classification: bool, create_sample: bool, rebuild: bool = False
) -> None:
    """Main processing logic for CHC locations."""

    console.print("[bold blue]CHC ABS Classifier[/bold blue]")
    console.print("Community Health Centre Geocoding and ABS Statistical Classification")
    console.print()

    settings = get_settings()
    input_path = Path(input_csv)
    output_path = Path(output_csv)

    # Handle sample creation
    if create_sample:
        from .io_utils import create_sample_locations_file

        create_sample_locations_file(input_path)
        console.print(f"[green]✓[/green] Sample file created: {input_path}")
        return

    # Ensure sample data exists
    setup_sample_data()

    try:
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            # Step 1: Read locations
            task = progress.add_task("Reading locations...", total=None)
            df = read_locations_file(input_path, required_columns=["CHC"])
            progress.update(task, description=f"✓ Loaded {len(df)} locations")

            # Step 2: Load cache and determine what needs processing
            task = progress.add_task("Analyzing cache...", total=None)
            cache_df = load_existing_cache(output_path)
            to_geocode_df, to_classify_df, already_complete_df = merge_with_cache(df, cache_df, rebuild)
            
            cache_msg = f"✓ Cache analyzed: {len(already_complete_df)} complete, {len(to_classify_df)} classification needed, {len(to_geocode_df)} full processing needed"
            if rebuild:
                cache_msg = f"✓ Rebuild mode: processing all {len(df)} locations"
            progress.update(task, description=cache_msg)

            # Step 3: Geocode locations that need it
            df_geocoded_results = []
            if not to_geocode_df.empty:
                task = progress.add_task("Geocoding locations...", total=None)
                df_geocoded_new = batch_geocode(to_geocode_df)
                df_geocoded_results.append(df_geocoded_new)
                progress.update(task, description=f"✓ Geocoded {len(to_geocode_df)} locations")

            # Add locations that only need classification to geocoded results
            if not to_classify_df.empty:
                df_geocoded_results.append(to_classify_df)

            # Combine all geocoded data for validation and classification
            if df_geocoded_results:
                df_geocoded = pd.concat(df_geocoded_results, ignore_index=True)
                
                # Step 4: Validate results
                task = progress.add_task("Validating results...", total=None)
                validation_passed = validate_geocoded_data(df_geocoded, min_success_rate=0.8)
                progress.update(task, description="✓ Validation complete")

                if not validation_passed:
                    console.print("[yellow]⚠ Warning: Geocoding validation failed[/yellow]")
            else:
                df_geocoded = pd.DataFrame()

            # Step 5: ABS Classification (if not skipped)
            df_classified_results = []
            
            # Check if ASGS files are available (needed for both logic and error messages)
            asgs_paths = settings.get_asgs_paths()
            available_files = [
                name for name, path in asgs_paths.items() if path and path.exists()
            ]
            
            if not skip_classification and not df_geocoded.empty:
                task = progress.add_task("Classifying into ABS areas...", total=None)

                if available_files:
                    df_classified_new = classify_points(df_geocoded)
                    df_classified_results.append(df_classified_new)
                    progress.update(task, description=f"✓ Classified {len(df_geocoded)} locations")
                else:
                    console.print(
                        "[yellow]⚠ No ASGS files found. Skipping classification.[/yellow]"
                    )
                    console.print(
                        "To enable classification, download ASGS boundaries to data/asgs/"
                    )
                    df_classified_results.append(df_geocoded)
                    progress.update(task, description="⚠ Classification skipped")
            elif not df_geocoded.empty:
                df_classified_results.append(df_geocoded)
                console.print("[yellow]ABS classification skipped as requested[/yellow]")

            # Add already complete locations from cache
            if not already_complete_df.empty:
                df_classified_results.append(already_complete_df)

            # Combine all results
            if df_classified_results:
                df_classified = pd.concat(df_classified_results, ignore_index=True)
                # Sort by CHC name for consistent output
                df_classified = df_classified.sort_values('CHC').reset_index(drop=True)
            else:
                df_classified = df

            # Step 6: Restore original names and save results
            task = progress.add_task("Saving results...", total=None)
            df_final = restore_original_names(df_classified)
            write_output_csv(df_final, output_path)
            progress.update(task, description=f"✓ Results saved to {output_path}")

        console.print()

        # Display summary
        summary = get_classification_summary(df_final)

        table = Table(title="Processing Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Total locations", str(summary["total_locations"]))
        table.add_row(
            "Successfully geocoded",
            f"{summary['geocoded_successfully']} ({summary['geocoding_success_rate']:.1%})",
        )
        table.add_row(
            "Successfully classified",
            f"{summary['classified_successfully']} ({summary['classification_success_rate']:.1%})",
        )

        if summary["states_distribution"]:
            table.add_row("", "")
            table.add_row("State distribution:", "")
            for state, count in summary["states_distribution"].items():
                table.add_row(f"  {state or 'Unknown'}", str(count))

        console.print(table)
        console.print()

        # Show preview of results
        console.print("[bold]Results Preview:[/bold]")
        print_results_preview(df_final)

        console.print(f"\n[green]✓[/green] Processing complete! Results saved to: {output_path}")

        if not skip_classification and not available_files:
            console.print(
                "\n[blue]💡 Tip:[/blue] Download ASGS boundary files to enable "
                "full ABS classification"
            )
            console.print(
                "Visit: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files"
            )

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        logger.error(f"Application error: {e}", exc_info=True)
        raise typer.Exit(1)


@app.command("run")
def run(
    input_csv: str = typer.Option(
        "data/input/locations.csv",
        "--input-csv",
        "-i",
        help="Path to input CSV file with CHC locations",
    ),
    output_csv: str = typer.Option(
        "outputs/chc_classified.csv", "--output-csv", "-o", help="Path to output CSV file"
    ),
    skip_classification: bool = typer.Option(
        False, "--skip-classification", help="Skip ABS classification (geocoding only)"
    ),
    create_sample: bool = typer.Option(
        False, "--create-sample", help="Create sample input file and exit"
    ),
    rebuild: bool = typer.Option(
        False, "--rebuild", help="Force rebuild - ignore cache and process all locations"
    ),
) -> None:
    """Process CHC locations with geocoding and ABS classification."""
    main_process(input_csv, output_csv, skip_classification, create_sample, rebuild)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    input_csv: str = typer.Option(
        "data/input/locations.csv",
        "--input-csv",
        "-i",
        help="Path to input CSV file with CHC locations",
    ),
    output_csv: str = typer.Option(
        "outputs/chc_classified.csv", "--output-csv", "-o", help="Path to output CSV file"
    ),
    skip_classification: bool = typer.Option(
        False, "--skip-classification", help="Skip ABS classification (geocoding only)"
    ),
    create_sample: bool = typer.Option(
        False, "--create-sample", help="Create sample input file and exit"
    ),
    rebuild: bool = typer.Option(
        False, "--rebuild", help="Force rebuild - ignore cache and process all locations"
    ),
) -> None:
    """CHC ABS Classifier - Community Health Centre geocoding and classification."""
    if ctx.invoked_subcommand is None:
        main_process(input_csv, output_csv, skip_classification, create_sample, rebuild)


@app.command()
def info() -> None:
    """Show configuration and system information."""
    settings = get_settings()

    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Nominatim User Agent", settings.nominatim_user_agent)
    table.add_row("Nominatim URL", settings.nominatim_url)
    table.add_row("Geocoding delay (sec)", str(settings.geocode_min_delay_sec))
    table.add_row("Default CRS", settings.default_crs)
    table.add_row("Data directory", str(settings.data_dir))
    table.add_row("Output directory", str(settings.output_dir))

    console.print(table)
    console.print()

    # ASGS files status
    asgs_table = Table(title="ASGS Files Status")
    asgs_table.add_column("Layer", style="cyan")
    asgs_table.add_column("Path", style="yellow")
    asgs_table.add_column("Status", style="green")

    asgs_paths = settings.get_asgs_paths()
    for layer, path in asgs_paths.items():
        if path is None:
            asgs_table.add_row(layer, "Not configured", "[red]✗[/red]")
        elif path.exists():
            asgs_table.add_row(layer, str(path), "[green]✓[/green]")
        else:
            asgs_table.add_row(layer, str(path), "[red]Missing[/red]")

    console.print(asgs_table)


if __name__ == "__main__":
    app()
