from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# =========================
# FILE DB
# =========================
DB_FILE = "accounts.json"

inbox = {}


# =========================
# LOAD ACCOUNTS
# =========================
def load_accounts():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

    with open(DB_FILE, "r") as f:
        return json.load(f)


# =========================
# ROOT (WICHTIG)
# =========================
@app.route("/")
def home():
    return "🚆 Railway Server läuft"


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
# SEND SYSTEM
# =========================
@app.route("/send", methods=["POST"])
def send():
    data = request.json

    to = data.get("to")
    frm = data.get("from")
    payload = data.get("payload")

    if not to:
        return {"status": "error"}

    if to not in inbox:
        inbox[to] = []

    inbox[to].append({
        "from": frm,
        "payload": payload
    })

    return {"status": "ok"}


# =========================
# INBOX
# =========================
@app.route("/inbox", methods=["POST"])
def get_inbox():
    user = request.json.get("username")

    return {
        "messages": inbox.get(user, [])
    }


# =========================
# RAILWAY START FIX
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
