#!/usr/bin/env python3

# NCAA Bracket predictor

import argparse
from dataclasses import dataclass
import random
import sys
from typing import Optional


@dataclass
class Team:
    seed: int
    region: str

    def __str__(self) -> str:
        return f"{self.seed} seed from the {self.region}"


def win_loss(probability):
    """
    Determine if a team wins or loses based on their win probability.

    :param probability: The probability of the team winning.
    :returns: A boolean indicating if the team wins.
    """
    return random.random() < probability


def advance_teams(teams: list[Team], prob_list: list[float]) -> list[Team]:
    # Play a list of initial seeded teams against each other and return list of advancing teams by seed
    # probList contains list of odds that the associated seed wins
    # first and last in list play each other in any given round before the final 4
    num_teams = len(teams)

    # Construct parallel lists for teams and opponents. The top teams are paired
    # with the lowest ranked opponents, ie we iterate from the beginning of the
    # list for the first team and the back of the list for their opponent.
    top_teams = teams[: num_teams // 2]
    opponents = teams[: num_teams // 2 - 1 : -1]

    winning_teams = []
    for team, opponent in zip(top_teams, opponents):
        if win_loss(prob_list[team.seed - 1]):
            winning_teams.append(team)
        else:
            winning_teams.append(opponent)

    return winning_teams


def advance_team(team_a: Team, team_b: Team, prob_list):
    # Needed for individual Final Four and Final games where equal seeds can meet
    # Takes the 2 seeds and probabilities by seed
    # Returns the winner

    # For equal seeds, it's a coin flip.
    if team_a.seed == team_b.seed:
        if win_loss(0.5):
            return team_a

        return team_b

    teams = [team_a, team_b]
    teams.sort(key=lambda t: t.seed, reverse=True)

    better_team, worse_team = teams
    if win_loss(prob_list[worse_team.seed - 1]):
        return worse_team

    return better_team


# list of win probabilities by seed for each round - source: https://www.betfirm.com/seeds-national-championship-odds/
win_probs = [
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


def predict_bracket(seed: Optional[str]):
    if seed is None:
        # If no seed, generate one that can be passed in to repeat the run in
        # the future.
        seed = str(random.randrange(sys.maxsize))

    print("Random seed:", seed)
    random.seed(seed)

    regions = ["East", "West", "South", "Midwest"]
    final_four_teams = {}

    # Play out the four regional tourneys to get the final four listed by seed
    for region in regions:
        print(f"\nProjected results from the {region} region:")
        teams = [Team(seed, region) for seed in range(1, 17)]
        for round in range(4):
            teams = advance_teams(
                teams, win_probs[round]
            )  # advance seeds based on win probabilities for that round
            print(
                f"In round {round+1} these teams will advance: "
                f"{[t.seed for t in teams]}"
            )

        final_four_teams[region] = teams[
            0
        ]  # collect the final four seeds from each region after all rounds

    # Show the Final Four and their Regions - East vs West and South vs Midwest
    print("\nYour Final Four is:")
    print(f'The {final_four_teams["East"]} vs the {final_four_teams["West"]}')
    print(f'The {final_four_teams["South"]} vs the {final_four_teams["Midwest"]}')

    final_teams = [
        advance_team(final_four_teams["East"], final_four_teams["West"], win_probs[4]),
        advance_team(
            final_four_teams["South"], final_four_teams["Midwest"], win_probs[4]
        ),
    ]

    # Play the final and pronounce a winner
    print("\nYour Championship Game is:")
    print(f"The {final_teams[0]} vs the {final_teams[1]}")
    winner = advance_team(*final_teams, win_probs[5])
    print(f"\nAnd the winner is the {winner}")

    print("\nTo repeat these results, use the seed:", seed)


def main():
    args = parse_args()

    predict_bracket(args.seed)


if __name__ == "__main__":
    main()
