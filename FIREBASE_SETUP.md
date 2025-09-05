# Firebase Setup Guide for Fall Detection Dashboard

## Overview
Your dashboard is now configured to fetch real data from Firebase Realtime Database under the `fall_detections` path. The application automatically maps your Firebase data structure to the dashboard format.

## Firebase Data Mapping

Your Firebase data structure:
```json
{
  "fall_detections": {
    "-OYkY_-w22uHk1ApT59c": {
      "confidence": "high",
      "device_type": "raspberry_pi", 
      "location": "raspberry_pi_camera",
      "status": "detected",
      "timestamp": "2025-08-28 13:01:54",
      "video": {
        "cloudinary_url": "https://res.cloudinary.com/...",
        "duration_seconds": 5.8
      }
    }
  }
}
```

Maps to dashboard format:
- `confidence` → `severity` (high/medium/low → High/Medium/Low)
- `device_type` → `person_id` (shown as "Device" in table)
- `location` → `location`
- `timestamp` → `timestamp` (converted to ISO format)
- `video.cloudinary_url` → `video_url` (direct URL)
- `video.duration_seconds` → `duration`

## Setting Up Firebase Credentials

### Step 1: Get Firebase Service Account Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings → Service Accounts
4. Click "Generate new private key"
5. Download the JSON file

### Step 2: Configure Environment Variables

Update your `.env` file with the values from the downloaded JSON:

```bash
# Copy from your Firebase service account JSON
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour actual private key\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/
FIREBASE_STORAGE_BUCKET=your-project.appspot.com

# Flask settings
FLASK_SECRET_KEY=your-secure-secret-key
FLASK_DEBUG=True
```

### Step 3: Testing the Connection

1. Update your `.env` file with real credentials
2. Restart the Flask application
3. Check the console output for "Firebase initialized successfully"
4. Visit http://localhost:5000 to see your real data

## Features with Your Data

### ✅ Working Features:
1. **Real Fall Detection Data**: Shows your actual fall detections from Raspberry Pi
2. **Cloudinary Video Integration**: Direct video playback from Cloudinary URLs
3. **Device Information**: Shows device type (raspberry_pi)
4. **Location Tracking**: Maps your camera locations
5. **Confidence Mapping**: Converts high/medium/low to dashboard format
6. **Timeline Charts**: Shows real fall detection patterns
7. **Statistics**: Calculates real stats from your data

### 📊 Dashboard Displays:
- **Today's Falls**: Count of falls detected today
- **This Week**: Weekly statistics
- **This Month**: Monthly analytics  
- **Total Falls**: All-time count
- **Timeline Chart**: 30-day trend of your actual data
- **Severity Distribution**: Based on your confidence levels
- **Location Analysis**: Your camera locations

### 🎥 Video Features:
- **Direct Cloudinary Playback**: Videos play directly from your Cloudinary URLs
- **Download Support**: Can download video files
- **Auto-loading**: Videos load automatically in detail view

## Troubleshooting

### Firebase Connection Issues
```
Error: "Unable to load PEM file"
```
**Solution**: Ensure private key in `.env` has proper line breaks (`\n`)

### No Data Showing
```
Error: "No data found in Firebase"
```
**Solution**: 
1. Check database URL in `.env`
2. Verify data exists under `fall_detections` path
3. Check Firebase Database rules allow read access

### Video Not Playing
```
Error: "Video not available"
```  
**Solution**:
1. Verify Cloudinary URLs are accessible
2. Check video format compatibility (MP4 recommended)
3. Ensure Cloudinary account has proper permissions

## Current Status

🔄 **Application Status**: Running on http://localhost:5000
📊 **Data Mode**: Mock data (will switch to real data when Firebase is configured)
🎯 **Ready for**: Firebase credential configuration

## Next Steps

1. **Configure Firebase**: Add your credentials to `.env` file
2. **Test Connection**: Restart app and verify "Firebase initialized successfully" 
3. **View Real Data**: Dashboard will automatically show your fall detection data
4. **Customize**: Modify mappings in `app.py` if needed

Your dashboard is fully prepared to work with your Firebase data structure!
