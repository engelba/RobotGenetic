#!/usr/bin/env python3

"""
|======================================|
| Gene and Individual reprensentation. |
|======================================|
"""

import inspect
import random
import time
import csv
import os

import matplotlib.pyplot as plt
import numpy as np

class Gene:
    """
    A gene is a sequence of moves.
    """
    def __init__(self, portion_duration, nbr_portions, *, nbr_outputs=4, fct=lambda x: x):
        """
        Parameters
        ----------
        :param portion_duration: Duration of a gene portion.
        :type portion_duration: float, int
        :param nbr_portions: Number of gene portions in a gene.
        :type nbr_sections: int
        :param nbr_outputs: Number of outputs.
        :type nbr_outputs: int
        :param fct: Bias function.
        :type fct: callable
        """
        assert isinstance(portion_duration, (int, float)), \
            "'portion_duration' must be of type float. Not %s." \
            % type(portion_duration).__name__
        assert portion_duration > 0, \
            "A duration must be positive. %f is not positive." \
            % portion_duration
        assert isinstance(nbr_portions, int), \
            "'nbr_portions' must be of type int. Not %s." \
            % type(nbr_portions).__name__
        assert nbr_portions > 0, "There must be at least 1 portion."
        assert isinstance(nbr_outputs, int), \
            "'nbr_outputs' must be of type int. Not %s." \
            % type(nbr_outputs).__name__
        assert nbr_outputs > 0, \
            "Number of outputs must be positive."
        assert hasattr(fct, "__call__"), "'fct' must be callable."
        assert all(a.kind == inspect.Parameter.POSITIONAL_ONLY
            or a.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            for a in inspect.signature(fct).parameters.values()), \
            "'fct' args must be simple, recognizable and accountable."

        self.portion_duration = portion_duration
        self.nbr_portions = nbr_portions
        self.nbr_outputs = nbr_outputs
        self.fct = fct

        self.nbr_parameters = len(inspect.signature(fct).parameters)
        self.bias = np.random.uniform(-1, 1,
            size=(self.nbr_portions, nbr_outputs, self.nbr_parameters))
        self.weight = 1.0 # La notoriete du gene.

    def copy(self):
        """
        |================|
        | Copies a gene. |
        |================|

        Returns
        -------
        :return: New gene, a copy of the current one.
        :rtype: Gene
        """
        def init(self, **kwargs):
            """Initialization."""
            for k, v in kwargs.items():
                setattr(self, k, v)

        return type(type(self).__name__, (type(self),), {"__init__": init})(**self.__dict__)

    def __add__(self, other):
        """
        |======================|
        | Conbines both genes. |
        |======================|

        Parameters
        ----------
        :param other: The other gene.
        :type other: Gene

        Returns
        -------
        :return: New version of the gene derived from the combination of self gene and other gene.
        :rtype: Gene
        :raise ValueError: If not homogene.
        """
        if not isinstance(other, Gene):
            return NotImplemented
        if self.portion_duration != other.portion_duration:
            raise ValueError("The genes must have the same portion_duration.")
        if self.bias.shape != other.bias.shape:
            raise ValueError("The genes must have the same dimension.")

        new_gene = self.copy()
        new_gene.bias = (self.weight*self.bias + other.weight*other.bias) \
                        / (self.weight + other.weight)
        return new_gene

    def __mul__(self, number):
        """
        |=============================|
        | Assigns a weight to a gene. |
        |    '0.2*gen1 + 0.8*gen2'    |
        |=============================|

        Parameters
        ----------
        :param number: Weight.
        :type number: float

        Returns
        -------
        :return: Copy of the current gene with the entered weight assigned to the gene.
        :rtype: Gene
        """
        if not isinstance(number, (int, float)):
            return NotImplemented
        new_gene = self.copy()
        new_gene.weight *= number
        return new_gene

    def __rmul__(self, number):
        """
        :seealso: self.__mul__
        """
        return number * self

    def __call__(self, instant):
        """
        |=================================================|
        | Evaluates the sequence at a particular instant. |
        |=================================================|

        Parameters
        ----------
        :param instant: Temporal continuous instant when the function is evaluated.
        :type instant: float

        Returns
        -------
        :return: Values of the gene at this instant.
        :rtype: list
        :raises ValueError: Entered instant does not belong to the given sequence.
        """
        assert isinstance(instant, (float, int)), \
            "'instant' must be a number. Not a %s." \
            % type(instant).__name__
        if instant < 0 or self.nbr_portions * self.portion_duration <= instant:
            raise ValueError("Entered instant does not belong to the definition interval.")

        rang = int(instant / self.portion_duration)
        return [self.fct(*self.bias[rang, s]) for s in range(self.nbr_outputs)]

    def mute(self, factor):
        """
        |====================|
        | Creates mutations. |
        |====================|

        Parameters
        ----------
        :param factor: Mutations factor.
            1 -> everything mutates.
            0 -> nothing mutates.
        :type factor: float

        Returns
        -------
        :return: New version of the gene that includes the mutations.
        :rtype: Gene
        """
        assert isinstance(factor, (float, int)), \
            "'factor' has to be a number. Not a %s." \
            % type(factor).__name__
        assert 0 <= factor <= 1, "The factor must be between 0 and 1."

        new_gene = self.copy()
        mutation_tensor = np.random.uniform(0, 1, size=new_gene.bias.shape) < factor
        new_gene.bias += mutation_tensor * np.random.normal(0, 1, size=new_gene.bias.shape)
        new_gene.bias = np.where( 1<new_gene.bias, 1, new_gene.bias)
        new_gene.bias = np.where( 0>new_gene.bias, 0, new_gene.bias)
        # new_gene.bias = np.where(max(0, min(1, new_gene.bias)))
        return new_gene

class Individual(Gene):
    """
    An individual is a behavior of the population,
    which is a sequence of nbr_portions moves of nbr_outputs wheels.
    """
    def __init__(self, *args, **kwargs):
        Gene.__init__(self, *args, **kwargs)
        self.score = None # Resultat donne par le traitement d'image.
        # self.orientation = 0
        # self.position = None # Mettre le centre de l'image
        # self.arriveeX, self.arriveeY = coord_arrivee

    def move_car(self):
        """
        Operates the car.

        Returns
        -------
        :return: les liste des points x, y qui representent les positions de la voiture.
        :rtype: (list, list)
        """
        import interface
        self.reset_position()
        print("move car during %f s..." % self.portion_duration*self.nbr_portions)

        X, Y = [], []
        t_debut = time.time()
        while time.time() - t_debut < self.portion_duration*self.nbr_portions:
            current_time = time.time() - t_debut
            # On fait bouger les 4 roues.
            for numero_roue, speed in enumerate(self(current_time)):
                print(numero_roue)
                interface.move_wheel(numero_roue+1, speed)

            # Recuperation de la position reele
            (x, y), _ = interface.get_position()
            X.append(x)
            Y.append(y)

        interface.move_wheel("", 0) # La voiture s'arette a la fin.
        print("\tterminate")
        return x, y

    def move_simulation(self):
        """
        Operates the simulation of the car.

        Returns
        -------
        :return: les liste des points x, y qui representent les positions de la voiture.
        :rtype: (list, list)
        """
        import simulation

        dt = 1e-3 # Pas de temps en seconde.
        x, y = [], []
        state = simulation.State() # On positione la voiture a l'origine
        for i, t in enumerate(np.arange(0, self.portion_duration*self.nbr_portions, dt)):
            state.update(*self(t), dt=dt)
            if not i % 1000:
                x.append(state.x)
                y.append(state.y)

        # self.score = x[-1]**2 + y[-1]**2 # Bidon et mal fait, c'est juste pour le test.
        # self.score = y[-1]-abs(x[-1])
        # self.score = 1 / ( (self.arriveeX*self.nbr_portions/10.0-x[-1])**2 + (self.arriveeY*self.nbr_portions/10.0-y[-1])**2 ) # Tout droit jusqu'au point choisi
        self.score = 1 / ( (self.arriveeX*self.nbr_portions*4.0/20-x[-1])**2 +
                    (self.arriveeY*self.nbr_portions*4.0/20-y[-1])**2 ) # Le point choisi dépend du point standard (0.1) et de nbr_portions

        return x, y

    def reset_position(self):
        """
        |=============================================|
        | Fait revenir l'individu au point de depart. |
        |=============================================|
        """
        import interface

        print("Start restet position...")

        sign = lambda x: int(x > 0) - int(x < 0) # Renvoi le signe de x (-1, 0, 1).
        fact_speed = 0.7 # On divise les vitesses.

        eps_angle = np.pi*20/180 # Tolerance angulaire. (en radian)
        eps_pos = 50 # Tolerance sur le carre centre autour du point d'arrive (en pxl).
        x0, y0 = 320, 230 # Point a atteindre.(en pxl)

        self.position, self.orientation = interface.get_position()

        # Calcul de l'angle entre barycentre de la voiture et point de depart.
        def get_alpha():
            """
            Recupere l'angle entre l'axe horizontal et le vecteur position de la voiture.
            """
            norm = np.sqrt((self.position[1] - y0)**2 + (self.position[0] - x0)**2)
            if norm:
                return np.arccos((self.position[0] - x0)/norm) * (1 - 2*(self.position[1] > y0))
            return 0

        control_angle = lambda a: (a+np.pi)%(2*np.pi) - np.pi

        # alpha : orientation souhaitee de la voiture pour retourner au point de depart (comprise entre -pi et +pi)

        # As long as we are not in the direction of the center, the car rotates on itself
        print("angle de la voiture en degre:", self.orientation*180/np.pi)
        print("angle qui reste a faire:", control_angle(np.pi - get_alpha() + self.orientation))
        print("\tOrientation vers la cible....")
        fact_bis = fact_speed
        while abs(control_angle(np.pi - get_alpha() + self.orientation)) > eps_angle:
        # while True:
            fact_bis *= 1.01
            # interface.move_wheel("l", -0.4)
            # interface.move_wheel("r", 0.4)
            interface.move_wheel("l", -fact_bis*control_angle(np.pi + get_alpha() - self.orientation)/np.pi)
            interface.move_wheel("r",  fact_bis*control_angle(np.pi + get_alpha() - self.orientation)/np.pi)
            self.position, self.orientation = interface.get_position()
            print("Orientation: ", control_angle(np.pi - get_alpha() + self.orientation),
                 "position actuelle: ", self.position, self.orientation)
            # print("fact speed : ", fact_bis)
        # As long as we are not at the center, the car goes straight
        interface.move_wheel("", 0)

        input("suite")

        print("\tavancer vers la cible")
        while abs(x0 - self.position[0]) > eps_pos or abs(y0 - self.position[1]) > eps_pos:
            # print(abs(x0 - self.position[0]), abs(y0 - self.position[1]))
            print("Avancer vers la cible - distance", 0.5*(np.sqrt((self.position[1] - y0)**2 + (self.position[0] - x0)**2) / norm))
            interface.move_wheel("", (0.5*(np.sqrt((self.position[1] - y0)**2 + (self.position[0] - x0)**2) / norm)))
            self.position, self.orientation = interface.get_position()
            print("Avancer vers la cible - position : ", self.position, self.orientation)

        # As long as the the car is not facing the chosen direction, it rotates on itself
        interface.move_wheel("", 0)
        print("\torientation finale")
        while abs(np.pi/2 - self.orientation) > eps_angle:
            print("Orientation finale - Angle : ", abs(np.pi/2 - self.orientation))
            interface.move_wheel("l", -fact_speed*(0.5+0.5*(abs(abs(self.orientation)-np.pi/2))/np.pi))
            interface.move_wheel("r", fact_speed*(0.5+0.5*(abs(abs(self.orientation)-np.pi/2))/np.pi))
            self.position, self.orientation = interface.get_position()

        interface.move_wheel("", 0)
        print("\tterminated")

    def __lt__(self, other):
        """
        self < other
        """
        assert isinstance(other, Individual), \
            "'other' has must be of type Individual. Not %s." \
            % type(other).__name__

        if self.score is None or other.score is None:
            raise ValueError("Individuals must be tested before comparing them.")

        return self.score < other.score

    def __gt__(self, other):
        """
        self > other
        """
        assert isinstance(other, Individual), \
            "'other' must be of type Individual. Not %s." \
            % type(other).__name__

        if self.score is None or other.score is None:
            raise ValueError("Individuals must be tested before comparing them.")

        return self.score > other.score

    def __eq__(self, other):
        """
        self == other
        """
        assert isinstance(other, Individual), \
            "'other' must be of type Individual. Not %s." \
            % type(other).__name__

        if self.score is None or other.score is None:
            raise ValueError("Individuals must be tested before comparing them.")

        return self.score == other.score

    def __le__(self, other):
        """
        self <= other
        """
        self < other or self == other

    def __ge__(self, other):
        """
        self >= other
        """
        self > other or self == other

class Generation:
    """
    |==================================|
    | Represente un paquet d'individu. |
    |==================================|
    """
    def __init__(self, nbr_individuals, mutation_factor, coord_arrivee=(0,1), accepted_radius=0.1, *args, **kwargs):
        """
        Parameters
        ----------
        :param nbr_individuals: Le nombre de voiture a chaque generation.
        :type nbr_individuals: int
        :param mutation_factor: Facteur de mutation entre 0 et 1.
        :type mutation_factor: float
        :param accepted_raidus : float: rayon de tolérance autour de l'arrivée
        :arg args: Same as Individual.__init__ .
        :key kwargs: Same as Individual.__init__ .
        """
        assert isinstance(nbr_individuals, int), \
            "'nbr_individuals' has to be int, not %s." \
            % type(nbr_individuals).__name__
        assert isinstance(mutation_factor, (float, int)), \
            "'mutation_factor' has to be float, not %s." \
            % type(mutation_factor).__name__
        assert 2 <= nbr_individuals, "Une population doit etre constituee " \
            "de 2 elements au moins."
        assert 0 <= mutation_factor <= 1, "Le facteur de mutation " \
            "doit etre exprime entre 0 et 1."

        self.nbr_individuals = nbr_individuals
        self.mutation_factor = mutation_factor
        self.accepted_radius = accepted_radius
        self.individuals = [Individual(*args, **kwargs)
            for _ in range(self.nbr_individuals)]

    def create_file(self, type_simu=0, simulation_counter=0):
        """
        |===================================|
        | Cree et initialise le fichier csv |
        | qui enregistrera les resultats.   |
        |===================================|
        """
        portion_duration = self.individuals[0].portion_duration
        nbr_portions = self.individuals[0].nbr_portions
        arriveeX = self.individuals[0].arriveeX*nbr_portions*4.0/20
        arriveeY = self.individuals[0].arriveeY*nbr_portions*4.0/20

        if type_simu == 0:
            repertoire = (f"simulation_data/Simu {simulation_counter} : "
            f"type_simu=0, nbr_individuals={self.nbr_individuals}, "
            f"mutation_factor={self.mutation_factor}, portion_duration={portion_duration}, "
            f"nbr_portions={nbr_portions}, arrivee=({arriveeX},{arriveeY})")
        else:
            repertoire = (f"simulation_data/Simu {simulation_counter} : "
            f"type_simu=1, nbr_individuals={self.nbr_individuals}, "
            f"mutation_factor={self.mutation_factor}, portion_duration={portion_duration}, "
            f"nbr_portions={nbr_portions}, accepted_radius={self.accepted_radius}, "
            f"arrivee=({arriveeX},{arriveeY})")

        fname = "data_simu.csv"
         
        try: 
            os.makedirs(repertoire)
        except OSError:
            if not os.path.isdir(repertoire):
                Raise

        with open(repertoire+"/"+fname, "a") as file:
            list_col = ["Génération", 'Individu', 'Score']
            for portion in range(self.individuals[0].nbr_portions):
                for roue in range(4):
                    list_col.append('Gene_' + str(portion) + 'roue_' + str(roue))
            if type_simu == 1:
                list_col.append('individuals_under_threshold')
            writer = csv.writer(file)
            writer.writerow(list_col)

        return repertoire

    def save_score(self, gen_number, ind_number, type_simu, repertoire="", individuals_under_threshold=0):
        """
        |===================|
        | Ajoute une ligne. |
        |===================|

        :param gen_number: Le numero de la generation de la ligne qui va etre completee.
        :param ind_number: Le numero de l'individu de la generation de la ligne.
        """
        fname = "data_simu.csv"
        with open(repertoire+"/"+fname, "a") as file:
            # Création de l'écrivain'' CSV.
            writer = csv.writer(file)

            list_data = [gen_number, ind_number, self.individuals[ind_number].score]

            # for portion in self.individuals[ind_number].Gene.nbr_portions :

            instant = 0
            while instant < self.individuals[0].nbr_portions * self.individuals[0].portion_duration:
                list_wheel = [self.individuals[ind_number](instant)[k] for k in range(4)]
                for i in range(4):
                    list_data.append(list_wheel[i])
                instant += self.individuals[0].portion_duration

            if (type_simu == 1) and (ind_number == self.nbr_individuals-1): 
                #condition1 : on a besoin de individuals_under_threshold puisque la type_simu dépend du rayon maximal autorisé (type_simu = 1)
                #condition2 : on ajoute le individuals_under_threshold de la génération si c'est le dernier individu (de la génération)
                    list_data.append(individuals_under_threshold)


            # Écriture des quelques données.
            writer.writerows([list_data])

    def simulation(self, nature="virtual", type_simu=0, nbr_generations=100, simulation_counter=0, tolerated_ind_percentage=10):
        """
        |=====================================|
        | Simule l'evolution des generations. |
        |=====================================|

        :param nbr_generations: Le nombre d'iterations.
        :param nature: 'virtual' ou 'real', simulation ou test reel.
        :param type_simu : 0 pour choisir le nombre de générations,
                           1 pour continuer à créer des générations tant que
                             tous les ind ne sont pas dans le rayon choisi autour de l'arrivée (accepted_radius)
        """
        assert nature in {"virtual", "real"}

        repertoire = self.create_file(type_simu=type_simu, simulation_counter=simulation_counter)

        # Cas où nbr_generations est fixé
        if (type_simu == 0):

            for gen_number in range(nbr_generations):
                plt.axis("equal")
                plt.title("generation : %d" % gen_number)

                # Excecution des simulations, ou activation de la voiture
                for ind_num, (x, y) in enumerate(
                        ind.move_simulation() if nature == "virtual" else ind.move_car()
                        for ind in self.individuals):
                    plt.plot(x, y)
                    self.save_score(gen_number, ind_num, type_simu, repertoire=repertoire)

                # for i in range(self.nbr_individuals):
                #     self.save_score(gen_number, i)

                # Bebe entre generations.
                weights = [ind.score for ind in self.individuals]
                self.individuals = [
                    (random.choices(self.individuals, weights=weights, k=1)[0]
                     + random.choices(self.individuals, weights=weights, k=1)[0]
                     ).mute(self.mutation_factor)
                    for _ in range(self.nbr_individuals)]

                if gen_number % 10 == 0:
                    plt.savefig(repertoire+"/generation_%02d.png" % gen_number)
                plt.clf()

        # Cas où on continue tant que tous les individus ne sont pas dans le rayon choisi
        elif type_simu == 1:

            gen_number = 0
            individuals_under_threshold = self.nbr_individuals

            while (individuals_under_threshold > (tolerated_ind_percentage*self.nbr_individuals/100)) and (gen_number < 50):
                individuals_under_threshold = self.nbr_individuals
                plt.axis("equal")
                plt.title("generation : %d" % gen_number)

                # Excecution des simulations, ou activation de la voiture
                for ind_num, (x, y) in enumerate(
                        ind.move_simulation() if nature == "virtual" else ind.move_car()
                        for ind in self.individuals):
                    plt.plot(x, y)
                    self.save_score(gen_number, ind_num, 1, repertoire, individuals_under_threshold)
                    #Maj du compteur d'individus sous le seuil de tolérance
                    if ( self.individuals[ind_num].score > (1/self.accepted_radius)):
                        individuals_under_threshold-=1

                # for i in range(self.nbr_individuals):
                #     self.save_score(gen_number, i)

                # Bebe entre generations.
                weights = [ind.score for ind in self.individuals]
                self.individuals = [
                    (random.choices(self.individuals, weights=weights, k=1)[0]
                     + random.choices(self.individuals, weights=weights, k=1)[0]
                     ).mute(self.mutation_factor)
                    for _ in range(self.nbr_individuals)]

                # if gen_number % 10 == 0:
                plt.savefig(repertoire+"/"+"generation_%02d.png" % gen_number)

                plt.clf()
                gen_number+=1


        else:

            print("type_simu doit valoir 0 (nbr_generations fixé) ou 1 (choix de accepted_radius)")

        
