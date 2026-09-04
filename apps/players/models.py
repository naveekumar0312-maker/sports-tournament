from django.db import models
from django.conf import settings
from django.db.models import Sum, Count, Max

class PlayerProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'

    class PlayingRole(models.TextChoices):
        BATSMAN = 'BATSMAN', 'Batsman'
        BOWLER = 'BOWLER', 'Bowler'
        ALL_ROUNDER = 'ALL_ROUNDER', 'All-Rounder'
        WICKET_KEEPER = 'WICKET_KEEPER', 'Wicket-Keeper / Batsman'

    class BattingStyle(models.TextChoices):
        RIGHT_HAND = 'RIGHT_HAND', 'Right Hand'
        LEFT_HAND = 'LEFT_HAND', 'Left Hand'

    class BattingPosition(models.TextChoices):
        OPENING = 'OPENING', 'Opening'
        TOP_ORDER = 'TOP_ORDER', 'Top Order'
        MIDDLE_ORDER = 'MIDDLE_ORDER', 'Middle Order'
        LOWER_ORDER = 'LOWER_ORDER', 'Lower Order'
        FINISHER = 'FINISHER', 'Finisher'

    class BowlingStyle(models.TextChoices):
        RIGHT_ARM_FAST = 'RIGHT_ARM_FAST', 'Right Arm Fast'
        RIGHT_ARM_MEDIUM = 'RIGHT_ARM_MEDIUM', 'Right Arm Medium'
        RIGHT_ARM_SPIN = 'RIGHT_ARM_SPIN', 'Right Arm Spin'
        LEFT_ARM_FAST = 'LEFT_ARM_FAST', 'Left Arm Fast'
        LEFT_ARM_MEDIUM = 'LEFT_ARM_MEDIUM', 'Left Arm Medium'
        LEFT_ARM_SPIN = 'LEFT_ARM_SPIN', 'Left Arm Spin'
        NONE = 'NONE', 'None / Non-Bowler'

    class BowlingType(models.TextChoices):
        PACE = 'PACE', 'Pace'
        SPIN = 'SPIN', 'Spin'
        NONE = 'NONE', 'None'

    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        IN_TEAM = 'IN_TEAM', 'Assigned to Team'
        INACTIVE = 'INACTIVE', 'Inactive'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player_profile')
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.MALE)
    mobile_number = models.CharField(max_length=15)
    playing_experience_years = models.PositiveIntegerField(default=1, help_text="Experience in years")
    
    district = models.ForeignKey('locations.District', on_delete=models.SET_NULL, null=True, blank=True, related_name='players')
    taluk = models.ForeignKey('locations.Taluk', on_delete=models.SET_NULL, null=True, blank=True, related_name='players')
    village = models.ForeignKey('locations.Village', on_delete=models.SET_NULL, null=True, blank=True, related_name='players')

    
    playing_role = models.CharField(max_length=30, choices=PlayingRole.choices, default=PlayingRole.ALL_ROUNDER)
    primary_role = models.CharField(max_length=30, choices=PlayingRole.choices, default=PlayingRole.ALL_ROUNDER)
    secondary_role = models.CharField(max_length=30, choices=PlayingRole.choices, default=PlayingRole.BATSMAN)
    
    batting_style = models.CharField(max_length=30, choices=BattingStyle.choices, default=BattingStyle.RIGHT_HAND)
    batting_position = models.CharField(max_length=30, choices=BattingPosition.choices, default=BattingPosition.MIDDLE_ORDER)
    
    bowling_style = models.CharField(max_length=30, choices=BowlingStyle.choices, default=BowlingStyle.RIGHT_ARM_SPIN)
    bowling_type = models.CharField(max_length=15, choices=BowlingType.choices, default=BowlingType.SPIN)
    
    jersey_number = models.PositiveIntegerField(blank=True, null=True)
    preferred_position = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. No. 3 Batsman / Death Bowler")
    bio = models.TextField(blank=True, null=True)
    
    current_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    player_status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    profile_photo = models.ImageField(upload_to='player_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.get_playing_role_display()})"

    @property
    def age(self):
        if self.date_of_birth:
            import datetime
            today = datetime.date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None


    # --- AUTOMATIC CAREER STATISTICS CALCULATION ENGINE ---
    def get_batting_stats(self):
        perfs = self.match_performances.all()
        matches = perfs.values('match').distinct().count()
        batted_perfs = perfs.exclude(batting_status='DID_NOT_BAT')
        innings = batted_perfs.count()
        
        runs = perfs.aggregate(total=Sum('runs'))['total'] or 0
        balls = perfs.aggregate(total=Sum('balls_faced'))['total'] or 0
        fours = perfs.aggregate(total=Sum('fours'))['total'] or 0
        sixes = perfs.aggregate(total=Sum('sixes'))['total'] or 0
        highest_score = perfs.aggregate(max_runs=Max('runs'))['max_runs'] or 0
        
        not_outs = perfs.filter(batting_status='NOT_OUT').count()
        ducks = batted_perfs.filter(runs=0).count()
        fifties = perfs.filter(runs__gte=50, runs__lt=100).count()
        hundreds = perfs.filter(runs__gte=100).count()
        
        dismissals = innings - not_outs
        average = round(runs / dismissals, 2) if dismissals > 0 else float(runs)
        strike_rate = round((runs / balls) * 100, 2) if balls > 0 else 0.0

        return {
            'matches': matches,
            'innings': innings,
            'runs': runs,
            'highest_score': highest_score,
            'average': average,
            'strike_rate': strike_rate,
            'fifties': fifties,
            'hundreds': hundreds,
            'fours': fours,
            'sixes': sixes,
            'not_outs': not_outs,
            'ducks': ducks,
        }

    def get_bowling_stats(self):
        perfs = self.match_performances.filter(overs_bowled__gt=0)
        matches = self.match_performances.values('match').distinct().count()
        innings = perfs.count()
        
        overs = float(perfs.aggregate(total=Sum('overs_bowled'))['total'] or 0.0)
        runs_conceded = perfs.aggregate(total=Sum('runs_conceded'))['total'] or 0
        wickets = perfs.aggregate(total=Sum('wickets'))['total'] or 0
        maidens = perfs.aggregate(total=Sum('maidens'))['total'] or 0
        
        four_wickets = perfs.filter(wickets=4).count()
        five_wickets = perfs.filter(wickets__gte=5).count()
        
        # Best Bowling calculation
        best_perf = perfs.order_by('-wickets', 'runs_conceded').first()
        best_bowling = f"{best_perf.wickets}/{best_perf.runs_conceded}" if best_perf else "N/A"
        
        average = round(runs_conceded / wickets, 2) if wickets > 0 else 0.0
        economy = round(runs_conceded / overs, 2) if overs > 0 else 0.0
        total_balls = int(overs) * 6 + int(round((overs % 1) * 10))
        strike_rate = round(total_balls / wickets, 2) if wickets > 0 else 0.0

        return {
            'matches': matches,
            'innings': innings,
            'overs': round(overs, 1),
            'runs_conceded': runs_conceded,
            'wickets': wickets,
            'best_bowling': best_bowling,
            'average': average,
            'economy': economy,
            'strike_rate': strike_rate,
            'four_wickets': four_wickets,
            'five_wickets': five_wickets,
            'maidens': maidens,
        }

    def get_fielding_stats(self):
        perfs = self.match_performances.all()
        catches = perfs.aggregate(total=Sum('catches'))['total'] or 0
        run_outs = perfs.aggregate(total=Sum('run_outs'))['total'] or 0
        stumpings = perfs.aggregate(total=Sum('stumpings'))['total'] or 0
        total_dismissals = catches + run_outs + stumpings

        return {
            'catches': catches,
            'run_outs': run_outs,
            'stumpings': stumpings,
            'total_dismissals': total_dismissals,
        }
