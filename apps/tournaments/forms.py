from django import forms
from .models import Tournament

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = [
            'name', 'tournament_type', 'description', 'exact_location', 'venue',
            'prize_amount', 'entry_fee', 'max_teams',
            'start_date', 'end_date', 'registration_start_date', 'registration_end_date',
            'rules_and_regulations', 'contact_phone', 'contact_email', 'status', 'banner'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Naveen Premier Cup 2026'}),
            'tournament_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tournament summary and highlights...'}),
            'exact_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Exact Ground/Stadium Address & Landmark (e.g. Near Bus Stand, Perur, Coimbatore)'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ground / Stadium Name (e.g. Naveen Cricket Ground)'}),
            'prize_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total Prize Pool Amount (Rs.) e.g. 50000'}),
            'entry_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Entry Fee (Rs.) e.g. 2500'}),
            'max_teams': forms.NumberInput(attrs={'class': 'form-control', 'value': 16}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'registration_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'registration_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rules_and_regulations': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tournament Rules: e.g. 1. White balls only. 2. 8 players must be village locals. 3. Umpire decision final.'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact phone number'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@naveencricket.com'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'banner': forms.FileInput(attrs={'class': 'form-control'}),
        }
