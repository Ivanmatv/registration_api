from django.urls import path

from .views import (
    ActivateInviteView,
    AuthRequestView,
    ProfileView,
    AuthVerifyView,
    index,
    profile_view,
    phone_auth,
    verify_code,
    activate_invite
)


urlpatterns = [
    # API Endpoints
    path('v1/auth/request/', AuthRequestView.as_view(), name='auth-request'),
    path('v1/auth/verify/', AuthVerifyView.as_view(), name='auth-verify'),
    path('v1/profile/', ProfileView.as_view(), name='profile'),
    path('v1/profile/activate/', ActivateInviteView.as_view(), name='activate-invite'),

    # Template Endpoints
    path('', index, name='index'),
    path('profile/', profile_view, name='profile_view'),
    path('auth/phone/', phone_auth, name='phone_auth'),
    path('auth/verify/', verify_code, name='verify_code'),
    path('profile/activate/', activate_invite, name='activate_invite'),
]
