from flask import Flask, request, jsonify, render_template_string, redirect, session
import json, os, shutil

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "MEGA_SECRET_KEY_123456")

DB_FILE = "accounts.json"
BACKUP_FILE = "accounts_backup.json"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "29a10C00")


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
        return {}

def save_accounts(data):
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# LOGIN API
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
# HOME
# =========================
@app.route("/")
def home():
    return redirect("/admin-login")


# =========================
# ADMIN LOGIN
# =========================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
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
# ADMIN PANEL
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect("/admin-login")

    accounts = load_accounts()

    # CREATE
    if request.method == "POST" and "create" in request.form:
        user = request.form.get("username")
        pw = request.form.get("password")

        if user and pw:
            accounts[user] = {
                "password": pw,
                "permissions": []
            }
            save_accounts(accounts)

    # DELETE
    if request.method == "POST" and "delete" in request.form:
        user = request.form.get("delete")
        if user in accounts:
            del accounts[user]
            save_accounts(accounts)

    # TOGGLE PERMISSION
    if request.method == "POST" and "toggle" in request.form:
        user = request.form.get("user")
        perm = request.form.get("perm")

        if user in accounts:
            if perm in accounts[user]["permissions"]:
                accounts[user]["permissions"].remove(perm)
            else:
                accounts[user]["permissions"].append(perm)

            save_accounts(accounts)


    return render_template_string("""
    <h1>🛠 ADMIN PANEL</h1>

    <a href="/logout">Logout</a>

    <hr>

    <h2>➕ Account erstellen</h2>
    <form method="post">
        <input name="username" placeholder="Username"><br>
        <input name="password" placeholder="Passwort"><br><br>
        <button name="create">Erstellen</button>
    </form>

    <hr>

    <h2>🗑 Account löschen</h2>
    <form method="post">
        <input name="delete" placeholder="Username">
        <button>Löschen</button>
    </form>

    <hr>

    <h2>📦 Accounts</h2>

    {% for user, data in accounts.items() %}
        <div style="border:1px solid #ccc; padding:10px; margin:10px;">
            <b>{{user}}</b><br>
            Passwort: {{data["password"]}}<br>
            Rechte: {{data.get("permissions", [])}}

            <br><br>

            <!-- Fahrplan Editor -->
            <form method="post" style="display:inline;">
                <input type="hidden" name="user" value="{{user}}">
                <input type="hidden" name="perm" value="fahrplan_editor">
                <button name="toggle">Fahrplan Editor</button>
            </form>

            <!-- Fahrpläne -->
            <form method="post" style="display:inline;">
                <input type="hidden" name="user" value="{{user}}">
                <input type="hidden" name="perm" value="fahrplaene">
                <button name="toggle">Fahrpläne</button>
            </form>

            <!-- Delete -->
            <form method="post" style="display:inline;">
                <form method="post">
                    <input type="hidden" name="delete" value="{{user}}">
                    <button>Löschen</button>
                </form>
            </form>

        </div>
    {% endfor %}
    """, accounts=accounts)


# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
