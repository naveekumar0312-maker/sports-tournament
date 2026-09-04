from django.contrib import admin
from .models import Match, PlayerMatchPerformance

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'round_name', 'team_a', 'team_b', 'match_date', 'status', 'winner', 'is_result_published')
    list_filter = ('status', 'is_result_published', 'tournament', 'match_date')
    search_fields = ('team_a__name', 'team_b__name', 'round_name', 'venue')

@admin.register(PlayerMatchPerformance)
class PlayerMatchPerformanceAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'team', 'runs', 'balls_faced', 'wickets', 'overs_bowled', 'catches')
    list_filter = ('team', 'batting_status')
    search_fields = ('player__full_name', 'match__tournament__name')
