import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from flask import current_app, render_template
from jinja2 import Template

def send_email(to_email, subject, html_content):
    """Send email using SMTP"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{current_app.config['SMTP_FROM_NAME']} <{current_app.config['SMTP_FROM_EMAIL']}>"
        msg['To'] = to_email
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server
        smtp_host = current_app.config['SMTP_HOST']
        smtp_port = current_app.config['SMTP_PORT']
        smtp_user = current_app.config['SMTP_USER']
        smtp_password = current_app.config['SMTP_PASSWORD']
        use_tls = current_app.config['SMTP_USE_TLS']
        use_ssl = current_app.config.get('SMTP_USE_SSL', False)
        
        if use_ssl:
            # Port 465 with SSL
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        elif use_tls:
            # Port 587 with STARTTLS
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
        else:
            # Plain SMTP (not recommended)
            server = smtplib.SMTP(smtp_host, smtp_port)
        
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

def send_invitation_email(organization, password):
    """Send invitation email to organization admin"""
    app_url = current_app.config['APP_URL']
    login_url = f"{app_url}/auth/login"
    
    subject = f"Invitation to HR Interview Platform - {organization.name}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .credentials {{ background-color: #fff; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }}
            .button {{ display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to HR Interview Platform</h1>
            </div>
            <div class="content">
                <p>Dear {organization.first_name} {organization.last_name},</p>
                
                <p>You have been invited to join the HR Interview Platform for <strong>{organization.name}</strong>.</p>
                
                <p>Your account has been created. Please use the following credentials to log in:</p>
                
                <div class="credentials">
                    <p><strong>Email:</strong> {organization.email}</p>
                    <p><strong>Temporary Password:</strong> {password}</p>
                </div>
                
                <p><strong>Important:</strong> For security reasons, you will be required to change your password upon first login.</p>
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{login_url}" class="button">Login to Your Account</a>
                </p>
                
                <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                
                <p>Best regards,<br>HR Interview Platform Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(organization.email, subject, html_content)

def send_application_confirmation(candidate, job, organization):
    """Send confirmation email to candidate after application"""
    subject = f"Application Received - {job.title} at {organization.name}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Application Received</h1>
            </div>
            <div class="content">
                <p>Dear {candidate.first_name} {candidate.last_name},</p>
                
                <p>Thank you for applying for the position of <strong>{job.title}</strong> at {organization.name}.</p>
                
                <p>We have received your application and our team will review it shortly. If your qualifications match our requirements, we will contact you for the next steps.</p>
                
                <p>Best of luck!</p>
                
                <p>Best regards,<br>{organization.name} Hiring Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(candidate.email, subject, html_content)

def send_interview_completion_email(application):
    """Send thank you email to candidate after interview completion"""
    candidate = application.candidate
    job = application.job
    organization = job.organization if job else None
    
    if not candidate or not job or not organization:
        raise ValueError("Incomplete application data for interview completion email")
    
    subject = f"Thank You for Interviewing - {job.title} at {organization.name}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 24px; background-color: #f9f9f9; }}
            .header {{ text-align: center; margin-bottom: 24px; }}
            .card {{ background-color: #ffffff; padding: 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .footer {{ text-align: center; padding: 16px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Thank You for Your Time</h2>
            </div>
            <div class="card">
                <p>Hi {candidate.first_name} {candidate.last_name},</p>
                <p>Thank you for taking the time to complete the interview for the <strong>{job.title}</strong> role at <strong>{organization.name}</strong>.</p>
                <p>Our hiring team is reviewing your responses carefully. If your profile is shortlisted for the next steps, we’ll reach out to you with more details.</p>
                <p>We appreciate your interest in joining our team and wish you the best of luck!</p>
                <p style="margin-top: 24px;">Warm regards,<br>{organization.name} Hiring Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(candidate.email, subject, html_content)

def send_user_invitation_email(user, organization, password):
    """Send invitation email to a team member within an organization"""
    app_url = current_app.config['APP_URL']
    login_url = f"{app_url}/auth/login"

    full_name = ' '.join(filter(None, [user.first_name, user.last_name])).strip() or 'there'

    subject = f"You have been invited to {organization.name}'s HR Interview Platform"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .credentials {{ background-color: #fff; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }}
            .button {{ display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to {organization.name}</h1>
            </div>
            <div class="content">
                <p>Hi {full_name},</p>

                <p>You have been added to the HR Interview Platform for <strong>{organization.name}</strong>.</p>

                <p>Your account has been created with the following credentials:</p>

                <div class="credentials">
                    <p><strong>Email:</strong> {user.email}</p>
                    <p><strong>Temporary Password:</strong> {password}</p>
                </div>

                <p><strong>Important:</strong> For security reasons, you will be asked to set a new password the first time you log in.</p>

                <p style="text-align: center; margin: 30px 0;">
                    <a href="{login_url}" class="button">Log In</a>
                </p>

                <p>If you have any questions or need help, please reach out to your administrator.</p>

                <p>Welcome aboard!<br>{organization.name} Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_content)

def send_application_pdf_email(to_email, application, pdf_buffer):
    """Send application PDF to specified email address"""
    candidate = application.candidate
    job = application.job
    organization = job.organization if job else None
    
    if not candidate or not job or not organization:
        raise ValueError("Incomplete application data for PDF email")
    
    subject = f"Application Report - {candidate.first_name} {candidate.last_name} - {job.title}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 24px; background-color: #f9f9f9; }}
            .header {{ text-align: center; margin-bottom: 24px; }}
            .card {{ background-color: #ffffff; padding: 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .info-row {{ margin: 12px 0; padding: 12px; background-color: #f5f5f5; border-radius: 4px; }}
            .label {{ font-weight: 600; color: #666; }}
            .footer {{ text-align: center; padding: 16px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Application Report</h2>
            </div>
            <div class="card">
                <p>Please find attached the application report for:</p>
                
                <div class="info-row">
                    <span class="label">Candidate:</span> {candidate.first_name} {candidate.last_name}
                </div>
                <div class="info-row">
                    <span class="label">Position:</span> {job.title}
                </div>
                <div class="info-row">
                    <span class="label">Organization:</span> {organization.name}
                </div>
                
                <p style="margin-top: 24px;">The attached PDF contains the complete application details, interview responses, scores, and candidate profile.</p>
                
                <p style="margin-top: 24px;">Best regards,<br>{organization.name} HR Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message from the HR Interview Platform.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        # Create message with attachment
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = f"{current_app.config['SMTP_FROM_NAME']} <{current_app.config['SMTP_FROM_EMAIL']}>"
        msg['To'] = to_email
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Attach PDF
        pdf_buffer.seek(0)
        pdf_attachment = MIMEApplication(pdf_buffer.read(), _subtype='pdf')
        pdf_filename = f"Application_{candidate.first_name}_{candidate.last_name}_{job.title}.pdf".replace(' ', '_')
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
        msg.attach(pdf_attachment)
        
        # Connect to SMTP server
        smtp_host = current_app.config['SMTP_HOST']
        smtp_port = current_app.config['SMTP_PORT']
        smtp_user = current_app.config['SMTP_USER']
        smtp_password = current_app.config['SMTP_PASSWORD']
        use_tls = current_app.config['SMTP_USE_TLS']
        use_ssl = current_app.config.get('SMTP_USE_SSL', False)
        
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        elif use_tls:
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
        
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending PDF email: {e}")
        raise

