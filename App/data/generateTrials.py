
import json
from random import randint
def main():
    numTrials = 0 # also the id of the trial
    allTrials = {}

    firstLargeGraph = [[0, [22, 0], [1, 1], [11, -1]], [22, [23, 1]], [23, [28, -3]], [28, 'None', [26, -22], 'None', [29, 5]], [29, [30, 13], 'None', [31, 13], [32, 17]], [1, 'None', [2, 1]], [2, 'None', [3, 3]], [3, [4, 4], 'None', [33, 3]], [4, [5, 4], [6, 23], 'None', [7, -20]], [33, 'None', [10, 0], [9, -4], [8, -6]], [11, 'None', 'None', [12, 2]], [12, 'None', 'None', [13, 1]], [13, 'None', [14, -2], 'None', [18, 0]], [14, [15, 26], [16, 6], [17, 19]], [18, [19, -21], 'None', [21, -26], [20, 5]]]
    secondLargeGraph = [[0, [22, 1], [1, 1], [11, -1]], [22, [23, 1]], [23, [28, -2]], [28, 'None', [26, 6], 'None', [29, -4]], [29, [30, 13], 'None', [31, -24], [32, -30]], [1, 'None', [2, 1]], [2, 'None', [3, -3]], [3, [4, -4], 'None', [33, -8]], [4, [5, 14], [6, -22], 'None', [7, 22]], [33, 'None', [10, 20], [9, 18], [8, -10]], [11, 'None', 'None', [12, -1]], [12, 'None', 'None', [13, 1]], [13, 'None', [14, -8], 'None', [18, 1]], [14, [15, 11], [16, -27], [17, -1]], [18, [19, 17], 'None', [21, 11], [20, -21]]]
    
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