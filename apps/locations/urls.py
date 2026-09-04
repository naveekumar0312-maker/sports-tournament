from django.urls import path
from .views import district_list_view, taluks_api_view, villages_api_view

urlpatterns = [
    path('districts/', district_list_view, name='district_list'),
    path('api/taluks/', taluks_api_view, name='taluks_api'),
    path('api/villages/', villages_api_view, name='villages_api'),
]

