"""
Fuzzy Matching and Deduplication Service
Matches names, addresses, and identifies duplicate records
"""
import logging
from typing import List, Dict, Tuple, Optional
import re

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """
    Advanced fuzzy matching for names, addresses, and deduplication
    """

    def __init__(self, name_threshold=0.90, address_threshold=0.85):
        """
        Initialize fuzzy matcher

        Args:
            name_threshold: Minimum similarity score for names (0-1)
            address_threshold: Minimum similarity score for addresses (0-1)
        """
        self.name_threshold = name_threshold
        self.address_threshold = address_threshold

    def match_names(self, name1: str, name2: str) -> Tuple[bool, float]:
        """
        Match two person names with fuzzy logic

        Args:
            name1: First name
            name2: Second name

        Returns:
            tuple: (is_match, similarity_score)
        """
        if not name1 or not name2:
            return False, 0.0

        # Normalize names
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)

        # Exact match after normalization
        if norm1 == norm2:
            return True, 1.0

        # Parse name components
        from nameparser import HumanName

        parsed1 = HumanName(name1)
        parsed2 = HumanName(name2)

        # Check if first and last names match
        first_match = self._fuzzy_string_match(parsed1.first, parsed2.first)
        last_match = self._fuzzy_string_match(parsed1.last, parsed2.last)

        # Calculate overall similarity
        scores = []

        if parsed1.first and parsed2.first:
            scores.append(first_match)
        if parsed1.last and parsed2.last:
            scores.append(last_match * 1.2)  # Weight last name more

        # Middle name matching (optional but helpful)
        if parsed1.middle and parsed2.middle:
            middle_match = self._fuzzy_string_match(parsed1.middle, parsed2.middle)
            scores.append(middle_match * 0.8)

        # Calculate average score
        if scores:
            avg_score = sum(scores) / len(scores)
            avg_score = min(avg_score, 1.0)  # Cap at 1.0
            is_match = avg_score >= self.name_threshold
            return is_match, avg_score

        # Fallback to full string comparison
        similarity = self._fuzzy_string_match(norm1, norm2)
        return similarity >= self.name_threshold, similarity

    def match_addresses(self, addr1: str, addr2: str) -> Tuple[bool, float]:
        """
        Match two addresses with fuzzy logic

        Args:
            addr1: First address
            addr2: Second address

        Returns:
            tuple: (is_match, similarity_score)
        """
        if not addr1 or not addr2:
            return False, 0.0

        # Normalize addresses
        norm1 = self._normalize_address(addr1)
        norm2 = self._normalize_address(addr2)

        # Exact match
        if norm1 == norm2:
            return True, 1.0

        # Try to parse addresses
        try:
            import usaddress

            parsed1, _ = usaddress.tag(addr1)
            parsed2, _ = usaddress.tag(addr2)

            # Compare key components
            scores = []

            # Street number (must match exactly)
            num1 = parsed1.get('AddressNumber', '')
            num2 = parsed2.get('AddressNumber', '')
            if num1 and num2:
                if num1 == num2:
                    scores.append(1.0)
                else:
                    return False, 0.0  # Different street number = not a match

            # Street name (fuzzy match)
            street1 = parsed1.get('StreetName', '')
            street2 = parsed2.get('StreetName', '')
            if street1 and street2:
                street_score = self._fuzzy_string_match(street1, street2)
                scores.append(street_score * 1.5)  # Weight street name heavily

            # City (fuzzy match)
            city1 = parsed1.get('PlaceName', '')
            city2 = parsed2.get('PlaceName', '')
            if city1 and city2:
                city_score = self._fuzzy_string_match(city1, city2)
                scores.append(city_score)

            # State (exact match)
            state1 = parsed1.get('StateName', '')
            state2 = parsed2.get('StateName', '')
            if state1 and state2:
                scores.append(1.0 if state1 == state2 else 0.0)

            # Zip code
            zip1 = parsed1.get('ZipCode', '')
            zip2 = parsed2.get('ZipCode', '')
            if zip1 and zip2:
                scores.append(1.0 if zip1 == zip2 else 0.5)

            if scores:
                avg_score = sum(scores) / len(scores)
                avg_score = min(avg_score, 1.0)
                is_match = avg_score >= self.address_threshold
                return is_match, avg_score

        except:
            pass

        # Fallback to string similarity
        similarity = self._fuzzy_string_match(norm1, norm2)
        return similarity >= self.address_threshold, similarity

    def _fuzzy_string_match(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings

        Args:
            str1: First string
            str2: Second string

        Returns:
            float: Similarity score 0-1
        """
        if not str1 or not str2:
            return 0.0

        str1 = str1.lower().strip()
        str2 = str2.lower().strip()

        if str1 == str2:
            return 1.0

        # Try multiple algorithms and take the best score
        scores = []

        # Levenshtein distance
        try:
            from fuzzywuzzy import fuzz
            scores.append(fuzz.ratio(str1, str2) / 100.0)
            scores.append(fuzz.token_sort_ratio(str1, str2) / 100.0)
        except ImportError:
            pass

        # Jaro-Winkler distance
        try:
            import jellyfish
            scores.append(jellyfish.jaro_winkler_similarity(str1, str2))
        except ImportError:
            pass

        # Fallback to simple character overlap
        if not scores:
            scores.append(self._simple_similarity(str1, str2))

        return max(scores) if scores else 0.0

    def _simple_similarity(self, str1: str, str2: str) -> float:
        """Simple character-based similarity (fallback)"""
        if not str1 or not str2:
            return 0.0

        # Convert to sets of characters
        set1 = set(str1.lower())
        set2 = set(str2.lower())

        # Jaccard similarity
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        if not name:
            return ""

        # Remove extra whitespace
        name = ' '.join(name.split())

        # Remove punctuation except hyphens in names
        name = re.sub(r'[^\w\s-]', '', name)

        # Convert to lowercase
        name = name.lower()

        # Remove common suffixes for comparison
        suffixes = ['jr', 'sr', 'ii', 'iii', 'iv', 'esq', 'phd', 'md']
        parts = name.split()
        parts = [p for p in parts if p not in suffixes]

        return ' '.join(parts)

    def _normalize_address(self, address: str) -> str:
        """Normalize address for comparison"""
        if not address:
            return ""

        # Convert to lowercase
        addr = address.lower()

        # Standardize abbreviations
        replacements = {
            'street': 'st',
            'avenue': 'ave',
            'road': 'rd',
            'drive': 'dr',
            'lane': 'ln',
            'boulevard': 'blvd',
            'court': 'ct',
            'circle': 'cir',
            'place': 'pl',
            'north': 'n',
            'south': 's',
            'east': 'e',
            'west': 'w',
        }

        for full, abbr in replacements.items():
            addr = re.sub(r'\b' + full + r'\b', abbr, addr)

        # Remove extra whitespace and punctuation
        addr = re.sub(r'[^\w\s]', ' ', addr)
        addr = ' '.join(addr.split())

        return addr

    def find_duplicates(self, records: List[Dict], key_field: str, match_type='name') -> List[List[Dict]]:
        """
        Find duplicate records in a list

        Args:
            records: List of record dictionaries
            key_field: Field name to compare
            match_type: 'name' or 'address'

        Returns:
            list: List of duplicate groups
        """
        duplicates = []
        processed = set()

        match_func = self.match_names if match_type == 'name' else self.match_addresses

        for i, record1 in enumerate(records):
            if i in processed:
                continue

            dup_group = [record1]
            value1 = record1.get(key_field, '')

            for j, record2 in enumerate(records[i+1:], start=i+1):
                if j in processed:
                    continue

                value2 = record2.get(key_field, '')
                is_match, score = match_func(value1, value2)

                if is_match:
                    dup_group.append(record2)
                    processed.add(j)

            if len(dup_group) > 1:
                duplicates.append(dup_group)
                processed.add(i)

        return duplicates

    def merge_duplicate_records(self, duplicates: List[Dict]) -> Dict:
        """
        Merge duplicate records into a single record

        Args:
            duplicates: List of duplicate records

        Returns:
            dict: Merged record
        """
        if not duplicates:
            return {}

        # Start with first record
        merged = duplicates[0].copy()

        # Merge data from other records
        for record in duplicates[1:]:
            for key, value in record.items():
                if key not in merged or not merged[key]:
                    merged[key] = value
                elif isinstance(merged[key], list):
                    # Merge lists
                    if isinstance(value, list):
                        merged[key].extend(value)
                    else:
                        merged[key].append(value)

        # Add metadata
        merged['_merged_from'] = len(duplicates)
        merged['_duplicate_ids'] = [d.get('id') for d in duplicates if 'id' in d]

        return merged

    def match_phone_numbers(self, phone1: str, phone2: str) -> Tuple[bool, float]:
        """
        Match two phone numbers

        Args:
            phone1: First phone number
            phone2: Second phone number

        Returns:
            tuple: (is_match, confidence)
        """
        import phonenumbers

        try:
            # Parse both numbers
            num1 = phonenumbers.parse(phone1, 'US')
            num2 = phonenumbers.parse(phone2, 'US')

            # Compare
            if num1 == num2:
                return True, 1.0

            # Check if same number, different formatting
            format1 = phonenumbers.format_number(num1, phonenumbers.PhoneNumberFormat.E164)
            format2 = phonenumbers.format_number(num2, phonenumbers.PhoneNumberFormat.E164)

            if format1 == format2:
                return True, 1.0

            return False, 0.0

        except:
            # Fallback to string comparison
            digits1 = re.sub(r'\D', '', phone1)
            digits2 = re.sub(r'\D', '', phone2)

            if digits1 == digits2:
                return True, 1.0
            return False, 0.0
