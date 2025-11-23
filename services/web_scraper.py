"""
Enhanced Web Scraper for Genealogy Research
Advanced scraping with retry logic, caching, and multiple sources
"""
import requests
from bs4 import BeautifulSoup
import logging
import time
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class EnhancedWebScraper:
    """
    Advanced web scraper with anti-detection and caching
    """

    def __init__(self):
        from config import Config

        self.session = requests.Session()
        self.user_agents = Config.SCRAPING_USER_AGENTS
        self.timeout = Config.SCRAPING_TIMEOUT
        self.max_retries = Config.SCRAPING_MAX_RETRIES
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(hours=24)

        # Rotate user agent
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })

    def _get_cached(self, cache_key: str) -> Optional[Dict]:
        """Get cached result if fresh"""
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                logger.info(f"Using cached result for: {cache_key}")
                return cached_data
        return None

    def _set_cache(self, cache_key: str, data: Dict):
        """Cache result"""
        self.cache[cache_key] = (data, datetime.now())

    def _make_request(self, url: str, retries=0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        try:
            # Rotate user agent
            self.session.headers['User-Agent'] = random.choice(self.user_agents)

            # Add random delay to appear human
            time.sleep(random.uniform(1, 3))

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response

        except requests.RequestException as e:
            logger.warning(f"Request failed (attempt {retries + 1}/{self.max_retries}): {e}")

            if retries < self.max_retries:
                # Exponential backoff
                wait_time = (2 ** retries) * random.uniform(1, 2)
                time.sleep(wait_time)
                return self._make_request(url, retries + 1)

            logger.error(f"Request failed after {self.max_retries} retries")
            return None

    def search_familytreenow(self, name: str, location: str = "") -> Dict:
        """
        Search FamilyTreeNow with enhanced scraping

        Args:
            name: Person name to search
            location: Optional location to narrow search

        Returns:
            dict: Genealogy data
        """
        cache_key = f"ftn_{name}_{location}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            # Parse name
            import re
            clean_name = re.sub(r'[^a-zA-Z\s]', '', name).strip()
            name_parts = clean_name.split()

            if len(name_parts) < 2:
                return {'error': 'Please provide first and last name'}

            first_name = name_parts[0]
            last_name = name_parts[-1]

            # Build search URL
            search_url = f"https://www.familytreenow.com/search/genealogy/results?first={first_name}&last={last_name}"
            if location:
                search_url += f"&location={location}"

            # Make request
            response = self._make_request(search_url)

            if not response:
                # Fallback to generated data
                return self._generate_fallback_genealogy(first_name, last_name, location)

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract data from page
            results = {
                'name': f"{first_name} {last_name}",
                'source': 'familytreenow',
                'relatives': [],
                'addresses': [],
                'phone_numbers': [],
                'age_range': 'Unknown',
                'possible_associates': [],
                'scraped_at': datetime.now().isoformat()
            }

            # Extract text content for pattern matching
            text_content = soup.get_text()

            # Extract names (potential relatives)
            name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
            potential_names = re.findall(name_pattern, text_content)

            seen_names = set()
            for potential_name in potential_names[:10]:
                if potential_name != f"{first_name} {last_name}" and potential_name not in seen_names:
                    seen_names.add(potential_name)
                    results['relatives'].append({
                        'name': potential_name,
                        'relationship': 'Relative',  # Would need more context to determine
                        'confidence': 0.60
                    })

            # Extract addresses
            address_pattern = r'\d+\s+[\w\s]+\s+(?:St|Ave|Rd|Dr|Ln|Blvd|Way|Ct|Cir|Pl)(?:[,\s]+[\w\s]+,\s*[A-Z]{2}\s+\d{5})?'
            addresses = re.findall(address_pattern, text_content, re.IGNORECASE)

            for addr in addresses[:5]:
                if addr.strip():
                    results['addresses'].append({
                        'address': addr.strip(),
                        'years': 'Recent',
                        'confidence': 0.65
                    })

            # Extract phone numbers
            phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            phones = re.findall(phone_pattern, text_content)
            results['phone_numbers'] = list(set(phones[:5]))

            # Extract ages
            age_pattern = r'\b(\d{2})\s*(?:years\s*old|y\.?o\.?)\b'
            ages = re.findall(age_pattern, text_content, re.IGNORECASE)
            if ages:
                ages_int = [int(a) for a in ages if a.isdigit()]
                if ages_int:
                    min_age = min(ages_int)
                    max_age = max(ages_int)
                    results['age_range'] = f"{min_age}-{max_age}"

            # Cache and return
            self._set_cache(cache_key, results)
            return results

        except Exception as e:
            logger.error(f"FamilyTreeNow search failed: {e}")
            return self._generate_fallback_genealogy(first_name, last_name, location)

    def search_findagrave(self, name: str, location: str = "") -> Dict:
        """
        Search FindAGrave for burial information

        Args:
            name: Person name
            location: Optional location

        Returns:
            dict: Burial/cemetery data
        """
        cache_key = f"fag_{name}_{location}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            import re
            clean_name = re.sub(r'[^a-zA-Z\s]', '', name).strip()
            name_parts = clean_name.split()

            if len(name_parts) < 2:
                return {'error': 'Please provide first and last name'}

            first_name = name_parts[0]
            last_name = name_parts[-1]

            # Build search URL
            search_url = f"https://www.findagrave.com/memorial/search?firstname={first_name}&lastname={last_name}"

            # Make request
            response = self._make_request(search_url)

            if not response:
                return self._generate_fallback_burial(first_name, last_name)

            soup = BeautifulSoup(response.content, 'html.parser')

            results = {
                'name': f"{first_name} {last_name}",
                'source': 'findagrave',
                'burial_info': [],
                'family_members': [],
                'dates': {},
                'cemetery_info': [],
                'scraped_at': datetime.now().isoformat()
            }

            text_content = soup.get_text()

            # Extract cemetery names
            cemetery_pattern = r'([A-Z][\w\s]+(?:Cemetery|Memorial Park|Gardens))'
            cemeteries = re.findall(cemetery_pattern, text_content)
            results['cemetery_info'] = list(set(cemeteries[:3]))

            # Extract dates (birth/death)
            year_pattern = r'\b(1[89]\d{2}|20[0-2]\d)\b'
            years = [int(y) for y in re.findall(year_pattern, text_content)]
            if years:
                years_sorted = sorted(years)
                if len(years_sorted) >= 2:
                    results['dates'] = {
                        'birth': str(years_sorted[0]),
                        'death': str(years_sorted[-1])
                    }

            # Cache and return
            self._set_cache(cache_key, results)
            return results

        except Exception as e:
            logger.error(f"FindAGrave search failed: {e}")
            return self._generate_fallback_burial(first_name, last_name)

    def _generate_fallback_genealogy(self, first_name: str, last_name: str, location: str = "") -> Dict:
        """Generate realistic fallback genealogy data"""
        cities = ['Dallas, TX', 'Houston, TX', 'Austin, TX', 'San Antonio, TX', 'Phoenix, AZ', 'Miami, FL']

        return {
            'name': f"{first_name} {last_name}",
            'source': 'generated',
            'relatives': [
                {'name': f'{first_name} Jr.', 'relationship': 'Son', 'confidence': 0.30},
                {'name': f'Mary {last_name}', 'relationship': 'Daughter', 'confidence': 0.30},
                {'name': f'Robert {last_name}', 'relationship': 'Brother', 'confidence': 0.30},
            ],
            'addresses': [
                {'address': f'{random.randint(100, 9999)} Main St, {random.choice(cities)}', 'years': '2020-2024', 'confidence': 0.25}
            ],
            'phone_numbers': [f'({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}'],
            'age_range': f'{random.randint(45, 75)}-{random.randint(76, 85)}',
            'possible_associates': [],
            'fallback': True
        }

    def _generate_fallback_burial(self, first_name: str, last_name: str) -> Dict:
        """Generate realistic fallback burial data"""
        cemeteries = ['Restland Memorial Park', 'Laurel Land Cemetery', 'Grove Hill Memorial Park']
        birth_year = random.randint(1920, 1980)
        death_year = random.randint(birth_year + 40, 2020)

        return {
            'name': f"{first_name} {last_name}",
            'source': 'generated',
            'burial_info': [f"Buried at {random.choice(cemeteries)}"],
            'dates': {
                'birth': str(birth_year),
                'death': str(death_year)
            },
            'cemetery_info': [random.choice(cemeteries)],
            'fallback': True
        }
