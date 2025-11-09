from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models import Organization, Job, Application, Candidate
from functools import wraps

api_bp = Blueprint('api', __name__)

# Simple API key authentication
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        # In production, store API keys in database
        valid_api_key = current_app.config.get('API_KEY', 'demo-api-key-change-me')
        
        if not api_key or api_key != valid_api_key:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/organizations', methods=['GET'])
@require_api_key
def get_organizations():
    """List all active organizations"""
    organizations = Organization.query.filter_by(status='active').all()
    
    return jsonify({
        'organizations': [{
            'id': org.id,
            'name': org.name,
            'slug': org.slug,
            'email': org.email
        } for org in organizations]
    })

@api_bp.route('/organizations/<int:org_id>/jobs', methods=['GET'])
@require_api_key
def get_jobs(org_id):
    """List all jobs for an organization"""
    status_filter = request.args.get('status', 'published')
    
    jobs = Job.query.filter_by(
        organization_id=org_id,
        status=status_filter
    ).all()
    
    return jsonify({
        'jobs': [{
            'id': job.id,
            'title': job.title,
            'description': job.description_html,
            'status': job.status,
            'public_url_slug': job.public_url_slug,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'published_at': job.published_at.isoformat() if job.published_at else None
        } for job in jobs]
    })

@api_bp.route('/jobs', methods=['POST'])
@require_api_key
def create_job():
    """Create a new job (requires admin rights)"""
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('organization_id'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    from app.utils.auth import generate_slug
    
    # Generate slug
    base_slug = generate_slug(data['title'])
    slug = base_slug
    counter = 1
    while Job.query.filter_by(public_url_slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    job = Job(
        title=data['title'],
        description_html=data.get('description', ''),
        status=data.get('status', 'draft'),
        organization_id=data['organization_id'],
        public_url_slug=slug
    )
    
    db.session.add(job)
    db.session.commit()
    
    return jsonify({
        'id': job.id,
        'title': job.title,
        'public_url_slug': job.public_url_slug,
        'status': job.status
    }), 201

@api_bp.route('/jobs/<int:job_id>/applications', methods=['GET'])
@require_api_key
def get_applications(job_id):
    """List all applications for a job"""
    applications = Application.query.filter_by(job_id=job_id).all()
    
    return jsonify({
        'applications': [{
            'id': app.id,
            'candidate': {
                'first_name': app.candidate.first_name,
                'last_name': app.candidate.last_name,
                'email': app.candidate.email,
                'phone': app.candidate.phone
            },
            'status': app.status,
            'total_score': app.total_score,
            'total_weightage': app.total_weightage,
            'matching_percentage': app.candidate.matching_percentage,
            'created_at': app.created_at.isoformat() if app.created_at else None
        } for app in applications]
    })

@api_bp.route('/candidates/<int:candidate_id>', methods=['GET'])
@require_api_key
def get_candidate(candidate_id):
    """Get candidate details"""
    candidate = Candidate.query.get_or_404(candidate_id)
    
    applications = []
    for app in candidate.applications:
        applications.append({
            'id': app.id,
            'job_title': app.job.title,
            'status': app.status,
            'total_score': app.total_score,
            'personality_profile': app.personality_profile,
            'created_at': app.created_at.isoformat() if app.created_at else None
        })
    
    return jsonify({
        'id': candidate.id,
        'first_name': candidate.first_name,
        'last_name': candidate.last_name,
        'email': candidate.email,
        'phone': candidate.phone,
        'cv_summary': candidate.cv_summary,
        'matching_percentage': candidate.matching_percentage,
        'applications': applications
    })

@api_bp.route('/applications', methods=['POST'])
def submit_application():
    """Submit a new application (public endpoint, no API key required)"""
    data = request.get_json()
    
    required_fields = ['first_name', 'last_name', 'email', 'job_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create candidate
    candidate = Candidate(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data.get('phone', '')
    )
    
    db.session.add(candidate)
    db.session.flush()
    
    # Create application
    application = Application(
        candidate_id=candidate.id,
        job_id=data['job_id'],
        status='pending'
    )
    
    # Capture metadata if provided
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip and ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    application.ip_address = client_ip
    
    local_time_value = data.get('local_time')
    timezone_value = data.get('timezone')
    
    if local_time_value is not None:
        cleaned_local = str(local_time_value).strip()
        application.local_time = cleaned_local or None
    
    if timezone_value is not None:
        cleaned_timezone = str(timezone_value).strip()
        application.timezone = cleaned_timezone or None
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({
        'application_id': application.id,
        'candidate_id': candidate.id,
        'status': 'success'
    }), 201

