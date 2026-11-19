from django.urls import path
from .views import (
    team_list_view, team_detail_view, team_create_view,
    register_team_for_tournament_view, add_player_to_team_view,
    captain_dashboard_view, send_join_request_view,
    respond_join_request_view, cancel_join_request_view,
    remove_player_from_team_view
)

urlpatterns = [
    path('', team_list_view, name='team_list'),
    path('captain/dashboard/', captain_dashboard_view, name='captain_dashboard'),
    path('create/', team_create_view, name='team_create'),
    path('<int:pk>/', team_detail_view, name='team_detail'),
    path('<int:tournament_id>/register-team/', register_team_for_tournament_view, name='register_team_tournament'),
    path('<int:team_id>/add-player/', add_player_to_team_view, name='add_player_to_team'),
    path('<int:team_id>/join-request/', send_join_request_view, name='send_join_request'),
    path('join-requests/<int:request_id>/<str:action>/', respond_join_request_view, name='respond_join_request'),
    path('join-requests/<int:request_id>/cancel/', cancel_join_request_view, name='cancel_join_request'),
    path('<int:team_id>/remove-player/<int:player_id>/', remove_player_from_team_view, name='remove_player_from_team'),
]
