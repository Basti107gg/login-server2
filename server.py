# server.py
from flask import Flask, request, jsonify, render_template_string, redirect, session
import json
import os
import shutil

app = Flask(__name__)
app.secret_key = "MEGA_SECRET_KEY_123456"  # wichtig für login speichern

DB_FILE = "accounts.json"
BACKUP_FILE = "accounts_backup.json"

ADMIN_PASSWORD = "29a10C00"

# =========================
# LOAD / SAVE
# =========================
def load_accounts():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, "r") as f:
                return json.load(f)
        return {}

def save_accounts(data):
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
        f.flush()
        os.fsync(f.fileno())

# =========================
# LOGIN API (für Programme)
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = data.get("username")
    pw = data.get("password")

    accounts = load_accounts()

    if user in accounts and accounts[user] == pw:
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"})

# =========================
# ADMIN LOGIN (MIT SESSION)
# =========================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True   # 🔥 gespeichert
            return redirect("/admin")
        return "❌ Falsches Passwort"

    return """
    <h2>🔒 Admin Login</h2>
    <form method="post">
        <input type="password" name="password">
        <button>Login</button>
    </form>
    """

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin-login")

# =========================
# ADMIN PANEL (GESCHÜTZT)
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # 🔒 Zugriff prüfen
    if not session.get("admin"):
        return redirect("/admin-login")

    accounts = load_accounts()

    if request.method == "POST" and "create" in request.form:
        user = request.form.get("username")
        pw = request.form.get("password")

        if user and pw:
            accounts[user] = pw
            save_accounts(accounts)

    if request.method == "POST" and "delete" in request.form:
        user = request.form.get("delete")
        if user in accounts:
            del accounts[user]
            save_accounts(accounts)

    return render_template_string("""
    <h1>ADMIN PANEL</h1>

    <a href="/logout">🔓 Logout</a>

    <h2>➕ Account erstellen</h2>
    <form method="post">
        <input name="username"><br><br>
        <input name="password"><br><br>
        <button name="create">Erstellen</button>
    </form>

    <hr>

    <h2>🗑 Account löschen</h2>
    <form method="post">
        <input name="delete">
        <button>Löschen</button>
    </form>

    <hr>

    <h2>📦 Accounts</h2>

    <ul>
    {% for user, pw in accounts.items() %}
        <li onclick="toggle('{{user}}')" style="cursor:pointer;">
            <b>{{user}}</b>
            <div id="{{user}}" style="display:none; margin-left:20px;">
                Passwort: {{pw}}
            </div>
        </li>
    {% endfor %}
    </ul>

    <script>
    function toggle(user){
        let el = document.getElementById(user);
        el.style.display = (el.style.display === "none") ? "block" : "none";
    }
    </script>
    """, accounts=accounts)

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return redirect("/admin")

# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
