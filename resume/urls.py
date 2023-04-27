from django.urls import path
from . import views

urlpatterns = [
    path("resume/", views.upload_resume),
    path("", views.index),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
]
