from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("chart", views.chart, name="chart"),
    path("chart_detail/", views.chart_detail, name="chart_detail"),
    path("show_weeks", views.show_weeks, name="show_weeks"),
    path(
        "add_playlist_to_app/",
        views.add_playlist_to_app,
        name="add_playlist_to_app",
    ),
    path("random_chart", views.random_chart, name="random_chart"),
    path("login/", views.login, name="login"),
    path("callback", views.callback, name="callback"),
    path("save_recent_chart", views.save_recent_chart, name="save_recent_chart"),
]
