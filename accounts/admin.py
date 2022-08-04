from django.contrib import admin

from .models import UserRole, UserProfile


@admin.register(UserRole)
class AdminUserRole(admin.ModelAdmin):
    """
    User role admin model
    """

@admin.register(UserProfile)
class AdminUserProfile(admin.ModelAdmin):
    """
    User profile admin model
    """
