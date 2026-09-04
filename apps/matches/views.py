from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Match, PlayerMatchPerformance
from .forms import MatchForm, MatchScoreForm, PlayerMatchPerformanceForm
from tournaments.models import Tournament
from players.models import PlayerProfile
from notifications.services import notify_team_members, notify_tournament_participants
from notifications.models import Notification

def match_detail_view(request, pk):
    match = get_object_or_404(Match.objects.select_related('tournament', 'team_a', 'team_b', 'toss_winner', 'winner', 'man_of_the_match'), pk=pk)
    performances = match.player_performances.select_related('player', 'team').all()

    return render(request, 'matches/match_detail.html', {
        'match': match,
        'performances': performances
    })

@login_required(login_url='login')
def match_create_view(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    if not (request.user == tournament.organizer or request.user.is_admin_role):
        messages.error(request, "Only the organizer can schedule matches.")
        return redirect('tournament_detail', pk=tournament_id)

    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            match.tournament = tournament
            match.save()

            notify_tournament_participants(
                tournament,
                f"New Fixture Scheduled: {match.team_a.name} vs {match.team_b.name}",
                f"Match round: {match.round_name} at {match.venue or tournament.venue} on {match.match_date}.",
                Notification.Type.FIXTURE_ANNOUNCEMENT,
                related_link=f"/matches/{match.id}/"
            )

            messages.success(request, f"Match fixture '{match.team_a.name} vs {match.team_b.name}' scheduled!")
            return redirect('tournament_detail', pk=tournament_id)
    else:
        form = MatchForm()

    return render(request, 'matches/match_form.html', {
        'form': form,
        'tournament': tournament,
        'title': 'Schedule New Match Fixture'
    })

@login_required(login_url='login')
def match_update_score_view(request, pk):
    match = get_object_or_404(Match, pk=pk)

    if not (request.user == match.tournament.organizer or request.user.is_admin_role):
        messages.error(request, "Permission denied.")
        return redirect('match_detail', pk=pk)

    was_published_before = match.is_result_published
    performances = match.player_performances.select_related('player', 'team').all()

    if request.method == 'POST':
        form = MatchScoreForm(request.POST, instance=match)
        if form.is_valid():
            updated_match = form.save()

            if updated_match.is_result_published and not was_published_before:
                winner_name = updated_match.winner.name if updated_match.winner else "Match Draw"
                
                notify_tournament_participants(
                    updated_match.tournament,
                    f"Match Result Published: {updated_match.team_a.short_code} vs {updated_match.team_b.short_code}",
                    f"Winner: {winner_name}. Scores: {updated_match.team_a.name} ({updated_match.team_a_score or 'N/A'}) vs {updated_match.team_b.name} ({updated_match.team_b_score or 'N/A'}). {updated_match.win_margin or ''}",
                    Notification.Type.MATCH_RESULT,
                    related_link=f"/matches/{updated_match.id}/"
                )
                messages.success(request, "Match scores updated and results published to all participants!")
            else:
                messages.success(request, "Match details updated successfully.")

            return redirect('match_detail', pk=pk)
    else:
        form = MatchScoreForm(instance=match)

    return render(request, 'matches/match_score_form.html', {
        'form': form,
        'match': match,
        'performances': performances,
    })

@login_required(login_url='login')
def add_player_performance_view(request, match_id):
    match = get_object_or_404(Match, pk=match_id)

    if not (request.user == match.tournament.organizer or request.user.is_admin_role):
        messages.error(request, "Permission denied.")
        return redirect('match_detail', pk=match_id)

    # Players in Team A and Team B
    team_a_players = PlayerProfile.objects.filter(current_team=match.team_a)
    team_b_players = PlayerProfile.objects.filter(current_team=match.team_b)
    participating_players = team_a_players | team_b_players

    if request.method == 'POST':
        form = PlayerMatchPerformanceForm(request.POST)
        if form.is_valid():
            perf = form.save(commit=False)
            perf.match = match
            perf.save()

            messages.success(request, f"Match performance added for {perf.player.full_name}! Career stats updated.")
            return redirect('match_update_score', pk=match_id)
    else:
        form = PlayerMatchPerformanceForm()

    return render(request, 'matches/performance_form.html', {
        'form': form,
        'match': match,
        'participating_players': participating_players,
    })
