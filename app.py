import os
import threading
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import bot as bot_module

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cambia-questa-chiave")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["auth"] = True
            return redirect(url_for("index"))
        return render_template("index.html", error="Password errata", logged=False)
    return render_template("index.html", logged=False)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    if not session.get("auth"):
        return redirect(url_for("login"))
    cfg = bot_module.load_config()
    return render_template("index.html", cfg=cfg, logged=True)


@app.route("/save", methods=["POST"])
def save():
    if not session.get("auth"):
        return jsonify({"ok": False, "error": "non autorizzato"}), 401

    cfg = bot_module.load_config()

    cfg["enabled"] = request.form.get("enabled") == "on"

    try:
        cfg["priority_user_id"] = int(request.form.get("priority_user_id", "0").strip() or "0")
    except ValueError:
        return jsonify({"ok": False, "error": "ID priorita' non valido"}), 400

    raw_blocked = request.form.get("blocked_user_ids", "")
    blocked = []
    for line in raw_blocked.replace(",", "\n").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            blocked.append(int(line))
        except ValueError:
            return jsonify({"ok": False, "error": f"ID bloccato non valido: {line}"}), 400
    cfg["blocked_user_ids"] = blocked

    bot_module.save_config(cfg)
    return redirect(url_for("index"))


def start_bot_thread():
    t = threading.Thread(target=bot_module.run_bot, daemon=True)
    t.start()


if __name__ == "__main__":
    start_bot_thread()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
