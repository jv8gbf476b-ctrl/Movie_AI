# service_rules.py

from google.genai import types


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
            temperature=0.30,
            top_p=0.90,
            max_output_tokens=1000,
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )


def prompt_request(client, model, parts):
    return client.models.generate_content(
        model=model,
        contents=build_contents(parts),
        config=types.GenerateContentConfig(
            temperature=0.50,
            top_p=0.90,
            max_output_tokens=2100,
        ),
    )
