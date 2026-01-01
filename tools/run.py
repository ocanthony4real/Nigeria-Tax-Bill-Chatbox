from datetime import datetime as dt
from pathlib import Path


import click
from loguru import logger


from llm_engineering import settings

from pipelines.pdf_data_etl import pdf_data_etl
from pipelines.feature_engineering import feature_engineering

# from pipelines import (
#      feature_engineering
# )


@click.command(
    help="""
LLM Engineering project CLI v0.0.1. 

Main entry point for the pipeline execution. 
This entrypoint is where everything comes together.

Run the ZenML LLM Engineering project pipelines with various options.

Run a pipeline with the required parameters. This executes
all steps in the pipeline in the correct order using the orchestrator
stack component that is configured in your active ZenML stack.

Examples:

  \b
  # Run the pipeline with default options
  python run.py
               
  \b
  # Run the pipeline without cache
  python run.py --no-cache
  
  \b
  # Run only the ETL pipeline
  python run.py --only-etl

"""
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Disable caching for the pipeline run.",
)
@click.option(
    "--run-pdf-etl",
    is_flag=True,
    default=False,
    help="Whether to run the pdf etl pipeline",
)
@click.option(
    "--run-feature-engineering",
    is_flag=True,
    default=False,
    help="Whether to run the FE pipeline.",
)
@click.option(
    "--export-settings",
    is_flag=True,
    default=False,
    help="Whether to export your settings to ZenML or not.",
)

def main(
    no_cache: bool = False,
    run_pdf_etl: bool = False,
    run_feature_engineering: bool = False,
    export_settings: bool = False,
) -> None:
    assert (
        run_pdf_etl
        or run_feature_engineering
        or export_settings
    ), "Please specify an action to run."

    if export_settings:
        logger.info("Exporting settings to ZenML secrets.")
        settings.export()

    pipeline_args = {
        "enable_cache": not no_cache,
    }
    root_dir = Path(__file__).resolve().parent.parent


    if run_pdf_etl:
        run_args_pdf_etl = {}
        pipeline_args["config_path"] = root_dir / "configs" / "pdf_data_etl.yaml"
        assert pipeline_args["config_path"].exists(), f"Config file not found: {pipeline_args['config_path']}"
        pipeline_args["run_name"] = f"pdf_etl_run_{dt.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        pdf_data_etl.with_options(**pipeline_args)(**run_args_pdf_etl)
    
    if run_feature_engineering:
        run_args_fe = {}
        pipeline_args["config_path"] = root_dir / "configs" / "feature_engineering.yaml"
        pipeline_args["run_name"] = f"feature_engineering_run_{dt.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        feature_engineering.with_options(**pipeline_args)(**run_args_fe)




if __name__ == "__main__":
    main()
