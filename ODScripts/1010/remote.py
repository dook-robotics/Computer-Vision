import pygame

axisUpDown = 4                          # Joystick axis to read for up / down position
axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
axisLeftRight = 3                       # Joystick axis to read for left / right position
axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped

def ps4(j):
    # Get the currently pressed keys on the keyboard
    events = pygame.event.get()
    for event in events:
        # Keys have changed, generate the command list based on keys
        if event.type == pygame.JOYBUTTONDOWN:
            if j.get_button(0):
                print("Pressed: X")
                return 2
            elif j.get_button(1):
                print("Pressed: Circle")
                return 4
            elif j.get_button(2):
                print("Pressed: Triangle")
                return 3
            elif j.get_button(3):
                print("Pressed: Square")
                return 5
            elif j.get_button(4):
                print("Pressed: L1")
            elif j.get_button(5):
                print("Pressed: R1")
            elif j.get_button(6):
                print("Pressed: L2")
            elif j.get_button(7):
                print("Pressed: R2")
            elif j.get_button(8):
                print("Pressed: SHARE")
            elif j.get_button(9):
                print("Pressed: OPTIONS")
                return 1
            elif j.get_button(10):
                print("Pressed: PS Button")
                return 6
            elif j.get_button(11):
                print("Pressed: Left Analog")
            elif j.get_button(12):
                print("Pressed: Right Analog")
    return 0

def ps4Stick(j):
    # Get the currently pressed keys on the keyboard
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.JOYAXISMOTION:
            moveUp = False
            moveDown = False
            moveRight = False
            moveLeft = False

            # A joystick has been moved, read axis positions (-1 to +1)
            upDown = j.get_axis(axisUpDown)
            leftRight = j.get_axis(axisLeftRight)

            # Invert any axes which are incorrect
            if axisUpDownInverted:
                upDown = -upDown
            if axisLeftRightInverted:
                leftRight = -leftRight

            # Determine Up / Down values
            if upDown < -0.1:
                moveUp = True
                moveDown = False
            elif upDown > 0.1:
                moveUp = False
                moveDown = True
            else:
                moveUp = False
                moveDown = False

            # Determine Left / Right values
            if leftRight < -0.1:
                moveLeft = True
                moveRight = False
            elif leftRight > 0.1:
                moveLeft = False
                moveRight = True
            else:
                moveLeft = False
                moveRight = False
            return (upDown, leftRight)
    return (0,0)

def controllerCount():
    return pygame.joystick.get_count()
