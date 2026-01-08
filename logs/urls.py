from django.urls import path
from .views import (
    VPNSessionCreateView,
    VPNSessionUpdateView,
    VPNSessionDeleteView
)

urlpatterns = [
    path("vpn-sessions/", VPNSessionCreateView.as_view()),
    path("vpn-sessions/<int:pk>/", VPNSessionUpdateView.as_view()),
    path("vpn-sessions/<int:pk>/delete/", VPNSessionDeleteView.as_view()),
]
