"""
Multi-Source Data Aggregation Service
Combines data from multiple sources for comprehensive results
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class DataAggregator:
    """
    Aggregates data from multiple sources in parallel
    """

    def __init__(self):
        from services.web_scraper import EnhancedWebScraper
        from services.ai_research import AIResearchService
        from services.fuzzy_matcher import FuzzyMatcher

        self.scraper = EnhancedWebScraper()
        self.ai_service = AIResearchService()
        self.matcher = FuzzyMatcher()

    def aggregate_person_data(self, name: str, location: str = None) -> Dict:
        """
        Aggregate person data from all available sources

        Args:
            name: Person name
            location: Optional location

        Returns:
            dict: Aggregated data with confidence scores
        """
        logger.info(f"Aggregating data for: {name}")

        results = {
            'name': name,
            'location': location,
            'started_at': datetime.now().isoformat(),
            'sources': {},
            'aggregated': {},
            'confidence': 0.0
        }

        # Collect from all sources
        sources_to_query = [
            ('familytreenow', lambda: self.scraper.search_familytreenow(name, location or '')),
            ('findagrave', lambda: self.scraper.search_findagrave(name, location or ''))
        ]

        for source_name, source_func in sources_to_query:
            try:
                logger.info(f"Querying {source_name}...")
                data = source_func()
                results['sources'][source_name] = data
            except Exception as e:
                logger.error(f"{source_name} query failed: {e}")
                results['sources'][source_name] = {'error': str(e)}

        # Aggregate data
        results['aggregated'] = self._merge_person_data(results['sources'])

        # AI analysis for enhanced insights
        if self.ai_service.client:
            try:
                ai_analysis = self.ai_service.analyze_person_data(results['sources'])
                results['ai_analysis'] = ai_analysis
                results['confidence'] = ai_analysis.get('confidence_score', 50.0)
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")

        results['completed_at'] = datetime.now().isoformat()

        return results

    def _merge_person_data(self, sources: Dict) -> Dict:
        """
        Intelligently merge data from multiple sources

        Args:
            sources: Dictionary of source data

        Returns:
            dict: Merged data
        """
        merged = {
            'names': [],
            'relatives': [],
            'addresses': [],
            'phone_numbers': [],
            'emails': [],
            'ages': [],
            'vital_records': []
        }

        # Merge names
        seen_names = set()
        for source_name, source_data in sources.items():
            if isinstance(source_data, dict):
                # Primary name
                name = source_data.get('name')
                if name and name not in seen_names:
                    merged['names'].append({
                        'name': name,
                        'source': source_name,
                        'confidence': 0.90
                    })
                    seen_names.add(name)

                # Relatives
                relatives = source_data.get('relatives', [])
                for rel in relatives:
                    rel_name = rel.get('name') if isinstance(rel, dict) else rel
                    if rel_name and rel_name not in seen_names:
                        merged['relatives'].append({
                            'name': rel_name,
                            'relationship': rel.get('relationship') if isinstance(rel, dict) else 'Unknown',
                            'source': source_name,
                            'confidence': rel.get('confidence', 0.60) if isinstance(rel, dict) else 0.60
                        })
                        seen_names.add(rel_name)

                # Addresses
                addresses = source_data.get('addresses', [])
                for addr in addresses:
                    addr_text = addr.get('address') if isinstance(addr, dict) else addr
                    if addr_text:
                        merged['addresses'].append({
                            'address': addr_text,
                            'source': source_name,
                            'years': addr.get('years') if isinstance(addr, dict) else 'Unknown',
                            'confidence': addr.get('confidence', 0.65) if isinstance(addr, dict) else 0.65
                        })

                # Phone numbers
                phones = source_data.get('phone_numbers', [])
                for phone in phones:
                    if phone and phone not in [p['number'] for p in merged['phone_numbers']]:
                        merged['phone_numbers'].append({
                            'number': phone,
                            'source': source_name,
                            'confidence': 0.70
                        })

                # Ages/dates
                if 'age_range' in source_data:
                    merged['ages'].append({
                        'range': source_data['age_range'],
                        'source': source_name
                    })

                # Vital records (from FindAGrave, etc)
                if 'dates' in source_data:
                    merged['vital_records'].append({
                        'dates': source_data['dates'],
                        'source': source_name
                    })

        # Deduplicate using fuzzy matching
        merged['addresses'] = self._deduplicate_addresses(merged['addresses'])
        merged['phone_numbers'] = self._deduplicate_phones(merged['phone_numbers'])

        return merged

    def _deduplicate_addresses(self, addresses: List[Dict]) -> List[Dict]:
        """Deduplicate addresses using fuzzy matching"""
        if not addresses:
            return []

        unique = []
        seen = set()

        for addr in addresses:
            addr_text = addr['address']

            # Check if similar to any seen address
            is_duplicate = False
            for seen_addr in seen:
                is_match, score = self.matcher.match_addresses(addr_text, seen_addr)
                if is_match:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique.append(addr)
                seen.add(addr_text)

        return unique

    def _deduplicate_phones(self, phones: List[Dict]) -> List[Dict]:
        """Deduplicate phone numbers"""
        unique = []
        seen = set()

        for phone in phones:
            phone_num = phone['number']
            # Extract just digits for comparison
            import re
            digits = re.sub(r'\D', '', phone_num)

            if digits and digits not in seen:
                unique.append(phone)
                seen.add(digits)

        return unique

    def enrich_property_data(self, property_id: int) -> Dict:
        """
        Enrich property data with additional sources

        Args:
            property_id: Property ID

        Returns:
            dict: Enriched property data
        """
        from models import Property

        property_obj = Property.query.get(property_id)
        if not property_obj:
            return {'error': 'Property not found'}

        enriched = {
            'property_id': property_id,
            'original_data': property_obj.to_dict(),
            'enrichments': {}
        }

        # Research owner if available
        if property_obj.owner_name:
            owner_data = self.aggregate_person_data(property_obj.owner_name)
            enriched['enrichments']['owner_research'] = owner_data

        return enriched
