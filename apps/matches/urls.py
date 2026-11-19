from django.urls import path
from .views import (
    match_detail_view, match_create_view, match_update_score_view,
    add_player_performance_view, set_live_batsmen_bowler_view, live_ball_record_view
)

urlpatterns = [
    path('<int:pk>/', match_detail_view, name='match_detail'),
    path('tournament/<int:tournament_id>/create/', match_create_view, name='match_create'),
    path('<int:pk>/update-score/', match_update_score_view, name='match_update_score'),
    path('<int:pk>/set-lineup/', set_live_batsmen_bowler_view, name='match_set_lineup'),
    path('<int:pk>/record-ball/', live_ball_record_view, name='match_record_ball'),
    path('<int:match_id>/add-performance/', add_player_performance_view, name='add_player_performance'),
]
