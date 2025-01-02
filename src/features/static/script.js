document.addEventListener('DOMContentLoaded', function () {
    const startBtn = document.getElementById('startRecording');
    const stopBtn = document.getElementById('stopRecording');
    const listBtn = document.getElementById('listRecordings');
    const replayBtn = document.getElementById('replaySelected');
    const recordingsList = document.getElementById('recordingsList');
    const statusDiv = document.getElementById('status');

    function showStatus(message, isError = false) {
        statusDiv.textContent = message;
        statusDiv.className = 'status-message ' + (isError ? 'error' : 'success');
    }

    startBtn.addEventListener('click', async () => {
        try {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            const response = await fetch('/start_recording', { method: 'POST' });
            const data = await response.json();
            showStatus(data.message);
        } catch (error) {
            showStatus('Error starting recording: ' + error, true);
        }
    });

    stopBtn.addEventListener('click', async () => {
        try {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            const response = await fetch('/stop_recording', { method: 'POST' });
            const data = await response.json();
            showStatus(data.message);
            updateRecordingsList();
        } catch (error) {
            showStatus('Error stopping recording: ' + error, true);
        }
    });

    async function updateRecordingsList() {
        try {
            const response = await fetch('/list_recordings');
            const data = await response.json();
            recordingsList.innerHTML = '';

            data.recordings.forEach(recording => {
                const div = document.createElement('div');
                div.className = 'recording-item';
                div.textContent = recording;
                div.onclick = () => selectRecording(div);
                recordingsList.appendChild(div);
            });
        } catch (error) {
            showStatus('Error listing recordings: ' + error, true);
        }
    }

    function selectRecording(element) {
        document.querySelectorAll('.recording-item').forEach(item => {
            item.classList.remove('selected');
        });
        element.classList.add('selected');
        replayBtn.disabled = false;
    }

    listBtn.addEventListener('click', updateRecordingsList);

    replayBtn.addEventListener('click', async () => {
        const selectedRecording = document.querySelector('.recording-item.selected');
        if (!selectedRecording) return;

        const precision = document.getElementById('precisionMode').checked;
        const loopCount = document.getElementById('loopCount').value;

        try {
            replayBtn.disabled = true;
            const response = await fetch('/replay', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    recording: selectedRecording.textContent,
                    precision: precision,
                    loop_count: loopCount
                })
            });
            const data = await response.json();
            showStatus(data.message);
        } catch (error) {
            showStatus('Error during replay: ' + error, true);
        } finally {
            replayBtn.disabled = false;
        }
    });

    // Initialize recordings list
    updateRecordingsList();
});