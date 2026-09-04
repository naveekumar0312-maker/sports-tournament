from django import forms
from .models import Prize
from teams.models import Team
from players.models import PlayerProfile

class PrizeForm(forms.ModelForm):
    class Meta:
        model = Prize
        fields = ['category', 'title_custom', 'amount_value', 'description', 'winner_team', 'winner_player']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title_custom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Custom award title'}),
            'amount_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount in INR'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'winner_team': forms.Select(attrs={'class': 'form-select'}),
            'winner_player': forms.Select(attrs={'class': 'form-select'}),
        }
