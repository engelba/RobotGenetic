import genetic as gen
import os

# PARTIE 1 : Variation de la taille de la population


def taille_pop():
    nbr_individus_tab = [10, 20, 50, 70, 100, 200, 500, 700, 1000]
    mutation_factor = 0.05
    portion_duration = 2
    nbr_portions = 10
    type_simu = 1
    accepted_radius = 0.05
    for i, nbr_individus in enumerate(nbr_individus_tab):
        generation = gen.Generation(nbr_individus, mutation_factor,
                                    portion_duration=portion_duration,
                                    nbr_portions=nbr_portions,
                                    accepted_radius=accepted_radius)
        generation.simulation(type_simu=type_simu, simulation_counter=i, tolerated_ind_percentage=10)

# PARTIE 2 : Variation du pourcentage d'erreur


def radius():
    radius_tab = [1e-3, 5e-3, 1e-2, 5e-2, 1e-1, 5e-1, 1]
    nbr_individus = 100
    mutation_factor = 0.005
    portion_duration = 2
    nbr_portions = 10
    type_simu = 1

    for i, accepted_radius in enumerate(radius_tab):
        generation = gen.Generation(nbr_individus, mutation_factor,
                                    portion_duration=portion_duration,
                                    nbr_portions=nbr_portions,
                                    accepted_radius=accepted_radius)
        generation.simulation(type_simu=type_simu, simulation_counter=i, tolerated_ind_percentage=10)

# PARTIE 3 : Variation du facteur de mutation


def mutation_factor():
    # mutation_factor_tab = [0.001, 0.003, 0.005, 0.007, 0.01, 0.03, 0.05, 0.07]
    mutation_factor_tab = [0.01, 0.03, 0.05, 0.07]

    nbr_individus = 100
    portion_duration = 2
    nbr_portions = 10
    type_simu = 1
    accepted_radius = 0.003

    for i, mutation_factor in enumerate(mutation_factor_tab):
        generation = gen.Generation(nbr_individus, mutation_factor,
                                    portion_duration=portion_duration,
                                    nbr_portions=nbr_portions,
                                    accepted_radius=accepted_radius)
        generation.simulation(type_simu=type_simu, simulation_counter=i, tolerated_ind_percentage=10)

# PARTIE 4 : Variation du nombre de portions


def nbr_portions():
    nbr_portions_tab = [2, 5, 10, 15, 20]
    nbr_individus = 100
    mutation_factor = 0.01
    portion_duration = 2
    type_simu = 1
    # defaut_radius = 0.01 #pour 2 portions
    # accepted_radius = [defaut_radius]
    # for nbr_portions in nbr_portions_tab: #adapte la précision au point choisi
    #     accepted_radius.append(nbr_portions*defaut_radius/2) #règle de 3
    accepted_radius = 0.001


    for i, nbr_portions in enumerate(nbr_portions_tab):
        generation = gen.Generation(nbr_individus, mutation_factor,
                                    portion_duration=portion_duration,
                                    nbr_portions=nbr_portions,
                                    accepted_radius=accepted_radius)
        generation.simulation(type_simu=type_simu, simulation_counter=i, tolerated_ind_percentage=10)

# main


if __name__ == '__main__':
    print("1 :\tVariation de la taille de la population")
    print("2 :\tVariation du pourcentage d'erreur")
    print("3 :\tVariation du facteur de mutation")
    print("4 :\tVariation du nombre de portions")
    critere_choisi = input("Quelle partie du script exécuter ? ")

    if int(critere_choisi) == 1:
        taille_pop()
        print("Simulation terminée.")
    elif int(critere_choisi) == 2:
        radius()
        print("Simulation terminée.")
    elif int(critere_choisi) == 3:
        mutation_factor()
        print("Simulation terminée.")
    elif int(critere_choisi) == 4:
        nbr_portions()
        print("Simulation terminée.")
    else:
        print("Veuillez choisir un entier entre 1 et 4.")
