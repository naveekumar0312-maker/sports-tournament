from django import forms
from .models import Team
from locations.models import District, Taluk, Village
from players.models import PlayerProfile

class TeamForm(forms.ModelForm):
    district = forms.ModelChoiceField(queryset=District.objects.all(), widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_district'}))
    taluk = forms.ModelChoiceField(queryset=Taluk.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_taluk'}))
    village = forms.ModelChoiceField(queryset=Village.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_village'}))

    class Meta:
        model = Team
        fields = ['name', 'short_code', 'logo', 'district', 'taluk', 'village', 'captain', 'vice_captain']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Chennai Super Kings XI'}),
            'short_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CSK'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'captain': forms.Select(attrs={'class': 'form-select'}),
            'vice_captain': forms.Select(attrs={'class': 'form-select'}),
        }

