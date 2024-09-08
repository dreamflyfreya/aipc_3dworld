# generate_text_response.py

from openai import OpenAI
from django.conf import settings
import time
from app.models import Message


def send_message(character, message_content):
    print(character, message_content)
    
    # #setup messaging client
    pass



def stream_text_response_gpt4(character, messages):
    # calculate start time while debugging
    start_time = time.time()

    # get response from api
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        # response_format={ "type": "json_object" },
        messages=messages,
        # max_tokens=4000,
        # n=1,
        # stop=None,
        # temperature=0.7,
        # top_p=0.9,
        stream=True,
    )

    # for debugging, handle any errors
    print("OpenAI response:")
    print(response)

    # create variables to collect the stream of events
    collected_events = []
    completion_text = ''
    message_content = ''
    token_counter = 0 
    text_buffer = ''
    paragraph_buffer = []

    # set the number of tokens to accumulate before sending a message
    tokens_per_message = 30

    # iterate through the stream of events
    for event in response:
        event_time = time.time() - start_time  # calculate the time delay of the event
        collected_events.append(event)  # save the event response

        if hasattr(event.choices[0], 'delta') and hasattr(event.choices[0].delta, 'content'):
            event_text = event.choices[0].delta.content  # extract the text
            if event_text:
                completion_text += event_text  # append the text

            print(f"Text received: {event_text} ({event_time:.2f} seconds after request)")

            text_buffer += event_text
            token_counter += len(event_text.split())
            paragraph_buffer.append(event_text)
            joined_text = ''.join(paragraph_buffer)

            if '\n\n' in joined_text:
                paragraphs = joined_text.split('\n\n')
                message_content = paragraphs[0].strip()
                paragraph_buffer = ['\n\n'.join(paragraphs[1:])]

                send_message(character, message_content)

    # send remaining text
    if ''.join(paragraph_buffer).strip():
        message_content = ''.join(paragraph_buffer).strip()
        send_message(character, message_content)

