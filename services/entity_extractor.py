"""
AI-Powered Entity Extraction
Extracts people, addresses, phones, dates, relationships from text
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    Extract structured entities from unstructured text
    Uses regex patterns and optional NLP models
    """

    def __init__(self, use_spacy=False):
        """
        Initialize entity extractor

        Args:
            use_spacy: Whether to use spaCy NLP (requires model download)
        """
        self.use_spacy = use_spacy
        self.nlp = None

        if use_spacy:
            try:
                import spacy
                try:
                    self.nlp = spacy.load('en_core_web_sm')
                except OSError:
                    logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
                    self.use_spacy = False
            except ImportError:
                logger.warning("spaCy not installed")
                self.use_spacy = False

    def extract_all(self, text: str) -> Dict[str, List]:
        """
        Extract all entities from text

        Args:
            text: Input text

        Returns:
            dict: Dictionary of extracted entities
        """
        return {
            'people': self.extract_people(text),
            'addresses': self.extract_addresses(text),
            'phone_numbers': self.extract_phone_numbers(text),
            'email_addresses': self.extract_emails(text),
            'dates': self.extract_dates(text),
            'relationships': self.extract_relationships(text),
            'financial_amounts': self.extract_financial_amounts(text),
            'case_numbers': self.extract_case_numbers(text),
            'ssn': self.extract_ssn(text)
        }

    def extract_people(self, text: str) -> List[Dict[str, str]]:
        """Extract person names from text"""
        if self.use_spacy and self.nlp:
            return self._extract_people_spacy(text)
        else:
            return self._extract_people_regex(text)

    def _extract_people_spacy(self, text: str) -> List[Dict[str, str]]:
        """Extract names using spaCy NLP"""
        doc = self.nlp(text)
        people = []

        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                people.append({
                    'name': ent.text,
                    'confidence': 0.85,
                    'method': 'spacy'
                })

        return people

    def _extract_people_regex(self, text: str) -> List[Dict[str, str]]:
        """Extract names using regex patterns"""
        from nameparser import HumanName

        people = []

        # Pattern for full names (First Middle Last or First Last)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z][a-z]+)\b'
        matches = re.finditer(name_pattern, text)

        seen = set()
        for match in matches:
            full_name = match.group(0)

            # Skip if too short or already seen
            if len(full_name) < 5 or full_name in seen:
                continue

            # Parse name components
            try:
                parsed = HumanName(full_name)
                if parsed.first and parsed.last:
                    people.append({
                        'name': full_name,
                        'first_name': parsed.first,
                        'middle_name': parsed.middle,
                        'last_name': parsed.last,
                        'suffix': parsed.suffix,
                        'confidence': 0.70,
                        'method': 'regex'
                    })
                    seen.add(full_name)
            except:
                pass

        return people

    def extract_addresses(self, text: str) -> List[Dict[str, str]]:
        """Extract US addresses from text"""
        import usaddress

        addresses = []

        # Pattern for street addresses
        address_pattern = r'\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Court|Ct|Circle|Cir|Place|Pl)(?:\s*,\s*(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?)?'

        matches = re.finditer(address_pattern, text, re.IGNORECASE)

        for match in matches:
            addr_text = match.group(0)

            try:
                # Parse address components
                parsed, addr_type = usaddress.tag(addr_text)

                addresses.append({
                    'full_address': addr_text,
                    'parsed': parsed,
                    'type': addr_type,
                    'confidence': 0.80
                })
            except:
                # Fallback to unparsed
                addresses.append({
                    'full_address': addr_text,
                    'confidence': 0.60
                })

        return addresses

    def extract_phone_numbers(self, text: str) -> List[Dict[str, str]]:
        """Extract phone numbers"""
        import phonenumbers

        phones = []

        # Pattern for US phone numbers
        patterns = [
            r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b',  # 123-456-7890
            r'\b\((\d{3})\)\s*(\d{3})[-.\s]?(\d{4})\b',  # (123) 456-7890
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                phone_text = match.group(0)

                try:
                    # Parse and format
                    parsed = phonenumbers.parse(phone_text, 'US')
                    if phonenumbers.is_valid_number(parsed):
                        formatted = phonenumbers.format_number(
                            parsed,
                            phonenumbers.PhoneNumberFormat.NATIONAL
                        )
                        phones.append({
                            'raw': phone_text,
                            'formatted': formatted,
                            'international': phonenumbers.format_number(
                                parsed,
                                phonenumbers.PhoneNumberFormat.INTERNATIONAL
                            ),
                            'valid': True,
                            'confidence': 0.95
                        })
                except:
                    phones.append({
                        'raw': phone_text,
                        'formatted': phone_text,
                        'valid': False,
                        'confidence': 0.50
                    })

        return phones

    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)
        return list(set(emails))  # Remove duplicates

    def extract_dates(self, text: str) -> List[Dict[str, str]]:
        """Extract dates from text"""
        from dateutil import parser as date_parser

        dates = []

        # Date patterns
        patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b',  # DD Month YYYY
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_text = match.group(0)

                try:
                    # Parse date
                    parsed_date = date_parser.parse(date_text, fuzzy=False)
                    dates.append({
                        'raw': date_text,
                        'parsed': parsed_date.isoformat(),
                        'year': parsed_date.year,
                        'month': parsed_date.month,
                        'day': parsed_date.day,
                        'confidence': 0.85
                    })
                except:
                    dates.append({
                        'raw': date_text,
                        'confidence': 0.50
                    })

        return dates

    def extract_relationships(self, text: str) -> List[Dict[str, str]]:
        """Extract family relationships"""
        relationships = []

        # Relationship keywords
        rel_patterns = {
            'child': [r'\b(son|daughter|child)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'],
            'parent': [r'\b(mother|father|parent)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'],
            'spouse': [r'\b(husband|wife|spouse)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'],
            'sibling': [r'\b(brother|sister|sibling)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'],
        }

        for rel_type, patterns in rel_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    relationships.append({
                        'relationship_type': rel_type,
                        'relationship_text': match.group(1),
                        'related_to': match.group(2) if len(match.groups()) > 1 else None,
                        'confidence': 0.75,
                        'raw': match.group(0)
                    })

        return relationships

    def extract_financial_amounts(self, text: str) -> List[Dict[str, any]]:
        """Extract dollar amounts"""
        amounts = []

        # Money patterns
        pattern = r'\$\s*[\d,]+(?:\.\d{2})?'
        matches = re.finditer(pattern, text)

        for match in matches:
            amount_text = match.group(0)
            # Remove $ and commas, convert to float
            try:
                value = float(amount_text.replace('$', '').replace(',', '').strip())
                amounts.append({
                    'raw': amount_text,
                    'value': value,
                    'formatted': f'${value:,.2f}'
                })
            except:
                pass

        return amounts

    def extract_case_numbers(self, text: str) -> List[str]:
        """Extract case/file numbers"""
        # Pattern for case numbers (flexible)
        pattern = r'\b(?:Case|File|Cause|Docket)\s*(?:No\.?|Number|#)?\s*:?\s*([A-Z0-9-]+)\b'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches

    def extract_ssn(self, text: str) -> List[str]:
        """Extract SSN (use with caution - PII)"""
        pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        ssns = re.findall(pattern, text)
        # Redact for logging
        logger.info(f"Found {len(ssns)} SSN patterns (redacted)")
        return ssns
