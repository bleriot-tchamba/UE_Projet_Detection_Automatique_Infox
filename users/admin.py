from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from users.models import MyUser, License


class UserInline(admin.StackedInline):
    model = MyUser
    can_delete = False

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(License)