# NCAA Bracket predictor

import random
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, unique
from typing import Optional


@unique
class Regions(Enum):
    EAST = "East"
    SOUTH = "South"
    WEST = "West"
    MIDWEST = "Midwest"

    def __str__(self):
        return self.value


@unique
class Round(Enum):
    # NOTE: There is code that relies on the numeric comparisons of round values, and
    # the fact that later rounds have higher values than lower ones.

    SEEDING = 0
    ROUND_OF_64 = 1
    ROUND_OF_32 = 2
    SWEET_16 = 3
    ELITE_8 = 4
    FINAL_4 = 5
    CHAMPIONSHIP = 6

    def __str__(self):
        match self:
            case Round.SEEDING:
                return "Seeding"
            case Round.ROUND_OF_64:
                return "Round of 64"
            case Round.ROUND_OF_32:
                return "Round of 32"
            case Round.SWEET_16:
                return "Sweet 16"
            case Round.ELITE_8:
                return "Elite 8"
            case Round.FINAL_4:
                return "Final 4"
            case Round.CHAMPIONSHIP:
                return "Championship"


# list of win probabilities by seed for each round - source: https://www.betfirm.com/seeds-national-championship-odds/
WIN_PROBABILITIES = {
    Round.ROUND_OF_64: [
        0.99,
        0.93,
        0.86,
        0.79,
        0.65,
        0.62,
        0.61,
        0.49,
        0.51,
        0.39,
        0.38,
        0.35,
        0.21,
        0.14,
        0.07,
        0.01,
    ],
    Round.ROUND_OF_32: [
        0.85,
        0.67,
        0.62,
        0.60,
        0.53,
        0.47,
        0.31,
        0.22,
        0.10,
        0.41,
        0.45,
        0.42,
        0.19,
        0.09,
        0.36,
        0.00,
    ],
    Round.SWEET_16: [
        0.79,
        0.72,
        0.49,
        0.32,
        0.23,
        0.36,
        0.34,
        0.56,
        0.63,
        0.38,
        0.35,
        0.09,
        0.00,
        0.00,
        0.25,
        0.00,
    ],
    Round.ELITE_8: [
        0.59,
        0.47,
        0.44,
        0.61,
        0.75,
        0.19,
        0.30,
        0.67,
        0.40,
        0.11,
        0.56,
        0.00,
        0.00,
        0.00,
        0.00,
        0.00,
    ],
    Round.FINAL_4: [
        0.62,
        0.41,
        0.65,
        0.29,
        0.44,
        0.67,
        0.33,
        0.67,
        0.00,
        0.00,
        0.00,
        0.00,
        0.00,
        0.00,
        0.00,
        0.00,
    ],
    Round.CHAMPIONSHIP: [
        0.65,
        0.38,
        0.36,
        0.50,
        0.00,
        0.50,
        1.00,
        0.25,
        0.00,
        0.00,
        0.00,
        0.00,
        0.00,
        0.00,
        0.00,
        0.00,
    ],
}


@dataclass
class Team:
    seed: int
    region: Regions

    def __str__(self) -> str:
        return f"{self.seed} seed from the {self.region}"


@dataclass
class Game:
    round: Round

    left: Optional["Game"] = None
    right: Optional["Game"] = None
    winner: Optional[Team] = None


@dataclass
class Final4Predictions:
    east_south: Game
    west_midwest: Game


@dataclass
class Prediction:
    regions: dict[Regions, dict[Round, list[Game]]]
    final_4: Final4Predictions
    championship: Game


def region_teams(region: Regions) -> list[Team]:
    """
    Construct team representations for a region.

    The team list is ordered by pairs that match up in the first round such that a
    balanced tree can be created with these teams as the leaf nodes, and the games will
    be played out as they are in the actual tournament.
    """
    seed_order = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]

    return [Team(seed, region) for seed in seed_order]


def build_tournament() -> Game:
    """
    Construct the tree of games representing the NCAA tournament.
    """
    # The easiest way to think about building the tournament is to construct each
    # regional tournament, then create the semis and finals manually with the desired
    # region matchups.

    region_finals = {}
    for region in Regions:
        games = [Game(Round.SEEDING, winner=t) for t in region_teams(region)]

        round_num = 1
        while len(games) > 1:
            new_games = []
            for left, right in zip(games[::2], games[1::2], strict=True):
                new_games.append(Game(Round(round_num), left=left, right=right))

            round_num += 1
            games = new_games

        region_finals[region] = games[0]

    semis = [
        Game(Round.FINAL_4, region_finals[Regions.EAST], region_finals[Regions.SOUTH]),
        Game(
            Round.FINAL_4, region_finals[Regions.WEST], region_finals[Regions.MIDWEST]
        ),
    ]

    finals = Game(Round.CHAMPIONSHIP, *semis)

    return finals


def win_loss(rand: random.Random, probability: float) -> bool:
    """
    Return a boolean win/loss indicator based on the probability that the team wins.

    :param rand: Random instance to use for generating random numbers.
    :param probability: The probability that the team wins as a float in the range
        [0, 1).
    :returns: ``True`` if the team wins, and ``False`` otherwise.
    """
    return rand.random() < probability


def pick_winner(
    random: random.Random, team_a: Team, team_b: Team, round: Round
) -> Team:
    """
    Pick a winning team for a particular game.

    :param random: The random generator used to test probabilities.
    :param team_a: The first team from the game.
    :param team_b: The second team from the game.
    :param round: The round the game is being played in.
    :returns: The team picked to be the winner.
    """
    probabilities = WIN_PROBABILITIES[round]

    teams = [team_a, team_b]
    teams.sort(key=lambda t: t.seed)
    high, low = teams

    # There are opportunities here to try out different strategies for picking winners.
    # - Based solely on lower seed's probability
    # - Based solely on higher seed's probability
    # - Use either high or low seed probability depending on which round we're in
    # - Run both high and low probabilities until they agree
    if win_loss(random, probabilities[low.seed - 1]):
        return low

    return high


def simulate_game(random: random.Random, game: Game) -> Game:
    """
    Simulate a game to predict winners.

    If the games leading to this one have not been simulated yet, they will be simulated
    first.
    """

    if not game.left or not game.right:
        raise ValueError("Cannot simulate a game without both left and right matches.")

    # Classic recursive operation. Traverse this node's left and right trees to ensure
    # they have winners before computing the result for this node.

    if not game.left.winner:
        game.left = simulate_game(random, game.left)

    if not game.right.winner:
        game.right = simulate_game(random, game.right)

    game.winner = pick_winner(random, game.left.winner, game.right.winner, game.round)

    return game


def collect_games_by_round(
    game: Game,
    collection: dict[Round, list[Game]] = None,
    lowest_round: Round = Round.ROUND_OF_64,
):
    """
    Collect games into a structure that's easier to display results from.

    A tree makes sense for showing dependencies between games, but when showing results,
    we often want to collect games by round. This function collects games into a map of
    rounds to games.

    :param collection: The collection of games. This is modified in-place.
    :param game: The game to add to the collection. The game's descendents will all be
        added as well.
    :param lowest_round: The lowest round to collect results for. Defaults to the round
        of 32 as that is the first round after some teams have been eliminated.
    """
    if collection is None:
        collection = defaultdict(list)

    if game is None or game.round.value < lowest_round.value:
        return

    collect_games_by_round(game.left, collection, lowest_round)
    collect_games_by_round(game.right, collection, lowest_round)

    collection[game.round].append(game)

    return dict(collection)


def collect_results(championship: Game) -> Prediction:
    """
    Collect results into a dictionary structure that's easier to iterate through.
    """
    east_south = championship.left
    west_midwest = championship.right

    return Prediction(
        {
            Regions.EAST: collect_games_by_round(east_south.left),
            Regions.SOUTH: collect_games_by_round(east_south.right),
            Regions.WEST: collect_games_by_round(west_midwest.left),
            Regions.MIDWEST: collect_games_by_round(west_midwest.right),
        },
        Final4Predictions(east_south, west_midwest),
        championship,
    )
