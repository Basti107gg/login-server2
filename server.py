from flask import Flask, request, jsonify, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY_CHANGE_ME"

DB_FILE = "accounts.json"


# =========================
# INIT DB
# =========================
def load_accounts():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_accounts(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# ROOT
# =========================
@app.route("/")
def home():
    return "🚆 Server läuft"


# =========================
# LOGIN API (PROGRAMME)
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
# ADMIN LOGIN
# =========================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        pw = request.form.get("password")

        if pw == "ADMIN123":   # 🔥 dein Admin Passwort
            session["admin"] = True
            return redirect("/admin")

        return "❌ Falsches Passwort"

    return """
    <h2>Admin Login</h2>
    <form method="post">
        <input name="password" type="password">
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

    # ================= CREATE ACCOUNT
    if request.method == "POST" and "create" in request.form:
        user = request.form.get("username")
        pw = request.form.get("password")

        accounts[user] = {
            "password": pw,
            "permissions": []
        }

        save_accounts(accounts)

    # ================= DELETE ACCOUNT
    if request.method == "POST" and "delete" in request.form:
        user = request.form.get("delete")
        if user in accounts:
            del accounts[user]
            save_accounts(accounts)

    # ================= ADD PERMISSION
    if request.method == "POST" and "add_perm" in request.form:
        user = request.form.get("user_perm")
        perm = request.form.get("perm")

        if user in accounts:
            if "permissions" not in accounts[user]:
                accounts[user]["permissions"] = []

            if perm not in accounts[user]["permissions"]:
                accounts[user]["permissions"].append(perm)

            save_accounts(accounts)

    # ================= HTML PANEL
    return """
    <h1>ADMIN PANEL 🚆</h1>

    <a href="/logout">Logout</a>

    <hr>

    <h2>➕ Account erstellen</h2>
    <form method="post">
        <input name="username" placeholder="User">
        <input name="password" placeholder="Passwort">
        <button name="create">Erstellen</button>
    </form>

    <hr>

    <h2>🗑 Account löschen</h2>
    <form method="post">
        <input name="delete" placeholder="User">
        <button>Löschen</button>
    </form>

    <hr>

    <h2>🔐 Permission hinzufügen</h2>
    <form method="post">
        <input name="user_perm" placeholder="User">
        <input name="perm" placeholder="z.B. fahrplan_editor">
        <button name="add_perm">Hinzufügen</button>
    </form>

    <hr>

    <h2>📦 Accounts</h2>
    """ + "".join([
        f"<p><b>{u}</b> → {a.get('permissions', [])}</p>"
        for u, a in accounts.items()
    ])


# =========================
# RUN (RAILWAY SAFE)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
