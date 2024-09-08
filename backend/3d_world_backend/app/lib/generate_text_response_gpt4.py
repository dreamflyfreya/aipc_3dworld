# generate_text_response.py

from openai import OpenAI
from django.conf import settings


def generate_text_response(messages, json_format=False):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    if json_format:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={ "type": "json_object" },
        )

    else:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

    print("OpenAI response:")
    print(response)

    return response.choices[0].message.content
