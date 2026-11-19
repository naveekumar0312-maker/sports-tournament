from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Team, TournamentRegistration, TeamJoinRequest
from .forms import TeamForm
from tournaments.models import Tournament
from players.models import PlayerProfile
from matches.models import Match
from notifications.services import create_notification, notify_team_members
from notifications.models import Notification

def team_list_view(request):
    teams = Team.objects.all().select_related('district', 'captain', 'created_by')
    player_profile = getattr(request.user, 'player_profile', None) if request.user.is_authenticated else None
    
    pending_team_ids = []
    if player_profile:
        pending_team_ids = list(TeamJoinRequest.objects.filter(
            player=player_profile,
            status=TeamJoinRequest.Status.PENDING
        ).values_list('team_id', flat=True))

    return render(request, 'teams/team_list.html', {
        'teams': teams,
        'player_profile': player_profile,
        'pending_team_ids': pending_team_ids,
    })

def team_detail_view(request, pk):
    team = get_object_or_404(Team.objects.select_related('district', 'taluk', 'captain', 'vice_captain', 'created_by'), pk=pk)
    members = team.members.select_related('user', 'district').all()
    registrations = team.tournament_registrations.select_related('tournament').all()

    # Join requests for this team (visible to captain/creator/admin)
    join_requests = []
    is_team_manager = request.user.is_authenticated and (request.user == team.created_by or request.user.is_admin_role)
    if is_team_manager:
        join_requests = team.join_requests.filter(status=TeamJoinRequest.Status.PENDING).select_related('player', 'player__district')

    # Available players to add
    available_players = PlayerProfile.objects.filter(current_team__isnull=True)

    # Check if current user has requested or joined
    user_request_status = None
    player_profile = getattr(request.user, 'player_profile', None) if request.user.is_authenticated else None
    if player_profile:
        existing_req = TeamJoinRequest.objects.filter(team=team, player=player_profile).first()
        if existing_req:
            user_request_status = existing_req.status

    return render(request, 'teams/team_detail.html', {
        'team': team,
        'members': members,
        'registrations': registrations,
        'available_players': available_players,
        'join_requests': join_requests,
        'is_team_manager': is_team_manager,
        'user_request_status': user_request_status,
        'player_profile': player_profile,
    })

@login_required
def captain_dashboard_view(request):
    user = request.user
    if not (user.is_captain_role or user.is_admin_role):
        messages.warning(request, "This dashboard is exclusively for Team Captains and Owners.")
        return redirect('player_dashboard')

    my_teams = Team.objects.filter(created_by=user).select_related('district', 'captain')
    
    # If captain has no team yet, offer to create one
    if not my_teams.exists():
        messages.info(request, "Please create your team first to start managing your squad and tournaments.")
        return redirect('team_create')

    active_team = my_teams.first()

    # Incoming Join Requests from Players
    pending_requests = TeamJoinRequest.objects.filter(
        team__in=my_teams,
        status=TeamJoinRequest.Status.PENDING
    ).select_related('player', 'player__district', 'team')

    processed_requests = TeamJoinRequest.objects.filter(
        team__in=my_teams
    ).exclude(status=TeamJoinRequest.Status.PENDING).select_related('player', 'team')[:10]

    # Current Squad
    squad_members = PlayerProfile.objects.filter(current_team__in=my_teams).select_related('user', 'district')

    # Available Players in Tamil Nadu to Scout
    available_players = PlayerProfile.objects.filter(current_team__isnull=True).select_related('district')[:25]

    # Tournaments hosted by Naveen Cricket Tournament Organization
    open_tournaments = Tournament.objects.all().order_by('-start_date')
    registered_tournament_ids = list(TournamentRegistration.objects.filter(
        team__in=my_teams
    ).values_list('tournament_id', flat=True))

    # Matches for Captain's Team
    upcoming_matches = Match.objects.filter(
        Q(team_a__in=my_teams) | Q(team_b__in=my_teams),
        status='SCHEDULED'
    ).select_related('team_a', 'team_b', 'tournament').order_by('match_date', 'match_time')

    recent_results = Match.objects.filter(
        Q(team_a__in=my_teams) | Q(team_b__in=my_teams),
        status='COMPLETED'
    ).select_related('team_a', 'team_b', 'winner', 'tournament').order_by('-match_date')

    return render(request, 'dashboards/captain_dashboard.html', {
        'my_teams': my_teams,
        'active_team': active_team,
        'pending_requests': pending_requests,
        'processed_requests': processed_requests,
        'squad_members': squad_members,
        'available_players': available_players,
        'open_tournaments': open_tournaments,
        'registered_tournament_ids': registered_tournament_ids,
        'upcoming_matches': upcoming_matches,
        'recent_results': recent_results,
    })

@login_required
def send_join_request_view(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    player_profile = getattr(request.user, 'player_profile', None)

    if not player_profile:
        messages.error(request, "Only registered cricket players can send join requests.")
        return redirect('team_detail', pk=team_id)

    if player_profile.current_team == team:
        messages.info(request, f"You are already in {team.name} squad!")
        return redirect('team_detail', pk=team_id)

    if request.method == 'POST':
        message_note = request.POST.get('message', '').strip()
        
        req, created = TeamJoinRequest.objects.get_or_create(
            team=team,
            player=player_profile,
            defaults={'message': message_note, 'status': TeamJoinRequest.Status.PENDING}
        )

        if not created:
            if req.status == TeamJoinRequest.Status.REJECTED:
                req.status = TeamJoinRequest.Status.PENDING
                req.message = message_note
                req.save()
                messages.success(request, f"Join request re-sent to {team.name}!")
            elif req.status == TeamJoinRequest.Status.PENDING:
                messages.info(request, f"You already have a pending join request for {team.name}.")
            else:
                messages.info(request, f"You are already a member of {team.name}.")
        else:
            messages.success(request, f"Join request sent successfully to {team.name}! Captain will review your request.")
            
            # Notify Team Captain
            if team.created_by:
                create_notification(
                    team.created_by,
                    f"New Squad Join Request: {player_profile.full_name}",
                    f"{player_profile.full_name} ({player_profile.get_playing_role_display()}) requested to join your team '{team.name}'.",
                    Notification.Type.PLAYER_ADDED,
                    related_link="/captain/dashboard/"
                )

    return redirect(request.META.get('HTTP_REFERER') or f'/teams/{team_id}/')

@login_required
def respond_join_request_view(request, request_id, action):
    join_req = get_object_or_404(TeamJoinRequest.objects.select_related('team', 'player', 'player__user'), pk=request_id)
    team = join_req.team

    # Verify authorization
    if not (request.user == team.created_by or request.user.is_admin_role):
        messages.error(request, "You are not authorized to manage join requests for this team.")
        return redirect('team_detail', pk=team.pk)

    if action == 'accept':
        join_req.status = TeamJoinRequest.Status.ACCEPTED
        join_req.save()

        # Add player to squad
        player = join_req.player
        player.current_team = team
        player.player_status = PlayerProfile.Status.IN_TEAM
        player.save()

        # Reject any other pending requests from this player
        TeamJoinRequest.objects.filter(
            player=player,
            status=TeamJoinRequest.Status.PENDING
        ).exclude(id=join_req.id).update(status=TeamJoinRequest.Status.REJECTED)

        # Notify Player
        if player.user:
            create_notification(
                player.user,
                f"Accepted into Team: {team.name}!",
                f"Congratulations! Captain {request.user.get_full_name() or request.user.username} accepted your request to join {team.name}.",
                Notification.Type.PLAYER_ADDED,
                related_link=f"/teams/{team.id}/"
            )

        messages.success(request, f"Player '{player.full_name}' accepted into {team.name} squad!")

    elif action == 'reject':
        join_req.status = TeamJoinRequest.Status.REJECTED
        join_req.save()

        # Notify Player
        if join_req.player.user:
            create_notification(
                join_req.player.user,
                f"Join Request Update from {team.name}",
                f"Your request to join {team.name} was not accepted at this time.",
                Notification.Type.PLAYER_ADDED,
                related_link="/teams/"
            )

        messages.info(request, f"Join request from '{join_req.player.full_name}' has been declined.")

    return redirect(request.META.get('HTTP_REFERER') or '/captain/dashboard/')

@login_required
def cancel_join_request_view(request, request_id):
    player_profile = getattr(request.user, 'player_profile', None)
    if not player_profile:
        return redirect('player_dashboard')

    join_req = get_object_or_404(TeamJoinRequest, pk=request_id, player=player_profile)
    team_name = join_req.team.name
    join_req.delete()
    messages.success(request, f"Join request for {team_name} cancelled.")
    return redirect('player_dashboard')

@login_required
def remove_player_from_team_view(request, team_id, player_id):
    team = get_object_or_404(Team, pk=team_id)
    if not (request.user == team.created_by or request.user.is_admin_role):
        messages.error(request, "You are not authorized to manage this team squad.")
        return redirect('team_detail', pk=team_id)

    player = get_object_or_404(PlayerProfile, pk=player_id, current_team=team)
    player.current_team = None
    player.player_status = PlayerProfile.Status.AVAILABLE
    player.save()

    messages.success(request, f"Player '{player.full_name}' has been removed from {team.name} squad.")
    return redirect(request.META.get('HTTP_REFERER') or f'/teams/{team_id}/')

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
                profile.player_status = PlayerProfile.Status.IN_TEAM
                profile.save()
                if not team.captain:
                    team.captain = profile
                    team.save()

            messages.success(request, f"Team '{team.name}' created successfully!")
            return redirect('captain_dashboard')
    else:
        form = TeamForm()

    return render(request, 'teams/team_form.html', {'form': form, 'title': 'Create New Cricket Team'})

@login_required
def register_team_for_tournament_view(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        team = get_object_or_404(Team, pk=team_id)

        # Check authorization: user must own team or be admin
        if not (request.user == team.created_by or request.user.is_admin_role):
            messages.error(request, "You can only register teams you own/manage.")
            return redirect('tournament_detail', pk=tournament_id)

        reg, created = TournamentRegistration.objects.get_or_create(
            tournament=tournament,
            team=team,
            defaults={'status': 'APPROVED'}
        )

        if created:
            messages.success(request, f"Team '{team.name}' successfully registered for {tournament.name}!")
            
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

    return redirect(request.META.get('HTTP_REFERER') or f'/tournaments/{tournament_id}/')

@login_required
def add_player_to_team_view(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    
    if not (request.user == team.created_by or request.user.is_admin_role):
        messages.error(request, "You are not authorized to add players to this team.")
        return redirect('team_detail', pk=team_id)

    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        player = get_object_or_404(PlayerProfile, pk=player_id)

        player.current_team = team
        player.player_status = PlayerProfile.Status.IN_TEAM
        player.save()

        # If there was a pending request, mark it accepted
        TeamJoinRequest.objects.filter(team=team, player=player).update(status=TeamJoinRequest.Status.ACCEPTED)

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

    return redirect(request.META.get('HTTP_REFERER') or f'/teams/{team_id}/')
