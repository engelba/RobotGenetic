# RobotGenetic
Répertoire du projet Robot Génétique, réalisé en équipe dans le cadre des projets de deuxième année de SICOM à Phelma - Grenoble INP  

@authors :  
Ernest Bayle  
Violaine Bened  
Baptiste Engel  
Robin Richard  
Marie-Ange Stefanos  

@Tuteur de projet :  
Bertrand Rivet, professeur à Grenoble-INP Phelma  

## Fichiers python
communication.py > Ensemble des objets servant à établir la communication entre un RaspberryPI et un ordinateur en utilisant des sockets TCP, et a piloté la voiture depuis un ordinateur  
detect.py > Ensemble des objets servant à détecter la position de la voiture dans le plan (traitement des images reçues de la caméra)  
genetic.py > Ensemble des objets relatifs à l'algorithme génétique  
interface.py > Fichier permettant à la carte Raspberry de piloter la vitesse de chacun des moteurs à l'aide des pins GPIO  
main.py > Lance l'algorithme d'entrainement (Inclue l'établissement de la communication avec la voiture)  
script_simu.py > Permet de lancer plusieurs simulations les unes à la suite des autres, en faisant varier les paramètres  
simulation.py > Simulation physique de la voiture  
test_algo_gen.py > Fichier de test pour mettre au point l'algorithme génétique  

## Autres
ip_rasp.txt > Fichier créé lors de la première communication entre le Raspberry et l'ordinateur de contrôle, afin de ne pas avoir à scanner l'intégralité du réseau à chaque fois  
plan.pdf > Une plan détaillé de la voiture, servant à réaliser la modélisation  
Rapport.pdf > Le rapport complet du projet  
