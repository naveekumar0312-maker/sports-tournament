from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import UserRegistrationForm, UserProfileForm
from players.models import PlayerProfile
from tournaments.models import Tournament
from teams.models import Team, TeamJoinRequest
from matches.models import Match
from locations.models import District
from notifications.models import Notification

def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin_role:
            return redirect('admin_dashboard')
        elif request.user.is_captain_role:
            return redirect('captain_dashboard')
        else:
            return redirect('player_dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            
            full_name = form.cleaned_data.get('full_name') or user.username
            name_parts = full_name.split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
            
            user.save()

            # Create appropriate profile based on role
            if user.role == User.Role.CAPTAIN:
                # 1. Create Captain's player profile
                captain_profile = PlayerProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    mobile_number=user.phone_number or '',
                    playing_role=PlayerProfile.PlayingRole.ALL_ROUNDER,
                    batting_style=PlayerProfile.BattingStyle.RIGHT_HAND,
                    bowling_style=PlayerProfile.BowlingStyle.RIGHT_ARM_SPIN,
                )

                # 2. Create the Captain's Team
                team_name = form.cleaned_data.get('team_name') or f"{full_name}'s XI"
                # Generate clean short code (first letters of words or 3-4 chars)
                words = team_name.split()
                short_code = ''.join([w[0].upper() for w in words[:4]])
                if len(short_code) < 2:
                    short_code = team_name[:3].upper()

                team = Team.objects.create(
                    name=team_name,
                    short_code=short_code,
                    created_by=user,
                    captain=captain_profile
                )

                # Link captain to their new team
                captain_profile.current_team = team
                captain_profile.player_status = PlayerProfile.Status.IN_TEAM
                captain_profile.save()

                messages.success(request, f"Welcome Captain {full_name}! Your team '{team.name}' has been created. Please log in.")
                return redirect('login')

            else:
                # Standard Cricket Player
                PlayerProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    mobile_number=user.phone_number or '',
                    playing_role=PlayerProfile.PlayingRole.ALL_ROUNDER,
                    batting_style=PlayerProfile.BattingStyle.RIGHT_HAND,
                    bowling_style=PlayerProfile.BowlingStyle.RIGHT_ARM_SPIN,
                )
                messages.success(request, f"Welcome Player {full_name}! Your player account is ready. Please log in.")
                return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin_role:
            return redirect('admin_dashboard')
        elif request.user.is_captain_role:
            return redirect('captain_dashboard')
        else:
            return redirect('player_dashboard')

    error_message = None
    username_val = ""

    if request.method == 'POST':
        username_val = request.POST.get('username', '').strip()
        password_val = request.POST.get('password', '').strip()

        if not username_val:
            error_message = "Please enter your username."
        elif not password_val:
            error_message = "Please enter your password."
        else:
            user = authenticate(request, username=username_val, password=password_val)
            if user is not None:
                login(request, user)
                if user.is_admin_role:
                    return redirect('admin_dashboard')
                elif user.is_captain_role:
                    return redirect('captain_dashboard')
                else:
                    return redirect('player_dashboard')
            else:
                error_message = "Invalid username or password. Please try again."

    return render(request, 'accounts/login.html', {
        'error_message': error_message,
        'username_val': username_val
    })

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@login_required(login_url='login')
def admin_dashboard_view(request):
    if not request.user.is_admin_role:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('player_dashboard')

    total_users = User.objects.count()
    total_organizers = User.objects.filter(role=User.Role.ORGANIZER).count()
    total_players = PlayerProfile.objects.count()
    total_teams = Team.objects.count()
    total_tournaments = Tournament.objects.count()
    total_matches = Match.objects.count()
    total_districts = District.objects.count()

    recent_tournaments = Tournament.objects.all().order_by('-created_at')[:5]
    recent_users = User.objects.all().order_by('-created_at')[:5]
    recent_matches = Match.objects.all().order_by('-created_at')[:5]

    return render(request, 'dashboards/admin_dashboard.html', {
        'total_users': total_users,
        'total_organizers': total_organizers,
        'total_players': total_players,
        'total_teams': total_teams,
        'total_tournaments': total_tournaments,
        'total_matches': total_matches,
        'total_districts': total_districts,
        'recent_tournaments': recent_tournaments,
        'recent_users': recent_users,
        'recent_matches': recent_matches,
    })

@login_required(login_url='login')
def organizer_dashboard_view(request):
    if not (request.user.is_organizer_role or request.user.is_admin_role):
        messages.error(request, "Access restricted to Tournament Organizers.")
        return redirect('player_dashboard')

    my_tournaments = Tournament.objects.filter(organizer=request.user)
    my_tournament_ids = my_tournaments.values_list('id', flat=True)

    my_teams = Team.objects.filter(tournament_registrations__tournament_id__in=my_tournament_ids).distinct()
    upcoming_matches = Match.objects.filter(tournament_id__in=my_tournament_ids, status='SCHEDULED')
    completed_matches = Match.objects.filter(tournament_id__in=my_tournament_ids, status='COMPLETED')

    return render(request, 'dashboards/organizer_dashboard.html', {
        'my_tournaments': my_tournaments,
        'my_teams': my_teams,
        'upcoming_matches': upcoming_matches,
        'completed_matches': completed_matches,
    })

@login_required(login_url='login')
def player_dashboard_view(request):
    user = request.user
    if user.is_captain_role and not user.is_admin_role:
        return redirect('captain_dashboard')
    elif user.is_admin_role and not hasattr(user, 'player_profile'):
        return redirect('admin_dashboard')

    player_profile = getattr(user, 'player_profile', None)

    my_team = player_profile.current_team if player_profile else None
    my_teams = [my_team] if my_team else []
    
    # Active Tournaments for my team
    my_tournaments = Tournament.objects.filter(
        registrations__team=my_team,
        registrations__status='APPROVED'
    ).distinct() if my_team else []
    
    upcoming_matches = Match.objects.filter(
        tournament__in=my_tournaments, 
        status='SCHEDULED'
    ).select_related('team_a', 'team_b', 'tournament') if my_tournaments else []

    recent_results = Match.objects.filter(
        tournament__in=my_tournaments, 
        status='COMPLETED', 
        is_result_published=True
    ).select_related('team_a', 'team_b', 'winner', 'tournament') if my_tournaments else []

    my_notifications = Notification.objects.filter(recipient=user)[:8]

    # Join Requests sent by this player
    my_join_requests = []
    pending_team_ids = []
    if player_profile:
        my_join_requests = TeamJoinRequest.objects.filter(
            player=player_profile
        ).select_related('team', 'team__captain', 'team__district')
        pending_team_ids = list(my_join_requests.filter(
            status=TeamJoinRequest.Status.PENDING
        ).values_list('team_id', flat=True))

    # All available teams in the organization for player to browse
    all_teams = Team.objects.all().select_related('district', 'captain', 'created_by')

    # Organization upcoming tournaments
    open_tournaments = Tournament.objects.filter(
        status__in=['UPCOMING', 'REGISTRATION_OPEN', 'ONGOING']
    ).order_by('-start_date')[:6]

    return render(request, 'dashboards/player_dashboard.html', {
        'player_profile': player_profile,
        'my_team': my_team,
        'my_teams': my_teams,
        'my_tournaments': my_tournaments,
        'upcoming_matches': upcoming_matches,
        'recent_results': recent_results,
        'my_notifications': my_notifications,
        'my_join_requests': my_join_requests,
        'pending_team_ids': pending_team_ids,
        'all_teams': all_teams,
        'open_tournaments': open_tournaments,
    })

@login_required(login_url='login')
def profile_view(request):
    user = request.user
    player_profile = getattr(user, 'player_profile', None)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'player_profile': player_profile
    })
