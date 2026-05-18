/**
 * Main JavaScript utilities for Face Recognition Attendance System
 */

// Utility function to show messages
function showMessage(message, type = 'info') {
    const messageBox = document.getElementById('messageBox');
    if (!messageBox) return;

    messageBox.textContent = message;
    messageBox.className = `message-box message-${type} show`;

    setTimeout(() => {
        messageBox.classList.remove('show');
    }, 5000);
}

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Utility function to format time
function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
}

// Utility function to validate form
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const inputs = form.querySelectorAll('input[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'var(--danger)';
            isValid = false;
        } else {
            input.style.borderColor = 'var(--gray-300)';
        }
    });

    return isValid;
}

// Utility function to clear form
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
    }
}

// Webcam utilities
class WebcamManager {
    constructor(videoElement, canvasElement) {
        this.video = videoElement;
        this.canvas = canvasElement;
        this.stream = null;
        this.ctx = canvasElement ? canvasElement.getContext('2d') : null;
    }

    async start() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 }
            });
            this.video.srcObject = this.stream;

            this.video.onloadedmetadata = () => {
                if (this.canvas) {
                    this.canvas.width = this.video.videoWidth;
                    this.canvas.height = this.video.videoHeight;
                }
            };

            return true;
        } catch (error) {
            console.error('Error starting webcam:', error);
            return false;
        }
    }

    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
            this.video.srcObject = null;
        }
    }

    captureFrame() {
        if (!this.video.videoWidth || !this.video.videoHeight) {
            return null;
        }

        if (this.canvas && this.ctx) {
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            this.ctx.drawImage(this.video, 0, 0);
            return this.canvas.toDataURL('image/jpeg', 0.8);
        }

        return null;
    }

    drawBox(x, y, width, height, label = '', color = '#00FF00') {
        if (!this.ctx) return;

        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(x, y, width, height);

        if (label) {
            this.ctx.fillStyle = color;
            this.ctx.fillRect(x, y - 30, width, 30);
            this.ctx.fillStyle = '#FFFFFF';
            this.ctx.font = '16px Inter';
            this.ctx.fillText(label, x + 5, y - 8);
        }
    }
}

// API utilities
class APIClient {
    static async post(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: data instanceof FormData ? data : JSON.stringify(data),
                headers: data instanceof FormData ? {} : {
                    'Content-Type': 'application/json'
                }
            });

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    static async get(url, params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const fullUrl = queryString ? `${url}?${queryString}` : url;

            const response = await fetch(fullUrl);
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
}

// Export utilities
window.showMessage = showMessage;
window.formatDate = formatDate;
window.formatTime = formatTime;
window.validateForm = validateForm;
window.clearForm = clearForm;
window.WebcamManager = WebcamManager;
window.APIClient = APIClient;
