import json
import re

from display_mapper import normalize_plan


def find_value(text, key, default):

    pattern = rf'"{key}"\s*:\s*"([^"]*)"'
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


def fallback_plan(text):

    plan = {
        "subject_type": find_value(text, "subject_type", "other"),
        "scene": find_value(text, "scene", "夜の街"),
        "mood": find_value(text, "mood", "映画風"),
        "romance": find_value(text, "romance", "none"),
        "camera": find_value(text, "camera", "ドリーショット"),
        "time": find_value(text, "time", "夜"),
        "style": find_value(text, "style", "映画風"),
        "service": "Kling",
        "reason_ja": find_value(
            text,
            "reason_ja",
            "画像の雰囲気に合う映像プランを選びました。",
        ),
        "confidence": find_value(text, "confidence", 4),
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

        try:
            return normalize_plan(
                dict(response.parsed)
            )
        except Exception:
            pass

    if not response.text:
        raise ValueError(
            "AI Selectから返答がありませんでした。"
        )

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
        return fallback_plan(cleaned)
