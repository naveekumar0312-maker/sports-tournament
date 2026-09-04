from django.shortcuts import render
# pyrefly: ignore [missing-import]
from tournaments.models import Tournament
# pyrefly: ignore [missing-import]
from teams.models import Team
# pyrefly: ignore [missing-import]
from players.models import PlayerProfile
# pyrefly: ignore [missing-import]
from matches.models import Match
# pyrefly: ignore [missing-import]
from locations.models import District

def home_view(request):
    total_tournaments = Tournament.objects.count()
    total_teams = Team.objects.count()
    total_players = PlayerProfile.objects.count()
    total_matches = Match.objects.count()
    total_districts = District.objects.count()

    featured_tournaments = Tournament.objects.filter(
        status__in=['ONGOING', 'REGISTRATION_OPEN', 'UPCOMING']
    )[:6]

    recent_matches = Match.objects.filter(
        status='COMPLETED',
        is_result_published=True
    ).order_by('-updated_at')[:4]

    live_matches = Match.objects.filter(status='LIVE')

    return render(request, 'home.html', {
        'total_tournaments': total_tournaments,
        'total_teams': total_teams,
        'total_players': total_players,
        'total_matches': total_matches,
        'total_districts': total_districts,
        'featured_tournaments': featured_tournaments,
        'recent_matches': recent_matches,
        'live_matches': live_matches,
    })
