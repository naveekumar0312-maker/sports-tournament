from django import forms
from .models import Tournament

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = [
            'name', 'tournament_type', 'description', 'venue',
            'start_date', 'end_date', 'registration_start_date', 'registration_end_date',
            'entry_fee', 'contact_phone', 'contact_email', 'max_teams', 'status', 'banner'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Naveen Premier Cup 2026'}),
            'tournament_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tournament rules, format, and details...'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ground / Stadium Name (e.g. Naveen Cricket Ground, Coimbatore)'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'registration_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'registration_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'entry_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2500.00'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact phone number'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'naveen@org.com'}),
            'max_teams': forms.NumberInput(attrs={'class': 'form-control', 'value': 16}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'banner': forms.FileInput(attrs={'class': 'form-control'}),
        }
