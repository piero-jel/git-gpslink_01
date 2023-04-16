from django.urls import path

#from Home.views import HomePageView
from Home import views


##  http://127.0.0.1:8000/
urlpatterns = [    
    path('', views.ViewHomePage, name='ViewHomePage')
]
