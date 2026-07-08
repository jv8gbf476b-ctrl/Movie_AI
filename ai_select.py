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


def build_ai_select_prompt(
    romance_mode,
    romance_level,
    user_situation="",
):
    return f"""
You are AI Select, the planning engine of Movie_AI.

Brand:
Movie_AI
One Tap Cinema
指先から、まるで映画のような動画を。

Mission:
Analyze the uploaded image or images.
Create the best cinematic video plan.

User Settings
romance_mode = {romance_mode}
romance_level = {romance_level}

User Situation
{user_situation if user_situation else "AI decides the best cinematic situation."}

Priority

1. Preserve identity.
2. Preserve clothing.
3. Preserve hairstyle.
4. Preserve accessories.
5. Preserve visible people.
6. Preserve visible objects.
7. Preserve atmosphere.

Creative Rules

- If the user wrote a situation, prioritize it.
- Recreate the user's requested situation while preserving the uploaded people.
- You may change lighting, weather, time of day and camera direction if it improves the cinematic feeling.
- Never change identity.
- Never change clothing.
- Never add important new characters.
- Never invent famous landmarks unless requested.
- Never change race, age or gender.
- Keep everything movie-like.

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

Romance Rules

- romance_mode off -> romance must be none.
- If two humans exist and romance_mode is on, romance must NOT be none.
- Romance must always match romance_level.
- Never generate explicit content.

Output Rules

- scene: Japanese
- mood: Japanese
- camera: Japanese
- time: Japanese
- style: Japanese
- reason_ja: Japanese, within 2 short sentences.
- service must always be Kling.

Return valid JSON only.
"""


def build_parts(
    photo1_bytes,
    photo1_type,
    photo2_bytes=None,
    photo2_type=None,
    romance_mode="off",
    romance_level="soft",
    user_situation="",
):
    parts = [
        types.Part.from_text(
            text=build_ai_select_prompt(
                romance_mode,
                romance_level,
                user_situation,
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
