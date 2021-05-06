#!/usr/bin/env python3

r"""
|=================================|
| Plan simulation of a model car. |
|=================================|

* All units are SI
* Wheels must form a rectangle
* Every relative value is the car between the floor

 ----                           ----
/    \          front          /    \
| a2 |                         | a1 |
|  . |------------+------------| .  |
|    |            |            |    |
\    /            |            \    /
 ----             |             ----
                  |
                  |
                  |     y
                  |     ^
                  |     |
                  |     |
                g .     -----> x
                  |
                  |
                  |
                  |
                  |
                  |
 ----             |             ----
/    \            |            /    \
| a4 |            |            | a3 |
|  . |------------+------------| .  |
|    |                         |    |
\    /          rear           \    /
 ----                           ----
"""

import math


J = 0.04 # (Kg.m**2) Moment d'inertie au point g projete sur l'axe vertical.
M = 400e-3 + 300e-3 # (Kg) Masse de la voiture.
PHI = 0.4 # (sans unite) Coeficient de frotement entre le caoutchou des roues et le sol.
A1 = (87e-3, 112e-3) # (m, m) Coordonee x y de la roue avant droite.
A2 = (-87e-3, 112e-3) # (m, m) Coordonnees x y de la roue avant gauche.
A3 = (87e-3, -112e-3) # (m, m) Coordonnees x y de la roue arriere droite.
A4 = (-87e-3, -112e-3) # (m, m) Coordonnees x y de la roue arriere gauche.
R = 0.02 # (m) Rayon des roues entre l'axe des roues et le point de contact au sol.
G = (0.0, 0.0) # (m, m) Coordonnees du centre de gravite projeter dans le plan du sol.
coeffAngleSpeed = 18

class State:
    """
    |===========================|
    | Current state of the car. |
    |===========================|

    * The purpose is to go to the next state.
    """
    def __init__(self, vx=0, vy=0, w=0, x=0, y=0, theta=0):
        """
        |=============================================|
        | Initialisation and resolution of equations. |
        |=============================================|

        Parameters
        ----------
        :param vx: Vitesse du centre de gravite de la voiture projetee sur l'axe x.
        :param vy: Vitesse du centre de gravite de la voiture projetee sur l'axe y.
        :param w: Vitesse angulaire de la voiture autoure de l'axe z.
        :param x: Position du centre de gravite de la voiture sur x.
        :param y: Position du centre de gravite de la voiture sur y.
        :param theta: Angle oriente en radian du repere local de la voiture par rapport au referenciel terrestre.
        """
        self.width = A1[0] - A2[0] # Entraxe entre les roues droite / gauche.
        self.length = A1[1] - A3[1] # Entraxe entre les roues avant / arriere.

        # On fait l'hypotèse  que le sol est plat, et que la voiture est parfaite.
        # Malgrè l'hyperstatisme de la voiture, on considère que le poids est bien réparti entre les 4 roues.
        # On suppose aussi que les roues + moto-reducteur n'ont pas d'inertie.
        self.a1_weight = M * (G[1]-A3[1])/self.length * (G[0]-A2[0])/self.width # Poids sur la roue avant droite.
        self.a2_weight = M * (G[1]-A3[1])/self.length * (A1[0]-G[0])/self.width # Poids sur la roue avant gauche.
        self.a3_weight = M * (A1[1]-G[1])/self.length * (G[0]-A2[0])/self.width # Poids sur la roue arriere droite.
        self.a4_weight = M * (A1[1]-G[1])/self.length * (A1[0]-G[0])/self.width # Poids sur la roue arriere gauche.

        # Initialisation de l'état courant de la voiture.
        self.vx, self.vy = vx, vy
        self.w = w
        self.x, self.y = x, y # Position absolue dans le referenciel du sol
        self.theta = theta # Angle de la voiture par rapport au repère du sol

        # Precalcul de certaine grandeurs pour plus d'optimisation.
        self.f1max = self.a1_weight * 9.81 * PHI # Force maximal de la roue avant droite.
        self.f2max = self.a2_weight * 9.81 * PHI # Force maximal de la roue avant gauche.
        self.f3max = self.a3_weight * 9.81 * PHI # Force maximal de la roue arriere droite.
        self.f4max = self.a4_weight * 9.81 * PHI # Force maximal de la roue arriere gauche.

        self.sign = lambda x, l=1000: 1 - 2/(1 + math.exp(max(-100, min(100, l*x)))) # Fonction signe continue.

    def update(self, consigne1, consigne2, consigne3, consigne4, *, dt=0.01):
        """
        |===============================================|
        | Met a jour l'etat de la voiture a t = t + dt. |
        |===============================================|

        * N'effectue pas de verification car cette fonction est
        appelle au coeur d'une boucle.

        Parameters
        ----------
        Les couple sont donne en N.m.
        Un couple positif tend a faire avancer la voiture.
        :param w1: Vitesse angulaire de la roue avant droite.
        :param w2: Vitesse angulaire de la roue avant gauche.
        :param w3: Vitesse angulaire de la roue arriere droite.
        :param w4: Vitesse angulaire de la roue arriere gauche.
        :param dt: Pas d'approximation temporel de l'equa-diff au sens de Newton en seconde.
        """

        w1 = coeffAngleSpeed*consigne1
        w2 = coeffAngleSpeed*consigne2
        w3 = coeffAngleSpeed*consigne3
        w4 = coeffAngleSpeed*consigne4


        # Calcul des vitesse en chaque point des roues a l'instant initial.
        vx1 = self.vx - (A1[1]-G[1])*self.w # Vitesse de la roue avant droite sur x.
        vx2 = self.vx - (A2[1]-G[1])*self.w
        vx3 = self.vx + (G[1]-A3[1])*self.w
        vx4 = self.vx + (G[1]-A4[1])*self.w
        vy1 = self.vy + (A1[0]-G[0])*self.w - w1*R # Vitesse de la roue avant droite sur y.
        vy2 = self.vy - (G[0]-A2[0])*self.w - w2*R
        vy3 = self.vy + (A3[0]-G[0])*self.w - w3*R
        vy4 = self.vy - (G[0]-A4[0])*self.w - w4*R
        v1 = math.sqrt(vx1**2 + vy1**2) # Norme de la vitesse de derappement de la roue avant droite.
        v2 = math.sqrt(vx2**2 + vy2**2)
        v3 = math.sqrt(vx3**2 + vy3**2)
        v4 = math.sqrt(vx4**2 + vy4**2)

        # Calcul des forces absolues sur chaque roues.
        f1 = self.f1max * self.sign(v1) # Comme la fonction signe est continue,
        f2 = self.f2max * self.sign(v2) # il suffit qu'il y a un tout petit dérapage
        f3 = self.f3max * self.sign(v3) # pour que la force ne soit pas negligeable.
        f4 = self.f4max * self.sign(v4)

        # Projection des forces sur x et y.
        try:
            theta1 = math.acos(vx1/v1) * (1 - 2*(vy1<0)) # C'est l'angle trigonometrique
        except ZeroDivisionError:
            theta1 = 0
        try:
            theta2 = math.acos(vx2/v2) * (1 - 2*(vy2<0)) # entre le vecteur de vitesse d'une roue et
        except ZeroDivisionError:
            theta2 = 0
        try:
            theta3 = math.acos(vx3/v3) * (1 - 2*(vy3<0)) # le referenciel locale de la voiture.
        except ZeroDivisionError:
            theta3 = 0
        try:
            theta4 = math.acos(vx4/v4) * (1 - 2*(vy4<0)) # On est passe par les matrices de rotation.
        except ZeroDivisionError:
            theta4 = 0

        f1x = -f1*math.cos(theta1) # Il y a un moins car la force est opposee a la vitesse.
        f2x = -f2*math.cos(theta2)
        f3x = -f3*math.cos(theta3)
        f4x = -f4*math.cos(theta4)
        f1y = -f1*math.sin(theta1)
        f2y = -f2*math.sin(theta2)
        f3y = -f3*math.sin(theta3)
        f4y = -f4*math.sin(theta4)

        # Calcul de la nouvelle tandance.
        moment = -f1x*(A1[1]-G[1]) + f1y*(A1[0]-G[0]) \
                 -f2x*(A2[1]-G[1]) - f2y*(G[0]-A2[0]) \
                 +f3x*(G[1]-A3[1]) + f3y*(A3[0]-G[0]) \
                 +f4x*(G[1]-A4[1]) - f4y*(G[0]-A4[0])
        accelx = (f1x + f2x + f3x + f4x)/M
        accely = (f1y + f2y + f3y + f4y)/M

        # Calcul du nouvel etat par integration.
        self.w += .5*dt * moment/J
        self.vx += .5*dt * accelx
        self.vy += .5*dt * accely
        self.theta += .5*dt * self.w
        self.x += .5*dt * (self.vx*math.cos(self.theta) - self.vy*math.sin(self.theta))
        self.y += .5*dt * (self.vx*math.sin(self.theta) + self.vy*math.cos(self.theta))
