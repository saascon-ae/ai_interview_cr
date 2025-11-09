from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.utils.auth import generate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'super_admin':
            return redirect(url_for('super_admin.dashboard'))
        else:
            return redirect(url_for('org_admin.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=True)
            
            # Check if password change is required
            if user.must_change_password:
                return redirect(url_for('auth.change_password'))
            
            # Redirect based on role
            if user.role == 'super_admin':
                return redirect(url_for('super_admin.dashboard'))
            else:
                return redirect(url_for('org_admin.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('public/index.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('public.index'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if not current_user.must_change_password:
        return redirect(url_for('org_admin.dashboard' if current_user.role == 'org_admin' else 'super_admin.dashboard'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
        elif len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
        else:
            current_user.set_password(new_password)
            current_user.must_change_password = False
            db.session.commit()
            
            flash('Password changed successfully. Please log in with your new password.', 'success')
            logout_user()
            return redirect(url_for('auth.login'))
    
    return render_template('auth/change_password.html')

