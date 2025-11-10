from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from app import db
from app.models import Organization, Job, Candidate, Application, Question, Answer, User
from app.utils.validators import save_uploaded_file
from app.utils.auth import generate_password, generate_slug
from app.services.ai_service import analyze_cv, evaluate_answer
from app.services.email_service import send_invitation_email
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Landing page"""
    featured_org = Organization.query.filter_by(status='active').first()
    return render_template('public/index.html', featured_org=featured_org)

@public_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Visitor registration page"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        trn = request.form.get('trn')
        
        # Validate required fields
        if not all([name, email, first_name, last_name]):
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('public.register'))
        
        # Check if organization email already exists
        if Organization.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please login or use a different email.', 'danger')
            return redirect(url_for('public.register'))
        
        # Check if user email already exists
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please login or use a different email.', 'danger')
            return redirect(url_for('public.register'))
        
        # Generate slug from organization name
        base_slug = generate_slug(name)
        slug = base_slug
        counter = 1
        while Organization.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Handle logo upload
        logo_path = None
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo.filename != '':
                logo_path, error = save_uploaded_file(logo, 'logos')
                if error:
                    flash(error, 'danger')
                    return redirect(url_for('public.register'))
        
        try:
            # Create organization
            organization = Organization(
                name=name,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                trn=trn,
                logo_path=logo_path,
                slug=slug,
                status='active'
            )
            
            db.session.add(organization)
            db.session.flush()  # Get organization ID
            
            # Generate temporary password
            temp_password = generate_password()
            
            # Create admin user for this organization
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='org_admin',
                organization_id=organization.id,
                must_change_password=True,
                is_active=True
            )
            user.set_password(temp_password)
            
            db.session.add(user)
            db.session.commit()
            
            # Send invitation email with temporary password
            try:
                send_invitation_email(organization, temp_password)
                flash('Registration successful! Please check your email for login credentials.', 'success')
            except Exception as e:
                print(f"Error sending invitation email: {e}")
                flash('Registration successful! However, we couldn\'t send the email. Please contact support for your login credentials.', 'warning')
            
            return redirect(url_for('public.index'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during registration: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('public.register'))
    
    return render_template('public/register.html')

@public_bp.route('/<org_slug>/openings')
def organization_openings(org_slug):
    """Show all job openings for an organization"""
    organization = Organization.query.filter_by(slug=org_slug, status='active').first_or_404()
    page = request.args.get('page', 1, type=int)
    
    # Get published jobs only
    pagination = Job.query.filter_by(
        organization_id=organization.id,
        status='published'
    ).order_by(Job.published_at.desc()).paginate(page=page, per_page=6, error_out=False)
    
    jobs = pagination.items
    
    return render_template('public/openings.html', organization=organization, jobs=jobs, pagination=pagination)

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
        # If a previous request left the scoped session in an error state, clear it now
        db.session.rollback()

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
        
        def _clean_matching_percentage(value):
            """Ensure we persist a numeric matching percentage (0-100)."""
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                return max(0.0, min(float(value), 100.0))
            if isinstance(value, str):
                import re
                match = re.search(r'-?\d+(\.\d+)?', value)
                if match:
                    try:
                        return max(0.0, min(float(match.group()), 100.0))
                    except ValueError:
                        pass
            return 0.0

        cv_summary = "Analysis pending"
        matching_percentage = 0.0

        try:
            cv_analysis = analyze_cv(cv_path, job.description_html)
            cv_summary = cv_analysis.get('summary', cv_summary)
            matching_percentage = _clean_matching_percentage(cv_analysis.get('matching_percentage'))
        except Exception:
            current_app.logger.exception("CV analysis failed during application submission")

        try:
            # Create candidate
            candidate = Candidate(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                cv_path=cv_path,
                cv_summary=cv_summary,
                matching_percentage=matching_percentage
            )
            
            db.session.add(candidate)
            db.session.flush()  # Get candidate ID
            
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
            application.total_weightage = sum((q.weightage or 0) for q in questions)
            
            db.session.add(application)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            orig = getattr(exc, 'orig', None)
            debug_message = f"{exc}"
            if orig:
                debug_message = f"{debug_message} | orig={orig}"
            current_app.logger.exception("Error while submitting job application")
            flash(f'We hit an unexpected error while submitting your application. Details: {debug_message}', 'danger')
            return redirect(url_for('public.apply_job', org_slug=org_slug, job_slug=job_slug))
        
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

