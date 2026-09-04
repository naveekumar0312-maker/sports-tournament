from django.db import models

class Prize(models.Model):
    class Category(models.TextChoices):
        FIRST = '1ST_PRIZE', '1st Prize / Champions'
        SECOND = '2ND_PRIZE', '2nd Prize / Runners Up'
        THIRD = '3RD_PRIZE', '3rd Prize / 3rd Place'
        MAN_OF_MATCH = 'MAN_OF_THE_MATCH', 'Man of the Match'
        BEST_BATSMAN = 'BEST_BATSMAN', 'Best Batsman of the Tournament'
        BEST_BOWLER = 'BEST_BOWLER', 'Best Bowler of the Tournament'
        PLAYER_OF_TOURNAMENT = 'PLAYER_OF_THE_TOURNAMENT', 'Player of the Tournament'
        CUSTOM = 'CUSTOM', 'Custom Award'

    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name='prizes')
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.FIRST)
    title_custom = models.CharField(max_length=150, blank=True, null=True, help_text="Fill if Custom Award selected")
    
    amount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)
    
    winner_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='prizes_won')
    winner_player = models.ForeignKey('players.PlayerProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='prizes_won')

    class Meta:
        ordering = ['amount_value']

    @property
    def title(self):
        if self.category == self.Category.CUSTOM and self.title_custom:
            return self.title_custom
        return self.get_category_display()

    def __str__(self):
        return f"{self.title} - ₹{self.amount_value:,.2f} ({self.tournament.name})"
