import json
import os

from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

app = Flask(__name__)

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
        "app": "Movie_AI",
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
        photo1_bytes = photo1.read()
        photo2_bytes = photo2.read() if photo2 else None

        parts = [
            types.Part.from_text(
                text=f"""
You are Movie_AI's AI Select engine.

Analyze the uploaded image or images and create the best AI video plan.

Detect the subject type:
person, couple, pet, car, motorcycle, illustration, original_character, scenery, product, or other.

User romance setting:
romance_mode: {romance_mode}
romance_level: {romance_level}

Rules:
- If romance_mode is off, romance must be "none".
- If romance_mode is on, choose an elegant, cinematic, non-explicit romantic action only when appropriate.
- If the image is a car, motorcycle, pet, illustration, product, scenery, or other non-human subject, romance must be "none".
- Choose a simple, high-impact video concept.
- service should usually be "Kling".
- confidence must be a number from 1 to 5.
- reason_ja must be short Japanese text.
"""
            ),
            types.Part.from_bytes(
                data=photo1_bytes,
                mime_type=photo1.mimetype or "image/jpeg",
            ),
        ]

        if photo2_bytes:
            parts.append(
                types.Part.from_bytes(
                    data=photo2_bytes,
                    mime_type=photo2.mimetype or "image/jpeg",
                )
            )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=parts,
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.4,
                top_p=0.9,
                max_output_tokens=1000,
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "subject_type": {"type": "string"},
                        "scene": {"type": "string"},
                        "mood": {"type": "string"},
                        "romance": {"type": "string"},
                        "camera": {"type": "string"},
                        "time": {"type": "string"},
                        "style": {"type": "string"},
                        "service": {"type": "string"},
                        "reason_ja": {"type": "string"},
                        "confidence": {"type": "number"},
                    },
                    "required": [
                        "subject_type",
                        "scene",
                        "mood",
                        "romance",
                        "camera",
                        "time",
                        "style",
                        "service",
                        "reason_ja",
                        "confidence",
                    ],
                },
            ),
        )

        if not response.text:
            return jsonify({"error": "AI Selectから返答がありませんでした。"}), 500

        plan = json.loads(response.text)
        return jsonify({"plan": plan})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def build_romance_instruction(romance):
    romance_map = {
        "none": "No romance. Do not describe romantic tension, dating energy, holding hands, hugging, kissing, flirting, or couple-like behavior.",
        "holding hands": "The two people gently hold hands in a natural romantic way.",
        "warm hug": "The two people share a warm, emotional hug, cinematic and elegant.",
        "gentle kiss": "The two people share a gentle romantic movie-style kiss, elegant and non-explicit.",
        "forehead kiss": "One person gently kisses the other on the forehead in a soft romantic moment.",
        "looking into each other's eyes": "The two people look deeply into each other's eyes with emotional romantic tension.",
        "proposal": "A romantic proposal moment with emotional eye contact and elegant body language.",
        "dancing together": "The two people dance together slowly and romantically.",
        "embracing in the rain": "The two people embrace emotionally in soft rain, cinematic and elegant.",
    }

    return romance_map.get(romance, romance_map["none"])


@app.route("/generate", methods=["POST"])
def generate():
    if not client:
        return jsonify({"error": "GEMINI_API_KEY is not set."}), 500

    photo1, photo2, error = get_uploaded_images()
    if error:
        return jsonify({"error": error}), 400

    plan_json = request.form.get("plan", "")

    if not plan_json:
        return jsonify({"error": "AI Planがありません。先にAI Selectを実行してください。"}), 400

    try:
        plan = json.loads(plan_json)

        photo1_bytes = photo1.read()
        photo2_bytes = photo2.read() if photo2 else None

        romance = plan.get("romance", "none")
        service = plan.get("service", "Kling")

        parts = [
            types.Part.from_text(
                text=f"""
You are Movie_AI, a professional AI video director and prompt engineer.

Create one polished English prompt for {service} image-to-video generation.

Use this AI Plan:
{json.dumps(plan, ensure_ascii=False)}

Romance instruction:
{build_romance_instruction(romance)}

Output format:
Use exactly this structure:

SUBJECT:
Describe the visible subject or subjects based on the uploaded image.

SCENE:
Describe the selected scene from the AI Plan.

ACTION:
Describe what happens in the 5 to 10 second video.

ROMANCE:
Describe the romance setting. If romance is none, clearly state there is no romantic behavior.

CAMERA:
Describe the camera movement from the AI Plan.

LIGHTING:
Describe lighting, color, weather, and atmosphere.

MOTION:
Describe realistic motion details.

QUALITY:
Ultra-realistic, high-detail, cinematic video quality.

NEGATIVE PROMPT:
Avoid distorted faces, identity change, extra fingers, bad hands, warped hands, deformed body, duplicated people, unnatural anatomy, blurry faces, low quality, artifacts, flickering, unrealistic motion, strange eye movement, broken limbs, inconsistent clothing, explicit content, and sexual content.

Rules:
- Keep identity and visible appearance consistent with the uploaded image.
- Do not invent impossible details.
- Make it ready to paste directly into {service}.
- Output only the final English prompt.
"""
            ),
            types.Part.from_bytes(
                data=photo1_bytes,
                mime_type=photo1.mimetype or "image/jpeg",
            ),
        ]

        if photo2_bytes:
            parts.append(
                types.Part.from_bytes(
                    data=photo2_bytes,
                    mime_type=photo2.mimetype or "image/jpeg",
                )
            )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=parts,
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.75,
                top_p=0.95,
                max_output_tokens=2200,
            ),
        )

        if not response.text:
            return jsonify({"error": "Geminiから返答がありませんでした。"}), 500

        return jsonify({"prompt": response.text.strip()})

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
