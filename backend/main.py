"""FastAPI application for HousingMatcher.

This module defines the web server that receives Jotform webhook calls
for landlords and applicants, stores submissions in a database, and
exposes endpoints for listing units, applicants, and computing
matches. It also contains a root endpoint to verify that the service
is running.

To run this application locally:

```bash
uvicorn housingmatcher.main:app --reload
```

When deploying, use a production WSGI server (e.g., uvicorn with
gunicorn) and configure environment variables for API keys and the
Apps Script URL.
"""

import os
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import database
import utils

# Import sync module (lazy import to avoid circular dependencies)
try:
    import sync_google_sheets
    SYNC_AVAILABLE = True
except ImportError:
    SYNC_AVAILABLE = False

# Ensure all models are registered before creating the tables.
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="HousingMatcher API")

# CORS configuration
# In production, update allow_origins to include your WordPress domain
# Example: allow_origins=["https://your-wordpress-site.com", "http://localhost:5173"]
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    # Split by comma and strip whitespace
    CORS_ORIGINS = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
else:
    # Default to allow all origins for development
    CORS_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    """A simple health check endpoint."""
    return {"message": "HousingMatcher API is running"}


@app.get("/debug/stats")
async def debug_stats(db: Session = Depends(database.get_db)) -> dict:
    """Debug endpoint to check what's in the database."""
    units_count = db.query(models.Unit).count()
    applicants_count = db.query(models.Applicant).count()
    master_units_count = db.query(models.MasterUnit).count()
    
    units = db.query(models.Unit).limit(5).all()
    applicants = db.query(models.Applicant).limit(5).all()
    master_units = db.query(models.MasterUnit).limit(5).all()
    
    return {
        "counts": {
            "units": units_count,
            "applicants": applicants_count,
            "master_units": master_units_count,
        },
        "sample_units": [
            {"id": u.id, "property_name": u.property_name, "address": u.address}
            for u in units
        ],
        "sample_applicants": [
            {"id": a.id, "name": a.name, "income": a.income}
            for a in applicants
        ],
        "sample_master_units": [
            {"id": mu.id, "complex_apartment": mu.complex_apartment, "address": mu.address}
            for mu in master_units
        ]
    }


@app.post("/sync/google-sheets")
async def sync_google_sheets_endpoint(db: Session = Depends(database.get_db)) -> dict:
    """Sync data from Google Sheets to the backend database.
    
    This endpoint:
    1. Reads master units from MASTER_SPREADSHEET_ID (CYC - Accessible Housing)
    2. Reads JotForm units from DATABASE_SPREADSHEET_ID (accessiblehousingdatabase)
    3. Updates the local database with the synced data
    
    This should be called periodically (e.g., via cron job) or manually to keep
    the backend database in sync with Google Sheets.
    
    The Apps Script writes new submissions to both sheets, but this sync ensures
    the backend has all existing data from Google Sheets.
    """
    try:
        import sync_google_sheets as sync_module
        result = sync_module.sync_all(db)
        return result
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Sync error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.get("/sync/google-sheets")
async def sync_google_sheets_get(db: Session = Depends(database.get_db)) -> dict:
    """GET endpoint for syncing (useful for manual triggers or cron jobs)."""
    return await sync_google_sheets_endpoint(db)


@app.post("/backfill/google-sheets")
async def backfill_google_sheets_endpoint(db: Session = Depends(database.get_db)) -> dict:
    """Backfill existing database records to Google Sheets.
    
    This endpoint sends all existing units and applicants from the database
    to Google Sheets via the Apps Script. Useful for:
    - Backfilling old submissions
    - Resyncing data if Google Sheets got out of sync
    - Testing the Google Sheets connection
    
    Returns statistics on how many records were sent.
    """
    try:
        units = db.query(models.Unit).all()
        applicants = db.query(models.Applicant).all()
        
        units_success = 0
        units_errors = 0
        applicants_success = 0
        applicants_errors = 0
        
        # Backfill units
        for unit in units:
            try:
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
                try:
                    utils.send_to_apps_script(unit_data, sheet="Units")
                    units_success += 1
                except Exception as e:
                    units_errors += 1
                    print(f"⚠️ Error backfilling unit {unit.id}: {e}")
            except Exception as e:
                units_errors += 1
                print(f"⚠️ Error processing unit {unit.id}: {e}")
        
        # Backfill applicants
        for applicant in applicants:
            try:
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
                try:
                    utils.send_to_apps_script(applicant_data, sheet="Applicants")
                    applicants_success += 1
                except Exception as e:
                    applicants_errors += 1
                    print(f"⚠️ Error backfilling applicant {applicant.id}: {e}")
            except Exception as e:
                applicants_errors += 1
                print(f"⚠️ Error processing applicant {applicant.id}: {e}")
        
        return {
            "status": "success",
            "units": {
                "total": len(units),
                "success": units_success,
                "errors": units_errors
            },
            "applicants": {
                "total": len(applicants),
                "success": applicants_success,
                "errors": applicants_errors
            }
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Backfill error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Backfill failed: {str(e)}")


@app.get("/backfill/google-sheets")
async def backfill_google_sheets_get(db: Session = Depends(database.get_db)) -> dict:
    """GET endpoint for backfilling (useful for manual triggers)."""
    return await backfill_google_sheets_endpoint(db)


@app.post("/webhook/landlord")
async def landlord_webhook(
    payload: dict, db: Session = Depends(database.get_db)
) -> dict:
    """Receive landlord submissions from Jotform and store them.

    The payload is expected to be the JSON body Jotform sends to
    webhooks. It contains a `submission_id` and an `answers` object.

    Returns a status message.
    """
    unit_data = utils.parse_unit(payload)
    if not unit_data.get("id"):
        raise HTTPException(status_code=400, detail="submission_id missing in payload")
    # Upsert: if the unit already exists, update it; otherwise create.
    unit = db.get(models.Unit, unit_data["id"])
    if unit:
        # Update existing unit - set all fields from parsed data
        for key, val in unit_data.items():
            try:
                setattr(unit, key, val)
            except AttributeError:
                # Skip fields that don't exist on the model (shouldn't happen, but be safe)
                pass
    else:
        # Create new unit - pass all fields from parsed data
        unit = models.Unit(**unit_data)
        db.add(unit)
    db.commit()
    
    # JotForm units from landlords are listings, so ensure availability is set
    if not unit.availability or unit.availability.lower() not in ["available", "waitlist", "occupied"]:
        unit.availability = "available"
        db.commit()
    
    # Send to Google Sheet. Use a try/except to avoid failing webhook.
    # Filter out "data" field before sending - only send schema fields
    sheet_data = {k: v for k, v in unit_data.items() if k != "data"}
    # Ensure availability is included in sheet data
    if "availability" not in sheet_data or not sheet_data["availability"]:
        sheet_data["availability"] = "available"
    try:
        utils.send_to_apps_script(sheet_data, sheet="Units")
        print(f"✅ Successfully sent unit {unit_data['id']} to Google Sheets")
    except Exception as exc:
        print(f"⚠️ Apps Script send failed: {exc}")
    return {"status": "received"}


@app.post("/webhook/applicant")
async def applicant_webhook(
    payload: dict, db: Session = Depends(database.get_db)
) -> dict:
    """Receive applicant submissions from Jotform and store them."""
    applicant_data = utils.parse_applicant(payload)
    if not applicant_data.get("id"):
        raise HTTPException(status_code=400, detail="submission_id missing in payload")
    applicant = db.get(models.Applicant, applicant_data["id"])
    if applicant:
        # Update existing applicant - set all fields from parsed data
        for key, val in applicant_data.items():
            try:
                setattr(applicant, key, val)
            except AttributeError:
                # Skip fields that don't exist on the model (shouldn't happen, but be safe)
                pass
    else:
        # Create new applicant - pass all fields from parsed data
        applicant = models.Applicant(**applicant_data)
        db.add(applicant)
    db.commit()
    # Send to Google Sheet
    # Filter out "data" field before sending - only send schema fields
    sheet_data = {k: v for k, v in applicant_data.items() if k != "data"}
    try:
        utils.send_to_apps_script(sheet_data, sheet="Applicants")
        print(f"✅ Successfully sent applicant {applicant_data['id']} to Google Sheets")
    except Exception as exc:
        print(f"⚠️ Apps Script send failed: {exc}")
    return {"status": "received"}


@app.get("/units", response_model=List[dict])
async def list_units(db: Session = Depends(database.get_db)) -> List[dict]:
    """Return all units stored in the database (both JotForm units and master units).
    
    Returns a unified list with both unit types, normalized to a common schema.
    """
    result = []
    
    # Get JotForm units (these are from landlords and should be available)
    units = db.query(models.Unit).all()
    for unit in units:
        # JotForm units are from landlords listing properties, so they should be available
        # Use the availability field if set, otherwise default to "available"
        availability = unit.availability or "available"
        if availability.lower() not in ["available", "waitlist", "occupied"]:
            availability = "available"  # Default to available for JotForm listings
        
        result.append({
            "id": unit.id or "",
            "type": "jotform",  # Mark as JotForm unit
            "property_name": unit.property_name or "",
            "address": unit.address or "",
            "rent": unit.rent if unit.rent is not None else "",
            "rent_display": str(unit.rent) if unit.rent is not None else "",
            "accessibility_features": unit.accessibility_features or "",
            "contact": unit.contact or "",
            "photo_url": unit.photo_url or "",
            "availability": availability,
            "city": "",
            "zip_code": "",
        })
    
    # Get master units and group by complex/apartment name
    master_units = db.query(models.MasterUnit).all()
    
    # Group units by complex/apartment name
    complexes = {}
    for master_unit in master_units:
        complex_name = master_unit.complex_apartment or "Unknown Complex"
        
        if complex_name not in complexes:
            # Initialize complex data with first unit's info
            address_parts = [master_unit.address or ""]
            if master_unit.city:
                address_parts.append(master_unit.city)
            if master_unit.zip_code:
                address_parts.append(master_unit.zip_code)
            full_address = ", ".join(filter(None, address_parts)) or master_unit.address or ""
            
            # Build contact info - prefer parsed fields, fall back to raw
            contact_display = ""
            if master_unit.landlord_phone and master_unit.landlord_email:
                contact_display = f"{master_unit.landlord_phone}; {master_unit.landlord_email}"
            elif master_unit.landlord_phone:
                contact_display = master_unit.landlord_phone
            elif master_unit.landlord_email:
                contact_display = master_unit.landlord_email
            elif master_unit.landlord_contact_raw:
                contact_display = master_unit.landlord_contact_raw
            
            complexes[complex_name] = {
                "id": f"complex_{hash(complex_name) % 1000000}",  # Generate ID from complex name
                "type": "master",
                "property_name": complex_name,
                "address": full_address,
                "rent": master_unit.rent or "",
                "rent_display": master_unit.rent or "",
                "accessibility_features": master_unit.accessibility_features or "",
                "contact": contact_display,
                "landlord_name": master_unit.landlord_name or "",
                "landlord_contact_raw": master_unit.landlord_contact_raw or "",
                "landlord_phone": master_unit.landlord_phone or "",
                "landlord_email": master_unit.landlord_email or "",
                "photo_url": "",
                "city": master_unit.city or "",
                "zip_code": master_unit.zip_code or "",
                "income_range": master_unit.income_range or "",
                "age_range": master_unit.age_range or "",
                "transportation": master_unit.transportation or "",
                "stores": master_unit.stores or "",
                "building_features": master_unit.building_features or "",
                "apartment_features": master_unit.apartment_features or "",
                "notes": master_unit.notes or "",
                "units_available": 0,  # Count of available units
                "total_units": 0,  # Total units in complex
                "availability": "N/A",
            }
        
        # Count units
        complexes[complex_name]["total_units"] += 1
        
        # Count available units
        if master_unit.is_available and master_unit.is_available.upper() == "Y":
            complexes[complex_name]["units_available"] += 1
        elif master_unit.units_available is not None and master_unit.units_available > 0:
            complexes[complex_name]["units_available"] += 1
    
    # Convert grouped complexes to list and set availability status
    # Note: Master database units don't have availability info, so we show "Contact for availability"
    for complex_data in complexes.values():
        if complex_data["units_available"] > 0:
            complex_data["availability"] = f"Available ({complex_data['units_available']} units)"
        elif complex_data["total_units"] > 0:
            # Master database doesn't track availability, so show neutral message
            complex_data["availability"] = "Contact for availability"
        else:
            complex_data["availability"] = "Contact for availability"
    
    # Add grouped complexes to result
    result.extend(complexes.values())
    
    return result


@app.get("/applicants", response_model=List[dict])
async def list_applicants(db: Session = Depends(database.get_db)) -> List[dict]:
    """Return all applicants stored in the database, normalized to match Google Sheet schema."""
    applicants = db.query(models.Applicant).all()
    return [
        {
            "id": applicant.id or "",
            "name": applicant.name or "",
            "income": applicant.income if applicant.income is not None else "",
            "voucher_type": applicant.voucher_type or "",
            "accessibility_needs": applicant.accessibility_needs or "",
            "location": applicant.location or "",
            "household_size": (
                applicant.household_size if applicant.household_size is not None else ""
            ),
            "contact": applicant.contact or "",
        }
        for applicant in applicants
    ]


@app.get("/match/{applicant_id}")
async def match_units(
    applicant_id: str, db: Session = Depends(database.get_db)
) -> dict:
    """Compute match scores between a specific applicant and all units (both types).

    Args:
        applicant_id: The submission ID of the applicant.
        db: Database session.

    Returns:
        A dict with the applicant ID and a list of unit matches sorted
        by descending score. Each match includes unit_id, score, type, and reasons.
    """
    applicant: models.Applicant | None = db.get(models.Applicant, applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    matches = []
    
    # Match against JotForm units
    units = db.query(models.Unit).all()
    for unit in units:
        score, reasons = utils.calculate_score(applicant, unit)
        matches.append(
            {
                "unit_id": unit.id,
                "type": "jotform",
                "score": round(score, 3),  # Round to 3 decimal places for readability
                "reasons": reasons,
            }
        )
    
    # Match against master units (grouped by complex)
    master_units = db.query(models.MasterUnit).all()
    
    # Group units by complex for matching
    complexes_for_matching = {}
    for master_unit in master_units:
        complex_name = master_unit.complex_apartment or "Unknown Complex"
        if complex_name not in complexes_for_matching:
            complexes_for_matching[complex_name] = {
                "master_unit": master_unit,  # Use first unit as representative
                "units_available": 0,
            }
        # Count available units
        if master_unit.is_available and master_unit.is_available.upper() == "Y":
            complexes_for_matching[complex_name]["units_available"] += 1
        elif master_unit.units_available is not None and master_unit.units_available > 0:
            complexes_for_matching[complex_name]["units_available"] += 1
    
    # Match against each complex (using representative unit)
    for complex_name, complex_data in complexes_for_matching.items():
        master_unit = complex_data["master_unit"]
        score, reasons = utils.calculate_score_master_unit(applicant, master_unit)
        # Don't add availability info to reasons (user requested to remove availability from reasons)
        matches.append(
            {
                "unit_id": f"complex_{hash(complex_name) % 1000000}",  # Match the grouped ID format
                "type": "master",
                "score": round(score, 3),
                "reasons": reasons,
            }
        )
    
    # Sort by score descending, then by unit_id for deterministic ordering on ties
    matches.sort(key=lambda x: (-x["score"], x["unit_id"]))
    return {"applicant_id": applicant_id, "matches": matches}


@app.post("/import/master-units")
async def import_master_units(
    units_data: List[dict], db: Session = Depends(database.get_db)
) -> dict:
    """Import master units from Google Sheets or other source.
    
    Accepts a list of unit dictionaries matching the master sheet structure.
    Each unit should have keys like: Complex/Apartment, Address, City, Zip Code,
    Rent, Income Range, Age Range, Accessible Units, Units Available,
    Accessibility Features, Notes.
    
    Returns the number of units imported/updated.
    """
    imported = 0
    updated = 0
    
    for row_data in units_data:
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
