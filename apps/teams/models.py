from django.db import models
from django.conf import settings

class Team(models.Model):
    name = models.CharField(max_length=150)
    short_code = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)
    
    district = models.ForeignKey('locations.District', on_delete=models.SET_NULL, null=True, blank=True, related_name='teams')
    taluk = models.ForeignKey('locations.Taluk', on_delete=models.SET_NULL, null=True, blank=True, related_name='teams')
    village = models.ForeignKey('locations.Village', on_delete=models.SET_NULL, null=True, blank=True, related_name='teams')

    
    captain = models.ForeignKey('players.PlayerProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='captain_teams')
    vice_captain = models.ForeignKey('players.PlayerProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='vice_captain_teams')
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_teams')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.short_code})"

    @property
    def total_players(self):
        return self.members.count()

class TournamentRegistration(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name='registrations')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tournament_registrations')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPROVED)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tournament', 'team')
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.team.name} in {self.tournament.name} ({self.get_status_display()})"
