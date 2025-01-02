import os
import sys
import threading
import json
from flask import Flask, render_template, jsonify, request, Response, send_file
from werkzeug.utils import secure_filename

# Import PreciseActionRecorder based on platform
if sys.platform == 'win32':
    from new_ import PreciseActionRecorder
else:
    # Only use virtual display on non-Windows systems
    from pyvirtualdisplay import Display
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    from new_ import PreciseActionRecorder

app = Flask(__name__, template_folder='templates')
recorder = PreciseActionRecorder()

@app.route('/')
def index():
    """Render the main page with initial recordings list"""
    recordings = recorder.list_recordings()
    return render_template('index.html', recordings=recordings)

@app.route('/start_button', methods=['POST'])
def start_button():
    """Handle start recording button"""
    try:
        if not recorder.recording:
            # Start recording in a non-blocking thread
            recording_thread = threading.Thread(target=recorder.start_recording)
            recording_thread.daemon = True
            recording_thread.start()
            return jsonify({
                'status': 'success',
                'message': 'Recording started',
                'is_recording': True
            })
        return jsonify({
            'status': 'error',
            'message': 'Recording already in progress'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stop_button', methods=['POST'])
def stop_button():
    """Handle stop recording button"""
    try:
        if recorder.recording:
            log_file = recorder.stop_recording()
            return jsonify({
                'status': 'success',
                'message': 'Recording stopped and saved',
                'file': log_file,
                'is_recording': False
            })
        return jsonify({
            'status': 'error',
            'message': 'No recording in progress'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/refresh_button', methods=['GET'])
def refresh_button():
    """Handle refresh list button"""
    try:
        recordings = recorder.list_recordings()
        return jsonify({
            'status': 'success',
            'recordings': recordings,
            'message': 'Recordings list refreshed'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/replay_button', methods=['POST'])
def replay_button():
    """Handle replay selected recording button"""
    try:
        data = request.json
        recording = data.get('recording')
        precision = data.get('precision', True)
        loop_count = int(data.get('loop_count', 1))

        if not recording:
            return jsonify({
                'status': 'error',
                'message': 'No recording selected'
            })

        if loop_count < 1 or loop_count > 10:
            return jsonify({
                'status': 'error',
                'message': 'Loop count must be between 1 and 10'
            })

        log_path = os.path.join(recorder.log_dir, recording)
        
        # Start replay in a non-blocking thread
        replay_thread = threading.Thread(
            target=recorder.replay_events,
            args=(log_path, precision, None, loop_count)
        )
        replay_thread.daemon = True
        replay_thread.start()

        return jsonify({
            'status': 'success',
            'message': 'Replay started'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/delete_button', methods=['POST'])
def delete_button():
    """Handle delete selected recordings button"""
    try:
        data = request.json
        recordings = data.get('recordings', [])

        if not recordings:
            return jsonify({
                'status': 'error',
                'message': 'No recordings selected for deletion'
            })

        deleted = []
        failed = []

        for recording in recordings:
            try:
                file_path = os.path.join(recorder.log_dir, recording)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted.append(recording)
                else:
                    failed.append(recording)
            except Exception as e:
                failed.append(recording)
                print(f"Error deleting {recording}: {e}")

        if failed:
            status = 'warning'
            message = f"Deleted {len(deleted)} recording(s). Failed to delete {len(failed)} recording(s)."
        else:
            status = 'success'
            message = f"Successfully deleted {len(deleted)} recording(s)."

        return jsonify({
            'status': status,
            'message': message,
            'deleted': deleted,
            'failed': failed
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/get_recording_status', methods=['GET'])
def get_recording_status():
    """Get current recording status"""
    return jsonify({
        'is_recording': recorder.recording,
        'is_paused': recorder.paused
    })

@app.route('/start_recording', methods=['POST'])
def start_recording():
    try:
        # Start recording in a non-blocking way
        recorder.start_recording()
        return jsonify({'status': 'success', 'message': 'Recording started'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    try:
        log_file = recorder.stop_recording()
        return jsonify({'status': 'success', 'message': 'Recording stopped', 'file': log_file})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/list_recordings', methods=['GET'])
def list_recordings():
    try:
        recordings = recorder.list_recordings()
        return jsonify({'status': 'success', 'recordings': recordings})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/replay', methods=['POST'])
def replay():
    try:
        data = request.json
        recording = data['recording']
        precision = data['precision']
        loop_count = int(data['loop_count'])
        
        # Validate loop count
        if loop_count < 1 or loop_count > 10:
            return jsonify({'status': 'error', 'message': 'Loop count must be between 1 and 10'})
        
        log_path = os.path.join(recorder.log_dir, recording)
        recorder.replay_events(log_path, precision_mode=precision, loop_count=loop_count)
        return jsonify({'status': 'success', 'message': 'Replay completed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/delete_recordings', methods=['POST'])
def delete_recordings():
    try:
        data = request.json
        recordings = data['recordings']
        deleted = []
        failed = []

        for recording in recordings:
            try:
                file_path = os.path.join(recorder.log_dir, recording)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted.append(recording)
                else:
                    failed.append(recording)
            except Exception as e:
                failed.append(recording)
                print(f"Error deleting {recording}: {e}")

        if failed:
            message = f"Deleted {len(deleted)} recording(s). Failed to delete {len(failed)} recording(s)."
            status = 'warning'
        else:
            message = f"Successfully deleted {len(deleted)} recording(s)."
            status = 'success'

        return jsonify({
            'status': status,
            'message': message,
            'deleted': deleted,
            'failed': failed
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# New routes
@app.route('/toggle_pause', methods=['POST'])
def toggle_pause():
    try:
        if recorder.recording:
            if recorder.paused:
                recorder.resume_recording()
                return jsonify({
                    'status': 'success',
                    'message': 'Recording resumed',
                    'is_paused': False
                })
            else:
                recorder.pause_recording()
                return jsonify({
                    'status': 'success',
                    'message': 'Recording paused',
                    'is_paused': True
                })
        return jsonify({
            'status': 'error',
            'message': 'No recording in progress'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/export_recordings', methods=['POST'])
def export_recordings():
    try:
        data = request.json
        recordings = data['recordings']
        export_data = {}

        for recording in recordings:
            file_path = os.path.join(recorder.log_dir, recording)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    export_data[recording] = json.load(f)

        temp_file = os.path.join(recorder.log_dir, 'temp_export.json')
        with open(temp_file, 'w') as f:
            json.dump(export_data, f)

        return send_file(
            temp_file,
            mimetype='application/json',
            as_attachment=True,
            download_name='recordings_export.json'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/import_recordings', methods=['POST'])
def import_recordings():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'})

        file = request.files['file']
        if not file.filename.endswith('.json'):
            return jsonify({'status': 'error', 'message': 'Invalid file type'})

        import_data = json.loads(file.read())
        imported = 0

        for filename, data in import_data.items():
            safe_filename = secure_filename(filename)
            file_path = os.path.join(recorder.log_dir, safe_filename)
            with open(file_path, 'w') as f:
                json.dump(data, f)
        recordings = recorder.list_recordings()
        return jsonify({'status': 'success', 'message': 'Recordings imported successfully', 'recordings': recordings})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/delete_recording', methods=['POST'])
def delete_recording():
    """Handle delete selected recording button"""
    try:
        data = request.json
        recording = data.get('recording')

        if not recording:
            return jsonify({
                'status': 'error',
                'message': 'No recording selected for deletion'
            })

        file_path = os.path.join(recorder.log_dir, recording)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({
                'status': 'success',
                'message': f'Recording {recording} deleted successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Recording not found'
            })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', debug=True)
    finally:
        if sys.platform != 'win32':
            display.stop()