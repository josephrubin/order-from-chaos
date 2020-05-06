"""Simulation of stems on a 2D plane.

TODO: more information here.
"""

import json
import math
from os import sys
import random

from matplotlib import pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import scipy.spatial
import numpy as np

import plane_v1


__author__ = "Jeremey Chizewer, Joseph Rubin"


DISK = 0
SQUARE = 1


def _main():
    if len(sys.argv) < 3:
        alert_bad_usage_and_abort()
    
    filename = sys.argv[1]
    output_filename = sys.argv[2]

    with open(filename, 'r') as data_file:
        data = json.loads(data_file.read())
        settings = data['settings']

        # Compatability.
        if 'state' in data:
            points = data['state']['points']
            stems = data['state']['stems']
        else:
            stems = data['stems']
    
    # Filter the stems if we would like to.
    heights = []
    for point in stems:
        height = point['height']
        heights.append(height)
    max_height = max(heights)

    stem_coords = []
    for point in stems:
        height = point['height']
        if height > max_height * 0.5:
            stem_coords.append(point['coord'])

    # Remove boundary simplices.
    tri = scipy.spatial.Delaunay(stem_coords)
    #boundary_simplices = [i for i, _ in enumerate(tri.simplices) if -1 in tri.neighbors[i]]
    #simplices_left = [s for i, s in enumerate(tri.simplices) if i not in boundary_simplices]
    #tri.simplices = simplices_left

    # Generate random points for comparison.
    random_coords = []
    for i in range(len(stem_coords)):
        random_coords.append(plane_v1.random_coord(settings['PLANE_SHAPE']))

    random_tri = scipy.spatial.Delaunay(random_coords)
    #boundary_simplices = [i for i, _ in enumerate(random_tri.simplices) if -1 in random_tri.neighbors[i]]
    #simplices_left = [s for i, s in enumerate(random_tri.simplices) if i not in boundary_simplices]
    #random_tri.simplices = simplices_left

    tri_angle_std = calculate_angle_stddev(tri, stem_coords)
    random_tri_angle_std = calculate_angle_stddev(random_tri, random_coords)
    tri_side_length_std = calculate_side_length_stddev(tri, stem_coords)
    random_tri_side_length_std = calculate_side_length_stddev(random_tri, random_coords)

    with open(output_filename, 'w') as output_file:
        output_file.write(json.dumps({
            'STEM_ANGLE_STD_DEV': tri_angle_std,
            'RANDOM_ANGLE_STD_DEV': random_tri_angle_std,
            'STEM_SIDE_STD_DEV': tri_side_length_std,
            'RANDOM_SIDE_STD_DEV': random_tri_side_length_std,
            'STEM_COUNT': len(stem_coords)
        }))

    #print('stem angle stddev is', tri_angle_std)
    #print('{} point random angle stddev is'.format(len(stem_coords)), random_tri_angle_std)
    #print('stem side length stddev is', tri_side_length_std)
    #print('{} point random side length stddev is'.format(len(stem_coords)), random_tri_side_length_std)

    #plt.triplot([p[0] for p in tri.points], [p[1] for p in tri.points], tri.simplices)
    #plt.triplot([p[0] for p in random_tri.points], [p[1] for p in random_tri.points], random_tri.simplices)
    #plt.show()


def calculate_angle_stddev(tri, from_coords):
    angles = []
    for simplex in tri.simplices:
        a = from_coords[simplex[0]]
        b = from_coords[simplex[1]]
        c = from_coords[simplex[2]]
        ang1 = calculate_angle(a, b, c)
        ang2 = calculate_angle(c, a, b)
        ang3 = calculate_angle(b, c, a)
        angles.append(ang1)
        angles.append(ang2)
        angles.append(ang3)
    return np.std(angles)


def calculate_side_length_stddev(tri, from_coords):
    side_lengths = []
    for simplex in tri.simplices:
        a = from_coords[simplex[0]]
        b = from_coords[simplex[1]]
        c = from_coords[simplex[2]]
        side_length1 = euclidean_distance(a, b)
        side_length2 = euclidean_distance(b, c)
        side_length3 = euclidean_distance(c, a)
        side_lengths.append(side_length1)
        side_lengths.append(side_length2)
        side_lengths.append(side_length3)
    return np.std(side_lengths)


def euclidean_distance(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.sqrt(dx * dx + dy * dy)


def calculate_angle(a, b, c):
    angle = abs(math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0])))
    if angle > 180:
        angle = 360 - angle
    return angle


def alert_bad_usage_and_abort():
    print('usage: {}: <filename.json> <output_filename.json>'.format(sys.argv[0]), file=sys.stderr)
    exit(1)


def visualize_init(settings):
    matplotlib.use('TkAgg')
    plt.clf()
    fig = plt.gcf()
    ax = plt.gca()
    #ax = Axes3D(fig)
    fig.set_size_inches(12, 12)
    ax.axis('equal', adjustable='datalim')
    ax.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5))
    #plt.axis(xmin=0, xmax=1, ymin=0, ymax=1)
    #plt.axis('equal')
    #fname = sys.argv[1] + shape + str(count) + '-' + str(pstick1) + '-' + str(pmelt) + '-' + str(pstick2) + '-' + str(delta) + '-' + str(width) + '-' + str(numdrops) + '-' +  str(minStemLen) + '-' + str(hexa) + '.png'
    #ax.axis('equal')
    if settings['PLANE_SHAPE'] == DISK: ax.add_artist(plt.Circle((0,0), radius=1, fill=False))


def visualize_state_points(state, settings):
    stems = state['stems']
    points = state['points']

    fig = plt.gcf()
    ax = plt.gca()
    
    for point_id in points:
        point = points[str(point_id)]
        coord = point['coord']
        assert point['stem']
        drop_artist = plt.Circle((coord[0], coord[1]), radius=settings['DROP_RADIUS'], fill=True, color=(0, 1, 0, 0.1))
        ax.add_artist(drop_artist)

    plt.draw()


#temp
def plot(coords):
    visualize_init({'PLANE_SHAPE': 0})
    fig = plt.gcf()
    ax = plt.gca()
    for coord in coords:
        drop_artist = plt.Circle((coord[0], coord[1]), radius=0.05, fill=True, color=(0.5, 0, 0, 1))
        ax.add_artist(drop_artist)
    plt.show()


def visualize_state_stems(state, settings):
    stems = state['stems']
    points = state['points']

    fig = plt.gcf()
    ax = plt.gca()

    height_max = None
    for point_id in points:
        point = points[str(point_id)]
        height = point['height']
        if height_max is None or height > height_max:
            height_max = height

    for point_id in stems:
        point = points[str(point_id)]
        coord = point['coord']
        height = point['height']
        #point_id_bottom = stem[0]
        #point_bottom = points[str(point_id_bottom)]
        #coord_bottom = point_bottom['coord']
        drop_artist = plt.Circle((coord[0], coord[1]), radius=settings['DROP_RADIUS'], fill=True, color=(height / height_max, 0, 0, 1))
        #drop_artist_bottom = plt.Circle((coord_bottom[0], coord_bottom[1]), radius=settings['DROP_RADIUS'], fill=True, color=(0, 0, 1, 0.1))
        ax.add_artist(drop_artist)
        #ax.add_artist(drop_artist_bottom)
        bounce_artist_outer = plt.Circle((coord[0], coord[1]), radius=settings['BOUNCE_DISTANCE'] + settings['DROP_RADIUS']*1, fill=False, color=(height / height_max, 0, 0, 1))
        bounce_artist_inner = plt.Circle((coord[0], coord[1]), radius=settings['BOUNCE_DISTANCE'] - settings['DROP_RADIUS']*1, fill=False, color=(height / height_max, 0, 0, 1))
        #ax.add_artist(bounce_artist_outer)
        #ax.add_artist(bounce_artist_inner)

    plt.draw()


if __name__ == '__main__':
    _main()
