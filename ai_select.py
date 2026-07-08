# ai_select.py

import json
import re

from google.genai import types


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

Detect one subject type only:
person, couple, pet, car, motorcycle, illustration, original_character, scenery, product, other

Planning Rules:
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
- service must be Kling.

Romance Rules:
- If romance_mode is off, romance must be none.
- Romance is only for humans.
- Never generate explicit or sexual content.

Return valid JSON only.
Do not use line breaks inside JSON string values.
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


def _find_value(text, key, default):
    pattern = rf'"{key}"\s*:\s*"([^"]*)'
    match = re.search(pattern, text)

    if match:
        return match.group(1).strip()

    pattern_number = rf'"{key}"\s*:\s*([0-9.]+)'
    match_number = re.search(pattern_number, text)

    if match_number:
        try:
            return float(match_number.group(1))
        except ValueError:
            return default

    return default


def _fallback_plan(text):
    return {
        "subject_type": _find_value(text, "subject_type", "other"),
        "scene": _find_value(text, "scene", "cinematic scene"),
        "mood": _find_value(text, "mood", "cinematic"),
        "romance": _find_value(text, "romance", "none"),
        "camera": _find_value(text, "camera", "medium shot"),
        "time": _find_value(text, "time", "cinematic lighting"),
        "style": _find_value(text, "style", "cinematic"),
        "service": "Kling",
        "reason_ja": _find_value(
            text,
            "reason_ja",
            "画像の雰囲気に合わせて、最も映える映像プランを選びました。",
        ),
        "confidence": _find_value(text, "confidence", 4),
    }


def parse_plan(response):
    if hasattr(response, "parsed") and response.parsed:
        if isinstance(response.parsed, dict):
            return response.parsed

        if hasattr(response.parsed, "model_dump"):
            return response.parsed.model_dump()

        try:
            return dict(response.parsed)
        except Exception:
            pass

    if not response.text:
        raise ValueError("AI Selectから返答がありませんでした。")

    cleaned = response.text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except Exception:
        return _fallback_plan(cleaned)
