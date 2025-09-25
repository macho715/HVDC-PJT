"""
HVDC Excel Reporter - Data Loading Module
"""
import pandas as pd
from pathlib import Path
import logging
from src import config

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Handles loading and initial preparation of HVDC data from Excel files.
    """
    def __init__(self):
        self.hitachi_file = config.HITACHI_FILE
        self.simense_file = config.SIMENSE_FILE

    def load_real_hvdc_data(self):
        """
        Loads and merges the raw data from HITACHI and SIMENSE Excel files.
        """
        logger.info("📂 Loading raw HVDC data...")
        
        combined_dfs = []
        
        try:
            # Load HITACHI data
            if self.hitachi_file.exists():
                logger.info(f"📊 Loading HITACHI data from: {self.hitachi_file}")
                hitachi_data = pd.read_excel(self.hitachi_file, engine='openpyxl')
                hitachi_data.columns = hitachi_data.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
                hitachi_data['Vendor'] = 'HITACHI'
                hitachi_data['Source_File'] = 'HITACHI(HE)'
                combined_dfs.append(hitachi_data)
                logger.info(f"✅ HITACHI data loaded: {len(hitachi_data)} records")

            # Load SIMENSE data
            if self.simense_file.exists():
                logger.info(f"📊 Loading SIMENSE data from: {self.simense_file}")
                simense_data = pd.read_excel(self.simense_file, engine='openpyxl')
                simense_data.columns = simense_data.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
                simense_data['Vendor'] = 'SIMENSE'
                simense_data['Source_File'] = 'SIMENSE(SIM)'
                combined_dfs.append(simense_data)
                logger.info(f"✅ SIMENSE data loaded: {len(simense_data)} records")

            if not combined_dfs:
                raise ValueError("No data files found to load.")

            # Combine dataframes
            combined_data = pd.concat(combined_dfs, ignore_index=True, sort=False)
            combined_data.columns = combined_data.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
            logger.info(f"🔗 Data combined successfully: {len(combined_data)} total records")
            
            return combined_data

        except Exception as e:
            logger.error(f"❌ Failed to load data: {str(e)}")
            raise