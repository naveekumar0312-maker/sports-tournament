from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin / System Superuser'
        ORGANIZER = 'ORGANIZER', 'Tournament Organizer'
        PLAYER = 'PLAYER', 'Cricket Player'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PLAYER
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_approved_organizer = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_organizer_role(self):
        return self.role == self.Role.ORGANIZER or self.is_superuser

    @property
    def is_player_role(self):
        return self.role == self.Role.PLAYER or not (self.is_organizer_role or self.is_admin_role)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
