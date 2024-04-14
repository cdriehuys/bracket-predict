# NCAA Bracket predictor
import random

def win_loss(probability):  
    # Figure out if specified team wins based on provided probability
    if random.random() < probability:
        return 1  # Victory!
    else:
        return 0  # Loss

def advance_seeds(initSeeds,probList):
    # Play a list of initial seeded teams against each other and return list of advancing teams by seed
    # probList contains list of odds that the associated seed wins
    # first and last in list play each other in any given round before the final 4
    numTeams = len(initSeeds)
    newSeeds = []
    for team in range(0,numTeams//2): # go through the first half of the list
        teamSeed = initSeeds[team]
        opponentSeed = initSeeds[numTeams-team-1] # oponent seed
        if win_loss(probList[teamSeed-1]):
            newSeeds.append(teamSeed)
        else:
            newSeeds.append(opponentSeed)
    return newSeeds

def advance_team(seeds,regions,probList):
    # Needed for individual Final Four and Final games where equal seeds can meet
    # Takes the 2 seeds and their regions, and probabilities by seed
    # Returns the winner and their region
    if seeds[0]==seeds[1]:            # if equal seeds just flip a coin
        if win_loss(0.5):
            winningSeed = seeds[0]
            winningRegion = regions[0]
        else:
            winningSeed =seeds[1]
            winningRegion = regions[1]
    else:                             # otherwise play out according to seed probabilities
        worse_team = seeds.index(max(seeds))  # find index of worse-seeded team and use their probabilities
        better_team = seeds.index(min(seeds))
        if win_loss(probList[seeds[worse_team]]):  
            winningSeed = seeds[worse_team]
            winningRegion = regions[worse_team]
        else:
            winningSeed = seeds[better_team]
            winningRegion = regions[better_team]
    return winningSeed, winningRegion

# list of win probabilities by seed for each round - source: https://www.betfirm.com/seeds-national-championship-odds/
winProbs = [
    [0.99, 0.93, 0.86, 0.79, 0.65, 0.62, 0.61, 0.49, 0.51, 0.39, 0.38, 0.35, 0.21, 0.14, 0.07, 0.01], # round of 64
    [0.85, 0.67, 0.62, 0.60, 0.53, 0.47, 0.31, 0.22, 0.10, 0.41, 0.45, 0.42, 0.19, 0.09, 0.36, 0.00], # round of 32
    [0.79, 0.72, 0.49, 0.32, 0.23, 0.36, 0.34, 0.56, 0.63, 0.38, 0.35, 0.09, 0.00, 0.00, 0.25, 0.00], # sweet 16
    [0.59, 0.47, 0.44, 0.61, 0.75, 0.19, 0.30, 0.67, 0.40, 0.11, 0.56, 0.00, 0.00, 0.00, 0.00, 0.00], # elite 8
    [0.62, 0.41, 0.65, 0.29, 0.44, 0.67, 0.33, 0.67, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00], # final 4
    [0.65, 0.38, 0.36, 0.50, 0.00, 0.50, 1.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00] # championship
]

finalFour = ['East','West','South','Midwest']  # List of region in the final four
finalFourSeeds = [None, None, None, None]      # Placeholder list for seeds from each region in the final
finalSeeds = [None, None]                      # place holder for regions that made the final
finalRegions = [None,None]                     # Place holder for seeds in the final

# Play out the four regional tourneys to get the final four listed by seed
for region in range(len(finalFour)):
    print('\nProjected results from the ' +finalFour[region] + ' region:')
    seeds = list(range(1,17)) # first round is just just seeded 1-16
    for round in range(0,4):
        seeds = advance_seeds(seeds,winProbs[round]) # advance seeds based on win probabilities for that round
        print('In round ' + str(round+1) + ' these seeds will advance: ' + str(seeds))
    finalFourSeeds[region] = seeds[0] # collect the final four seeds from each region after all rounds

# Show the Final Four and their Regions - East vs West and South vs Midwest
print('\nYour Final Four is: ')
print('The ' + str(finalFourSeeds[0]) + ' seed from the East vs the ' \
     + str(finalFourSeeds[1]) + ' from the West')
print('The ' + str(finalFourSeeds[2]) + ' seed from the South vs the ' \
     + str(finalFourSeeds[3]) + ' from the Midwest')

# Play the two semis and capture the final seeds and regions
for i in range(2): # step through two semi-final games
    seeds = [finalFourSeeds[2*i],finalFourSeeds[2*i+1]]
    regions = finalFour[2*i],finalFour[2*i+1]
    finalSeeds[i],finalRegions[i] = advance_team(seeds,regions, winProbs[4])

# Play the final and pronounce a winner
print('\nYour Champtionship Game is: ')
print('The ' + str(finalSeeds[0]) + ' seed from the ' + finalRegions[0] \
      + ' vs the ' + str(finalSeeds[1]) + ' seed from the ' + finalRegions[1])
winningSeed,winningRegion = advance_team(finalSeeds,finalRegions,winProbs[5])
print('\nAnd the winner is the ' +str(winningSeed) + ' seed from the ' + winningRegion)