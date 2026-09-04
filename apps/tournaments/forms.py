from django import forms
from .models import Tournament
from locations.models import District, Taluk, Village

class TournamentForm(forms.ModelForm):
    district = forms.ModelChoiceField(queryset=District.objects.all(), widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_district'}))
    taluk = forms.ModelChoiceField(queryset=Taluk.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_taluk'}))
    village = forms.ModelChoiceField(queryset=Village.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_village'}))

    class Meta:
        model = Tournament
        fields = [
            'name', 'tournament_type', 'description', 'district', 'taluk', 'village', 'venue',
            'start_date', 'end_date', 'registration_start_date', 'registration_end_date',
            'entry_fee', 'contact_phone', 'contact_email', 'max_teams', 'status', 'banner'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tamil Nadu Premier Trophy 2026'}),
            'tournament_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Stadium or Ground name'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'registration_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'registration_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'entry_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5000.00'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'organizer@domain.com'}),
            'max_teams': forms.NumberInput(attrs={'class': 'form-control', 'value': 16}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'banner': forms.FileInput(attrs={'class': 'form-control'}),
        }
