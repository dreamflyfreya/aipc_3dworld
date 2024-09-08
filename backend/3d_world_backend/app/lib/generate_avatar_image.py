from openai import OpenAI
from django.conf import settings



client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_avatar_image(prompt, user_id):
    # Generate an image based on the prompt
    response = client.images.generate(prompt=prompt, model="dall-e-3", response_format="b64_json", quality="hd", size="1024x1024", user=f"mused_avatar_generator_user_{user_id}")
    return response