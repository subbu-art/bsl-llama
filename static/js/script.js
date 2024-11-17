// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const inputText = document.getElementById('inputText');
    const micButton = document.getElementById('micButton');
    const translateButton = document.getElementById('translateButton');
    const resultContainer = document.getElementById('resultContainer');
    const translationText = document.getElementById('translationText');
    const singleVideoView = document.getElementById('singleVideoView');
    const multiVideoView = document.getElementById('multiVideoView');
    const bslVideo = document.getElementById('bslVideo');
    const videoPlaceholder = document.getElementById('videoPlaceholder');
    
    // Demo video mapping
    const demoVideos = {
        "We are excited to be part of this event": "demo1",
        "Let's go party tonight": "demo2",
        "I hope it will snow this winter": "demo3",
        "You only live once so keep enjoying": "demo4"
    };
    
    // Audio Recording Variables
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let recordingTimer;

    // Suggestions Feature
    window.usesuggestion = function(text) {
        inputText.value = text;
        translateText(text);
    };

    // Reset all videos function
    function resetAllVideos() {
        document.querySelectorAll('.video-item').forEach(item => {
            item.classList.add('hidden');
            item.classList.remove('active');
            const video = item.querySelector('video');
            if (video) {
                video.pause();
                video.currentTime = 0;
            }
        });
        if (bslVideo) {
            bslVideo.pause();
            bslVideo.currentTime = 0;
        }
    }

    // Play specific demo video
    function playDemoVideo(demoId) {
        resetAllVideos();
        const videoItem = document.querySelector(`#${demoId}`);
        if (videoItem) {
            videoItem.classList.remove('hidden');
            videoItem.classList.add('active');
            const video = videoItem.querySelector('video');
            if (video) {
                setTimeout(() => {
                    video.play().catch(e => console.error('Error playing video:', e));
                }, 2000); // 2 second delay after gloss is generated
            }
        }
    }

    // Translation Function
    async function translateText(text) {
        if (!text.trim()) {
            alert('Please enter some text to translate');
            return;
        }

        resetAllVideos();
        translateButton.disabled = true;
        const spinner = translateButton.querySelector('.loading-spinner');
        spinner.classList.remove('hidden');
        
        try {
            const response = await fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `text=${encodeURIComponent(text.trim())}`
            });
            
            const data = await response.json();
            
            if (response.ok) {
                displayResults(data);
            } else {
                throw new Error(data.error || 'Translation failed');
            }
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            translateButton.disabled = false;
            spinner.classList.add('hidden');
        }
    }

    // Display Results Function
    function displayResults(data) {
        translationText.textContent = data.translation;
        const currentText = inputText.value.trim();
        
        if (demoVideos[currentText]) {
            // Show demo video
            singleVideoView.classList.add('hidden');
            multiVideoView.classList.remove('hidden');
            playDemoVideo(demoVideos[currentText]);
        } else {
            // Show regular video
            multiVideoView.classList.add('hidden');
            singleVideoView.classList.remove('hidden');
            resetAllVideos();
            
            if (data.video_path) {
                bslVideo.src = data.video_path;
                bslVideo.classList.remove('hidden');
                videoPlaceholder.classList.add('hidden');
                
                setTimeout(() => {
                    bslVideo.play().catch(e => console.error('Error playing video:', e));
                }, 2000);
            }
        }
        
        resultContainer.classList.remove('hidden');
        setTimeout(() => {
            resultContainer.classList.add('visible');
        }, 50);
    }

    // Handle Recording Timer
    function startRecordingTimer() {
        let duration = 0;
        const maxDuration = 10; // Maximum recording duration in seconds
        
        recordingTimer = setInterval(() => {
            duration++;
            if (duration >= maxDuration && isRecording) {
                stopRecording();
            }
        }, 1000);
    }

    function stopRecording() {
        if (isRecording) {
            clearInterval(recordingTimer);
            mediaRecorder.stop();
            isRecording = false;
            micButton.classList.remove('recording');
        }
    }

    // Audio Recording Setup
    async function setupAudioRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = async () => {
                try {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'recording.wav');
                    
                    const response = await fetch('/transcribe-audio', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        inputText.value = data.text;
                        translateText(data.text);
                    } else {
                        throw new Error(data.error || 'Transcription failed');
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                } finally {
                    audioChunks = [];
                }
            };
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            micButton.disabled = true;
            micButton.title = 'Microphone access denied';
        }
    }

    // Event Listeners
    translateButton.addEventListener('click', () => {
        translateText(inputText.value);
    });

    // Allow translation with Enter key
    inputText.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            translateText(inputText.value);
        }
    });

    // Microphone button handler
    micButton.addEventListener('click', () => {
        if (!isRecording) {
            // Start recording
            audioChunks = [];
            mediaRecorder.start();
            isRecording = true;
            micButton.classList.add('recording');
            startRecordingTimer();
        } else {
            // Stop recording
            stopRecording();
        }
    });

    // Initialize audio recording setup
    setupAudioRecording();
});