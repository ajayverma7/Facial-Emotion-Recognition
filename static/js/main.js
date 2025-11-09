/**
 * Frontend JavaScript for Real-Time Facial Emotion Recognition System
 * Handles webcam access, image upload, and API communication
 */

class EmotionRecognitionApp {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.stream = null;
        this.isDetecting = false;
        this.detectionInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupElements();
        this.setupEventListeners();
        this.loadStatistics();
        this.loadHistory();
    }
    
    setupElements() {
        // Video elements
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas?.getContext('2d');
        
        // Buttons
        this.startCameraBtn = document.getElementById('start-camera');
        this.stopCameraBtn = document.getElementById('stop-camera');
        this.captureBtn = document.getElementById('capture-frame');
        this.autoDetectCheckbox = document.getElementById('auto-detect');
        
        // Upload elements
        this.fileInput = document.getElementById('file-input');
        this.uploadArea = document.getElementById('upload-area');
        
        // Results elements
        this.realtimeResults = document.getElementById('realtime-results');
        this.uploadResults = document.getElementById('upload-results');
        
        // Loading overlay
        this.loadingOverlay = document.getElementById('loading-overlay');
    }
    
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // Camera controls
        this.startCameraBtn?.addEventListener('click', () => this.startCamera());
        this.stopCameraBtn?.addEventListener('click', () => this.stopCamera());
        this.captureBtn?.addEventListener('click', () => this.captureAndAnalyze());
        this.autoDetectCheckbox?.addEventListener('change', (e) => this.toggleAutoDetect(e.target.checked));
        
        // File upload
        this.fileInput?.addEventListener('change', (e) => this.handleFileUpload(e));
        this.uploadArea?.addEventListener('click', () => this.fileInput?.click());
        this.uploadArea?.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea?.addEventListener('drop', (e) => this.handleDrop(e));
        this.uploadArea?.addEventListener('dragleave', (e) => this.handleDragLeave(e));
    }
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // Load data for specific tabs
        if (tabName === 'statistics') {
            this.loadStatistics();
        } else if (tabName === 'history') {
            this.loadHistory();
        }
    }
    
    async startCamera() {
        try {
            this.showLoading();
            
            const constraints = {
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            };
            
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;
            
            await new Promise((resolve) => {
                this.video.onloadedmetadata = resolve;
            });
            
            // Setup canvas
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            
            // Update UI
            this.startCameraBtn.style.display = 'none';
            this.stopCameraBtn.style.display = 'inline-flex';
            this.captureBtn.style.display = 'inline-flex';
            this.realtimeResults.style.display = 'block';
            
            // Start auto-detection if enabled
            if (this.autoDetectCheckbox.checked) {
                this.startAutoDetection();
            }
            
            this.showToast('Camera started successfully', 'success');
            
        } catch (error) {
            console.error('Error starting camera:', error);
            this.showToast('Failed to start camera. Please check permissions.', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        this.stopAutoDetection();
        
        // Update UI
        this.startCameraBtn.style.display = 'inline-flex';
        this.stopCameraBtn.style.display = 'none';
        this.captureBtn.style.display = 'none';
        this.realtimeResults.style.display = 'none';
        
        this.showToast('Camera stopped', 'success');
    }
    
    startAutoDetection() {
        this.isDetecting = true;
        this.detectionInterval = setInterval(() => {
            if (this.isDetecting && this.video && this.video.readyState === 4) {
                this.detectEmotionFromVideo();
            }
        }, 2000); // Detect every 2 seconds
    }
    
    stopAutoDetection() {
        this.isDetecting = false;
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
            this.detectionInterval = null;
        }
    }
    
    toggleAutoDetect(enabled) {
        if (enabled && this.stream) {
            this.startAutoDetection();
        } else {
            this.stopAutoDetection();
        }
    }
    
    async captureAndAnalyze() {
        if (!this.video || this.video.readyState !== 4) {
            this.showToast('Video not ready', 'warning');
            return;
        }
        
        await this.detectEmotionFromVideo(true);
    }
    
    async detectEmotionFromVideo(saveToDb = false) {
        try {
            // Capture frame
            this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            const imageData = this.canvas.toDataURL('image/jpeg', 0.8);
            
            console.log('Sending image data to API...');
            
            // Send to API
            const response = await fetch('/api/detect_emotion_webcam', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData,
                    save_to_db: saveToDb
                })
            });
            
            console.log('API response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('API result:', result);
            
            if (result.success) {
                this.displayRealtimeResults(result);
                if (saveToDb) {
                    this.showToast('Frame analyzed and saved', 'success');
                }
                
                // Show note if it's a mock result
                if (result.note) {
                    console.warn('Mock result:', result.note);
                    if (result.error_details) {
                        console.error('Detection error details:', result.error_details);
                    }
                }
            } else {
                console.error('Detection failed:', result.error);
                if (saveToDb) {
                    this.showToast('Detection failed: ' + result.error, 'error');
                } else {
                    // Show error in console for auto-detection
                    console.warn('Auto-detection failed:', result.error);
                }
            }
            
        } catch (error) {
            console.error('Error detecting emotion:', error);
            if (saveToDb) {
                this.showToast('Error analyzing frame: ' + error.message, 'error');
            } else {
                console.warn('Auto-detection error:', error.message);
            }
        }
    }
    
    displayRealtimeResults(result) {
        const dominantEmotion = document.getElementById('dominant-emotion');
        const dominantConfidence = document.getElementById('dominant-confidence');
        const emotionBars = document.getElementById('emotion-bars');
        
        if (dominantEmotion && dominantConfidence && emotionBars) {
            dominantEmotion.textContent = result.dominant_emotion;
            dominantConfidence.textContent = `${result.emotions[result.dominant_emotion].toFixed(1)}%`;
            
            this.createEmotionBars(result.emotions, emotionBars);
        }
        
        // Update emotion overlay
        const overlay = document.getElementById('emotion-overlay');
        if (overlay) {
            overlay.innerHTML = `
                <div><strong>${result.dominant_emotion}</strong></div>
                <div>${result.emotions[result.dominant_emotion].toFixed(1)}%</div>
            `;
            overlay.style.display = 'block';
        }
    }
    
    createEmotionBars(emotions, container) {
        container.innerHTML = '';
        
        const sortedEmotions = Object.entries(emotions)
            .sort(([,a], [,b]) => b - a);
        
        sortedEmotions.forEach(([emotion, confidence]) => {
            const barElement = document.createElement('div');
            barElement.className = 'emotion-bar';
            barElement.innerHTML = `
                <span class="emotion-name">${emotion}</span>
                <div class="bar-container">
                    <div class="bar-fill" style="width: ${confidence}%"></div>
                </div>
                <span class="emotion-value">${confidence.toFixed(1)}%</span>
            `;
            container.appendChild(barElement);
        });
    }
    
    // File Upload Handlers
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            this.processUploadedFile(file);
        }
    }
    
    handleDragOver(event) {
        event.preventDefault();
        this.uploadArea.classList.add('dragover');
    }
    
    handleDragLeave(event) {
        event.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }
    
    handleDrop(event) {
        event.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.processUploadedFile(files[0]);
        }
    }
    
    async processUploadedFile(file) {
        if (!this.isImageFile(file)) {
            this.showToast('Please select a valid image file', 'error');
            return;
        }
        
        if (file.size > 16 * 1024 * 1024) { // 16MB limit
            this.showToast('File size too large. Maximum 16MB allowed.', 'error');
            return;
        }
        
        try {
            this.showLoading();
            
            // Create FormData
            const formData = new FormData();
            formData.append('image', file);
            
            // Send to API
            const response = await fetch('/api/detect_emotion', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayUploadResults(result, file);
                this.showToast('Image analyzed successfully', 'success');
            } else {
                this.showToast('Analysis failed: ' + result.error, 'error');
            }
            
        } catch (error) {
            console.error('Error uploading file:', error);
            this.showToast('Error uploading file', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    displayUploadResults(result, file) {
        const uploadedImg = document.getElementById('uploaded-img');
        const dominantEmotion = document.getElementById('upload-dominant-emotion');
        const dominantConfidence = document.getElementById('upload-dominant-confidence');
        const emotionBars = document.getElementById('upload-emotion-bars');
        
        // Display uploaded image
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedImg.src = e.target.result;
        };
        reader.readAsDataURL(file);
        
        // Display results
        dominantEmotion.textContent = result.dominant_emotion;
        dominantConfidence.textContent = `${result.emotions[result.dominant_emotion].toFixed(1)}%`;
        
        this.createEmotionBars(result.emotions, emotionBars);
        
        // Show results section
        this.uploadResults.style.display = 'block';
    }
    
    isImageFile(file) {
        const imageTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
        return imageTypes.includes(file.type);
    }
    
    // Statistics
    async loadStatistics() {
        try {
            const response = await fetch('/api/emotions/statistics');
            const result = await response.json();
            
            if (result.success) {
                this.displayStatistics(result.statistics);
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }
    
    displayStatistics(stats) {
        // Update stat cards
        document.getElementById('total-detections').textContent = stats.total_detections || 0;
        
        // Find most common emotion
        const emotionCounts = stats.emotion_counts || {};
        const mostCommon = Object.entries(emotionCounts)
            .sort(([,a], [,b]) => b - a)[0];
        
        document.getElementById('most-common-emotion').textContent = 
            mostCommon ? mostCommon[0] : '-';
        
        // Create emotion chart
        this.createEmotionChart(emotionCounts);
    }
    
    createEmotionChart(emotionCounts) {
        const chartContainer = document.getElementById('emotion-chart');
        chartContainer.innerHTML = '';
        
        const maxCount = Math.max(...Object.values(emotionCounts));
        
        Object.entries(emotionCounts).forEach(([emotion, count]) => {
            const barHeight = maxCount > 0 ? (count / maxCount) * 250 : 20;
            
            const barElement = document.createElement('div');
            barElement.className = 'chart-bar';
            barElement.style.height = `${barHeight}px`;
            barElement.innerHTML = `
                <span class="chart-label">${emotion}</span>
                <span class="chart-value">${count}</span>
            `;
            
            chartContainer.appendChild(barElement);
        });
    }
    
    // History
    async loadHistory() {
        try {
            const response = await fetch('/api/emotions/recent?limit=20');
            const result = await response.json();
            
            if (result.success) {
                this.displayHistory(result.emotions);
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }
    
    displayHistory(emotions) {
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '';
        
        if (emotions.length === 0) {
            historyList.innerHTML = '<p>No emotion records found.</p>';
            return;
        }
        
        emotions.reverse().forEach(emotion => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            const timestamp = new Date(emotion.timestamp).toLocaleString();
            
            historyItem.innerHTML = `
                <div class="history-emotion">${emotion.dominant_emotion}</div>
                <div class="history-details">
                    <div class="history-time">${timestamp}</div>
                    <div>Source: ${emotion.source}</div>
                </div>
                <div class="history-confidence">${emotion.confidence.toFixed(1)}%</div>
            `;
            
            historyList.appendChild(historyItem);
        });
    }
    
    // Filter history
    async filterHistory() {
        const dateFilter = document.getElementById('date-filter').value;
        const emotionFilter = document.getElementById('emotion-filter').value;
        
        let url = '/api/emotions/recent?limit=50';
        
        if (dateFilter) {
            url = `/api/emotions/by_date?date=${dateFilter}`;
        } else if (emotionFilter) {
            url = `/api/emotions/search?type=${emotionFilter}`;
        }
        
        try {
            const response = await fetch(url);
            const result = await response.json();
            
            if (result.success) {
                this.displayHistory(result.emotions);
            }
        } catch (error) {
            console.error('Error filtering history:', error);
        }
    }
    
    // Utility functions
    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }
    
    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        const container = document.getElementById('toast-container');
        container.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }
}

// Global functions for button clicks
async function exportData() {
    try {
        const response = await fetch('/api/emotions/export');
        const result = await response.json();
        
        if (result.success) {
            app.showToast('Data exported successfully', 'success');
        } else {
            app.showToast('Export failed', 'error');
        }
    } catch (error) {
        app.showToast('Export error', 'error');
    }
}

async function clearData() {
    if (!confirm('Are you sure you want to clear all emotion data? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/emotions/clear', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            app.showToast('Data cleared successfully', 'success');
            app.loadStatistics();
            app.loadHistory();
        } else {
            app.showToast('Clear operation failed', 'error');
        }
    } catch (error) {
        app.showToast('Clear operation error', 'error');
    }
}

function loadStatistics() {
    app.loadStatistics();
}

function filterHistory() {
    app.filterHistory();
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new EmotionRecognitionApp();
});
