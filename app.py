import os

from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

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
    romance = request.form.get("romance", "none")
    camera = request.form.get("camera", "cinematic")
    director = request.form.get("director", "cinematic")

    if not photo1 or not photo2:
        return jsonify({"error": "写真を2枚選んでください。"}), 400

    try:
        photo1_bytes = photo1.read()
        photo2_bytes = photo2.read()

        client = genai.Client(api_key=GEMINI_API_KEY)

        director_prompt = f"""
You are Movie_AI, a professional AI video director.

Analyze the two uploaded reference photos carefully and create one highly detailed English prompt for {service} image-to-video generation.

User settings:
Scene: {scene}
Mood: {mood}
Romance action: {romance}
Camera style: {camera}
Director level: {director}

Create a cinematic 5 to 10 second video prompt.

Rules:
- Keep both identities and faces consistent with the reference photos.
- Describe both people naturally based on the photos.
- Include hairstyle, clothing, expression, posture, and visible details.
- Make the two people appear naturally together in the same scene.
- The romance must be elegant, cinematic, and non-explicit.
- If romance is "gentle kiss", describe a romantic movie-style kiss, not explicit adult content.
- Add natural body movement and emotional facial expressions.
- Add camera movement based on the selected camera style.
- Add lighting, background, atmosphere, depth of field, and realistic motion.
- Optimize the wording for {service}.
- Include negative instructions to avoid distorted faces, extra fingers, warped hands, strange bodies, identity changes, duplicated people, and unnatural movement.

Output only the final English prompt.
Make the prompt rich, polished, and ready to paste into {service}.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=director_prompt),
                        types.Part.from_bytes(
                            data=photo1_bytes,
                            mime_type=photo1.mimetype or "image/jpeg",
                        ),
                        types.Part.from_bytes(
                            data=photo2_bytes,
                            mime_type=photo2.mimetype or "image/jpeg",
                        ),
                    ],
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.9,
                top_p=0.95,
                max_output_tokens=1800,
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
