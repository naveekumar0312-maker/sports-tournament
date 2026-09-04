from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from accounts.models import User
from locations.models import District, Taluk
from tournaments.models import Tournament
from teams.models import Team, TournamentRegistration
from players.models import PlayerProfile
from matches.models import Match
from prizes.models import Prize
from notifications.models import Notification
from notifications.services import create_notification, notify_team_members, notify_tournament_participants

class Command(BaseCommand):
    help = 'Seeds realistic demo data for Tamil Nadu Cricket Tournament system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding Demo Data for Tamil Nadu Cricket Tournaments...'))

        # Ensure locations exist
        chennai_dist, _ = District.objects.get_or_create(name="Chennai", defaults={'region': 'North'})
        kovai_dist, _ = District.objects.get_or_create(name="Coimbatore", defaults={'region': 'West'})
        madurai_dist, _ = District.objects.get_or_create(name="Madurai", defaults={'region': 'South'})
        trichy_dist, _ = District.objects.get_or_create(name="Tiruchirappalli", defaults={'region': 'Central'})

        mylapore_taluk, _ = Taluk.objects.get_or_create(name="Mylapore", district=chennai_dist)
        kovai_s_taluk, _ = Taluk.objects.get_or_create(name="Coimbatore South", district=kovai_dist)

        # 1. Create Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@tncricket.org',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '9876543210',
                'bio': 'State Cricket Association System Administrator'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        # 2. Create Tournament Organizers
        org1, created = User.objects.get_or_create(
            username='organizer_chennai',
            defaults={
                'email': 'chennai.org@tncricket.org',
                'role': User.Role.ORGANIZER,
                'phone_number': '9840123456',
                'bio': 'Official Chennai District Cricket Tournament Organizer'
            }
        )
        if created:
            org1.set_password('password123')
            org1.save()

        org2, created = User.objects.get_or_create(
            username='organizer_kovai',
            defaults={
                'email': 'kovai.org@tncricket.org',
                'role': User.Role.ORGANIZER,
                'phone_number': '9842123456',
                'bio': 'Official Kovai Zone Cricket Event Organizer'
            }
        )
        if created:
            org2.set_password('password123')
            org2.save()

        # 3. Create Players & Player Profiles
        players_data = [
            ("player_vijay", "Vijay Kumar", "BATSMAN", "RIGHT_HAND", "RIGHT_ARM_SPIN", chennai_dist, "9876500001"),
            ("player_karthik", "Dinesh Karthik", "WICKET_KEEPER", "RIGHT_HAND", "NONE", chennai_dist, "9876500002"),
            ("player_ashwin", "Ravi Ashwin", "ALL_ROUNDER", "RIGHT_HAND", "RIGHT_ARM_SPIN", chennai_dist, "9876500003"),
            ("player_sundar", "Washington Sundar", "ALL_ROUNDER", "LEFT_HAND", "RIGHT_ARM_SPIN", kovai_dist, "9876500004"),
            ("player_natarajan", "T. Natarajan", "BOWLER", "LEFT_HAND", "LEFT_ARM_FAST", madurai_dist, "9876500005"),
            ("player_shahrukh", "Shahrukh Khan", "BATSMAN", "RIGHT_HAND", "RIGHT_ARM_SPIN", kovai_dist, "9876500006"),
            ("player_jagadeesan", "N. Jagadeesan", "WICKET_KEEPER", "RIGHT_HAND", "NONE", trichy_dist, "9876500007"),
            ("player_sai", "Sai Sudharsan", "BATSMAN", "LEFT_HAND", "RIGHT_ARM_SPIN", chennai_dist, "9876500008"),
        ]

        player_profiles = []
        for uname, fname, role, bat, bowl, dist, mobile in players_data:
            p_user, u_created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': f"{uname}@tncricket.org",
                    'role': User.Role.PLAYER,
                    'phone_number': mobile
                }
            )
            if u_created:
                p_user.set_password('password123')
                p_user.save()

            profile, _ = PlayerProfile.objects.get_or_create(
                user=p_user,
                defaults={
                    'full_name': fname,
                    'date_of_birth': date(1998, 5, 15),
                    'mobile_number': mobile,
                    'district': dist,
                    'playing_role': role,
                    'batting_style': bat,
                    'bowling_style': bowl,
                    'player_status': 'AVAILABLE'
                }
            )
            player_profiles.append(profile)

        # 4. Create Tournaments
        t1, _ = Tournament.objects.get_or_create(
            name="Tamil Nadu Premier Trophy 2026 - Chennai",
            defaults={
                'tournament_type': 'T20',
                'description': 'Premier T20 Cricket Championship for top district clubs across Tamil Nadu.',
                'district': chennai_dist,
                'taluk': mylapore_taluk,
                'venue': 'MA Chidambaram Cricket Ground, Chepauk',
                'start_date': date.today() - timedelta(days=2),
                'end_date': date.today() + timedelta(days=10),
                'registration_start_date': date.today() - timedelta(days=20),
                'registration_end_date': date.today() - timedelta(days=5),
                'entry_fee': 5000.00,
                'organizer': org1,
                'contact_phone': '9840123456',
                'contact_email': 'chennai.org@tncricket.org',
                'max_teams': 8,
                'status': Tournament.Status.ONGOING
            }
        )

        t2, _ = Tournament.objects.get_or_create(
            name="Kovai Zone District Championship 2026",
            defaults={
                'tournament_type': '10_OVER',
                'description': 'High-octane 10-Over knockouts featuring Western Zone Tamil Nadu clubs.',
                'district': kovai_dist,
                'taluk': kovai_s_taluk,
                'venue': 'SNR College Cricket Stadium, Coimbatore',
                'start_date': date.today() + timedelta(days=7),
                'end_date': date.today() + timedelta(days=12),
                'registration_start_date': date.today() - timedelta(days=10),
                'registration_end_date': date.today() + timedelta(days=5),
                'entry_fee': 3000.00,
                'organizer': org2,
                'contact_phone': '9842123456',
                'contact_email': 'kovai.org@tncricket.org',
                'max_teams': 12,
                'status': Tournament.Status.REGISTRATION_OPEN
            }
        )

        # 5. Create Teams
        team_csk, _ = Team.objects.get_or_create(
            name="Chennai Super Kings XI",
            defaults={
                'short_code': 'CSK',
                'district': chennai_dist,
                'captain': player_profiles[0], # Vijay Kumar
                'vice_captain': player_profiles[2], # Ashwin
                'created_by': org1
            }
        )

        team_kek, _ = Team.objects.get_or_create(
            name="Kovai Express Kings",
            defaults={
                'short_code': 'KEK',
                'district': kovai_dist,
                'captain': player_profiles[3], # Sundar
                'vice_captain': player_profiles[5], # Shahrukh
                'created_by': org2
            }
        )

        team_mpx, _ = Team.objects.get_or_create(
            name="Madurai Panthers XI",
            defaults={
                'short_code': 'MPX',
                'district': madurai_dist,
                'captain': player_profiles[4], # Natarajan
                'created_by': org1
            }
        )

        team_trw, _ = Team.objects.get_or_create(
            name="Trichy Warriors",
            defaults={
                'short_code': 'TRW',
                'district': trichy_dist,
                'captain': player_profiles[6], # Jagadeesan
                'created_by': org1
            }
        )

        # Assign players to teams
        player_profiles[0].current_team = team_csk; player_profiles[0].save()
        player_profiles[1].current_team = team_csk; player_profiles[1].save()
        player_profiles[2].current_team = team_csk; player_profiles[2].save()
        player_profiles[7].current_team = team_csk; player_profiles[7].save()

        player_profiles[3].current_team = team_kek; player_profiles[3].save()
        player_profiles[5].current_team = team_kek; player_profiles[5].save()

        player_profiles[4].current_team = team_mpx; player_profiles[4].save()
        player_profiles[6].current_team = team_trw; player_profiles[6].save()

        # 6. Register Teams for Tournament 1
        for tm in [team_csk, team_kek, team_mpx, team_trw]:
            TournamentRegistration.objects.get_or_create(
                tournament=t1,
                team=tm,
                defaults={'status': 'APPROVED'}
            )

        # 7. Create Matches / Fixtures
        m1, _ = Match.objects.get_or_create(
            tournament=t1,
            round_name="Group Stage - Match 1",
            team_a=team_csk,
            team_b=team_kek,
            defaults={
                'match_date': date.today() - timedelta(days=1),
                'match_time': '14:30:00',
                'venue': 'Chepauk Stadium Ground A',
                'status': Match.Status.COMPLETED,
                'toss_winner': team_csk,
                'toss_decision': Match.TossDecision.BAT,
                'team_a_score': '192/5 (20.0 ov)',
                'team_b_score': '178/8 (20.0 ov)',
                'winner': team_csk,
                'win_margin': 'Won by 14 runs',
                'man_of_the_match': player_profiles[0], # Vijay Kumar
                'is_result_published': True
            }
        )

        m2, _ = Match.objects.get_or_create(
            tournament=t1,
            round_name="Group Stage - Match 2",
            team_a=team_mpx,
            team_b=team_trw,
            defaults={
                'match_date': date.today(),
                'match_time': '16:00:00',
                'venue': 'Chepauk Stadium Ground B',
                'status': Match.Status.LIVE,
                'team_a_score': '145/6 (17.2 ov)',
                'team_b_score': 'Yet to Bat',
            }
        )

        m3, _ = Match.objects.get_or_create(
            tournament=t1,
            round_name="Group Stage - Match 3",
            team_a=team_csk,
            team_b=team_trw,
            defaults={
                'match_date': date.today() + timedelta(days=1),
                'match_time': '10:00:00',
                'venue': 'Chepauk Main Pitch',
                'status': Match.Status.SCHEDULED,
            }
        )

        # 8. Create Tournament Prizes
        Prize.objects.get_or_create(
            tournament=t1,
            category=Prize.Category.FIRST,
            defaults={'amount_value': 100000.00, 'description': 'Trophy + ₹1,00,000 Cash Prize for Champions'}
        )
        Prize.objects.get_or_create(
            tournament=t1,
            category=Prize.Category.SECOND,
            defaults={'amount_value': 50000.00, 'description': 'Runners Up Trophy + ₹50,000 Cash Prize'}
        )
        Prize.objects.get_or_create(
            tournament=t1,
            category=Prize.Category.MAN_OF_MATCH,
            defaults={'amount_value': 5000.00, 'description': 'Cash award & Memento per match'}
        )
        Prize.objects.get_or_create(
            tournament=t1,
            category=Prize.Category.BEST_BATSMAN,
            defaults={'amount_value': 10000.00, 'description': 'Custom Bat & Cash Prize'}
        )
        Prize.objects.get_or_create(
            tournament=t1,
            category=Prize.Category.BEST_BOWLER,
            defaults={'amount_value': 10000.00, 'description': 'Puma Spike Shoes & Cash Prize'}
        )

        # 9. Create Notifications
        notify_tournament_participants(
            t1,
            f"Fixture Released: {m1.team_a.name} vs {m1.team_b.name}",
            f"Match scheduled at {m1.venue} on {m1.match_date}.",
            Notification.Type.FIXTURE_ANNOUNCEMENT,
            related_link=f"/matches/{m1.id}/"
        )

        notify_tournament_participants(
            t1,
            f"Match Result Published: {m1.team_a.name} Won!",
            f"{m1.team_a.name} ({m1.team_a_score}) defeated {m1.team_b.name} ({m1.team_b_score}). {m1.win_margin}.",
            Notification.Type.MATCH_RESULT,
            related_link=f"/matches/{m1.id}/"
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded realistic Tamil Nadu Cricket demo data!"))
        self.stdout.write(self.style.WARNING("Superuser Admin login: username='admin', password='admin123'"))
        self.stdout.write(self.style.WARNING("Organizer login: username='organizer_chennai', password='password123'"))
        self.stdout.write(self.style.WARNING("Player login: username='player_vijay', password='password123'"))
