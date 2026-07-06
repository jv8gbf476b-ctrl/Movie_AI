import base64
import json
import os
import urllib.error
import urllib.request

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"


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


@app.route("/generate", methods=["POST"])
def generate():
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY is not set."}), 500

    photo1 = request.files.get("photo1")
    photo2 = request.files.get("photo2")
    scene = request.form.get("scene", "")
    mood = request.form.get("mood", "")
    service = request.form.get("service", "Kling")

    if not photo1 or not photo2:
        return jsonify({"error": "写真を2枚選んでください。"}), 400

    image1_data = base64.b64encode(photo1.read()).decode("utf-8")
    image2_data = base64.b64encode(photo2.read()).decode("utf-8")

    prompt_text = f"""
You are Movie_AI, a professional AI video director.

Analyze the two uploaded reference photos carefully.
Create one polished English prompt for {service} image-to-video generation.

Selected scene:
{scene}

Selected mood:
{mood}

Write the final prompt with:
- A natural description of both people based on the photos
- Their expressions, clothing, pose, and relationship-like interaction
- A cinematic 5 to 10 second scene
- Realistic motion
- Camera movement
- Lighting
- Background
- Atmosphere
- Negative instructions to avoid face distortion, extra fingers, warped hands, identity changes, strange bodies, and unnatural motion

Important:
Keep both identities consistent with the reference photos.
Make the two people appear naturally together in the same scene.
Output only the final English prompt.
"""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt_text},
                    {
                        "inline_data": {
                            "mime_type": photo1.mimetype or "image/jpeg",
                            "data": image1_data,
                        }
                    },
                    {
                        "inline_data": {
                            "mime_type": photo2.mimetype or "image/jpeg",
                            "data": image2_data,
                        }
                    },
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.8,
            "topP": 0.95,
            "maxOutputTokens": 1200,
        },
    }

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))

        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        if not text:
            return jsonify({"error": "Geminiから返答がありませんでした。"}), 500

        return jsonify({"prompt": text.strip()})

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return jsonify({"error": error_body}), 500

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
