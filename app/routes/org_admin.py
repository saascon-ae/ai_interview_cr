from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Job, Question, Application, Candidate, Answer, User
from app.utils.auth import org_admin_required, generate_slug, generate_password
from app.services.ai_service import generate_questions_from_description
from app.services.email_service import send_user_invitation_email
from datetime import datetime
from math import ceil
from urllib.parse import urlencode
from sqlalchemy import func
import traceback

org_admin_bp = Blueprint('org_admin', __name__)

@org_admin_bp.route('/dashboard')
@login_required
@org_admin_required
def dashboard():
    # Get statistics
    total_jobs = Job.query.filter_by(organization_id=current_user.organization_id).count()
    total_applications = Application.query.join(Job).filter(
        Job.organization_id == current_user.organization_id
    ).count()
    active_jobs = Job.query.filter_by(
        organization_id=current_user.organization_id,
        status='published'
    ).count()
    
    return render_template('org_admin/dashboard.html', 
                         total_jobs=total_jobs,
                         total_applications=total_applications,
                         active_jobs=active_jobs)

@org_admin_bp.route('/jobs')
@login_required
@org_admin_required
def jobs():
    # Get all jobs for this organization
    page = request.args.get('page', 1, type=int) or 1
    per_page = 20

    jobs_query = Job.query.filter_by(
        organization_id=current_user.organization_id
    ).order_by(Job.created_at.desc())

    jobs_pagination = jobs_query.paginate(page=page, per_page=per_page, error_out=False)
    jobs_list = jobs_pagination.items
    
    if jobs_pagination.pages and page > jobs_pagination.pages:
        return redirect(url_for('org_admin.jobs', page=jobs_pagination.pages))
    
    # Add application count for each job
    for job in jobs_list:
        job.application_count = job.applications.count()
    
    jobs_stats = {
        'start_index': ((jobs_pagination.page - 1) * jobs_pagination.per_page + 1) if jobs_pagination.total else 0,
        'end_index': min(jobs_pagination.page * jobs_pagination.per_page, jobs_pagination.total) if jobs_pagination.total else 0,
        'total': jobs_pagination.total
    }
    
    return render_template('org_admin/jobs.html', jobs=jobs_list, jobs_pagination=jobs_pagination, jobs_stats=jobs_stats)

@org_admin_bp.route('/jobs/new', methods=['GET', 'POST'])
@login_required
@org_admin_required
def new_job():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        # Generate slug from title
        base_slug = generate_slug(title)
        slug = base_slug
        counter = 1
        while Job.query.filter_by(public_url_slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create job
        job = Job(
            title=title,
            description_html=description,
            status='draft',
            organization_id=current_user.organization_id,
            public_url_slug=slug
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('Job created successfully', 'success')
        return redirect(url_for('org_admin.edit_job', job_id=job.id))
    
    return render_template('org_admin/new_job.html')

@org_admin_bp.route('/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
@login_required
@org_admin_required
def edit_job(job_id):
    job = Job.query.filter_by(
        id=job_id, 
        organization_id=current_user.organization_id
    ).first_or_404()
    
    if request.method == 'POST':
        job.title = request.form.get('title')
        job.description_html = request.form.get('description')
        status = request.form.get('status')
        
        if status and status in ['draft', 'published', 'ended']:
            job.status = status
            if status == 'published' and not job.published_at:
                job.published_at = datetime.utcnow()
        
        db.session.commit()
        flash('Job updated successfully', 'success')
        return redirect(url_for('org_admin.edit_job', job_id=job.id))
    
    questions = Question.query.filter_by(job_id=job.id).order_by(Question.order_index).all()
    return render_template('org_admin/edit_job.html', job=job, questions=questions)

@org_admin_bp.route('/jobs/<int:job_id>/add-question', methods=['POST'])
@login_required
@org_admin_required
def add_question(job_id):
    job = Job.query.filter_by(
        id=job_id, 
        organization_id=current_user.organization_id
    ).first_or_404()
    
    text = request.form.get('text')
    weightage = request.form.get('weightage', 10, type=int)
    
    # Get max order_index
    max_order = db.session.query(func.max(Question.order_index)).filter_by(job_id=job_id).scalar() or 0
    
    question = Question(
        text=text,
        weightage=weightage,
        job_id=job_id,
        is_ai_generated=False,
        order_index=max_order + 1
    )
    
    db.session.add(question)
    db.session.commit()
    
    flash('Question added successfully', 'success')
    return redirect(url_for('org_admin.edit_job', job_id=job_id))

@org_admin_bp.route('/jobs/<int:job_id>/generate-questions', methods=['POST'])
@login_required
@org_admin_required
def generate_questions(job_id):
    job = Job.query.filter_by(
        id=job_id, 
        organization_id=current_user.organization_id
    ).first_or_404()
    
    if not job.description_html:
        return jsonify({'error': 'Job description is required'}), 400
    
    try:
        # Generate questions using AI
        questions = generate_questions_from_description(job.description_html)
        
        # Get max order_index
        max_order = db.session.query(func.max(Question.order_index)).filter_by(job_id=job_id).scalar() or 0
        
        # Save questions
        for idx, q_data in enumerate(questions):
            question = Question(
                text=q_data['text'],
                weightage=q_data['weightage'],
                job_id=job_id,
                is_ai_generated=True,
                order_index=max_order + idx + 1
            )
            db.session.add(question)
        
        db.session.commit()
        
        return jsonify({'success': True, 'count': len(questions)})
    except Exception as e:
        print(f"Error in generate_questions route: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@org_admin_bp.route('/questions/<int:question_id>/edit', methods=['POST'])
@login_required
@org_admin_required
def edit_question(question_id):
    question = Question.query.join(Job).filter(
        Question.id == question_id,
        Job.organization_id == current_user.organization_id
    ).first_or_404()
    
    question.text = request.form.get('text')
    question.weightage = request.form.get('weightage', type=int)
    
    db.session.commit()
    
    return jsonify({'success': True})

@org_admin_bp.route('/questions/<int:question_id>/delete', methods=['POST'])
@login_required
@org_admin_required
def delete_question(question_id):
    question = Question.query.join(Job).filter(
        Question.id == question_id,
        Job.organization_id == current_user.organization_id
    ).first_or_404()
    
    job_id = question.job_id
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully', 'success')
    return redirect(url_for('org_admin.edit_job', job_id=job_id))

@org_admin_bp.route('/applications')
@login_required
@org_admin_required
def applications():
    # Get job_id filter from query parameters
    job_id = request.args.get('job_id', type=int)
    selected_job = None
    
    # Build query for applications
    query = Application.query.join(Job).join(Candidate).filter(
        Job.organization_id == current_user.organization_id
    )
    
    # Apply job filter if provided
    if job_id:
        query = query.filter(Application.job_id == job_id)
        selected_job = Job.query.filter_by(
            id=job_id,
            organization_id=current_user.organization_id
        ).first()
    
    applications_list = query.order_by(Application.created_at.desc()).all()

    # Compute score percentages and split into recommended / others
    recommended_applications = []
    other_applications = []
    
    for application in applications_list:
        if application.total_weightage and application.total_weightage > 0:
            percentage = (application.total_score / application.total_weightage) * 100
        else:
            percentage = 0.0
        
        application.score_percentage = percentage
        
        if percentage >= 70:
            recommended_applications.append(application)
        else:
            other_applications.append(application)
    
    # Sort lists (recommended by highest score, others by highest score)
    recommended_applications.sort(key=lambda app: app.score_percentage, reverse=True)
    other_applications.sort(key=lambda app: app.score_percentage, reverse=True)

    # Pagination settings
    per_page = 20
    rec_total = len(recommended_applications)
    other_total = len(other_applications)

    rec_page = request.args.get('rec_page', 1, type=int) or 1
    other_page = request.args.get('other_page', 1, type=int) or 1

    rec_pages = ceil(rec_total / per_page) if rec_total else 0
    other_pages = ceil(other_total / per_page) if other_total else 0

    if rec_pages and rec_page > rec_pages:
        rec_page = rec_pages
    if other_pages and other_page > other_pages:
        other_page = other_pages

    rec_page = max(rec_page, 1)
    other_page = max(other_page, 1)

    rec_start = (rec_page - 1) * per_page if rec_total else 0
    other_start = (other_page - 1) * per_page if other_total else 0

    recommended_page_items = recommended_applications[rec_start:rec_start + per_page]
    other_page_items = other_applications[other_start:other_start + per_page]

    def build_page_sequence(total_pages, current_page, edge=1, around=1):
        if total_pages <= 0:
            return []
        sequence = []
        last = 0
        for num in range(1, total_pages + 1):
            if num <= edge or num > total_pages - edge or abs(num - current_page) <= around:
                if last and last + 1 != num:
                    sequence.append(None)
                sequence.append(num)
                last = num
        return sequence

    recommended_pagination = {
        'page': rec_page,
        'pages': rec_pages,
        'has_prev': rec_page > 1 and rec_pages > 0,
        'has_next': rec_pages > 0 and rec_page < rec_pages,
        'prev_num': rec_page - 1,
        'next_num': rec_page + 1,
        'sequence': build_page_sequence(rec_pages, rec_page)
    }

    other_pagination = {
        'page': other_page,
        'pages': other_pages,
        'has_prev': other_page > 1 and other_pages > 0,
        'has_next': other_pages > 0 and other_page < other_pages,
        'prev_num': other_page - 1,
        'next_num': other_page + 1,
        'sequence': build_page_sequence(other_pages, other_page)
    }

    recommended_stats = {
        'start_index': rec_start + 1 if rec_total else 0,
        'end_index': min(rec_start + per_page, rec_total) if rec_total else 0,
        'total': rec_total
    }

    other_stats = {
        'start_index': other_start + 1 if other_total else 0,
        'end_index': min(other_start + per_page, other_total) if other_total else 0,
        'total': other_total
    }

    args_dict = request.args.to_dict()
    recommended_params = {k: v for k, v in args_dict.items() if k != 'rec_page'}
    other_params = {k: v for k, v in args_dict.items() if k != 'other_page'}
    
    def build_applications_link(base_params, **updates):
        merged = {}
        merged.update(base_params or {})
        for key, value in updates.items():
            if value is None:
                merged.pop(key, None)
            else:
                merged[key] = value
        clean_params = {k: str(v) for k, v in merged.items() if v not in (None, '')}
        query_string = urlencode(clean_params, doseq=True)
        base_url = url_for('org_admin.applications')
        return f"{base_url}?{query_string}" if query_string else base_url
    
    recommended_links = {
        'prev': build_applications_link(recommended_params, rec_page=recommended_pagination['prev_num']) if recommended_pagination['has_prev'] else None,
        'next': build_applications_link(recommended_params, rec_page=recommended_pagination['next_num']) if recommended_pagination['has_next'] else None,
        'pages': []
    }
    
    for num in recommended_pagination['sequence']:
        if num:
            recommended_links['pages'].append({
                'page': num,
                'url': build_applications_link(recommended_params, rec_page=num),
                'is_gap': False
            })
        else:
            recommended_links['pages'].append({'is_gap': True})
    
    other_links = {
        'prev': build_applications_link(other_params, other_page=other_pagination['prev_num']) if other_pagination['has_prev'] else None,
        'next': build_applications_link(other_params, other_page=other_pagination['next_num']) if other_pagination['has_next'] else None,
        'pages': []
    }
    
    for num in other_pagination['sequence']:
        if num:
            other_links['pages'].append({
                'page': num,
                'url': build_applications_link(other_params, other_page=num),
                'is_gap': False
            })
        else:
            other_links['pages'].append({'is_gap': True})
    
    # Get all jobs for filtering dropdown
    jobs_list = Job.query.filter_by(organization_id=current_user.organization_id).all()
    
    return render_template('org_admin/applications.html', 
                         recommended_applications=recommended_page_items,
                         recommended_pagination=recommended_pagination,
                         recommended_stats=recommended_stats,
                         recommended_links=recommended_links,
                         other_applications=other_page_items,
                         other_pagination=other_pagination,
                         other_stats=other_stats,
                         other_links=other_links,
                         jobs=jobs_list,
                         selected_job=selected_job,
                         job_id=job_id,
                         per_page=per_page)

@org_admin_bp.route('/applications/<int:application_id>')
@login_required
@org_admin_required
def view_application(application_id):
    application = Application.query.join(Job).filter(
        Application.id == application_id,
        Job.organization_id == current_user.organization_id
    ).first_or_404()
    
    # Get answers with questions
    answers = Answer.query.filter_by(application_id=application_id).all()
    
    return render_template('org_admin/view_application.html', 
                         application=application,
                         answers=answers)

@org_admin_bp.route('/applications/<int:application_id>/download-pdf')
@login_required
@org_admin_required
def download_application_pdf(application_id):
    application = Application.query.join(Job).filter(
        Application.id == application_id,
        Job.organization_id == current_user.organization_id
    ).first_or_404()
    
    from app.services.pdf_service import generate_application_pdf
    
    try:
        pdf_file = generate_application_pdf(application)
        return pdf_file
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('org_admin.view_application', application_id=application_id))

@org_admin_bp.route('/team', methods=['GET', 'POST'])
@login_required
@org_admin_required
def manage_team():
    if request.method == 'POST':
        first_name = (request.form.get('first_name') or '').strip()
        last_name = (request.form.get('last_name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()

        # Basic validation
        if not first_name or not last_name or not email:
            flash('First name, last name, and email are required.', 'danger')
            return redirect(url_for('org_admin.manage_team'))

        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            # If user exists and is active, show error
            if existing_user.is_active:
                flash('A user with this email already exists.', 'danger')
                return redirect(url_for('org_admin.manage_team'))
            
            # If user exists but is deactivated, reactivate them
            existing_user.first_name = first_name
            existing_user.last_name = last_name
            existing_user.is_active = True
            existing_user.must_change_password = True
            
            password = generate_password()
            existing_user.set_password(password)
            
            db.session.commit()
            
            try:
                send_user_invitation_email(existing_user, current_user.organization, password)
                flash('User reactivated and invited successfully.', 'success')
            except Exception as e:
                flash(f'User reactivated but failed to send email: {str(e)}', 'warning')
            
            return redirect(url_for('org_admin.manage_team'))

        # Create new user if doesn't exist
        password = generate_password()
        organization_id = current_user.organization_id

        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='org_admin',
            organization_id=organization_id,
            must_change_password=True,
            is_active=True
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        try:
            send_user_invitation_email(new_user, current_user.organization, password)
            flash('User invited successfully.', 'success')
        except Exception as e:
            flash(f'User created but failed to send email: {str(e)}', 'warning')

        return redirect(url_for('org_admin.manage_team'))

    team_members = User.query.filter(
        User.organization_id == current_user.organization_id,
        User.role == 'org_admin'
    ).order_by(User.created_at.asc()).all()

    return render_template('org_admin/team.html', team_members=team_members)

@org_admin_bp.route('/team/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@org_admin_required
def toggle_team_member_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # Verify the user belongs to the same organization
    if user.organization_id != current_user.organization_id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('org_admin.manage_team'))
    
    # Prevent deactivating yourself
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('org_admin.manage_team'))
    
    # Toggle status
    user.is_active = not user.is_active
    db.session.commit()
    
    status_text = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.email} has been {status_text}.', 'success')
    return redirect(url_for('org_admin.manage_team'))

@org_admin_bp.route('/team/<int:user_id>/edit', methods=['POST'])
@login_required
@org_admin_required
def edit_team_member(user_id):
    user = User.query.get_or_404(user_id)
    
    # Verify the user belongs to the same organization
    if user.organization_id != current_user.organization_id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('org_admin.manage_team'))
    
    first_name = (request.form.get('first_name') or '').strip()
    last_name = (request.form.get('last_name') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    
    # Basic validation
    if not first_name or not last_name or not email:
        flash('First name, last name, and email are required.', 'danger')
        return redirect(url_for('org_admin.manage_team'))
    
    # Check if email is being changed and if new email already exists (and is active)
    if email != user.email:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.is_active:
            flash('A user with this email already exists.', 'danger')
            return redirect(url_for('org_admin.manage_team'))
        user.email = email
    
    user.first_name = first_name
    user.last_name = last_name
    
    db.session.commit()
    flash(f'User {user.email} has been updated.', 'success')
    return redirect(url_for('org_admin.manage_team'))

@org_admin_bp.route('/applications/<int:application_id>/update-status', methods=['POST'])
@login_required
@org_admin_required
def update_application_status(application_id):
    application = Application.query.join(Job).filter(
        Application.id == application_id,
        Job.organization_id == current_user.organization_id
    ).first_or_404()
    
    new_status = request.form.get('status')
    
    # Validate status
    valid_statuses = ['pending', 'in_progress', 'completed', 'shortlisted', 'rejected']
    if new_status not in valid_statuses:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Invalid status'}), 400
        flash('Invalid status selected', 'danger')
        return redirect(url_for('org_admin.view_application', application_id=application_id))
    
    application.status = new_status
    db.session.commit()
    
    # Handle AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'status': new_status})
    
    # Handle regular form submission
    status_labels = {
        'pending': 'Pending',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'shortlisted': 'Short Listed',
        'rejected': 'Rejected'
    }
    flash(f'Application status updated to {status_labels.get(new_status, new_status)}', 'success')
    return redirect(url_for('org_admin.view_application', application_id=application_id))

@org_admin_bp.route('/applications/<int:application_id>/send-pdf-email', methods=['POST'])
@login_required
@org_admin_required
def send_application_pdf_email(application_id):
    application = Application.query.join(Job).filter(
        Application.id == application_id,
        Job.organization_id == current_user.organization_id
    ).first_or_404()
    
    # Get email address from request
    to_email = request.form.get('email', '').strip()
    
    # Validate email
    if not to_email:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Email address is required'}), 400
        flash('Email address is required', 'danger')
        return redirect(url_for('org_admin.view_application', application_id=application_id))
    
    # Basic email validation
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, to_email):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Invalid email address format'}), 400
        flash('Invalid email address format', 'danger')
        return redirect(url_for('org_admin.view_application', application_id=application_id))
    
    try:
        # Generate PDF buffer
        from app.services.pdf_service import generate_application_pdf_buffer
        from app.services.email_service import send_application_pdf_email as send_pdf_email
        
        pdf_buffer = generate_application_pdf_buffer(application)
        
        # Send email with PDF attachment
        send_pdf_email(to_email, application, pdf_buffer)
        
        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': f'PDF sent successfully to {to_email}'})
        
        flash(f'Application PDF sent successfully to {to_email}', 'success')
        return redirect(url_for('org_admin.view_application', application_id=application_id))
        
    except Exception as e:
        print(f"Error sending PDF email: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': f'Failed to send email: {str(e)}'}), 500
        
        flash(f'Failed to send email: {str(e)}', 'danger')
        return redirect(url_for('org_admin.view_application', application_id=application_id))

