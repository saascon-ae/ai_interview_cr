# AI-Powered HR Interview Platform

A comprehensive web application that automates the pre-screening interview process using AI. This platform helps HR admins from multiple organizations manage job postings, conduct voice-based interviews, and evaluate candidates intelligently.

## Features

- **Multi-Organization Support**: Super admin can manage multiple organizations
- **AI-Powered Question Generation**: Automatically generate relevant interview questions from job descriptions
- **CV Analysis**: AI analyzes candidate CVs and matches them with job requirements
- **Real-Time Voice Interviews**: Conduct pre-screening interviews through voice conversations
- **Personality Profiling**: Generate comprehensive candidate profiles based on CV, answers, and voice tone
- **Comprehensive Reporting**: Download detailed PDF reports for each candidate
- **REST API**: API endpoints for external integrations

## Technology Stack

- **Backend**: Python (Flask)
- **Database**: PostgreSQL
- **Real-time Communication**: Flask-SocketIO + WebSocket
- **AI**: OpenAI API (GPT-4, Whisper, TTS)
- **PDF Generation**: ReportLab
- **Email**: SMTP
- **Frontend**: HTML, CSS, JavaScript, Jinja2

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- OpenAI API key

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd intverview_v_cursor
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

Create a PostgreSQL database:

```bash
createdb interview_db
```

Or use psql:

```sql
CREATE DATABASE interview_db;
```

### 5. Configure Environment Variables

Copy the example environment file and update it with your credentials:

```bash
cp .env.example .env
```

Edit `.env` file:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/interview_db
OPENAI_API_KEY=your-openai-api-key

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-email-password
SMTP_FROM_EMAIL=noreply@yourapp.com
SMTP_FROM_NAME=HR Interview Platform

# File Storage
UPLOAD_FOLDER=./app/static/uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=pdf,doc,docx

# Application
APP_URL=http://localhost:5000
DEBUG=True
```

### 6. Initialize Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. Create Super Admin User

Open Python shell:

```bash
python
```

```python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User(
        email='admin@example.com',
        role='super_admin',
        is_active=True
    )
    admin.set_password('your-admin-password')
    db.session.add(admin)
    db.session.commit()
    print("Super admin created!")
```

## Running the Application

### Development Mode

```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Production Mode (with Gunicorn)

```bash
gunicorn -k eventlet -w 1 --bind 0.0.0.0:5000 wsgi:app
```

**Note**: Use only 1 worker (`-w 1`) with eventlet for WebSocket support.

## Application Structure

```
interview_platform/
├── app/
│   ├── __init__.py           # Application factory
│   ├── config.py             # Configuration
│   ├── models.py             # Database models
│   ├── routes/               # Route blueprints
│   │   ├── auth.py          # Authentication
│   │   ├── super_admin.py   # Super admin routes
│   │   ├── org_admin.py     # Organization admin routes
│   │   ├── public.py        # Public routes
│   │   └── api.py           # REST API
│   ├── services/             # Business logic
│   │   ├── ai_service.py    # OpenAI integration
│   │   ├── email_service.py # Email sending
│   │   ├── pdf_service.py   # PDF generation
│   │   └── voice_service.py # Audio processing
│   ├── sockets/              # WebSocket handlers
│   │   └── interview_socket.py
│   ├── templates/            # Jinja2 templates
│   ├── static/               # Static files
│   └── utils/                # Utility functions
├── migrations/               # Database migrations
├── requirements.txt
├── .env.example
├── run.py                    # Development server
└── wsgi.py                   # Production WSGI entry
```

## User Roles

### Super Admin
- Manage organizations
- Add/edit/delete organizations
- Send invitation emails to organization admins
- Activate/deactivate organizations

### Organization Admin
- Manage job postings
- Create/edit/delete jobs
- Generate AI questions
- View applications
- Download candidate reports

### Public (Candidates)
- View job openings
- Submit applications
- Participate in voice interviews

## API Endpoints

The platform provides REST API endpoints for external integrations:

### Authentication
All API requests require an API key in the header:
```
X-API-Key: your-api-key
```

### Available Endpoints

- `GET /api/v1/organizations` - List all organizations
- `GET /api/v1/organizations/<org_id>/jobs` - List jobs for an organization
- `POST /api/v1/jobs` - Create a new job
- `GET /api/v1/jobs/<job_id>/applications` - List applications for a job
- `GET /api/v1/candidates/<candidate_id>` - Get candidate details
- `POST /api/v1/applications` - Submit application (no API key required)

## Deployment

### Shared Hosting (cPanel)

1. Upload files to your hosting directory
2. Set up PostgreSQL database via cPanel
3. Configure `.env` file
4. Set up Python application in cPanel
5. Point to `wsgi.py` as the WSGI entry point

### AWS Deployment

1. Set up EC2 instance
2. Configure RDS for PostgreSQL
3. Set up Application Load Balancer
4. Configure environment variables
5. Run with Gunicorn + Nginx

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

### WebSocket Connection Issues
- Check if port 5000 is accessible
- Verify Flask-SocketIO is properly installed
- Use eventlet worker for production

### OpenAI API Errors
- Verify API key is correct
- Check API quota and billing
- Ensure network connectivity

### Audio Recording Issues
- Browser must support Web Audio API
- HTTPS required for microphone access in production
- Check browser permissions

## Security Considerations

- Change SECRET_KEY in production
- Use HTTPS in production
- Secure database credentials
- Implement rate limiting for API
- Validate all file uploads
- Sanitize user inputs

## Support

For issues or questions, please contact the development team.

## License

Proprietary - All rights reserved

