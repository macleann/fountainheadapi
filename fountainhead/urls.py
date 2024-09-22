"""fountainhead URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from fountainhead_api.views import (
    my_state, clear_state, register, login, google_authenticate, 
    logout, get_user, chat, CustomTokenObtainPairView
)

router = DefaultRouter(trailing_slash=False)

urlpatterns = [
    path('', include(router.urls)),
    path('token', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('register', register, name='register'),
    path('login', login, name='login'),
    path('google-authenticate', google_authenticate, name='google-authenticate'),
    path('logout', logout, name='logout'),
    path('user', get_user, name='get-user'),
    path('game-state', my_state, name='game-state'),
    path('game-state/clear', clear_state, name='clear-game-state'),
    path('chat', chat, name='chat'),
    path('admin/', admin.site.urls),
]