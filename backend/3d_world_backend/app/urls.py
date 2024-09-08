from django.urls import path
from . import views

urlpatterns = [
    path('api/character/<int:pk>/', views.CharacterAPIView.as_view(), name='character-detail'),
    path('api/character/event/', views.CharacterEvent.as_view(), name='character-event'),
    path('api/characters/', views.CharacterListAPIView.as_view(), name='character-list'),  # Added path for character list
    path('rome', views.rome, name="rome"),
    path('', views.index, name="index"),
]