from django.urls import path
from .views import HomePageView
from .views import sync_databases_view

app_name = 'core'

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),   
    path('sync-databases/', sync_databases_view, name='sync_databases'), 

    
    
]