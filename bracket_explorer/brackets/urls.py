from django.urls import path

from brackets import views

urlpatterns = [
    path("brackets/<uuid:bracket_id>/", views.bracket_prediction, name="bracket-detail")
]
