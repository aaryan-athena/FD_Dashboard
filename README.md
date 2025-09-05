# Fall Detection Dashboard

A comprehensive dashboard for monitoring fall detection events with Firebase integration.

## Features

- **Real-time Dashboard**: Monitor fall detection events in real-time
- **Statistics & Analytics**: View comprehensive statistics with charts and graphs
- **Video Playback**: Watch fall detection videos stored in Firebase Storage
- **Detailed Fall Information**: View detailed information about each fall event
- **Timeline Tracking**: Track falls over time with interactive charts
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: Firebase Realtime Database
- **Storage**: Firebase Storage
- **Frontend**: Bootstrap 5, Chart.js
- **Authentication**: Firebase Admin SDK

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Firebase project with Realtime Database and Storage enabled

### 2. Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip install flask firebase-admin python-dotenv requests
```

### 3. Firebase Configuration

1. Create a Firebase project at https://console.firebase.google.com/
2. Enable Realtime Database and Storage
3. Generate a service account key:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download the JSON file

4. Update the `.env` file with your Firebase credentials:
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-service-account-email
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com/
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FLASK_SECRET_KEY=your-secret-key
```

### 4. Database Structure

The dashboard expects the following structure in Firebase Realtime Database:

```json
{
  "falls": {
    "fall_1": {
      "timestamp": "2024-01-15T10:30:00Z",
      "location": "Living Room",
      "person_id": "person_1",
      "severity": "High",
      "confidence": 95.5,
      "video_url": "videos/fall_1.mp4",
      "duration": 3.2,
      "response_time": 45
    }
  }
}
```

### 5. Running the Application

```bash
python run.py
```

The dashboard will be available at http://localhost:5000

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/falls` - Get falls data (with pagination)
- `GET /api/stats` - Get statistics
- `GET /api/video/<path>` - Get signed URL for video
- `GET /fall/<fall_id>` - Fall detail page

## File Structure

```
FD_Dashboard/
├── app.py              # Main Flask application
├── run.py              # Application runner
├── .env                # Environment variables
├── templates/
│   ├── dashboard.html  # Main dashboard template
│   └── fall_detail.html # Fall detail template
├── static/
│   ├── css/
│   │   └── dashboard.css # Dashboard styles
│   └── js/
│       └── dashboard.js  # Dashboard JavaScript
└── fddenv/             # Virtual environment
```

## Features in Detail

### Dashboard Overview
- Real-time statistics showing falls today, this week, this month, and total
- Interactive timeline chart showing fall patterns over the last 30 days
- Severity distribution pie chart
- Location distribution bar chart
- Recent falls table with pagination

### Fall Detail View
- Complete fall information including timestamp, location, severity, and confidence
- Video player for fall detection footage
- Event timeline showing detection, analysis, and alert phases
- Action buttons for marking as resolved, sending alerts, and generating reports
- System status indicators

### Video Integration
- Secure video playback using Firebase Storage signed URLs
- Auto-loading of videos in detail view
- Download functionality for video files

### Data Visualization
- Chart.js powered charts for better data visualization
- Responsive design that works on all devices
- Real-time updates with auto-refresh functionality

## Customization

### Adding New Chart Types
1. Add chart creation function in `dashboard.js`
2. Update the `initializeCharts()` function
3. Add corresponding HTML canvas element

### Modifying Data Structure
1. Update the Firebase service methods in `app.py`
2. Modify the frontend JavaScript to handle new data fields
3. Update templates to display new information

### Styling Changes
1. Modify `dashboard.css` for custom styling
2. Update Bootstrap classes in templates
3. Add new CSS animations or transitions

## Troubleshooting

### Firebase Connection Issues
- Verify your Firebase credentials in `.env`
- Check if Realtime Database and Storage are enabled
- Ensure service account has proper permissions

### Video Playback Issues
- Verify video files are uploaded to Firebase Storage
- Check if signed URL generation is working
- Ensure video formats are supported by browsers

### Mock Data
The application includes mock data generation for development and testing when Firebase is not available.

## Security Considerations

- Store Firebase credentials securely
- Use signed URLs for video access
- Implement proper authentication for production use
- Validate all user inputs
- Use HTTPS in production

## Future Enhancements

- User authentication and role-based access
- Email/SMS alerts for emergency situations
- Machine learning model integration for better accuracy
- Historical data analysis and reporting
- Mobile app companion
- Integration with smart home systems
