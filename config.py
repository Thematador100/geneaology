"""
Configuration Management for Advanced Skip Tracing Platform
Handles all environment variables and configuration settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    TESTING = False

    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'genealogy.db'))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Upload
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = str(BASE_DIR / 'uploads')
    PDF_FOLDER = str(BASE_DIR / 'pdf_uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf', 'txt'}

    # AI Configuration
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'anthropic')  # 'anthropic' or 'openai'
    AI_MODEL = os.getenv('AI_MODEL', 'claude-3-5-sonnet-20241022')
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', '4096'))

    # OCR Configuration
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
    OCR_LANGUAGE = os.getenv('OCR_LANGUAGE', 'eng')

    # Celery / Redis (for async tasks)
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Data Source APIs
    # Public Records
    ATTOM_API_KEY = os.getenv('ATTOM_API_KEY', '')  # Property data API
    CORE_LOGIC_API_KEY = os.getenv('CORE_LOGIC_API_KEY', '')

    # Skip Tracing Services
    TRACERS_API_KEY = os.getenv('TRACERS_API_KEY', '')
    TRUTHFINDER_API_KEY = os.getenv('TRUTHFINDER_API_KEY', '')
    SPOKEO_API_KEY = os.getenv('SPOKEO_API_KEY', '')

    # Phone/Email Services
    WHITEPAGES_API_KEY = os.getenv('WHITEPAGES_API_KEY', '')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')

    # Social Media (for OSINT)
    PIPL_API_KEY = os.getenv('PIPL_API_KEY', '')
    CLEARBIT_API_KEY = os.getenv('CLEARBIT_API_KEY', '')

    # Web Scraping
    SCRAPING_USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    SCRAPING_TIMEOUT = int(os.getenv('SCRAPING_TIMEOUT', '30'))
    SCRAPING_MAX_RETRIES = int(os.getenv('SCRAPING_MAX_RETRIES', '3'))

    # Fuzzy Matching
    FUZZY_MATCH_THRESHOLD = float(os.getenv('FUZZY_MATCH_THRESHOLD', '0.85'))
    NAME_SIMILARITY_THRESHOLD = float(os.getenv('NAME_SIMILARITY_THRESHOLD', '0.90'))
    ADDRESS_SIMILARITY_THRESHOLD = float(os.getenv('ADDRESS_SIMILARITY_THRESHOLD', '0.85'))

    # Heir Scoring
    HEIR_MIN_CONFIDENCE = float(os.getenv('HEIR_MIN_CONFIDENCE', '0.60'))
    HEIR_HIGH_CONFIDENCE = float(os.getenv('HEIR_HIGH_CONFIDENCE', '0.85'))

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '100'))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '1000'))

    # Cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'app.log'))

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # Security
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Feature Flags
    ENABLE_AI_ANALYSIS = os.getenv('ENABLE_AI_ANALYSIS', 'True').lower() == 'true'
    ENABLE_OCR = os.getenv('ENABLE_OCR', 'True').lower() == 'true'
    ENABLE_SOCIAL_MEDIA = os.getenv('ENABLE_SOCIAL_MEDIA', 'False').lower() == 'true'
    ENABLE_PAID_APIS = os.getenv('ENABLE_PAID_APIS', 'False').lower() == 'true'
    ENABLE_BACKGROUND_TASKS = os.getenv('ENABLE_BACKGROUND_TASKS', 'True').lower() == 'true'

    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.PDF_FOLDER, exist_ok=True)
        os.makedirs(BASE_DIR / 'logs', exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_PATH = ':memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
