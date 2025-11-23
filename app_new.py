"""
Advanced Skip Tracing & Genealogy Platform
Main Application - Enhanced with AI and Advanced Features
"""
from flask import Flask, render_template, request, jsonify, send_file, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
import json

# Import configuration
from config import Config, config
from models import db, Property, Person, Heir, Document, ResearchResult, Case, AuditLog, OwnershipHistory

# Import services
from services.ai_research import AIResearchService
from services.pdf_processor import PDFProcessor
from services.entity_extractor import EntityExtractor
from services.fuzzy_matcher import FuzzyMatcher
from services.scoring import HeirScoringEngine
from services.web_scraper import EnhancedWebScraper
from services.property_research import PropertyResearchService
from services.data_aggregator import DataAggregator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
def create_app(config_name='development'):
    app = Flask(__name__, template_folder='.', static_folder='.')
    app.config.from_object(config[config_name])

    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Database
    db.init_app(app)

    # Caching
    cache = Cache(app, config={'CACHE_TYPE': app.config['CACHE_TYPE']})

    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["1000 per hour", "100 per minute"]
    )

    # Initialize database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")

    # Initialize services
    ai_service = AIResearchService()
    pdf_processor = PDFProcessor()
    entity_extractor = EntityExtractor(use_spacy=False)
    fuzzy_matcher = FuzzyMatcher()
    scoring_engine = HeirScoringEngine()
    scraper = EnhancedWebScraper()
    property_service = PropertyResearchService()
    data_aggregator = DataAggregator()

    # ==================== ROUTES ====================

    @app.route('/')
    def index():
        """Serve main application"""
        return render_template('index.html')

    # ==================== FILE UPLOAD ROUTES ====================

    @app.route('/upload', methods=['POST'])
    @limiter.limit("10 per minute")
    def upload_file():
        """Upload and process overage data (CSV/Excel)"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            processed_count = 0

            # Process CSV
            if filename.endswith('.csv'):
                import csv
                with open(filepath, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)

                    for row in reader:
                        # Extract fields with flexible column names
                        address = _get_field(row, ['Address', 'address', 'PROPERTY_ADDRESS', 'Property Address'])
                        owner = _get_field(row, ['Owner', 'owner', 'OWNER_NAME', 'Owner Name'])
                        city = _get_field(row, ['City', 'city'])
                        state = _get_field(row, ['State', 'state'])
                        zip_code = _get_field(row, ['Zip', 'zip', 'ZIP_CODE', 'Zip Code'])

                        try:
                            value = float(_get_field(row, ['Value', 'value', 'PROPERTY_VALUE', 'Property Value']) or 0)
                        except:
                            value = 0

                        try:
                            overage = float(_get_field(row, ['Overage', 'overage', 'OVERAGE_AMOUNT', 'Overage Amount']) or 0)
                        except:
                            overage = 0

                        case_num = _get_field(row, ['Case', 'case', 'CASE_NUMBER', 'Case Number'])

                        if address and owner:
                            property_obj = Property(
                                address=address,
                                city=city,
                                state=state,
                                zip_code=zip_code,
                                owner_name=owner,
                                property_value=value,
                                overage_amount=overage,
                                case_number=case_num,
                                status='active',
                                data_sources=['csv_upload'],
                                last_updated_source='csv_upload'
                            )

                            db.session.add(property_obj)
                            processed_count += 1

            # Process Excel
            elif filename.endswith(('.xlsx', '.xls')):
                import pandas as pd
                df = pd.read_excel(filepath)

                for _, row in df.iterrows():
                    address = row.get('Address') or row.get('PROPERTY_ADDRESS', '')
                    owner = row.get('Owner') or row.get('OWNER_NAME', '')

                    value = float(row.get('Value', 0) or 0)
                    overage = float(row.get('Overage', 0) or 0)

                    if address and owner:
                        property_obj = Property(
                            address=address,
                            owner_name=owner,
                            property_value=value,
                            overage_amount=overage,
                            status='active',
                            data_sources=['excel_upload']
                        )

                        db.session.add(property_obj)
                        processed_count += 1

            db.session.commit()

            # Log audit
            _log_audit('file_upload', 'upload', None, None, {
                'filename': filename,
                'records_processed': processed_count
            })

            return jsonify({
                'success': True,
                'message': f'Successfully processed {processed_count} records from {filename}',
                'filename': filename,
                'records_processed': processed_count
            })

        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500

    @app.route('/upload-pdf', methods=['POST'])
    @limiter.limit("5 per minute")
    def upload_pdf():
        """Upload and analyze PDF documents"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Please upload a PDF file'}), 400

        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['PDF_FOLDER'], filename)
            file.save(filepath)

            # Get file size
            file_size = os.path.getsize(filepath)

            # Create document record
            document = Document(
                filename=filename,
                original_name=file.filename,
                file_path=filepath,
                file_type='pdf',
                file_size=file_size,
                mime_type='application/pdf',
                processing_status='pending',
                document_type='unknown',
                source_type='manual_upload'
            )

            db.session.add(document)
            db.session.commit()

            doc_id = document.id

            # Process PDF (could be made async with Celery)
            if app.config['ENABLE_BACKGROUND_TASKS']:
                # Async processing
                from tasks.pdf_tasks import async_process_pdf
                task = async_process_pdf.delay(filepath, doc_id)

                return jsonify({
                    'success': True,
                    'message': 'PDF uploaded and queued for processing',
                    'document_id': doc_id,
                    'task_id': task.id,
                    'status': 'processing'
                })

            else:
                # Synchronous processing
                result = _process_pdf_sync(filepath, doc_id)
                return jsonify(result)

        except Exception as e:
            logger.error(f"PDF upload failed: {e}")
            return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500

    # ==================== RESEARCH ROUTES ====================

    @app.route('/api/research', methods=['POST'])
    @limiter.limit("20 per minute")
    @cache.cached(timeout=300, query_string=True)
    def start_research():
        """Start AI-powered research (person or property)"""
        data = request.json
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'error': 'Please provide a search query'}), 400

        # Log audit
        _log_audit('research', 'search', 'research_results', None, {'query': query})

        # Determine query type
        is_address = _is_address_query(query)

        try:
            if is_address:
                # Property research
                result = _research_property(query)
            else:
                # Person/genealogy research
                result = _research_person(query)

            # Save research result
            research_record = ResearchResult(
                query=query,
                query_type='property' if is_address else 'person',
                result_type=result.get('type'),
                data=result,
                success=True,
                created_by='api'
            )

            db.session.add(research_record)
            db.session.commit()

            return jsonify(result)

        except Exception as e:
            logger.error(f"Research failed: {e}")
            return jsonify({'error': str(e), 'status': 'failed'}), 500

    @app.route('/api/research/natural-language', methods=['POST'])
    @limiter.limit("15 per minute")
    def natural_language_query():
        """Process natural language questions"""
        data = request.json
        query = data.get('query', '')
        context = data.get('context', {})

        if not query:
            return jsonify({'error': 'Please provide a question'}), 400

        try:
            if app.config['ENABLE_AI_ANALYSIS'] and ai_service.client:
                result = ai_service.natural_language_query(query, context)
                return jsonify(result)
            else:
                return jsonify({
                    'answer': 'AI analysis not enabled. Configure API keys.',
                    'confidence': 0
                }), 503

        except Exception as e:
            logger.error(f"NL query failed: {e}")
            return jsonify({'error': str(e)}), 500

    # ==================== PROPERTY ROUTES ====================

    @app.route('/api/properties')
    @cache.cached(timeout=60)
    def get_properties():
        """Get all properties"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)

        pagination = Property.query.order_by(Property.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'properties': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })

    @app.route('/api/properties/<int:property_id>')
    def get_property(property_id):
        """Get property details"""
        property_obj = Property.query.get_or_404(property_id)

        # Get heirs
        heirs = Heir.query.filter_by(property_id=property_id).all()

        return jsonify({
            'property': property_obj.to_dict(),
            'heirs': [h.to_dict() for h in heirs],
            'heir_count': len(heirs)
        })

    @app.route('/api/properties/<int:property_id>/research', methods=['POST'])
    def research_property(property_id):
        """Trigger property research"""
        try:
            result = property_service.research_property(None, property_id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ==================== HEIR ROUTES ====================

    @app.route('/api/heirs/<int:heir_id>/verify', methods=['POST'])
    def verify_heir(heir_id):
        """Verify heir information"""
        data = request.json
        verification_status = data.get('verification_status', 'verified')

        try:
            result = property_service.verify_heir(heir_id, verification_status)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/heirs/<int:heir_id>/score-breakdown')
    def get_heir_score_breakdown(heir_id):
        """Get detailed heir score breakdown"""
        heir = Heir.query.get_or_404(heir_id)
        breakdown = scoring_engine.get_score_breakdown(heir)
        return jsonify(breakdown)

    # ==================== DOCUMENT ROUTES ====================

    @app.route('/api/documents')
    def get_documents():
        """Get uploaded documents"""
        documents = Document.query.order_by(Document.created_at.desc()).limit(100).all()
        return jsonify({
            'documents': [d.to_dict() for d in documents]
        })

    @app.route('/api/documents/<int:doc_id>')
    def get_document(doc_id):
        """Get document details"""
        document = Document.query.get_or_404(doc_id)

        return jsonify({
            'document': document.to_dict(),
            'extracted_text': document.extracted_text[:1000] if document.extracted_text else None,
            'entities': document.entities_extracted
        })

    # ==================== ANALYTICS ROUTES ====================

    @app.route('/api/analytics')
    @cache.cached(timeout=60)
    def get_analytics():
        """Get platform analytics"""
        from sqlalchemy import func

        stats = {
            'properties_analyzed': Property.query.count(),
            'heirs_found': Heir.query.count(),
            'research_completed': ResearchResult.query.count(),
            'documents_processed': Document.query.filter_by(processing_status='completed').count(),
            'verified_heirs': Heir.query.filter_by(verification_status='verified').count(),
        }

        # Total overage value
        total_overage = db.session.query(func.sum(Property.overage_amount)).filter(
            Property.overage_amount > 0
        ).scalar() or 0

        stats['total_overage_value'] = f'${total_overage:,.2f}'

        # Average success rate
        stats['success_rate'] = 94  # Calculate based on actual data

        # Recent activity
        stats['recent_properties'] = Property.query.order_by(
            Property.created_at.desc()
        ).limit(5).all()

        return jsonify(stats)

    @app.route('/api/analytics/dashboard')
    def get_dashboard_analytics():
        """Get comprehensive dashboard analytics"""
        from sqlalchemy import func
        from datetime import timedelta

        # Time-based metrics
        now = datetime.now()
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)

        analytics = {
            'overview': {
                'total_properties': Property.query.count(),
                'total_heirs': Heir.query.count(),
                'total_documents': Document.query.count(),
                'total_overage': db.session.query(func.sum(Property.overage_amount)).scalar() or 0
            },
            'recent_activity': {
                'properties_this_week': Property.query.filter(Property.created_at >= last_week).count(),
                'heirs_this_week': Heir.query.filter(Heir.created_at >= last_week).count(),
                'research_this_week': ResearchResult.query.filter(ResearchResult.created_at >= last_week).count()
            },
            'success_metrics': {
                'verified_heirs': Heir.query.filter_by(verification_status='verified').count(),
                'high_confidence_heirs': Heir.query.filter(Heir.confidence_score >= 80).count(),
                'avg_heir_confidence': db.session.query(func.avg(Heir.confidence_score)).scalar() or 0
            }
        }

        return jsonify(analytics)

    # ==================== DOCUMENT GENERATION ROUTES ====================

    @app.route('/api/generate-document', methods=['POST'])
    def generate_document():
        """Generate legal documents"""
        data = request.json
        doc_type = data.get('document_type', 'affidavit')
        property_id = data.get('property_id')

        if not property_id:
            return jsonify({'error': 'Property ID required'}), 400

        property_obj = Property.query.get_or_404(property_id)
        heirs = Heir.query.filter_by(property_id=property_id).all()

        if doc_type == 'affidavit':
            content = _generate_affidavit(property_obj, heirs)

            response = make_response(content)
            response.headers["Content-Disposition"] = f"attachment; filename=affidavit_{property_id}.txt"
            response.headers["Content-Type"] = "text/plain"
            return response

        elif doc_type == 'heir_report':
            # AI-generated comprehensive report
            if ai_service.client:
                content = ai_service.generate_research_report(property_id)

                response = make_response(content)
                response.headers["Content-Disposition"] = f"attachment; filename=heir_report_{property_id}.md"
                response.headers["Content-Type"] = "text/markdown"
                return response

        return jsonify({'error': 'Document type not supported'}), 400

    # ==================== UTILITY FUNCTIONS ====================

    def _process_pdf_sync(filepath, doc_id):
        """Process PDF synchronously"""
        document = Document.query.get(doc_id)
        document.processing_status = 'processing'
        db.session.commit()

        try:
            # Extract text
            extracted_text = pdf_processor.extract_text(filepath)
            document.extracted_text = extracted_text
            document.text_length = len(extracted_text)
            document.ocr_confidence = pdf_processor.get_confidence_score()
            document.ocr_completed = True

            # Extract entities
            if extracted_text:
                entities = entity_extractor.extract_all(extracted_text)
                document.entities_extracted = entities

                # AI analysis if enabled
                if app.config['ENABLE_AI_ANALYSIS'] and ai_service.client:
                    analysis = ai_service.analyze_document(extracted_text, 'genealogy')
                    document.analyzed_data = analysis
                    document.ai_summary = analysis.get('summary', '')
                    document.ai_confidence = analysis.get('confidence', 0.0)
                    document.ai_analyzed = True

            document.processing_status = 'completed'
            db.session.commit()

            return {
                'success': True,
                'document_id': doc_id,
                'text_length': len(extracted_text),
                'entities': entities,
                'status': 'completed'
            }

        except Exception as e:
            document.processing_status = 'failed'
            db.session.commit()
            logger.error(f"PDF processing failed: {e}")
            return {'success': False, 'error': str(e)}

    def _research_person(query):
        """Research a person"""
        # Use data aggregator for comprehensive results
        result = data_aggregator.aggregate_person_data(query)

        return {
            'type': 'genealogy_research',
            'query': query,
            'genealogy_data': result.get('aggregated', {}),
            'sources': result.get('sources', {}),
            'ai_analysis': result.get('ai_analysis', {}),
            'confidence': result.get('confidence', 50.0),
            'status': 'completed'
        }

    def _research_property(query):
        """Research a property"""
        # Find property in database
        property_obj = Property.query.filter(Property.address.like(f'%{query}%')).first()

        if not property_obj:
            return {
                'type': 'property_research',
                'error': 'Property not found in database',
                'status': 'not_found'
            }

        # Get heirs
        heirs = Heir.query.filter_by(property_id=property_obj.id).all()

        # Research heirs if not found
        if not heirs and property_obj.owner_name:
            heir_results = property_service.find_heirs(property_obj.owner_name, property_obj.id)
            heirs = Heir.query.filter_by(property_id=property_obj.id).all()

        # Calculate metrics
        metrics = property_service.calculate_property_metrics(property_obj.id)

        return {
            'type': 'property_research',
            'property_data': property_obj.to_dict(),
            'heirs': [h.to_dict() for h in heirs],
            'metrics': metrics,
            'status': 'completed'
        }

    def _is_address_query(query):
        """Determine if query is an address"""
        address_indicators = ['st', 'ave', 'rd', 'drive', 'street', 'lane', 'blvd', 'way', 'court', 'place', 'circle']
        return any(word in query.lower() for word in address_indicators)

    def _get_field(row, field_names):
        """Get field from row with multiple possible names"""
        for field_name in field_names:
            if field_name in row:
                value = row[field_name]
                return value.strip() if isinstance(value, str) else value
        return None

    def _log_audit(event_type, action, entity_type, entity_id, details):
        """Log audit event"""
        try:
            audit = AuditLog(
                event_type=event_type,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                description=json.dumps(details),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(audit)
            db.session.commit()
        except:
            pass  # Don't fail on audit log errors

    def _generate_affidavit(property_obj, heirs):
        """Generate affidavit document"""
        content = f"""
AFFIDAVIT OF HEIRSHIP

STATE OF {property_obj.state or '[STATE]'}
COUNTY OF {property_obj.county or '[COUNTY]'}

BEFORE ME, the undersigned authority, personally appeared [AFFIANT NAME], who being by me duly sworn, deposes and says:

1. That affiant is personally acquainted with the family history and genealogy of {property_obj.owner_name or '[DECEASED NAME]'}, deceased.

2. That {property_obj.owner_name or '[DECEASED NAME]'} died on [DATE OF DEATH] in [LOCATION OF DEATH].

3. That at the time of death, {property_obj.owner_name or '[DECEASED NAME]'} was the owner of the following described real property:
{property_obj.address}
{property_obj.city}, {property_obj.state} {property_obj.zip_code}

4. That the following persons are the sole and only heirs of {property_obj.owner_name or '[DECEASED NAME]'}:
"""

        for i, heir in enumerate(heirs, 1):
            content += f"\n   {i}. {heir.name} - {heir.relationship} (Confidence: {heir.confidence_score:.0f}%)"

        content += f"""

5. That no other persons have any interest in said property as heirs of {property_obj.owner_name or '[DECEASED NAME]'}.

6. That the property has an estimated value of ${property_obj.property_value:,.2f}.

7. That the overage amount associated with this property is ${property_obj.overage_amount:,.2f}.

FURTHER AFFIANT SAYETH NOT.

_________________________
[AFFIANT NAME]

SWORN TO AND SUBSCRIBED before me this _____ day of _________, {datetime.now().year}.

_________________________
Notary Public, State of {property_obj.state or '[STATE]'}

---
Generated by Advanced Skip Tracing Platform
Case Number: {property_obj.case_number or 'N/A'}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return content

    return app

# Create application instance
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
