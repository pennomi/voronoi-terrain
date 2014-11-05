from __future__ import print_function
import pygame


class XboxController(object):
    sensitivity_digits = 1

    def __init__(self, joystick):
        self.joystick = joystick
        self.joystick.init()

        self._pressing_bumper_right = False

    def _axis(self, i):
        return round(self.joystick.get_axis(i), self.sensitivity_digits)

    @property
    def name(self):
        return self.joystick.get_name()

    @property
    def stick_left(self):
        return self._axis(0), self._axis(1)

    @property
    def stick_right(self):
        return self._axis(3), self._axis(4)

    @property
    def trigger_left(self):
        return self._axis(2)

    @property
    def trigger_right(self):
        return self._axis(5)

    @property
    def bumper_left(self):
        return self.joystick.get_button(4)

    @property
    def bumper_right(self):
        pressed = self.joystick.get_button(5)
        if pressed:
            if not self._pressing_bumper_right:
                return_val = pressed
            else:
                return_val = 0
            self._pressing_bumper_right = True
        else:
            return_val = pressed
            self._pressing_bumper_right = False
        return return_val

    @property
    def dpad(self):
        return self.joystick.get_hat(0)

    @property
    def button_a(self):
        return self.joystick.get_button(0)

    @property
    def button_b(self):
        return self.joystick.get_button(1)

    @property
    def button_x(self):
        return self.joystick.get_button(2)

    @property
    def button_y(self):
        return self.joystick.get_button(3)

    @property
    def button_back(self):
        return self.joystick.get_button(6)

    @property
    def button_start(self):
        return self.joystick.get_button(7)

    @property
    def button_home(self):
        return self.joystick.get_button(8)

    def __repr__(self):
        return "<XBOX Controller: {}>".format(self.name)

    def __str__(self):
        return self.name


class ControllerInput(object):
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        # TODO: hot plugging
        self.controllers = [XboxController(pygame.joystick.Joystick(i))
                            for i in range(pygame.joystick.get_count())]

    def update(self):
        pygame.event.pump()

if __name__ == "__main__":
    """Run this module in debug mode as an input sniffer."""
    c_input = ControllerInput()
    clock = pygame.time.Clock()

    while True:
        c_input.update()
        print(c_input.controllers[0].stick_left, end="\r")
        clock.tick(60)  # Limit to 60 frames per second