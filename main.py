#!/usr/bin/env python3

"""
|=================================================|
| Script qui fait concretement bouger la voiture. |
|=================================================|
"""

import genetic

generation = genetic.Generation(
	nbr_individuals=5,
	mutation_factor=0.05,
	portion_duration=1,
	nbr_portions=10)

generation.simulation(nature="real", nbr_generations=5)
