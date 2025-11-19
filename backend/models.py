"""Data models for HousingMatcher.

Defines SQLAlchemy ORM models for `Unit` and `Applicant`. Each model
stores its raw submission data in a JSON-encoded string along with
standardised accessibility flags extracted from the forms. This allows
the matching engine to operate on both structured and unstructured
submission data.
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, Text
from sqlalchemy.types import JSON
from sqlalchemy.orm import declarative_base

from database import Base


class Unit(Base):
    """Represents a housing unit submitted by a landlord via Jotform."""

    __tablename__ = "units"

    # Use the Jotform submission ID as the primary key. It is a string
    # rather than an integer because Jotform submission IDs can be large.
    id = Column(String, primary_key=True, index=True)

    # Raw submission data stored as JSON. This allows us to retain
    # answers that are not explicitly mapped to structured columns.
    data = Column(JSON, nullable=False)

    # Fields matching Google Sheet schema: AccessibleHousingDatabase.units
    property_name = Column(String, nullable=True)
    address = Column(String, nullable=True)
    rent = Column(Integer, nullable=True)  # rent is int in schema
    accessibility_features = Column(String, nullable=True)  # comma-separated lowercase
    contact = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    availability = Column(
        String, nullable=True
    )  # "available" | "waitlist" | "occupied"

    def __repr__(self) -> str:
        return f"<Unit id={self.id} address={self.address}>"


class Applicant(Base):
    """Represents a housing applicant's submission via Jotform."""

    __tablename__ = "applicants"

    id = Column(String, primary_key=True, index=True)
    data = Column(JSON, nullable=False)

    # Fields matching Google Sheet schema: AccessibleHousingDatabase.applicants
    name = Column(String, nullable=True)
    income = Column(Integer, nullable=True)  # income is int in schema
    voucher_type = Column(String, nullable=True)  # e.g., "Section 8" or ""
    accessibility_needs = Column(String, nullable=True)  # comma-separated lowercase
    location = Column(String, nullable=True)  # city/ZIP
    household_size = Column(Integer, nullable=True)
    contact = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<Applicant id={self.id} name={self.name}>"


class MasterUnit(Base):
    """Represents a housing unit from the master CYC - Accessible Housing sheet.
    
    This model handles the new master database structure with contact information.
    Schema matches: Unit Number, Complex/Apartment, Landlord Name, Landlord Contact,
    Response Status, Is Available?, Address, City, Zip Code, Rent, Income Range,
    Age Range, Accessibility Features, Transportation, Stores, Building Features,
    Apartment Features, Notes
    """

    __tablename__ = "master_units"

    # Use a composite key or generate ID from row number
    id = Column(String, primary_key=True, index=True)
    
    # Raw data stored as JSON for flexibility
    data = Column(JSON, nullable=True)

    # Core identification fields
    unit_number = Column(String, nullable=True)  # Unit Number
    complex_apartment = Column(String, nullable=True)  # Complex/Apartment
    
    # Contact information
    landlord_name = Column(String, nullable=True)  # Landlord Name
    landlord_contact_raw = Column(String, nullable=True)  # Landlord Contact (original string)
    landlord_phone = Column(String, nullable=True)  # Parsed phone number
    landlord_email = Column(String, nullable=True)  # Parsed email address
    
    # Status fields
    response_status = Column(String, nullable=True)  # Response Status
    is_available = Column(String, nullable=True)  # Is Available? (Y/N)
    
    # Location fields
    address = Column(String, nullable=True)  # Address
    city = Column(String, nullable=True)  # City
    zip_code = Column(String, nullable=True)  # Zip Code
    
    # Financial and eligibility
    rent = Column(String, nullable=True)  # Rent (can be "30% gross monthly income" or number)
    income_range = Column(String, nullable=True)  # Income Range
    age_range = Column(String, nullable=True)  # Age Range
    
    # Features and amenities
    accessibility_features = Column(String, nullable=True)  # Accessibility Features (comma-separated)
    transportation = Column(String, nullable=True)  # Transportation
    stores = Column(String, nullable=True)  # Stores
    building_features = Column(String, nullable=True)  # Building Features
    apartment_features = Column(String, nullable=True)  # Apartment Features
    
    # Additional info
    notes = Column(Text, nullable=True)  # Notes
    
    # Legacy fields (for backwards compatibility)
    accessible_units = Column(Integer, nullable=True)  # Deprecated, kept for compatibility
    units_available = Column(Integer, nullable=True)  # Deprecated, kept for compatibility

    def __repr__(self) -> str:
        return f"<MasterUnit id={self.id} complex={self.complex_apartment} unit={self.unit_number}>"
