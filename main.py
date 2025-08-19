#!/usr/bin/env python3
"""
IT Dashboard Generator - Main Entry Point
Orchestrates GitHub data fetching and Excel report generation
"""
import sys
import os
from pathlib import Path
import argparse
import logging
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))
from github_api import fetch_github_data
from excel_generator import generate_excel_report

def setup_logging(config: dict) -> logging.Logger:
    log_dir = Path(config["logging"]["log_dir"])
    log_dir.mkdir(exist_ok=True)
    log_filename = config["logging"]["log_file"].format(
        date=datetime.now().strftime("%Y%m%d")
    )
    log_path = log_dir / log_filename
    logging.basicConfig(
        level=getattr(logging, config["logging"]["level"]),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Starting IT Dashboard Generation - {datetime.now()}")
    return logger

def main():
    parser = argparse.ArgumentParser(
        description="Generate IT Dashboard from GitHub data"
    )
    parser.add_argument(
        "--config", 
        default="config/settings.json",
        help="Configuration file path (default: config/settings.json)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without generating reports"
    )
    args = parser.parse_args()
    try:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Configuration file not found: {config_path}")
            sys.exit(1)
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger = setup_logging(config)
        if args.dry_run:
            logger.info("DRY RUN MODE - No reports will be generated")
        logger.info("Fetching GitHub repository data...")
        data = fetch_github_data(str(config_path))
        if data.empty:
            logger.error("No data retrieved from GitHub API")
            sys.exit(1)
        logger.info(f"Successfully fetched data for {len(data)} repositories")
        if not args.dry_run:
            logger.info("Generating Excel dashboard report...")
            report_path = generate_excel_report(data, str(config_path))
            logger.info(f"✓ Dashboard report generated successfully: {report_path}")
        else:
            logger.info("Dry run complete - no report generated")
        logger.info("IT Dashboard generation completed successfully")
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"Dashboard generation failed: {e}")
        else:
            print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
