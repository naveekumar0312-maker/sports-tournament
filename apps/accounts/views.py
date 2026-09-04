from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import UserRegistrationForm, UserProfileForm
from players.models import PlayerProfile
from tournaments.models import Tournament
from teams.models import Team
from matches.models import Match
from locations.models import District
from notifications.models import Notification

def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_organizer_role:
            return redirect('organizer_dashboard')
        elif request.user.is_admin_role:
            return redirect('/admin/')
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

            # Create appropriate player profile automatically
            if user.role == User.Role.PLAYER or user.role == 'PLAYER':
                PlayerProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    mobile_number=user.phone_number or '',
                    playing_role=PlayerProfile.PlayingRole.ALL_ROUNDER,
                    batting_style=PlayerProfile.BattingStyle.RIGHT_HAND,
                    bowling_style=PlayerProfile.BowlingStyle.RIGHT_ARM_SPIN,
                )

            messages.success(request, "Registration successful. Please login.")
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_organizer_role:
            return redirect('organizer_dashboard')
        elif request.user.is_admin_role:
            return redirect('/admin/')
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
                if user.is_organizer_role:
                    return redirect('organizer_dashboard')
                elif user.is_admin_role:
                    return redirect('/admin/')
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
    if user.is_organizer_role and not user.is_admin_role:
        return redirect('organizer_dashboard')

    player_profile = getattr(user, 'player_profile', None)

    my_teams = Team.objects.filter(members=player_profile) if player_profile else []
    my_tournaments = Tournament.objects.filter(registrations__team__in=my_teams, registrations__status='APPROVED').distinct() if my_teams else []
    
    upcoming_matches = Match.objects.filter(
        tournament__in=my_tournaments, 
        status='SCHEDULED'
    ) if my_tournaments else []

    recent_results = Match.objects.filter(
        tournament__in=my_tournaments, 
        status='COMPLETED', 
        is_result_published=True
    ) if my_tournaments else []

    my_notifications = Notification.objects.filter(recipient=user)[:8]

    return render(request, 'dashboards/player_dashboard.html', {
        'player_profile': player_profile,
        'my_teams': my_teams,
        'my_tournaments': my_tournaments,
        'upcoming_matches': upcoming_matches,
        'recent_results': recent_results,
        'my_notifications': my_notifications,
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
