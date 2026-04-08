from flask import Flask, request, jsonify
import json
import os

from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)

DATA_FILE = "data.json"
GOOGLE_CLIENT_ID = "YOUR_CLIENT_ID"

# 📦 データ読み込み
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}}, f)

    with open(DATA_FILE, "r") as f:
        return json.load(f)

# 💾 保存
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# 🔐 Register
@app.route("/register", methods=["POST"])
def register():
    data = load_data()
    username = request.json.get("username")

    if username in data["users"]:
        return jsonify({"msg": "User exists"})

    data["users"][username] = []
    save_data(data)

    return jsonify({"msg": "Registered"})

# 🔐 Login
@app.route("/login", methods=["POST"])
def login():
    data = load_data()
    username = request.json.get("username")

    if username in data["users"]:
        return jsonify({"msg": "Login success"})
    else:
        return jsonify({"msg": "User not found"})

# 🔥 Googleログイン
@app.route("/google-login", methods=["POST"])
def google_login():
    data = load_data()
    token = request.json.get("token")

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo["email"]

        if email not in data["users"]:
            data["users"][email] = []
            save_data(data)

        return jsonify({"username": email})

    except:
        return jsonify({"error": "Invalid token"}), 400

# 🤖 生成
@app.route("/generate", methods=["POST"])
def generate():
    data = load_data()

    username = request.json.get("username")
    agent = request.json.get("agent")

    result = f"{agent} result generated!"

    # 履歴保存
    if username in data["users"]:
        data["users"][username].append({
            "agent": agent,
            "result": result
        })
        save_data(data)

    return jsonify({"result": result})

# 📜 履歴取得
@app.route("/history", methods=["POST"])
def history():
    data = load_data()
    username = request.json.get("username")

    if username in data["users"]:
        return jsonify({"history": data["users"][username]})

    return jsonify({"history": []})

# 🚀 起動
if __name__ == "__main__":
    app.run(debug=True)
