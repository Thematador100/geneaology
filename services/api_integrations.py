"""
Third-Party API Integrations
Public records, skip tracing services, phone/email verification
"""
import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class PublicRecordsAPI:
    """
    Integration with public records APIs
    """

    def __init__(self):
        from config import Config
        self.attom_api_key = Config.ATTOM_API_KEY
        self.timeout = 30

    def lookup_property(self, address: str) -> Dict:
        """
        Lookup property data from ATTOM Data API

        Args:
            address: Property address

        Returns:
            dict: Property information
        """
        if not self.attom_api_key:
            return {'error': 'ATTOM API key not configured'}

        try:
            url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/address"
            headers = {'apikey': self.attom_api_key}
            params = {'address': address}

            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            return {
                'source': 'attom',
                'data': data,
                'success': True
            }

        except Exception as e:
            logger.error(f"ATTOM API lookup failed: {e}")
            return {'error': str(e), 'success': False}


class SkipTracingAPI:
    """
    Integration with skip tracing services (Tracers, TruthFinder, etc.)
    """

    def __init__(self):
        from config import Config
        self.tracers_key = Config.TRACERS_API_KEY
        self.spokeo_key = Config.SPOKEO_API_KEY

    def search_person(self, name: str, location: str = None) -> Dict:
        """
        Search for person using skip tracing services

        Args:
            name: Person name
            location: Optional location

        Returns:
            dict: Person data
        """
        results = {
            'name': name,
            'location': location,
            'sources': {}
        }

        # Try Tracers API
        if self.tracers_key:
            try:
                tracers_data = self._query_tracers(name, location)
                results['sources']['tracers'] = tracers_data
            except Exception as e:
                logger.error(f"Tracers API failed: {e}")

        # Try Spokeo API
        if self.spokeo_key:
            try:
                spokeo_data = self._query_spokeo(name, location)
                results['sources']['spokeo'] = spokeo_data
            except Exception as e:
                logger.error(f"Spokeo API failed: {e}")

        return results

    def _query_tracers(self, name: str, location: str = None) -> Dict:
        """Query Tracers API (placeholder - actual implementation depends on API docs)"""
        return {'placeholder': 'Tracers API integration - requires API documentation'}

    def _query_spokeo(self, name: str, location: str = None) -> Dict:
        """Query Spokeo API (placeholder)"""
        return {'placeholder': 'Spokeo API integration - requires API documentation'}


class PhoneEmailVerification:
    """
    Phone and email verification services
    """

    def __init__(self):
        from config import Config
        self.whitepages_key = Config.WHITEPAGES_API_KEY
        self.twilio_sid = Config.TWILIO_ACCOUNT_SID
        self.twilio_token = Config.TWILIO_AUTH_TOKEN

    def verify_phone(self, phone_number: str) -> Dict:
        """
        Verify and lookup phone number

        Args:
            phone_number: Phone number to verify

        Returns:
            dict: Verification results
        """
        import phonenumbers

        try:
            # Parse and validate
            parsed = phonenumbers.parse(phone_number, 'US')
            is_valid = phonenumbers.is_valid_number(parsed)

            result = {
                'phone_number': phone_number,
                'formatted': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
                'international': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
                'valid': is_valid,
                'carrier': None,
                'type': None
            }

            # Get carrier info if Twilio configured
            if self.twilio_sid and self.twilio_token and is_valid:
                try:
                    from twilio.rest import Client
                    client = Client(self.twilio_sid, self.twilio_token)

                    lookup = client.lookups.v1.phone_numbers(parsed.country_code + str(parsed.national_number)).fetch(type=['carrier'])

                    result['carrier'] = lookup.carrier.get('name')
                    result['type'] = lookup.carrier.get('type')

                except Exception as e:
                    logger.error(f"Twilio lookup failed: {e}")

            return result

        except Exception as e:
            logger.error(f"Phone verification failed: {e}")
            return {
                'phone_number': phone_number,
                'valid': False,
                'error': str(e)
            }

    def lookup_email(self, email: str) -> Dict:
        """
        Lookup and verify email address

        Args:
            email: Email address

        Returns:
            dict: Email information
        """
        import re

        # Basic validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid_format = bool(re.match(email_pattern, email))

        result = {
            'email': email,
            'valid_format': is_valid_format,
            'disposable': False,
            'deliverable': None
        }

        # Check disposable email domains
        disposable_domains = ['tempmail.com', 'guerrillamail.com', 'mailinator.com', '10minutemail.com']
        domain = email.split('@')[-1].lower()
        result['disposable'] = domain in disposable_domains

        return result


class SocialMediaOSINT:
    """
    Social media intelligence gathering (OSINT)
    NOTE: Use responsibly and in compliance with platform ToS
    """

    def __init__(self):
        from config import Config
        self.pipl_key = Config.PIPL_API_KEY

    def search_person(self, name: str, email: str = None, phone: str = None) -> Dict:
        """
        Search for person across social media and web

        Args:
            name: Person name
            email: Optional email
            phone: Optional phone

        Returns:
            dict: Social media profiles and information
        """
        results = {
            'name': name,
            'profiles': [],
            'photos': [],
            'addresses': [],
            'jobs': []
        }

        # Pipl API (comprehensive people search)
        if self.pipl_key:
            try:
                pipl_data = self._query_pipl(name, email, phone)
                results.update(pipl_data)
            except Exception as e:
                logger.error(f"Pipl API failed: {e}")

        return results

    def _query_pipl(self, name: str, email: str = None, phone: str = None) -> Dict:
        """Query Pipl API (placeholder)"""
        return {'placeholder': 'Pipl API integration - requires API key and implementation'}
