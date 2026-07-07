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

Your job:
Choose a video concept that would look impressive, natural, and commercially useful.

Detect the subject type:
person, couple, pet, car, motorcycle, illustration, original_character, scenery, product, or other.

User romance setting:
romance_mode: {romance_mode}
romance_level: {romance_level}

Rules:
- If romance_mode is off, romance must be "none".
- If romance_mode is on, choose elegant, cinematic, non-explicit romance only when the subject is human.
- If the subject is car, motorcycle, pet, illustration, product, scenery, or other non-human subject, romance must be "none".
- Choose a simple, high-impact concept.
- Do not choose complicated scenes that are hard for video AI to generate.
- service should usually be "Kling".
- confidence must be a number from 1 to 5.
- reason_ja must be short Japanese text explaining why this plan fits the image.
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
                temperature=0.35,
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
        "none": "No romance. Do not describe romantic tension, dating energy, holding hands, hugging, kissing, flirting, intimate eye contact, or couple-like behavior.",
        "holding hands": "The two people gently hold hands in a natural, elegant, non-explicit romantic way.",
        "warm hug": "The two people share a warm emotional hug, cinematic, tasteful, and non-explicit.",
        "gentle kiss": "The two people share a gentle movie-style kiss, tasteful, elegant, and non-explicit.",
        "forehead kiss": "One person gently kisses the other on the forehead in a soft, emotional, non-explicit moment.",
        "looking into each other's eyes": "The two people look into each other's eyes with subtle emotional tension, cinematic and tasteful.",
        "proposal": "A tasteful romantic proposal moment with emotional eye contact and elegant body language.",
        "dancing together": "The two people dance together slowly and naturally in a cinematic, elegant way.",
        "embracing in the rain": "The two people embrace emotionally in soft rain, cinematic, elegant, and non-explicit.",
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

        prompt_engine = f"""
You are Movie_AI, a professional AI video director and expert prompt engineer for {service} image-to-video generation.

Your job:
Create ONE final English prompt that is ready to paste directly into {service}.

This prompt must prioritize:
1. Faithfulness to the uploaded image
2. Clear cinematic motion
3. Stable identity
4. Realistic camera movement
5. Strong but not excessive visual detail
6. Practical wording for image-to-video generation

Use this AI Plan:
{json.dumps(plan, ensure_ascii=False)}

Romance instruction:
{build_romance_instruction(romance)}

Critical image fidelity rules:
- Describe only visible details from the uploaded image.
- Preserve the subject's face, clothing, hairstyle, accessories, pose, and visible background elements.
- If unusual creatures, objects, text, logos, vehicles, pets, or illustrated elements are visible, include them accurately.
- Do not remove important visible elements.
- Do not invent major new characters or objects that are not visible unless the AI Plan clearly requires a simple environment extension.
- Keep the subject identity consistent.
- Keep clothing and styling consistent.
- If there are two uploaded images, treat them as references that must be combined naturally without changing identities.

Kling optimization rules:
- Use clear production-style sections.
- Avoid novel-like writing.
- Avoid overly long paragraphs.
- Prefer direct cinematic instructions.
- Make motion easy for video AI to understand.
- Keep the total prompt detailed but not bloated.
- Describe a 5 to 10 second video.
- Include camera movement, lighting, environment, motion, and negative prompt.

Output exactly this structure:

SUBJECT:
A concise but accurate description of the visible subject or subjects.

SCENE:
The environment based on the AI Plan and uploaded image. Keep it visually coherent.

ACTION:
Clear 5 to 10 second action. Add meaningful movement, not just standing still. Keep it realistic for the subject.

CAMERA:
Camera movement, framing, lens feel, and depth of field.

LIGHTING:
Lighting, color, mood, atmosphere, and weather if relevant.

MOTION:
Natural motion details such as clothing movement, hair movement, object movement, environmental movement, vehicle movement, pet movement, or character animation.

STYLE:
Visual style based on the AI Plan. Keep it suitable for {service}.

QUALITY:
Ultra-realistic, high-detail, cinematic, stable identity, clean motion, high resolution.

NEGATIVE PROMPT:
Avoid distorted faces, identity change, extra fingers, bad hands, warped hands, deformed body, duplicated people, unnatural anatomy, blurry faces, low quality, artifacts, flickering, unrealistic motion, strange eye movement, broken limbs, inconsistent clothing, melted objects, unstable background, explicit content, and sexual content.

Important:
- If romance is none, do not mention romance, romantic tension, couple, lovers, kissing, hugging, holding hands, or intimate behavior.
- If the subject is a car, motorcycle, pet, product, scenery, illustration, or original character, adapt the action naturally to that subject.
- Output only the final English prompt.
"""

        parts = [
            types.Part.from_text(text=prompt_engine),
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
                temperature=0.55,
                top_p=0.9,
                max_output_tokens=2000,
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
