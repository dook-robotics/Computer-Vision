import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

contrast = 128

def limit(c):
    if c < 0:
        c = 0
    if c > 255:
        c = 255
    return int(c)

def update(val):
    global blank_image
    global contrast
    global imgplot
    print(sfreq.val)
    contrast = sfreq.val
    imgplot.set_data(imgProc())
    return

def imgProc():
    img = cv2.imread('trees.jpg',1)
    p = img.shape
    rows,cols,colors = p
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

blank_image = imgProc()
# cv2.imwrite("new.jpg", blank_image)
# cv2.imshow('image', blank_image)

imgplot = plt.imshow(blank_image)
axcolor = 'lightgoldenrodyellow'
axfreq = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
sfreq = Slider(axfreq, 'Contrast', -255, 255, valinit=0, valstep=5)
sfreq.on_changed(update)

plt.show()

# cv2.waitKey(0)
# cv2.destroyAllWindows()
