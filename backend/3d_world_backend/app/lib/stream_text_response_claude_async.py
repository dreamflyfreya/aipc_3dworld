import asyncio
from anthropic import Anthropic
from django.conf import settings
import time
from app.models import Message
from aiostream import stream

error_message = "...I'm sorry, I'm not feeling myself right now. Talk to me later."

async def stream_text_response_claude_async(character, messages, system=""):
    # calculate start time while debugging
    start_time = time.time()

    # get response from api
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    try:
        response_stream = client.messages.create(
            model="claude-3-opus-20240229",
            stream=True,
            messages=messages,
            max_tokens=4000,
            system=system
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
    async for event in stream.iterate(response_stream):
        event_time = time.time() - start_time # calculate the time delay of the event
        collected_events.append(event) # save the event response

        if hasattr(event, 'delta') and hasattr(event.delta, 'text'):
            event_text = event.delta.text # extract the text
            if event_text and len(event_text):
                yield event_text

        if event.type == "message_stop": 
            # Yield a special EOM marker. Adjust the marker based on your needs.
            yield ""