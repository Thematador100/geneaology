"""
AI-Powered Heir Probability Scoring Engine
Calculates confidence scores for potential heirs using multiple factors
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class HeirScoringEngine:
    """
    Advanced heir probability scoring using AI and rule-based logic
    """

    def __init__(self):
        """Initialize scoring engine"""
        self.weights = {
            'relationship_proximity': 0.30,  # How close is the relationship
            'data_verification': 0.25,       # Quality and verification of data
            'contact_information': 0.15,     # Availability of contact info
            'documentation': 0.15,           # Supporting documentation
            'name_match_quality': 0.10,      # Name matching confidence
            'legal_factors': 0.05            # Legal considerations
        }

    def calculate_heir_score(self, heir_data: Dict) -> float:
        """
        Calculate comprehensive heir probability score

        Args:
            heir_data: Heir information dictionary or Heir model object

        Returns:
            float: Score from 0-100
        """
        # Convert model object to dict if needed
        if hasattr(heir_data, 'to_dict'):
            heir_dict = heir_data.to_dict()
        elif hasattr(heir_data, '__dict__'):
            heir_dict = heir_data.__dict__
        else:
            heir_dict = heir_data

        scores = {
            'relationship_proximity': self._score_relationship_proximity(heir_dict),
            'data_verification': self._score_data_verification(heir_dict),
            'contact_information': self._score_contact_information(heir_dict),
            'documentation': self._score_documentation(heir_dict),
            'name_match_quality': self._score_name_match(heir_dict),
            'legal_factors': self._score_legal_factors(heir_dict)
        }

        # Calculate weighted score
        total_score = sum(
            scores[factor] * self.weights[factor]
            for factor in scores
        )

        # Store individual scores if heir is a model object
        if hasattr(heir_data, 'name_match_score'):
            heir_data.name_match_score = scores['name_match_quality']

        return round(total_score, 2)

    def _score_relationship_proximity(self, heir_dict: Dict) -> float:
        """
        Score based on relationship closeness to deceased

        Scoring logic:
        - Direct children: 100
        - Grandchildren: 85
        - Siblings: 75
        - Spouse: 90
        - Nieces/nephews: 65
        - More distant: decreases
        """
        relationship = (heir_dict.get('relationship') or '').lower()
        degree = heir_dict.get('relationship_degree', 999)

        # Direct relationship types
        relationship_scores = {
            'son': 100,
            'daughter': 100,
            'child': 100,
            'spouse': 95,
            'wife': 95,
            'husband': 95,
            'mother': 90,
            'father': 90,
            'parent': 90,
            'grandchild': 85,
            'grandson': 85,
            'granddaughter': 85,
            'sibling': 75,
            'brother': 75,
            'sister': 75,
            'niece': 65,
            'nephew': 65,
            'aunt': 55,
            'uncle': 55,
            'cousin': 45,
            'great-grandchild': 70,
        }

        # Check for direct match
        for rel_type, score in relationship_scores.items():
            if rel_type in relationship:
                return score

        # Score based on degree if available
        if degree < 999:
            if degree == 1:
                return 100  # Direct child
            elif degree == 2:
                return 85   # Grandchild
            elif degree == 3:
                return 70   # Great-grandchild
            elif degree == 4:
                return 55   # Great-great-grandchild
            else:
                return max(30, 100 - (degree * 15))

        # Unknown relationship
        return 30

    def _score_data_verification(self, heir_dict: Dict) -> float:
        """
        Score based on verification status and data quality

        Factors:
        - Verification status
        - Data sources
        - Cross-referenced data
        """
        score = 0

        # Verification status
        verification = (heir_dict.get('verification_status') or '').lower()
        if verification == 'verified':
            score += 100
        elif verification == 'partial':
            score += 60
        elif 'unverified' in verification:
            score += 20
        else:
            score += 30

        # Has verified date
        if heir_dict.get('verified_date'):
            score += 10

        # Multiple data sources
        data_sources = heir_dict.get('data_sources') or []
        if isinstance(data_sources, list):
            source_bonus = min(len(data_sources) * 10, 40)
            score += source_bonus

        # Relationship verified
        if heir_dict.get('relationship_verified'):
            score += 20

        # Documentation exists
        if heir_dict.get('documentation_exists'):
            score += 20

        return min(score / 2, 100)  # Normalize to 0-100

    def _score_contact_information(self, heir_dict: Dict) -> float:
        """
        Score based on availability and quality of contact information
        """
        score = 0

        # Has phone number
        phone = heir_dict.get('phone')
        if phone and len(str(phone).strip()) > 0:
            score += 30
            # Contact verified
            if heir_dict.get('contact_verified'):
                score += 20

        # Has email
        email = heir_dict.get('email')
        if email and len(str(email).strip()) > 0:
            score += 25

        # Has address
        address = heir_dict.get('address')
        if address and len(str(address).strip()) > 0:
            score += 25

        # Contact attempts made
        contact_attempts = heir_dict.get('contact_attempts', 0)
        if contact_attempts > 0:
            score += 10

        # Contact status
        contact_status = (heir_dict.get('contact_status') or '').lower()
        if 'responded' in contact_status or 'interested' in contact_status:
            score += 30

        return min(score, 100)

    def _score_documentation(self, heir_dict: Dict) -> float:
        """
        Score based on supporting documentation
        """
        score = 40  # Base score

        # Documentation exists flag
        if heir_dict.get('documentation_exists'):
            score += 30

        # Data sources available
        data_sources = heir_dict.get('data_sources') or []
        if isinstance(data_sources, list) and len(data_sources) > 0:
            score += 20

        # Discovered by reliable method
        discovered_by = (heir_dict.get('discovered_by') or '').lower()
        if 'manual' in discovered_by or 'verified' in discovered_by:
            score += 20
        elif 'pdf' in discovered_by or 'document' in discovered_by:
            score += 15
        elif 'ai' in discovered_by:
            score += 10

        return min(score, 100)

    def _score_name_match(self, heir_dict: Dict) -> float:
        """
        Score based on name matching quality
        """
        # Use existing name match score if available
        name_match = heir_dict.get('name_match_score')
        if name_match is not None:
            return float(name_match)

        # Check for name
        name = heir_dict.get('name')
        if not name or len(str(name).strip()) < 3:
            return 20

        # Has parsed name components
        if heir_dict.get('first_name') and heir_dict.get('last_name'):
            return 80

        # Default moderate confidence
        return 60

    def _score_legal_factors(self, heir_dict: Dict) -> float:
        """
        Score based on legal factors
        """
        score = 50  # Base score

        # Marked as legal heir
        if heir_dict.get('legal_heir'):
            score += 30

        # Has intestate share calculated
        if heir_dict.get('intestate_share') and heir_dict.get('intestate_share') > 0:
            score += 20

        # Has person_id (linked to person record)
        if heir_dict.get('person_id'):
            score += 10

        return min(score, 100)

    def calculate_property_success_probability(self, property_obj) -> float:
        """
        Calculate overall success probability for a property case

        Args:
            property_obj: Property model object

        Returns:
            float: Success probability 0-100
        """
        score = 0

        # Has heirs identified
        heir_count = property_obj.heir_count or 0
        if heir_count > 0:
            score += 30
        else:
            return 10  # Very low if no heirs

        # Average heir confidence
        avg_confidence = property_obj.heir_confidence_avg or 0
        score += (avg_confidence * 0.30)

        # Research completeness
        completeness = property_obj.research_completeness or 0
        score += (completeness * 0.25)

        # Property value (higher value = more effort)
        if property_obj.overage_amount:
            if property_obj.overage_amount > 50000:
                score += 15
            elif property_obj.overage_amount > 10000:
                score += 10
            else:
                score += 5

        # Case complexity
        complexity = (property_obj.case_complexity or '').lower()
        if complexity == 'simple':
            score += 10
        elif complexity == 'moderate':
            score += 5

        return min(score, 100)

    def calculate_intestate_shares(self, heirs: List[Dict], deceased_info: Dict = None) -> List[Dict]:
        """
        Calculate intestate succession shares for heirs

        Args:
            heirs: List of heir dictionaries
            deceased_info: Information about deceased

        Returns:
            list: Heirs with calculated intestate_share percentages
        """
        # Group heirs by relationship degree
        degree_groups = {}

        for heir in heirs:
            degree = heir.get('relationship_degree', 999)
            if degree not in degree_groups:
                degree_groups[degree] = []
            degree_groups[degree].append(heir)

        # Apply intestate succession rules (simplified US law)
        # Priority: 1=children, 2=grandchildren, 3=siblings, etc.

        # Find highest priority group with heirs
        closest_degree = min(degree_groups.keys()) if degree_groups else 999

        if closest_degree == 999:
            # No valid heirs
            return heirs

        # Get heirs at closest degree
        primary_heirs = degree_groups[closest_degree]

        # Calculate equal shares among primary heirs
        share_per_heir = 100.0 / len(primary_heirs) if primary_heirs else 0

        # Assign shares
        for heir in heirs:
            if heir in primary_heirs:
                heir['intestate_share'] = round(share_per_heir, 2)
                heir['heir_class'] = 'primary'
            else:
                heir['intestate_share'] = 0
                heir['heir_class'] = 'contingent'

        return heirs

    def rank_heirs(self, heirs: List, recalculate=True) -> List:
        """
        Rank heirs by probability score

        Args:
            heirs: List of Heir objects or dictionaries
            recalculate: Whether to recalculate scores

        Returns:
            list: Heirs sorted by confidence score (highest first)
        """
        if recalculate:
            for heir in heirs:
                score = self.calculate_heir_score(heir)
                if hasattr(heir, 'confidence_score'):
                    heir.confidence_score = score
                elif isinstance(heir, dict):
                    heir['confidence_score'] = score

        # Sort by confidence score
        return sorted(
            heirs,
            key=lambda h: h.confidence_score if hasattr(h, 'confidence_score') else h.get('confidence_score', 0),
            reverse=True
        )

    def get_score_breakdown(self, heir_data: Dict) -> Dict:
        """
        Get detailed breakdown of heir score

        Args:
            heir_data: Heir information

        Returns:
            dict: Detailed score breakdown
        """
        # Convert to dict if model
        if hasattr(heir_data, 'to_dict'):
            heir_dict = heir_data.to_dict()
        elif hasattr(heir_data, '__dict__'):
            heir_dict = heir_data.__dict__
        else:
            heir_dict = heir_data

        breakdown = {
            'relationship_proximity': {
                'score': self._score_relationship_proximity(heir_dict),
                'weight': self.weights['relationship_proximity'],
                'weighted_score': self._score_relationship_proximity(heir_dict) * self.weights['relationship_proximity']
            },
            'data_verification': {
                'score': self._score_data_verification(heir_dict),
                'weight': self.weights['data_verification'],
                'weighted_score': self._score_data_verification(heir_dict) * self.weights['data_verification']
            },
            'contact_information': {
                'score': self._score_contact_information(heir_dict),
                'weight': self.weights['contact_information'],
                'weighted_score': self._score_contact_information(heir_dict) * self.weights['contact_information']
            },
            'documentation': {
                'score': self._score_documentation(heir_dict),
                'weight': self.weights['documentation'],
                'weighted_score': self._score_documentation(heir_dict) * self.weights['documentation']
            },
            'name_match_quality': {
                'score': self._score_name_match(heir_dict),
                'weight': self.weights['name_match_quality'],
                'weighted_score': self._score_name_match(heir_dict) * self.weights['name_match_quality']
            },
            'legal_factors': {
                'score': self._score_legal_factors(heir_dict),
                'weight': self.weights['legal_factors'],
                'weighted_score': self._score_legal_factors(heir_dict) * self.weights['legal_factors']
            }
        }

        breakdown['total_score'] = sum(b['weighted_score'] for b in breakdown.values())

        return breakdown
