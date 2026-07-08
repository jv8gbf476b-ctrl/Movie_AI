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


KEYWORD_JA = {
    "scene": [
        ("beach", "海辺"),
        ("ocean", "海辺"),
        ("sea", "海辺"),
        ("city", "夜景の街"),
        ("street", "街並み"),
        ("japanese", "日本の街並み"),
        ("night", "夜の街"),
        ("mountain", "峠"),
        ("pass", "峠"),
        ("circuit", "サーキット"),
        ("race", "サーキット"),
        ("park", "公園"),
        ("cafe", "カフェ"),
        ("festival", "夏祭り"),
        ("shrine", "神社"),
        ("temple", "寺院"),
    ],
    "mood": [
        ("dark fantasy", "ダークファンタジー"),
        ("mysterious", "神秘的"),
        ("eerie", "不気味"),
        ("romantic", "ロマンチック"),
        ("emotional", "感動的"),
        ("cool", "クール"),
        ("cute", "かわいい"),
        ("dramatic", "ドラマチック"),
        ("cinematic", "映画風"),
    ],
    "camera": [
        ("medium", "ミディアムショット"),
        ("close", "クローズアップ"),
        ("drone", "ドローン撮影"),
        ("tracking", "追従カメラ"),
        ("dolly", "ゆっくり寄るカメラ"),
        ("handheld", "手持ちカメラ"),
        ("low angle", "ローアングル"),
        ("wide", "ワイドショット"),
    ],
    "time": [
        ("night", "夜"),
        ("full moon", "満月の夜"),
        ("moon", "月夜"),
        ("sunset", "夕方"),
        ("golden", "夕方"),
        ("morning", "朝"),
        ("day", "昼"),
        ("rain", "雨"),
        ("snow", "雪"),
        ("cinematic lighting", "映画風ライティング"),
    ],
    "style": [
        ("japanese dark fantasy", "和風ダークファンタジー"),
        ("dark fantasy", "ダークファンタジー"),
        ("anime", "アニメ風"),
        ("ukiyo", "浮世絵風"),
        ("music video", "MV風"),
        ("cinematic", "映画風"),
        ("realistic", "リアル"),
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
- reason_ja must be short Japanese, maximum 2 sentences.

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


def _to_ja(category, value):
    if not value:
        return "未判定"

    raw = str(value).strip()
    key = raw.lower()

    if category in DISPLAY_JA:
        direct = DISPLAY_JA[category].get(key)
        if direct:
            return direct

    for keyword, label in KEYWORD_JA.get(category, []):
        if keyword in key:
            return label

    return raw


def _clean_reason(reason):
    if not reason:
        return "画像の雰囲気に合わせて、最も映える映像プランを選びました。"

    reason = str(reason).replace("\n", " ").strip()
    sentences = re.split(r"(?<=[。.!?！？])", reason)
    short_reason = "".join(sentences[:2]).strip()

    return short_reason or reason[:80]


def normalize_plan(plan):
    plan["service"] = "Kling"

    if not plan.get("romance"):
        plan["romance"] = "none"

    plan["reason_ja"] = _clean_reason(plan.get("reason_ja"))

    plan["display"] = {
        "subject_type": _to_ja("subject_type", plan.get("subject_type")),
        "scene": _to_ja("scene", plan.get("scene")),
        "mood": _to_ja("mood", plan.get("mood")),
        "romance": _to_ja("romance", plan.get("romance")),
        "camera": _to_ja("camera", plan.get("camera")),
        "time": _to_ja("time", plan.get("time")),
        "style": _to_ja("style", plan.get("style")),
        "service": "Kling",
    }

    return plan


def _fallback_plan(text):
    plan = {
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

    return normalize_plan(plan)


def parse_plan(response):
    if hasattr(response, "parsed") and response.parsed:
        if isinstance(response.parsed, dict):
            return normalize_plan(response.parsed)

        if hasattr(response.parsed, "model_dump"):
            return normalize_plan(response.parsed.model_dump())

        try:
            return normalize_plan(dict(response.parsed))
        except Exception:
            pass

    if not response.text:
        raise ValueError("AI Selectから返答がありませんでした。")

    cleaned = response.text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return normalize_plan(json.loads(cleaned))
    except Exception:
        return _fallback_plan(cleaned)
