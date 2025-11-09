from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Organization, User, Job, Application, Candidate, Answer
from app.utils.auth import super_admin_required, generate_password, generate_slug
from app.utils.validators import save_uploaded_file
from app.services.email_service import send_invitation_email
from werkzeug.utils import secure_filename
import os

super_admin_bp = Blueprint('super_admin', __name__)

@super_admin_bp.route('/dashboard')
@login_required
@super_admin_required
def dashboard():
    organizations = Organization.query.order_by(Organization.created_at.desc()).all()
    
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
        
        # Format file sizes
        def format_size(size_bytes):
            """Convert bytes to human readable format"""
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} TB"
        
        org_stats.append({
            'organization': org,
            'total_jobs': total_jobs,
            'total_candidates': total_candidates,
            'cv_total_size': format_size(cv_total_size),
            'audio_total_size': format_size(audio_total_size)
        })
    
    return render_template('super_admin/dashboard.html', org_stats=org_stats)

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

