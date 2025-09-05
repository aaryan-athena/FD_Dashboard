# Deployment Guide for Fall Detection Dashboard

## Local Development

### Prerequisites
- Python 3.8+
- Virtual environment (already created as `fddenv`)
- Firebase project with Realtime Database and Storage

### Quick Start
1. Update `.env` file with your Firebase credentials
2. Run: `python run.py`
3. Open: http://localhost:5000

## Production Deployment

### Option 1: Heroku Deployment

1. **Install Heroku CLI**
2. **Create requirements.txt**:
```bash
pip freeze > requirements.txt
```

3. **Create Procfile**:
```
web: gunicorn run:app
```

4. **Add gunicorn to requirements.txt**:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

5. **Deploy**:
```bash
heroku create your-app-name
heroku config:set FIREBASE_PROJECT_ID=your-project-id
heroku config:set FIREBASE_PRIVATE_KEY="your-private-key"
heroku config:set FIREBASE_CLIENT_EMAIL=your-client-email
# ... set other environment variables
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

### Option 2: AWS EC2 Deployment

1. **Launch EC2 instance** (Ubuntu 20.04)

2. **Install dependencies**:
```bash
sudo apt update
sudo apt install python3 python3-pip nginx
sudo pip3 install virtualenv
```

3. **Setup application**:
```bash
git clone your-repo
cd FD_Dashboard
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Setup Nginx**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

5. **Setup systemd service**:
```ini
[Unit]
Description=Fall Detection Dashboard
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/FD_Dashboard
Environment=PATH=/home/ubuntu/FD_Dashboard/venv/bin
ExecStart=/home/ubuntu/FD_Dashboard/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Option 3: Docker Deployment

1. **Create Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

2. **Create docker-compose.yml**:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
      - FIREBASE_PRIVATE_KEY=${FIREBASE_PRIVATE_KEY}
      - FIREBASE_CLIENT_EMAIL=${FIREBASE_CLIENT_EMAIL}
    volumes:
      - .:/app
```

3. **Deploy**:
```bash
docker-compose up -d
```

## Environment Variables for Production

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/
FIREBASE_STORAGE_BUCKET=your-project.appspot.com

# Flask Configuration
FLASK_SECRET_KEY=your-very-secure-secret-key
FLASK_DEBUG=False
```

## Security Considerations

### Firebase Security Rules

**Realtime Database Rules**:
```json
{
  "rules": {
    "falls": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```

**Storage Rules**:
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /videos/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null;
    }
  }
}
```

### Application Security

1. **Use HTTPS in production**
2. **Implement authentication**
3. **Validate all inputs**
4. **Use environment variables for secrets**
5. **Regular security updates**

## Monitoring and Logging

### Application Monitoring
```python
import logging
from flask import Flask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

app = Flask(__name__)

# Add request logging
@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())
```

### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

## Performance Optimization

### Caching
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/stats')
@cache.cached(timeout=300)  # Cache for 5 minutes
def api_stats():
    # Your stats logic
    pass
```

### Database Optimization
- Use Firebase Database indexing
- Implement pagination for large datasets
- Cache frequently accessed data

## Backup and Recovery

### Database Backup
```bash
# Export Firebase data
firebase database:get / > backup.json

# Import Firebase data
firebase database:set / backup.json
```

### Code Backup
- Use Git for version control
- Regular automated backups
- Documentation of deployment process

## Troubleshooting

### Common Issues

1. **Firebase Connection Failed**
   - Check environment variables
   - Verify service account permissions
   - Ensure Firebase services are enabled

2. **Video Playback Issues**
   - Check Firebase Storage rules
   - Verify video file formats
   - Check signed URL expiration

3. **Performance Issues**
   - Implement caching
   - Optimize database queries
   - Use CDN for static assets

### Debug Mode
```python
# Enable debug mode for development
app.run(debug=True)

# Disable for production
app.run(debug=False)
```
