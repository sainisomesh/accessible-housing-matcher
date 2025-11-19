#!/usr/bin/env python3
"""Backfill existing submissions to Google Sheets.

This script sends all existing units and applicants from the database
to Google Sheets via the Apps Script endpoint. Useful for:
1. Backfilling old submissions that were created before Google Sheets integration
2. Resyncing data if Google Sheets got out of sync
3. Testing the Google Sheets connection

Usage:
    python backfill_google_sheets.py
"""

import sys
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from housingmatcher import models, database, utils

def backfill_units():
    """Send all existing units to Google Sheets."""
    print("🔄 Backfilling units to Google Sheets...")
    
    db = next(database.get_db())
    try:
        units = db.query(models.Unit).all()
        print(f"   Found {len(units)} units in database")
        
        success_count = 0
        error_count = 0
        
        for unit in units:
            try:
                # Prepare unit data (same format as webhook)
                unit_data = {
                    "id": unit.id or "",
                    "property_name": unit.property_name or "",
                    "address": unit.address or "",
                    "rent": unit.rent if unit.rent is not None else "",
                    "accessibility_features": unit.accessibility_features or "",
                    "contact": unit.contact or "",
                    "photo_url": unit.photo_url or "",
                    "availability": unit.availability or "",
                }
                
                # Send to Google Sheets
                utils.send_to_apps_script(unit_data, sheet="Units")
                success_count += 1
                print(f"   ✅ Sent unit: {unit.id} - {unit.property_name}")
            except Exception as e:
                error_count += 1
                print(f"   ❌ Error sending unit {unit.id}: {e}")
        
        print(f"\n   Units backfill complete: {success_count} successful, {error_count} errors")
        return {"success": success_count, "errors": error_count}
    finally:
        db.close()


def backfill_applicants():
    """Send all existing applicants to Google Sheets."""
    print("\n🔄 Backfilling applicants to Google Sheets...")
    
    db = next(database.get_db())
    try:
        applicants = db.query(models.Applicant).all()
        print(f"   Found {len(applicants)} applicants in database")
        
        success_count = 0
        error_count = 0
        
        for applicant in applicants:
            try:
                # Prepare applicant data (same format as webhook)
                applicant_data = {
                    "id": applicant.id or "",
                    "name": applicant.name or "",
                    "income": applicant.income if applicant.income is not None else "",
                    "voucher_type": applicant.voucher_type or "",
                    "accessibility_needs": applicant.accessibility_needs or "",
                    "location": applicant.location or "",
                    "household_size": applicant.household_size if applicant.household_size is not None else "",
                    "contact": applicant.contact or "",
                }
                
                # Send to Google Sheets
                utils.send_to_apps_script(applicant_data, sheet="Applicants")
                success_count += 1
                print(f"   ✅ Sent applicant: {applicant.id} - {applicant.name}")
            except Exception as e:
                error_count += 1
                print(f"   ❌ Error sending applicant {applicant.id}: {e}")
        
        print(f"\n   Applicants backfill complete: {success_count} successful, {error_count} errors")
        return {"success": success_count, "errors": error_count}
    finally:
        db.close()


def backfill_all():
    """Backfill both units and applicants."""
    print("=" * 60)
    print("Google Sheets Backfill")
    print("=" * 60)
    print(f"Apps Script URL: {utils.APPS_SCRIPT_URL}\n")
    
    if not utils.APPS_SCRIPT_URL:
        print("❌ APPS_SCRIPT_URL is not configured!")
        print("   Set it in your environment or .env file")
        return
    
    units_result = backfill_units()
    applicants_result = backfill_applicants()
    
    print("\n" + "=" * 60)
    print("Backfill Summary:")
    print(f"   Units: {units_result['success']} successful, {units_result['errors']} errors")
    print(f"   Applicants: {applicants_result['success']} successful, {applicants_result['errors']} errors")
    print("=" * 60)


if __name__ == "__main__":
    backfill_all()

