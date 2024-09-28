"""
URL configuration for bu_hacktoberfest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from users.views import profile, update_user_contributions_view, profile_view, pr_detail_view, update_all_user_contributions_view
from .views import home
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('profile/', profile_view),
    path('profile/pr/<int:id>/', pr_detail_view, name='pr_detail'),
    path('update_user_contributions/', update_user_contributions_view),
    path('update_all_user_contributions/', update_all_user_contributions_view),
    path('', home)


]
