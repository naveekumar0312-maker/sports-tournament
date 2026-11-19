from django import forms
from .models import Team
from players.models import PlayerProfile

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'short_code', 'logo', 'captain', 'vice_captain']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Kovai Kings XI'}),
            'short_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. KSK'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'captain': forms.Select(attrs={'class': 'form-select'}),
            'vice_captain': forms.Select(attrs={'class': 'form-select'}),
        }
