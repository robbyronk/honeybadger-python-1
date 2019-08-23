from django.urls import path
from . import views

urlpatterns = [
  path('plain_view/', views.plain_view),
  path('always_fails/', views.always_fails)
]