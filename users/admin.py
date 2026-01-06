from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'last_name', 'first_name', 'is_staff']

    fieldsets: tuple[Any, ...] = UserAdmin.fieldsets + ( # type: ignore
        (None, {'fields': ('photo', 'age')}),
    )

    # Explicitly define the layout for adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'password',
                'photo',
                'age'
            ),
        }),
    )
admin.site.register(CustomUser, CustomUserAdmin)
