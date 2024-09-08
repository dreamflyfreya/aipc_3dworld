from django.core.management.base import BaseCommand
from app.models import Character
from app.lib.generate_avatar_image import generate_avatar_image
from django.core.files.base import ContentFile
import base64

class Command(BaseCommand):
    help = 'Generate avatar images for characters without an avatar'

    def handle(self, *args, **kwargs):
        characters_without_avatar = Character.objects.filter(avatar__isnull=True)
        for character in characters_without_avatar:
            world = character.world
            family = character.family
            family_members = family.members.exclude(id=character.id) if family else []
            family_members_data = "; ".join([f"{member.name} ({member.family_role}), Age {member.age}, Profession {member.profession}" for member in family_members])
            
            prompt_parts = [
                f"Create a pixel art avatar image of a character named {character.name}. The avatar should focus on the character's chest and head, depicting them in their environment.",
                f"In ancient {character.region}." if character.region else "",
                f"The character's description is: {character.profession}." if character.profession else "",
                f"{character.age} years old." if character.age else "",
                f"{character.personality} personality." if character.personality else "",
                f"They live in the world of {world.title}." if world and world.title else "",
                f"During the {world.time_period}." if world and world.time_period else "",
                f"The world description is: {world.description}." if world and world.description else "",
                f"Their family includes {character.family.family_name}." if family and character.family_name else "",
                f"Their role is {character.family_role}." if character.family_role else "",
                f"Family members: {family_members_data}." if family_members_data else "",
                f"Citizenship: {character.citizenship}." if character.citizenship else "",
                f"Gender: {character.sex}." if character.sex else "",
                f"Freedom status: {character.freedom}." if character.freedom else "",
                f"Tribe: {character.tribe}." if character.tribe else "",
                f"Religion: {character.religion}." if character.religion else "",
                f"Backstory: {character.backstory}." if character.backstory else "",
                f"Additional details: Home building ID: {character.home_building_id}." if character.home_building_id else "",
                f"Work building ID: {character.work_building_id}." if character.work_building_id else "",
                "Ensure the pixel art style is detailed yet consistent. No text or words should be included in the image."
            ]
            
            prompt = " ".join(filter(None, prompt_parts))
            
            # Check if the prompt is too long
            max_length = 4000  # Adjust this value based on the API's limit
            if len(prompt) > max_length:
                # Truncate the backstory to fit within the limit
                truncated_backstory = character.backstory[:max_length - len(prompt) + len(character.backstory) - 3] + "..."
                prompt_parts = [
                    f"Create a pixel art avatar image of a character named {character.name}. The avatar should focus on the character's chest and head, depicting them in their environment.",
                    f"In ancient {character.region}." if character.region else "",
                    f"The character's description is: {character.profession}." if character.profession else "",
                    f"{character.age} years old." if character.age else "",
                    f"{character.personality} personality." if character.personality else "",
                    f"They live in the world of {world.title}." if world and world.title else "",
                    f"During the {world.time_period}." if world and world.time_period else "",
                    f"The world description is: {world.description}." if world and world.description else "",
                    f"Their family includes {character.family.family_name}." if family and character.family_name else "",
                    f"Their role is {character.family_role}." if character.family_role else "",
                    f"Family members: {family_members_data}." if family_members_data else "",
                    f"Citizenship: {character.citizenship}." if character.citizenship else "",
                    f"Gender: {character.sex}." if character.sex else "",
                    f"Freedom status: {character.freedom}." if character.freedom else "",
                    f"Tribe: {character.tribe}." if character.tribe else "",
                    f"Religion: {character.religion}." if character.religion else "",
                    f"Backstory: {truncated_backstory}." if truncated_backstory else "",
                    f"Additional details: Home building ID: {character.home_building_id}." if character.home_building_id else "",
                    f"Work building ID: {character.work_building_id}." if character.work_building_id else "",
                    "Ensure the pixel art style is detailed."
                ]
                prompt = " ".join(filter(None, prompt_parts))
            
            print(prompt)
            response = generate_avatar_image(prompt, character.id)
            # response = None
            print(response)

            if response and len(response.data):
                avatar_data = response.data[0].b64_json
                # Save the avatar data to the character model
                character.avatar.save(f"{character.id}_avatar.png", ContentFile(base64.b64decode(avatar_data)))
                character.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully generated avatar for character {character.name}"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to generate avatar for character {character.name}"))