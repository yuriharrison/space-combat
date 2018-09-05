import math
import numpy as np
from scipy.spatial import distance


def circle_collision(a, b):
    return (a.radius + b.radius) >= distance.euclidean(a.spos, b.spos)


def rectangle_collision(a, b):
    pass


def coordinates(distance, degrees):
    radians = degrees * math.pi / 180
    x = distance * np.cos(radians)
    y = distance * np.sin(radians)
    return x, y