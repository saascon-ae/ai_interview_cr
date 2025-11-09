# Quick Start Guide

Get your AI-Powered HR Interview Platform up and running in minutes!

## Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ PostgreSQL 12 or higher installed and running
- ✅ OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- ✅ SMTP credentials for sending emails (Gmail, SendGrid, etc.)

## Quick Setup (5 minutes)

### Option 1: Using Setup Script (Recommended)

```bash
# 1. Navigate to project directory
cd intverview_v_cursor

# 2. Run the setup script
./setup.sh

# 3. Edit .env file with your credentials
nano .env  # or use your preferred editor

# 4. Initialize the database
python init_db.py

# 5. Start the application
python run.py
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create PostgreSQL database
createdb interview_db

# 4. Copy and configure environment file
cp .env.example .env
# Edit .env with your credentials

# 5. Initialize database
python init_db.py

# 6. Start the application
python run.py
```

## Access the Application

Once the server is running:

1. **Open your browser**: http://localhost:5000
2. **Login as Super Admin**:
   - Email: `admin@hrplatform.com`
   - Password: `admin123`
3. **⚠️ IMPORTANT**: Change the default password immediately!

## First Steps After Login

### As Super Admin:

1. **Add an Organization**
   - Click "Add Organization"
   - Fill in organization details
   - Upload logo (optional)
   - Click "Add Organization"

2. **Send Invitation to Organization Admin**
   - Find the organization in the list
   - Click "Send Invite"
   - The admin will receive an email with login credentials

### As Organization Admin:

1. **First Login**
   - Use credentials from invitation email
   - System will prompt you to change password
   - After changing password, log in again with new password

2. **Create a Job**
   - Navigate to "Jobs" in sidebar
   - Click "New Job"
   - Enter job title and description
   - Click "Create Job"

3. **Add Questions**
   - In the job edit page, scroll to "Interview Questions"
   - Option A: Click "Auto-Generate Questions" (AI will create questions)
   - Option B: Manually add questions using the form

4. **Publish the Job**
   - Change status to "Published"
   - Copy the public URL
   - Share with candidates

### For Candidates (Public):

1. **View Job Openings**
   - Visit: `http://localhost:5000/{organization-slug}/openings`
   - Browse available positions

2. **Apply for a Job**
   - Click "View Details & Apply"
   - Click "Apply Now"
   - Fill in personal information
   - Upload CV (PDF, DOC, or DOCX)
   - Click "Submit & Start Interview"

3. **Complete Voice Interview**
   - Allow microphone access when prompted
   - Listen to AI questions
   - Click "Start Recording" to answer
   - Speak your response
   - Click "Stop & Submit Answer"
   - Repeat for all questions

4. **Interview Complete**
   - Review completion message
   - Wait for HR team to contact you

## Environment Configuration

### Minimum Required Configuration (.env)

```env
# Database
DATABASE_URL=postgresql://username:password@localhost/interview_db

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here

# SMTP (Example with Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourcompany.com
```

### Getting SMTP Credentials

#### Option 1: Gmail
1. Enable 2-Factor Authentication on your Google account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password in SMTP_PASSWORD

#### Option 2: SendGrid
1. Sign up at [SendGrid](https://sendgrid.com/)
2. Create an API key
3. Use SMTP settings from SendGrid dashboard

#### Option 3: AWS SES
1. Set up AWS SES
2. Verify your email domain
3. Use SMTP credentials from SES console

## Testing the Application

### Test Super Admin Features
- ✅ Login as super admin
- ✅ Create organization
- ✅ Send invitation email
- ✅ Activate/deactivate organization

### Test Organization Admin Features
- ✅ Login as org admin
- ✅ Create job posting
- ✅ Generate AI questions
- ✅ Add manual questions
- ✅ Publish job
- ✅ View applications

### Test Public Features
- ✅ View job openings
- ✅ Submit application
- ✅ Upload CV
- ✅ Complete voice interview
- ✅ View completion page

### Test API Endpoints
```bash
# Set API key (use a strong key in production)
API_KEY="demo-api-key-change-me"

# List organizations
curl -H "X-API-Key: $API_KEY" http://localhost:5000/api/v1/organizations

# List jobs for organization
curl -H "X-API-Key: $API_KEY" http://localhost:5000/api/v1/organizations/1/jobs
```

## Common Issues and Solutions

### Issue: Database connection failed
**Solution**: 
- Ensure PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in .env file
- Check database exists: `psql -l`

### Issue: OpenAI API errors
**Solution**:
- Verify API key is correct
- Check API quota at [OpenAI Dashboard](https://platform.openai.com/usage)
- Ensure you have billing set up

### Issue: Microphone not working
**Solution**:
- For local testing, access via http://localhost:5000 (not 127.0.0.1)
- For production, HTTPS is required for microphone access
- Check browser permissions

### Issue: Email not sending
**Solution**:
- Verify SMTP credentials
- Check if SMTP port (587) is not blocked by firewall
- For Gmail, ensure "Less secure app access" is enabled OR use App Password

### Issue: WebSocket connection failed
**Solution**:
- Ensure Flask-SocketIO is installed
- Check browser console for errors
- Verify no firewall is blocking WebSocket connections

## Next Steps

1. **Customize Branding**
   - Update organization logos
   - Modify email templates in `app/services/email_service.py`

2. **Configure Production**
   - Set up proper database backups
   - Configure SSL certificate
   - Set up monitoring and logging

3. **Integrate with External Systems**
   - Use API endpoints to integrate with your ATS
   - Set up webhooks for real-time updates

4. **Scale Your Infrastructure**
   - Follow DEPLOYMENT.md for production setup
   - Consider AWS/cloud hosting for better scalability

## Support

For detailed information:
- 📖 Full Documentation: See README.md
- 🚀 Deployment Guide: See DEPLOYMENT.md
- 💻 API Documentation: See API section in README.md

## Security Checklist

Before going to production:
- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Configure firewall rules
- [ ] Enable database backups
- [ ] Set up monitoring and alerts

---

**Ready to revolutionize your hiring process? Start now! 🚀**

