from django.urls import path
from .views import (
    team_list_view, team_detail_view, team_create_view,
    register_team_for_tournament_view, add_player_to_team_view
)

urlpatterns = [
    path('', team_list_view, name='team_list'),
    path('create/', team_create_view, name='team_create'),
    path('<int:pk>/', team_detail_view, name='team_detail'),
    path('<int:tournament_id>/register-team/', register_team_for_tournament_view, name='register_team_tournament'),
    path('<int:team_id>/add-player/', add_player_to_team_view, name='add_player_to_team'),
]
