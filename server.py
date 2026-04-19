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
# ADMIN LOGIN
# =========================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        return "❌ Falsch"

    return """
    <h2>Admin Login</h2>
    <form method="post">
        <input type="password" name="password">
        <button>Login</button>
    </form>
    """


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin-login")


# =========================
# ADMIN PANEL (CLICK SYSTEM)
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
<!DOCTYPE html>
<html>
<head>
<title>Admin Panel</title>
<style>
body { font-family: Arial; }

.user {
    padding:10px;
    border:1px solid #ccc;
    margin:5px;
    cursor:pointer;
}

#popup {
    display:none;
    position:fixed;
    top:20%;
    left:30%;
    width:40%;
    background:white;
    border:2px solid black;
    padding:20px;
    z-index:1000;
}
</style>
</head>

<body>

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

<h2>👤 User Liste</h2>

{% for user, data in accounts.items() %}
    <div class="user" onclick="openUser('{{user}}','{{data['password']}}','{{data.get('permissions', [])}}')">
        {{user}}
    </div>
{% endfor %}

<!-- POPUP -->
<div id="popup">
    <h2 id="pu_user"></h2>

    <p><b>Passwort:</b> <span id="pu_pass"></span></p>
    <p><b>Rechte:</b> <span id="pu_perm"></span></p>

    <form method="post">
        <input type="hidden" name="user" id="form_user">

        <input type="hidden" name="perm" value="fahrplan_editor">
        <button name="toggle">Fahrplan Editor</button>
    </form>

    <form method="post">
        <input type="hidden" name="user" id="form_user2">

        <input type="hidden" name="perm" value="fahrplaene">
        <button name="toggle">Fahrpläne</button>
    </form>

    <form method="post">
        <input type="hidden" name="delete" id="form_delete">
        <button>Löschen</button>
    </form>

    <br>
    <button onclick="closePopup()">Schließen</button>
</div>

<script>
function openUser(user, pw, perm){
    document.getElementById("popup").style.display="block";

    document.getElementById("pu_user").innerText=user;
    document.getElementById("pu_pass").innerText=pw;
    document.getElementById("pu_perm").innerText=perm;

    document.getElementById("form_user").value=user;
    document.getElementById("form_user2").value=user;
    document.getElementById("form_delete").value=user;
}

function closePopup(){
    document.getElementById("popup").style.display="none";
}
</script>

</body>
</html>
""", accounts=accounts)


# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
