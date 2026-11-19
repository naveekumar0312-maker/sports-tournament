from django.db import models
from django.conf import settings

class Tournament(models.Model):
    class TournamentType(models.TextChoices):
        T20 = 'T20', 'T20 Format'
        TEN_OVER = '10_OVER', '10 Overs Format'
        KNOCKOUT = 'KNOCKOUT', 'Knockout Tournament'
        LEAGUE_KNOCKOUT = 'LEAGUE_KNOCKOUT', 'League + Knockout'
        BOX_CRICKET = 'BOX_CRICKET', 'Box Cricket / Indoor'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        UPCOMING = 'UPCOMING', 'Upcoming'
        REGISTRATION_OPEN = 'REGISTRATION_OPEN', 'Registration Open'
        REGISTRATION_CLOSED = 'REGISTRATION_CLOSED', 'Registration Closed'
        ONGOING = 'ONGOING', 'Ongoing'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    name = models.CharField(max_length=200)
    tournament_type = models.CharField(
        max_length=50,
        choices=TournamentType.choices,
        default=TournamentType.T20
    )
    description = models.TextField()
    district = models.ForeignKey('locations.District', on_delete=models.SET_NULL, null=True, related_name='tournaments')
    taluk = models.ForeignKey('locations.Taluk', on_delete=models.SET_NULL, null=True, blank=True, related_name='tournaments')
    village = models.ForeignKey('locations.Village', on_delete=models.SET_NULL, null=True, blank=True, related_name='tournaments')

    venue = models.CharField(max_length=255)
    
    start_date = models.DateField()
    end_date = models.DateField()
    registration_start_date = models.DateField()
    registration_end_date = models.DateField()
    
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total Tournament Prize Pool (Rs)")
    rules_and_regulations = models.TextField(blank=True, null=True, help_text="Tournament rules and guidelines")
    exact_location = models.CharField(max_length=255, blank=True, null=True, help_text="Exact ground/stadium location or map address")

    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_tournaments')
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    max_teams = models.PositiveIntegerField(default=16)
    
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.REGISTRATION_OPEN
    )
    banner = models.ImageField(upload_to='tournament_banners/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} - {self.district.name if self.district else 'TN'}"

    @property
    def registered_teams_count(self):
        return self.registrations.filter(status='APPROVED').count()
