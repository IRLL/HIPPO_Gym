# can generate any number of trials
import json
from random import randint
def main():
    numTrials = 0 # also the id of the trial
    allTrials = {}

    firstLargeGraph = [[0, [22, 1], [1, -1], [11, 1]], [22, [23, -1]], [23, [28, 0]], [28, 'None', [26, -1], 'None', [29, -3]], [26, [27, -8], [25, -18], [24, -20]], [29, [30, 12], 'None', [31, 6], [32, 9]], [1, 'None', [2, 1]], [2, 'None', [3, -2]], [3, [4, -4], 'None', [33, -3]], [4, [5, 32], [6, 32], 'None', [7, -17]], [33, 'None', [10, 27], [9, -31], [8, -25]], [11, 'None', 'None', [12, 1]], [12, 'None', 'None', [13, -2]], [13, 'None', [14, 8], 'None', [18, 4]], [14, [15, 4], [16, 19], [17, 24]], [18, [19, 2], 'None', [21, -19], [20, 30]]]
    secondLargeGraph = [[0, [22, 1], [1, 0], [11, 1]], [22, [23, -2]], [23, [28, 3]], [28, 'None', [26, -4], 'None', [29, 5]], [26, [27, 22], [25, 15], [24, 3]], [29, [30, -27], 'None', [31, -12], [32, -32]], [1, 'None', [2, -1]], [2, 'None', [3, 2]], [3, [4, 8], 'None', [33, -3]], [4, [5, 29], [6, -12], 'None', [7, -11]], [33, 'None', [10, 10], [9, -22], [8, 5]], [11, 'None', 'None', [12, -1]], [12, 'None', 'None', [13, -1]], [13, 'None', [14, 8], 'None', [18, -1]], [14, [15, -27], [16, -32], [17, 28]], [18, [19, -29], 'None', [21, 2], [20, 19]]]
    
    with open('increasing_prs.json') as json_file:
        data = json.load(json_file)
    
    for j in range(5):
        listOfSelectedGraphs = []
        numSelGraphs = 0
        while numSelGraphs != 31:
            rGraph = randint(0, 59)
            while data[rGraph]['trial_id'] in listOfSelectedGraphs:
                rGraph = randint(0, 59)
            
            listOfSelectedGraphs.append(data[rGraph]['trial_id'])
            numSelGraphs +=1

        completeTrial = {1: firstLargeGraph, 33:secondLargeGraph}
        gID = 2
        for item in listOfSelectedGraphs:
            completeTrial[gID] = item
            gID +=1
        
        allTrials[numTrials] = completeTrial
        numTrials +=1
    # outfile trial
    with open('trials.json', 'w') as trials:
        json.dump(allTrials, trials)
main()