"""Geometric primitives."""


import random
import math


DISK = 0
SQUARE = 1


def circle_circle_intersect(center_coord_a, center_coord_b, radius_a, radius_b):
    """Return True iff. the circle of radius `radius_a` centered on `center_coord_a`
    intersects with the circle of radius `radius_b` centered on `center_coord_b`."""
    delta_x = center_coord_b[0] - center_coord_a[0]
    delta_y = center_coord_b[1] - center_coord_a[1]
    distance_squared = delta_x * delta_x + delta_y * delta_y
    radius_sum = radius_a + radius_b
    return distance_squared <= radius_sum * radius_sum


def random_coord(shape):
    """Return a random (x,y) coordinate inside  unit `shape`."""
    if shape == DISK:
        theta = random_theta()
        radial = math.sqrt(random_real())
        return polar_to_cartesian(radial, theta)
    elif shape == SQUARE:
        return (random_real() * 2 - 1, random_real() * 2 - 1)
    else:
        raise ValueError('Illegal value for `shape`.')


def random_real(maximum=1):
    """Return a random real number from 0 to `maximum`."""
    return random.random() * maximum


def random_theta():
    """Return a random angle from 0 to 2*PI."""
    return random_real() * 2 * math.pi


def polar_to_cartesian(radial, theta):
    """Convert a coordinate in (r, th) to (x, y)."""
    return (radial * math.cos(theta), radial * math.sin(theta))