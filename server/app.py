import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from .object_detection import ObjectDetector
from .utils import setup_logging

# Setup Flask and SocketIO
app = Flask(__name__, 
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup logging
logger = setup_logging()

# Initialize object detector
model_path = os.path.abspath('models/ppe.pt')
detector = ObjectDetector(model_path)

@app.route('/')
def index():
    logger.info("Serving the index page.")
    return render_template('index.html')

@app.route('/about')
def about():
    logger.info("Serving the about page.")
    return render_template('about.html')

@app.route('/settings')
def settings():
    logger.info("Serving the settings page.")
    return render_template('settings.html')

@socketio.on('frame')
def handle_frame(data):
    try:
        detections, stats = detector.process_frame(data)
        socketio.emit('detection_results', {'detections': detections, 'stats': stats})
        logger.debug("Processed frame and sent detection results.")
    except Exception as e:
        logger.error(f"Error processing frame: {e}")

@app.route('/update_settings', methods=['POST'])
def update_settings():
    try:
        new_settings = request.json
        detector.update_settings(new_settings)
        return jsonify({"status": "success", "message": "Settings updated successfully"})
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    logger.info("Starting the Flask server...")
    socketio.run(app, debug=True)
