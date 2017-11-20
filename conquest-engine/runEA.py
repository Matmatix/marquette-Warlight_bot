import random

from deap import base
from deap import creator
from deap import tools

popsize = 0
chromLength = 0
numGen = 0
probCross = 0.0
probMut = 0.0
outputFile = "nothing"

def pullVals(file):
    with open(str(file)) as f:
        global popsize, chromLength, numGen, probCross
        global probMut, outputFile
        content = f.read().splitlines()
        popsize = int(content[0])
        chromLength = int(content[1])
        numGen = int(content[2])
        probCross = float(content[3])
        probMut = float(content[4])
        outputFile = content[5]


pullVals('params.txt')
print("Population Size: %d\r\nChromosome Length: %d\r\nNumber of Generations to run: %d\r\nProbability of Crossover: %f\r\nProbability of Mutation: %f\r\nOutput File: %s\r\n" % (popsize, chromLength, numGen, probCross, probMut, outputFile))
