import json
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404, HttpResponseBadRequest

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.models import Character, World, Message, Event, Character
from app.serializers import CharacterSerializer
from rest_framework.generics import ListAPIView
from rest_framework.renderers import JSONRenderer



def index(request):
    worlds = World.objects.all()
    return render(request, 'index.twig', {
            'worlds': worlds,
        })



def rome(request):
    world = World.objects.get(id=1)
    return render(request, 'world.twig', {
            'world': world,
        })



class CharacterAPIView(APIView):
    def get(self, request, pk, format=None):
        try:
            character = Character.objects.get(pk=pk)
            serializer = CharacterSerializer(character)
            return Response(serializer.data)
        except Character.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)



class CharacterEvent(APIView):
    def post(self, request):
        event_description = request.data["Description"]
        event_location = request.data["Location"]
        character_id = request.data["CharacterId"]
        character = Character.objects.get(id=character_id)

        event = Event(character=character, description=event_description, priority=1, location=event_location)
        event.save()

        return JsonResponse({'status': 'ok'})



class CharacterListAPIView(ListAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    renderer_classes = [JSONRenderer]  # Ensure the response is in JSON format