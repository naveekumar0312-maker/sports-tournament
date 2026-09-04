from django.db import models
from django.conf import settings

class Notification(models.Model):
    class Type(models.TextChoices):
        TEAM_REGISTRATION = 'TEAM_REGISTRATION', 'Team Registration Confirmation'
        PLAYER_ADDED = 'PLAYER_ADDED', 'Player Added to Team'
        TOURNAMENT_REGISTRATION = 'TOURNAMENT_REGISTRATION', 'Tournament Registration'
        FIXTURE_ANNOUNCEMENT = 'FIXTURE_ANNOUNCEMENT', 'Match Fixture Announcement'
        MATCH_RESULT = 'MATCH_RESULT', 'Match Result Announcement'
        TOURNAMENT_WINNER = 'TOURNAMENT_WINNER', 'Tournament Winner Announcement'
        PRIZE_ANNOUNCEMENT = 'PRIZE_ANNOUNCEMENT', 'Prize Announcement'
        TOURNAMENT_UPDATE = 'TOURNAMENT_UPDATE', 'Tournament Cancellation / Update'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=Type.choices, default=Type.TOURNAMENT_UPDATE)
    is_read = models.BooleanField(default=False)
    related_link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
