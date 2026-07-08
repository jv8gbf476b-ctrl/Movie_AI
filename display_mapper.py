import re


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
        ("city", "街並み"),
        ("street", "街並み"),
        ("night", "夜の街"),
        ("mountain", "山"),
        ("park", "公園"),
        ("shrine", "神社"),
        ("temple", "寺院"),
        ("festival", "祭り"),
    ],
    "mood": [
        ("cinematic", "映画風"),
        ("dark fantasy", "ダークファンタジー"),
        ("romantic", "ロマンチック"),
        ("emotional", "感動的"),
        ("cool", "クール"),
        ("cute", "かわいい"),
        ("dramatic", "ドラマチック"),
        ("mysterious", "神秘的"),
    ],
    "camera": [
        ("medium", "ミディアムショット"),
        ("close", "クローズアップ"),
        ("tracking", "追従カメラ"),
        ("dolly", "ドリーショット"),
        ("drone", "ドローン撮影"),
        ("handheld", "手持ちカメラ"),
        ("wide", "ワイドショット"),
    ],
    "time": [
        ("night", "夜"),
        ("morning", "朝"),
        ("day", "昼"),
        ("sunset", "夕方"),
        ("rain", "雨"),
        ("snow", "雪"),
        ("moon", "月夜"),
    ],
    "style": [
        ("cinematic", "映画風"),
        ("dark fantasy", "ダークファンタジー"),
        ("japanese dark fantasy", "和風ダークファンタジー"),
        ("anime", "アニメ風"),
        ("music video", "MV風"),
        ("realistic", "リアル"),
    ],
}


def clean_reason(reason):

    if not reason:
        return "画像の雰囲気に合う映像プランを選びました。"

    reason = str(reason).replace("\n", " ").strip()

    sentences = re.split(r"(?<=[。！？])", reason)

    short = "".join(sentences[:2]).strip()

    return short if short else reason[:80]


def to_ja(category, value):

    if value is None:
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


def normalize_plan(plan):

    plan["service"] = "Kling"

    if not plan.get("romance"):
        plan["romance"] = "none"

    plan["subject_type"] = to_ja(
        "subject_type",
        plan.get("subject_type"),
    )

    plan["romance"] = to_ja(
        "romance",
        plan.get("romance"),
    )

    plan["scene"] = to_ja(
        "scene",
        plan.get("scene"),
    )

    plan["mood"] = to_ja(
        "mood",
        plan.get("mood"),
    )

    plan["camera"] = to_ja(
        "camera",
        plan.get("camera"),
    )

    plan["time"] = to_ja(
        "time",
        plan.get("time"),
    )

    plan["style"] = to_ja(
        "style",
        plan.get("style"),
    )

    plan["reason_ja"] = clean_reason(
        plan.get("reason_ja"),
    )

    return plan
