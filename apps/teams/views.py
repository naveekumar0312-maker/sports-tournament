from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Team, TournamentRegistration
from .forms import TeamForm
from tournaments.models import Tournament
from players.models import PlayerProfile
from notifications.services import create_notification, notify_team_members
from notifications.models import Notification

def team_list_view(request):
    teams = Team.objects.all().select_related('district', 'captain', 'created_by')
    return render(request, 'teams/team_list.html', {'teams': teams})

def team_detail_view(request, pk):
    team = get_object_or_404(Team.objects.select_related('district', 'taluk', 'captain', 'vice_captain', 'created_by'), pk=pk)
    members = team.members.select_related('user', 'district').all()
    registrations = team.tournament_registrations.select_related('tournament').all()

    # Available players to add
    available_players = PlayerProfile.objects.filter(current_team__isnull=True)

    return render(request, 'teams/team_detail.html', {
        'team': team,
        'members': members,
        'registrations': registrations,
        'available_players': available_players,
    })

@login_required
def team_create_view(request):
    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES)
        if form.is_valid():
            team = form.save(commit=False)
            team.created_by = request.user
            team.save()

            # If user has a PlayerProfile, assign to team automatically
            if hasattr(request.user, 'player_profile'):
                profile = request.user.player_profile
                profile.current_team = team
                profile.save()
                if not team.captain:
                    team.captain = profile
                    team.save()

            messages.success(request, f"Team '{team.name}' created successfully!")
            return redirect('team_detail', pk=team.pk)
    else:
        form = TeamForm()

    return render(request, 'teams/team_form.html', {'form': form, 'title': 'Create New Cricket Team'})

@login_required
def register_team_for_tournament_view(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        team = get_object_or_404(Team, pk=team_id)

        reg, created = TournamentRegistration.objects.get_or_create(
            tournament=tournament,
            team=team,
            defaults={'status': 'APPROVED'}
        )

        if created:
            messages.success(request, f"Team '{team.name}' registered for {tournament.name}!")
            
            # Notify Team members & Organizer
            notify_team_members(
                team,
                f"Registered for {tournament.name}",
                f"Your team {team.name} has been registered for {tournament.name}.",
                Notification.Type.TOURNAMENT_REGISTRATION,
                related_link=f"/tournaments/{tournament.id}/"
            )
            create_notification(
                tournament.organizer,
                f"New Team Registration: {team.name}",
                f"{team.name} registered for your tournament '{tournament.name}'.",
                Notification.Type.TOURNAMENT_REGISTRATION,
                related_link=f"/tournaments/{tournament.id}/"
            )
        else:
            messages.info(request, f"Team '{team.name}' is already registered for this tournament.")

    return redirect('tournament_detail', pk=tournament_id)

@login_required
def add_player_to_team_view(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    
    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        player = get_object_or_404(PlayerProfile, pk=player_id)

        player.current_team = team
        player.player_status = PlayerProfile.Status.IN_TEAM
        player.save()

        # Notify Player
        if player.user:
            create_notification(
                player.user,
                f"Added to Team: {team.name}",
                f"You have been added to the team '{team.name}'. Welcome aboard!",
                Notification.Type.PLAYER_ADDED,
                related_link=f"/teams/{team.id}/"
            )

        messages.success(request, f"Player '{player.full_name}' added to {team.name}!")

    return redirect('team_detail', pk=team_id)
