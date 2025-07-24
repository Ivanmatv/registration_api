from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework import routers

from .views import (
    ActivateInviteView,
    AuthRequestView,
    ProfileView,
    AuthVerifyView
)

app_name = 'user'

urlpatterns = [
    path('v1/auth/request/', AuthRequestView.as_view(), name='auth-request'),
    path('v1/auth/verify/', AuthVerifyView.as_view(), name='auth-verify'),
    path('v1/profile/', ProfileView.as_view(), name='profile'),
    path('v1/profile/activate/', ActivateInviteView.as_view(), name='activate-invite'),
]
