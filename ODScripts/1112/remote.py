import pygame

axisUpDown = 4                          # Joystick axis to read for up / down position
axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
axisLeftRight = 3                       # Joystick axis to read for left / right position
axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped

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
            elif event.button == 5:
                print("Pressed: R1")
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

def ps4Stick(j):
    # Get the currently pressed keys on the keyboard
    print("getting joysticks")
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            print(event.axis)
            print(event.value)
            

    return (0,0)

def controllerCount():
    return pygame.joystick.get_count()
