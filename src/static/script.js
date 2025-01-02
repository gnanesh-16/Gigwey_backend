document.addEventListener('DOMContentLoaded', function () {
    // ...existing variable declarations...

    // Status polling
    let statusPolling;
    
    function updateButtonStates(isRecording, isPaused) {
        startBtn.disabled = isRecording;
        stopBtn.disabled = !isRecording;
        replayBtn.disabled = isRecording;
        deleteBtn.disabled = isRecording;
        
        const indicator = startBtn.querySelector('.status-indicator');
        indicator.className = 'status-indicator ' + 
            (isRecording ? (isPaused ? 'paused' : 'recording') : 'stopped');
    }

    function startStatusPolling() {
        statusPolling = setInterval(async () => {
            try {
                const response = await fetch('/get_recording_status');
                const data = await response.json();
                updateButtonStates(data.is_recording, data.is_paused);
            } catch (error) {
                console.error('Status polling error:', error);
            }
        }, 1000);
    }

    startBtn.addEventListener('click', async () => {
        try {
            startBtn.disabled = true;
            const response = await fetch('/start_button', { method: 'POST' });
            const data = await response.json();
            showStatus(data.message);
            updateButtonStates(true, false);
        } catch (error) {
            showStatus('Error starting recording: ' + error, true);
            startBtn.disabled = false;
        }
    });

    stopBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/stop_button', { method: 'POST' });
            const data = await response.json();
            showStatus(data.message);
            updateButtonStates(false, false);
            await updateRecordingsList();
        } catch (error) {
            showStatus('Error stopping recording: ' + error, true);
        }
    });

    refreshBtn.addEventListener('click', updateRecordingsList);

    // Initialize
    startStatusPolling();
    updateRecordingsList();

    // Cleanup
    window.addEventListener('beforeunload', () => {
        clearInterval(statusPolling);
    });

    // ...existing code for replay and delete functionality...

    const pauseBtn = document.getElementById('pauseBtn');
    const exportBtn = document.getElementById('exportBtn');
    const importBtn = document.getElementById('importBtn');
    const importInput = document.getElementById('importInput');
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const selectAllBtn = document.getElementById('selectAllBtn');
    const deselectAllBtn = document.getElementById('deselectAllBtn');
    const categoryBtn = document.getElementById('categoryBtn');
    const replaySpeed = document.getElementById('replaySpeed');

    // Pause/Resume recording
    pauseBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/toggle_pause', { method: 'POST' });
            const data = await response.json();
            showStatus(data.message);
            pauseBtn.textContent = data.is_paused ? 'Resume' : 'Pause';
        } catch (error) {
            showStatus('Error toggling pause: ' + error, true);
        }
    });

    // Export recordings
    exportBtn.addEventListener('click', async () => {
        const selectedRecordings = Array.from(document.querySelectorAll('.recording-item.selected'))
            .map(item => item.textContent);
        
        if (!selectedRecordings.length) {
            showStatus('No recordings selected for export', true);
            return;
        }

        try {
            const response = await fetch('/export_recordings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ recordings: selectedRecordings })
            });
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'recordings_export.json';
            a.click();
        } catch (error) {
            showStatus('Error exporting recordings: ' + error, true);
        }
    });

    // Import recordings
    importBtn.addEventListener('click', () => importInput.click());
    importInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/import_recordings', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            showStatus(data.message);
            await updateRecordingsList();
        } catch (error) {
            showStatus('Error importing recordings: ' + error, true);
        }
    });

    // Search and filter
    searchInput.addEventListener('input', filterRecordings);
    categoryFilter.addEventListener('change', filterRecordings);

    function filterRecordings() {
        const searchText = searchInput.value.toLowerCase();
        const category = categoryFilter.value;
        
        document.querySelectorAll('.recording-item').forEach(item => {
            const matchesSearch = item.textContent.toLowerCase().includes(searchText);
            const matchesCategory = !category || item.dataset.category === category;
            item.style.display = matchesSearch && matchesCategory ? '' : 'none';
        });
    }

    // Batch operations
    selectAllBtn.addEventListener('click', () => {
        document.querySelectorAll('.recording-item:not([style*="display: none"])')
            .forEach(item => item.classList.add('selected'));
        updateButtonStates();
    });

    deselectAllBtn.addEventListener('click', () => {
        document.querySelectorAll('.recording-item.selected')
            .forEach(item => item.classList.remove('selected'));
        updateButtonStates();
    });

    categoryBtn.addEventListener('click', async () => {
        const selectedRecordings = Array.from(document.querySelectorAll('.recording-item.selected'))
            .map(item => item.textContent);
        
        if (!selectedRecordings.length) {
            showStatus('No recordings selected', true);
            return;
        }

        const category = prompt('Enter category name:');
        if (!category) return;

        try {
            const response = await fetch('/set_category', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    recordings: selectedRecordings,
                    category: category
                })
            });
            const data = await response.json();
            showStatus(data.message);
            await updateRecordingsList();
        } catch (error) {
            showStatus('Error setting category: ' + error, true);
        }
    });

    // Update replay options when starting replay
    replayBtn.addEventListener('click', async () => {
        // ...existing replay code...
        const speed = parseFloat(replaySpeed.value);
        const data = {
            recording: selectedRecording.textContent,
            precision: document.getElementById('precisionMode').checked,
            loop_count: parseInt(document.getElementById('loopCount').value),
            speed: speed
        };
        // ...rest of replay code...
    });

    // ...existing code...
});
