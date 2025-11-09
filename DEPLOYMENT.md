# Deployment Guide

## Local Development Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Initialize Database**
   ```bash
   python init_db.py
   ```

4. **Run Development Server**
   ```bash
   python run.py
   ```

5. **Access Application**
   - Main app: http://localhost:5000
   - Login: http://localhost:5000/auth/login
   - Default credentials: admin@hrplatform.com / admin123

## Shared Hosting Deployment (cPanel)

### Prerequisites
- cPanel account with Python support
- PostgreSQL database access
- SSH access (optional but recommended)

### Steps

1. **Create PostgreSQL Database**
   - Log in to cPanel
   - Go to PostgreSQL Databases
   - Create a new database (e.g., `interview_db`)
   - Create a database user and grant all privileges

2. **Upload Files**
   - Upload all project files via FTP or File Manager
   - Recommended location: `/home/username/interview_platform/`

3. **Set Up Python Application**
   - In cPanel, go to "Setup Python App"
   - Python version: 3.8 or higher
   - Application root: `/home/username/interview_platform`
   - Application URL: Your desired URL
   - Application startup file: `wsgi.py`
   - Application Entry point: `app`

4. **Install Dependencies**
   - Enter the Python app's virtual environment:
     ```bash
     source /home/username/virtualenv/interview_platform/3.X/bin/activate
     cd /home/username/interview_platform
     pip install -r requirements.txt
     ```

5. **Configure Environment**
   - Create `.env` file with production settings:
     ```env
     SECRET_KEY=generate-a-strong-random-key
     DATABASE_URL=postgresql://dbuser:dbpass@localhost/interview_db
     OPENAI_API_KEY=your-openai-key
     SMTP_HOST=smtp.yourdomain.com
     SMTP_PORT=587
     SMTP_USE_TLS=True
     SMTP_USER=noreply@yourdomain.com
     SMTP_PASSWORD=your-smtp-password
     SMTP_FROM_EMAIL=noreply@yourdomain.com
     APP_URL=https://yourdomain.com
     DEBUG=False
     ```

6. **Initialize Database**
   ```bash
   python init_db.py
   ```

7. **Set File Permissions**
   ```bash
   chmod 755 -R app/static/uploads
   ```

8. **Restart Application**
   - In cPanel Python App interface, click "Restart"

### Important Notes for Shared Hosting

- **WebSocket Support**: Check if your hosting provider supports WebSockets. If not, the real-time interview feature may not work properly.
- **Memory Limits**: AI operations require sufficient memory. Ensure your hosting plan has adequate resources.
- **File Upload Limits**: Configure `MAX_UPLOAD_SIZE` based on your hosting limits.
- **HTTPS**: SSL certificate is required for microphone access in browsers.

## AWS Deployment

### Architecture
- EC2 for application server
- RDS for PostgreSQL database
- S3 for file storage (optional)
- Application Load Balancer
- Route 53 for DNS

### Steps

1. **Launch EC2 Instance**
   ```bash
   # Ubuntu 20.04 LTS or later
   # t2.medium or larger recommended
   ```

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx postgresql-client
   ```

3. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd interview_platform
   ```

4. **Set Up Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

5. **Configure Environment**
   - Create `.env` file with RDS connection details

6. **Set Up Gunicorn Service**
   Create `/etc/systemd/system/interview-platform.service`:
   ```ini
   [Unit]
   Description=HR Interview Platform
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/interview_platform
   Environment="PATH=/home/ubuntu/interview_platform/venv/bin"
   ExecStart=/home/ubuntu/interview_platform/venv/bin/gunicorn -k eventlet -w 1 --bind 127.0.0.1:5000 wsgi:app

   [Install]
   WantedBy=multi-user.target
   ```

7. **Configure Nginx**
   Create `/etc/nginx/sites-available/interview-platform`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /socket.io {
           proxy_pass http://127.0.0.1:5000/socket.io;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }

       location /static {
           alias /home/ubuntu/interview_platform/app/static;
           expires 30d;
       }
   }
   ```

8. **Enable and Start Services**
   ```bash
   sudo systemctl enable interview-platform
   sudo systemctl start interview-platform
   sudo systemctl enable nginx
   sudo systemctl restart nginx
   ```

9. **Set Up SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

10. **Initialize Database**
    ```bash
    source venv/bin/activate
    python init_db.py
    ```

## Environment Variables Reference

### Required
- `SECRET_KEY`: Flask secret key (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: Your OpenAI API key

### SMTP Configuration
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP port (usually 587 for TLS)
- `SMTP_USE_TLS`: Enable TLS (True/False)
- `SMTP_USER`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `SMTP_FROM_EMAIL`: From email address
- `SMTP_FROM_NAME`: From name

### Application Settings
- `APP_URL`: Full URL of your application
- `DEBUG`: Debug mode (True/False)
- `UPLOAD_FOLDER`: Path for file uploads
- `MAX_UPLOAD_SIZE`: Maximum file size in bytes
- `ALLOWED_EXTENSIONS`: Comma-separated list of allowed file extensions

## Post-Deployment Checklist

- [ ] Change default super admin password
- [ ] Configure SMTP settings
- [ ] Test email sending
- [ ] Test file uploads
- [ ] Test WebSocket connections
- [ ] Set up database backups
- [ ] Configure monitoring
- [ ] Set up error logging
- [ ] Test all user roles
- [ ] Test API endpoints
- [ ] Verify SSL certificate
- [ ] Configure firewall rules
- [ ] Set up CDN (optional)

## Troubleshooting

### WebSocket Not Connecting
- Check if hosting supports WebSockets
- Verify nginx configuration includes WebSocket upgrade headers
- Check firewall rules allow WebSocket traffic

### Database Connection Failed
- Verify DATABASE_URL is correct
- Check database server is accessible
- Verify credentials are correct

### File Upload Issues
- Check upload directory permissions (755 or 777)
- Verify MAX_UPLOAD_SIZE is appropriate
- Check disk space

### Email Not Sending
- Verify SMTP credentials
- Check if SMTP port is accessible
- Review firewall rules for outbound SMTP

## Monitoring and Maintenance

### Log Files
- Application logs: Check system logs or configure logging
- Nginx access logs: `/var/log/nginx/access.log`
- Nginx error logs: `/var/log/nginx/error.log`

### Database Backups
```bash
# Backup
pg_dump interview_db > backup_$(date +%Y%m%d).sql

# Restore
psql interview_db < backup_YYYYMMDD.sql
```

### Update Application
```bash
cd /path/to/interview_platform
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart interview-platform
```

