from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Organization, User, Job, Application, Candidate, Answer, AIPrompt
from app.utils.auth import super_admin_required, generate_password, generate_slug
from app.utils.validators import save_uploaded_file
from app.services.email_service import send_invitation_email
from werkzeug.utils import secure_filename
import os
import math

super_admin_bp = Blueprint('super_admin', __name__)

@super_admin_bp.route('/dashboard')
@login_required
@super_admin_required
def dashboard():
    organizations = Organization.query.order_by(Organization.created_at.desc()).all()
    
    def format_size(size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    # Calculate statistics for each organization
    org_stats = []
    for org in organizations:
        # Total jobs created by this organization
        total_jobs = Job.query.filter_by(organization_id=org.id).count()
        
        # Get all applications for this organization's jobs
        applications = Application.query.join(Job).filter(
            Job.organization_id == org.id
        ).all()
        
        # Total unique candidates who applied
        candidate_ids = set([app.candidate_id for app in applications])
        total_candidates = len(candidate_ids)
        
        # Calculate total CV file size
        cv_total_size = 0
        for candidate_id in candidate_ids:
            candidate = Candidate.query.get(candidate_id)
            if candidate and candidate.cv_path:
                cv_full_path = os.path.join(current_app.root_path, 'static', candidate.cv_path)
                if os.path.exists(cv_full_path):
                    try:
                        cv_total_size += os.path.getsize(cv_full_path)
                    except OSError:
                        pass
        
        # Calculate total answer audio file size
        audio_total_size = 0
        for app in applications:
            answers = Answer.query.filter_by(application_id=app.id).all()
            for answer in answers:
                if answer.audio_path:
                    audio_full_path = os.path.join(current_app.root_path, 'static', answer.audio_path)
                    if os.path.exists(audio_full_path):
                        try:
                            audio_total_size += os.path.getsize(audio_full_path)
                        except OSError:
                            pass
        
        # Preserve raw bytes for summary cards
        cv_total_bytes = cv_total_size
        audio_total_bytes = audio_total_size

        org_stats.append({
            'organization': org,
            'total_jobs': total_jobs,
            'total_candidates': total_candidates,
            'cv_total_size': format_size(cv_total_bytes),
            'audio_total_size': format_size(audio_total_bytes),
            'cv_total_bytes': cv_total_bytes,
            'audio_total_bytes': audio_total_bytes
        })
    
    search_query = request.args.get('search', '').strip()
    if search_query:
        search_lower = search_query.lower()
        filtered_stats = []
        for stat in org_stats:
            org = stat['organization']
            contact_name = f"{(org.first_name or '').strip()} {(org.last_name or '').strip()}".strip()
            if (
                search_lower in (org.name or '').lower() or
                search_lower in (org.email or '').lower() or
                search_lower in contact_name.lower()
            ):
                filtered_stats.append(stat)
        org_stats = filtered_stats

    sort_by = request.args.get('sort', 'name')
    sort_direction = request.args.get('direction', 'asc')
    sort_direction = 'desc' if sort_direction == 'desc' else 'asc'

    def contact_key(stat):
        org = stat['organization']
        return f"{(org.first_name or '').strip()} {(org.last_name or '').strip()}".strip().lower()

    sort_key_map = {
        'name': lambda stat: (stat['organization'].name or '').lower(),
        'email': lambda stat: (stat['organization'].email or '').lower(),
        'contact': contact_key,
        'jobs': lambda stat: stat['total_jobs'],
        'candidates': lambda stat: stat['total_candidates'],
        'cv_storage': lambda stat: stat['cv_total_bytes'],
        'audio_storage': lambda stat: stat['audio_total_bytes'],
        'status': lambda stat: (stat['organization'].status or '').lower(),
    }
    sort_key = sort_key_map.get(sort_by, sort_key_map['name'])
    org_stats.sort(key=sort_key, reverse=(sort_direction == 'desc'))

    total_jobs = sum(stat['total_jobs'] for stat in org_stats)
    total_candidates = sum(stat['total_candidates'] for stat in org_stats)
    total_cv_bytes = sum(stat['cv_total_bytes'] for stat in org_stats)
    total_audio_bytes = sum(stat['audio_total_bytes'] for stat in org_stats)
    active_count = sum(1 for stat in org_stats if stat['organization'].status == 'active')
    inactive_count = sum(1 for stat in org_stats if stat['organization'].status == 'inactive')

    summary = {
        'organizations': len(org_stats),
        'active_orgs': active_count,
        'inactive_orgs': inactive_count,
        'total_jobs': total_jobs,
        'total_candidates': total_candidates,
        'cv_storage': format_size(total_cv_bytes) if org_stats else '0.00 B',
        'audio_storage': format_size(total_audio_bytes) if org_stats else '0.00 B'
    }

    page = request.args.get('page', 1, type=int)
    page = max(page, 1)
    per_page = 10
    total_items = len(org_stats)
    if total_items:
        total_pages = max(1, math.ceil(total_items / per_page))
        page = min(page, total_pages)
    else:
        page = 1
        total_pages = 1
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_stats = org_stats[start_idx:end_idx]

    pagination = {
        'page': page,
        'per_page': per_page,
        'total_items': total_items,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }

    return render_template(
        'super_admin/dashboard.html',
        org_stats=paginated_stats,
        summary=summary,
        search=search_query,
        sort_by=sort_by,
        sort_direction=sort_direction,
        pagination=pagination
    )

@super_admin_bp.route('/organization/<int:org_id>/jobs')
@login_required
@super_admin_required
def organization_jobs(org_id):
    organization = Organization.query.get_or_404(org_id)
    page = request.args.get('page', 1, type=int) or 1
    per_page = 20

    jobs_query = Job.query.filter_by(organization_id=org_id).order_by(Job.created_at.desc())
    jobs_pagination = jobs_query.paginate(page=page, per_page=per_page, error_out=False)
    jobs_list = jobs_pagination.items

    for job in jobs_list:
        job.application_count = job.applications.count()

    jobs_stats = {
        'start_index': ((jobs_pagination.page - 1) * jobs_pagination.per_page + 1) if jobs_pagination.total else 0,
        'end_index': min(jobs_pagination.page * jobs_pagination.per_page, jobs_pagination.total) if jobs_pagination.total else 0,
        'total': jobs_pagination.total
    }

    return render_template(
        'super_admin/organization_jobs.html',
        organization=organization,
        jobs=jobs_list,
        jobs_pagination=jobs_pagination,
        jobs_stats=jobs_stats
    )

@super_admin_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@super_admin_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
        elif len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'danger')
        elif new_password != confirm_password:
            flash('New password and confirmation do not match.', 'danger')
        else:
            current_user.set_password(new_password)
            current_user.must_change_password = False
            db.session.commit()
            flash('Password updated successfully.', 'success')
            return redirect(url_for('super_admin.dashboard'))

    return render_template('super_admin/change_password.html')

@super_admin_bp.route('/organization/add', methods=['GET', 'POST'])
@login_required
@super_admin_required
def add_organization():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        trn = request.form.get('trn')
        
        # Check if organization email already exists
        if Organization.query.filter_by(email=email).first():
            flash('Organization with this email already exists', 'danger')
            return redirect(url_for('super_admin.add_organization'))
        
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
                    return redirect(url_for('super_admin.add_organization'))
        
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
        db.session.commit()
        
        flash('Organization added successfully', 'success')
        return redirect(url_for('super_admin.dashboard'))
    
    return render_template('super_admin/add_organization.html')

@super_admin_bp.route('/organization/edit/<int:org_id>', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_organization(org_id):
    organization = Organization.query.get_or_404(org_id)
    
    if request.method == 'POST':
        organization.name = request.form.get('name')
        organization.email = request.form.get('email')
        organization.first_name = request.form.get('first_name')
        organization.last_name = request.form.get('last_name')
        organization.phone = request.form.get('phone')
        organization.trn = request.form.get('trn')
        
        # Handle logo upload
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo.filename != '':
                logo_path, error = save_uploaded_file(logo, 'logos')
                if error:
                    flash(error, 'danger')
                else:
                    organization.logo_path = logo_path
        
        db.session.commit()
        flash('Organization updated successfully', 'success')
        return redirect(url_for('super_admin.dashboard'))
    
    return render_template('super_admin/edit_organization.html', organization=organization)

@super_admin_bp.route('/organization/toggle-status/<int:org_id>')
@login_required
@super_admin_required
def toggle_organization_status(org_id):
    organization = Organization.query.get_or_404(org_id)
    organization.status = 'inactive' if organization.status == 'active' else 'active'
    
    # Also deactivate all users if organization is being deactivated
    if organization.status == 'inactive':
        for user in organization.users:
            user.is_active = False
    else:
        for user in organization.users:
            user.is_active = True
    
    db.session.commit()
    flash(f'Organization {organization.status}d successfully', 'success')
    return redirect(url_for('super_admin.dashboard'))

@super_admin_bp.route('/organization/send-invite/<int:org_id>', methods=['POST'])
@login_required
@super_admin_required
def send_invite(org_id):
    organization = Organization.query.get_or_404(org_id)
    
    # Generate new password
    password = generate_password()
    
    # Check if user already exists for this organization
    user = User.query.filter_by(email=organization.email, organization_id=org_id).first()
    
    if user:
        # Update existing user with new password
        user.set_password(password)
        user.must_change_password = True
        user.is_active = True
    else:
        # Create new user
        user = User(
            email=organization.email,
            role='org_admin',
            organization_id=org_id,
            must_change_password=True,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
    
    db.session.commit()
    
    # Send invitation email
    try:
        send_invitation_email(organization, password)
        flash('Invitation sent successfully', 'success')
    except Exception as e:
        flash(f'Error sending invitation: {str(e)}', 'danger')
    
    return redirect(url_for('super_admin.dashboard'))

@super_admin_bp.route('/organization/delete/<int:org_id>', methods=['POST'])
@login_required
@super_admin_required
def delete_organization(org_id):
    organization = Organization.query.get_or_404(org_id)
    db.session.delete(organization)
    db.session.commit()
    flash('Organization deleted successfully', 'success')
    return redirect(url_for('super_admin.dashboard'))

@super_admin_bp.route('/ai-prompts')
@login_required
@super_admin_required
def ai_prompts():
    """Display all AI prompts"""
    prompts = AIPrompt.query.order_by(AIPrompt.category, AIPrompt.name).all()
    
    # Group prompts by category
    categories = {}
    for prompt in prompts:
        category = prompt.category or 'Other'
        if category not in categories:
            categories[category] = []
        categories[category].append(prompt)
    
    return render_template('super_admin/ai_prompts.html', categories=categories)

@super_admin_bp.route('/ai-prompts/edit/<int:prompt_id>', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_ai_prompt(prompt_id):
    """Edit an AI prompt"""
    prompt = AIPrompt.query.get_or_404(prompt_id)
    
    if request.method == 'POST':
        prompt.name = request.form.get('name')
        prompt.description = request.form.get('description')
        prompt.system_message = request.form.get('system_message')
        prompt.prompt_template = request.form.get('prompt_template')
        prompt.model = request.form.get('model')
        prompt.temperature = float(request.form.get('temperature', 0.5))
        prompt.category = request.form.get('category')
        prompt.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('AI Prompt updated successfully', 'success')
        return redirect(url_for('super_admin.ai_prompts'))
    
    return render_template('super_admin/edit_ai_prompt.html', prompt=prompt)

@super_admin_bp.route('/ai-prompts/add', methods=['GET', 'POST'])
@login_required
@super_admin_required
def add_ai_prompt():
    """Add a new AI prompt"""
    if request.method == 'POST':
        key = request.form.get('key')
        
        # Check if key already exists
        if AIPrompt.query.filter_by(key=key).first():
            flash('A prompt with this key already exists', 'danger')
            return redirect(url_for('super_admin.add_ai_prompt'))
        
        prompt = AIPrompt(
            key=key,
            name=request.form.get('name'),
            description=request.form.get('description'),
            system_message=request.form.get('system_message'),
            prompt_template=request.form.get('prompt_template'),
            model=request.form.get('model', 'gpt-3.5-turbo'),
            temperature=float(request.form.get('temperature', 0.5)),
            category=request.form.get('category'),
            is_active=request.form.get('is_active') == 'on'
        )
        
        db.session.add(prompt)
        db.session.commit()
        flash('AI Prompt added successfully', 'success')
        return redirect(url_for('super_admin.ai_prompts'))
    
    return render_template('super_admin/add_ai_prompt.html')

@super_admin_bp.route('/ai-prompts/toggle/<int:prompt_id>', methods=['POST'])
@login_required
@super_admin_required
def toggle_ai_prompt(prompt_id):
    """Toggle AI prompt active status"""
    prompt = AIPrompt.query.get_or_404(prompt_id)
    prompt.is_active = not prompt.is_active
    db.session.commit()
    
    status = 'activated' if prompt.is_active else 'deactivated'
    flash(f'Prompt {status} successfully', 'success')
    return redirect(url_for('super_admin.ai_prompts'))

@super_admin_bp.route('/ai-prompts/delete/<int:prompt_id>', methods=['POST'])
@login_required
@super_admin_required
def delete_ai_prompt(prompt_id):
    """Delete an AI prompt"""
    prompt = AIPrompt.query.get_or_404(prompt_id)
    db.session.delete(prompt)
    db.session.commit()
    flash('AI Prompt deleted successfully', 'success')
    return redirect(url_for('super_admin.ai_prompts'))

