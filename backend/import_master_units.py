#!/usr/bin/env python3
"""Script to import master units from Google Sheets into the database.

This script can be used to periodically sync master units from the Google Sheet
into the local database. You can run this manually or set it up as a scheduled task.

Usage:
    python import_master_units.py

The script expects a JSON file or can be modified to fetch directly from Google Sheets API.
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add current directory to path to import housingmatcher
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from housingmatcher import models, database, utils

# Ensure database tables exist
models.Base.metadata.create_all(bind=database.engine)


def import_from_json_file(file_path: str) -> Dict[str, Any]:
    """Import master units from a JSON file.
    
    The JSON file should be an array of objects, where each object represents
    a row from the master Google Sheet with keys like:
    - Complex/Apartment
    - Address
    - City
    - Zip Code
    - Rent
    - Income Range
    - Age Range
    - Accessible Units
    - Units Available
    - Accessibility Features
    - Notes
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("JSON file must contain an array of unit objects")
    
    db = next(database.get_db())
    imported = 0
    updated = 0
    
    try:
        for row_data in data:
            master_unit_data = utils.parse_master_unit(row_data)
            if not master_unit_data.get("id"):
                continue
            
            # Upsert: if the unit already exists, update it; otherwise create.
            master_unit = db.get(models.MasterUnit, master_unit_data["id"])
            if master_unit:
                # Update existing unit
                for key, val in master_unit_data.items():
                    try:
                        setattr(master_unit, key, val)
                    except AttributeError:
                        pass
                updated += 1
            else:
                # Create new unit
                master_unit = models.MasterUnit(**master_unit_data)
                db.add(master_unit)
                imported += 1
        
        db.commit()
        return {
            "status": "success",
            "imported": imported,
            "updated": updated,
            "total": imported + updated
        }
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def import_from_api(api_url: str) -> Dict[str, Any]:
    """Import master units by calling the backend API endpoint.
    
    This is useful when you want to import via the API rather than directly
    accessing the database.
    """
    # This would require the data to be fetched first (e.g., from Google Sheets API)
    # For now, this is a placeholder
    raise NotImplementedError("Direct API import not yet implemented. Use import_from_json_file instead.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_master_units.py <json_file_path>")
        print("\nExample:")
        print("  python import_master_units.py master_units.json")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        result = import_from_json_file(file_path)
        print(f"✅ Import successful!")
        print(f"   Imported: {result['imported']} units")
        print(f"   Updated: {result['updated']} units")
        print(f"   Total: {result['total']} units")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)

