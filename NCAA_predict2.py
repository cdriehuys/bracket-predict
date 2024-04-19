#!/usr/bin/env python3

# NCAA Bracket predictor

import argparse
import random
import sys
from dataclasses import dataclass
from typing import Optional, Union

# list of win probabilities by seed for each round - source: https://www.betfirm.com/seeds-national-championship-odds/
WIN_PROBABILITIES = [
    [
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
    ],  # round of 64
    [
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
    ],  # round of 32
    [
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
    ],  # sweet 16
    [
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
    ],  # elite 8
    [
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
    ],  # final 4
    [
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
    ],  # championship
]


@dataclass
class Team:
    seed: int
    region: str

    def __str__(self) -> str:
        return f"{self.seed} seed from the {self.region}"

    def as_dict(self):
        return {
            "seed": self.seed,
            "region": self.region,
        }


@dataclass
class Game:
    name: str

    left: Optional["Game"] = None
    right: Optional["Game"] = None
    winner: Optional[Team] = None

    def as_dict(self):
        info = {"name": self.name}
        info["left"] = self.left.as_dict() if self.left else None
        info["right"] = self.right.as_dict() if self.right else None
        info["winner"] = self.winner.as_dict() if self.winner else None

        return info


def region_teams(region: str) -> list[Team]:
    seed_order = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]

    return [Team(seed, region) for seed in seed_order]


def build_tournament() -> Game:
    rounds = ["Final 4", "Elite 8", "Sweet 16", "Round of 32", "Round of 64"]
    regions = ["East", "South", "West", "Midwest"]

    region_finals = {}
    for region in regions:
        games = [Game(name="Seeding", winner=t) for t in region_teams(region)]

        round_num = 1
        while len(games) > 1:
            new_games = []
            for left, right in zip(games[::2], games[1::2], strict=True):
                new_games.append(Game(name=rounds[-round_num], left=left, right=right))

            round_num += 1
            games = new_games

        region_finals[region] = games[0]

    semis = [
        Game("Final 4 - East/South", region_finals["East"], region_finals["South"]),
        Game("Final 4 - West/Midwest", region_finals["West"], region_finals["Midwest"]),
    ]

    finals = Game("Championship", *semis)

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


def pick_winner(random: random.Random, team_a: Team, team_b: Team, depth: int) -> Team:
    probabilities = WIN_PROBABILITIES[-(depth + 1)]

    teams = [team_a, team_b]
    teams.sort(key=lambda t: t.seed)
    high, low = teams

    if win_loss(random, probabilities[low.seed - 1]):
        return low

    return high


def simulate_game(random: random.Random, game: Game, depth=0) -> Game:
    if not game.left or not game.right:
        raise ValueError("Cannot simulate a game without both left and right matches.")

    if not game.left.winner:
        game.left = simulate_game(random, game.left, depth + 1)

    if not game.right.winner:
        game.right = simulate_game(random, game.right, depth + 1)

    game.winner = pick_winner(random, game.left.winner, game.right.winner, depth)

    return game


def parse_args(args: Optional[list[str]] = None):
    parser = argparse.ArgumentParser(description="Predict NCAA tournament results")

    parser.add_argument(
        "--seed",
        help=(
            "Seed to provide to the random generator. Providing the same seed "
            "will yield the same results."
        ),
    )

    return parser.parse_args(args)


def collect_display_games(
    collection: list[list[Team]], round_names: list[str], game: Game, depth: int = 0
):
    if game is None or depth >= len(round_names):
        return

    collect_display_games(collection, round_names, game.left, depth + 1)
    collect_display_games(collection, round_names, game.right, depth + 1)

    if game.winner:
        collection[depth].append(game.winner)


def display_region_results(region: str, game: Game):
    round_names = ["Elite 8", "Sweet 16", "Round of 32", "Round of 64"]
    round_results = [[] for _ in round_names]

    collect_display_games(round_results, round_names, game)

    print(f"\nResults for the {region}:")
    for round_name, winners in zip(round_names[::-1], round_results[::-1]):
        seeds = ", ".join(str(t.seed) for t in winners)
        print(f"  {round_name} winners: {seeds}")

    print(f"  {region} winner: {game.winner.seed} seed")


def display_bracket(championship: Game):
    east_south = championship.left
    west_midwest = championship.right

    display_region_results("East", east_south.left)
    display_region_results("South", east_south.right)
    display_region_results("West", west_midwest.left)
    display_region_results("Midwest", west_midwest.right)

    print("\nFinal Four results:")
    print(f"  East/South:   {east_south.winner}")
    print(f"  West/Midwest: {west_midwest.winner}")

    print(f"\nChampion: {championship.winner}")


def predict_bracket(seed: Optional[Union[str, int]]):
    if seed is None:
        # If no seed, generate one that can be passed in to repeat the run in
        # the future.
        seed = str(random.randrange(sys.maxsize))

    print("Random seed:", seed)
    local_random = random.Random(seed)

    tournament = build_tournament()
    championship = simulate_game(local_random, tournament)

    display_bracket(championship)

    print("\nTo repeat these results, use the seed:", seed)


def main():
    args = parse_args()

    predict_bracket(args.seed)


if __name__ == "__main__":
    main()
