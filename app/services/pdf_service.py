from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from flask import make_response, current_app
from io import BytesIO
import os
import PyPDF2

def generate_application_pdf_buffer(application):
    """Generate PDF buffer for application (for email attachments)"""
    buffer = BytesIO()
    
    # Create the PDF object
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2196F3'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#4CAF50'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph(f"Application Report - {application.job.title}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Candidate Information
    candidate = application.candidate
    elements.append(Paragraph("Candidate Information", heading_style))
    
    candidate_data = [
        ['Candidate Name:', f"{candidate.first_name} {candidate.last_name}"],
        ['Email:', candidate.email],
        ['Phone:', candidate.phone or 'N/A'],
        ['Job Title:', application.job.title],
        ['Total Score:', f"{application.total_score:.1f} / {application.total_weightage}"],
        ['Score Percentage:', f"{(application.total_score/application.total_weightage*100):.1f}%" if application.total_weightage > 0 else 'N/A'],
        ['CV Matching:', f"{candidate.matching_percentage:.1f}%" if candidate.matching_percentage else 'N/A'],
        ['Status:', application.status.capitalize()],
    ]
    
    candidate_table = Table(candidate_data, colWidths=[2*inch, 4*inch])
    candidate_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    elements.append(candidate_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # CV Summary
    if candidate.cv_summary:
        elements.append(Paragraph("CV Summary", heading_style))
        cv_para = Paragraph(candidate.cv_summary, styles['BodyText'])
        elements.append(cv_para)
        elements.append(Spacer(1, 0.2*inch))
    
    # Personality Profile
    if application.personality_profile:
        elements.append(Paragraph("Personality Profile", heading_style))
        personality_para = Paragraph(application.personality_profile, styles['BodyText'])
        elements.append(personality_para)
        elements.append(Spacer(1, 0.2*inch))
    
    # Interview Q&A
    elements.append(PageBreak())
    elements.append(Paragraph("Interview Q&A", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    answers = application.answers.all()
    for idx, answer in enumerate(answers, 1):
        # Question
        q_text = f"<b>Question {idx}:</b> {answer.question.text}"
        elements.append(Paragraph(q_text, styles['BodyText']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Answer
        a_text = f"<b>Answer:</b> {answer.answer_text or 'No answer provided'}"
        elements.append(Paragraph(a_text, styles['BodyText']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Score
        score_text = f"<b>Score:</b> {answer.score:.1f} / {answer.weightage} ({(answer.score/answer.weightage*100):.1f}%)" if answer.weightage > 0 else f"<b>Score:</b> {answer.score:.1f}"
        elements.append(Paragraph(score_text, styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Build PDF
    doc.build(elements)
    
    # Get the PDF data
    buffer.seek(0)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Merge CV if available
    if candidate.cv_path:
        try:
            # Get full path to CV file
            cv_full_path = os.path.join(current_app.root_path, 'static', candidate.cv_path)
            
            # Check if CV file exists and is a PDF
            if os.path.exists(cv_full_path) and candidate.cv_path.lower().endswith('.pdf'):
                # Create PDF merger
                merger = PyPDF2.PdfMerger()
                
                # Add the report PDF
                report_pdf = BytesIO(pdf_data)
                merger.append(report_pdf)
                
                # Create a separator page with "Candidate CV" heading
                cv_header_buffer = BytesIO()
                cv_header_doc = SimpleDocTemplate(cv_header_buffer, pagesize=letter,
                                                 rightMargin=72, leftMargin=72,
                                                 topMargin=72, bottomMargin=18)
                cv_header_elements = []
                cv_header_elements.append(Paragraph("Candidate CV", heading_style))
                cv_header_elements.append(Spacer(1, 0.3*inch))
                cv_header_doc.build(cv_header_elements)
                cv_header_pdf_data = cv_header_buffer.getvalue()
                cv_header_buffer.close()
                
                # Add the CV header page (will start on new page naturally)
                cv_header_pdf = BytesIO(cv_header_pdf_data)
                merger.append(cv_header_pdf)
                
                # Add the CV PDF
                with open(cv_full_path, 'rb') as cv_file:
                    merger.append(cv_file)
                
                # Create new buffer with merged PDF
                merged_buffer = BytesIO()
                merger.write(merged_buffer)
                merged_buffer.seek(0)
                
                # Close merger and return merged buffer
                merger.close()
                report_pdf.close()
                cv_header_pdf.close()
                
                return merged_buffer
                
        except Exception as e:
            print(f"Error merging CV PDF: {e}")
            # Continue with report PDF only if CV merge fails
    
    # Return report PDF buffer (without CV if merge failed or CV not available)
    return BytesIO(pdf_data)

def generate_application_pdf(application):
    """Generate PDF report for application"""
    buffer = BytesIO()
    
    # Create the PDF object
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2196F3'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#4CAF50'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph(f"Application Report - {application.job.title}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Candidate Information
    candidate = application.candidate
    elements.append(Paragraph("Candidate Information", heading_style))
    
    candidate_data = [
        ['Name:', f"{candidate.first_name} {candidate.last_name}"],
        ['Email:', candidate.email],
        ['Phone:', candidate.phone or 'N/A'],
        ['Application Date:', application.created_at.strftime('%d-%m-%Y') if application.created_at else 'N/A'],
        ['Matching Percentage:', f"{candidate.matching_percentage:.1f}%" if candidate.matching_percentage else 'N/A'],
        ['Submitted IP Address:', application.ip_address or 'N/A'],
        ['Candidate Local Time:', application.local_time or 'N/A'],
        ['Candidate Timezone:', application.timezone or 'N/A']
    ]
    
    candidate_table = Table(candidate_data, colWidths=[2*inch, 4*inch])
    candidate_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(candidate_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # CV Summary
    if candidate.cv_summary:
        elements.append(Paragraph("CV Summary", heading_style))
        cv_summary_text = Paragraph(candidate.cv_summary, styles['BodyText'])
        elements.append(cv_summary_text)
        elements.append(Spacer(1, 0.3*inch))
    
    # Interview Results
    elements.append(Paragraph("Interview Results", heading_style))
    
    score_data = [
        ['Total Score:', f"{application.total_score:.1f}"],
        ['Total Weightage:', str(application.total_weightage)],
        ['Percentage:', f"{(application.total_score / application.total_weightage * 100) if application.total_weightage > 0 else 0:.1f}%"],
        ['Status:', application.status.capitalize()]
    ]
    
    score_table = Table(score_data, colWidths=[2*inch, 4*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Questions and Answers
    elements.append(Paragraph("Interview Questions & Answers", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    answers = application.answers.all()
    for idx, answer in enumerate(answers, 1):
        # Question
        question_text = f"<b>Question {idx}:</b> {answer.question.text}"
        elements.append(Paragraph(question_text, styles['BodyText']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Answer
        answer_text = f"<b>Answer:</b> {answer.answer_text or 'No answer provided'}"
        elements.append(Paragraph(answer_text, styles['BodyText']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Score and Duration
        duration_text = ""
        if answer.duration:
            minutes = int(answer.duration // 60)
            seconds = int(answer.duration % 60)
            duration_text = f" | <b>Duration:</b> {minutes}:{seconds:02d}"
        
        score_text = f"<b>Score:</b> {answer.score:.1f} / {answer.weightage}{duration_text}"
        elements.append(Paragraph(score_text, styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Personality Profile
    if application.personality_profile:
        elements.append(PageBreak())
        elements.append(Paragraph("Personality Profile", heading_style))
        profile_text = Paragraph(application.personality_profile, styles['BodyText'])
        elements.append(profile_text)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Merge CV if available
    if candidate.cv_path:
        try:
            # Get full path to CV file
            cv_full_path = os.path.join(current_app.root_path, 'static', candidate.cv_path)
            
            # Check if CV file exists and is a PDF
            if os.path.exists(cv_full_path) and candidate.cv_path.lower().endswith('.pdf'):
                # Create PDF merger
                merger = PyPDF2.PdfMerger()
                
                # Add the report PDF
                report_pdf = BytesIO(pdf_data)
                merger.append(report_pdf)
                
                # Create a separator page with "Candidate CV" heading
                cv_header_buffer = BytesIO()
                cv_header_doc = SimpleDocTemplate(cv_header_buffer, pagesize=letter,
                                                 rightMargin=72, leftMargin=72,
                                                 topMargin=72, bottomMargin=18)
                cv_header_elements = []
                cv_header_elements.append(Paragraph("Candidate CV", heading_style))
                cv_header_elements.append(Spacer(1, 0.3*inch))
                cv_header_doc.build(cv_header_elements)
                cv_header_pdf_data = cv_header_buffer.getvalue()
                cv_header_buffer.close()
                
                # Add the CV header page (will start on new page naturally)
                cv_header_pdf = BytesIO(cv_header_pdf_data)
                merger.append(cv_header_pdf)
                
                # Add the CV PDF
                with open(cv_full_path, 'rb') as cv_file:
                    merger.append(cv_file)
                
                # Create new buffer with merged PDF
                merged_buffer = BytesIO()
                merger.write(merged_buffer)
                merged_buffer.seek(0)
                pdf_data = merged_buffer.getvalue()
                merged_buffer.close()
                merger.close()
                
        except Exception as e:
            print(f"Error merging CV PDF: {e}")
            # Continue with report PDF only if CV merge fails
    
    # Generate filename from candidate name and job title
    candidate = application.candidate
    job_title = application.job.title
    
    # Sanitize filename: remove invalid characters and spaces
    candidate_name = f"{candidate.first_name}_{candidate.last_name}".replace(' ', '_')
    sanitized_job_title = job_title.replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    
    # Limit filename length to avoid issues
    filename = f"{candidate_name}_{sanitized_job_title}.pdf"
    if len(filename) > 200:  # Limit to reasonable length
        filename = f"{candidate_name}_{sanitized_job_title[:150]}.pdf"
    
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

