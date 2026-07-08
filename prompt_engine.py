import json


def build_romance_instruction(romance):
    romance_map = {
        "none": (
            "No romance. Do not mention romance, flirting, kissing, hugging, "
            "holding hands, lovers, intimacy, passion, or romantic tension."
        ),
        "なし": (
            "No romance. Do not mention romance, flirting, kissing, hugging, "
            "holding hands, lovers, intimacy, passion, or romantic tension."
        ),
        "holding hands": "The two people gently hold hands in a natural, elegant, non-explicit way.",
        "手をつなぐ": "The two people gently hold hands in a natural, elegant, non-explicit way.",
        "warm hug": "The two people share a warm cinematic hug in a tasteful, non-explicit way.",
        "ハグ": "The two people share a warm cinematic hug in a tasteful, non-explicit way.",
        "gentle kiss": "The two people share one gentle cinematic kiss in a tasteful, non-explicit way.",
        "キス": "The two people share one gentle cinematic kiss in a tasteful, non-explicit way.",
        "forehead kiss": "One person gives a gentle forehead kiss in a soft emotional moment.",
        "おでこキス": "One person gives a gentle forehead kiss in a soft emotional moment.",
        "looking into each other's eyes": "The two people quietly look into each other's eyes.",
        "見つめ合う": "The two people quietly look into each other's eyes.",
        "proposal": "A tasteful proposal scene.",
        "プロポーズ": "A tasteful proposal scene.",
        "dancing together": "The two people dance together naturally.",
        "ダンス": "The two people dance together naturally.",
        "embracing in the rain": "The two people embrace softly in the rain.",
        "雨の中で抱き合う": "The two people embrace softly in the rain.",
    }

    return romance_map.get(romance, romance_map["none"])


def build_service_instruction(service):
    service = (service or "Kling").lower()

    if "runway" in service:
        return """
Runway optimization:
- Stable identity.
- Clean cinematic motion.
- Simple scene composition.
"""

    if "veo" in service:
        return """
Veo optimization:
- Natural cinematic language.
- Physically realistic motion.
- Story focused.
"""

    if "pika" in service:
        return """
Pika optimization:
- Clear motion.
- Strong visual action.
- Simple instructions.
"""

    if "luma" in service:
        return """
Luma optimization:
- Beautiful lighting.
- Strong camera movement.
- Cinematic depth.
"""

    return """
Kling optimization:
- Stable identity.
- Professional cinematic wording.
- Smooth camera movement.
- Easy image-to-video instructions.
"""


def build_prompt(plan):
    romance = plan.get("romance", "none")
    service = plan.get("service", "Kling")

    return f"""
You are Prompt Engine V2 of Movie_AI.

Brand:
Movie_AI
One Tap Cinema
指先から、まるで映画のような動画を。

Create ONE complete English prompt for {service} image-to-video generation.

AI Plan:
{json.dumps(plan, ensure_ascii=False)}

Romance:
{build_romance_instruction(romance)}

Service:
{build_service_instruction(service)}

Rules:
- Keep identity.
- Keep clothing.
- Keep hairstyle.
- Keep accessories.
- Keep background.
- Keep visible objects.
- Keep visible creatures.
- Keep atmosphere.
- Never remove visible objects.
- Never change identity.
- Never redesign clothing.
- Never redesign hairstyle.
- Never invent important characters.
- Only extend the environment naturally.
- Make a complete 5 to 10 second cinematic video prompt.
- Do not stop mid-sentence.
- Finish every section.

Output exactly this format:

SUBJECT:
Describe the visible subject and important visible details in one compact paragraph.

SCENE:
Describe the scene based on the AI Plan and uploaded image in one compact paragraph.

ACTION:
Describe clear 5 to 10 second action with meaningful movement.

CAMERA:
Describe camera movement, framing, and shot style.

LIGHTING:
Describe lighting, color, mood, atmosphere, and time.

MOTION:
Describe natural movement such as breathing, blinking, hair movement, clothing movement, object movement, environmental movement, vehicle movement, pet movement, or character animation.

STYLE:
Describe the visual style based on the AI Plan.

QUALITY:
Ultra-realistic or style-consistent, cinematic, high-detail, stable identity, clean motion, high resolution.

NEGATIVE PROMPT:
distorted faces, identity change, bad hands, extra fingers, warped hands, deformed body, duplicated people, unnatural anatomy, blurry faces, low quality, artifacts, flickering, unrealistic motion, strange eye movement, broken limbs, inconsistent clothing, melted objects, unstable background, explicit content, sexual content.

Output only the final English prompt.
"""
