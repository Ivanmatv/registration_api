from django.urls import path
from .views import (
    ActivateInviteView,
    AuthRequestView,
    ProfileView,
    AuthVerifyView
)

urlpatterns = [
    path('auth/request/', AuthRequestView.as_view(), name='auth-request'),
    path('auth/verify/', AuthVerifyView.as_view(), name='auth-verify'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/activate/', ActivateInviteView.as_view(), name='activate-invite'),
]
