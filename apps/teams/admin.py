from django.contrib import admin
from .models import Team, TournamentRegistration

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_code', 'district', 'captain', 'vice_captain', 'created_by')
    list_filter = ('district',)
    search_fields = ('name', 'short_code', 'captain__full_name')

@admin.register(TournamentRegistration)
class TournamentRegistrationAdmin(admin.ModelAdmin):
    list_display = ('team', 'tournament', 'status', 'registered_at')
    list_filter = ('status', 'tournament')
    search_fields = ('team__name', 'tournament__name')
