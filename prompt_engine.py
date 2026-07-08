import json


def build_romance_instruction(romance):
    romance_map = {
        "none": "No romance.",
        "なし": "No romance.",
        "holding hands": "They gently hold hands in a natural, cinematic way.",
        "手をつなぐ": "They gently hold hands in a natural, cinematic way.",
        "warm hug": "They share a warm cinematic hug.",
        "ハグ": "They share a warm cinematic hug.",
        "gentle kiss": "They share a gentle cinematic kiss.",
        "キス": "They share a gentle cinematic kiss.",
        "forehead kiss": "One person gently kisses the other's forehead.",
        "おでこキス": "One person gently kisses the other's forehead.",
        "looking into each other's eyes": "They quietly look into each other's eyes.",
        "見つめ合う": "They quietly look into each other's eyes.",
        "proposal": "One person proposes in a cinematic way.",
        "プロポーズ": "One person proposes in a cinematic way.",
        "dancing together": "They dance together naturally.",
        "ダンス": "They dance together naturally.",
        "embracing in the rain": "They embrace softly in the rain.",
        "雨の中で抱き合う": "They embrace softly in the rain.",
    }

    return romance_map.get(romance, romance_map["none"])


def build_prompt(plan):

    romance = plan.get("romance", "none")
    service = plan.get("service", "Kling")
    user_situation = plan.get("user_situation", "").strip()

    situation_block = (
        f"""
USER REQUEST:
{user_situation}

Priority:
The user's requested situation is the highest priority.
Recreate it while preserving the uploaded people.
"""
        if user_situation
        else """
No user situation was provided.
Create the best cinematic situation from the AI Plan.
"""
    )

    return f"""
You are Movie_AI Prompt Engine.

Create ONE complete English prompt for {service}.

AI PLAN:
{json.dumps(plan, ensure_ascii=False)}

{situation_block}

ROMANCE:
{build_romance_instruction(romance)}

Rules:

- Preserve identity.
- Preserve hairstyle.
- Preserve clothing.
- Preserve accessories.
- Preserve visible people.
- Preserve visible objects.
- Preserve the overall atmosphere.
- Never invent important new characters.
- Never change the person's appearance.
- You may change lighting, weather, time of day, camera movement and mood if it improves the cinematic result.
- Follow the USER REQUEST whenever possible.
- If the USER REQUEST conflicts with the uploaded image, preserve the people and adapt the environment naturally.
- Keep the prompt compact.
- Make a 5 to 10 second cinematic video.

Output Format

SUBJECT:

SCENE:

ACTION:

CAMERA:

STYLE:

NEGATIVE PROMPT:

Output only the final English prompt.
"""
