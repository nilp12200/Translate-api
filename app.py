
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    res = requests.post("https://libretranslate.de/translate", json=data)
    return jsonify(res.json())

@app.route("/")
def home():
    return "LibreTranslate proxy is running!"
