# NCAA Predicitons

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import scipy as sp

## Read in CSV files
# teams = pd.read_csv("Teams.csv")
tour_comp = pd.read_csv("TourneyCompactResults.csv")
# tour_deta = pd.read_csv("TourneyDetailedResults.csv")
tour_seed = pd.read_csv("TourneySeeds.csv")
tour_slot = pd.read_csv("TourneySlots.csv")
# seas_comp = pd.read_csv("RegularSeasonCompactResults.csv")
# seas_deta = pd.read_csv("RegularSeasonDetailedResults.csv")
# seasons = pd.read_csv("Seasons.csv")
mas_his = pd.read_csv("massey_ordinals_2003-2015.csv")
# mas_new = pd.read_csv("MasseyOrdinals2016ThruDay128_59systems.csv")
ratings = list(mas_his['sys_name'].unique())
# print(ratings)

rpi_his = pd.DataFrame({'season': mas_his.loc[(mas_his['sys_name'] == 'RPI') & (mas_his['rating_day_num'] == 133), 'season'],
						'rating_day_num': mas_his.loc[(mas_his['sys_name'] == 'RPI') & (mas_his['rating_day_num'] == 133), 'rating_day_num'],
						'sys_name': mas_his.loc[(mas_his['sys_name'] == 'RPI') & (mas_his['rating_day_num'] == 133), 'sys_name'],
						'team': mas_his.loc[(mas_his['sys_name'] == 'RPI') & (mas_his['rating_day_num'] == 133), 'team'],
						'orank': mas_his.loc[(mas_his['sys_name'] == 'RPI') & (mas_his['rating_day_num'] == 133), 'orank']
						})


def transform_mas(ratings):
	"""Change vertical structure to a wider structure."""
	mas_list_ords = []
	mas_list_team = []
	mas_list_season = []

	for r in ratings:
		temp_max = mas_his.loc[mas_his['sys_name'] == r, 'rating_day_num'].max()
		# print(temp_max)

		mas_list_ords.append(list(mas_his.loc[(mas_his['sys_name'] == r) & (mas_his['rating_day_num'] == temp_max), 'orank']))
		mas_list_team.append(list(mas_his.loc[(mas_his['sys_name'] == r) & (mas_his['rating_day_num'] == temp_max), 'team']))
		mas_list_season.append(list(mas_his.loc[(mas_his['sys_name'] == r) & (mas_his['rating_day_num'] == temp_max), 'season']))

		# print(mas_lists)
		break
	return None

mas_ord = transform_mas(ratings)


def logloss(act, pred):
    """Kaggles scoring function"""
    epsilon = 1e-15
    pred = sp.maximum(epsilon, pred)
    pred = sp.minimum(1-epsilon, pred)
    ll = sum(act*sp.log(pred) + sp.subtract(1,act)*sp.log(sp.subtract(1,pred)))
    ll = ll * -1.0/len(act)
    return ll


def create_index(df, a, b):
	"""Creates index by combining a_b, primarily for Season_Team"""
	x = list(df[a])
	y = list(df[b])
	idx = [str(x[i])+"_"+str(y[i]) for i in range(0, len(x))]
	return idx


def create_dict(a, b):
	"""Creates a dict of index:value, for adding values to the tour_comp or whatever"""
	a = list(a)
	b = list(b)
	return {a[i]:b[i] for i in range(0,len(a))}


print(rpi_his.head())
# rpi_his.to_csv("rpi_history.csv", index=False) # used for creating an excel/gnumeric friendly sized file

rpi_his['Index'] = create_index(rpi_his, 'season', 'team')
rpi_mapping = create_dict(rpi_his['Index'], rpi_his['orank'])
 
tour_seed['Index'] = create_index(tour_seed, 'Season', 'Team')
seed_mapping = create_dict(tour_seed["Index"], tour_seed["Seed"])



def set_matchups(season):
	"""Compile and return list of matchups for a given season (for Contest 2)"""

	slots = list(tour_slot["Slot"].loc[tour_slot["Season"] == season]) # get list of slots, e.g. R1W1
	strongseeds = list(tour_slot["Strongseed"].loc[tour_slot["Season"] == season]) # get list of strongseeds
	weakseeds = list(tour_slot["Weakseed"].loc[tour_slot["Season"] == season]) # get list of weakseeds
	seeds = list(tour_seed["Seed"].loc[tour_seed["Season"] == season]) # get list of seeds
	teams = list(tour_seed["Team"].loc[tour_seed["Season"] == season]) # get list of teams ordered by seed

	team_dict = {seeds[i]:teams[i] for i in range(0,len(seeds))} # make dict of teams by seed (probably redundant)
	slot_dict = {slots[j]:[strongseeds[j], weakseeds[j]] for j in range(0, len(slots))} # make dict of slots, value = slots that comprise key slot

	eligible = {} # initialize empty dict of teams by slot, {"slot":[[strongseed list],[weakseed list]]}
	# count = 0 # used for testing
	for s in slots:
		eligible[s] = [] # each slot has a list of 2 sets of teams that could face each other
		for t in slot_dict[s]:
			if t in team_dict: # if slot component is a team, create a list element of the team id
				team_id = []
				team_id.append(team_dict[t]) # could probably combine these 2 lines into team_id = list(team_dict[t])
				eligible[s].append(team_id) # append team_id to eligible teams for that slot
			elif t in eligible: # if t is a slot itself
				temp_list = []
				for u in eligible[t]: # for teams from prior round, add them all to a list of teams for 1/2 of this slots matchups
					if type(u) is list: # to avoid nesting lists, 
						temp_list += u
					else:
						temp_list.append(u) # should all be list now, legacy element, should never fire
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


# set_matchups(2015)

def create_train_set():

	tour_comp['Matchup'] = tour_comp['Season'].astype(str) + "_" + tour_comp[['Wteam','Lteam']].min(axis=1).astype(str) + "_" + tour_comp[['Wteam','Lteam']].max(axis=1).astype(str)
	tour_comp['Windex'] = tour_comp['Season'].astype(str) + "_" + tour_comp['Wteam'].astype(str)
	tour_comp['Lindex'] = tour_comp['Season'].astype(str) + "_" + tour_comp['Lteam'].astype(str)
	tour_comp['Wseed'] = tour_comp['Windex'].apply(lambda x: seed_mapping[x])
	tour_comp['Lseed'] = tour_comp['Lindex'].apply(lambda x: seed_mapping[x])
	tour_comp['Wseed'] = tour_comp['Wseed'].apply(lambda x: int(x[1:3]))
	tour_comp['Lseed'] = tour_comp['Lseed'].apply(lambda x: int(x[1:3]))
	tour_comp['Order'] = 1
	tour_comp.loc[tour_comp['Wteam'] > tour_comp['Lteam'], 'Order'] = -1
	tour_comp['Seed_Diff'] = tour_comp['Lseed'] - tour_comp['Wseed']
	tour_comp['Seed_Diff'] = tour_comp['Seed_Diff'] * tour_comp['Order']
	tour_comp['Winner'] = 1 # winner is on left
	tour_comp.loc[tour_comp['Wteam'] > tour_comp['Lteam'], 'Winner'] = 0 # winner is on right
	tour_comp['W_RPI'] = tour_comp['Windex'].apply(lambda x: rpi_mapping[x] if x in rpi_mapping else 0)
	tour_comp['L_RPI'] = tour_comp['Lindex'].apply(lambda x: rpi_mapping[x] if x in rpi_mapping else 0)
	tour_comp['RPI_Diff'] = tour_comp['L_RPI'] - tour_comp['W_RPI']
	tour_comp['RPI_Diff'] = tour_comp['RPI_Diff'] * tour_comp['Order']

	# print(tour_comp.head(10))
	return None


create_train_set()

alg = LinearRegression()
# predictors = ['Seed_Diff']
predictors = ['RPI_Diff']

# tour_comp = tour_comp.loc[tour_comp['Season'] >= 2003]

alg.fit(tour_comp[predictors], tour_comp["Winner"])
predictions = alg.predict(tour_comp[predictors])
predictions[predictions > 1] = 1

tour_comp['pred'] = predictions
# print(tour_comp.head())

submission = pd.DataFrame({'id': tour_comp.loc[tour_comp['Season'] >= 2012, 'Matchup'],
						   'pred': tour_comp.loc[tour_comp['Season'] >= 2012, 'pred'],
						   'win': tour_comp.loc[tour_comp['Season'] >= 2012, 'Winner']
						   })

# print(submission.head(10))
# print(submission.describe())

submission.to_csv("kaggleNCAA.csv", index=False)

print(logloss(submission['win'], submission['pred']))