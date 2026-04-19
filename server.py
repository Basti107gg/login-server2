from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DB_FILE = "accounts.json"

# =========================
# ACCOUNTS
# =========================
def load_accounts():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = data.get("username")
    pw = data.get("password")

    accounts = load_accounts()

    if user in accounts and accounts[user]["password"] == pw:
        return jsonify({
            "status": "ok",
            "permissions": accounts[user].get("permissions", [])
        })

    return jsonify({"status": "error"})


# =========================
# INBOX SYSTEM
# =========================
inbox = {}


@app.route("/send", methods=["POST"])
def send():
    data = request.json

    to = data.get("to")
    frm = data.get("from")
    payload = data.get("payload")

    if to not in inbox:
        inbox[to] = []

    inbox[to].append({
        "from": frm,
        "payload": payload
    })

    return {"status": "ok"}


@app.route("/inbox", methods=["POST"])
def get_inbox():
    user = request.json.get("username")

    return {
        "messages": inbox.get(user, [])
    }


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
