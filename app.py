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


def build_romance_instruction(romance):
    romance_map = {
        "none": "No romance. Do not describe romantic tension, dating energy, holding hands, hugging, kissing, flirting, or couple-like behavior. Keep the interaction as close friends or travel companions.",
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


def build_camera_instruction(camera):
    camera_map = {
        "cinematic": "Slow cinematic dolly-in, film-like framing, shallow depth of field.",
        "drone shot": "Elegant aerial drone shot slowly moving closer.",
        "close up": "Close-up shots focused on faces, eyes, expressions, and subtle emotion.",
        "slow motion": "Graceful slow motion with emotional pacing.",
        "POV": "Immersive first-person POV camera perspective.",
        "handheld": "Soft handheld cinematic camera with realistic documentary intimacy.",
    }
    return camera_map.get(camera, camera_map["cinematic"])


def build_director_instruction(director):
    if director == "simple":
        return "Keep the prompt short, practical, and easy to paste into Kling."
    if director == "hollywood":
        return "Make the prompt extremely cinematic, detailed, premium, and Hollywood-level."
    return "Make the prompt polished, cinematic, and director-level."


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
You are Movie_AI, a professional AI video director and prompt engineer.

Analyze the two uploaded reference photos carefully.
Create ONE English prompt optimized for {service} image-to-video generation.

Important:
Do NOT write a novel.
Do NOT write poetic paragraphs.
Write a clear production-style shooting instruction sheet.

User settings:
Scene: {scene}
Mood: {mood}
Romance action: {romance}
Camera style: {camera}
Director level: {director}

Romance rule:
{build_romance_instruction(romance)}

Camera rule:
{build_camera_instruction(camera)}

Director rule:
{build_director_instruction(director)}

Photo analysis:
Describe only visible details from the uploaded photos.
Include hairstyle, clothing, expression, posture, accessories, and overall vibe.
Do not invent details that are not visible.

Output format:
Use exactly this structure:

SUBJECT:
Describe both people clearly based on the reference photos.

SCENE:
Describe the location and environment.

ACTION:
Describe what they do in the 5 to 10 second video.

ROMANCE:
Describe the selected romance action. If romance is none, clearly state there is no romantic physical contact or romantic behavior.

CAMERA:
Describe camera movement based on the selected camera style.

LIGHTING:
Describe lighting, color, atmosphere, and cinematic look.

MOTION:
Describe natural movement, clothing movement, facial expression changes, and realistic body motion.

QUALITY:
Describe ultra-realistic, high-detail, cinematic video quality.

NEGATIVE PROMPT:
Avoid distorted faces, identity change, extra fingers, bad hands, warped hands, deformed body, duplicated people, unnatural anatomy, blurry faces, low quality, artifacts, flickering, unrealistic motion, strange eye movement, broken limbs, inconsistent clothing, explicit content, and sexual content.

Rules:
- Keep both identities and faces consistent with the reference photos.
- Keep clothing and hairstyle consistent unless minor cinematic styling is necessary.
- Make the two people appear naturally together in the same scene.
- Romantic content must be elegant, cinematic, and non-explicit.
- If romance is none, avoid words like romantic, couple, lovers, kiss, hug, holding hands, intimate, passionate.
- Make it ready to paste directly into {service}.
- Output only the final prompt.
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
                temperature=0.75,
                top_p=0.95,
                max_output_tokens=2400,
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
