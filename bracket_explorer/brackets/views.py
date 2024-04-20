import random
import uuid

from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from brackets import models, prediction_engine


@require_GET
def bracket_prediction(request: HttpRequest, bracket_id: uuid.UUID):
    bracket = get_object_or_404(models.Bracket, pk=bracket_id)
    championship = prediction_engine.build_tournament()
    championship = prediction_engine.simulate_game(
        random.Random(bracket.random_seed), championship
    )

    return render(request, "brackets/bracket-detail.html")
