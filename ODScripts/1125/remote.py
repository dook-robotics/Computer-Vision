## remote.py ##
## functions for the ps4 remote ##
#
# Authors:
#   Mikian Musser      - https://github.com/mm909
#   Eric Becerril-Blas - https://github.com/lordbecerril
#   Zoyla Orellana     - https://github.com/ZoylaO
#   Austin Janushan    - https://github.com/Janushan-Austin
#   Giovanny Vazquez   - https://github.com/giovannyVazquez
#   Ameera Essaqi      - https://github.com/AmeeraE
#   Brandon Herrera    - herrer10@unlv.nevada.edu
#   Esdras Morales     - morale2@unlv.nevada.edu
#
# Organization:
#   Dook Robotics - https://github.com/dook-robotics

import os
import pygame

# Joystick axis to read for up / down left / right position
# Set this to True if up and down appear to be swapped
axisUpDown            = 4
axisUpDownInverted    = False
axisLeftRight         = 3
axisLeftRightInverted = False

def ps4(j):
    # Get the currently pressed keys on the keyboard
    events = pygame.event.get()
    buttonPressed = 0
    axis = {}
    for event in events:
        # Keys have changed, generate the command list based on keys
        if event.type == pygame.JOYBUTTONDOWN:

            if event.button == 0:
                print("Pressed: X")
                buttonPressed = 2

            elif event.button == 1:
                print("Pressed: Circle")
                buttonPressed = 4

            elif event.button == 2:
                print("Pressed: Triangle")
                buttonPressed = 3

            elif event.button == 3:
                print("Pressed: Square")
                buttonPressed = 5

            elif event.button == 4:
                print("Pressed: L1")
                buttonPressed = 7

            elif event.button == 5:
                print("Pressed: R1")
                buttonPressed = 8

            elif event.button == 6:
                print("Pressed: L2")

            elif event.button == 7:
                print("Pressed: R2")

            elif event.button == 8:
                print("Pressed: SHARE")

            elif event.button == 9:
                print("Pressed: OPTIONS")
                buttonPressed = 1

            elif event.button == 10:
                print("Pressed: PS Button")
                buttonPressed = 6

            elif event.button == 11:
                print("Pressed: Left Analog")

            elif event.button == 12:
                print("Pressed: Right Analog")

        elif event.type == pygame.JOYAXISMOTION:
            axis[event.axis] = round(event.value,2)
            
    return buttonPressed, axis

def controllerCount():
    return pygame.joystick.get_count()

