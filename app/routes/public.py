from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app import db
from app.models import Organization, Job, Candidate, Application, Question, Answer
from app.utils.validators import save_uploaded_file
from app.services.ai_service import analyze_cv, evaluate_answer
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Landing page"""
    return render_template('public/index.html')

@public_bp.route('/<org_slug>/openings')
def organization_openings(org_slug):
    """Show all job openings for an organization"""
    organization = Organization.query.filter_by(slug=org_slug, status='active').first_or_404()
    
    # Get published jobs only
    jobs = Job.query.filter_by(
        organization_id=organization.id,
        status='published'
    ).order_by(Job.published_at.desc()).all()
    
    return render_template('public/openings.html', organization=organization, jobs=jobs)

@public_bp.route('/<org_slug>/jobs/<job_slug>')
def job_detail(org_slug, job_slug):
    """Show job details"""
    organization = Organization.query.filter_by(slug=org_slug, status='active').first_or_404()
    job = Job.query.filter_by(
        public_url_slug=job_slug,
        organization_id=organization.id,
        status='published'
    ).first_or_404()
    
    return render_template('public/job_detail.html', organization=organization, job=job)

@public_bp.route('/<org_slug>/jobs/<job_slug>/apply', methods=['GET', 'POST'])
def apply_job(org_slug, job_slug):
    """Application form"""
    organization = Organization.query.filter_by(slug=org_slug, status='active').first_or_404()
    job = Job.query.filter_by(
        public_url_slug=job_slug,
        organization_id=organization.id,
        status='published'
    ).first_or_404()
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        local_time = (request.form.get('local_time') or '').strip() or None
        timezone = (request.form.get('timezone') or '').strip() or None
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip and ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        # Handle CV upload
        cv_path = None
        if 'cv' in request.files:
            cv = request.files['cv']
            if cv.filename != '':
                cv_path, error = save_uploaded_file(cv, 'cv')
                if error:
                    flash(error, 'danger')
                    return redirect(url_for('public.apply_job', org_slug=org_slug, job_slug=job_slug))
        
        if not cv_path:
            flash('CV upload is required', 'danger')
            return redirect(url_for('public.apply_job', org_slug=org_slug, job_slug=job_slug))
        
        # Create candidate
        candidate = Candidate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            cv_path=cv_path
        )
        
        db.session.add(candidate)
        db.session.flush()  # Get candidate ID
        
        # Analyze CV using AI
        try:
            cv_analysis = analyze_cv(cv_path, job.description_html)
            candidate.cv_summary = cv_analysis['summary']
            candidate.matching_percentage = cv_analysis['matching_percentage']
        except Exception as e:
            print(f"Error analyzing CV: {e}")
            candidate.cv_summary = "Analysis pending"
            candidate.matching_percentage = 0.0
        
        # Create application
        application = Application(
            candidate_id=candidate.id,
            job_id=job.id,
            status='in_progress',
            ip_address=client_ip,
            local_time=local_time,
            timezone=timezone
        )
        
        # Calculate total weightage from questions
        questions = Question.query.filter_by(job_id=job.id).all()
        application.total_weightage = sum(q.weightage for q in questions)
        
        db.session.add(application)
        db.session.commit()
        
        # Store application ID in session for interview
        session['application_id'] = application.id
        
        return redirect(url_for('public.interview', application_id=application.id))
    
    return render_template('public/apply.html', organization=organization, job=job)

@public_bp.route('/interview/<int:application_id>')
def interview(application_id):
    """Voice interview interface"""
    application = Application.query.get_or_404(application_id)
    
    # Verify session
    if session.get('application_id') != application_id:
        flash('Invalid session', 'danger')
        return redirect(url_for('public.index'))
    
    # Get questions for this job
    questions = Question.query.filter_by(job_id=application.job_id).order_by(Question.order_index).all()
    
    return render_template('public/interview.html', 
                         application=application,
                         questions=questions)

@public_bp.route('/interview/<int:application_id>/complete', methods=['GET', 'POST'])
def complete_interview(application_id):
    """Show interview completion page"""
    application = Application.query.get_or_404(application_id)
    
    # Verify session for active interviews
    if session.get('application_id') != application_id and application.status != 'completed':
        return redirect(url_for('public.index'))
    
    if application.status != 'completed':
        application.status = 'completed'
        application.completed_at = datetime.utcnow()
        db.session.commit()
    
    # Clear session
    session.pop('application_id', None)
    
    return render_template('public/interview_complete.html', application=application)

