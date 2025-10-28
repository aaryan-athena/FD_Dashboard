import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
import firebase_admin
from firebase_admin import credentials, db, storage
from dotenv import load_dotenv
import json
from collections import defaultdict, Counter

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback-secret-key')

# Add custom Jinja2 filters
@app.template_filter('format_datetime')
def format_datetime(timestamp):
    """Format datetime for display"""
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp

@app.template_filter('add_seconds')
def add_seconds(timestamp, seconds):
    """Add seconds to timestamp"""
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        return dt + timedelta(seconds=seconds)
    except:
        return timestamp

class FirebaseService:
    def __init__(self):
        self.mock_mode = False
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # First try to use service account file (most reliable)
            service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
            
            if os.path.exists(service_account_path):
                # Use service account file
                cred = credentials.Certificate(service_account_path)
                print(f"Using Firebase service account from: {service_account_path}")
            else:
                # Fall back to environment variables
                required_vars = ['FIREBASE_PROJECT_ID', 'FIREBASE_PRIVATE_KEY', 'FIREBASE_CLIENT_EMAIL']
                if all(os.getenv(var) for var in required_vars):
                    # Create credentials from environment variables
                    cred_dict = {
                        "type": "service_account",
                        "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                        "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                        "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                        "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                        "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
                        "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL'),
                        "universe_domain": "googleapis.com"
                    }
                    cred = credentials.Certificate(cred_dict)
                    print("Using Firebase credentials from environment variables")
                else:
                    print("Firebase credentials not found. Using mock data.")
                    self.mock_mode = True
                    return
            
            # Initialize the app if not already initialized
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, {
                    'databaseURL': os.getenv('FIREBASE_DATABASE_URL'),
                    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
                })
                print("Firebase initialized successfully")
            else:
                print("Firebase app already initialized")
                
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            print("Falling back to mock data mode")
            self.mock_mode = True
    
    def get_all_falls(self):
        """Get all fall detection records from Firebase"""
        if self.mock_mode:
            print("Using mock data (Firebase not initialized)")
            return self.get_mock_data()
            
        try:
            # Updated to use 'fall_detections' path from your Firebase structure
            ref = db.reference('fall_detections')
            print(f"Attempting to fetch data from Firebase path: fall_detections")
            falls_data = ref.get()
            
            if not falls_data:
                print("No data found in Firebase at 'fall_detections' path, using mock data")
                return self.get_mock_data()
            
            print(f"Successfully fetched {len(falls_data)} records from Firebase")
            
            # Convert Firebase data to dashboard format
            falls_list = []
            for key, value in falls_data.items():
                # Map Firebase data to dashboard format
                fall_record = {
                    'id': key,
                    'timestamp': self._convert_timestamp(value.get('timestamp')),
                    'location': value.get('location', 'Unknown'),
                    'severity': self._map_confidence_to_severity(value.get('confidence', 'medium')),
                    'confidence': self._convert_confidence_to_percentage(value.get('confidence', 'medium')),
                    'person_id': value.get('device_type', 'Unknown'),
                    'video_url': self._get_video_url_from_data(value),
                    'duration': self._get_video_duration(value),
                    'response_time': self._calculate_response_time(value),
                    'detection_method': value.get('detection_method', 'Unknown'),
                    'status': value.get('status', 'detected'),
                    'created_at': value.get('created_at', ''),
                    'device_type': value.get('device_type', 'Unknown')
                }
                falls_list.append(fall_record)
            
            # Sort by timestamp (newest first)
            falls_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return falls_list
            
        except Exception as e:
            print(f"Error fetching falls data: {e}")
            print("Falling back to mock data")
            return self.get_mock_data()
    
    def _convert_timestamp(self, timestamp):
        """Convert Firebase timestamp to ISO format"""
        if not timestamp:
            return datetime.now().isoformat()
        
        try:
            # Handle different timestamp formats from Firebase
            if isinstance(timestamp, str):
                # Try parsing "2025-08-28 13:01:54" format
                if ' ' in timestamp and ':' in timestamp:
                    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    return dt.isoformat()
                # If already in ISO format, return as is
                return timestamp
            return str(timestamp)
        except Exception as e:
            print(f"Error converting timestamp {timestamp}: {e}")
            return datetime.now().isoformat()
    
    def _map_confidence_to_severity(self, confidence):
        """Map Firebase confidence to dashboard severity"""
        if isinstance(confidence, str):
            confidence_lower = confidence.lower()
            if confidence_lower == 'high':
                return 'High'
            elif confidence_lower == 'medium':
                return 'Medium'
            elif confidence_lower == 'low':
                return 'Low'
        return 'Medium'  # Default
    
    def _convert_confidence_to_percentage(self, confidence):
        """Convert Firebase confidence to percentage"""
        if isinstance(confidence, str):
            confidence_lower = confidence.lower()
            if confidence_lower == 'high':
                return 95.0
            elif confidence_lower == 'medium':
                return 75.0
            elif confidence_lower == 'low':
                return 55.0
        return 75.0  # Default
    
    def _get_video_url_from_data(self, fall_data):
        """Extract video URL from Firebase data"""
        video_info = fall_data.get('video', {})
        
        # Check for Cloudinary URL first
        if 'cloudinary_url' in video_info:
            return video_info['cloudinary_url']
        
        # Check for local filename
        if 'local_filename' in video_info:
            return f"videos/{video_info['local_filename']}"
        
        # Fallback to generated name based on timestamp
        timestamp = fall_data.get('timestamp', '')
        if timestamp:
            clean_timestamp = timestamp.replace(' ', '_').replace(':', '').replace('-', '')
            return f"videos/fall_{clean_timestamp}.mp4"
        
        return "videos/no_video.mp4"
    
    def _get_video_duration(self, fall_data):
        """Get video duration from Firebase data"""
        video_info = fall_data.get('video', {})
        duration = video_info.get('duration_seconds', 0)
        
        if duration > 0:
            return round(duration, 1)
        
        return 5.0  # Default duration
    
    def _calculate_response_time(self, fall_data):
        """Calculate response time (simulated for now)"""
        # This would be calculated based on when alerts were sent
        # For now, return a reasonable default
        import random
        return round(30 + random.randint(0, 60), 1)
    
    def get_mock_data(self):
        """Generate mock data for development"""
        mock_falls = []
        base_time = datetime.now()
        
        for i in range(20):
            fall_time = base_time - timedelta(days=i*2, hours=i, minutes=i*30)
            mock_falls.append({
                'id': f'fall_{i+1}',
                'timestamp': fall_time.isoformat(),
                'location': f'raspberry_pi_camera',
                'severity': ['Low', 'Medium', 'High'][i % 3],
                'confidence': round(85 + (i % 15), 1),
                'person_id': 'raspberry_pi',
                'video_url': f'videos/fall_{i+1}.mp4',
                'duration': round(2.5 + (i % 5), 1),
                'response_time': round(30 + (i % 120), 1),
                'detection_method': 'pose_analysis',
                'status': 'detected',
                'created_at': fall_time.isoformat(),
                'device_type': 'raspberry_pi'
            })
        
        return mock_falls
    
    def get_video_url(self, video_path):
        """Get signed URL for video from Firebase Storage or return direct URL"""
        try:
            # If it's already a full URL (like Cloudinary), return it directly
            if video_path.startswith('http://') or video_path.startswith('https://'):
                return video_path
            
            # For Firebase Storage paths
            if not self.mock_mode:
                bucket = storage.bucket()
                blob = bucket.blob(video_path)
                # Generate signed URL valid for 1 hour
                url = blob.generate_signed_url(expiration=timedelta(hours=1))
                return url
            
            # Fallback for mock mode
            return None
            
        except Exception as e:
            print(f"Error getting video URL: {e}")
            return None

# Initialize Firebase service
firebase_service = FirebaseService()

def calculate_stats(falls_data):
    """Calculate statistics from falls data"""
    now = datetime.now()
    today = now.date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    stats = {
        'today': 0,
        'this_week': 0,
        'this_month': 0,
        'total': len(falls_data),
        'by_severity': {'Low': 0, 'Medium': 0, 'High': 0},
        'by_location': defaultdict(int),
        'timeline': defaultdict(int)
    }
    
    for fall in falls_data:
        try:
            fall_date = datetime.fromisoformat(fall['timestamp'].replace('Z', '+00:00')).date()
            
            # Count by time period
            if fall_date == today:
                stats['today'] += 1
            if fall_date >= week_start:
                stats['this_week'] += 1
            if fall_date >= month_start:
                stats['this_month'] += 1
            
            # Count by severity
            severity = fall.get('severity', 'Low')
            if severity in stats['by_severity']:
                stats['by_severity'][severity] += 1
            
            # Count by location
            location = fall.get('location', 'Unknown')
            stats['by_location'][location] += 1
            
            # Timeline data (by day for last 30 days)
            if (today - fall_date).days <= 30:
                stats['timeline'][fall_date.strftime('%Y-%m-%d')] += 1
                
        except Exception as e:
            print(f"Error processing fall data: {e}")
            continue
    
    return stats

@app.route('/')
def home():
    """Home page route"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard route"""
    falls_data = firebase_service.get_all_falls()
    stats = calculate_stats(falls_data)
    return render_template('dashboard.html', falls=falls_data[:10], stats=stats, mock_mode=firebase_service.mock_mode)

@app.route('/api/falls')
def api_falls():
    """API endpoint for falls data"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    falls_data = firebase_service.get_all_falls()
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_falls = falls_data[start:end]
    
    return jsonify({
        'falls': paginated_falls,
        'total': len(falls_data),
        'page': page,
        'per_page': per_page,
        'has_next': end < len(falls_data)
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    falls_data = firebase_service.get_all_falls()
    stats = calculate_stats(falls_data)
    return jsonify(stats)

@app.route('/api/video/<path:video_path>')
def get_video_url(video_path):
    """Get signed URL for video or return direct URL"""
    # If it's already a full URL, return it directly
    if video_path.startswith('http://') or video_path.startswith('https://'):
        return jsonify({'url': video_path})
    
    # Otherwise, get from Firebase Storage
    url = firebase_service.get_video_url(video_path)
    if url:
        return jsonify({'url': url})
    else:
        return jsonify({'error': 'Video not found'}), 404

@app.route('/fall/<fall_id>')
def fall_detail(fall_id):
    """Fall detail page"""
    falls_data = firebase_service.get_all_falls()
    fall = next((f for f in falls_data if f['id'] == fall_id), None)
    
    if not fall:
        return "Fall not found", 404
    
    return render_template('fall_detail.html', fall=fall)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
