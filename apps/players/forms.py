from django import forms
from .models import PlayerProfile
from locations.models import District, Taluk, Village

class PlayerProfileForm(forms.ModelForm):
    district = forms.ModelChoiceField(queryset=District.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_district'}))
    taluk = forms.ModelChoiceField(queryset=Taluk.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_taluk'}))
    village = forms.ModelChoiceField(queryset=Village.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_village'}))

    class Meta:
        model = PlayerProfile
        fields = [
            'full_name', 'date_of_birth', 'gender', 'mobile_number', 'playing_experience_years',
            'district', 'taluk', 'village', 'playing_role', 'primary_role', 'secondary_role',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'data' in kwargs:
            # If form data is bound, filter taluk and village querysets based on posted data
            try:
                district_id = int(kwargs['data'].get('district'))
                self.fields['taluk'].queryset = Taluk.objects.filter(district_id=district_id)
            except (ValueError, TypeError):
                pass
            try:
                taluk_id = int(kwargs['data'].get('taluk'))
                self.fields['village'].queryset = Village.objects.filter(taluk_id=taluk_id)
            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.pk:
            if self.instance.district_id:
                self.fields['taluk'].queryset = Taluk.objects.filter(district=self.instance.district)
            if self.instance.taluk_id:
                self.fields['village'].queryset = Village.objects.filter(taluk=self.instance.taluk)

    def clean(self):
        cleaned_data = super().clean()
        district = cleaned_data.get('district')
        taluk = cleaned_data.get('taluk')
        village = cleaned_data.get('village')

        if taluk and district and taluk.district_id != district.id:
            self.add_error('taluk', f"Selected Taluk '{taluk.name}' does not belong to District '{district.name}'.")

        if village and taluk and village.taluk_id != taluk.id:
            self.add_error('village', f"Selected Village '{village.name}' does not belong to Taluk '{taluk.name}'.")

        return cleaned_data

