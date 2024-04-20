import logging
import random
import sys

from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from brackets import prediction_engine

logger = logging.getLogger(__name__)


@require_GET
def random_prediction(request: HttpRequest):
    seed = random.randrange(sys.maxsize)

    return redirect(reverse("bracket-prediction", kwargs={"seed": str(seed)}))


@require_GET
def bracket_prediction(request: HttpRequest, seed: str):
    logger.info("Simulating bracket with seed %s", seed)
    championship = prediction_engine.build_tournament()
    championship = prediction_engine.simulate_game(random.Random(seed), championship)

    context = {
        "results": prediction_engine.collect_results(championship),
        "seed": seed,
    }

    return render(request, "brackets/bracket-detail.html", context)
