from django.contrib import admin
from django.urls import path

from Login import views


admin.site.site_header = "Administracion del Sistema"
admin.site.site_title = "Administracion del Sistema"
# ## para registrar las url de los archivos de services
# from django.conf import settings
# from django.conf.urls.static import static

urlpatterns = [
    ## add the admin views here
    ## http://127.0.0.1:8000/login/admin/
    path('admin/', admin.site.urls,name='Admin'),
    path('', views.home_page,name="Login"),
    path('login/', views.Login,name="login"),
    path('logout/',views.Logout,name="logout"),
    path('password_change_request/',views.PasswordChangeRequest,name="PasswordChangeRequest"),
     #path('send_comment/',views.SendComment,name="SendComment"),
    
    
    ## http://127.0.0.1:8000/login/change_pass/

    path('change_pass/', views.ChangePassword,name="ChangePassword"),
    ## news verificadas 2021/10/29
    ## http://127.0.0.1:8000/login/view_admin/
    ## http://127.0.0.1:8000/login/view_useradmin/ 
    ## http://127.0.0.1:8000/login/view_programmers/  
    ## http://127.0.0.1:8000/login/view_clients/ FIXME Vista si uso actual
    ## http://127.0.0.1:8000/login/view_clients/10/   FIXME  idem al anterior
    path('view_admin/', views.ViewAdmin,name="view_admin"),
    path('view_useradmin/', views.ViewUserAdmin,name="view_useradmin"),
    ## http://127.0.0.1:8000/login/clean_password/10/ admite admin root
    path('clean_password/<int:user_id>/', views.CleanPassword,name="CleanPassword"),
    ## add 2021/10/27
    ## http://127.0.0.1:8000/login/new_administrador/
    ## http://127.0.0.1:8000/login/new_programmer/    
    ## http://127.0.0.1:8000/login/new_client/5/
    ## http://127.0.0.1:8000/login/new_modulo/
    ## http://127.0.0.1:8000/login/new_company/
    path('new_administrador/', views.NewAdministrador,name="NewAdministrador"),
       
    ## para editar el usuario
    path('view_users/<int:id>/', views.ViewConfigUsers,name="ViewConfigUsers"),
    path('view_contact/', views.ViewContact,name="ViewContact"),
    path('view_contact/<int:id>/', views.ViewContact,name="ViewContact"),
    path('view_contact/<int:id>/<str:word>', views.ViewContact,name="ViewContact_word"),

        
    ## vista desde compania, verificadas 
    ## http://127.0.0.1:8000/login/view_modulos/    
    path('view_expand_contact/', views.ViewExpandContact,name="ViewExpandContact"),
    path('view_expand_contact/<int:id>/', views.ViewExpandContact,name="ViewExpandContact_word"),
    path('view_expand_contact/<int:id>/<str:word>', views.ViewExpandContact,name="ViewExpandContact_word"),    
]
