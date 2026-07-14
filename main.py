#!/usr/bin/env python3
"""
Medicament Barcode Database Scraper - Algeria
Scrapes pharmaceutical barcodes and exports to CSV/JSON
"""

import click
import json
import os
from pathlib import Path
from loguru import logger
from datetime import datetime

from scrapers.pharmnet_scraper import PharmnetScraper
from scrapers.dawa_scraper import DawaScraper
from utils.exporter import DataExporter


class BarcodeScraperPipeline:
    """Pipeline for scraping barcode data."""

    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.output_dir = Path(self.config["output"]["directory"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.exporter = DataExporter(self.config)

    def _load_config(self, config_path):
        """Load configuration from JSON file."""
        if not Path(config_path).exists():
            logger.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Configuration file {config_path} not found")
        
        with open(config_path, "r") as f:
            return json.load(f)

    def _setup_logging(self):
        """Configure logging."""
        log_dir = Path("./logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.remove()  # Remove default handler
        logger.add(
            log_dir / "scraper.log",
            level="INFO",
            rotation="500 MB"
        )
        logger.add(
            lambda msg: print(msg, end=""),  # Console output
            level="INFO"
        )

    def scrape(self, source="all", format="csv"):
        """Scrape barcodes from configured sources."""
        logger.info(f"Starting scrape from source: {source}")
        logger.info(f"Output format: {format}")
        
        all_data = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # PharmNet-DZ
        if source in ["all", "pharmnet"] and self.config["scrapers"]["pharmnet"]["enabled"]:
            logger.info("\n" + "="*50)
            logger.info("Scraping PharmNet-DZ...")
            logger.info("="*50)
            try:
                scraper = PharmnetScraper(self.config)
                data = scraper.scrape()
                all_data.extend(data)
                
                # Export individual source
                output_file = self.exporter.export(
                    data, 
                    f"barcodes_pharmnet_{timestamp}",
                    format
                )
                logger.info(f"✓ Scraped {len(data)} medicines from PharmNet-DZ")
                logger.info(f"✓ Exported to {output_file}")
            except Exception as e:
                logger.error(f"PharmNet-DZ scraping failed: {e}")
        
        # DAWA
        if source in ["all", "dawa"] and self.config["scrapers"]["dawa"]["enabled"]:
            logger.info("\n" + "="*50)
            logger.info("Scraping DAWA...")
            logger.info("="*50)
            try:
                scraper = DawaScraper(self.config)
                data = scraper.scrape()
                all_data.extend(data)
                
                # Export individual source
                output_file = self.exporter.export(
                    data, 
                    f"barcodes_dawa_{timestamp}",
                    format
                )
                logger.info(f"✓ Scraped {len(data)} medicines from DAWA")
                logger.info(f"✓ Exported to {output_file}")
            except Exception as e:
                logger.error(f"DAWA scraping failed: {e}")
        
        # Export combined data if multiple sources
        if len(all_data) > 0 and source == "all":
            logger.info("\n" + "="*50)
            logger.info("Combining all sources...")
            logger.info("="*50)
            output_file = self.exporter.export(
                all_data, 
                f"combined_barcodes_{timestamp}",
                format
            )
            logger.info(f"✓ Total: {len(all_data)} medicines")
            logger.info(f"✓ Combined file: {output_file}")
        
        logger.info("\n" + "="*50)
        logger.info("✓ Scraping completed!")
        logger.info("="*50)
        logger.info(f"Output directory: {self.output_dir.absolute()}")
        
        return all_data


@click.command()
@click.option(
    "--scrape", 
    is_flag=True, 
    help="Run scraping"
)
@click.option(
    "--source", 
    default="all", 
    type=click.Choice(["all", "pharmnet", "dawa"]),
    help="Scrape source: all, pharmnet, or dawa"
)
@click.option(
    "--format", 
    default="csv", 
    type=click.Choice(["csv", "json"]),
    help="Output format: csv or json"
)
@click.option(
    "--config", 
    default="config.json", 
    help="Configuration file path"
)
def main(scrape, source, format, config):
    """Medicament Barcode Database Scraper - Algeria."""
    
    if not scrape:
        click.echo("Use --scrape to start scraping. Example:")
        click.echo("  python main.py --scrape --source pharmnet --format csv")
        click.echo("  python main.py --scrape --source all --format json")
        return
    
    try:
        pipeline = BarcodeScraperPipeline(config)
        pipeline.scrape(source=source, format=format)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
