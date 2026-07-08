# ai_select.py

import json
import re

from google.genai import types


DISPLAY_JA = {
    "subject_type": {
        "person": "人物",
        "couple": "人物",
        "pet": "ペット",
        "car": "車",
        "motorcycle": "バイク",
        "illustration": "イラスト",
        "original_character": "オリジナルキャラ",
        "scenery": "風景",
        "product": "商品",
        "other": "その他",
    },
    "romance": {
        "none": "なし",
        "holding hands": "手をつなぐ",
        "warm hug": "ハグ",
        "gentle kiss": "キス",
        "forehead kiss": "おでこキス",
        "looking into each other's eyes": "見つめ合う",
        "proposal": "プロポーズ",
        "dancing together": "ダンス",
        "embracing in the rain": "雨の中で抱き合う",
    },
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

Everything else MUST be written in natural Japanese.

scene:
例）夜の日本の街並み

mood:
例）神秘的で不気味

camera:
例）ドリーショット

time:
例）夜

style:
例）和風ダークファンタジー

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
    pattern = rf'"{key}"\s*:\s*"([^"]*)"'
    match = re.search(pattern, text)

    if match:
        return match.group(1).strip()

    number = re.search(rf'"{key}"\s*:\s*([0-9.]+)', text)

    if number:
        try:
            return float(number.group(1))
        except Exception:
            pass

    return default


def _clean_reason(reason):
    if not reason:
        return "画像の雰囲気に合う映像プランを選びました。"

    reason = str(reason).replace("\n", " ").strip()

    sentences = re.split(r"(?<=[。！？])", reason)

    return "".join(sentences[:2]).strip()


def normalize_plan(plan):

    plan["service"] = "Kling"

    if not plan.get("romance"):
        plan["romance"] = "none"

    plan["subject_type"] = DISPLAY_JA["subject_type"].get(
        str(plan.get("subject_type", "")).lower(),
        plan.get("subject_type", "その他"),
    )

    plan["romance"] = DISPLAY_JA["romance"].get(
        str(plan.get("romance", "")).lower(),
        plan.get("romance", "なし"),
    )

    plan["reason_ja"] = _clean_reason(
        plan.get("reason_ja")
    )

    return plan


def _fallback_plan(text):

    plan = {
        "subject_type": _find_value(text, "subject_type", "other"),
        "scene": _find_value(text, "scene", "夜の街"),
        "mood": _find_value(text, "mood", "映画風"),
        "romance": _find_value(text, "romance", "none"),
        "camera": _find_value(text, "camera", "ドリーショット"),
        "time": _find_value(text, "time", "夜"),
        "style": _find_value(text, "style", "映画風"),
        "service": "Kling",
        "reason_ja": _find_value(
            text,
            "reason_ja",
            "画像の雰囲気に合う映像プランを選びました。",
        ),
        "confidence": _find_value(text, "confidence", 4),
    }

    return normalize_plan(plan)


def parse_plan(response):

    if hasattr(response, "parsed") and response.parsed:

        if isinstance(response.parsed, dict):
            return normalize_plan(response.parsed)

        if hasattr(response.parsed, "model_dump"):
            return normalize_plan(
                response.parsed.model_dump()
            )

    if not response.text:
        raise ValueError("AI Selectから返答がありませんでした。")

    cleaned = (
        response.text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        return normalize_plan(
            json.loads(cleaned)
        )
    except Exception:
        return _fallback_plan(cleaned)
