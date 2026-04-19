from flask import Flask, request, jsonify, redirect, session, render_template_string
import json
import os

app = Flask(__name__)
app.secret_key = "CHANGE_ME_SECRET"

DB_FILE = "accounts.json"

ADMIN_PASSWORD = "29a10C00"


# =========================
# DB
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
    <h2>Admin Login</h2>
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

    # ➕ CREATE USER
    if request.method == "POST" and "create" in request.form:
        user = request.form.get("username")
        pw = request.form.get("password")

        if user and pw:
            accounts[user] = {
                "password": pw,
                "permissions": []
            }
            save_accounts(accounts)

    # 🗑 DELETE USER
    if request.method == "POST" and "delete" in request.form:
        user = request.form.get("delete")
        if user in accounts:
            del accounts[user]
            save_accounts(accounts)

    # 🔐 SAVE PERMISSIONS (FIXED)
    if request.method == "POST" and "save_perms" in request.form:
        user = request.form.get("user")
        perms = request.form.getlist("perm")  # ✔ FIX: LISTE

        if user in accounts:
            accounts[user]["permissions"] = perms
            save_accounts(accounts)

    return render_template_string("""
    <h1>ADMIN PANEL 🚆</h1>

    <a href="/logout">Logout</a>

    <hr>

    <h2>➕ User erstellen</h2>
    <form method="post">
        <input name="username" placeholder="User">
        <input name="password" placeholder="Passwort">
        <button name="create">Erstellen</button>
    </form>

    <hr>

    <h2>👤 Users</h2>

    <ul>
    {% for u, a in accounts.items() %}
        <li>
            <b>{{u}}</b> → {{a.get("permissions", [])}}

            <button onclick="openPerm('{{u}}')">Permissions</button>

            <form method="post" style="display:inline;">
                <input type="hidden" name="delete" value="{{u}}">
                <button>Löschen</button>
            </form>
        </li>
    {% endfor %}
    </ul>

    <!-- =========================
         PERMISSION WINDOW
    ========================== -->
    <div id="permWin" style="display:none; position:fixed; top:20%; left:35%; background:white; padding:20px; border:1px solid black;">
        <h3>Permissions</h3>

        <form method="post">
            <input type="hidden" name="user" id="userField">

            <input type="checkbox" name="perm" value="Fahrplan_Editor"> Fahrplan_Editor<br>
            <input type="checkbox" name="perm" value="Fahrpläne"> Fahrpläne<br>

            <br>
            <button name="save_perms">Speichern</button>
        </form>

        <button onclick="closeWin()">Schließen</button>
    </div>

    <script>
    function openPerm(user){
        document.getElementById("permWin").style.display = "block";
        document.getElementById("userField").value = user;

        // reset checkboxes
        document.querySelectorAll("input[type=checkbox]").forEach(c => c.checked = false);
    }

    function closeWin(){
        document.getElementById("permWin").style.display = "none";
    }
    </script>
    """, accounts=accounts)


# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
