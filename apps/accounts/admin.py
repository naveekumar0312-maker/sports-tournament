from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone_number', 'is_approved_organizer', 'is_staff', 'is_active')
    list_filter = ('role', 'is_approved_organizer', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Profile Info', {'fields': ('role', 'phone_number', 'profile_picture', 'bio', 'is_approved_organizer')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Profile Info', {'fields': ('role', 'phone_number', 'profile_picture', 'bio', 'is_approved_organizer')}),
    )
