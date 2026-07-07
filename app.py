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
        "none": "No romantic physical action. Keep the interaction natural, friendly, and cinematic without holding hands, hugging, or kissing.",
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
        "cinematic": "Use cinematic camera movement, smooth dolly-in, shallow depth of field, and film-like framing.",
        "drone shot": "Use an elegant aerial drone shot that slowly moves closer to the couple.",
        "close up": "Use intimate close-up shots focused on faces, expressions, and subtle emotions.",
        "slow motion": "Use graceful slow-motion movement with cinematic emotional pacing.",
        "POV": "Use a natural POV-style camera perspective, immersive and realistic.",
        "handheld": "Use soft handheld cinematic camera movement with realistic documentary-style intimacy.",
    }
    return camera_map.get(camera, camera_map["cinematic"])


def build_director_instruction(director):
    if director == "simple":
        return "Create a clear, simple, easy-to-use prompt. Keep it practical and not too long."
    if director == "hollywood":
        return "Create a highly detailed Hollywood-level prompt with strong cinematic direction, lens language, lighting, emotion, movement, atmosphere, and negative prompt."
    return "Create a polished cinematic director-level prompt with detailed camera, lighting, motion, and emotional direction."


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

        romance_instruction = build_romance_instruction(romance)
        camera_instruction = build_camera_instruction(camera)
        director_instruction = build_director_instruction(director)

        client = genai.Client(api_key=GEMINI_API_KEY)

        director_prompt = f"""
You are Movie_AI, a professional AI video director and prompt engineer.

Analyze the two uploaded reference photos carefully.
Create one high-quality English prompt for {service} image-to-video generation.

User settings:
Scene: {scene}
Mood: {mood}
Romance action: {romance}
Camera style: {camera}
Director level: {director}

Romance rule:
{romance_instruction}

Camera rule:
{camera_instruction}

Director rule:
{director_instruction}

Photo analysis requirements:
Describe each person based only on visible details in the uploaded images.
Include:
- apparent age range
- hairstyle and hair color
- facial expression
- clothing
- posture
- visible accessories
- overall vibe
- relationship-like positioning only if requested by the romance setting

Prompt structure:
Write the final prompt in polished English.
Include these sections naturally:
1. Main subject
2. Appearance of both people
3. Scene and environment
4. Action and interaction
5. Romance direction
6. Camera movement
7. Lighting and atmosphere
8. Realistic motion details
9. Quality instructions
10. Negative prompt

Important rules:
- Keep both identities and faces consistent with the reference photos.
- Do not change race, age, face shape, hairstyle, or clothing unless the scene clearly requires only minor cinematic styling.
- Make both people appear naturally together in the same scene.
- If romance is "none", do not include kissing, hugging, holding hands, or romantic physical contact.
- Romantic content must stay elegant, cinematic, and non-explicit.
- Avoid sexual or explicit content.
- Optimize wording for {service}.
- Make the prompt ready to paste directly into {service}.

Negative prompt must include:
Avoid distorted faces, identity change, extra fingers, bad hands, warped hands, deformed body, duplicated people, unnatural anatomy, blurry faces, low quality, artifacts, flickering, unrealistic motion, strange eye movement, broken limbs, and inconsistent clothing.

Output only the final English prompt.
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
                temperature=0.85,
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
