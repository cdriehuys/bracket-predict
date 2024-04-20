from django.urls import path

from brackets import views

urlpatterns = [
    path("prediction/", views.random_prediction, name="random-prediction"),
    path("prediction/<str:seed>/", views.bracket_prediction, name="bracket-prediction"),
]
