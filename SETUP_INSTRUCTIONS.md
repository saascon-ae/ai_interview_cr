# Setup Instructions - Configured for Your Environment

## ✅ What's Already Configured

Your database and email settings have been prepared based on your credentials:

- **PostgreSQL**: localhost (127.0.0.1:5432)
- **Database User**: muhammadkhurram
- **SMTP Server**: mail.saascon.ae (Port 465 with SSL)
- **Email**: connect@saascon.ae

## 🔑 What You Need to Add

**OpenAI API Key** - This is required for the AI features to work.

### How to Get Your OpenAI API Key:

1. Visit: https://platform.openai.com/api-keys
2. Sign in (or create a free account)
3. Click **"Create new secret key"**
4. Name it something like "HR Interview Platform"
5. **Copy the key** (starts with `sk-proj-...` or `sk-...`)
6. ⚠️ **Save it immediately** - you won't be able to see it again!

### Important Notes About OpenAI:
- You need to add billing information (credit card) to use the API
- The API is pay-as-you-go (typically $0.01-0.03 per interview)
- You can set monthly spending limits in your OpenAI dashboard
- Free tier: $5 in credits for new accounts (expires after 3 months)

## 📝 Step-by-Step Setup

### Step 1: Create .env File

```bash
cd /Users/muhammadkhurram/mvp/cursorproj/intverview_v_cursor
cp .env.example .env
```

Or create `.env` manually and paste this content:

```env
# Flask Secret Key
SECRET_KEY=hr-interview-platform-secret-key-2024

# PostgreSQL Database - YOUR SETTINGS
DATABASE_URL=postgresql://muhammadkhurram:admin123@127.0.0.1:5432/interview_db

# OpenAI API - ADD YOUR KEY HERE
OPENAI_API_KEY=sk-YOUR-ACTUAL-KEY-HERE

# SMTP Email - YOUR SETTINGS
SMTP_HOST=mail.saascon.ae
SMTP_PORT=465
SMTP_USE_TLS=False
SMTP_USER=connect@saascon.ae
SMTP_PASSWORD=2014$Khur
SMTP_FROM_EMAIL=connect@saascon.ae
SMTP_FROM_NAME=HR Interview Platform

# File Storage
UPLOAD_FOLDER=./app/static/uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=pdf,doc,docx

# Application
APP_URL=http://localhost:5005
DEBUG=True
```

**⚠️ IMPORTANT**: Replace `sk-YOUR-ACTUAL-KEY-HERE` with your real OpenAI API key!

### Step 2: Create PostgreSQL Database

Open Terminal and run:

```bash
createdb interview_db
```

Or using psql:

```bash
psql -U muhammadkhurram
CREATE DATABASE interview_db;
\q
```

### Step 3: Set Up Python Environment

```bash
# Navigate to project directory
cd /Users/muhammadkhurram/mvp/cursorproj/intverview_v_cursor

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
python init_db.py
```

This will:
- Create all database tables
- Create a default super admin user
- Set up the database schema

### Step 5: Start the Application

```bash
python run.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Running on http://localhost:5000
```

### Step 6: Access the Application

Open your browser and go to: **http://localhost:5000**

**Default Login:**
- Email: `admin@hrplatform.com`
- Password: `admin123`

**⚠️ Change this password immediately after first login!**

## 🎯 Quick Test Checklist

### Test Super Admin:
1. ✅ Log in at http://localhost:5000/auth/login
2. ✅ Create a test organization
3. ✅ Upload organization logo
4. ✅ Send invitation email (check if email arrives)

### Test Organization Admin:
1. ✅ Check email for invitation
2. ✅ Log in with provided credentials
3. ✅ Change password (forced on first login)
4. ✅ Create a job posting
5. ✅ Click "Auto-Generate Questions" (tests OpenAI API)
6. ✅ Publish the job

### Test Public Interface:
1. ✅ Visit job openings page
2. ✅ Apply for a job
3. ✅ Upload CV (tests OpenAI CV analysis)
4. ✅ Complete voice interview (tests OpenAI Whisper)

## 🔧 Troubleshooting

### Database Connection Issues

**Error**: "could not connect to server"
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL (macOS)
brew services start postgresql@14

# Check if database exists
psql -U muhammadkhurram -l
```

### SMTP Email Issues

**Port 465 with SSL** is configured for your mail server.

If emails don't send:
1. Check if port 465 is open: `telnet mail.saascon.ae 465`
2. Verify credentials are correct
3. Check spam folder
4. Look at application logs for error messages

**Test SMTP manually:**
```python
python3
>>> import smtplib
>>> from email.mime.text import MIMEText
>>> 
>>> msg = MIMEText("Test email")
>>> msg['Subject'] = 'Test'
>>> msg['From'] = 'connect@saascon.ae'
>>> msg['To'] = 'your-email@example.com'
>>> 
>>> server = smtplib.SMTP_SSL('mail.saascon.ae', 465)
>>> server.login('connect@saascon.ae', '2014$Khur')
>>> server.send_message(msg)
>>> server.quit()
>>> print("Email sent successfully!")
```

### OpenAI API Issues

**Error**: "Authentication failed"
- Verify your API key is correct in `.env`
- Check you've added billing info at https://platform.openai.com/account/billing

**Error**: "Rate limit exceeded"
- You've exceeded your monthly limit
- Increase limit in OpenAI dashboard

**Error**: "Insufficient quota"
- Add more credits to your OpenAI account

### Microphone Not Working in Interview

- Browser requires HTTPS for microphone in production
- For local testing, use `http://localhost:5000` (not `http://127.0.0.1:5000`)
- Check browser permissions (camera/microphone settings)

## 📊 Monitoring Your Usage

### OpenAI API Usage:
- Dashboard: https://platform.openai.com/usage
- Set spending limits: https://platform.openai.com/account/billing/limits

### Estimated Costs per Interview:
- Question Generation: ~$0.01-0.02
- CV Analysis: ~$0.01-0.02
- Voice Transcription: ~$0.006 per minute
- Answer Evaluation: ~$0.02-0.03
- Personality Profile: ~$0.01-0.02

**Total per interview**: Approximately $0.05-0.10

## 🚀 Going to Production

When you're ready to deploy:

1. **Change SECRET_KEY** to a strong random key:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Set DEBUG=False** in .env

3. **Use environment variables** instead of .env file on server

4. **Set up SSL/HTTPS** (required for microphone access)

5. **Configure proper firewall rules**

6. **Set up database backups**

7. **Monitor API usage and costs**

See `DEPLOYMENT.md` for detailed production deployment instructions.

## 📞 Need Help?

If you encounter any issues:

1. Check the logs in terminal where you ran `python run.py`
2. Review the troubleshooting section above
3. Check `README.md` for detailed documentation
4. Verify all credentials in `.env` are correct

## ✅ Success Indicators

You'll know everything is working when:
- ✅ Application starts without errors
- ✅ You can log in as super admin
- ✅ You can create organizations
- ✅ Invitation emails are received
- ✅ Auto-generate questions works (OpenAI)
- ✅ CV upload and analysis works
- ✅ Voice interview recording works
- ✅ You can download PDF reports

---

**Your platform is ready to revolutionize hiring! 🎉**

