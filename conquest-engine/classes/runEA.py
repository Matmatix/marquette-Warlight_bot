# Authors: Matthew Kinzler, Ryan Clulo, Jason Wallenfang
# Date: 12/4/17
# This Python script uses the Distributed Evolutionary Algorithms in Python (DEAP) library to run a Genetic Algorithm
# on the different bot configurations using the conquest engine as the evaluation.
import random
import os
import numpy

from deap import base
from deap import creator
from deap import tools

# These are the default values for the EA parameters
popsize = 0
chromLength = 0
numGen = 0
probCross = 0.0
probMut = 0.0
outputFile = "nothing"

# These are the default values for the attack probability and division of troops for attackers and defenders.
attackProb = 1.2
divisor = 2.0

# This function pulls the parameter values from a text file.
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


# This function handles the evaluation of an individual.
# It takes the output and uses the number of rounds as the fitness.
def evaluate(individual):
    attackProb = individual[0]
    divisor = individual[1]
    print("Running with:\n--- Attack Probability: %.3f\n--- Troop Balance: %.3f" % (attackProb, divisor))
    os.system('java main.RunGame 0 0 0 "python ../../bot.py %f %f" "python ../../bot.py 1.2 2"  2>err.txt 1>out.txt' % (attackProb, divisor))
    os.system('grep rounds out.txt > fitness.txt')
    with open("fitness.txt") as g:
        content = g.read().split()
        try:
            print("%s: %d rounds" % (content[0], int(content[3])))
            if content[0] == "player1":
                return(int(content[3]))
            else:
                return(1/(int(content[3]))*10000)
        except IndexError:
            print("Tie: 100 rounds")

# Runs the Genetic Algorithm for a certain number of generations defined by the passed argument.
def startGA(num_gen):
    for g in range(num_gen):
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = map(toolbox.clone, offspring)

        # Apply crossover on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < probCross:
                tools.cxBlend(child1, child2, 0.5)
                del child1.fitness.values
                del child2.fitness.values

        # Apply mutation on the offspring
        for mutant in offspring:
            if random.random() < probMut:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        try:
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
        except TypeError:
            print("-----------------")

        # The population is entirely replaced by the offspring
        pop[:] = offspring


def main():
    global toolbox, pop
    pullVals('params.txt')

    IND_SIZE = 2

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("attr_float", random.uniform, 1.01, 2)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=IND_SIZE)

    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=5)

    #Stats
    stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)


    #print("Population Size: %d\r\nChromosome Length: %d\r\nNumber of Generations to run: %d\r\nProbability of Crossover: %f\r\nProbability of Mutation: %f\r\nOutput File: %s\r\n" % (popsize, chromLength, numGen, probCross, probMut, outputFile))
    startGA(20)

    print(pop)

if __name__ == "__main__":
    main()
