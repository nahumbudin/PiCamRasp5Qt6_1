import cv2
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
import numpy as np




def plot_image_histogram(widget, image):
    im = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    histogram, bin_edges = np.histogram(im, bins=128)  #, range=(10, 1024))

    # print(histogram)

    widget.clear()
    widget.hideAxis('bottom')
    widget.hideAxis('left')
    widget.plot(bin_edges[0:-1], histogram)
    widget.autoRange()

    # widget.plot([1, 2, 3], [0, 7, 6])

