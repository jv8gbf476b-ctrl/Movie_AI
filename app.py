import base64
import json
import os
import urllib.request
import urllib.error

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {
        "status": "running",
        "app": "Movie_AI",
        "gemini_key": bool(GEMINI_API_KEY),
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
You are Movie_AI, an expert AI video director.

Analyze the two uploaded reference photos and create a high-quality English prompt for {service} image-to-video generation.

Goal:
Create a natural cinematic video using the two people from the uploaded photos.

Selected scene:
{scene}

Selected mood:
{mood}

Requirements:
- Keep both identities and faces consistent with the reference photos.
- Describe both people naturally based on the photos.
- Make them appear naturally together in one scene.
- Use realistic body movement.
- Use natural expressions and eye contact.
- Avoid distorted faces, extra fingers, warped hands, strange bodies, identity changes, or unnatural motion.
- Add cinematic camera direction.
- Add lighting, atmosphere, background, and motion details.
- Make it suitable for a 5 to 10 second video.
- Output only the final English prompt.
"""

    payload = {
        "contents": [
            {
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
                ]
            }
        ]
    }

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as response:
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
