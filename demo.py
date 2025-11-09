#!/usr/bin/env python3
"""
Demo Script for Facial Emotion Recognition System
Quick demonstration of core functionality
"""

import os
import sys
import time
import json
from datetime import datetime

def print_demo_header():
    """Print demo header"""
    header = """
    ╔══════════════════════════════════════════════════════════════╗
    ║            Facial Emotion Recognition - Demo                 ║
    ║                                                              ║
    ║  This demo showcases the core functionality of the system   ║
    ║  without requiring a webcam or image uploads.                ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(header)

def demo_emotion_detector():
    """Demonstrate emotion detection capabilities"""
    print("\n🧠 EMOTION DETECTION DEMO")
    print("="*50)
    
    try:
        from emotion_detector import emotion_detector
        
        print("✅ Emotion detector loaded successfully")
        print("   Supported emotions: angry, disgust, fear, happy, sad, surprise, neutral")
        print("   Backend: DeepFace with pre-trained models")
        print("   Detection method: OpenCV + VGG-Face")
        
        # Simulate emotion detection results
        sample_emotions = {
            "happy": 85.2,
            "neutral": 8.1,
            "surprise": 4.2,
            "sad": 1.8,
            "angry": 0.4,
            "disgust": 0.2,
            "fear": 0.1
        }
        
        print(f"\n📊 Sample Detection Results:")
        print(f"   Dominant Emotion: happy (85.2%)")
        for emotion, confidence in sample_emotions.items():
            bar_length = int(confidence / 5)  # Scale for display
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"   {emotion:>8}: {bar} {confidence:>5.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading emotion detector: {e}")
        return False

def demo_database():
    """Demonstrate database functionality"""
    print("\n💾 DATABASE DEMO")
    print("="*50)
    
    try:
        from database import emotion_db
        
        print("✅ Database connection established")
        
        # Get current statistics
        stats = emotion_db.get_emotion_statistics()
        total_detections = stats.get('total_detections', 0)
        
        print(f"   Database file: data/emotions.json")
        print(f"   Total detections: {total_detections}")
        
        if total_detections > 0:
            emotion_counts = stats.get('emotion_counts', {})
            print(f"   Emotion breakdown:")
            for emotion, count in emotion_counts.items():
                if count > 0:
                    print(f"     {emotion}: {count} detections")
        else:
            print("   No detection records found")
            
            # Add sample data
            print("\n   Adding sample detection records...")
            sample_records = [
                {
                    "dominant_emotion": "happy",
                    "emotions": {"happy": 87.3, "neutral": 8.2, "surprise": 4.5},
                    "success": True,
                    "source": "demo"
                },
                {
                    "dominant_emotion": "neutral", 
                    "emotions": {"neutral": 82.1, "happy": 12.3, "sad": 5.6},
                    "success": True,
                    "source": "demo"
                },
                {
                    "dominant_emotion": "surprise",
                    "emotions": {"surprise": 78.9, "happy": 15.2, "neutral": 5.9},
                    "success": True,
                    "source": "demo"
                }
            ]
            
            for record in sample_records:
                emotion_db.add_emotion_record(record)
                print(f"     ✅ Added {record['dominant_emotion']} detection")
            
            print(f"   Sample data created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with database: {e}")
        return False

def demo_api_endpoints():
    """Demonstrate API endpoint structure"""
    print("\n🌐 API ENDPOINTS DEMO")
    print("="*50)
    
    endpoints = [
        {
            "method": "POST",
            "endpoint": "/api/detect_emotion",
            "description": "Upload image for emotion analysis",
            "example": "curl -X POST -F 'image=@photo.jpg' http://localhost:5000/api/detect_emotion"
        },
        {
            "method": "POST", 
            "endpoint": "/api/detect_emotion_webcam",
            "description": "Analyze webcam frame (base64 image)",
            "example": "Used by frontend for real-time detection"
        },
        {
            "method": "GET",
            "endpoint": "/api/emotions/recent",
            "description": "Get recent emotion detections",
            "example": "curl http://localhost:5000/api/emotions/recent?limit=10"
        },
        {
            "method": "GET",
            "endpoint": "/api/emotions/statistics", 
            "description": "Get emotion detection statistics",
            "example": "curl http://localhost:5000/api/emotions/statistics"
        },
        {
            "method": "GET",
            "endpoint": "/api/emotions/search",
            "description": "Search emotions by type",
            "example": "curl http://localhost:5000/api/emotions/search?type=happy"
        }
    ]
    
    print("✅ Available API endpoints:")
    for endpoint in endpoints:
        print(f"\n   {endpoint['method']} {endpoint['endpoint']}")
        print(f"   Description: {endpoint['description']}")
        print(f"   Example: {endpoint['example']}")

def demo_r_integration():
    """Demonstrate R integration"""
    print("\n📊 R INTEGRATION DEMO")
    print("="*50)
    
    r_scripts = [
        {
            "file": "r_scripts/emotion_analysis.R",
            "description": "Statistical analysis of emotion data",
            "outputs": ["Emotion frequency analysis", "Confidence statistics", "Temporal patterns"]
        },
        {
            "file": "r_scripts/image_experiments.R", 
            "description": "Image processing experiments",
            "outputs": ["Image preprocessing", "Quality metrics", "Face detection simulation"]
        },
        {
            "file": "r_scripts/data_visualization.R",
            "description": "Advanced data visualizations",
            "outputs": ["Interactive plots", "Statistical charts", "Dashboard creation"]
        }
    ]
    
    print("✅ R Scripts available:")
    for script in r_scripts:
        print(f"\n   📄 {script['file']}")
        print(f"   Purpose: {script['description']}")
        print(f"   Outputs:")
        for output in script['outputs']:
            print(f"     • {output}")
    
    # Check if R is available
    try:
        import subprocess
        result = subprocess.run(["R", "--version"], capture_output=True, text=True, check=True)
        print(f"\n✅ R is installed and available")
        print(f"   To run analysis: Rscript r_scripts/emotion_analysis.R")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"\n⚠️  R is not installed or not in PATH")
        print(f"   R scripts are available but require R installation")

def demo_web_interface():
    """Demonstrate web interface features"""
    print("\n🌐 WEB INTERFACE DEMO")
    print("="*50)
    
    features = [
        {
            "tab": "Live Camera",
            "features": ["Real-time emotion detection", "Auto-detection mode", "Manual capture", "Emotion overlay"]
        },
        {
            "tab": "Upload Image", 
            "features": ["Drag & drop upload", "Multiple format support", "Instant analysis", "Detailed results"]
        },
        {
            "tab": "Statistics",
            "features": ["Detection counts", "Emotion distribution", "Confidence metrics", "Data export"]
        },
        {
            "tab": "History",
            "features": ["Detection timeline", "Filter by date/emotion", "Detailed records", "Search functionality"]
        }
    ]
    
    print("✅ Web interface features:")
    for feature in features:
        print(f"\n   📱 {feature['tab']} Tab:")
        for item in feature['features']:
            print(f"     • {item}")
    
    print(f"\n🚀 To access the web interface:")
    print(f"   1. Run: python app.py")
    print(f"   2. Open browser: http://localhost:5000")
    print(f"   3. Grant camera permissions for live detection")

def demo_project_structure():
    """Show project structure"""
    print("\n📁 PROJECT STRUCTURE DEMO")
    print("="*50)
    
    structure = {
        "Core Files": ["app.py", "emotion_detector.py", "database.py"],
        "Frontend": ["templates/index.html", "static/css/style.css", "static/js/main.js"],
        "R Analytics": ["r_scripts/emotion_analysis.R", "r_scripts/image_experiments.R", "r_scripts/data_visualization.R"],
        "Data": ["data/emotions.json", "data/sample_images/"],
        "Documentation": ["README.md", "INSTALLATION_GUIDE.md", "requirements.txt"]
    }
    
    print("✅ Project organization:")
    for category, files in structure.items():
        print(f"\n   📂 {category}:")
        for file in files:
            exists = "✅" if os.path.exists(file) else "❌"
            print(f"     {exists} {file}")

def run_quick_test():
    """Run a quick functionality test"""
    print("\n🧪 QUICK FUNCTIONALITY TEST")
    print("="*50)
    
    tests = []
    
    # Test 1: Import core modules
    try:
        import flask
        import cv2
        import numpy as np
        tests.append(("Core dependencies", True, "Flask, OpenCV, NumPy imported"))
    except Exception as e:
        tests.append(("Core dependencies", False, f"Import error: {e}"))
    
    # Test 2: Database connection
    try:
        from database import emotion_db
        stats = emotion_db.get_emotion_statistics()
        tests.append(("Database connection", True, "JSON database accessible"))
    except Exception as e:
        tests.append(("Database connection", False, f"Database error: {e}"))
    
    # Test 3: Directory structure
    required_dirs = ["data", "static", "templates", "r_scripts"]
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    if not missing_dirs:
        tests.append(("Directory structure", True, "All required directories exist"))
    else:
        tests.append(("Directory structure", False, f"Missing: {missing_dirs}"))
    
    # Test 4: Configuration files
    config_files = ["requirements.txt", "README.md"]
    missing_files = [f for f in config_files if not os.path.exists(f)]
    if not missing_files:
        tests.append(("Configuration files", True, "All config files present"))
    else:
        tests.append(("Configuration files", False, f"Missing: {missing_files}"))
    
    # Display test results
    print("Test Results:")
    passed = 0
    for test_name, success, message in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}: {message}")
        if success:
            passed += 1
    
    print(f"\n📊 Test Summary: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! System is ready to use.")
    else:
        print("⚠️  Some tests failed. Check installation and try setup_and_run.py")

def main():
    """Main demo function"""
    print_demo_header()
    
    print("This demo will showcase the key features of the Facial Emotion Recognition System.")
    print("No webcam or image uploads required - this is a functionality overview.\n")
    
    input("Press Enter to start the demo...")
    
    # Run demo sections
    demo_emotion_detector()
    input("\nPress Enter to continue...")
    
    demo_database()
    input("\nPress Enter to continue...")
    
    demo_api_endpoints()
    input("\nPress Enter to continue...")
    
    demo_r_integration()
    input("\nPress Enter to continue...")
    
    demo_web_interface()
    input("\nPress Enter to continue...")
    
    demo_project_structure()
    input("\nPress Enter to continue...")
    
    run_quick_test()
    
    print("\n" + "="*60)
    print("🎓 DEMO COMPLETED")
    print("="*60)
    print("\nNext steps:")
    print("1. Run 'python setup_and_run.py' for full setup and launch")
    print("2. Or run 'python app.py' to start the web application directly")
    print("3. Open http://localhost:5000 in your browser")
    print("4. Try the R scripts for statistical analysis")
    print("\nFor detailed instructions, see INSTALLATION_GUIDE.md")
    print("\nThank you for trying the Facial Emotion Recognition System! 🚀")

if __name__ == "__main__":
    main()
