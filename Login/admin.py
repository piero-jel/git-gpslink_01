from django.contrib import admin

# Register your models here.
from .models import User
# Register your models here.

from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm



class CustomUserAdmin(UserAdmin):
  add_form = CustomUserCreationForm
  form = CustomUserChangeForm
  model = User
  list_display = ('username','email','first_name','last_name', 'telefono','is_staff', 'is_active','empresa')
  list_filter = ('username','email','first_name','last_name', 'telefono', 'is_staff', 'is_active','empresa','groups')

  ## Cuando Ingresamos, indicamos que campos son visibles y cuales de ellos alterables
  fieldsets = (
      (None, {'fields': ('username', 'password')}),
      ('Permissions', {'fields': ('email','first_name','last_name', 'telefono','is_staff', 'is_active','empresa','groups',)}),        
  )
  ## Cuando agregamos un nuevo usuario, indicamos cuales son los campos visibles
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ('username','email','first_name', 'telefono','last_name', 'password1', 'password2', 'is_staff', 'is_active','empresa')}
      ),
  )
  search_fields = ('username',)
  ordering = ('username',)



admin.site.register(User, CustomUserAdmin)
# admin.site.register(CustomUser)

