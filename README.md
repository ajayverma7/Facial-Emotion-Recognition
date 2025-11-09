# 🧠 Real-Time Facial Emotion Recognition System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-orange.svg)](https://tensorflow.org)
[![R](https://img.shields.io/badge/R-4.0+-blue.svg)](https://r-project.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive real-time facial emotion recognition system built with **Python Flask backend**, **modern web frontend**, and **R programming** for advanced statistical analysis. Perfect for academic projects, research, and learning computer vision concepts.

## 🌟 Features

- 🎥 **Real-time emotion detection** from webcam feed
- 📸 **Image upload and analysis** with drag-and-drop support
- 😊 **7 Emotion categories**: Happy, Sad, Angry, Surprised, Neutral, Disgust, Fear
- 💾 **JSON database** for storing predictions and statistics
- 📊 **R scripts** for statistical analysis and data visualization
- 🌐 **Modern responsive web interface** with live video feed
- 📈 **Interactive charts** and emotion analytics
- 🔍 **Face detection** with bounding boxes and confidence scores

## 🚀 Demo

![Emotion Recognition Demo](https://via.placeholder.com/800x400/4CAF50/FFFFFF?text=Real-Time+Emotion+Detection+Demo)

## 📁 Project Structure

```
face-emotion/
├── 🐍 Backend
│   ├── app.py                    # Flask server with REST API
│   ├── emotion_detector.py       # DeepFace emotion detection
│   ├── database.py              # JSON database operations
│   ├── setup_and_run.py         # Automated setup script
│   └── requirements.txt         # Python dependencies
│
├── 🌐 Frontend
│   ├── templates/index.html     # Responsive web interface
│   ├── static/css/style.css     # Modern CSS styling
│   ├── static/js/main.js        # Interactive JavaScript
│   └── static/uploads/          # Image upload storage
│
├── 📊 R Analytics
│   ├── r_scripts/emotion_analysis.R     # Statistical analysis
│   ├── r_scripts/image_experiments.R    # Image processing
│   └── r_scripts/data_visualization.R   # Advanced visualizations
│
├── 💾 Data & Models
│   ├── data/emotions.json       # Emotion detection database
│   └── models/                  # Pre-trained model cache
│
└── 📖 Documentation
    ├── README.md                # This file
    └── INSTALLATION_GUIDE.md    # Detailed setup guide
```

## ⚡ Quick Start

### 🔧 Automated Setup (Recommended)
```bash
git clone https://github.com/yourusername/face-emotion-recognition.git
cd face-emotion-recognition
python setup_and_run.py
```

### 📦 Manual Installation
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/face-emotion-recognition.git
cd face-emotion-recognition

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py

# 4. Open browser to http://localhost:5000
```

### 📊 R Analytics Setup (Optional)
```r
# Install required R packages
install.packages(c("jsonlite", "ggplot2", "dplyr", "plotly", 
                   "magick", "imager", "gridExtra", "corrplot"))

# Run analysis scripts
Rscript r_scripts/emotion_analysis.R
Rscript r_scripts/data_visualization.R
```

## 🎯 Usage

### 🌐 Web Interface
1. **Live Camera Tab**: Real-time webcam emotion detection
2. **Upload Image Tab**: Analyze photos with drag-and-drop
3. **Statistics Tab**: View emotion analytics and export data
4. **History Tab**: Browse detection history with filters

### 🔌 API Endpoints
- `POST /api/detect_emotion` - Upload image analysis
- `POST /api/detect_emotion_webcam` - Real-time webcam analysis
- `GET /api/emotions/recent` - Get recent detections
- `GET /api/emotions/statistics` - Get emotion statistics

### 📊 R Analysis
```bash
# Statistical analysis
Rscript r_scripts/emotion_analysis.R

# Image processing experiments
Rscript r_scripts/image_experiments.R

# Generate visualizations
Rscript r_scripts/data_visualization.R
```

## 🛠️ Technologies Used

| Category | Technologies |
|----------|-------------|
| **Backend** | Python, Flask, OpenCV, DeepFace, TensorFlow |
| **Frontend** | HTML5, CSS3, JavaScript, WebRTC |
| **Database** | JSON file-based storage |
| **Analytics** | R, ggplot2, plotly, dplyr |
| **ML Models** | Pre-trained VGG-Face, emotion classification |
| **Deployment** | Local development server |

## 🎓 Academic Applications

This project demonstrates key concepts in:
- **Computer Vision**: Face detection and emotion classification
- **Web Development**: Full-stack application with REST API
- **Data Science**: Statistical analysis and visualization with R
- **Machine Learning**: Pre-trained model integration
- **Database Design**: JSON-based data storage and retrieval
- **Real-time Processing**: Live video stream analysis

## 📊 Supported Emotions

| Emotion | Description | Use Cases |
|---------|-------------|-----------|
| 😊 **Happy** | Joy, satisfaction, contentment | Customer satisfaction, user experience |
| 😢 **Sad** | Sorrow, disappointment, melancholy | Mental health monitoring, content analysis |
| 😠 **Angry** | Frustration, irritation, rage | Conflict detection, stress analysis |
| 😲 **Surprised** | Shock, amazement, wonder | Engagement measurement, reaction analysis |
| 😐 **Neutral** | Calm, composed, balanced | Baseline measurement, attention tracking |
| 🤢 **Disgust** | Revulsion, distaste, aversion | Content filtering, preference analysis |
| 😨 **Fear** | Anxiety, worry, apprehension | Safety monitoring, stress detection |

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set TensorFlow logging level
export TF_CPP_MIN_LOG_LEVEL=2

# Optional: Disable oneDNN optimizations if needed
export TF_ENABLE_ONEDNN_OPTS=0
```

### Camera Permissions
- Grant camera access when prompted by browser
- For HTTPS deployment, use SSL certificates
- Test camera access at `chrome://settings/content/camera`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DeepFace** library for emotion recognition models
- **TensorFlow** for machine learning framework
- **OpenCV** for computer vision operations
- **Flask** for web framework
- **R Community** for statistical analysis tools

## 📞 Support

- 📧 **Email**: your.email@example.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/face-emotion-recognition/issues)
- 📖 **Documentation**: [Installation Guide](INSTALLATION_GUIDE.md)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/face-emotion-recognition&type=Date)](https://star-history.com/#yourusername/face-emotion-recognition&Date)

---

**Made with ❤️ for academic learning and research**
