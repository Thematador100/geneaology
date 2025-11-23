"""
Background tasks for PDF processing and analysis
"""
from celery_app import celery
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=2)
def async_process_pdf(self, pdf_path, document_id, property_id=None):
    """
    Asynchronously process PDF with OCR and AI analysis

    Args:
        pdf_path: Path to PDF file
        document_id: Document ID in database
        property_id: Optional associated property ID

    Returns:
        dict: Processing results with extracted data
    """
    try:
        from services.pdf_processor import PDFProcessor
        from services.ai_analyzer import AIAnalyzer
        from models import db, Document

        processor = PDFProcessor()
        ai_analyzer = AIAnalyzer()

        # Update document status
        document = Document.query.get(document_id)
        if document:
            document.processing_status = 'processing'
            db.session.commit()

        results = {
            'document_id': document_id,
            'started_at': datetime.utcnow().isoformat(),
        }

        # OCR extraction
        try:
            extracted_text = processor.extract_text(pdf_path)
            results['text_extracted'] = True
            results['text_length'] = len(extracted_text)
            results['ocr_confidence'] = processor.get_confidence_score()

            # Update document
            if document:
                document.extracted_text = extracted_text
                document.text_length = len(extracted_text)
                document.ocr_confidence = processor.get_confidence_score()
                document.ocr_completed = True
                db.session.commit()

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            results['text_extracted'] = False
            results['ocr_error'] = str(e)
            extracted_text = ""

        # AI Analysis
        try:
            if extracted_text:
                analysis = ai_analyzer.analyze_document(extracted_text, document_type='genealogy')
                results['ai_analysis'] = analysis
                results['entities'] = analysis.get('entities', {})

                # Update document
                if document:
                    document.analyzed_data = analysis
                    document.entities_extracted = analysis.get('entities', {})
                    document.ai_summary = analysis.get('summary', '')
                    document.ai_confidence = analysis.get('confidence', 0.0)
                    document.ai_analyzed = True
                    document.processing_status = 'completed'
                    db.session.commit()

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            results['ai_error'] = str(e)
            if document:
                document.processing_status = 'completed'
                db.session.commit()

        results['completed_at'] = datetime.utcnow().isoformat()
        results['success'] = True

        return results

    except Exception as e:
        logger.error(f"PDF processing failed: {e}")

        # Update document status to failed
        try:
            document = Document.query.get(document_id)
            if document:
                document.processing_status = 'failed'
                db.session.commit()
        except:
            pass

        raise self.retry(exc=e, countdown=120 * (2 ** self.request.retries))


@celery.task
def batch_process_pdfs(document_ids):
    """
    Process multiple PDFs in batch

    Args:
        document_ids: List of document IDs to process

    Returns:
        dict: Batch processing summary
    """
    from models import Document

    results = {
        'total': len(document_ids),
        'queued': 0,
        'errors': []
    }

    for doc_id in document_ids:
        try:
            document = Document.query.get(doc_id)
            if document and document.file_path:
                async_process_pdf.delay(document.file_path, doc_id, document.property_id)
                results['queued'] += 1
        except Exception as e:
            results['errors'].append({'document_id': doc_id, 'error': str(e)})

    return results


@celery.task
def extract_entities_from_document(document_id):
    """
    Extract and link entities (people, properties) from a document

    Args:
        document_id: Document ID

    Returns:
        dict: Extracted entities
    """
    try:
        from services.entity_extractor import EntityExtractor
        from models import Document

        extractor = EntityExtractor()
        document = Document.query.get(document_id)

        if not document or not document.extracted_text:
            return {'error': 'Document not found or no text extracted'}

        entities = extractor.extract_all(document.extracted_text)

        # Update document with entities
        document.entities_extracted = entities
        from models import db
        db.session.commit()

        return {
            'document_id': document_id,
            'entities': entities,
            'people_found': len(entities.get('people', [])),
            'addresses_found': len(entities.get('addresses', [])),
            'dates_found': len(entities.get('dates', []))
        }

    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        return {'error': str(e)}
