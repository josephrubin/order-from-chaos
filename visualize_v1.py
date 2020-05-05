"""Simulation of stems on a 2D plane.

TODO: more information here.
"""

import json
import math
from os import sys
import random

import kdtreemap
from matplotlib import pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import scipy.spatial


__author__ = "Jeremey Chizewer, Joseph Rubin"


DISK = 0
SQUARE = 1


def _main():
    """Run a 2D simulation of life. Chazelle is love. Chazelle is life."""
    if len(sys.argv) < 3:
        alert_bad_usage_and_abort()
    
    filename = sys.argv[1]
    visualization = sys.argv[2]

    with open(filename, 'r') as data_file:
        data = json.loads(data_file.read())
        settings = data['settings']
        state = data['state']

    # Find clusters.
    #coords = [state['points'][point_id]['coord'] for point_id in state['points']]
    #seen_points = set()
    #geo = kdtreemap.create(coords)
    #stack = []
    #while stack

    visualize_init(settings)
    
    heights = []
    for point_id in state['stems']:
        point = state['points'][str(point_id)]
        height = point['height']
        heights.append(height)
    max_height = max(heights)

    stem_coords = []
    stems = []
    for point_id in state['stems']:
        point = state['points'][str(point_id)]
        height = point['height']
        if height > max_height * 0.5:
            stem_coords.append(point['coord'])
            stems.append(point_id)

    state['stems'] = stems

    if visualization == 'p':
        visualize_state_points(state, settings)
    elif visualization == 's':
        visualize_state_stems(state, settings)
    elif visualization == 'b':
        visualize_state_points(state, settings)
        visualize_state_stems(state, settings)
    else:
        alert_bad_usage_and_abort()

    tri = scipy.spatial.Delaunay(stem_coords)
    #boundary_simplices = [i for i, _ in enumerate(tri.simplices) if -1 in tri.neighbors[i]]
    #simplices_left = [s for i, s in enumerate(tri.simplices) if i not in boundary_simplices]
    plt.triplot([p[0] for p in tri.points], [p[1] for p in tri.points], tri.simplices)

    plt.show()


def alert_bad_usage_and_abort():
    print('usage: {}: <filename.json> <p/s/b>'.format(sys.argv[0]), file=sys.stderr)
    print('p - show all points (drops); s - show stem tops; b - show both', file=sys.stderr)
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
