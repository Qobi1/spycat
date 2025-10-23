from django.urls import path
from .views import *

urlpatterns = [
    path("cats/", CatListCreateAPIView.as_view(), name="cat-list-create"),
    path("cats/<int:pk>/", CatDetailAPIView.as_view(), name="cat-detail"),

    path("missions/", MissionListCreateAPIView.as_view(), name="mission-list-create"),
    path("missions/<int:pk>/", MissionDetailAPIView.as_view(), name="mission-detail"),

    path("missions/<int:pk>/assign/", MissionAssignCatAPIView.as_view(), name="mission-assign-cat"),
    path("missions/<int:mission_id>/targets/<int:target_id>/notes/", TargetNotesAPIView.as_view(), name="target-notes"),
]