from django.urls import path
from .views import (
    player_list_view, player_profile_detail_view, edit_player_profile_view
)

urlpatterns = [
    path('', player_list_view, name='player_list'),
    path('edit-profile/', edit_player_profile_view, name='edit_player_profile'),
    path('<int:pk>/', player_profile_detail_view, name='player_profile_detail'),
]
