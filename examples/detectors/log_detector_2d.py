"""
LoG 2D detection
================

This example shows how to detect particles in 2D+t image using the LoG detector
"""

import numpy as np
import napari

from stracking.detectors import LoGDetector
from stracking.data import fake_traks1

# load 2D+t sample
image = fake_traks1()

# detect particles
detector = LoGDetector(min_sigma=4, max_sigma=5, threshold=0.2)
particles = detector.run(image)

# visualize in napari
viewer = napari.view_image(np.transpose(image, (2, 0, 1)))
viewer.add_points(particles.data, size=2)
napari.run()
