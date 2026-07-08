# prompt_engine.py

import json


def build_romance_instruction(romance):
    romance_map = {
        "none": (
            "No romance. Do not mention romance, flirting, kissing, hugging, "
            "holding hands, lovers, intimacy, passion, or romantic tension."
        ),
        "holding hands": (
            "The two people gently hold hands in a natural, elegant, non-explicit way."
        ),
        "warm hug": (
            "The two people share a warm cinematic hug in a tasteful, non-explicit way."
        ),
        "gentle kiss": (
            "The two people share one gentle cinematic kiss in a tasteful, non-explicit way."
        ),
        "forehead kiss": (
            "One person gives a gentle forehead kiss in a soft emotional moment."
        ),
        "looking into each other's eyes": (
            "The two people quietly look into each other's eyes."
        ),
        "proposal": (
            "A tasteful proposal scene."
        ),
        "dancing together": (
            "The two people dance together naturally."
        ),
        "embracing in the rain": (
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

Brand

Movie_AI

One Tap Cinema

指先から、まるで映画のような動画を。

Create ONE professional English prompt.

Target AI

{service}

AI Plan

{json.dumps(plan, ensure_ascii=False)}

Romance

{build_romance_instruction(romance)}

Service

{build_service_instruction(service)}

Priority

1. Keep identity
2. Keep clothing
3. Keep hairstyle
4. Keep accessories
5. Keep background
6. Keep visible objects
7. Keep visible creatures
8. Keep atmosphere
9. Cinematic motion
10. Stable video

Rules

- Never change identity.
- Never redesign clothing.
- Never remove visible objects.
- Never invent major new characters.
- Extend the environment only when natural.

Video Length

5 to 10 seconds.

Output Format

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

Humans:
Natural breathing.
Natural blinking.
Hair movement.
Clothing movement.
Small body movement.

Pets:
Tail movement.
Ear movement.
Natural walking.

Cars:
Wheel rotation.
Road reflections.
Camera tracking.

Illustrations:
Preserve design.
Natural animation.

Scenery:
Wind.
Fog.
Clouds.
Particles.
Water.
Leaves.

Everything should feel cinematic but realistic.

Output only the final English prompt.
"""
