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

    team_a_players = PlayerProfile.objects.filter(current_team=match.team_a)
    team_b_players = PlayerProfile.objects.filter(current_team=match.team_b)

    # Bowler performance record if selected
    bowler_perf = None
    striker_perf = None
    non_striker_perf = None

    if match.striker:
        striker_perf, _ = PlayerMatchPerformance.objects.get_or_create(
            match=match, player=match.striker, defaults={'team': match.current_batting_team or match.team_a, 'batting_status': PlayerMatchPerformance.BattingStatus.NOT_OUT}
        )
    if match.non_striker:
        non_striker_perf, _ = PlayerMatchPerformance.objects.get_or_create(
            match=match, player=match.non_striker, defaults={'team': match.current_batting_team or match.team_a, 'batting_status': PlayerMatchPerformance.BattingStatus.NOT_OUT}
        )
    if match.current_bowler:
        bowling_team = match.team_b if match.current_batting_team == match.team_a else match.team_a
        bowler_perf, _ = PlayerMatchPerformance.objects.get_or_create(
            match=match, player=match.current_bowler, defaults={'team': bowling_team}
        )

    # Available batting team players who are NOT dismissed yet
    batting_team = match.current_batting_team or match.team_a
    bowling_team = match.team_b if batting_team == match.team_a else match.team_a

    batting_team_players = PlayerProfile.objects.filter(current_team=batting_team)
    bowling_team_players = PlayerProfile.objects.filter(current_team=bowling_team)

    # Dismissed players list
    dismissed_player_ids = PlayerMatchPerformance.objects.filter(
        match=match,
        team=batting_team
    ).exclude(
        batting_status__in=[
            PlayerMatchPerformance.BattingStatus.DID_NOT_BAT,
            PlayerMatchPerformance.BattingStatus.NOT_OUT
        ]
    ).values_list('player_id', flat=True)

    available_next_batsmen = batting_team_players.exclude(id__in=dismissed_player_ids)
    if match.non_striker:
        available_next_batsmen = available_next_batsmen.exclude(id=match.non_striker.id)

    # Check if a new bowler needs to be chosen for next over:
    # Over is complete when current_overs is whole number (e.g. 1.0, 2.0) and current_bowler is None
    needs_new_batsman = (match.striker is None)
    needs_new_bowler = (match.current_bowler is None)

    return render(request, 'matches/match_score_form.html', {
        'form': form,
        'match': match,
        'performances': performances,
        'team_a_players': team_a_players,
        'team_b_players': team_b_players,
        'batting_team_players': batting_team_players,
        'bowling_team_players': bowling_team_players,
        'available_next_batsmen': available_next_batsmen,
        'needs_new_batsman': needs_new_batsman,
        'needs_new_bowler': needs_new_bowler,
        'striker_perf': striker_perf,
        'non_striker_perf': non_striker_perf,
        'bowler_perf': bowler_perf,
    })

@login_required(login_url='login')
def set_live_batsmen_bowler_view(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if not (request.user == match.tournament.organizer or request.user.is_admin_role):
        messages.error(request, "Permission denied.")
        return redirect('match_detail', pk=pk)

    if request.method == 'POST':
        batting_team_id = request.POST.get('batting_team_id')
        striker_id = request.POST.get('striker_id')
        non_striker_id = request.POST.get('non_striker_id')
        bowler_id = request.POST.get('bowler_id')

        from teams.models import Team
        if batting_team_id:
            match.current_batting_team = Team.objects.filter(pk=batting_team_id).first()
        if striker_id:
            match.striker = PlayerProfile.objects.filter(pk=striker_id).first()
        if non_striker_id:
            match.non_striker = PlayerProfile.objects.filter(pk=non_striker_id).first()
        if bowler_id:
            match.current_bowler = PlayerProfile.objects.filter(pk=bowler_id).first()
        
        match.status = Match.Status.LIVE
        match.save()

        # Initialize performance rows if they don't exist
        if match.striker:
            PlayerMatchPerformance.objects.get_or_create(
                match=match, player=match.striker,
                defaults={'team': match.current_batting_team or match.team_a, 'batting_status': PlayerMatchPerformance.BattingStatus.NOT_OUT}
            )
        if match.non_striker:
            PlayerMatchPerformance.objects.get_or_create(
                match=match, player=match.non_striker,
                defaults={'team': match.current_batting_team or match.team_a, 'batting_status': PlayerMatchPerformance.BattingStatus.NOT_OUT}
            )
        if match.current_bowler:
            bowling_team = match.team_b if match.current_batting_team == match.team_a else match.team_a
            PlayerMatchPerformance.objects.get_or_create(
                match=match, player=match.current_bowler,
                defaults={'team': bowling_team}
            )

        messages.success(request, f"Live match lineups set: {match.striker.full_name if match.striker else ''} & {match.non_striker.full_name if match.non_striker else ''} batting against {match.current_bowler.full_name if match.current_bowler else ''}!")
        return redirect('match_update_score', pk=pk)

@login_required(login_url='login')
def live_ball_record_view(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if not (request.user == match.tournament.organizer or request.user.is_admin_role):
        messages.error(request, "Permission denied.")
        return redirect('match_detail', pk=pk)

    if request.method == 'POST':
        action = request.POST.get('ball_action') # '0', '1', '2', '3', '4', '6', 'W', 'WD', 'NB'

        # Ensure performance objects exist
        striker_perf = None
        non_striker_perf = None
        bowler_perf = None

        if match.striker:
            striker_perf, _ = PlayerMatchPerformance.objects.get_or_create(
                match=match, player=match.striker,
                defaults={'team': match.current_batting_team or match.team_a, 'batting_status': PlayerMatchPerformance.BattingStatus.NOT_OUT}
            )
        if match.non_striker:
            non_striker_perf, _ = PlayerMatchPerformance.objects.get_or_create(
                match=match, player=match.non_striker,
                defaults={'team': match.current_batting_team or match.team_a, 'batting_status': PlayerMatchPerformance.BattingStatus.NOT_OUT}
            )
        if match.current_bowler:
            bowling_team = match.team_b if match.current_batting_team == match.team_a else match.team_a
            bowler_perf, _ = PlayerMatchPerformance.objects.get_or_create(
                match=match, player=match.current_bowler,
                defaults={'team': bowling_team}
            )

        runs_added = 0
        is_legal_delivery = True

        if action in ['0', '1', '2', '3', '4', '6']:
            runs = int(action)
            runs_added = runs
            if striker_perf:
                striker_perf.runs += runs
                striker_perf.balls_faced += 1
                if runs == 4:
                    striker_perf.fours += 1
                elif runs == 6:
                    striker_perf.sixes += 1
                striker_perf.save()

            if bowler_perf:
                bowler_perf.runs_conceded += runs
                # overs_bowled representation: .1, .2, .3, .4, .5, .6 -> next over
                current_ov = float(bowler_perf.overs_bowled)
                overs_int = int(current_ov)
                balls_in_ov = round((current_ov - overs_int) * 10) + 1
                if balls_in_ov >= 6:
                    bowler_perf.overs_bowled = float(overs_int + 1)
                else:
                    bowler_perf.overs_bowled = float(overs_int + (balls_in_ov / 10.0))
                bowler_perf.save()

            # Swap strike if 1 or 3 runs
            if runs in [1, 3] and match.striker and match.non_striker:
                match.striker, match.non_striker = match.non_striker, match.striker

        elif action == 'W':
            # Wicket
            if striker_perf:
                striker_perf.balls_faced += 1
                striker_perf.batting_status = PlayerMatchPerformance.BattingStatus.CAUGHT
                striker_perf.save()

            if bowler_perf:
                bowler_perf.wickets += 1
                current_ov = float(bowler_perf.overs_bowled)
                overs_int = int(current_ov)
                balls_in_ov = round((current_ov - overs_int) * 10) + 1
                if balls_in_ov >= 6:
                    bowler_perf.overs_bowled = float(overs_int + 1)
                else:
                    bowler_perf.overs_bowled = float(overs_int + (balls_in_ov / 10.0))
                bowler_perf.save()

            match.current_wickets += 1
            # striker is dismissed, clear striker to pick next
            match.striker = None

        elif action == 'WD':
            runs_added = 1
            is_legal_delivery = False
            if bowler_perf:
                bowler_perf.runs_conceded += 1
                bowler_perf.save()

        elif action == 'NB':
            runs_added = 1
            is_legal_delivery = False
            if bowler_perf:
                bowler_perf.runs_conceded += 1
                bowler_perf.save()

        # Update Match total runs and overs
        match.current_runs += runs_added
        if is_legal_delivery:
            current_tot_ov = float(match.current_overs)
            tot_int = int(current_tot_ov)
            tot_balls = round((current_tot_ov - tot_int) * 10) + 1
            if tot_balls >= 6:
                match.current_overs = float(tot_int + 1)
                # Over completed: swap strike
                if match.striker and match.non_striker:
                    match.striker, match.non_striker = match.non_striker, match.striker
                # Over finished! Clear current_bowler so new bowler must be chosen
                match.current_bowler = None
                over_finished = True
            else:
                match.current_overs = float(tot_int + (tot_balls / 10.0))
                over_finished = False

        # Recent balls ribbon
        recent_list = [b.strip() for b in match.recent_balls.split(',') if b.strip()]
        recent_list.append(action)
        match.recent_balls = ', '.join(recent_list[-8:])

        # Auto update team score string
        score_str = f"{match.current_runs}/{match.current_wickets} ({match.current_overs} ov)"
        if match.current_batting_team == match.team_a or not match.current_batting_team:
            match.team_a_score = score_str
        else:
            match.team_b_score = score_str

        match.status = Match.Status.LIVE
        match.save()

        if action == 'W':
            messages.warning(request, f"Wicket down! {score_str}. Select the incoming new batsman below.")
        elif 'over_finished' in locals() and over_finished:
            messages.info(request, f"Over {int(match.current_overs)} completed! {score_str}. Select new bowler for the next over.")
        else:
            messages.success(request, f"Ball recorded: {action}! Total: {score_str}")
        return redirect('match_update_score', pk=pk)

@login_required(login_url='login')
def set_new_batsman_view(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if not (request.user == match.tournament.organizer or request.user.is_admin_role):
        messages.error(request, "Permission denied.")
        return redirect('match_detail', pk=pk)

    if request.method == 'POST':
        batsman_id = request.POST.get('new_batsman_id')
        if batsman_id:
            new_batsman = PlayerProfile.objects.filter(pk=batsman_id).first()
            if new_batsman:
                match.striker = new_batsman
                match.save()
                PlayerMatchPerformance.objects.get_or_create(
                    match=match, player=new_batsman,
                    defaults={
                        'team': match.current_batting_team or match.team_a,
                        'batting_status': PlayerMatchPerformance.BattingStatus.NOT_OUT
                    }
                )
                messages.success(request, f"New batsman {new_batsman.full_name} is on strike!")
        return redirect('match_update_score', pk=pk)

@login_required(login_url='login')
def set_new_bowler_view(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if not (request.user == match.tournament.organizer or request.user.is_admin_role):
        messages.error(request, "Permission denied.")
        return redirect('match_detail', pk=pk)

    if request.method == 'POST':
        bowler_id = request.POST.get('new_bowler_id')
        if bowler_id:
            new_bowler = PlayerProfile.objects.filter(pk=bowler_id).first()
            if new_bowler:
                match.current_bowler = new_bowler
                match.save()
                bowling_team = match.team_b if match.current_batting_team == match.team_a else match.team_a
                PlayerMatchPerformance.objects.get_or_create(
                    match=match, player=new_bowler,
                    defaults={'team': bowling_team}
                )
                messages.success(request, f"New bowler {new_bowler.full_name} assigned for this over!")
        return redirect('match_update_score', pk=pk)

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
