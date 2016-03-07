# NCAA Predicitons

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import scipy as sp

# teams = pd.read_csv("Teams.csv")
tour_comp = pd.read_csv("TourneyCompactResults.csv")
# tour_deta = pd.read_csv("TourneyDetailedResults.csv")
tour_seed = pd.read_csv("TourneySeeds.csv")
tour_slot = pd.read_csv("TourneySlots.csv")
# seas_comp = pd.read_csv("RegularSeasonCompactResults.csv")
# seas_deta = pd.read_csv("RegularSeasonDetailedResults.csv")
# seasons = pd.read_csv("Seasons.csv")

tour_seed['Index'] = tour_seed['Season'].astype(str) + "_" + tour_seed['Team'].astype(str)
seed_list = list(tour_seed["Seed"])
index_list = list(tour_seed["Index"])
seed_mapping = {index_list[i]:seed_list[i] for i in range(0,len(seed_list))}
print(seed_mapping)
# print(tour_seed.describe())
# print(teams.iloc[[0]])
print(tour_seed.head())
# print(tour_slot)

# print(tour_slot.loc[tour_slot["Season"] == 2015])
# print(tour_seed.loc[tour_seed["Season"] == 2015])


def logloss(act, pred):
    epsilon = 1e-15
    pred = sp.maximum(epsilon, pred)
    pred = sp.minimum(1-epsilon, pred)
    ll = sum(act*sp.log(pred) + sp.subtract(1,act)*sp.log(sp.subtract(1,pred)))
    ll = ll * -1.0/len(act)
    return ll


def set_matchups(season):
	"""Compile and return list of matchups for a given season"""

	slots = list(tour_slot["Slot"].loc[tour_slot["Season"] == season]) # get list of slots, e.g. R1W1
	strongseeds = list(tour_slot["Strongseed"].loc[tour_slot["Season"] == season]) # get list of strongseeds
	weakseeds = list(tour_slot["Weakseed"].loc[tour_slot["Season"] == season]) # get list of weakseeds
	seeds = list(tour_seed["Seed"].loc[tour_seed["Season"] == season]) # get list of seeds
	teams = list(tour_seed["Team"].loc[tour_seed["Season"] == season]) # get list of teams ordered by seed

	team_dict = {seeds[i]:teams[i] for i in range(0,len(seeds))} # make dict of teams by seed (probably redundant)
	# print(team_dict)
	slot_dict = {slots[j]:[strongseeds[j], weakseeds[j]] for j in range(0, len(slots))} # make dict of slots, value = slots that comprise key slot
	# print(slot_dict)


	eligible = {} # initialize empty dict of teams by slot, {"slot":[[strongseed list],[weakseed list]]}
	# count = 0 # used for testing
	for s in slots:
		eligible[s] = [] # each slot has a list of 2 sets of teams that could face each other
		for t in slot_dict[s]:
			# print("t = ",t)
			if t in team_dict: # if slot component is a team, create a list element of the team id
				# print(1)
				team_id = []
				team_id.append(team_dict[t]) # could probably combine these 2 lines into team_id = list(team_dict[t])
				# print("team_id = ",team_id)
				eligible[s].append(team_id) # append team_id to eligible teams for that slot
				# print(2)
			elif t in eligible: # if t is a slot itself
				# print(eligible[t])
				temp_list = []
				for u in eligible[t]: # for teams from prior round, add them all to a list of teams for 1/2 of this slots matchups
					# print("u = ",u)
					if type(u) is list: # to avoid nesting lists, 
						temp_list += u
					else:
						temp_list.append(u) # should all be list now, legacy element, should never fire
				# print("u2 =",temp_list)
				eligible[s].append(temp_list) # add list of opponents to eligible slot for that round
			else:
				pass
		# count += 1 # for testing
		# if count > 50:
		# 	break

	# lengths = []
	# for key in eligible:
	# 	lengths.append(len(eligible[key]))
		# pass
	# print(lengths, len(lengths)) # testing to make sure all eligible has length 2

	matchups = [] # initialize list of matchups
	for key in eligible: # iterate slots
		group_A = eligible[key][0] # take first list, could replace in list comp below
		group_B = eligible[key][1] # take second list, could replace in list comp below
		# list comp for all matchups for a given slot
		temp_match = [str(season)+'_'+str(min(a,b))+'_'+str(max(a,b)) for a in group_A for b in group_B]
		matchups += temp_match # append to matchups

	# print(matchups, len(matchups)) # test for correct # of matchups

	return matchups

set_matchups(2015)

# print(tour_comp.describe())

# seed_mapping = {}

# def get_seed(row):
# 	"""Takes in a row, and returns the seed of the winning and losing team"""
# 	index = row['Windex']
# 	if index not in seed_mapping:
# 		seed_mapping[index] = tour_seed.loc[tour_seed['Index'] == index, 'Seed']

# 	# return seed_mapping[index]
# 	return None


# Add index column to tour_seeds -> YYYY_TeamId, then use that index to return the seeds
# Wseeds = tour_comp.apply(get_seed)


def create_train_set():

	tour_comp['Matchup'] = tour_comp['Season'].astype(str) + "_" + tour_comp[['Wteam','Lteam']].min(axis=1).astype(str) + "_" + tour_comp[['Wteam','Lteam']].max(axis=1).astype(str)
	tour_comp['Windex'] = tour_comp['Season'].astype(str) + "_" + tour_comp['Wteam'].astype(str)
	tour_comp['Lindex'] = tour_comp['Season'].astype(str) + "_" + tour_comp['Lteam'].astype(str)
	# tour_seed.apply(get_seed, axis=1)
	# print(seed_mapping['1985_1116'])
	# print(tour_comp.iloc[[0]])

	tour_comp['Wseed'] = tour_comp['Windex'].apply(lambda x: seed_mapping[x])
	tour_comp['Lseed'] = tour_comp['Lindex'].apply(lambda x: seed_mapping[x])
	tour_comp['Wseed'] = tour_comp['Wseed'].apply(lambda x: int(x[1:3]))
	tour_comp['Lseed'] = tour_comp['Lseed'].apply(lambda x: int(x[1:3]))
	tour_comp['Order'] = 1
	tour_comp.loc[tour_comp['Wteam'] > tour_comp['Lteam'], 'Order'] = -1
	tour_comp['SeedDiff'] = tour_comp['Lseed'] - tour_comp['Wseed']
	tour_comp['SeedDiff'] = tour_comp['SeedDiff'] * tour_comp['Order']
	tour_comp['Winner'] = 1
	tour_comp.loc[tour_comp['Wteam'] > tour_comp['Lteam'], 'Winner'] = 0
	print(tour_comp.head(10))


create_train_set()

alg = LinearRegression()
predictors = ['SeedDiff']

alg.fit(tour_comp[predictors], tour_comp["Winner"])
predictions = alg.predict(tour_comp[predictors])
predictions[predictions > 1] = 1

tour_comp['pred'] = predictions
print(tour_comp.head())

submission = pd.DataFrame({'id': tour_comp.loc[tour_comp['Season'] >= 2012, 'Matchup'],
						   'pred': tour_comp.loc[tour_comp['Season'] >= 2012, 'pred'],
						   'win': tour_comp.loc[tour_comp['Season'] >= 2012, 'Winner']
						   })

print(submission.head(10))

# print(submission.describe())

submission.to_csv("kaggleNCAA.csv", index=False)

print(logloss(submission['win'], submission['pred']))