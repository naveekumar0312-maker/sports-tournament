from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Prize
from .forms import PrizeForm
from tournaments.models import Tournament
from notifications.services import notify_tournament_participants
from notifications.models import Notification

@login_required
def prize_create_view(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    if not (request.user == tournament.organizer or request.user.is_admin_role):
        messages.error(request, "Only tournament organizer can add prizes.")
        return redirect('tournament_detail', pk=tournament_id)

    if request.method == 'POST':
        form = PrizeForm(request.POST)
        if form.is_valid():
            prize = form.save(commit=False)
            prize.tournament = tournament
            prize.save()

            if prize.winner_team or prize.winner_player:
                winner_name = prize.winner_team.name if prize.winner_team else prize.winner_player.full_name
                notify_tournament_participants(
                    tournament,
                    f"Prize Announced: {prize.title}",
                    f"{winner_name} awarded {prize.title} worth ₹{prize.amount_value:,.2f}!",
                    Notification.Type.PRIZE_ANNOUNCEMENT,
                    related_link=f"/tournaments/{tournament.id}/"
                )

            messages.success(request, f"Prize '{prize.title}' added to tournament!")
            return redirect('tournament_detail', pk=tournament_id)
    else:
        form = PrizeForm()

    return render(request, 'prizes/prize_form.html', {
        'form': form,
        'tournament': tournament,
    })
