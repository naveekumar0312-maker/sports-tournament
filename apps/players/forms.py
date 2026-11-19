from django import forms
from .models import PlayerProfile

class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = PlayerProfile
        fields = [
            'full_name', 'date_of_birth', 'gender', 'mobile_number', 'playing_experience_years',
            'playing_role', 'primary_role', 'secondary_role',
            'batting_style', 'batting_position', 'bowling_style', 'bowling_type',
            'jersey_number', 'preferred_position', 'bio', 'profile_photo'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'playing_experience_years': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Experience in years'}),
            'playing_role': forms.Select(attrs={'class': 'form-select'}),
            'primary_role': forms.Select(attrs={'class': 'form-select'}),
            'secondary_role': forms.Select(attrs={'class': 'form-select'}),
            'batting_style': forms.Select(attrs={'class': 'form-select'}),
            'batting_position': forms.Select(attrs={'class': 'form-select'}),
            'bowling_style': forms.Select(attrs={'class': 'form-select'}),
            'bowling_type': forms.Select(attrs={'class': 'form-select'}),
            'jersey_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jersey Number'}),
            'preferred_position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. No. 3 Batsman / Death Bowler'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Short player biography...'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
