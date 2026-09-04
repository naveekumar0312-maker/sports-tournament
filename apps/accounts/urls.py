from django.urls import path
from .views import (
    register_view, login_view, logout_view, profile_view,
    admin_dashboard_view, organizer_dashboard_view, player_dashboard_view
)

urlpatterns = [
    path('register/', register_view, name='accounts_register'),
    path('login/', login_view, name='accounts_login'),
    path('logout/', logout_view, name='accounts_logout'),
    path('profile/', profile_view, name='accounts_profile'),
    path('dashboard/', player_dashboard_view, name='accounts_player_dashboard'),
    path('organizer/dashboard/', organizer_dashboard_view, name='accounts_organizer_dashboard'),
]
