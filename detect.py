#!/usr/bin/env python3

"""
|======================|
| Detect car position. |
|======================|
"""

import cv2
import numpy as np
import threading


lock = threading.Lock()


class ImageCapture(threading.Thread):
    """
    Enable connection with the camera,
    Process read images .
    """
    def __init__ (self):
        super().__init__()
        for k in range(1,5): # Try every possible port where the webcam can be
           self.capture = cv2.VideoCapture(k)
           if not self.capture.isOpened():
                print(k)
                continue
           break

        assert self.capture.isOpened(), "Unable to read data from camera."
        self.camera_image = None
        self.thresh_image = None

        self.show = False

        self.rear = (1, 1)  # Centre du rond arriere de la voiture.
        self.front = (2, 2) # Centre du rond rond avant.
        self.pos = (0, 0) # Le centre de la voiture
        self.alpha = np.pi/2 # L'angle de la voiture par defaut.
        self.init_thresh() # Valeur par defaut du seuil.

    def init_thresh(self):
        """
        Recherche Le seuil optimal.

        * Seul la voiture doit etre presente dans le champ de l'image.
        """
        # On part d'une image toute noire.
        # On diminue le seuil jusqu'a la bonne valeur.

        for thresh in range(255, 0, -1):
            self.thresh = thresh
            self.read()
            if self.thresh_image.mean() > 1.05: #1.045:
                break

    def read(self):
        """
        Get image from camera.

        Returns
        -------
        :return: Image from camera, Thresholded black and white image.
        :rtype: np.ndarray, np.ndarray
        """
        with lock:
            return_value, self.camera_image = self.capture.read()

        if not return_value:
            raise ConnectionError('Unable to read camera video (Stream Stopped ?)')

        gray_image = cv2.cvtColor(self.camera_image, cv2.COLOR_BGR2GRAY)
        _, self.thresh_image = cv2.threshold(gray_image, thresh=self.thresh, maxval=255, type=0) # il y avait thresh=220, maxval=255

    def get_position(self):
        """
        Return barycenter of the car and angle between the car and the abscisses axes.
        """
        self.read()
        coef = 1
        contours, hierarchy = cv2.findContours(self.thresh_image,
                                mode=cv2.RETR_TREE,
                                method=cv2.CHAIN_APPROX_SIMPLE) # Find coutours.
                                
        for i, contour in enumerate(contours):
            if 150*coef < cv2.arcLength(contour, True) < 190*coef: # On detecte la voiture (le perimetre de la voiture etant contenu entre ces 2 valeurs.)
                x, y, width, height = cv2.boundingRect(contour) # Recupere la position du contour.

                moments = cv2.moments(contour)
                try:
                    cx = int(moments['m10']/moments['m00'])
                except ZeroDivisionError:
                    cx = x + width//2
                try:
                    cy = int(moments['m01']/moments['m00'])
                except ZeroDivisionError:
                    cy = y + height//2
                self.pos = (cx, cy)
                self.rear, self.front = self.pos, self.pos

                # Récupère les enfants:
                for j in range(len(hierarchy[0])):
                    if hierarchy[0][j][3] == i:
                        x, y, width, height = cv2.boundingRect(contours[j])
                        moments = cv2.moments(contours[j])
                        try:
                            cx = int(moments['m10']/moments['m00'])
                        except ZeroDivisionError:
                            cx = x + width//2
                        try:
                            cy = int(moments['m01']/moments['m00'])
                        except ZeroDivisionError:
                            cy = y + height//2

                        peri_child = cv2.arcLength(contours[j], True)
                        if peri_child > 75*coef and peri_child < 90*coef:
                            self.rear = (cx, cy)

                        if peri_child > 40*coef and peri_child < 60*coef:
                            self.front = (cx, cy)

        self.orientation() # Met a jour l'angle
        return self.pos, self.alpha

    def run(self):
        """
        Pour le debaugage, affiche en temps reel ce qu'il se passe.
        """
        def draw_target(image, x, y, length):
            """
            Trace une mire sur une image.
            """
            image = cv2.line(image, (x-length, y), (x+length, y), (255, 50, 130), 2)
            image = cv2.line(image, (x, y-length), (x, y+length), (255, 50, 130), 2)
            return image

        while True:
            self.get_position() if self.show else self.read()

            if self.show:
                copy_image = self.camera_image

                copy_image = cv2.putText(copy_image, 'Car', self.pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    color=(0, 255, 0),
                    lineType=2,
                    bottomLeftOrigin=cv2.LINE_AA) # Ajoute du texte.
                copy_image = cv2.circle(copy_image,
                    center=self.pos,
                    radius=3,
                    color=(0, 0, 255),
                    thickness=-1)
                copy_image = cv2.circle(copy_image, self.rear, 3, (255,0,0), -1)
                copy_image = cv2.circle(copy_image, self.front, 3, (0,0,255), -1)

                copy_image = cv2.putText(copy_image,
                    f'Angle : {self.alpha*180/np.pi}' ,(0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
                copy_image = cv2.putText(copy_image,
                    f'Position : {self.pos}', (0, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)

                x = copy_image.shape[1]//2
                y = copy_image.shape[0]//2
                # print("x=", x)
                # print("y=", y)
                print(self.alpha*180/np.pi)
                copy_image = draw_target(copy_image, x, y, 40)
                copy_image = draw_target(copy_image, self.rear[0], self.rear[1], 20)

                cv2.imshow('Thresholded Image', self.thresh_image)
                cv2.imshow('Image test', copy_image)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    def orientation(self):
        """
        |================================|
        | Recupere l'angle d'un segment. |
        |================================|

        Met a jour l'ange oriante par rapport a l'horizontale en radian entre ]-pi, pi].
        """
        norm = np.sqrt((self.front[1] - self.rear[1])**2 + (self.front[0] - self.rear[0])**2)
        if norm:
            self.alpha = np.arccos((self.front[0] - self.rear[0])/norm) * (1 - 2*(self.front[1] > self.rear[1]))

    def __del__(self):
        cv2.destroyAllWindows()


# Starting video capture.

image_capture = ImageCapture()
image_capture.start()

def get_position():
    return image_capture.get_position()

def main():
    image_capture.show = True
    image_capture.join()

if __name__ == '__main__':
    main()
