from django.urls import path
from .views import (
    SocialLoginView,
    ConnectGameuserView,
)

urlpatterns = [
    path('/login', SocialLoginView.as_view()),
    path('/connect-gameuser', ConnectGameuserView.as_view())
]
