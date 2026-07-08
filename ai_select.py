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
Return JSON only.

User Settings:
romance_mode = {romance_mode}
romance_level = {romance_level}

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

Japanese Output Rules:
- scene must be Japanese.
- mood must be Japanese.
- camera must be Japanese.
- time must be Japanese.
- style must be Japanese.
- reason_ja must be Japanese and maximum 2 short sentences.

Human Count Rules:
- If two or more humans are visible in the uploaded image or images, subject_type must be couple.
- If two separate human reference images are uploaded, subject_type must be couple.
- If only one human is visible, subject_type must be person.
- Do not classify two visible humans as person.
- Do not ignore the second human.

Romance Rules:
- If romance_mode is off, romance must be none.
- If romance_mode is on and two or more humans are visible, romance must NOT be none.
- If romance_mode is on and two separate human reference images are uploaded, romance must NOT be none.
- If romance_mode is on and romance_level is soft, choose holding hands, looking into each other's eyes, or warm hug.
- If romance_mode is on and romance_level is romantic, choose warm hug, forehead kiss, dancing together, or looking into each other's eyes.
- If romance_mode is on and romance_level is passionate, choose warm hug, gentle kiss, embracing in the rain, or looking into each other's eyes.
- If romance_mode is on but only one human is visible and no second human reference image exists, romance must be none.
- Never generate explicit or sexual content.
- Romance must be tasteful, cinematic, and non-explicit.

Image Fidelity Rules:
- Use only visible background elements.
- Do not add torii gates unless clearly visible.
- Do not add temples unless clearly visible.
- Do not add full moon unless clearly visible.
- Do not add roads, mountains, forests, or buildings unless visible.
- Preserve identity.
- Preserve clothing.
- Preserve hairstyle.
- Preserve accessories.
- Preserve visible objects.
- Preserve visible creatures.
- Preserve atmosphere.
- Do not invent unnecessary characters.

Good Examples:
scene: 室内のベッドルーム
mood: 穏やかで温かい
camera: ドリーショット
time: 室内照明
style: 映画風
reason_ja: 画像に写る2人の雰囲気を活かし、自然で控えめなロマンス演出を選びました。

Return valid JSON only.
Do not use markdown.
Do not use code fences.
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
