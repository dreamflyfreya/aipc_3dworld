from rest_framework import serializers
from .models import Character, Message, Event

class MessageSerializer(serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'character', 'content', 'sender', 'timestamp', 'media_url', 'image_url']

    def get_media_url(self, obj):
        return obj.get_media_url()

    def get_image_url(self, obj):
        return obj.get_image_url()

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'start_time', 'end_time', 'location']

class CharacterSerializer(serializers.ModelSerializer):
    sent_messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = ['id', 'world', 'name', 'citizenship', 'profession', 'family', 'family_role', 'age', 'sex', 'freedom', 'personality', 'tribe', 'religion', 'region', 'backstory', 'avatar', 'sent_messages', 'home_building_id', 'work_building_id']