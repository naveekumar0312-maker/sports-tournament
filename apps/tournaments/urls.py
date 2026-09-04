from django.urls import path
from .views import (
    tournament_list_view, tournament_detail_view,
    tournament_create_view, tournament_edit_view
)

urlpatterns = [
    path('', tournament_list_view, name='tournament_list'),
    path('create/', tournament_create_view, name='tournament_create'),
    path('<int:pk>/', tournament_detail_view, name='tournament_detail'),
    path('<int:pk>/edit/', tournament_edit_view, name='tournament_edit'),
]
