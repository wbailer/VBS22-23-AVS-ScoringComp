import pandas as pd
import numpy as np
import json
import copy

from scipy import stats

filenames = {}
filenames['2022'] = ['../VBS22-AVS-Analysis/data/avs-submissions.csv','']
filenames['2023'] = ['../VBS23-Post-Hoc-Analysis/data/processed/avs-submissions.csv','../VBS23-Post-Hoc-Analysis/data/raw/scores-vbsofficial2023.csv']



def read_data(submission_file, score_file):

    subm = pd.read_csv(submission_file)
    scores = {}

    if len(score_file)>0:

        sdata = pd.read_csv(score_file)
        sdata = sdata.loc[sdata['group']=='AVS']
		
        for task in sdata['task'].unique():
            scores[task] = {}
            sd_task = sdata.loc[sdata['task']==task]
            for team in sd_task['team']:
                scores[task][team] = float(sd_task.loc[sd_task['team']==team]['score'])
	
	
    return subm, scores
	
def merge_ranges(ranges,overlap):

    if len(ranges)==0:
        return []
		
    pairs = copy.deepcopy(ranges)
    pairs.sort(key=lambda x: x[0])
	
    i = 1
    current = pairs[0]
	
    merged = []
 
    while i < len(pairs):

        next = pairs[i]

        # if overlapping, merge
        if current[1] + overlap >= next[0]:
            current[1] = next[1]
		# add to list and continue
        else:
            merged.append(current)
            current = next
        i = i+1
    merged.append(current)
	
		
    return merged
	
def countQuantized(corr):

    cq = 0
	
    for item in corr['item'].unique():
	
        corr_item = corr.loc[corr['item']==item]

        ranges = []	
		
        for index, row in corr_item.iterrows():
	
            r = [int(row['start']),int(row['ending'])]
            ranges.append(r)
    
	
        cq =cq + len(merge_ranges(ranges,1))
	
    return cq
	


def AVS_scorer(subm):

    scores = {}
    for task in subm['task'].unique():
        scores[task] = {}

        correctSubmissions = subm.loc[np.logical_and(subm['status']=='CORRECT', subm['task']==task)]
        wrongSubmissions = subm.loc[np.logical_and(subm['status']=='WRONG' , subm['task']==task)]
	
        totalCorrectQuantized = float(countQuantized(correctSubmissions))
		
        for team in subm['team'].unique():
            scores[task][team] = 0.0

            if len(correctSubmissions['team']==team)>0:
                correctSubs = correctSubmissions.loc[correctSubmissions['team']==team]
                correct = len(correctSubs)
            else:
                correct = 0
        
            if len(wrongSubmissions['team']==team)>0:
                wrongSubs = wrongSubmissions.loc[wrongSubmissions['team']==team]
                wrong = len(wrongSubs)
            else:
                wrong = 0
	
            if correct+wrong==0:
                continue			
				
            correctq = countQuantized(correctSubs)
	
            scores[task][team] = 100.0 * (correct / (correct + wrong / 2.0)) * (float(correctq) / totalCorrectQuantized)

      	
    return scores

def AVS2_scorer(subm):

    penaltyConstant = 0.2
    maxPointsPerTask = 1000.0

    scores = {}
    for task in subm['task'].unique():
        scores[task] = {}
	
        correctSubmissions = subm.loc[np.logical_and(subm['status']=='CORRECT' , subm['task']==task)]
        wrongSubmissions = subm.loc[np.logical_and(subm['status']=='WRONG' , subm['task']==task)]

        distinctCorrectVideos = len( correctSubmissions['item'].unique())  	

		
        for team in subm['team'].unique():
            scores[task][team] = 0.0

            subm_task_team = subm.loc[np.logical_and(subm['task']==task , subm['team']==team)]
			 
            for video in subm_task_team['item'].unique():
			
                subm_task_team_vid = subm_task_team.loc[np.logical_and(subm_task_team['item']==video,np.logical_or(subm_task_team['status']=='CORRECT',subm_task_team['status']=='WRONG'))]
			
                subm_task_team_srt = subm_task_team_vid.sort_values(['time'])
                subm_task_team_srt = subm_task_team_srt.reset_index(drop=True)

                sc = 0	
				
                if len(subm_task_team_srt[subm_task_team_srt['status']=='CORRECT'])==0:
                    sc = len(subm_task_team_srt) * -penaltyConstant
                else:
                    firstCorrectIdx = subm_task_team_srt[subm_task_team_srt['status']=='CORRECT'].index[0]				

                    sc = 1.0 - int(firstCorrectIdx) * penaltyConstant
	
                scores[task][team] = scores[task][team] + sc
				
            scores[task][team] = max(0,scores[task][team]) / distinctCorrectVideos * maxPointsPerTask 

    return scores

def compare_scores(s1,s2):
    sum = 0.0
    nsc = 0.0

    diff = {}
	
    for task in s1.keys():
        diff[task] = {}				
        for team in s1[task].keys():

            if team not in s2[task].keys():
                continue
				
            diff[task][team] = s1[task][team]-s2[task][team]
            sum = sum + diff[task][team]
            nsc = nsc + 1

			
			
    return diff, sum/nsc
    
def sum_per_team(scores,normalise=False):

    tsc = {}
    maxsc = 0

    for task in scores.keys():
		
        for team in scores[task].keys():
            if team in tsc.keys():
                tsc[team] = tsc[team] + scores[task][team]
            else:
                tsc[team] = scores[task][team]
            if tsc[team]>maxsc:
                maxsc = tsc[team]
			
    if normalise:			
        for team in tsc.keys():
            tsc[team] = tsc[team] / maxsc * 100
				
    return tsc
	
def get_ranks(scores,teamlist):

    # make sure to sort by teamlist to have the same order
    vlist = np.zeros((len(teamlist),))
	
    i=0
    for team in teamlist:

        vlist[i] = scores[team]
        i=i+1

	
    indices = list(range(len(vlist)))
    indices.sort(key=lambda x: vlist[x])
    ranks = [0] * len(indices)
    for i, x in enumerate(indices):
        ranks[x] = len(teamlist)-i
		
    return ranks
	
def get_rank_correlation(scores1,scores2,teamlist):

    # make sure to sort by teamlist to have the same order
    vlist1 = np.zeros((len(teamlist),))
    vlist2 = np.zeros((len(teamlist),))
	
    i=0
    for team in teamlist:

        vlist1[i] = scores1[team]
        vlist2[i] = scores2[team]
        i=i+1
	
    res = stats.spearmanr(vlist1,vlist2)


    return res.correlation
	
def get_all_rank_correlations(taskscores1,summedscores1,taskscores2,summedscores2,teamlist,prefix):

    correl = {}
	
    correl[prefix+'_all'] = get_rank_correlation(summedscores1,summedscores2, teamlist)
	
    for task in taskscores1.keys():	
        correl[prefix+'_'+task] = get_rank_correlation(taskscores1[task],taskscores2[task], teamlist)

    return correl
	
	
# MAIN
# --------

# load data
subm22, score22 = read_data(filenames['2022'][0],filenames['2022'][1])
subm23, score23 = read_data(filenames['2023'][0],filenames['2023'][1])

# rescore

rescore22_22 = AVS_scorer(subm22)
rescore22_23 = AVS2_scorer(subm22)

rescore23_22 = AVS_scorer(subm23)
rescore23_23 = AVS2_scorer(subm23)

# compare loaded scores and rescorded data for 2023
d23_23,m23_23 = compare_scores(score23,rescore23_23)

#get overall scores
summed22_22 = sum_per_team(rescore22_22)
summed22_23 = sum_per_team(rescore22_23)

summed23_22 = sum_per_team(rescore23_22)
summed23_23 = sum_per_team(rescore23_23)

# get ranks

ranks_vbs22 = {}
ranks_vbs23 = {}

ranks_vbs22['vbs22_all_AVS'] = get_ranks(summed22_22, summed22_22.keys())
ranks_vbs22['vbs22_all_AVS2'] = get_ranks(summed22_23, summed22_22.keys())

ranks_vbs23['vbs23_all_AVS'] = get_ranks(summed23_22, summed23_23.keys())
ranks_vbs23['vbs23_all_AVS2'] = get_ranks(summed23_23, summed23_23.keys())

for task in rescore22_22:
    ranks_vbs22[task+'_AVS'] = get_ranks(rescore22_22[task], summed22_22.keys()) 
    ranks_vbs22[task+'_AVS2'] = get_ranks(rescore22_23[task], summed22_22.keys()) 

for task in rescore23_23:
    ranks_vbs23[task+'_AVS'] = get_ranks(rescore23_22[task], summed23_23.keys()) 
    ranks_vbs23[task+'_AVS2'] = get_ranks(rescore23_23[task], summed23_23.keys()) 
		
df_vbs22 = pd.DataFrame.from_dict(ranks_vbs22, orient='index', columns = summed22_22.keys())
df_vbs22.to_csv('results/ranks_vbs22.csv')

df_vbs23 = pd.DataFrame.from_dict(ranks_vbs23, orient='index', columns = summed23_23.keys())
df_vbs23.to_csv('results/ranks_vbs23.csv')

# get rank correlation coefficients
correl = get_all_rank_correlations(rescore22_22,summed22_22,rescore22_23,summed22_23,summed22_22.keys(),'vbs22')
correl23 = get_all_rank_correlations(rescore23_22,summed23_22,rescore23_23,summed23_23,summed23_23.keys(),'vbs23')
correl.update(correl23)

df_correl = pd.DataFrame.from_dict(correl, orient='index')
df_correl.to_csv('results/correl.csv')