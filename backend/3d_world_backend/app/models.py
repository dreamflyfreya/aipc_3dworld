import os
import uuid
import mimetypes
import urllib.request

from django.contrib.auth.models import AbstractUser
from django.db import models


PUBLIC = 'PUBLIC'
PRIVATE = 'PRIVATE'
PRIVACY_CHOICES = [
    (PUBLIC, 'Public'),
    (PRIVATE, 'Private'),
]




class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=256, blank=True)
    title = models.CharField(max_length=1024, blank=True)
    biography = models.TextField(blank=True)
    profile_photo = models.ImageField(
        upload_to='profile_images', blank=True)
    email_verified = models.BooleanField(default=False, blank=True)
    membership = models.TextField(blank=True)

    profile_photo_google = models.TextField(blank=True)
    google_oauth_jwt = models.TextField(blank=True)

    def __str__(self):
        return self.username



class World(models.Model):
    title = models.CharField(max_length=1024, blank=True)
    time_period = models.CharField(max_length=1024, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    user_uuid = models.CharField(max_length=255, null=True, blank=True)
    sender = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    media = models.FileField(upload_to='media/', blank=True, null=True)
    image = models.ImageField(upload_to='media/', blank=True, null=True)

    def __str__(self):
        return f"Message with {self.character} on {self.timestamp}"

    def get_media_url(self):
        if self.media and self.media.name:
            return f"https://static.mused.org/{self.media.name}"
        else:
            return None 

    def get_image_url(self):
        if self.image and self.image.name:
            return f"https://static.mused.org/{self.image.name}"
        else:
            return None 


class Event(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='events')
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.id}-{self.character.id}: {self.description[:90]}"

class Family(models.Model):
    family_name = models.CharField(max_length=100)
    home_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.family_name

class Character(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE, related_name='characters', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    citizenship = models.CharField(max_length=255, null=True, blank=True)
    profession = models.CharField(max_length=255, null=True, blank=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='members', null=True, blank=True)
    family_role = models.CharField(max_length=255, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    sex = models.CharField(max_length=255, null=True, blank=True)
    freedom = models.CharField(max_length=255, null=True, blank=True)
    personality = models.CharField(max_length=255, null=True, blank=True)
    tribe = models.CharField(max_length=255, null=True, blank=True)
    religion = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    backstory = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to='character_avatar/', blank=True, null=True)

    home_building_id = models.IntegerField(null=True, blank=True)
    work_building_id = models.IntegerField(null=True, blank=True)


    def __str__(self):
        if self.name:
            return f"{self.id} {self.name}"

    def get_most_recent_message(self):
        latest_message = Message.objects.filter(character=self.id, sender="user").order_by('-timestamp').first()
        return latest_message

    def get_unread_messages(self):
        unread_messages = Message.objects.filter(character=self.id, read=False)
        return unread_messages

    def get_avatar_url(self):
        if self.user and self.user.picture:
            return f"https://iiif.mused.org/{self.user.picture.name}/full/full/0/default.jpg"
        else:
            return static('images/default_user.jpg')

    def time_since_last_user_message(self):
        latest_message = self.get_most_recent_message()
        if latest_message:
            delta = timezone.now() - latest_message.timestamp
            formatted_duration = format_duration(delta)
            return formatted_duration 
        else:
            return None

    def get_character_media(self):
        media_messages = Message.objects.filter(character=self.id).filter(Q(media__isnull=False))
        return media_messages

    def get_character_images(self):
        image_messages = Message.objects.filter(character=self.id).filter(Q(image__isnull=False))
        return image_messages


class MemoryEvent(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='memory_events')
    user_id = models.CharField(max_length=255, null=True, blank=True)
    priority = models.IntegerField(choices=[(i, i) for i in range(1, 11)], default=1)
    place_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.character.name} - {self.description[:50]}"
