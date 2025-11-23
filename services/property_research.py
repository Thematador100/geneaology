"""
Property Research Service
Researches properties and finds heirs
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PropertyResearchService:
    """
    Advanced property research and heir finding
    """

    def __init__(self):
        from services.web_scraper import EnhancedWebScraper
        from services.fuzzy_matcher import FuzzyMatcher
        from services.scoring import HeirScoringEngine

        self.scraper = EnhancedWebScraper()
        self.matcher = FuzzyMatcher()
        self.scoring_engine = HeirScoringEngine()

    def research_property(self, address: str, property_id: Optional[int] = None) -> Dict:
        """
        Research property details

        Args:
            address: Property address
            property_id: Optional property ID in database

        Returns:
            dict: Property data
        """
        from models import db, Property

        # Try to find in database
        if property_id:
            property_obj = Property.query.get(property_id)
        else:
            property_obj = Property.query.filter(
                Property.address.like(f'%{address}%')
            ).first()

        if property_obj:
            return property_obj.to_dict()

        # Property not in database
        return {
            'address': address,
            'found_in_database': False,
            'message': 'Property not found in database. Upload overage data first.'
        }

    def find_heirs(self, owner_name: str, property_id: Optional[int] = None) -> Dict:
        """
        Find potential heirs for a property owner

        Args:
            owner_name: Name of property owner (likely deceased)
            property_id: Property ID to associate heirs with

        Returns:
            dict: Heir research results
        """
        from models import db, Heir, Person

        logger.info(f"Starting heir research for: {owner_name}")

        results = {
            'owner_name': owner_name,
            'property_id': property_id,
            'started_at': datetime.now().isoformat(),
            'heirs_found': [],
            'sources_used': []
        }

        # Search genealogy sources
        try:
            # FamilyTreeNow search
            ftn_data = self.scraper.search_familytreenow(owner_name)
            results['sources_used'].append('familytreenow')

            # Extract potential heirs from relatives
            if ftn_data.get('relatives'):
                for relative in ftn_data['relatives']:
                    heir_data = {
                        'name': relative.get('name'),
                        'relationship': relative.get('relationship', 'Unknown'),
                        'data_source': 'familytreenow',
                        'confidence': relative.get('confidence', 0.50),
                        'discovered_at': datetime.now().isoformat()
                    }

                    # Add contact info if available
                    if ftn_data.get('phone_numbers'):
                        heir_data['phone'] = ftn_data['phone_numbers'][0]
                    if ftn_data.get('addresses'):
                        heir_data['address'] = ftn_data['addresses'][0].get('address')

                    results['heirs_found'].append(heir_data)

            # FindAGrave search
            fag_data = self.scraper.search_findagrave(owner_name)
            results['sources_used'].append('findagrave')

            # Extract family members from burial records
            if fag_data.get('family_members'):
                for family_member in fag_data['family_members']:
                    results['heirs_found'].append({
                        'name': family_member,
                        'relationship': 'Family Member',
                        'data_source': 'findagrave',
                        'confidence': 0.45
                    })

        except Exception as e:
            logger.error(f"Heir research failed: {e}")
            results['error'] = str(e)

        # Save heirs to database if property_id provided
        if property_id and results['heirs_found']:
            saved_count = 0
            for heir_data in results['heirs_found']:
                try:
                    # Check if heir already exists
                    existing = Heir.query.filter_by(
                        property_id=property_id,
                        name=heir_data['name']
                    ).first()

                    if not existing:
                        heir = Heir(
                            property_id=property_id,
                            name=heir_data['name'],
                            relationship=heir_data.get('relationship'),
                            phone=heir_data.get('phone'),
                            address=heir_data.get('address'),
                            data_sources=[heir_data.get('data_source')],
                            discovered_by='ai_research',
                            verification_status='unverified'
                        )

                        # Calculate confidence score
                        heir.confidence_score = self.scoring_engine.calculate_heir_score(heir_data)

                        db.session.add(heir)
                        saved_count += 1

                except Exception as e:
                    logger.error(f"Failed to save heir: {e}")

            if saved_count > 0:
                db.session.commit()
                results['saved_to_database'] = saved_count

        results['completed_at'] = datetime.now().isoformat()
        results['total_heirs_found'] = len(results['heirs_found'])

        return results

    def verify_heir(self, heir_id: int, verification_status: str, verified_by: str = 'manual') -> Dict:
        """
        Verify an heir's information

        Args:
            heir_id: Heir ID
            verification_status: 'verified', 'partial', 'unverified', 'invalid'
            verified_by: Who verified

        Returns:
            dict: Verification result
        """
        from models import db, Heir

        heir = Heir.query.get(heir_id)
        if not heir:
            return {'error': 'Heir not found'}

        heir.verification_status = verification_status
        heir.verified_by = verified_by
        heir.verified_date = datetime.now()

        # Recalculate confidence score
        heir.confidence_score = self.scoring_engine.calculate_heir_score(heir)

        db.session.commit()

        return {
            'heir_id': heir_id,
            'verification_status': verification_status,
            'confidence_score': heir.confidence_score,
            'updated_at': datetime.now().isoformat()
        }

    def calculate_property_metrics(self, property_id: int) -> Dict:
        """
        Calculate metrics for a property

        Args:
            property_id: Property ID

        Returns:
            dict: Property metrics
        """
        from models import db, Property, Heir

        property_obj = Property.query.get(property_id)
        if not property_obj:
            return {'error': 'Property not found'}

        # Get all heirs
        heirs = Heir.query.filter_by(property_id=property_id).all()

        # Calculate metrics
        heir_count = len(heirs)
        avg_confidence = sum(h.confidence_score or 0 for h in heirs) / heir_count if heir_count > 0 else 0
        verified_count = sum(1 for h in heirs if h.verification_status == 'verified')

        # Update property
        property_obj.heir_count = heir_count
        property_obj.heir_confidence_avg = round(avg_confidence, 2)

        # Calculate research completeness
        completeness = 0
        if property_obj.owner_name:
            completeness += 25
        if heir_count > 0:
            completeness += 50
        if verified_count > 0:
            completeness += 25

        property_obj.research_completeness = completeness

        # Calculate success probability
        property_obj.success_probability = self.scoring_engine.calculate_property_success_probability(property_obj)

        db.session.commit()

        return {
            'property_id': property_id,
            'heir_count': heir_count,
            'avg_confidence': round(avg_confidence, 2),
            'verified_heirs': verified_count,
            'research_completeness': completeness,
            'success_probability': property_obj.success_probability
        }
