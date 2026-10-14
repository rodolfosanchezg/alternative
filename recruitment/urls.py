"""URL routes for the application board view."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.board, name="board"),
]