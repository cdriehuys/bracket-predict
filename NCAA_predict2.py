#!/usr/bin/env python3

# NCAA Bracket predictor

import argparse
import random
import sys
from typing import Optional


def win_loss(probability):
    """
    Determine if a team wins or loses based on their win probability.

    :param probability: The probability of the team winning.
    :returns: A boolean indicating if the team wins.
    """
    return random.random() < probability


def advance_seeds(init_seeds, prob_list):
    # Play a list of initial seeded teams against each other and return list of advancing teams by seed
    # probList contains list of odds that the associated seed wins
    # first and last in list play each other in any given round before the final 4
    numTeams = len(init_seeds)

    # Construct parallel lists for teams and opponents. The top teams are paired
    # with the lowest ranked opponents, ie we iterate from the beginning of the
    # list for the first team and the back of the list for their opponent.
    team_seeds = init_seeds[:numTeams//2]
    opponent_seeds = init_seeds[:numTeams//2-1:-1]

    new_seeds = []
    for team_seed, opponent_seed in zip(team_seeds, opponent_seeds):
        if win_loss(prob_list[team_seed-1]):
            new_seeds.append(team_seed)
        else:
            new_seeds.append(opponent_seed)

    return new_seeds


def advance_team(seeds, regions, prob_list):
    # Needed for individual Final Four and Final games where equal seeds can meet
    # Takes the 2 seeds and their regions, and probabilities by seed
    # Returns the winner and their region
    if seeds[0]==seeds[1]:            # if equal seeds just flip a coin
        if win_loss(0.5):
            winning_seed = seeds[0]
            winning_region = regions[0]
        else:
            winning_seed = seeds[1]
            winning_region = regions[1]
    else:                             # otherwise play out according to seed probabilities
        worse_team = seeds.index(max(seeds))  # find index of worse-seeded team and use their probabilities
        better_team = seeds.index(min(seeds))
        if win_loss(prob_list[seeds[worse_team]]):
            winning_seed = seeds[worse_team]
            winning_region = regions[worse_team]
        else:
            winning_seed = seeds[better_team]
            winning_region = regions[better_team]
    return winning_seed, winning_region


# list of win probabilities by seed for each round - source: https://www.betfirm.com/seeds-national-championship-odds/
win_probs = [
    [0.99, 0.93, 0.86, 0.79, 0.65, 0.62, 0.61, 0.49, 0.51, 0.39, 0.38, 0.35, 0.21, 0.14, 0.07, 0.01], # round of 64
    [0.85, 0.67, 0.62, 0.60, 0.53, 0.47, 0.31, 0.22, 0.10, 0.41, 0.45, 0.42, 0.19, 0.09, 0.36, 0.00], # round of 32
    [0.79, 0.72, 0.49, 0.32, 0.23, 0.36, 0.34, 0.56, 0.63, 0.38, 0.35, 0.09, 0.00, 0.00, 0.25, 0.00], # sweet 16
    [0.59, 0.47, 0.44, 0.61, 0.75, 0.19, 0.30, 0.67, 0.40, 0.11, 0.56, 0.00, 0.00, 0.00, 0.00, 0.00], # elite 8
    [0.62, 0.41, 0.65, 0.29, 0.44, 0.67, 0.33, 0.67, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00], # final 4
    [0.65, 0.38, 0.36, 0.50, 0.00, 0.50, 1.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00] # championship
]


def parse_args(args: Optional[list[str]] = None):
    parser = argparse.ArgumentParser(
        description="Predict NCAA tournament results"
    )

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

    final_four = ['East','West','South','Midwest']  # List of region in the final four
    final_four_seeds = [None, None, None, None]      # Placeholder list for seeds from each region in the final
    final_seeds = [None, None]                      # place holder for regions that made the final
    final_regions = [None,None]                     # Place holder for seeds in the final

    # Play out the four regional tourneys to get the final four listed by seed
    for region in range(len(final_four)):
        print(f'\nProjected results from the {final_four[region]} region:')
        seeds = list(range(1,17)) # first round is just just seeded 1-16
        for round in range(4):
            seeds = advance_seeds(seeds, win_probs[round]) # advance seeds based on win probabilities for that round
            print(f'In round {round+1} these seeds will advance: {seeds}')
        final_four_seeds[region] = seeds[0] # collect the final four seeds from each region after all rounds

    # Show the Final Four and their Regions - East vs West and South vs Midwest
    print('\nYour Final Four is:')
    print(
        f'The {final_four_seeds[0]} seed from the East vs the '
        f'{final_four_seeds[1]} from the West'
    )
    print(
        f'The {final_four_seeds[2]} seed from the South vs the '
        f'{final_four_seeds[3]} from the Midwest'
    )

    # Play the two semis and capture the final seeds and regions
    for i in range(2): # step through two semi-final games
        seeds = [final_four_seeds[2*i], final_four_seeds[2*i+1]]
        regions = final_four[2*i], final_four[2*i+1]
        final_seeds[i], final_regions[i] = advance_team(seeds, regions, win_probs[4])

    # Play the final and pronounce a winner
    print('\nYour Championship Game is:')
    print(
        f'The {final_seeds[0]} seed from the {final_regions[0]} vs the '
        f'{final_seeds[1]} seed from the {final_regions[1]}'
    )
    winning_seed, winning_region = advance_team(final_seeds, final_regions, win_probs[5])
    print(f'\nAnd the winner is the {winning_seed} seed from the {winning_region}')

    print("\nTo repeat these results, use the seed:", seed)


def main():
    args = parse_args()

    predict_bracket(args.seed)


if __name__ == "__main__":
    main()
