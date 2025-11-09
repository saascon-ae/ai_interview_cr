import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://localhost/interview_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # SMTP Configuration
    SMTP_HOST = os.environ.get('SMTP_HOST', 'mail.saascon.ae')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 465))
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'False').lower() == 'true'
    SMTP_USE_SSL = os.environ.get('SMTP_USE_SSL', 'True').lower() == 'true'
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL', 'noreply@hrplatform.com')
    SMTP_FROM_NAME = os.environ.get('SMTP_FROM_NAME', 'HR Interview Platform')
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', './app/static/uploads')
    MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 10485760))  # 10MB default
    def _split_env_list(var_name, default):
        value = os.environ.get(var_name, default)
        return [item.strip().lower() for item in value.split(',') if item.strip()]

    ALLOWED_EXTENSIONS = _split_env_list('ALLOWED_EXTENSIONS', 'pdf,doc,docx')
    ALLOWED_CV_EXTENSIONS = _split_env_list('ALLOWED_CV_EXTENSIONS', 'pdf,doc,docx')
    ALLOWED_LOGO_EXTENSIONS = _split_env_list('ALLOWED_LOGO_EXTENSIONS', 'png,jpg,jpeg,gif,svg,webp')
    ALLOWED_AUDIO_EXTENSIONS = _split_env_list('ALLOWED_AUDIO_EXTENSIONS', 'webm,wav,mp3,ogg')
    
    # Application Configuration
    APP_URL = os.environ.get('APP_URL', 'http://localhost:5005')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Session Configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

