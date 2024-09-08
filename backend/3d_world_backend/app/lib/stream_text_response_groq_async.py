import asyncio
from groq import GroqClient
from django.conf import settings
import time
from app.models import Message
from aiostream import stream

error_message = "...I'm sorry, I'm not feeling myself right now. Talk to me later."

async def stream_text_response_async(character, messages, system="", response_format=None):
    # calculate start time while debugging
    start_time = time.time()

    # get response from api
    client = GroqClient(api_key=settings.GROQ_API_KEY)
    system_message = {
        "role": "system",
        "content": system,
    }

    # Prepend the system message to the messages list
    messages.insert(0, system_message)

    try:
        response_stream = client.chat.completions.create(
            model="llama-3.1-405b-reasoning",
            response_format=response_format,
            messages=messages,
            stream=True,
        )
    except Exception as e:
        print(e)
        yield error_message 
        return

    # create variables to collect the stream of events
    collected_events = []
    completion_text = ''
    message_content = ''
    token_counter = 0
    text_buffer = ''
    paragraph_buffer = []

    # set the number of tokens to accumulate before sending a message
    tokens_per_message = 30

    # convert the response stream to an asynchronous iterator
    async for event in response_stream:
        event_time = time.time() - start_time # calculate the time delay of the event
        collected_events.append(event) # save the event response

        if hasattr(event.choices[0], 'delta') and hasattr(event.choices[0].delta, 'content'):
            event_text = event.choices[0].delta.content  # extract the text
            if event_text and len(event_text):
                yield event_text