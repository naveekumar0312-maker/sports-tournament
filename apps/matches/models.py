from django.db import models

class Match(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        LIVE = 'LIVE', 'Live'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class TossDecision(models.TextChoices):
        BAT = 'BAT', 'Elected to Bat'
        BOWL = 'BOWL', 'Elected to Bowl'

    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name='matches')
    round_name = models.CharField(max_length=100, default='Group Stage')
    
    team_a = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='matches_as_team_a')
    team_b = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='matches_as_team_b')
    
    match_date = models.DateField()
    match_time = models.TimeField(blank=True, null=True)
    venue = models.CharField(max_length=255, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    
    toss_winner = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='toss_wins')
    toss_decision = models.CharField(max_length=10, choices=TossDecision.choices, blank=True, null=True)
    
    team_a_score = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. 185/4 (20.0 ov)")
    team_b_score = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. 170/8 (20.0 ov)")
    
    winner = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='match_wins')
    win_margin = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Won by 15 runs")
    man_of_the_match = models.ForeignKey('players.PlayerProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='mom_awards')
    
    is_result_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['match_date', 'match_time']
        verbose_name_plural = 'Matches'

    def __str__(self):
        return f"{self.team_a.name} vs {self.team_b.name} ({self.tournament.name})"

class PlayerMatchPerformance(models.Model):
    class BattingStatus(models.TextChoices):
        DID_NOT_BAT = 'DID_NOT_BAT', 'Did Not Bat'
        NOT_OUT = 'NOT_OUT', 'Not Out'
        BOWLED = 'BOWLED', 'Bowled'
        CAUGHT = 'CAUGHT', 'Caught'
        LBW = 'LBW', 'LBW'
        RUN_OUT = 'RUN_OUT', 'Run Out'
        STUMPED = 'STUMPED', 'Stumped'
        RETIRED_OUT = 'RETIRED_OUT', 'Retired Out'

    player = models.ForeignKey('players.PlayerProfile', on_delete=models.CASCADE, related_name='match_performances')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='player_performances')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='player_performances')
    
    # Batting
    batting_status = models.CharField(max_length=20, choices=BattingStatus.choices, default=BattingStatus.DID_NOT_BAT)
    runs = models.PositiveIntegerField(default=0)
    balls_faced = models.PositiveIntegerField(default=0)
    fours = models.PositiveIntegerField(default=0)
    sixes = models.PositiveIntegerField(default=0)
    
    # Bowling
    overs_bowled = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    runs_conceded = models.PositiveIntegerField(default=0)
    wickets = models.PositiveIntegerField(default=0)
    maidens = models.PositiveIntegerField(default=0)
    
    # Fielding
    catches = models.PositiveIntegerField(default=0)
    run_outs = models.PositiveIntegerField(default=0)
    stumpings = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'match')

    @property
    def strike_rate(self):
        if self.balls_faced > 0:
            return round((self.runs / self.balls_faced) * 100, 2)
        return 0.0

    @property
    def economy_rate(self):
        if self.overs_bowled > 0:
            return round(self.runs_conceded / float(self.overs_bowled), 2)
        return 0.0

    def __str__(self):
        return f"{self.player.full_name} in {self.match}"
