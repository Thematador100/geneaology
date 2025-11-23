"""
Background tasks for genealogy research and skip tracing
"""
from celery_app import celery
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3)
def async_person_research(self, person_name, location=None):
    """
    Asynchronously research a person across multiple data sources

    Args:
        person_name: Full name to research
        location: Optional location to narrow search

    Returns:
        dict: Comprehensive research results
    """
    try:
        from services.ai_research import AIResearchService
        from services.web_scraper import EnhancedWebScraper

        research_service = AIResearchService()
        scraper = EnhancedWebScraper()

        # Multi-source research
        results = {
            'person_name': person_name,
            'location': location,
            'started_at': datetime.utcnow().isoformat(),
            'sources': {}
        }

        # FamilyTreeNow
        try:
            results['sources']['familytreenow'] = scraper.search_familytreenow(person_name, location)
        except Exception as e:
            logger.error(f"FamilyTreeNow search failed: {e}")
            results['sources']['familytreenow'] = {'error': str(e)}

        # FindAGrave
        try:
            results['sources']['findagrave'] = scraper.search_findagrave(person_name, location)
        except Exception as e:
            logger.error(f"FindAGrave search failed: {e}")
            results['sources']['findagrave'] = {'error': str(e)}

        # AI Analysis
        try:
            results['ai_analysis'] = research_service.analyze_person_data(results['sources'])
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            results['ai_analysis'] = {'error': str(e)}

        results['completed_at'] = datetime.utcnow().isoformat()
        results['success'] = True

        return results

    except Exception as e:
        logger.error(f"Person research failed: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery.task(bind=True, max_retries=3)
def async_property_research(self, address, property_id=None):
    """
    Asynchronously research property and find heirs

    Args:
        address: Property address
        property_id: Optional property ID in database

    Returns:
        dict: Property research results with heir information
    """
    try:
        from services.property_research import PropertyResearchService

        research_service = PropertyResearchService()

        results = {
            'address': address,
            'property_id': property_id,
            'started_at': datetime.utcnow().isoformat(),
        }

        # Property data lookup
        property_data = research_service.research_property(address, property_id)
        results['property_data'] = property_data

        # Find heirs if owner identified
        if property_data.get('owner_name'):
            heir_results = research_service.find_heirs(property_data['owner_name'], property_id)
            results['heir_research'] = heir_results

        results['completed_at'] = datetime.utcnow().isoformat()
        results['success'] = True

        return results

    except Exception as e:
        logger.error(f"Property research failed: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery.task
def async_batch_research(property_ids):
    """
    Process multiple properties in batch

    Args:
        property_ids: List of property IDs to research

    Returns:
        dict: Summary of batch processing results
    """
    from models import db, Property

    results = {
        'total': len(property_ids),
        'successful': 0,
        'failed': 0,
        'errors': []
    }

    for prop_id in property_ids:
        try:
            property_obj = Property.query.get(prop_id)
            if property_obj:
                # Trigger async research for each property
                async_property_research.delay(property_obj.address, prop_id)
                results['successful'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({'property_id': prop_id, 'error': str(e)})

    return results


@celery.task
def update_heir_confidence_scores(property_id):
    """
    Recalculate confidence scores for all heirs of a property

    Args:
        property_id: Property ID

    Returns:
        dict: Updated scores
    """
    try:
        from services.scoring import HeirScoringEngine
        from models import db, Heir

        scoring_engine = HeirScoringEngine()

        heirs = Heir.query.filter_by(property_id=property_id).all()
        updated_count = 0

        for heir in heirs:
            try:
                score = scoring_engine.calculate_heir_score(heir)
                heir.confidence_score = score
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to score heir {heir.id}: {e}")

        db.session.commit()

        return {
            'property_id': property_id,
            'heirs_updated': updated_count,
            'total_heirs': len(heirs)
        }

    except Exception as e:
        logger.error(f"Heir scoring failed: {e}")
        return {'error': str(e)}
