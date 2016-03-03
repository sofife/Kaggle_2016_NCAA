# NCAA Predicitons

import numpy as np
import pandas as pd


# teams = pd.read_csv("Teams.csv")
# tour_comp = pd.read_csv("TourneyCompactResults.csv")
# tour_deta = pd.read_csv("TourneyDetailedResults.csv")
tour_seed = pd.read_csv("TourneySeeds.csv")
tour_slot = pd.read_csv("TourneySlots.csv")
# seas_comp = pd.read_csv("RegularSeasonCompactResults.csv")
# seas_deta = pd.read_csv("RegularSeasonDetailedResults.csv")
# seasons = pd.read_csv("Seasons.csv")

# print(tour_slot.describe())
# print(teams.iloc[[0]])
# print(teams.head())
# print(tour_slot)

print(tour_slot.loc[tour_slot["Season"] == 2015])
# print(tour_seed.loc[tour_seed["Season"] == 2015])

def set_matchups(season):
	"""Solve matchups for a given season"""

	slots = list(tour_slot["Slot"].loc[tour_slot["Season"] == season])
	strongseeds = list(tour_slot["Strongseed"].loc[tour_slot["Season"] == season])
	weakseeds = list(tour_slot["Weakseed"].loc[tour_slot["Season"] == season])
	seeds = list(tour_seed["Seed"].loc[tour_seed["Season"] == season])
	teams = list(tour_seed["Team"].loc[tour_seed["Season"] == season])
	team_dict = {seeds[i]:teams[i] for i in range(0,len(seeds))}
	print(seeds)
	print(team_dict)

	slot_dict = {slots[j]:[strongseeds[j], weakseeds[j]] for j in range(0, len(slots))} 
	print(slot_dict)

	print(slots[0])

	eligible = {}
	count = 0
	for s in slots:
		eligible[s] = []
		for t in slot_dict[s]:
			print("t = ",t)
			if t in team_dict:
				# print(1)
				team_id = []
				team_id.append(team_dict[t])
				# print("team_id = ",team_id)
				eligible[s].append(team_id)
				# print(2)
			elif t in eligible:
				print(eligible[t])
				temp_list = []
				for u in eligible[t]:
					print("u = ",u)
					if type(u) is list:
						temp_list += u
					else:
						temp_list.append(u)
				print("u2 =",temp_list)
				# eligible[s] += temp_list
				eligible[s].append(temp_list)
			else:
				pass
		count += 1
		# if count > 50:
		# 	break
		
	print(eligible)

	lengths = []
	for key in eligible:
		lengths.append(len(eligible[key]))
		# pass

	print(lengths, len(lengths))

	matchups = []
	for key in eligible:
		group_A = eligible[key][0]
		group_B = eligible[key][1]
		for a in group_A:
			# temp_match = []
			for b in group_B:
				
				# print(temp_match)
				matchups.append(str(season)+'_'+str(min(a,b))+'_'+str(max(a,b)))
				# print(matchups)
				# break
			# break
		# break

	print(matchups, len(matchups))

	return None

set_matchups(2015)

