#!/usr/bin/python

"""
|=========================================|
| Interface between Raspberry and Arduino |
|=========================================|

* Communication functions to control the motors.
* Communication functions to read the camera image.

Sur la vraie carte

"""

import getpass
import importlib
import os
import queue
import sys
import threading
import time


class RaspControler:
    """
    |====================================|
    | Controls motors through GPIO pins. |
    |====================================|
    """
    def __init__(self):
        """
        |==============================|
        | Prepare pins to communicate. |
        |==============================|
        """
        self.gpio = importlib.import_module("RPi.GPIO")
        self.gpio.setmode(self.gpio.BCM) # Allow to design GPIO by their names
        self.motors = {
            "m1": {"pwm": 26, "en": 19},
            "m2": {"pwm": 6, "en": 5},
            "m3": {"pwm": 22, "en": 27},
            "m4": {"pwm": 24, "en": 23}} # Matches betwin PINs and GPIOs

        # Set pins as outputs
        for table in self.motors.values():
            for pin in table.values():
                self.gpio.setup(pin, self.gpio.OUT)

        # PWM declaration
        self.pwm = {mot: self.gpio.PWM(table["pwm"], 1000)
            for mot, table in self.motors.items()}

        # Output initialisation
        for mot in self.motors.keys():
            self.gpio.output(self.motors[mot]["en"], self.gpio.LOW)
            self.pwm[mot].start(0.0) # Duty cycle between 0 and 1.

    def move_wheel(self, wheel, speed):
        """
        |================================|
        | Move wheel at the given speed. |
        |================================|

        Parameters
        ----------
        :param wheel: Concerned wheel.
            1/"fr"/"rf": Right front wheel
            2/"fl"/"lf": Left front wheel
            3/"br"/"rb": Right back wheel
            4/"bl"/"lb": Left back wheel
            "l": 2 & 4
            "r": 1 & 3
            "f": 1 & 2
            "b": 3 & 4
            "": 1 & 2 & 3 & 4
        :type wheel: int or str
        :param speed: Concerned motor medium voltage.
            -1 < speed < 1
            -1 = maximal backing up speed
            1 = maximal moving forward speed
            0 = stops
        :type speed: float
        """
        assert isinstance(speed, (int, float)), \
            "'speed' have to be a number. Not a %s." % type(speed).__name__
        assert -1 <= speed <= 1, "abs(speed) must be <= 1. Not %f." % speed

        if isinstance(wheel, int):
            assert 1 <= wheel <= 4, "Wheel number must be between 1 and 4."
            wheels = {w: wheel == w for w in [1, 2, 3, 4]}

        elif isinstance(wheel, str):
            assert all(c in "lrfb" for c in wheel.lower()), "Only 'lrfb' are allowed."
            wheels = {w: True for w in [1, 2, 3, 4]} # Les roues concernees.
            table = {"f": {3, 4}, "b": {1, 2}, "r": {2, 4}, "l": {1, 3}}
            for c in wheel.lower():
                wheels = {w: False if w in table[c] else v for w, v in wheels.items()}

        else:
            raise TypeError("'wheel' has to be of type str or int.")

        for wheel_number, is_change in wheels.items():
            if is_change:
                mot = "m%d" % wheel_number
                self.gpio.output(self.motors[mot]["en"],
                    self.gpio.HIGH if speed >= 0 else self.gpio.LOW)
                self.pwm[mot].ChangeDutyCycle(100*abs(speed))
                print(mot, abs(speed))

    def close(self):
        """
        |================|
        | Close outputs. |
        |================|
        """
        if hasattr(self, "gpio"):
            for p in self.pwm.values():
                p.stop()
            self.gpio.cleanup()

    def __del__(self):
        """
        |=============================|
        | Help the garbage collector. |
        |=============================|
        """
        self.close()

def move_wheel(*args, **kwargs):
    """
    Alias to Controler.move_wheel.
    The purpose is not to recreate a connection each time.

    :seealso: Controler.move_wheel
    """
    if getpass.getuser() == "pi": # If we are on the Raspberry.
        if "controler" not in globals():
            globals()["controler"] = RaspControler()
        return controler.move_wheel(*args, **kwargs)
    else: # If we are not on the Raspberry.
        import communication
        if "client" not in globals():
            globals()["client"] = communication.Client()
        return client.move_wheel(*args, **kwargs)

def get_position():
    """
    Return the actual position of the car.
    """
    import detect
    return detect.get_position()

if __name__ == "__main__":
    if getpass.getuser() == "pi": # If we are on the Raspberry.
        import communication
        communication.Server().ecoute() # The server starts listening.
        print("Program end.")
