from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("start/", views.start_game, name="start_game"),
    path("play/", views.play, name="play"),
    path("api/save-score/", views.save_score, name="save_score"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
]
