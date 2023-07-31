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
	
def countQuantized(corr):

        # return submissions.filterIsInstance<ItemAspect>().groupBy { it.item }.map {
            # when(it.key) {
                # is MediaItem.ImageItem -> 1
                # is MediaItem.VideoItem -> {
                    # val ranges = it.value.map { s -> (s as Submission.Temporal).temporalRange }
                    # TimeUtil.merge(ranges, overlap = 1).size
                # }
            # }
        # }.sum()

    return 0


def AVS_scorer(subm):


    scores = {}
    for task in subm['task'].unique():
        scores[task] = {}

        correctSubmissions = subm.loc[subm['status']=='CORRECT' and subm['task']==task]
        wrongSubmissions = subm.loc[subm['status']=='WRONG' and subm['task']==task]
	
        totalCorrectQuantized = double(countQuantized(correctSubmissions))

        for team in subm['team'].unique():
            scores[team] = 0.0


            correctSubs = correctSubmissions.loc[correctSubmissions['team'==team]]
            correct = len(correctSubs)
        
            wrongSubs = wrongSubmissions.loc[wrongSubmissions['team'==team]]
            wrong = len(wrongSubs)
		
            scores[task][team] = 100.0 * (correct / (correct + wrong / 2.0)) * (double(countQuantized(correctSubs)) / totalCorrectQuantized)
      	
    return {}

def AVS2_scorer(subm):


    # constructor(parameters: Map<String, String>) : this(
        # abs(
            # parameters.getOrDefault("penalty", "$defaultPenalty").toDoubleOrNull() ?: defaultPenalty
        # ),
        # parameters.getOrDefault("maxPointsPerTask", "$defaultMaxPointsPerTask").toDoubleOrNull()
            # ?: defaultMaxPointsPerTask
    # )

    # constructor() : this(defaultPenalty, defaultMaxPointsPerTask)

    # companion object {
        # const val defaultPenalty: Double = 0.2
        # private const val defaultMaxPointsPerTask: Double = 1000.0

        # /**
         # * Sanitised team scores: Either the team has score 0.0 (no submission) or the calculated score
         # */
        # fun teamScoreMapSanitised(scores: Map<TeamId, Double>, teamIds: Collection<TeamId>): Map<TeamId, Double> {

            # val cleanMap = teamIds.associateWith { 0.0 }.toMutableMap()

            # scores.forEach { (teamId, score) ->
                # cleanMap[teamId] = max(0.0, score)
            # }

            # return cleanMap
        # }

    # }

    # override fun computeScores(
        # submissions: Collection<Submission>,
        # context: TaskContext
    # ): Map<TeamId, Double> {

        # val distinctCorrectVideos =
            # submissions.mapNotNullTo(mutableSetOf()) {//map directly to set and filter in one step
                # if (it !is ItemAspect || it.status != SubmissionStatus.CORRECT) {
                    # null//filter all incorrect submissions
                # } else {
                    # it.item.id
                # }
            # }.size

        # //no correct submissions yet
        # if (distinctCorrectVideos == 0) {
            # lastScores = this.lastScoresLock.write {
                # teamScoreMapSanitised(mapOf(), context.teamIds)
            # }
            # this.lastScoresLock.read {
                # return lastScores
            # }
        # }

        # lastScores = this.lastScoresLock.write {
            # teamScoreMapSanitised(
                # submissions.filter {
                    # it is ItemAspect &&
                            # (it.status == SubmissionStatus.CORRECT || it.status == SubmissionStatus.WRONG)
                # }.groupBy { it.teamId }
                    # .map { submissionsPerTeam ->
                        # submissionsPerTeam.key to
                                # max(0.0, //prevent negative total scores
                                    # submissionsPerTeam.value.groupBy { submission ->
                                        # submission as ItemAspect
                                        # submission.item.id
                                    # }.map {
                                        # val firstCorrectIdx = it.value.sortedBy { s -> s.timestamp }
                                            # .indexOfFirst { s -> s.status == SubmissionStatus.CORRECT }
                                        # if (firstCorrectIdx < 0) { //no correct submissions, only penalty
                                            # it.value.size * -penaltyConstant
                                        # } else { //apply penalty for everything before correct submission
                                            # 1.0 - firstCorrectIdx * penaltyConstant
                                        # }
                                    # }.sum() / distinctCorrectVideos * maxPointsPerTask //normalize
                                # )
                    # }.toMap(), context.teamIds
            # )
        # }
        # this.lastScoresLock.read {
            # return lastScores
        # }
    # }


   return {}

	
	
# main
subm23, score23 = read_data(filenames['2023'][0],filenames['2023'][1])

print(score23)

	
	
	
