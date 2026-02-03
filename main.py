from flask import Flask, request, jsonify, render_template, redirect
from app import generate_Content
from app.services.call_esp8266 import light_control
import logging

_app = Flask(__name__)
_app.logger.setLevel(logging.INFO)
_app.template_folder = "templates"
_app.static_folder = "static"

@_app.route("/", methods = ["GET"])
def home():
    return render_template("home.html")

@_app.route("/introduction", methods = ["GET"])
def introduction():
    return render_template("introduction.html")

@_app.route("/toggle_led1", methods=["POST"])
def toggle_led1():
    result = light_control(status="toggle", led="1")
    return jsonify({"message": result["content"]})

@_app.route("/toggle_led2", methods=["POST"])
def toggle_led2():
    result = light_control(status="toggle", led="2")
    return jsonify({"message": result["content"]})

@_app.route("/control_all", methods=["POST"])
def control_all():
    action = request.args.get("action", "off")
    if action not in ["on", "off"]:
        action = "off"
    result = light_control(status=action, led="all")
    return jsonify({"message": result["content"]})
def botController():
    req: dict = request.get_json()
    message = req.get("message", None)
    attchment = req.get('attchment', None)

    response:str = generate_Content(prompt=message, attchment=attchment) or "Xảy ra lỗi. Tôi là CHATBOT."
    _app.logger.info("model message")
    return jsonify({
        "model": response
    }), 200


if __name__ == "__main__":
    _app.run(host="0.0.0.0", port=8080, debug=True)
    