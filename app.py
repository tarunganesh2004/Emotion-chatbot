import logging
from flask import Flask, render_template, request, jsonify
from utils.emotion_detector import detect_emotion
from utils.chatbot import Chatbot
from utils.db_handler import DBHandler
from datetime import datetime
import base64
import numpy as np
import cv2

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
chatbot = Chatbot()
db_handler = DBHandler("db/chat.db")


@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/detect_emotion", methods=["POST"])
def detect_emotion_route():
    try:
        img_data = request.json["image"]
        img_bytes = base64.b64decode(img_data.split(",")[1])
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        emotion = detect_emotion(img)
        user_id = request.json.get("user_id", "anonymous")
        db_handler.log_emotion(user_id, emotion, datetime.now())
        return jsonify({"emotion": emotion})
    except Exception as e:
        logger.error(f"Emotion detection error: {str(e)}")
        return jsonify({"error": "Emotion detection failed"}), 400


@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json["message"]
        emotion = request.json.get("emotion", "neutral")
        user_id = request.json.get("user_id", "anonymous")
        response = chatbot.generate_response(user_input, emotion)
        db_handler.log_chat(user_id, user_input, response, emotion, datetime.now())
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": "Chat processing failed"}), 400


@app.route("/emotion_stats", methods=["GET"])
def emotion_stats():
    try:
        user_id = request.args.get("user_id", "anonymous")
        stats = db_handler.get_emotion_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Emotion stats error: {str(e)}")
        return jsonify({"error": "Failed to fetch stats"}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
