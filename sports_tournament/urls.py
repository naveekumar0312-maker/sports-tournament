from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view
# pyrefly: ignore [missing-import]
from accounts.views import (
    register_view, login_view, logout_view, profile_view,
    admin_dashboard_view, organizer_dashboard_view, player_dashboard_view
)
# pyrefly: ignore [missing-import]
from teams.views import captain_dashboard_view
# pyrefly: ignore [missing-import]
from locations.views import taluks_api_view, villages_api_view

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),

    # Port Opens Directly to Login Page
    path('', login_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    
    # Role-Based Dashboards
    path('dashboard/', player_dashboard_view, name='player_dashboard'),
    path('captain/dashboard/', captain_dashboard_view, name='captain_dashboard_direct'),
    path('organizer/dashboard/', organizer_dashboard_view, name='organizer_dashboard'),
    path('dashboard/admin/', admin_dashboard_view, name='admin_dashboard'),

    # Cascading Location APIs
    path('api/locations/taluks/', taluks_api_view, name='taluks_api_direct'),
    path('locations/api/taluks/', taluks_api_view, name='taluks_api_sub'),
    path('api/locations/villages/', villages_api_view, name='villages_api_direct'),
    path('locations/api/villages/', villages_api_view, name='villages_api_sub'),


    # Feature Apps
    path('locations/', include('locations.urls')),
    path('tournaments/', include('tournaments.urls')),
    path('teams/', include('teams.urls')),
    path('players/', include('players.urls')),
    path('matches/', include('matches.urls')),
    path('prizes/', include('prizes.urls')),
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
