# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 16:09:42 2021

@author: ernes
"""

import random


# Initialisation

GENERATION_MAX = 1000
POPULATION_COUNT = 100
PARAMETERS_COUNT = 2
MAXIMUM_FITNESS = 1

CHANCE_TO_MUTATE = 0.1
PART_OF_POP_TO_KEEP = 0.2
PART_OF_BAD_TO_KEEP = 0.05

NB_POP_TO_KEEP = int(POPULATION_COUNT*PART_OF_POP_TO_KEEP)

choose = lambda x: x[int( random() * len(x) )]


### Fonctions ###

def get_random_individual():
    """Create a new random individual """
    return [ random.random() for _ in range(PARAMETERS_COUNT) ]

def get_random_population():
    """ Create a new population, made of 'POPULATION_COUNT' individual """
    return [ get_random_individual() for _ in range(POPULATION_COUNT) ]

def get_individual_fitness(individual):
    """Compute the fitness of the given individual """
    fitness = 0
    # A COMPLETER
    
    #Si distance avec le point objectif diminue, alors fitness augmente ?
    
    return fitness

def average_population_grade(population):
    """Return the average fitness of the whole population """
    total = 0
    for individual in population :
        total += get_individual_fitness(individual)
    return total/POPULATION_COUNT

def sort_population(population):
    """Return a list of tuple (individual, fitness) sorted from most most graded to less graded"""
    graded_individual =[]
    for individual in population :
        graded_individual.append( (individual, get_individual_fitness(individual)) )
    return graded_individual.sort(key=lambda x: x[1], reverse=True)


def evolve_population(population):
    """Make the given population evolve to the next generation """
    
    
    pop = sort_population(population)
    
    # test de la meilleure solution ?

    #On choisit les parents
    #parents = pop[:NB_POP_TO_KEEP]
    for individual in pop[:NB_POP_TO_KEEP]:
        parents.append(i[0])
    
    #On garde des mauvais
    for individual in pop[NB_POP_TO_KEEP:]:
        if random.random() < PART_OF_BAD_TO_KEEP :
            parents.append(i[0])
            
    
    #On réalise des mutations
    for individual in parents :
        if random.random() < CHANCE_TO_MUTATE :
            indice = int( random.random() * PARAMETERS_COUNT )
            individual[indice] = random.random()
    
    #Create new pop
    size_parents = len(parents)
    size_to_create = POPULATION_COUNT - size_parents
    children = []
    while len(children) < size_to_create:
        parent1 = choose(parents)
        parent2 = choose(parents)
        child = parent1[:(PARAMETERS_COUNT/2)] + parent2[(PARAMETERS_COUNT/2):]
        children.append(child)
        
    return parents
    
    
def main():
    """ Main function """
    
    # Creer une population
    population = get_random_population()
    average_grade = average_population_grade(population)
    print(population)
    print(average_grade)
    
    # Iterations
    i = 0
    """
    while i < GENERATION_MAX :
        population = evolve_population(population)
        #Ajouter un affichage toutes les x iterations pour voir l'evolution ?
        i+=1
    """

main()