"""Utility functions for HousingMatcher.

This module contains helper functions for:

* Parsing Jotform submission payloads into structured `Unit` and
  `Applicant` objects.
* Calculating a compatibility score between an applicant and a unit.
* Sending structured data to a Google Apps Script endpoint for logging
  into a Google Sheet.

Jotform submits submissions as a nested dictionary under the `answers`
key. The parsing functions below should be adapted as you learn more
about the actual field names in your forms.
"""

import os
from typing import Dict, Any

import requests

try:
    # ``python‑dotenv`` is optional. If the package is unavailable,
    # fallback to a no‑op loader so that local development can
    # continue without raising an ImportError.
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    # Define a dummy load_dotenv to satisfy type checkers and allow
    # the absence of the ``dotenv`` package. This function does
    # nothing; environment variables must be set via other means.
    def load_dotenv(*args: Any, **kwargs: Any) -> None:  # type: ignore
        return


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import ORM models only for type checking. At runtime these
    # imports are avoided to prevent unnecessary dependencies when
    # SQLAlchemy is unavailable (e.g., in the demo server). See
    # https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING
    from .models import Unit, Applicant, MasterUnit  # pragma: no cover

# Load environment variables from `.env` if present. This allows
# development outside of a hosted environment.
load_dotenv()

# Endpoint for posting data to the Google Apps Script. When deployed
# to a hosting platform you should set this value in the environment.
# Default to the new deployment ID if not set
APPS_SCRIPT_URL = os.getenv(
    "APPS_SCRIPT_DEPLOY_URL",
    "https://script.google.com/macros/s/AKfycbyV8pw9XZ3fiUxw1Ko1iB9AYWkna1bFR2eqnmenGLt7R8ODvPHBe2CL5UQ4BdiCYTE/exec"
)


def parse_unit(submission: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key fields from a landlord submission.

    The structure of a Jotform submission is documented in the Jotform
    API. Each answer is stored under `answers` with a key equal to the
    question's ID. Replace the keys below with those used in your
    landlord form.

    Maps to Google Sheet columns: id, property_name, address, rent,
    accessibility_features, contact, photo_url, availability

    Args:
        submission: Raw submission dictionary from Jotform.

    Returns:
        A dict with fields for creating a Unit instance, matching the
        Google Sheet schema.
    """
    answers = submission.get("answers", {})

    # Extract accessibility features and normalize to comma-separated lowercase
    accessibility_features = _parse_accessibility_features(answers)

    # Coerce rent to int, default to "" if parsing fails
    rent = _parse_int_answer(answers, "rent")

    unit_data = {
        "id": str(submission.get("submission_id", "")),
        "data": submission,
        "property_name": _parse_text_answer(answers, "property_name") or "",
        "address": _parse_text_answer(answers, "address") or "",
        "rent": (
            rent if rent is not None else None
        ),  # Store None, will convert to "" for sheet
        "accessibility_features": accessibility_features,
        "contact": _parse_text_answer(answers, "contact") or "",
        "photo_url": _parse_text_answer(answers, "photo_url") or "",
        "availability": _parse_text_answer(answers, "availability") or "",
    }
    return unit_data


def parse_applicant(submission: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key fields from an applicant submission.

    Maps to Google Sheet columns: id, name, income, voucher_type,
    accessibility_needs, location, household_size, contact

    Args:
        submission: Raw submission dictionary from Jotform.

    Returns:
        A dict with fields for creating an Applicant instance, matching
        the Google Sheet schema.
    """
    answers = submission.get("answers", {})

    # Extract accessibility needs and normalize to comma-separated lowercase
    accessibility_needs = _parse_accessibility_needs(answers)

    # Coerce income and household_size to int, default to None if parsing fails
    income = _parse_int_answer(answers, "income")
    household_size = _parse_int_answer(answers, "household_size")

    applicant_data = {
        "id": str(submission.get("submission_id", "")),
        "data": submission,
        "name": _parse_text_answer(answers, "name") or "",
        "income": (
            income if income is not None else None
        ),  # Store None, will convert to "" for sheet
        "voucher_type": _parse_text_answer(answers, "voucher_type") or "",
        "accessibility_needs": accessibility_needs,
        "location": _parse_text_answer(answers, "location") or "",
        "household_size": (
            household_size if household_size is not None else None
        ),  # Store None, will convert to "" for sheet
        "contact": _parse_text_answer(answers, "contact") or "",
    }
    return applicant_data


def parse_contact_info(contact_raw: str) -> tuple[str | None, str | None]:
    """Parse contact information from Landlord Contact field.
    
    Expected format: "PHONE_NUMBER; EMAIL_ADDRESS" (e.g., "216-961-9690; edeninfo@EDENcle.org")
    Also handles cases like "30; edeninfo@EDENcle.org" where "30" might be incomplete
    
    Args:
        contact_raw: The raw contact string from the sheet
    
    Returns:
        Tuple of (phone, email) where each can be None if not found
    """
    if not contact_raw or not isinstance(contact_raw, str):
        return None, None
    
    contact_raw = contact_raw.strip()
    if not contact_raw:
        return None, None
    
    # Split on semicolon
    parts = [p.strip() for p in contact_raw.split(";")]
    
    phone = None
    email = None
    
    for part in parts:
        if not part:
            continue
        # Check if it contains @ (email) - this is definitive
        if "@" in part:
            email = part
        # Check if it contains digits (phone) - but skip very short numbers that are likely errors
        elif any(c.isdigit() for c in part):
            # Only treat as phone if it has at least 7 digits (minimum valid phone number)
            digit_count = sum(c.isdigit() for c in part)
            if digit_count >= 7:
                phone = part
            # If it's shorter, it might be incomplete/error, so skip it
    
    return phone, email


def parse_master_unit(row_data: Dict[str, Any], row_id: str = None) -> Dict[str, Any]:
    """Parse a row from the master Google Sheet into a MasterUnit structure.
    
    New schema columns:
    Unit Number, Complex/Apartment, Landlord Name, Landlord Contact,
    Response Status, Is Available? (Y/N), Address, City, Zip Code, Rent,
    Income Range, Age Range, Accessibility Features, Transportation, Stores,
    Building Features, Apartment Features, Notes
    
    Args:
        row_data: Dictionary with keys matching master sheet column headers
        row_id: Optional ID for the unit (defaults to generated ID)
    
    Returns:
        A dict with fields for creating a MasterUnit instance.
    """
    # Generate ID from unit number + complex name + address if not provided
    if not row_id:
        unit_number = str(row_data.get("Unit Number", "") or row_data.get("unit_number", "")).strip()
        complex_name = str(row_data.get("Complex/Apartment", "") or row_data.get("complex_apartment", "")).strip()
        address = str(row_data.get("Address", "") or row_data.get("address", "")).strip()
        city = str(row_data.get("City", "") or row_data.get("city", "")).strip()
        zip_code = str(row_data.get("Zip Code", "") or row_data.get("zip_code", "")).strip()
        
        # Create unique ID using all identifying fields
        unique_string = f"{complex_name}|{unit_number}|{address}|{city}|{zip_code}"
        # Use a larger hash range and include more fields for uniqueness
        row_id = f"master_{abs(hash(unique_string)) % 100000000}"
    
    # Parse contact information
    landlord_contact_raw = str(row_data.get("Landlord Contact", "") or 
                               row_data.get("landlord_contact", "")).strip() or None
    landlord_phone, landlord_email = parse_contact_info(landlord_contact_raw or "")
    
    # Normalize accessibility features
    accessibility_features = str(row_data.get("Accessibility Features", "") or 
                                 row_data.get("accessibility_features", "")).strip()
    if accessibility_features:
        # Normalize to comma-separated lowercase
        features = [f.strip().lower() for f in accessibility_features.split(",") if f.strip()]
        accessibility_features = ",".join(sorted(set(features)))
    
    # Parse is_available (Y/N) to determine units_available for backwards compatibility
    is_available_str = str(row_data.get("Is Available? (Y /N)", "") or 
                          row_data.get("Is Available?", "") or
                          row_data.get("is_available", "")).strip().upper()
    units_available = None
    if is_available_str == "Y":
        units_available = 1  # At least 1 available
    elif is_available_str == "N":
        units_available = 0
    
    master_unit_data = {
        "id": row_id,
        "data": row_data,
        # Core identification
        "unit_number": str(row_data.get("Unit Number", "") or row_data.get("unit_number", "")).strip() or None,
        "complex_apartment": str(row_data.get("Complex/Apartment", "") or 
                                 row_data.get("complex_apartment", "")).strip() or None,
        # Contact information
        "landlord_name": str(row_data.get("Landlord Name", "") or 
                            row_data.get("landlord_name", "")).strip() or None,
        "landlord_contact_raw": landlord_contact_raw,
        "landlord_phone": landlord_phone,
        "landlord_email": landlord_email,
        # Status
        "response_status": str(row_data.get("Response Status", "") or 
                              row_data.get("response_status", "")).strip() or None,
        "is_available": is_available_str if is_available_str in ("Y", "N") else None,
        # Location
        "address": str(row_data.get("Address", "") or row_data.get("address", "")).strip() or None,
        "city": str(row_data.get("City", "") or row_data.get("city", "")).strip() or None,
        "zip_code": str(row_data.get("Zip Code", "") or row_data.get("zip_code", "")).strip() or None,
        # Financial and eligibility
        "rent": str(row_data.get("Rent", "") or row_data.get("rent", "")).strip() or None,
        "income_range": str(row_data.get("Income Range", "") or row_data.get("income_range", "")).strip() or None,
        "age_range": str(row_data.get("Age Range", "") or row_data.get("age_range", "")).strip() or None,
        # Features
        "accessibility_features": accessibility_features or None,
        "transportation": str(row_data.get("Transportation", "") or 
                             row_data.get("transportation", "")).strip() or None,
        "stores": str(row_data.get("Stores", "") or row_data.get("stores", "")).strip() or None,
        "building_features": str(row_data.get("Building Features", "") or 
                                row_data.get("building_features", "")).strip() or None,
        "apartment_features": str(row_data.get("Apartment Features", "") or 
                                 row_data.get("apartment_features", "")).strip() or None,
        # Additional
        "notes": str(row_data.get("Notes", "") or row_data.get("notes", "")).strip() or None,
        # Legacy fields for backwards compatibility
        "accessible_units": None,  # Not in new schema
        "units_available": units_available,
    }
    return master_unit_data


def calculate_score(applicant: "Applicant", unit: "Unit") -> tuple[float, list[str]]:
    """Compute a compatibility score between an applicant and a unit.

    Matching Algorithm:
    1. Parse accessibility_needs and accessibility_features into sets
    2. Base score = (|needs ∩ features| / |needs|), if needs non-empty; else 0.5 baseline
    3. +0.2 if rent ≤ max budget (infer max budget as income * 0.3 / 12 if no explicit budget)
    4. +0.1 if unit availability == "available"
    5. Cap at 1.0

    Args:
        applicant: An Applicant ORM instance.
        unit: A Unit ORM instance.

    Returns:
        A tuple of (float score, list[str] reasons) where score is between
        0 and 1, and reasons explains the scoring factors.
    """
    reasons = []

    # Parse accessibility features/needs into sets
    needs_set = set()
    features_set = set()

    if applicant.accessibility_needs:
        needs_set = {
            n.strip().lower()
            for n in applicant.accessibility_needs.split(",")
            if n.strip()
        }

    if unit.accessibility_features:
        features_set = {
            f.strip().lower()
            for f in unit.accessibility_features.split(",")
            if f.strip()
        }

    # Calculate base score based on accessibility match
    if needs_set:
        intersection = needs_set & features_set
        base_score = len(intersection) / len(needs_set)
        if intersection:
            # Only add positive reasons
            reasons.append(
                f"Accessibility match: {len(intersection)}/{len(needs_set)} needs met"
            )
        # Don't add negative reasons (accessibility mismatch)
    else:
        base_score = 0.5
        # Don't add "No accessibility requirements specified" - not useful

    score = base_score

    # Budget check: +0.2 if rent ≤ max budget
    # Infer max budget as income * 0.3 / 12 (30% of monthly income) if no explicit budget
    max_budget = None
    if applicant.income is not None:
        max_budget = int(applicant.income * 0.3 / 12)

    if max_budget is not None and unit.rent is not None:
        if unit.rent <= max_budget:
            score += 0.2
            reasons.append(f"Within budget: ${unit.rent} ≤ ${max_budget}")
        # Don't add negative reasons (over budget)

    # Availability bonus: +0.1 if available
    # Don't add availability reasons to the display (user requested to remove these)
    if unit.availability and unit.availability.lower() == "available":
        score += 0.1
        # reasons.append("Unit is available")  # Removed per user request

    # Cap at 1.0
    score = min(1.0, score)

    return score, reasons


def calculate_score_master_unit(applicant: "Applicant", master_unit: "MasterUnit") -> tuple[float, list[str]]:
    """Compute a compatibility score between an applicant and a master unit.

    Similar algorithm to calculate_score but handles MasterUnit's different structure:
    - Rent can be a string like "30% gross monthly income" or a number
    - Availability is determined by units_available > 0
    - Uses complex_apartment as property name

    Args:
        applicant: An Applicant ORM instance.
        master_unit: A MasterUnit ORM instance.

    Returns:
        A tuple of (float score, list[str] reasons) where score is between
        0 and 1, and reasons explains the scoring factors.
    """
    reasons = []

    # Parse accessibility features/needs into sets
    needs_set = set()
    features_set = set()

    if applicant.accessibility_needs:
        needs_set = {
            n.strip().lower()
            for n in applicant.accessibility_needs.split(",")
            if n.strip()
        }

    if master_unit.accessibility_features:
        features_set = {
            f.strip().lower()
            for f in master_unit.accessibility_features.split(",")
            if f.strip()
        }

    # Calculate base score based on accessibility match
    if needs_set:
        intersection = needs_set & features_set
        base_score = len(intersection) / len(needs_set)
        if intersection:
            # Only add positive reasons
            reasons.append(
                f"Accessibility match: {len(intersection)}/{len(needs_set)} needs met"
            )
        # Don't add negative reasons (accessibility mismatch)
    else:
        base_score = 0.5
        # Don't add "No accessibility requirements specified" - not useful

    score = base_score

    # Budget check: +0.2 if rent is affordable
    # Master units may have rent as "30% gross monthly income" which is always affordable
    max_budget = None
    if applicant.income is not None:
        max_budget = int(applicant.income * 0.3 / 12)

    rent_str = master_unit.rent or ""
    rent_str_lower = rent_str.lower()
    
    # Check if rent is percentage-based (always affordable)
    if "%" in rent_str_lower or "percentage" in rent_str_lower or "gross monthly income" in rent_str_lower:
        score += 0.2
        reasons.append(f"Rent is income-based: {rent_str}")
    elif max_budget is not None:
        # Try to parse numeric rent
        try:
            # Extract number from rent string (e.g., "$1200" -> 1200)
            import re
            rent_match = re.search(r'\d+', rent_str.replace(',', ''))
            if rent_match:
                rent_value = int(rent_match.group())
                if rent_value <= max_budget:
                    score += 0.2
                    reasons.append(f"Within budget: ${rent_value} ≤ ${max_budget}")
                # Don't add negative reasons (over budget)
        except (ValueError, AttributeError):
            # Don't add "Rent format" reasons - not useful
            pass

    # Availability check for master units
    # Don't add availability reasons to the display (user requested to remove these)
    if master_unit.is_available:
        if master_unit.is_available.upper() == "Y":
            score += 0.1
            # reasons.append("Unit is available")  # Removed per user request
    elif master_unit.units_available is not None:
        # Fallback to legacy units_available field
        if master_unit.units_available > 0:
            score += 0.1
            # reasons.append(f"{master_unit.units_available} unit(s) available")  # Removed per user request

    # Cap at 1.0
    score = min(1.0, score)

    return score, reasons


def send_to_apps_script(data: Dict[str, Any], sheet: str) -> None:
    """Post structured data to the Google Apps Script endpoint.

    This function sends data to a Google Apps Script that writes
    submissions into a Google Sheet. The payload must include a
    `sheet` property to direct the script to the correct worksheet.

    Ensures all required columns are present (with empty string "" if missing)
    to maintain consistent column order in the sheet.

    Args:
        data: The record to send. It should be a plain dict of
            key/value pairs that correspond to columns in the sheet.
        sheet: The name of the sheet tab within the spreadsheet ("units" or "applicants").

    Raises:
        RuntimeError: If the request fails or the Apps Script returns
            an error status.
    """
    if not APPS_SCRIPT_URL:
        # Skip sending if the environment is not configured. This
        # facilitates local development and testing without network
        # calls. In production you should always set APPS_SCRIPT_URL.
        return

    # Define required columns for each sheet to ensure consistency
    # Note: Sheet names should match Apps Script expectations ("Units" or "Applicants")
    if sheet.lower() == "units" or sheet == "Units":
        required_columns = [
            "id",
            "property_name",
            "address",
            "rent",
            "accessibility_features",
            "contact",
            "photo_url",
            "availability",
        ]
        # Normalize sheet name to "Units" for Apps Script
        sheet = "Units"
    elif sheet.lower() == "applicants" or sheet == "Applicants":
        required_columns = [
            "id",
            "name",
            "income",
            "voucher_type",
            "accessibility_needs",
            "location",
            "household_size",
            "contact",
        ]
        # Normalize sheet name to "Applicants" for Apps Script (required for per-applicant sheets)
        sheet = "Applicants"
    else:
        required_columns = list(data.keys())

    # Ensure all required columns are present, using "" for missing values
    # Convert None to "" for numeric fields that failed parsing
    normalized_data = {}
    for col in required_columns:
        value = data.get(col)
        if value is None:
            normalized_data[col] = ""
        elif isinstance(value, (int, float)):
            # Keep numeric values as-is (they'll be converted to string by JSON serialization)
            normalized_data[col] = value
        else:
            # Convert other types (including strings) to string
            normalized_data[col] = str(value)

    payload = {"sheet": sheet, **normalized_data}
    try:
        print(f"📤 Sending data to Google Sheets (sheet: {sheet}, id: {normalized_data.get('id', 'unknown')})")
        print(f"   URL: {APPS_SCRIPT_URL}")
        
        # Google Apps Script web apps sometimes need allow_redirects=True
        resp = requests.post(APPS_SCRIPT_URL, json=payload, timeout=30, allow_redirects=True)
        resp.raise_for_status()
        
        # Try to parse JSON response
        try:
            result = resp.json()
            if result.get("status") != "success":
                raise RuntimeError(f"Apps Script error: {result}")
            print(f"✅ Google Sheets update successful for {sheet} (id: {normalized_data.get('id', 'unknown')})")
        except ValueError:
            # If response is not JSON, check if it's HTML (redirect page)
            # Google Apps Script web apps often return HTML redirects, but still process the data
            if "html" in resp.text.lower() or resp.text.strip().startswith("<") or "Moved Temporarily" in resp.text:
                # This is normal - Apps Script web apps redirect, but data is still processed
                print(f"✅ Google Sheets update sent (Apps Script redirect response is normal)")
                # Don't raise error - Apps Script processes the data even with redirect
            else:
                print(f"⚠️ Apps Script response is not JSON: {resp.text[:200]}")
                # Don't raise error - Apps Script might still process it
        
    except requests.exceptions.RequestException as exc:
        # Log the error rather than halting execution. In a real
        # application you might want to send this exception to an
        # observability service.
        print(f"❌ Failed to send data to Apps Script (network error): {exc}")
        print(f"   URL: {APPS_SCRIPT_URL}")
        print(f"   Payload keys: {list(payload.keys())}")
        raise  # Re-raise so caller knows it failed
    except Exception as exc:
        print(f"❌ Failed to send data to Apps Script: {exc}")
        if hasattr(exc, 'response'):
            print(f"   Response status: {exc.response.status_code if hasattr(exc.response, 'status_code') else 'N/A'}")
        raise  # Re-raise so caller knows it failed


def _parse_boolean_answer(answers: Dict[str, Any], key: str) -> bool:
    """Helper to parse a yes/no answer into a boolean.

    Jotform may return booleans as strings like "Yes" or "No". This
    helper normalises various truthy values to a Python boolean.
    """
    val = answers.get(key)
    if val is None:
        return False
    if isinstance(val, dict):
        # Some answers are nested with a "answer" field.
        val = val.get("answer")
    if isinstance(val, str):
        return val.strip().lower() in {"yes", "true", "1", "on"}
    return bool(val)


def _parse_int_answer(answers: Dict[str, Any], key: str) -> int | None:
    val = answers.get(key)
    if val is None:
        return None
    if isinstance(val, dict):
        val = val.get("answer")
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _parse_float_answer(answers: Dict[str, Any], key: str) -> float | None:
    val = answers.get(key)
    if val is None:
        return None
    if isinstance(val, dict):
        val = val.get("answer")
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _parse_text_answer(answers: Dict[str, Any], key: str) -> str | None:
    val = answers.get(key)
    if val is None:
        return None
    if isinstance(val, dict):
        val = val.get("answer")
    if isinstance(val, str):
        return val
    return str(val)


def _parse_accessibility_features(answers: Dict[str, Any]) -> str:
    """Parse accessibility features from Jotform answers and normalize to comma-separated lowercase.

    Handles various input formats:
    - Checkboxes (list or comma-separated string)
    - Single selection
    - Multiple fields (wheelchair_access, elevator_access, ramp_access, etc.)

    Returns a comma-separated lowercase string with no spaces, e.g., "wheelchair,elevator,ramp"
    """
    features = []

    # Try to find accessibility features in various formats
    # Check for a direct "accessibility_features" field
    val = answers.get("accessibility_features")
    if val is None:
        # Try common alternative field names
        val = (
            answers.get("accessibility")
            or answers.get("features")
            or answers.get("amenities")
        )

    if val:
        if isinstance(val, dict):
            val = val.get("answer")

        if isinstance(val, list):
            # Handle checkbox-style lists
            features = [str(item).strip().lower() for item in val if item]
        elif isinstance(val, str):
            # Handle comma-separated strings or single values
            parts = [p.strip() for p in val.split(",")]
            features = [p.lower() for p in parts if p]

    # Also check individual boolean flags (backwards compatibility)
    accessibility_map = {
        "wheelchair_access": "wheelchair",
        "elevator_access": "elevator",
        "ramp_access": "ramp",
    }
    for key, feature_name in accessibility_map.items():
        if _parse_boolean_answer(answers, key):
            if feature_name not in features:
                features.append(feature_name)

    # Normalize: lowercase, no spaces, comma-separated
    normalized = ",".join(sorted(set(features)))  # Sort for consistency
    return normalized


def _parse_accessibility_needs(answers: Dict[str, Any]) -> str:
    """Parse accessibility needs from Jotform answers and normalize to comma-separated lowercase.

    Handles various input formats similar to accessibility_features.

    Returns a comma-separated lowercase string with no spaces, e.g., "wheelchair,elevator"
    """
    needs = []

    # Try to find accessibility needs in various formats
    val = answers.get("accessibility_needs")
    if val is None:
        # Try common alternative field names
        val = (
            answers.get("accessibility")
            or answers.get("needs")
            or answers.get("requirements")
        )

    if val:
        if isinstance(val, dict):
            val = val.get("answer")

        if isinstance(val, list):
            # Handle checkbox-style lists
            needs = [str(item).strip().lower() for item in val if item]
        elif isinstance(val, str):
            # Handle comma-separated strings or single values
            parts = [p.strip() for p in val.split(",")]
            needs = [p.lower() for p in parts if p]

    # Also check individual boolean flags (backwards compatibility)
    needs_map = {
        "needs_wheelchair": "wheelchair",
        "needs_elevator": "elevator",
        "needs_ramp": "ramp",
    }
    for key, need_name in needs_map.items():
        if _parse_boolean_answer(answers, key):
            if need_name not in needs:
                needs.append(need_name)

    # Normalize: lowercase, no spaces, comma-separated
    normalized = ",".join(sorted(set(needs)))  # Sort for consistency
    return normalized
