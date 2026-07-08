# app.py

import json
import os

from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

from ai_select import (
    AI_SELECT_SCHEMA,
    build_parts,
    parse_plan,
)

from prompt_engine import build_prompt

from service_rules import (
    recommend_request,
    prompt_request,
)

app = Flask(__name__)

APP_NAME = "Movie_AI"
APP_BRAND = "One Tap Cinema"
APP_TAGLINE = "指先から、まるで映画のような動画を。"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {
        "status": "running",
        "app": APP_NAME,
        "brand": APP_BRAND,
        "tagline": APP_TAGLINE,
        "gemini_key": bool(GEMINI_API_KEY),
        "gemini_model": GEMINI_MODEL,
    }


def get_uploaded_images():

    photo1 = request.files.get("photo1")
    photo2 = request.files.get("photo2")

    if not photo1:
        return None, None, "画像①を選んでください。"

    return photo1, photo2, None


@app.route("/recommend", methods=["POST"])
def recommend():

    if not client:
        return jsonify({"error": "GEMINI_API_KEY is not set."}), 500

    photo1, photo2, error = get_uploaded_images()

    if error:
        return jsonify({"error": error}), 400

    romance_mode = request.form.get("romanceMode", "off")
    romance_level = request.form.get("romanceLevel", "soft")

    try:

        parts = build_parts(
            photo1.read(),
            photo1.mimetype,
            photo2.read() if photo2 else None,
            photo2.mimetype if photo2 else None,
            romance_mode,
            romance_level,
        )

        response = recommend_request(
            client,
            GEMINI_MODEL,
            parts,
            AI_SELECT_SCHEMA,
        )

        return jsonify({
            "plan": parse_plan(response)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate", methods=["POST"])
def generate():

    if not client:
        return jsonify({"error": "GEMINI_API_KEY is not set."}), 500

    photo1, photo2, error = get_uploaded_images()

    if error:
        return jsonify({"error": error}), 400

    plan_json = request.form.get("plan")

    if not plan_json:
        return jsonify({
            "error": "AI Planがありません。"
        }), 400

    try:

        plan = json.loads(plan_json)

        parts = [
            types.Part.from_text(
                text=build_prompt(plan)
            ),
            types.Part.from_bytes(
                data=photo1.read(),
                mime_type=photo1.mimetype,
            ),
        ]

        if photo2:
            parts.append(
                types.Part.from_bytes(
                    data=photo2.read(),
                    mime_type=photo2.mimetype,
                )
            )

        response = prompt_request(
            client,
            GEMINI_MODEL,
            parts,
        )

        return jsonify({
            "prompt": response.text.strip()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/<path:path>")
def catch_all(path):
    return render_template("index.html")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
