from django.contrib import admin

# Register your models here.
from .models import Contact


class ContactAdmin(admin.ModelAdmin):
  model = Contact
  '''
    name    
    email 
    telephone
    comment
    ##
    ## uso interno
    attend 
    date_open
    date_update
    date_close 
    status
    email_status 
    err_email 
  '''    
  readonly_fields=('id','date_open',)
  
  list_display = ('id','name', 'attend','comment','email' \
                 , 'telephone','date_open','date_update','date_close' \
                 , 'status','email_status','err_email' )

  list_filter = ('id','attend' )

  ## Cuando Ingresamos, indicamos que campos son visibles y cuales de ellos alterables
  fieldsets = (
      (None, {'fields': ('date_open', )}),
      ('Permissions', {'fields': ( 'name','attend','comment','email' \
                                 , 'telephone','date_update','date_close' \
                                 , 'status','email_status','err_email')}), 
    )
  ## Cuando agregamos un nuevo tickets, indicamos cuales son los campos visibles
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ( 'name','attend','comment','email'
                    , 'telephone','date_update','date_close' \
                    , 'status','email_status','err_email')}
      ),
    )
  search_fields = ('names',)


admin.site.register(Contact,ContactAdmin)

# admin.site.register(TicketsHistory,TicketsHistoryAdmin)



