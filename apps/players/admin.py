from django.contrib import admin
from .models import PlayerProfile

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'playing_role', 'district', 'current_team', 'player_status', 'mobile_number')
    list_filter = ('playing_role', 'batting_style', 'bowling_style', 'player_status', 'district')
    search_fields = ('full_name', 'mobile_number', 'user__username')
