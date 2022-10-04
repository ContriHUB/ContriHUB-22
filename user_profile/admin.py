from faulthandler import register
from django.contrib import admin
from .models import UserProfile
# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'registration_no', 'course', 'current_year', 'linkedin_id')


# admin.site.register(UserProfile, UserProfileAdmin)   
# "this above line is updated as decorator in line 7 "
