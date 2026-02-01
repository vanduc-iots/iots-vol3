from flask import Flask, request, jsonify, render_template, redirect
from app import generate_Content
import logging
import os

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.template_folder = os.path.join(os.path.dirname(__file__), "../templates")
app.static_folder = os.path.join(os.path.dirname(__file__), "../static")

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/introduction", methods=["GET"])
def introduction():
    return render_template("introduction.html")

@app.route("/bot", methods=["POST"])
def botController():
    req: dict = request.get_json()
    message = req.get("message", None)
    attchment = req.get('attchment', None)

    response = generate_Content(prompt=message, attchment=attchment) or "Xảy ra lỗi. Tôi là CHATBOT."
    app.logger.info("model message")
    return jsonify({
        "model": response
    }), 200

# Vercel expects the Flask app to be named 'app'