from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Organization, InviteCode

from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'org', 'is_staff', 'is_active']
    actions = ["reset_user_password"]

    fieldsets = (
        (('User'), {'fields': ('username', 'org', 'invite_code', 'password')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'invite_code', 'password1', 'password2'),
        }),
    )

    def reset_user_password(self, request, queryset):
        for user in queryset:
            user.set_password("NewSecurePassword123")  # Change this to generate a random password
            user.save()
        self.message_user(request, "Passwords have been reset to default.")
    
    reset_user_password.short_description = "Reset password for selected users"


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organization)
admin.site.register(InviteCode)