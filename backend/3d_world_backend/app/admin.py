from django.contrib import admin
from .models import CustomUser, World, Message, Event, Character, Family, World 

admin.site.register(CustomUser)
admin.site.register(Message)
admin.site.register(Event)
admin.site.register(Character)
admin.site.register(Family)
admin.site.register(World)
