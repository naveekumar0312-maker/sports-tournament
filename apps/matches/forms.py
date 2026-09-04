from django import forms
from .models import Match, PlayerMatchPerformance

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            'round_name', 'team_a', 'team_b', 'match_date', 'match_time', 'venue', 'status'
        ]
        widgets = {
            'round_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Group Stage, Semi Final, Final'}),
            'team_a': forms.Select(attrs={'class': 'form-select'}),
            'team_b': forms.Select(attrs={'class': 'form-select'}),
            'match_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'match_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue location'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class MatchScoreForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            'status', 'toss_winner', 'toss_decision', 'team_a_score', 'team_b_score',
            'winner', 'win_margin', 'man_of_the_match', 'is_result_published'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'toss_winner': forms.Select(attrs={'class': 'form-select'}),
            'toss_decision': forms.Select(attrs={'class': 'form-select'}),
            'team_a_score': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 185/4 (20.0 ov)'}),
            'team_b_score': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 170/8 (20.0 ov)'}),
            'winner': forms.Select(attrs={'class': 'form-select'}),
            'win_margin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Won by 15 runs'}),
            'man_of_the_match': forms.Select(attrs={'class': 'form-select'}),
            'is_result_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PlayerMatchPerformanceForm(forms.ModelForm):
    class Meta:
        model = PlayerMatchPerformance
        fields = [
            'player', 'team', 'batting_status', 'runs', 'balls_faced', 'fours', 'sixes',
            'overs_bowled', 'runs_conceded', 'wickets', 'maidens',
            'catches', 'run_outs', 'stumpings'
        ]
        widgets = {
            'player': forms.Select(attrs={'class': 'form-select'}),
            'team': forms.Select(attrs={'class': 'form-select'}),
            'batting_status': forms.Select(attrs={'class': 'form-select'}),
            'runs': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'balls_faced': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'fours': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'sixes': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'overs_bowled': forms.NumberInput(attrs={'class': 'form-control', 'value': 0.0, 'step': 0.1}),
            'runs_conceded': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'wickets': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'maidens': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'catches': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'run_outs': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'stumpings': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
        }
