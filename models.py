"""
Advanced Database Models for Skip Tracing Genealogy Platform
Includes scoring, confidence levels, data sources, and relationship tracking
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Float, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship

db = SQLAlchemy()


# Association table for many-to-many relationship between people
person_relationships = Table(
    'person_relationships',
    db.Model.metadata,
    db.Column('person_id', Integer, ForeignKey('people.id'), primary_key=True),
    db.Column('related_person_id', Integer, ForeignKey('people.id'), primary_key=True),
    db.Column('relationship_type', String(50)),
    db.Column('confidence_score', Float, default=0.0),
    db.Column('verified', Boolean, default=False),
    db.Column('created_at', DateTime, default=datetime.utcnow)
)


class Property(db.Model):
    """Enhanced property model with tracking and analysis"""
    __tablename__ = 'properties'

    id = db.Column(Integer, primary_key=True)

    # Basic Information
    address = db.Column(String(500), nullable=False, index=True)
    city = db.Column(String(100))
    state = db.Column(String(50))
    zip_code = db.Column(String(20))
    county = db.Column(String(100))
    apn = db.Column(String(100))  # Assessor's Parcel Number

    # Owner Information
    owner_name = db.Column(String(200))
    owner_type = db.Column(String(50))  # 'individual', 'corporate', 'trust', etc.

    # Financial Information
    property_value = db.Column(Float)
    assessed_value = db.Column(Float)
    overage_amount = db.Column(Float)
    tax_amount = db.Column(Float)

    # Case Information
    case_number = db.Column(String(100), index=True)
    case_type = db.Column(String(50))  # 'foreclosure', 'tax_lien', 'probate', etc.
    sale_date = db.Column(DateTime)
    filing_date = db.Column(DateTime)

    # Status & Processing
    status = db.Column(String(50), default='active')  # 'active', 'researched', 'completed', 'archived'
    research_status = db.Column(String(50), default='pending')  # 'pending', 'in_progress', 'completed', 'failed'
    priority = db.Column(Integer, default=0)  # 0-100 priority score

    # AI Analysis
    heir_count = db.Column(Integer, default=0)
    heir_confidence_avg = db.Column(Float, default=0.0)
    research_completeness = db.Column(Float, default=0.0)  # 0-100%
    case_complexity = db.Column(String(20))  # 'simple', 'moderate', 'complex'
    success_probability = db.Column(Float, default=0.0)  # 0-100%

    # Data Sources
    data_sources = db.Column(JSON)  # List of sources that provided data
    last_updated_source = db.Column(String(100))

    # Metadata
    notes = db.Column(Text)
    tags = db.Column(JSON)  # Array of tags for categorization
    created_at = db.Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    heirs = relationship('Heir', back_populates='property', cascade='all, delete-orphan')
    ownership_chain = relationship('OwnershipHistory', back_populates='property', cascade='all, delete-orphan')
    documents = relationship('Document', back_populates='property')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'county': self.county,
            'owner_name': self.owner_name,
            'property_value': self.property_value,
            'overage_amount': self.overage_amount,
            'case_number': self.case_number,
            'status': self.status,
            'heir_count': self.heir_count,
            'success_probability': self.success_probability,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Person(db.Model):
    """Person entity with comprehensive genealogy tracking"""
    __tablename__ = 'people'

    id = db.Column(Integer, primary_key=True)

    # Name Information
    first_name = db.Column(String(100), index=True)
    middle_name = db.Column(String(100))
    last_name = db.Column(String(100), index=True)
    maiden_name = db.Column(String(100))
    suffix = db.Column(String(20))
    nickname = db.Column(String(100))
    aliases = db.Column(JSON)  # Array of known aliases

    # Demographics
    date_of_birth = db.Column(DateTime)
    date_of_death = db.Column(DateTime)
    age = db.Column(Integer)
    age_range = db.Column(String(20))
    gender = db.Column(String(20))
    ssn = db.Column(String(20))  # Encrypted

    # Contact Information
    current_address = db.Column(String(500))
    previous_addresses = db.Column(JSON)  # Array of address objects
    phone_numbers = db.Column(JSON)  # Array of phone objects
    email_addresses = db.Column(JSON)  # Array of email addresses

    # Location
    city = db.Column(String(100))
    state = db.Column(String(50))
    zip_code = db.Column(String(20))
    country = db.Column(String(100), default='USA')

    # Vital Records
    birth_city = db.Column(String(100))
    birth_state = db.Column(String(50))
    death_city = db.Column(String(100))
    death_state = db.Column(String(50))
    burial_location = db.Column(String(500))
    cemetery_name = db.Column(String(200))

    # AI Scoring
    confidence_score = db.Column(Float, default=0.0)  # 0-100 confidence this is the right person
    data_quality_score = db.Column(Float, default=0.0)  # 0-100 quality of available data
    verification_status = db.Column(String(50), default='unverified')  # 'unverified', 'partial', 'verified'

    # Data Sources
    data_sources = db.Column(JSON)  # Sources that provided information
    last_verified_date = db.Column(DateTime)
    last_scraped_date = db.Column(DateTime)

    # Metadata
    notes = db.Column(Text)
    tags = db.Column(JSON)
    created_at = db.Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    related_persons = relationship(
        'Person',
        secondary=person_relationships,
        primaryjoin=id == person_relationships.c.person_id,
        secondaryjoin=id == person_relationships.c.related_person_id,
        backref='related_to'
    )

    def full_name(self):
        """Get full name"""
        parts = [self.first_name, self.middle_name, self.last_name, self.suffix]
        return ' '.join(filter(None, parts))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'full_name': self.full_name(),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'date_of_death': self.date_of_death.isoformat() if self.date_of_death else None,
            'current_address': self.current_address,
            'phone_numbers': self.phone_numbers,
            'email_addresses': self.email_addresses,
            'confidence_score': self.confidence_score
        }


class Heir(db.Model):
    """Heir with advanced probability scoring"""
    __tablename__ = 'heirs'

    id = db.Column(Integer, primary_key=True)
    property_id = db.Column(Integer, ForeignKey('properties.id'), nullable=False, index=True)
    person_id = db.Column(Integer, ForeignKey('people.id'), index=True)

    # Basic Information
    name = db.Column(String(200), nullable=False)
    relationship = db.Column(String(100))  # 'son', 'daughter', 'spouse', etc.
    relationship_degree = db.Column(Integer)  # 1=child, 2=grandchild, etc.

    # Contact Information
    contact_info = db.Column(Text)
    address = db.Column(String(500))
    phone = db.Column(String(50))
    email = db.Column(String(200))

    # Legal Status
    legal_heir = db.Column(Boolean, default=True)
    intestate_share = db.Column(Float)  # Percentage of estate (0-100)

    # AI Scoring & Verification
    confidence_score = db.Column(Float, default=0.0)  # 0-100 confidence
    verification_status = db.Column(String(50), default='unverified')
    verified_by = db.Column(String(100))
    verified_date = db.Column(DateTime)

    # Scoring Factors (for transparency)
    name_match_score = db.Column(Float, default=0.0)
    relationship_verified = db.Column(Boolean, default=False)
    documentation_exists = db.Column(Boolean, default=False)
    contact_verified = db.Column(Boolean, default=False)

    # Contact Attempts
    contact_attempts = db.Column(Integer, default=0)
    last_contact_date = db.Column(DateTime)
    contact_status = db.Column(String(50))  # 'not_contacted', 'contacted', 'responded', 'interested', 'declined'

    # Data Sources
    data_sources = db.Column(JSON)
    discovered_by = db.Column(String(100))  # 'ai_research', 'manual', 'pdf_upload', etc.

    # Metadata
    notes = db.Column(Text)
    tags = db.Column(JSON)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    property = relationship('Property', back_populates='heirs')
    person = relationship('Person')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'relationship': self.relationship,
            'confidence_score': self.confidence_score,
            'verification_status': self.verification_status,
            'contact_info': self.contact_info,
            'phone': self.phone,
            'email': self.email,
            'intestate_share': self.intestate_share
        }


class OwnershipHistory(db.Model):
    """Track property ownership chain"""
    __tablename__ = 'ownership_history'

    id = db.Column(Integer, primary_key=True)
    property_id = db.Column(Integer, ForeignKey('properties.id'), nullable=False, index=True)
    person_id = db.Column(Integer, ForeignKey('people.id'))

    # Ownership Details
    owner_name = db.Column(String(200), nullable=False)
    owner_type = db.Column(String(50))
    ownership_type = db.Column(String(50))  # 'sole', 'joint', 'trust', 'corporate'
    ownership_percentage = db.Column(Float, default=100.0)

    # Dates
    acquisition_date = db.Column(DateTime)
    transfer_date = db.Column(DateTime)

    # Transaction Details
    deed_type = db.Column(String(100))
    deed_book = db.Column(String(50))
    deed_page = db.Column(String(50))
    sale_price = db.Column(Float)

    # Status
    current_owner = db.Column(Boolean, default=False)

    # Data Source
    data_source = db.Column(String(100))

    # Metadata
    notes = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    property = relationship('Property', back_populates='ownership_chain')
    person = relationship('Person')


class Document(db.Model):
    """Enhanced document model with AI analysis"""
    __tablename__ = 'documents'

    id = db.Column(Integer, primary_key=True)
    property_id = db.Column(Integer, ForeignKey('properties.id'), index=True)

    # File Information
    filename = db.Column(String(255), nullable=False)
    original_name = db.Column(String(255))
    file_path = db.Column(String(500))
    file_type = db.Column(String(50))  # 'pdf', 'image', 'csv', 'doc'
    file_size = db.Column(Integer)
    mime_type = db.Column(String(100))

    # Document Classification
    document_type = db.Column(String(100))  # 'deed', 'affidavit', 'death_certificate', 'tracers_report', etc.
    source_type = db.Column(String(100))  # 'tracers', 'county_clerk', 'manual_upload', etc.

    # OCR & Extraction
    extracted_text = db.Column(Text)
    ocr_confidence = db.Column(Float, default=0.0)
    text_length = db.Column(Integer)

    # AI Analysis
    analyzed_data = db.Column(JSON)  # Structured data extracted by AI
    entities_extracted = db.Column(JSON)  # Names, addresses, dates, etc.
    ai_summary = db.Column(Text)
    ai_confidence = db.Column(Float, default=0.0)

    # Processing Status
    processing_status = db.Column(String(50), default='pending')  # 'pending', 'processing', 'completed', 'failed'
    ocr_completed = db.Column(Boolean, default=False)
    ai_analyzed = db.Column(Boolean, default=False)

    # Metadata
    notes = db.Column(Text)
    tags = db.Column(JSON)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    property = relationship('Property', back_populates='documents')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'document_type': self.document_type,
            'file_type': self.file_type,
            'ocr_confidence': self.ocr_confidence,
            'ai_confidence': self.ai_confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ResearchResult(db.Model):
    """Track research activities and results"""
    __tablename__ = 'research_results'

    id = db.Column(Integer, primary_key=True)

    # Query Information
    query = db.Column(String(500), nullable=False, index=True)
    query_type = db.Column(String(50))  # 'person', 'property', 'address', 'phone'

    # Result
    result_type = db.Column(String(50))  # 'genealogy', 'property', 'skip_trace'
    data = db.Column(JSON)  # Full result data

    # Sources Used
    sources_queried = db.Column(JSON)  # List of sources queried
    sources_returned_data = db.Column(JSON)  # Sources that returned data

    # Quality Metrics
    data_quality_score = db.Column(Float, default=0.0)
    confidence_score = db.Column(Float, default=0.0)
    completeness_score = db.Column(Float, default=0.0)

    # Processing
    processing_time = db.Column(Float)  # Seconds
    success = db.Column(Boolean, default=True)
    error_message = db.Column(Text)

    # Metadata
    created_at = db.Column(DateTime, default=datetime.utcnow, index=True)
    created_by = db.Column(String(100))  # User or system


class Case(db.Model):
    """Case management for tracking full skip tracing projects"""
    __tablename__ = 'cases'

    id = db.Column(Integer, primary_key=True)

    # Case Information
    case_number = db.Column(String(100), unique=True, nullable=False, index=True)
    case_name = db.Column(String(200))
    case_type = db.Column(String(50))  # 'skip_trace', 'heir_search', 'property_research'

    # Client Information
    client_name = db.Column(String(200))
    client_contact = db.Column(String(200))

    # Status
    status = db.Column(String(50), default='open')  # 'open', 'in_progress', 'completed', 'closed'
    priority = db.Column(String(20), default='normal')  # 'low', 'normal', 'high', 'urgent'

    # Dates
    opened_date = db.Column(DateTime, default=datetime.utcnow)
    due_date = db.Column(DateTime)
    closed_date = db.Column(DateTime)

    # Progress Tracking
    progress_percentage = db.Column(Integer, default=0)
    properties_count = db.Column(Integer, default=0)
    heirs_found_count = db.Column(Integer, default=0)

    # Financial
    estimated_value = db.Column(Float)
    fee_amount = db.Column(Float)

    # Metadata
    notes = db.Column(Text)
    tags = db.Column(JSON)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(db.Model):
    """Audit trail for compliance and tracking"""
    __tablename__ = 'audit_logs'

    id = db.Column(Integer, primary_key=True)

    # Event Information
    event_type = db.Column(String(100), nullable=False, index=True)  # 'search', 'data_access', 'update', etc.
    entity_type = db.Column(String(50))  # 'property', 'person', 'heir', etc.
    entity_id = db.Column(Integer)

    # Action Details
    action = db.Column(String(100))  # 'create', 'read', 'update', 'delete'
    description = db.Column(Text)
    old_values = db.Column(JSON)
    new_values = db.Column(JSON)

    # User/System
    user_id = db.Column(String(100))
    ip_address = db.Column(String(50))
    user_agent = db.Column(String(500))

    # Result
    success = db.Column(Boolean, default=True)
    error_message = db.Column(Text)

    # Metadata
    created_at = db.Column(DateTime, default=datetime.utcnow, index=True)
