from django.contrib import admin
from .models import Tournament

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament_type', 'district', 'taluk', 'status', 'start_date', 'entry_fee', 'organizer')
    list_filter = ('status', 'tournament_type', 'district', 'start_date')
    search_fields = ('name', 'venue', 'organizer__username')
    date_hierarchy = 'start_date'
