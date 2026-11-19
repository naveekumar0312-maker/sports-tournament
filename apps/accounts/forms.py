from django import forms
from django.contrib.auth import get_user_model
from players.models import PlayerProfile

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'})
    )
    team_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Perur Kings XI (Required for Captains)'}),
        label="Team Name (For Captains / Owners)"
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile number'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'role': 'Account Type',
            'phone_number': 'Mobile Number',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            (User.Role.CAPTAIN, '🏏 Team Captain / Team Owner (Manage Squad & Register for Tournaments)'),
            (User.Role.PLAYER, '🏃 Cricket Player (Join Teams & Track Career Stats)'),
        ]
        self.fields['role'].initial = User.Role.PLAYER

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        role = cleaned_data.get('role')
        team_name = cleaned_data.get('team_name')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        if role == User.Role.CAPTAIN and not team_name:
            self.add_error('team_name', "Team Name is required when registering as a Team Captain.")

        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'bio', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
