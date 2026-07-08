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
        "holding hands": (
            "The two people gently hold hands in a natural, elegant, non-explicit way."
        ),
        "手をつなぐ": (
            "The two people gently hold hands in a natural, elegant, non-explicit way."
        ),
        "warm hug": (
            "The two people share a warm cinematic hug in a tasteful, non-explicit way."
        ),
        "ハグ": (
            "The two people share a warm cinematic hug in a tasteful, non-explicit way."
        ),
        "gentle kiss": (
            "The two people share one gentle cinematic kiss in a tasteful, non-explicit way."
        ),
        "キス": (
            "The two people share one gentle cinematic kiss in a tasteful, non-explicit way."
        ),
        "forehead kiss": (
            "One person gives a gentle forehead kiss in a soft emotional moment."
        ),
        "おでこキス": (
            "One person gives a gentle forehead kiss in a soft emotional moment."
        ),
        "looking into each other's eyes": (
            "The two people quietly look into each other's eyes."
        ),
        "見つめ合う": (
            "The two people quietly look into each other's eyes."
        ),
        "proposal": (
            "A tasteful proposal scene."
        ),
        "プロポーズ": (
            "A tasteful proposal scene."
        ),
        "dancing together": (
            "The two people dance together naturally."
        ),
        "ダンス": (
            "The two people dance together naturally."
        ),
        "embracing in the rain": (
            "The two people embrace softly in the rain."
        ),
        "雨の中で抱き合う": (
            "The two people embrace softly in the rain."
        ),
    }

    return romance_map.get(romance, romance_map["none"])


def build_service_instruction(service):

    service = (service or "Kling").lower()

    if "runway" in service:
        return """
Runway optimization:
- Stable identity.
- Simple realistic motion.
- Never invent objects.
"""

    if "veo" in service:
        return """
Veo optimization:
- Real-world physics.
- Natural camera movement.
- Faithful to the reference image.
"""

    if "pika" in service:
        return """
Pika optimization:
- Clear movement.
- Strong visual readability.
"""

    if "luma" in service:
        return """
Luma optimization:
- Beautiful lighting.
- Stable environment.
"""

    return """
Kling optimization:
- Keep the uploaded image almost unchanged.
- Preserve every visible object.
- Never add landmarks not visible.
- Never invent buildings.
- Never invent trees.
- Never invent roads.
- Never invent gates.
- Never invent temples.
- Camera movement should create the cinematic feeling instead of adding scenery.
"""


def build_prompt(plan):

    romance = plan.get("romance", "none")
    service = plan.get("service", "Kling")

    return f"""
You are Movie_AI Prompt Engine V3.

Create ONE professional English image-to-video prompt.

Target AI

{service}

AI PLAN

{json.dumps(plan, ensure_ascii=False)}

ROMANCE

{build_romance_instruction(romance)}

SERVICE

{build_service_instruction(service)}

Highest Priority

1. Preserve identity.
2. Preserve clothing.
3. Preserve hairstyle.
4. Preserve accessories.
5. Preserve background.
6. Preserve every visible object.
7. Preserve every visible creature.
8. Never invent large new scenery.
9. Motion first.
10. Camera first.

Critical Rules

- Describe ONLY what is visible.
- If something is not visible, do not add it.
- Never add torii gates unless visible.
- Never add temples unless visible.
- Never add stone paths unless visible.
- Never add mountains unless visible.
- Never add forests unless visible.
- Never add extra people.
- Never redesign the scene.
- Small environmental extension is allowed only if visually obvious.
- Keep perfect identity consistency.

Video Length

5 to 10 seconds.

Output Format

SUBJECT:

SCENE:

ACTION:

CAMERA:

LIGHTING:

MOTION:

STYLE:

QUALITY:

NEGATIVE PROMPT:

Motion Guidelines

Human:
Natural breathing.
Natural blinking.
Tiny posture shift.
Hair movement.
Clothing movement.

Ghost:
Slow floating.
Subtle drifting.
Soft transparency.

Animals:
Natural idle movement.

Vehicles:
Natural wheel movement only.

Environment:
Wind.
Fog.
Smoke.
Dust.
Particles.
Leaves.
Water.

QUALITY

Ultra-realistic.
Stable identity.
Cinematic.
Natural movement.
Professional composition.

Output only the final English prompt.
"""
