from django.contrib import admin
from .models import Prize

@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'title', 'category', 'amount_value', 'winner_team', 'winner_player')
    list_filter = ('category', 'tournament')
    search_fields = ('tournament__name', 'title_custom', 'winner_team__name', 'winner_player__full_name')
