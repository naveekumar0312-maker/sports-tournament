from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PlayerProfile
from .forms import PlayerProfileForm
from locations.models import District

from tournaments.models import Tournament

def player_list_view(request):
    players = PlayerProfile.objects.all().select_related('district', 'taluk', 'village', 'current_team')

    role_filter = request.GET.get('role')
    district_filter = request.GET.get('district')
    search_query = request.GET.get('q')

    if role_filter:
        players = players.filter(playing_role=role_filter)
    if district_filter:
        players = players.filter(district_id=district_filter)
    if search_query:
        players = players.filter(full_name__icontains=search_query)

    districts = District.objects.all()

    return render(request, 'players/player_list.html', {
        'players': players,
        'districts': districts,
        'selected_role': role_filter,
        'selected_district': district_filter,
        'search_query': search_query,
    })

def player_profile_detail_view(request, pk):
    profile = get_object_or_404(
        PlayerProfile.objects.select_related('user', 'district', 'taluk', 'village', 'current_team'),
        pk=pk
    )
    
    # Calculate statistics automatically via dynamic engine
    batting_stats = profile.get_batting_stats()
    bowling_stats = profile.get_bowling_stats()
    fielding_stats = profile.get_fielding_stats()

    # Match-by-match performances
    recent_performances = profile.match_performances.select_related(
        'match', 'match__tournament', 'match__team_a', 'match__team_b', 'match__winner'
    ).order_by('-match__match_date')

    mom_awards = profile.mom_awards.select_related('tournament', 'team_a', 'team_b').all()
    prizes_won = profile.prizes_won.select_related('tournament').all()

    # Tournaments player's team is participating in
    tournaments = []
    if profile.current_team:
        tournaments = Tournament.objects.filter(
            registrations__team=profile.current_team,
            registrations__status='APPROVED'
        ).select_related('district', 'taluk', 'village').distinct()

    return render(request, 'players/player_profile.html', {
        'profile': profile,
        'batting_stats': batting_stats,
        'bowling_stats': bowling_stats,
        'fielding_stats': fielding_stats,
        'recent_performances': recent_performances,
        'mom_awards': mom_awards,
        'prizes_won': prizes_won,
        'tournaments': tournaments,
    })


@login_required(login_url='login')
def edit_player_profile_view(request):
    profile, created = PlayerProfile.objects.get_or_create(
        user=request.user,
        defaults={'full_name': request.user.username, 'mobile_number': request.user.phone_number or ''}
    )

    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Player profile & cricket statistics settings updated!")
            return redirect('player_profile_detail', pk=profile.pk)
    else:
        form = PlayerProfileForm(instance=profile)

    return render(request, 'players/player_form.html', {
        'form': form,
        'title': 'Edit Cricket Profile'
    })
