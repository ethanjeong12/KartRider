from django.contrib import admin
from django.urls import (
    path,
    include
)

urlpatterns = [
    path('user', include('user.urls')),
    path('rank', include('rank.urls')),
    path('match', include('match.urls'))
]
