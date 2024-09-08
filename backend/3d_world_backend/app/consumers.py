import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from .models import Character, Event, Message, MemoryEvent
from .lib.stream_text_response_claude_async import stream_text_response_claude_async
from .lib.stream_text_response_oai_async import stream_text_response_async
from .lib.generate_avatar_image import generate_avatar_image
from .lib.describe_character_vision import describe_character_vision


EXAMPLE_DAY_PLAN = {
    'day_overview': 'Take care of my farm and spend time with my family',
    'actions': [{
        'action': 'Harvest olives',
        'emoji': '🫒',
        'location': 'Olive Orchard',
    }, {
        'action': 'Ask Simichidas how his day is going',
        'emoji': '💬',
        'location': 'Simichidas',
    }, {
        'action': 'Make offering to Ceres',
        'emoji': '🤲',
        'location': 'Household Shrine',
    }, {
        'action': 'Greet the new stranger to our farm',
        'emoji': '💬',
        'location': 'Player',
    }]
}


class CharacterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):

        if bytes_data:
            try:
                text_data = bytes_data.decode('utf-8')
                text_data_json = json.loads(text_data)

                print(' -- receiving transmission')
                print(text_data_json)

                event_type = text_data_json.get('type')

                if event_type == 'character_planner':
                    character_id = text_data_json.get('character_id')
                    character = await self.get_character(character_id)
                    game_world_date = text_data_json.get('game_world_date')
                    game_world_place_setting = text_data_json.get('game_world_place_setting')
                    waypoint_names = text_data_json.get('waypoint_names')
                    npc_names = text_data_json.get('npc_names')
                    player_names = text_data_json.get('player_names')
                    await self.stream_plan(character, game_world_date, game_world_place_setting, waypoint_names, npc_names, player_names)

                elif event_type == 'character_event':
                    character_id = text_data_json.get('character_id')
                    character = await self.get_character(character_id)
                    event_description = text_data_json.get('description')
                    event_location = text_data_json.get('location')
                    game_world_place_setting = text_data_json.get('game_world_place_setting')
                    game_world_date_time = text_data_json.get('game_world_date_time')
                    if event_description and event_location:
                        await self.create_event(character, event_description, event_location)

                elif event_type == 'character_conversation':
                    character_id = text_data_json.get('character_id')
                    character = await self.get_character(character_id)
                    user_uuid = text_data_json.get('user_uuid')
                    message = text_data_json.get('message')
                    game_world_place_setting = text_data_json.get('game_world_place_setting')
                    game_world_date_time = text_data_json.get('game_world_date_time')
                    current_day_plan = text_data_json.get('current_day_plan')
                    current_action = text_data_json.get('current_action')
                    current_location = text_data_json.get('current_location')
                    extra_instruction = text_data_json.get('extra_instruction')

                    if message:
                        await self.stream_respond(character, message, game_world_place_setting, game_world_date_time, current_day_plan, current_action, current_location, extra_instruction, user_uuid)

                elif event_type == 'generate_avatar':
                    await self.handle_avatar_generation(text_data_json)

                elif event_type == 'character_vision':
                    base64_image = text_data_json.get('base64_image')
                    if base64_image:
                        description = await describe_character_vision(base64_image)
                        await self.send(text_data=json.dumps({'type': 'vision_response', 'description': description}))

                elif event_type == 'character_memory':
                    character_id = text_data_json.get('character_id')
                    character = await self.get_character(character_id)
                    description = text_data_json.get('description')
                    location = text_data_json.get('location')
                    priority = text_data_json.get('priority')
                    user_id = text_data_json.get('user_id')
                    await self.create_memory_event(character, description, location, priority, user_id)

            except json.JSONDecodeError:
                # print("Invalid JSON data received")
                pass

    async def get_character(self, character_id):
        return await sync_to_async(Character.objects.get, thread_sensitive=True)(id=character_id)

    async def create_event(self, character, description, location):
        event = Event(character=character, description=description, priority=1, location=location)
        await sync_to_async(event.save, thread_sensitive=True)()

    async def create_message(self, character, message):
        user_message = Message(content=message, character=character, sender="user")
        await sync_to_async(user_message.save, thread_sensitive=True)()

    async def stream_plan(self, character, game_world_date, game_world_place_setting, waypoint_names, npc_names, player_names):
        print(" -- streaming response for", character.name, game_world_date, waypoint_names, npc_names, player_names)

        messages = []
        role = "user"

        messages.append({"role": role, "content": f"You just woke up. The date is {game_world_date} in {game_world_place_setting}. Plan your day. Respond in json format like this: {json.dumps(EXAMPLE_DAY_PLAN)}. Your available locations are {waypoint_names}. In the environment are these characters: {npc_names}. There are players: {player_names}. Include a single relevant emoji for display purposes with each task. Only include a single unicode character, no skin tone data." })

        # sending complete json plan 
        complete_plan = await self.generate_complete_plan(character, messages, game_world_place_setting)
        await self.send(bytes_data=json.dumps({'type': 'plan_response', 'character_id': character.id, 'message': complete_plan }).encode('utf-8'))

    async def generate_complete_plan(self, character, messages, game_world_place_setting):
        system_message = f"You are roleplaying as a character in ancient {game_world_place_setting}. You plan your day actions for your character. Plan your day. Respond in json format like this: {json.dumps(EXAMPLE_DAY_PLAN)}. If you want to go to a location to complete a task, state that location. If you want to go to a character or a player to engage in conversation, put the character or player name as the location. Include a single relevant emoji for display purposes with each task. Only include a single unicode character, no skin tone data. {self.make_system_message(character)}"
        full_message = ""
        async for event_text in stream_text_response_async(character, messages, system_message, { "type": "json_object" }):
            full_message += event_text

        return full_message

    async def stream_respond(self, character, incoming_message, game_world_date_time, game_world_place_setting, current_day_plan, current_action, current_location, extra_instruction, user_uuid):
        messages = []
        # system_message = f"You are roleplaying as a character in ancient {game_world_place_setting}. Respond in character to the player asking questions. Do not include any text between asterisks--only include dialog. Never break character. For example, if the player asks 'How are you?', respond with something like 'I am doing well, thank you for asking.' without any asterisks or stage directions. {self.make_system_message(character)}."
        system_message = f"""You are a character in ancient {game_world_place_setting} on {game_world_date_time}. 
            Reflect on your character and respond to the player asking questions as if you were your character with the outward and inward psychological motivations of your character's identity. 
            Respond with emotional sensitivity and intelligence. Respond in the language that the player speaks. 
            Focus on being historically accurate to the time and place specified. 
            Do not be creative.
            Be Historically accurate.
            Be informal.
            Speak in conversational language.
            Be colloquial.
            Contemplate your character. Consider and respond from your characters inner pyschological state. Generate a response in character based on their environmental social and pyschological factors.
            Consider the motivations of your character. Why are they behaving the way they are? Compose your response to the player like that in the roleplaying scenario. 
            Only include your character's words in your response.
            Never break character for any reason. 

            {self.make_system_message(character)}"""

        # conversation history
        context_messages = await sync_to_async(list)(
            Message.objects.filter(character=character, user_uuid=user_uuid)
            .order_by('timestamp')[:10]
            .values('sender', 'content')
        )
        messages = [{"role": m['sender'], "content": m['content']} for m in context_messages]

        # Save user's message AFTER querying message history
        user_message = Message(character=character, content=incoming_message, sender="user", user_uuid=user_uuid)  
        await sync_to_async(user_message.save)()


        message = f'Respond to the player. It is {game_world_date_time} in {game_world_place_setting}.' 

        if current_day_plan and current_action and current_location:
            message += f'Your plan for the day is {current_day_plan}. Youre currently {current_action}. Youre located at {current_location}.'

        message += f'Player asks: {incoming_message}'

        if extra_instruction:
            message += f' {extra_instruction}'

        messages.append({"role": "user", "content": message})


        assistant_response = ""
        async for message in stream_text_response_async(character, messages, system_message):

            # remove newline and return characters
            message = message.replace('\n', ' ').replace('\r', '')
            if message and len(message):
                assistant_response += message
                await self.send(text_data=json.dumps({'type': 'conversation_response', 'character_id': character.id, 'message': message}))

        # Save the complete assistant response as a single Message
        assistant_message = Message(character=character, content=assistant_response, sender="assistant", user_uuid=user_uuid)
        await sync_to_async(assistant_message.save)()

    def make_system_message(self, character):
        system_message = f"Your name is {character.name}. Your citizenship is {character.citizenship}. Your profession is {character.profession}. Your age is {character.age}. Your gender is {character.sex}. Your personality is {character.personality}. Your tribe is {character.tribe}. Your religion is {character.religion}. Your region is {character.region}. Your backstory is {character.backstory}."

        return system_message

    async def handle_avatar_generation(self, data):
        civilization = data.get('civilization')
        art_style = data.get('art_style')
        name = data.get('name')
        description = data.get('description')

        user_id = data.get('user_id')

        prompt = f"Create an image of a character in ancient {civilization}. "

        if art_style == "Pixel Art":
            prompt += f"Make the image in detailed pixel art style. "

        else: 
            prompt += f"Make the image in the {art_style} art style. "

        if name:
            prompt += f"The character's name is {name}. "

        if description:
            prompt += f"The character's description is: {description}. "

        prompt += "Focus on making the image historically accurate to the ancient civilization and time period represented."

        print("Generating avatar:", prompt)

        # Generate the image
        response = generate_avatar_image(prompt, user_id)
        if response and len(response.data):
            await self.send(text_data=json.dumps({
                'type': 'avatar_generated', 
                'response': { 
                    'b64_json': response.data[0].b64_json,
                },
            }))
        else:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Failed to generate image'}))

    async def create_memory_event(self, character, description, location, priority, user_id=None):
        memory_event = MemoryEvent(
            character=character,
            description=description,
            place_name=location,
            priority=priority,
            user_id=user_id
        )
        await sync_to_async(memory_event.save, thread_sensitive=True)()

