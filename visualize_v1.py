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


__author__ = "Jeremey Chizewer, Joseph Rubin"


DISK = 0
SQUARE = 1


def _main():
    if len(sys.argv) < 2:
        alert_bad_usage_and_abort()
    
    filename = sys.argv[1]

    with open(filename, 'r') as data_file:
        data = json.loads(data_file.read())
        settings = data['settings']
        stems = data['stems']

    # Find clusters.
    #coords = [state['points'][point_id]['coord'] for point_id in state['points']]
    #seen_points = set()
    #geo = kdtreemap.create(coords)
    #stack = []
    #while stack

    visualize_init(settings)
    
    heights = []
    for point in stems:
        height = point['height']
        heights.append(height)
    max_height = max(heights)

    stem_coords = []
    stems_pruned = []
    for point in stems:
        height = point['height']
        if height > max_height * 0.5:
            stem_coords.append(point['coord'])
            stems_pruned.append(point)

    visualize_state_stems(stems_pruned, settings)

    tri = scipy.spatial.Delaunay(stem_coords)
    boundary_simplices = [i for i, _ in enumerate(tri.simplices) if -1 in tri.neighbors[i]]
    simplices_left = [s for i, s in enumerate(tri.simplices) if i not in boundary_simplices]
    plt.triplot([p[0] for p in tri.points], [p[1] for p in tri.points], tri.simplices)

    #vor = scipy.spatial.Voronoi(stem_coords)
    #scipy.spatial.voronoi_plot_2d(vor, plt.gca())

    plt.show()


def alert_bad_usage_and_abort():
    print('usage: {}: <filename.json>'.format(sys.argv[0]), file=sys.stderr)
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


def visualize_state_stems(stems, settings):
    fig = plt.gcf()
    ax = plt.gca()

    height_max = None
    for point in stems:
        height = point['height']
        if height_max is None or height > height_max:
            height_max = height

    for point in stems:
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
