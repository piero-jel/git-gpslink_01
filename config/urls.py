"""gpslink URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path , include


from django.conf.urls.static import static

from django.views.generic import RedirectView
from django.conf.urls import url
from django.conf import settings
from Login.views import Error_404,Error_500
from django.conf.urls import handler404
# from .settings import STATIC_URL , STATIC_ROOT , MEDIA_URL , MEDIA_ROOT

"""
    Cambiamos el nombre del panel principal
    Debemos importar 'from django.contrib import admin'
"""
# admin.site.site_header = "Administracion del Sistema"
# admin.site.site_title = "Administracion del Sistema"


handler404 = Error_404
handler500 = Error_500

##  http://127.0.0.1:8000/
##  http://127.0.0.1:8000/login/
##  http://127.0.0.1:8000/contact/

urlpatterns = [
    path('', include('Home.urls')),
    path('login/', include('Login.urls')),
    path('contact/', include('Contact.urls')),
    url(r'^favicon\.ico$',RedirectView.as_view(url='/static/Home/img/favicon.ico')),    
] 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 