"""
URL configuration for bu_hacktoberfest project.
"""
from django.contrib import admin
from django.urls import path, include
from users.views import (
    profile_view, leaderboard_view, update_all, redirect_view, 
    repositories_view, leaderboard_api_view, public_profile_view, 
    stats_view, event_ended_view
)
from .views import home, faq_view, resources_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/3rdparty/', redirect_view, name='redirect'),
    # Redirect all auth URLs to event ended page
    path('accounts/login/', event_ended_view),
    path('accounts/signup/', event_ended_view),
    path('accounts/github/login/', event_ended_view),
    path('accounts/microsoft/login/', event_ended_view),
    path('welcome/', event_ended_view),
    path('login/', event_ended_view),
    # Regular pages
    path('', home),
    path('profile/', profile_view, name='profile'),
    path('leaderboard/', leaderboard_view, name='leaderboard'),
    path('update_all/', update_all, name='update_all'),
    path('repositories/', repositories_view, name='repositories'),
    path('faq/', faq_view, name='faq'),
    path('resources/', resources_view, name='resources'),
    path('api/leaderboard', leaderboard_api_view, name='leaderboard_api'),
    path('profile/<str:username>/', public_profile_view, name='public_profile'),
    path('stats/', stats_view, name='stats'),
]