
from distutils.fancy_getopt import OptionDummy
from glob import glob
from pickle import TRUE
from platform import node
from random import randint
import json
import pickle

def generate(IDList):

    newlist = []

    for i in range(0, len(IDList)):
        list = IDList[i]
        adjList = []
        for j in range(0, len(list)):
            item = IDList[i][j]

            if j==0 or item == "None":
                adjList.append(item)
            else:
                k = 1
                found = False
                while not found and k < len(IDList):
                    if item == IDList[k][0]:
                        # internal node
                        # assign values based on position in graph
                        # distribution with mean 0 and sd=2^(i-1)
                        if item in [22, 1, 11]: # first layer
                            sd = 2**(1-1)
                        elif item in [23, 2, 12]: # second layer
                            sd = 2**(2-1)
                        elif item in [28, 3, 13]: # third layer
                            sd = 2**(3-1)
                        elif item in [29, 26, 4, 33, 14, 18]: # fourth layer
                            sd = 2**(4-1)
                        adjList.append([item,randint(0-sd,0+sd)])
                        found = True
                    k+=1
                if not found:
                    # leaf node
                    sd = 2**5
                    adjList.append([item,randint(0-sd,0+sd)])
        newlist.append(adjList)
    
    return newlist   
    
def main():
    graph = [
        [0, 22, 1, 11],
        [22, 23],
        [23, 28],
        [28, "None", 26, "None", 29],
        [26, 27, 25, 24],
        [29, 30, "None", 31, 32],
        [1, "None", 2],
        [2, "None", 3],
        [3, 4, "None", 33],
        [4, 5, 6, "None", 7],
        [33, "None", 10, 9, 8],
        [11, "None", "None", 12],
        [12, "None", "None", 13],
        [13, "None", 14, "None", 18],
        [14, 15, 16, 17],
        [18, 19, "None", 21, 20]
        ]

    gGraph = generate(graph)
    print(gGraph)

main()


