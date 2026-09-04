from django.urls import path
from .views import prize_create_view

urlpatterns = [
    path('tournament/<int:tournament_id>/create/', prize_create_view, name='prize_create'),
]
