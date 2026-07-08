import json
import os

from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

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

        photo1_bytes = photo1.read()
        photo2_bytes = photo2.read() if photo2 else None

        system_prompt = f"""
You are AI Select, the planning engine of Movie_AI.

Brand:
Movie_AI
One Tap Cinema
指先から、まるで映画のような動画を。

Mission:
Analyze the uploaded image.
Choose the best cinematic plan.

User romance setting

romance_mode = {romance_mode}

romance_level = {romance_level}

Detect one:

person
couple
pet
car
motorcycle
illustration
original_character
scenery
product
other

Rules

- Never invent romance when OFF.
- Romance only for humans.
- Preserve the original atmosphere.
- Prefer scenes that current video AI can generate well.
- Prefer cinematic but realistic ideas.
- If the uploaded image already has a strong world, keep that world.
- Avoid unnecessary new objects.
- Keep identities consistent.

Return ONLY JSON.

{
"subject_type":"",
"scene":"",
"mood":"",
"romance":"",
"camera":"",
"time":"",
"style":"",
"service":"Kling",
"reason_ja":"",
"confidence":5
}
"""

        parts = [
            types.Part.from_text(text=system_prompt),
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
                temperature=0.30,
                top_p=0.90,
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

        "none":
        "No romance. Do not mention romance, flirting, kissing, hugging, holding hands, lovers, intimacy or romantic tension.",

        "holding hands":
        "The two people gently hold hands naturally.",

        "warm hug":
        "The two people share a warm cinematic hug.",

        "gentle kiss":
        "The two people share one elegant cinematic kiss.",

        "forehead kiss":
        "A gentle forehead kiss.",

        "looking into each other's eyes":
        "The two people quietly look into each other's eyes.",

        "proposal":
        "A tasteful proposal scene.",

        "dancing together":
        "The two people dance together naturally.",

        "embracing in the rain":
        "The two people embrace softly in the rain.",

    }

    return romance_map.get(
        romance,
        romance_map["none"],
    )

def build_service_instruction(service):

    service = (service or "Kling").lower()

    if "runway" in service:
        return """
Runway optimization
- Prioritize clean cinematic movement.
- Keep scenes simple.
- Stable identity.
- Strong camera language.
"""

    if "veo" in service:
        return """
Veo optimization
- Natural cinematic language.
- Story driven.
- Smooth realistic motion.
"""

    if "pika" in service:
        return """
Pika optimization
- Fun motion.
- Clear action.
- Short visual descriptions.
"""

    if "luma" in service:
        return """
Luma optimization
- Strong depth.
- Beautiful lighting.
- Elegant camera movement.
"""

    return """
Kling optimization
- Professional production language.
- Stable identity.
- Smooth camera movement.
- Strong cinematic atmosphere.
- Easy for image-to-video generation.
"""


@app.route("/generate", methods=["POST"])
def generate():

    if not client:
        return jsonify({"error": "GEMINI_API_KEY is not set."}), 500

    photo1, photo2, error = get_uploaded_images()

    if error:
        return jsonify({"error": error}), 400

    plan_json = request.form.get("plan", "")

    if not plan_json:
        return jsonify(
            {
                "error": "AI Planがありません。先にAI Selectを実行してください。"
            }
        ), 400

    try:

        plan = json.loads(plan_json)

        photo1_bytes = photo1.read()
        photo2_bytes = photo2.read() if photo2 else None

        romance = plan.get("romance", "none")
        service = plan.get("service", "Kling")

        prompt_engine = f"""
You are Prompt Engine V2 of Movie_AI.

Brand

Movie_AI

One Tap Cinema

指先から、まるで映画のような動画を。

Your mission

Create ONE professional English prompt.

The prompt must be ready to paste into

{service}

AI Plan

{json.dumps(plan, ensure_ascii=False)}

Romance

{build_romance_instruction(romance)}

Service Optimization

{build_service_instruction(service)}

Priority

1 Keep identity

2 Keep clothing

3 Keep hairstyle

4 Keep accessories

5 Keep background

6 Keep visible creatures

7 Keep visible objects

8 Keep visible text

9 Keep atmosphere

10 Create realistic movement

Never remove visible objects.

Never change identity.

Never redesign clothing.

Never redesign hairstyle.

Never invent important characters.

Only extend the environment naturally.

Video length

5 to 10 seconds.

Output format

SUBJECT

SCENE

ACTION

CAMERA

LIGHTING

MOTION

STYLE

QUALITY

NEGATIVE PROMPT

Motion Rules

Humans

Natural breathing

Small head movement

Natural blinking

Natural body balance

Hair movement

Clothing movement

Facial expression change

Pets

Tail movement

Ear movement

Blinking

Natural walking

Natural running

Cars

Wheel rotation

Road reflections

Suspension movement

Camera tracking

Illustration

Respect original design

Natural animation

Scenery

Wind

Fog

Clouds

Particles

Water

Leaves

Lighting movement

Camera movement

Everything should feel cinematic but realistic.
"""

        parts = [

            types.Part.from_text(
                text=prompt_engine,
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
                temperature=0.45,
                top_p=0.90,
                max_output_tokens=2100,
            ),

        )

        if not response.text:

            return jsonify(
                {
                    "error": "Geminiから返答がありませんでした。"
                }
            ), 500

        final_prompt = response.text.strip()

        return jsonify(
            {
                "prompt": final_prompt
            }
        )

    except Exception as e:

        return jsonify(
            {
                "error": str(e)
            }
        ), 500


@app.route("/<path:path>")
def catch_all(path):
    return render_template("index.html")


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
