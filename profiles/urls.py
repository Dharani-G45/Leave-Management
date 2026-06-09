from django.urls import path
from . import views

urlpatterns = [
    path('my-profile/', views.profile_page, name='profile_page'),
]