import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

def grab_frame(cap):
    ret,frame = cap.read()
    return cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

def update(val):
    global contrast
    print("Update contrast:",  sfreq.val)
    contrast = sfreq.val
    return

cap1 = cv2.VideoCapture(0)

im1 = plt.imshow(grab_frame(cap1))
axcolor = 'lightgoldenrodyellow'
axfreq = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
sfreq = Slider(axfreq, 'Contrast', -255, 255, valinit=0, valstep=5)
sfreq.on_changed(update)

plt.ion()

contrast = 128

def limit(c):
    if c < 0:
        c = 0
    if c > 255:
        c = 255
    return int(c)

def imgProc(img):
    p = img.shape
    rows,cols,colors = p
    print(rows,cols)
    print(contrast)
    blank_image = np.zeros((rows,cols,3), np.uint8)

    for i in range(rows):
        for j in range(cols):
            factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
            colour = img[i,j]
            newRed   = limit(factor * (colour[0]   - 128) + 128)
            newGreen = limit(factor * (colour[1] - 128) + 128)
            newBlue  = limit(factor * (colour[2]  - 128) + 128)
            blank_image[i,j] = [newRed, newGreen, newBlue]
    return blank_image

while True:
    im1.set_data(imgProc(grab_frame(cap1)))
    plt.pause(0.2)

plt.ioff() # due to infinite loop, this gets never called.
plt.show()
