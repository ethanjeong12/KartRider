from django.urls import path
from .views import (
    CommentView,
    RankDetailView,
    IndiRankListView,
    TeamRankListView,
    IndiDetailTrackView,
    TeamDetailTrackView,
    IndiDetailTrackDist,
    TeamDetailTrackDist
)

urlpatterns = [
    path('/comment/<str:user_id>', CommentView.as_view()),
    path('/detail/<str:access_id>', RankDetailView.as_view()),
    path('/indiranklist', IndiRankListView.as_view()),
    path('/teamranklist', TeamRankListView.as_view()),
    path('/detailtrack/indi/<str:access_id>', IndiDetailTrackView.as_view()),
    path('/detaitrack/team/<str:access_id>', TeamDetailTrackView.as_view()),
    path('/detailtrack/indi/<str:access_id>/<str:track_key>', IndiDetailTrackDist.as_view()),
    path('/detailtrack/team/<str:access_id>/<str:track_key>', TeamDetailTrackDist.as_view())
]
