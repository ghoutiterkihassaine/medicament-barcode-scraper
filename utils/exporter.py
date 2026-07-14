"""
Data Exporter
Exports scraped data to CSV and JSON formats
"""

import csv
import json
from pathlib import Path
from loguru import logger
from typing import List, Dict


class DataExporter:
    """Exports barcode data to CSV and JSON files."""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = Path(config["output"]["directory"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, data: List[Dict], filename: str, format: str = "csv") -> str:
        """Export data to file."""
        if format == "csv":
            return self._export_csv(data, filename)
        elif format == "json":
            return self._export_json(data, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_csv(self, data: List[Dict], filename: str) -> str:
        """Export data to CSV file."""
        if not data:
            logger.warning(f"No data to export for {filename}")
            return None
        
        filepath = self.output_dir / f"{filename}.csv"
        
        try:
            # Get all unique keys from all dictionaries
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"✓ Exported CSV: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            return None
    
    def _export_json(self, data: List[Dict], filename: str) -> str:
        """Export data to JSON file."""
        if not data:
            logger.warning(f"No data to export for {filename}")
            return None
        
        filepath = self.output_dir / f"{filename}.json"
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✓ Exported JSON: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            return None
