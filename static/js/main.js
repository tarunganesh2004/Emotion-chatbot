let video = document.getElementById('webcam');
let canvas = document.getElementById('canvas');
let chatWindow = document.getElementById('chat');
let emotionDisplay = document.getElementById('emotion');
let messageInput = document.getElementById('message');
let currentEmotion = 'neutral';
let previousEmotion = null; // Track previous emotion for change detection
const userId = 'anonymous'; // Replace with dynamic user ID if needed

// Initialize webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => console.error('Webcam access failed:', err));

// Capture and detect emotion
async function captureFrame() {
    try {
        video.style.filter = 'brightness(1.5) contrast(1.2)'; // Adjust brightness
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        let imgData = canvas.toDataURL('image/jpeg');
        let response = await fetch('/detect_emotion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imgData, user_id: userId })
        });
        let data = await response.json();
        if (data.emotion) {
            currentEmotion = data.emotion;
            emotionDisplay.textContent = `Feeling: ${currentEmotion.charAt(0).toUpperCase() + currentEmotion.slice(1)}`;
            // Check if emotion has changed
            if (previousEmotion !== currentEmotion) {
                await fetchEmotionResponse(currentEmotion);
                previousEmotion = currentEmotion;
            }
            updateEmotionChart();
        }
    } catch (err) {
        console.error('Emotion detection failed:', err);
    }
}

// Fetch emotion-based response
async function fetchEmotionResponse(emotion) {
    try {
        let response = await fetch('/emotion_response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emotion, user_id: userId })
        });
        let data = await response.json();
        if (data.response) {
            chatWindow.innerHTML += `<p class="bot"><b>Bot:</b> ${data.response}</p>`;
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    } catch (err) {
        console.error('Emotion response failed:', err);
        chatWindow.innerHTML += `<p class="bot text-danger"><b>Bot:</b> Oops, something went wrong!</p>`;
    }
}

// Send chat message
async function sendMessage() {
    let message = messageInput.value.trim();
    if (!message) return;

    chatWindow.innerHTML += `<p class="user"><b>You:</b> ${message}</p>`;
    chatWindow.scrollTop = chatWindow.scrollHeight;
    messageInput.value = '';

    try {
        let response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, emotion: currentEmotion, user_id: userId })
        });
        let data = await response.json();
        if (data.response) {
            chatWindow.innerHTML += `<p class="bot"><b>Bot:</b> ${data.response}</p>`;
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    } catch (err) {
        console.error('Chat failed:', err);
        chatWindow.innerHTML += `<p class="bot text-danger"><b>Bot:</b> Oops, something went wrong!</p>`;
    }
}

// Initialize emotion chart
let emotionChart = new Chart(document.getElementById('emotionChart'), {
    type: 'pie',
    data: {
        labels: [],
        datasets: [{
            data: [],
            backgroundColor: [
                '#28a745', // Happy (Green)
                '#dc3545', // Sad (Red)
                '#ffc107', // Angry (Yellow)
                '#17a2b8', // Neutral (Cyan)
                '#6f42c1', // Disgust (Purple)
                '#fd7e14', // Fear (Orange)
                '#6610f2'  // Surprise (Indigo)
            ]
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: 'Emotion Distribution' }
        }
    }
});

// Update emotion chart
async function updateEmotionChart() {
    try {
        let response = await fetch(`/emotion_stats?user_id=${userId}`);
        let stats = await response.json();
        emotionChart.data.labels = stats.labels;
        emotionChart.data.datasets[0].data = stats.data;
        emotionChart.update();
    } catch (err) {
        console.error('Failed to update emotion chart:', err);
    }
}

// Handle Enter key for sending messages
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Initialize
window.onload = () => {
    chatWindow.innerHTML = '<p class="bot"><b>Bot:</b> Hey there! I’m here to chat and understand how you’re feeling!</p>';
    setInterval(captureFrame, 2000); // Detect emotion every 2 seconds
    updateEmotionChart();
};