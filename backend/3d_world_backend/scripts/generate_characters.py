import os
import django
import json
from django.conf import settings
from app.models import Character, Family, World
from app.lib.generate_text_response_gpt4 import generate_text_response

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "civs.settings")
django.setup()

def create_character_from_json(character_data, world, family):
    character = Character(
        world=world,
        name=character_data['name'],
        profession=character_data['profession'],
        family_role=character_data['family_role'],
        age=character_data['age'],
        sex=character_data['gender'],
        freedom="FREE",
        personality=character_data['personality'],
        tribe=character_data['tribe'],
        region=character_data['region'],
        religion=character_data['religion'],
        backstory=character_data.get('backstory', ''),
        citizenship=character_data['citizenship'],
        family=family  # Associate character with the family
    )
    character.save()
    return character


def run():
    world, created = World.objects.get_or_create(title="Ancient Rome")

    families = []
    characters = []
    while len(characters) < 100:
        existing_family_character_data = ""
        for family in families:
            existing_family_character_data += f"Family: {family.family_name}. Members: "
            for member in family.members.all():
                existing_family_character_data += f"{member.name} ({member.family_role}), Age {member.age}, Profession {member.profession}; "

        family_prompt = [
            {"role": "system", "content": "You are a historian creating detailed family profiles and social graphs for a simulation of ancient Rome in 42 BCE."},
            {"role": "user", "content": f"""Generate JSON profile of a family with description and the following attributes: `name`, `profession`, `family_role`, `age`, `gender`, `personality` (Meyers Briggs four letter code), `tribe`, `region`, `religion`. Avoid repeating existing family names and attributes. The current families and characters of the world are as follows: {existing_family_character_data} Format the json response like this: {{
                "family_name": "Faustus",
                "members": [{{
                    "name": "Tityrus",
                    "citizenship": "Roman",
                    "profession": "Shepherd",
                    "family_role": "Father",
                    "age": 41,
                    "gender": "Male",
                    "personality": "INFP",
                    "tribe": "Romilia",
                    "region": "Regio XI - Circus Maximus",
                    "religion": "Polytheistic Roman",
                }},{{
                    "name": "Amaryllis",
                    "citizenship": "Roman",
                    "profession": "Shepherdess",
                    "family_role": "Mother",
                    "age": 36,
                    "gender": "Female",
                    "personality": "ENFP",
                    "tribe": "Romilia",
                    "region": "Regio XI - Circus Maximus",
                    "religion": "Polytheistic Roman",
                    "backstory": ""
                }}]}}"""
            }
        ]



        family_response = generate_text_response(family_prompt, json_format=True)
        family_data = json.loads(family_response)

        family = Family(
            family_name=family_data['family_name'],
            home_id="" 
        )
        family.save()
        families.append(family)

        for character_data in family_data['members']:
            # Create the character without backstory first
            new_char = create_character_from_json(character_data, world, family)
            characters.append(new_char)
        
        # Second pass: Generate detailed backstories for each character
        for family in families:
            for character in family.members.all():
                # Prepare a string for the prompt about the character's family members
                family_members_data = ""
                for member in family.members.all():
                    if member != character:
                        family_members_data += f"{member.name} ({member.family_role}), Age {member.age}, Profession {member.profession}; "

                # Full world characters - exclude the character's family from this
                existing_family_character_data = ""
                for fam in families:
                    if fam != family:
                        existing_family_character_data += f"Family: {fam.family_name}. Members: "
                        for member in fam.members.all():
                            existing_family_character_data += f"{member.name} ({member.family_role}), Age {member.age}, Profession {member.profession}; "

                backstory_prompt = [
                    {"role": "system", "content": "You are a historian providing detailed backstories for characters in an ancient Roman city simulation."},
                    {"role": "user", "content": f"""Generate a detailed backstory for the following character in the context of their family and world. 
                    Character: {character.name}, {character.family_role}, Age {character.age}, Profession {character.profession}, Personality {character.personality}, Tribe {character.tribe}, Region {character.region}, Religion {character.religion}. 
                    The character's family members are: {family_members_data}
                    The current families and characters of the world are as follows: {existing_family_character_data}. 
                    Respond with only the backstory. Focus on a backstory with detailed sections and character motivations up to their current point in life."""}
                ]

                backstory_response = generate_text_response(backstory_prompt)

                # Update character with backstory
                char_instance = Character.objects.get(id=character.id)
                char_instance.backstory = backstory_response
                char_instance.save()

if __name__ == "__main__":
    run()
