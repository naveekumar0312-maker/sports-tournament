from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Tournament
from .forms import TournamentForm
from locations.models import District
from teams.models import Team, TournamentRegistration
from notifications.services import notify_tournament_participants, create_notification

def tournament_list_view(request):
    tournaments = Tournament.objects.all().select_related('district', 'taluk', 'village', 'organizer')
    
    district_filter = request.GET.get('district')
    taluk_filter = request.GET.get('taluk')
    village_filter = request.GET.get('village')
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    search_query = request.GET.get('q')

    if district_filter:
        tournaments = tournaments.filter(district_id=district_filter)
    if taluk_filter:
        tournaments = tournaments.filter(taluk_id=taluk_filter)
    if village_filter:
        tournaments = tournaments.filter(village_id=village_filter)
    if status_filter:
        tournaments = tournaments.filter(status=status_filter)
    if type_filter:
        tournaments = tournaments.filter(tournament_type=type_filter)
    if search_query:
        tournaments = tournaments.filter(name__icontains=search_query)

    districts = District.objects.all()

    return render(request, 'tournaments/tournament_list.html', {
        'tournaments': tournaments,
        'districts': districts,
        'selected_district': district_filter,
        'selected_taluk': taluk_filter,
        'selected_village': village_filter,
        'selected_status': status_filter,
        'selected_type': type_filter,
        'search_query': search_query,
    })


def tournament_detail_view(request, pk):
    tournament = get_object_or_404(Tournament.objects.select_related('district', 'taluk', 'organizer'), pk=pk)
    registrations = tournament.registrations.select_related('team').all()
    matches = tournament.matches.select_related('team_a', 'team_b', 'winner', 'man_of_the_match').all()
    prizes = tournament.prizes.all()

    # User's teams for register button
    user_teams = []
    if request.user.is_authenticated:
        user_teams = Team.objects.filter(created_by=request.user)

    return render(request, 'tournaments/tournament_detail.html', {
        'tournament': tournament,
        'registrations': registrations,
        'matches': matches,
        'prizes': prizes,
        'user_teams': user_teams,
    })

@login_required
def tournament_create_view(request):
    if not request.user.is_admin_role:
        messages.error(request, "Only the Organization Super Admin can host tournaments.")
        return redirect('tournament_list')

    if request.method == 'POST':
        form = TournamentForm(request.POST, request.FILES)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.organizer = request.user
            tournament.save()

            messages.success(request, f"Tournament '{tournament.name}' created successfully!")
            return redirect('tournament_detail', pk=tournament.pk)
    else:
        form = TournamentForm()

    return render(request, 'tournaments/tournament_form.html', {
        'form': form,
        'title': 'Create New Tournament'
    })

@login_required
def tournament_edit_view(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)

    if not (request.user == tournament.organizer or request.user.is_admin_role):
        messages.error(request, "Permission denied.")
        return redirect('tournament_detail', pk=pk)

    if request.method == 'POST':
        form = TournamentForm(request.POST, request.FILES, instance=tournament)
        if form.is_valid():
            updated_tournament = form.save()
            
            # Send notification to participants if status updated
            notify_tournament_participants(
                updated_tournament,
                f"Tournament Updated: {updated_tournament.name}",
                f"Status: {updated_tournament.get_status_display()}. Check tournament page for latest details.",
                related_link=f"/tournaments/{updated_tournament.id}/"
            )

            messages.success(request, "Tournament updated successfully!")
            return redirect('tournament_detail', pk=pk)
    else:
        form = TournamentForm(instance=tournament)

    return render(request, 'tournaments/tournament_form.html', {
        'form': form,
        'tournament': tournament,
        'title': 'Edit Tournament'
    })
