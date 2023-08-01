import pandas as pd
import numpy as np
import json

import plotly.express as px


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
		
    pairs = ranges
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
            continue
        i = i+1
    merged.append(current)
		
    return merged
	
def countQuantized(corr):

    cnt = 0

    ranges = []	

    for index, row in corr.iterrows():
	
        r = [int(row['start']),int(row['ending'])]
        ranges.append(r)
    
	
    return len(merge_ranges(ranges,1))
	


def AVS_scorer(subm):

    scores = {}
    for task in subm['task'].unique():
        scores[task] = {}

        correctSubmissions = subm.loc[np.logical_and(subm['status']=='CORRECT', subm['task']==task)]
        wrongSubmissions = subm.loc[np.logical_and(subm['status']=='WRONG' , subm['task']==task)]
	
        totalCorrectQuantized = float(countQuantized(correctSubmissions))

        for team in subm['team'].unique():
            scores[team] = 0.0


            correctSubs = correctSubmissions.loc[correctSubmissions['team'==team]]
            correct = len(correctSubs)
        
            wrongSubs = wrongSubmissions.loc[wrongSubmissions['team'==team]]
            wrong = len(wrongSubs)
		
            scores[task][team] = 100.0 * (correct / (correct + wrong / 2.0)) * (float(countQuantized(correctSubs)) / totalCorrectQuantized)
      	
    return scores

def AVS2_scorer(subm):

    defaultPenalty = 0.2
    defaultMaxPointsPerTask = 1000.0

    scores = {}
    for task in subm['task'].unique():
        scores[task] = {}
	
        correctSubmissions = subm.loc[np.logical_and(subm['status']=='CORRECT' , subm['task']==task)]
        wrongSubmissions = subm.loc[np.logical_and(subm['status']=='WRONG' , subm['task']==task)]

        distinctCorrectVideos = len( correctSubmissions['item'].unique())  	

		
        for team in subm['team'].unique():
            scores[team] = 0.0

            subm_task_team = subm.loc[np.logical_and(subm['task']==task , subm['team']==team)]
			 
            for video in subm_task_team['item'].unique():
			
                subm_task_team_vid = subm.loc[subm_task_team['item']==video]
			
                subm_task_team_srt = subm_task_team_vid.sort_values(['time'])
                subm_task_team_srt = subm_task_team_srt.reset_index(drop=True)

                sc = 0	
			
                if len(subm_task_team_srt[subm['status']=='CORRECT'])==0:
                   sc = len(subm_task_team_srt) * -penaltyConstant
                else:
                    firstCorrectIdx = subm_task_team_srt[subm['status']=='CORRECT'].iloc[0]
                    sc = 1.0 - firstCorrectIdx * penaltyConstant
	
                scores[team] = scores[team] + max(0,sc) 
				
            scores[team] = score[team] / distinctCorrectVideos * maxPointsPerTask 

    return scores

	
	
# main
subm23, score23 = read_data(filenames['2023'][0],filenames['2023'][1])

rescore23_22 = AVS_scorer(subm23)

rescore23_22 = AVS_scorer(subm23)



	
	
	
