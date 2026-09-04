from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from locations.models import District, Taluk
from tournaments.models import Tournament
from teams.models import Team, TournamentRegistration
from players.models import PlayerProfile
from matches.models import Match, PlayerMatchPerformance
from datetime import date

class SportsTournamentSystemTest(TestCase):
    def setUp(self):
        # Create District & Taluk
        self.chennai = District.objects.create(name="Chennai", region="North")
        self.mylapore = Taluk.objects.create(name="Mylapore", district=self.chennai)

        # Create Users
        self.admin = User.objects.create_superuser('test_admin', 'admin@test.com', 'pass123', role='ADMIN')
        self.organizer = User.objects.create_user('test_org', 'org@test.com', 'pass123', role='ORGANIZER')
        self.player_user = User.objects.create_user('test_player', 'player@test.com', 'pass123', role='PLAYER')

        # Player Profile with Cricket attributes
        self.player_profile = PlayerProfile.objects.create(
            user=self.player_user,
            full_name="Naveen Kumar",
            district=self.chennai,
            playing_role="ALL_ROUNDER",
            batting_style="RIGHT_HAND",
            batting_position="TOP_ORDER",
            bowling_style="RIGHT_ARM_FAST",
            bowling_type="PACE",
            jersey_number=7
        )

        # Tournament
        self.tournament = Tournament.objects.create(
            name="Chennai T20 League 2026",
            tournament_type="T20",
            description="T20 League",
            district=self.chennai,
            taluk=self.mylapore,
            venue="MA Chidambaram Stadium",
            start_date=date.today(),
            end_date=date.today(),
            registration_start_date=date.today(),
            registration_end_date=date.today(),
            entry_fee=5000.00,
            organizer=self.organizer,
            contact_phone="9876543210",
            contact_email="org@test.com"
        )

        # Teams
        self.team_a = Team.objects.create(name="Chennai Super Kings", short_code="CSK", district=self.chennai, created_by=self.organizer)
        self.team_b = Team.objects.create(name="Kovai Kings", short_code="KK", district=self.chennai, created_by=self.organizer)

        self.player_profile.current_team = self.team_a
        self.player_profile.save()

        # Match
        self.match = Match.objects.create(
            tournament=self.tournament,
            round_name="Final",
            team_a=self.team_a,
            team_b=self.team_b,
            match_date=date.today(),
            status=Match.Status.COMPLETED
        )

    def test_automatic_player_statistics_calculation(self):
        # Record Match Performance for Naveen Kumar
        PlayerMatchPerformance.objects.create(
            player=self.player_profile,
            match=self.match,
            team=self.team_a,
            batting_status='NOT_OUT',
            runs=102,
            balls_faced=62,
            fours=8,
            sixes=5,
            overs_bowled=4.0,
            runs_conceded=18,
            wickets=4,
            catches=2
        )

        bat_stats = self.player_profile.get_batting_stats()
        bowl_stats = self.player_profile.get_bowling_stats()
        field_stats = self.player_profile.get_fielding_stats()

        # Verify Batting stats
        self.assertEqual(bat_stats['matches'], 1)
        self.assertEqual(bat_stats['runs'], 102)
        self.assertEqual(bat_stats['highest_score'], 102)
        self.assertEqual(bat_stats['hundreds'], 1)
        self.assertEqual(bat_stats['fours'], 8)
        self.assertEqual(bat_stats['sixes'], 5)
        self.assertEqual(bat_stats['strike_rate'], 164.52)

        # Verify Bowling stats
        self.assertEqual(bowl_stats['wickets'], 4)
        self.assertEqual(bowl_stats['best_bowling'], '4/18')
        self.assertEqual(bowl_stats['economy'], 4.5)
        self.assertEqual(bowl_stats['four_wickets'], 1)

        # Verify Fielding stats
        self.assertEqual(field_stats['catches'], 2)

    def test_login_flow_player(self):
        response = self.client.post(reverse('login'), {'username': 'test_player', 'password': 'pass123'})
        self.assertRedirects(response, reverse('player_dashboard'))

    def test_login_flow_organizer(self):
        response = self.client.post(reverse('login'), {'username': 'test_org', 'password': 'pass123'})
        self.assertRedirects(response, reverse('organizer_dashboard'))
