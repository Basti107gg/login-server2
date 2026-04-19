from flask import Flask, request, jsonify, redirect, session, render_template_string
import json
import os

app = Flask(__name__)
app.secret_key = "CHANGE_ME_SECRET"

DB_FILE = "accounts.json"

ADMIN_PASSWORD = "29a10C00"


# =========================
# DATABASE
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
# PERMISSIONS LIST (WICHTIG)
# =========================
ALL_PERMISSIONS = [
    "fahrplan_editor",
    "fahrplan_view",
    "fahrplan_create",
    "fahrplan_delete",
    "fahrplan_send",
    "fahrplan_receive",
    "user_create",
    "user_delete",
    "user_permissions",
    "admin_panel",
    "system_export",
    "system_import",
    "system_settings"
]


# =========================
# ROOT
# =========================
@app.route("/")
def home():
    return "🚆 Server läuft"


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
    <h2>🔐 Admin Login</h2>
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

    # CREATE ACCOUNT
    if request.method == "POST" and "create" in request.form:
        user = request.form.get("username")
        pw = request.form.get("password")

        accounts[user] = {
            "password": pw,
            "permissions": []
        }

        save_accounts(accounts)

    # DELETE ACCOUNT
    if request.method == "POST" and "delete" in request.form:
        user = request.form.get("delete")
        if user in accounts:
            del accounts[user]
            save_accounts(accounts)

    return render_template_string("""
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

    <h2>🗑 Accounts</h2>

    <ul>
    {% for u, a in accounts.items() %}
        <li>
            <b>{{u}}</b>
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
    <div id="permWindow" style="display:none; position:fixed; top:10%; left:30%; background:white; border:1px solid black; padding:20px;">
        <h3>Permissions für <span id="userName"></span></h3>

        <form method="post" id="permForm">
            <input type="hidden" name="user" id="permUser">

            {% for p in perms %}
                <div>
                    <input type="checkbox" name="perm" value="{{p}}" id="{{p}}">
                    <label for="{{p}}">{{p}}</label>
                </div>
            {% endfor %}

            <br>
            <button name="save_perms">Speichern</button>
        </form>

        <button onclick="closePerm()">Schließen</button>
    </div>

    <script>
    function openPerm(user){
        document.getElementById("permWindow").style.display = "block";
        document.getElementById("userName").innerText = user;
        document.getElementById("permUser").value = user;

        // Reset checkboxes
        document.querySelectorAll("input[type=checkbox]").forEach(cb => cb.checked = false);
    }

    function closePerm(){
        document.getElementById("permWindow").style.display = "none";
    }
    </script>
    """, accounts=accounts, perms=ALL_PERMISSIONS)


# =========================
# SAVE PERMISSIONS
# =========================
@app.route("/admin", methods=["POST"])
def save_permissions():
    if not session.get("admin"):
        return redirect("/admin-login")

    accounts = load_accounts()

    if "save_perms" in request.form:
        user = request.form.get("user")
        perms = request.form.getlist("perm")

        if user in accounts:
            accounts[user]["permissions"] = perms
            save_accounts(accounts)

    return redirect("/admin")


# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
