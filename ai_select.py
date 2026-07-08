from google.genai import types

from plan_parser import parse_plan


AI_SELECT_SCHEMA = {
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
}


def build_ai_select_prompt(romance_mode, romance_level):
    return f"""
You are AI Select, the planning engine of Movie_AI.

Brand:
Movie_AI
One Tap Cinema
指先から、まるで映画のような動画を。

Mission:
Analyze the uploaded image or images.
Create the best cinematic video plan.

User Romance Setting:
romance_mode = {romance_mode}
romance_level = {romance_level}

Return JSON only.

subject_type must be one of:
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

romance must be one of:
none
holding hands
warm hug
gentle kiss
forehead kiss
looking into each other's eyes
proposal
dancing together
embracing in the rain

service must always be:
Kling

Everything else should be natural Japanese.

scene example:
夜の日本の街並み

mood example:
神秘的で不気味

camera example:
ドリーショット

time example:
夜

style example:
和風ダークファンタジー

reason_ja:
2文以内。
短く自然な日本語。

Rules:
- Preserve identity.
- Preserve clothing.
- Preserve hairstyle.
- Preserve visible objects.
- Preserve visible creatures.
- Preserve atmosphere.
- No unnecessary characters.
- No explicit content.
- Romance only for humans.
- If romance_mode is off, romance must be none.
"""


def build_parts(
    photo1_bytes,
    photo1_type,
    photo2_bytes=None,
    photo2_type=None,
    romance_mode="off",
    romance_level="soft",
):
    parts = [
        types.Part.from_text(
            text=build_ai_select_prompt(
                romance_mode,
                romance_level,
            )
        ),
        types.Part.from_bytes(
            data=photo1_bytes,
            mime_type=photo1_type or "image/jpeg",
        ),
    ]

    if photo2_bytes:
        parts.append(
            types.Part.from_bytes(
                data=photo2_bytes,
                mime_type=photo2_type or "image/jpeg",
            )
        )

    return parts
