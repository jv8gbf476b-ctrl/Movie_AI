import json


def build_romance_instruction(romance):
    romance_map = {
        "none": "No romance.",
        "なし": "No romance.",
        "holding hands": "They gently hold hands in a natural, tasteful way.",
        "手をつなぐ": "They gently hold hands in a natural, tasteful way.",
        "warm hug": "They share a warm, tasteful hug.",
        "ハグ": "They share a warm, tasteful hug.",
        "gentle kiss": "They share a gentle, tasteful movie-style kiss.",
        "キス": "They share a gentle, tasteful movie-style kiss.",
        "forehead kiss": "One person gives a gentle forehead kiss.",
        "おでこキス": "One person gives a gentle forehead kiss.",
        "looking into each other's eyes": "They quietly look into each other's eyes.",
        "見つめ合う": "They quietly look into each other's eyes.",
        "proposal": "A tasteful proposal moment.",
        "プロポーズ": "A tasteful proposal moment.",
        "dancing together": "They dance together naturally.",
        "ダンス": "They dance together naturally.",
        "embracing in the rain": "They embrace softly in the rain.",
        "雨の中で抱き合う": "They embrace softly in the rain.",
    }

    return romance_map.get(romance, romance_map["none"])


def build_prompt(plan):
    romance = plan.get("romance", "none")
    service = plan.get("service", "Kling")

    return f"""
You are Movie_AI Prompt Engine V4.

Create ONE short, complete English prompt for {service} image-to-video generation.

AI Plan:
{json.dumps(plan, ensure_ascii=False)}

Romance:
{build_romance_instruction(romance)}

Rules:
- Keep the uploaded image identity, clothing, hairstyle, accessories, background, visible objects, and visible people.
- Do not add new people, buildings, temples, gates, roads, moons, forests, or scenery unless clearly visible.
- Do not redesign the subject.
- Make a 5 to 10 second video.
- Keep the prompt compact.
- Finish every section.
- Output only the final prompt.

Use exactly this format:

SUBJECT:
Describe only the visible subject or subjects in 1 short paragraph.

SCENE:
Describe only the visible setting in 1 short paragraph.

ACTION:
Describe simple 5 to 10 second movement based on the AI Plan.

CAMERA:
Describe one camera movement.

STYLE:
Describe the visual style and mood.

NEGATIVE PROMPT:
distorted face, identity change, bad hands, extra fingers, deformed body, duplicated people, blurry face, low quality, artifacts, flickering, unrealistic motion, broken limbs, inconsistent clothing, explicit content, sexual content.
"""
