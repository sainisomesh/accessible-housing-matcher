"""Sync data from Google Sheets to the backend database.

This module reads data from both Google Sheets:
1. MASTER_SPREADSHEET_ID - Existing master units (CYC - Accessible Housing)
2. DATABASE_SPREADSHEET_ID - JotForm intake units (accessiblehousingdatabase)

Uses Google Sheets API v4 or public CSV export format.
"""

import os
import sys
from pathlib import Path
import requests
from typing import List, Dict, Any

# Add parent directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import models and utils
import models
import utils
from sqlalchemy.orm import Session

# Google Sheets IDs from Apps Script
MASTER_SPREADSHEET_ID = '19is049RiNyvLRpo0kpU1Xub8SaI_9XkO5a7Y2ILkC5U'
DATABASE_SPREADSHEET_ID = '19FO0fWMxrCjPXLIXJYAAipJAgqpN79yyfagv5IPPiHg'

# Google Sheets API key (optional, for private sheets)
# For public sheets, we can use CSV export format
GOOGLE_SHEETS_API_KEY = os.getenv("GOOGLE_SHEETS_API_KEY", "")


def fetch_sheet_as_csv(spreadsheet_id: str, sheet_name: str = "Sheet1") -> List[List[str]]:
    """Fetch a Google Sheet as CSV format.
    
    This works for public sheets. For private sheets, you need API key.
    
    Args:
        spreadsheet_id: The Google Sheets spreadsheet ID
        sheet_name: The name of the sheet/tab (default: "Sheet1")
    
    Returns:
        List of rows, where each row is a list of cell values
    """
    # Use CSV export format (works for public sheets)
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse CSV
        import csv
        from io import StringIO
        
        csv_data = StringIO(response.text)
        reader = csv.reader(csv_data)
        rows = list(reader)
        
        return rows
    except Exception as e:
        print(f"❌ Error fetching sheet {sheet_name} from {spreadsheet_id}: {e}")
        return []


def fetch_sheet_as_json(spreadsheet_id: str, sheet_name: str = "Sheet1", api_key: str = "") -> List[Dict[str, Any]]:
    """Fetch a Google Sheet using Google Sheets API v4.
    
    Args:
        spreadsheet_id: The Google Sheets spreadsheet ID
        sheet_name: The name of the sheet/tab
        api_key: Google Sheets API key (optional for public sheets)
    
    Returns:
        List of dictionaries, where keys are column headers
    """
    if api_key:
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}?key={api_key}"
    else:
        # Try public access
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        values = data.get("values", [])
        if not values:
            return []
        
        # First row is headers
        headers = [h.strip() for h in values[0]]
        
        # Convert rows to dictionaries
        result = []
        for row in values[1:]:
            # Pad row to match header length
            row_padded = row + [""] * (len(headers) - len(row))
            row_dict = dict(zip(headers, row_padded))
            result.append(row_dict)
        
        return result
    except Exception as e:
        print(f"❌ Error fetching sheet via API {sheet_name} from {spreadsheet_id}: {e}")
        # Fallback to CSV
        return fetch_sheet_csv_as_dict(spreadsheet_id, sheet_name)


def fetch_sheet_csv_as_dict(spreadsheet_id: str, sheet_name: str = "Sheet1") -> List[Dict[str, Any]]:
    """Fetch a Google Sheet as CSV and convert to list of dictionaries.
    
    Args:
        spreadsheet_id: The Google Sheets spreadsheet ID
        sheet_name: The name of the sheet/tab
    
    Returns:
        List of dictionaries, where keys are column headers
    """
    rows = fetch_sheet_as_csv(spreadsheet_id, sheet_name)
    if not rows:
        return []
    
    # First row is headers
    headers = [h.strip() for h in rows[0]]
    
    # Convert rows to dictionaries
    result = []
    for row in rows[1:]:
        # Pad row to match header length
        row_padded = row + [""] * (len(headers) - len(row))
        row_dict = dict(zip(headers, row_padded))
        result.append(row_dict)
    
    return result


def sync_master_units(db: Session) -> Dict[str, Any]:
    """Sync master units from Google Sheets to database.
    
    Reads from MASTER_SPREADSHEET_ID, sheet "Sheet1" (or the sheet name that contains master units).
    
    Returns:
        Dict with sync statistics
    """
    print("🔄 Syncing master units from Google Sheets...")
    
    # Try different sheet names
    sheet_names = ["Sheet1", "Units", "Master", "CYC - Accessible Housing"]
    master_units_data = []
    
    for sheet_name in sheet_names:
        print(f"   Trying sheet: {sheet_name}")
        data = fetch_sheet_csv_as_dict(MASTER_SPREADSHEET_ID, sheet_name)
        if data and len(data) > 0:
            print(f"   ✅ Found {len(data)} rows in {sheet_name}")
            master_units_data = data
            break
    
    if not master_units_data:
        print("   ⚠️ No master units found in any sheet")
        return {"status": "no_data", "imported": 0, "updated": 0}
    
    imported = 0
    updated = 0
    
    for row_data in master_units_data:
        try:
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
        except Exception as e:
            print(f"   ⚠️ Error processing master unit row: {e}")
            continue
    
    db.commit()
    print(f"   ✅ Master units sync complete: {imported} imported, {updated} updated")
    
    return {
        "status": "success",
        "imported": imported,
        "updated": updated,
        "total": imported + updated
    }


def sync_jotform_units(db: Session) -> Dict[str, Any]:
    """Sync JotForm units from Google Sheets to database.
    
    Reads from DATABASE_SPREADSHEET_ID, sheet "Units" (or "Sheet1").
    These are units that came through JotForm webhooks and were written to Google Sheets.
    
    Returns:
        Dict with sync statistics
    """
    print("🔄 Syncing JotForm units from Google Sheets...")
    
    # Try different sheet names
    sheet_names = ["Units", "Sheet1"]
    units_data = []
    
    for sheet_name in sheet_names:
        print(f"   Trying sheet: {sheet_name}")
        data = fetch_sheet_csv_as_dict(DATABASE_SPREADSHEET_ID, sheet_name)
        if data and len(data) > 0:
            print(f"   ✅ Found {len(data)} rows in {sheet_name}")
            units_data = data
            break
    
    if not units_data:
        print("   ⚠️ No JotForm units found in any sheet")
        return {"status": "no_data", "imported": 0, "updated": 0}
    
    imported = 0
    updated = 0
    
    for row_data in units_data:
        try:
            # Convert Google Sheets row to Unit format
            # The row should have: id, property_name, address, rent, accessibility_features, contact, photo_url, availability
            unit_id = str(row_data.get("id", "")).strip()
            if not unit_id:
                continue
            
            # Check if unit already exists in database
            unit = db.get(models.Unit, unit_id)
            
            unit_data = {
                "id": unit_id,
                "data": row_data,  # Store raw data
                "property_name": str(row_data.get("property_name", "")).strip() or None,
                "address": str(row_data.get("address", "")).strip() or None,
                "rent": _parse_rent(row_data.get("rent", "")),
                "accessibility_features": str(row_data.get("accessibility_features", "")).strip() or None,
                "contact": str(row_data.get("contact", "")).strip() or None,
                "photo_url": str(row_data.get("photo_url", "")).strip() or None,
                "availability": str(row_data.get("availability", "")).strip() or None,
            }
            
            if unit:
                # Update existing unit
                for key, val in unit_data.items():
                    try:
                        setattr(unit, key, val)
                    except AttributeError:
                        pass
                updated += 1
            else:
                # Create new unit
                unit = models.Unit(**unit_data)
                db.add(unit)
                imported += 1
        except Exception as e:
            print(f"   ⚠️ Error processing JotForm unit row: {e}")
            continue
    
    db.commit()
    print(f"   ✅ JotForm units sync complete: {imported} imported, {updated} updated")
    
    return {
        "status": "success",
        "imported": imported,
        "updated": updated,
        "total": imported + updated
    }


def _parse_rent(rent_value: Any) -> int | None:
    """Parse rent value from Google Sheets (could be string or number)."""
    if rent_value is None or rent_value == "":
        return None
    try:
        # Try to extract number from string (e.g., "$1200" -> 1200)
        if isinstance(rent_value, (int, float)):
            return int(rent_value)
        import re
        rent_str = str(rent_value).replace(',', '').replace('$', '').strip()
        rent_match = re.search(r'\d+', rent_str)
        if rent_match:
            return int(rent_match.group())
    except (ValueError, AttributeError):
        pass
    return None


def sync_all(db: Session) -> Dict[str, Any]:
    """Sync both master units and JotForm units from Google Sheets.
    
    Returns:
        Dict with combined sync statistics
    """
    print("=" * 60)
    print("Starting Google Sheets Sync")
    print("=" * 60)
    
    master_result = sync_master_units(db)
    jotform_result = sync_jotform_units(db)
    
    total_imported = master_result.get("imported", 0) + jotform_result.get("imported", 0)
    total_updated = master_result.get("updated", 0) + jotform_result.get("updated", 0)
    
    print("=" * 60)
    print(f"Sync Complete: {total_imported} imported, {total_updated} updated")
    print("=" * 60)
    
    return {
        "status": "success",
        "master_units": master_result,
        "jotform_units": jotform_result,
        "total_imported": total_imported,
        "total_updated": total_updated,
    }

