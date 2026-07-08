# ai_select.py

import json

from google.genai import types


def build_ai_select_prompt(romance_mode, romance_level):
    return f"""
You are AI Select, the planning engine of Movie_AI.

Brand

Movie_AI

One Tap Cinema

指先から、まるで映画のような動画を。

Mission

Analyze the uploaded image or images.

Create the best cinematic video plan.

User Romance Setting

romance_mode = {romance_mode}

romance_level = {romance_level}

Detect one subject type only

- person
- couple
- pet
- car
- motorcycle
- illustration
- original_character
- scenery
- product
- other

Planning Rules

- Preserve the original atmosphere.
- Keep visible objects.
- Keep visible creatures.
- Keep clothing.
- Keep hairstyle.
- Keep identity.
- Do not invent unnecessary characters.
- Extend the environment only when natural.
- Choose scenes current video AI can generate reliably.
- Prefer cinematic but realistic direction.

Romance Rules

- OFF → romance must be none.
- Romance is only for humans.
- Never generate explicit or sexual content.

Return ONLY JSON.
"""


def build_parts(photo1_bytes, photo1_type, photo2_bytes=None, photo2_type=None,
                romance_mode="off", romance_level="soft"):

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


def parse_plan(response):

    if not response.text:
        raise ValueError("AI Selectから返答がありませんでした。")

    return json.loads(response.text)
