"""
DAWA Scraper
Scrapes medicament data and barcodes from medicamentdz.com
"""

import requests
from bs4 import BeautifulSoup
import time
from loguru import logger
from typing import List, Dict


class DawaScraper:
    """Scrapes pharmaceutical data from DAWA (medicamentdz.com)."""
    
    def __init__(self, config):
        self.config = config
        self.base_url = config["scrapers"]["dawa"]["url"]
        self.timeout = config["scrapers"]["dawa"]["timeout"]
        self.delay = config["scrapers"]["dawa"]["delay"]
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def scrape(self) -> List[Dict]:
        """Scrape all medicines and barcodes from DAWA."""
        logger.info(f"Connecting to {self.base_url}")
        medicines = []
        
        try:
            url = self.base_url
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract medicine links
            medicine_links = soup.select("a.medicine-link, a[href*='medicament']")
            
            logger.info(f"Found {len(medicine_links)} medicine links")
            
            for i, link in enumerate(medicine_links):
                if i % 10 == 0:
                    logger.info(f"Processing: {i+1}/{len(medicine_links)} medicines...")
                
                try:
                    medicine = self._extract_medicine_data(link)
                    if medicine:
                        medicines.append(medicine)
                    
                    time.sleep(self.delay)
                except Exception as e:
                    logger.debug(f"Failed to extract medicine: {e}")
                    continue
            
            return medicines
        
        except Exception as e:
            logger.error(f"DAWA scraping failed: {e}")
            return medicines
    
    def _extract_medicine_data(self, link) -> Dict:
        """Extract medicine data from a medicine page."""
        try:
            url = link.get("href")
            if not url.startswith("http"):
                url = f"{self.base_url}/{url}"
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract medicine details
            name = soup.select_one(".medicine-name, .med-name, h1")
            barcode = soup.select_one(".medicine-barcode, .barcode, [class*='barcode']")
            dosage = soup.select_one(".medicine-dosage, .dosage, [class*='dosage']")
            manufacturer = soup.select_one(".medicine-manufacturer, .manufacturer, [class*='manufacturer']")
            therapeutic = soup.select_one(".therapeutic, [class*='therapeutic']")
            
            medicine_data = {
                "commercial_name": name.text.strip() if name else None,
                "barcode": barcode.text.strip() if barcode else None,
                "dosage": dosage.text.strip() if dosage else None,
                "manufacturer": manufacturer.text.strip() if manufacturer else None,
                "therapeutic_class": therapeutic.text.strip() if therapeutic else None,
                "source": "DAWA",
                "url": url,
            }
            
            if medicine_data.get("commercial_name"):
                return medicine_data
            
            return None
        
        except Exception as e:
            logger.debug(f"Error extracting medicine data: {e}")
            return None
