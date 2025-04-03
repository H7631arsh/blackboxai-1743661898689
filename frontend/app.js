// DOM Elements
const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const audioUpload = document.getElementById('audioUpload');
const audioPlayer = document.getElementById('audioPlayer');
const audioContainer = document.getElementById('audioContainer');
const noAudio = document.getElementById('noAudio');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsContainer = document.getElementById('resultsContainer');
const resultsContent = document.getElementById('resultsContent');

// Audio recording variables
let mediaRecorder;
let audioChunks = [];
let audioBlob;

// Initialize the app
function init() {
    // Check for browser support
    if (!navigator.mediaDevices || !window.MediaRecorder) {
        alert('Audio recording is not supported in your browser. Please use Chrome or Firefox.');
        recordBtn.disabled = true;
    }

    // Event listeners
    recordBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);
    audioUpload.addEventListener('change', handleFileUpload);
    analyzeBtn.addEventListener('click', analyzeAudio);
}

// Start audio recording
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = () => {
            audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayer.src = audioUrl;
            showAudioPlayer();
            audioChunks = [];
        };
        
        mediaRecorder.start();
        recordBtn.disabled = true;
        stopBtn.disabled = false;
    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Error accessing microphone. Please ensure you have granted microphone permissions.');
    }
}

// Stop audio recording
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        recordBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

// Handle file upload
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.match('audio.*')) {
        alert('Please select an audio file');
        return;
    }

    audioBlob = file;
    const audioUrl = URL.createObjectURL(file);
    audioPlayer.src = audioUrl;
    showAudioPlayer();
}

// Show the audio player and hide the "no audio" message
function showAudioPlayer() {
    audioContainer.classList.remove('hidden');
    noAudio.classList.add('hidden');
}

// Analyze the audio content
async function analyzeAudio() {
    if (!audioBlob) {
        alert('Please record or upload audio first');
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Analyzing...</span>';

    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.wav');

        const response = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Analysis failed');
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Error analyzing audio:', error);
        alert('Error analyzing audio. Please try again.');
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search"></i><span>Analyze Content</span>';
    }
}

// Display the analysis results
function displayResults(result) {
    resultsContent.innerHTML = '';
    
    if (result.inappropriate) {
        resultsContent.innerHTML += `
            <div class="bg-red-100 border-l-4 border-red-500 p-4 mb-4">
                <div class="flex items-center">
                    <i class="fas fa-exclamation-circle text-red-500 mr-2"></i>
                    <h3 class="font-bold text-red-700">Inappropriate Content Detected</h3>
                </div>
                <p class="text-red-600 mt-2">Confidence: ${(result.confidence * 100).toFixed(2)}%</p>
            </div>
        `;
    } else {
        resultsContent.innerHTML += `
            <div class="bg-green-100 border-l-4 border-green-500 p-4 mb-4">
                <div class="flex items-center">
                    <i class="fas fa-check-circle text-green-500 mr-2"></i>
                    <h3 class="font-bold text-green-700">No Inappropriate Content Detected</h3>
                </div>
                <p class="text-green-600 mt-2">Confidence: ${(result.confidence * 100).toFixed(2)}%</p>
            </div>
        `;
    }

    if (result.keywords && result.keywords.length > 0) {
        resultsContent.innerHTML += `
            <div class="bg-blue-100 border-l-4 border-blue-500 p-4">
                <h3 class="font-bold text-blue-700">Detected Keywords:</h3>
                <div class="flex flex-wrap gap-2 mt-2">
                    ${result.keywords.map(keyword => `
                        <span class="bg-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm">
                            ${keyword}
                        </span>
                    `).join('')}
                </div>
            </div>
        `;
    }

    resultsContainer.classList.remove('hidden');
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', init);