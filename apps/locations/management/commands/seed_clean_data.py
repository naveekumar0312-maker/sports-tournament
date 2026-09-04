from django.core.management.base import BaseCommand
from locations.models import District, Taluk
from tournaments.models import Tournament
from teams.models import Team, TournamentRegistration
from players.models import PlayerProfile
from matches.models import Match, PlayerMatchPerformance
from prizes.models import Prize
from notifications.models import Notification
from accounts.models import User

class Command(BaseCommand):
    help = 'Cleans sample dummy data while keeping Tamil Nadu 38 Districts & Superuser Admin'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Cleaning sample dummy data..."))

        # Clear match performances, matches, prizes, registrations, teams, tournaments, notifications
        PlayerMatchPerformance.objects.all().delete()
        Match.objects.all().delete()
        Prize.objects.all().delete()
        TournamentRegistration.objects.all().delete()
        Team.objects.all().delete()
        Tournament.objects.all().delete()
        Notification.objects.all().delete()

        # Ensure Superuser Admin exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@tncricket.org',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '9876543210',
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        # Seed Locations
        from django.core.management import call_command
        call_command('seed_locations')

        self.stdout.write(self.style.SUCCESS("Database is clean and ready! All 38 Tamil Nadu Districts & Admin active."))
        self.stdout.write(self.style.WARNING("Admin login: username='admin', password='admin123' at /admin/"))
