from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, MyUser, Withdrawal


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profile"


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'nickname', 'location', 'location2', 'is_staff')


class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('location', 'location2', 'reason')


admin.site.register(MyUser, UserAdmin)
admin.site.register(Withdrawal, WithdrawalAdmin)