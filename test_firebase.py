#!/usr/bin/env python3
"""
Simple Firebase connectivity test
"""
import os
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_firebase_connection():
    try:
        # Initialize Firebase using the service account file
        service_account_path = 'firebase-service-account.json'
        
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            print(f"✓ Service account file found: {service_account_path}")
        else:
            print(f"✗ Service account file not found: {service_account_path}")
            return False
        
        # Initialize Firebase app
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv('FIREBASE_DATABASE_URL'),
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
            })
            print("✓ Firebase app initialized successfully")
        
        # Test database connection
        ref = db.reference('/')
        print("✓ Connected to Firebase Realtime Database")
        
        # Test reading from fall_detections path
        fall_ref = db.reference('fall_detections')
        data = fall_ref.get()
        
        if data:
            print(f"✓ Successfully read data from 'fall_detections' path")
            print(f"✓ Found {len(data)} records:")
            for key, value in data.items():
                timestamp = value.get('timestamp', 'No timestamp')
                confidence = value.get('confidence', 'No confidence')
                location = value.get('location', 'No location')
                print(f"  - {key}: {timestamp} | {confidence} | {location}")
        else:
            print("✗ No data found at 'fall_detections' path")
            
        # Test reading from root to see all available paths
        print("\n📋 Available database paths:")
        root_data = ref.get()
        if root_data:
            for key in root_data.keys():
                print(f"  - {key}")
        
        return True
        
    except Exception as e:
        print(f"✗ Firebase connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔥 Firebase Connection Test")
    print("=" * 30)
    success = test_firebase_connection()
    print("=" * 30)
    if success:
        print("✓ Firebase test completed successfully")
    else:
        print("✗ Firebase test failed")
