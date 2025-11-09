import os
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_file_size(file):
    """Check if file size is within limit"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= current_app.config['MAX_UPLOAD_SIZE']

def save_uploaded_file(file, subfolder):
    """Save uploaded file and return the path"""
    if not file or not file.filename:
        return None, "Invalid file type"

    extension_group = current_app.config.get('ALLOWED_EXTENSIONS', [])
    if subfolder == 'logos':
        extension_group = current_app.config.get('ALLOWED_LOGO_EXTENSIONS', extension_group)
    elif subfolder == 'cv':
        extension_group = current_app.config.get('ALLOWED_CV_EXTENSIONS', extension_group)
    elif subfolder == 'interviews':
        extension_group = current_app.config.get('ALLOWED_AUDIO_EXTENSIONS', extension_group)

    if file and allowed_file(file.filename, extension_group):
        if not validate_file_size(file):
            return None, "File size exceeds limit"
        
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder, filename)
        file.save(filepath)
        
        return os.path.join('uploads', subfolder, filename), None
    
    return None, "Invalid file type"

