import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from agent import build_email_crew

load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/draft", methods=["POST"])
def draft_email():
    data = request.get_json(silent=True) or {}

    context = (data.get("context") or "").strip()
    tone = (data.get("tone") or "professional and friendly").strip()
    recipient = (data.get("recipient") or "the recipient").strip()

    if not context:
        return jsonify({"error": "Please describe what the email should be about."}), 400

    try:
        email = build_email_crew(context, tone, recipient)
        return jsonify({"email": email})
    except Exception as exc:
        return jsonify({"error": f"Failed to draft email: {exc}"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5005))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
