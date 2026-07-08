from google.genai import types


def generate_config(json_mode=False):

    if json_mode:
        return types.GenerateContentConfig(
            temperature=0.20,
            top_p=0.85,
            max_output_tokens=1200,
            response_mime_type="application/json",
        )

    return types.GenerateContentConfig(
        temperature=0.40,
        top_p=0.85,
        max_output_tokens=1800,
    )


def build_contents(parts):
    return [
        types.Content(
            role="user",
            parts=parts,
        )
    ]


def recommend_request(client, model, parts, schema):

    return client.models.generate_content(
        model=model,
        contents=build_contents(parts),
        config=types.GenerateContentConfig(
            temperature=0.20,
            top_p=0.85,
            max_output_tokens=1200,
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )


def prompt_request(client, model, parts):

    return client.models.generate_content(
        model=model,
        contents=build_contents(parts),
        config=types.GenerateContentConfig(
            temperature=0.40,
            top_p=0.85,
            max_output_tokens=1800,
        ),
    )
