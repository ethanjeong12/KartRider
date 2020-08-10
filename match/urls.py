from django.urls import path
from .views import IndiMatchView, TeamMatchView 

urlpatterns = [
        path('/indimatch/<str:access_id>/<str:match_type>', IndiMatchView.as_view()),
        path('/teammatch/<str:access_id>/<str:match_type>', TeamMatchView.as_view())
]
