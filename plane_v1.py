"""Simulation of stems on a 2D plane.

TODO: more information here.
"""

import json
import math
from os import sys
import random

import kdtree
from matplotlib import pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from drop import Drop

import cProfile


__author__ = "Jeremey Chizewer, Joseph Rubin"


DISK = 0
SQUARE = 1

# The number of drops to generate.
DROP_COUNT = 20000
# The radius of a drop.
DROP_RADIUS = 0.05
# The radius of a stem.
STEM_RADIUS = DROP_RADIUS
# The distance that a drop will bounce.
BOUNCE_DISTANCE = 5 * DROP_RADIUS
# The shape of this 2D plane.
PLANE_SHAPE = DISK
# The probability that any given stem will melt after a single simulation step.
MELT_PROBABILITY = 0.03
# The probability that a drop will stick to the ground.
GROUND_STICK_PROBABILITY = 0.5#0.05
# The probability that a drop will stick to a stem if it doesn't bounce.
STEM_STICK_PROBABILITY = 1
# Run in interactive (draw-as-you-go) mode.
INTERACTIVE_MODE = False
# Delay between each draw in INTERACTIVE_MODE.
INTERACTIVE_DELAY = 0.01
#
INTERACTIVE_FAST_MODE = False
#
INTERACTIVE_FAST_INTERVAL = 10000
#
BOUNCE_HEIGHT_ADDITION = 20
#
OLD_GENOME_BIAS = 40
#
SHOW_BOUNCE_RADIUS = False
#
MELT_INTERVAL = 10


def bounce_probability(bounce_count):
    """Return the probability that a drop will bounce given that it
    has bounced `bounce_count` times already."""
    return 1 / (math.pow(2, bounce_count + 1))


def _main():
    """Run a 2D simulation of life."""
    visualize_init()

    # Output data:
    settings = {
        'DROP_COUNT': DROP_COUNT,
        'DROP_RADIUS': DROP_RADIUS,
        'STEM_RADIUS': STEM_RADIUS,
        'BOUNCE_DISTANCE': BOUNCE_DISTANCE,
        'PLANE_SHAPE': PLANE_SHAPE,
        'MELT_PROBABILITY': MELT_PROBABILITY,
        'GROUND_STICK_PROBABILITY': GROUND_STICK_PROBABILITY,
        'STEM_STICK_PROBABILITY': STEM_STICK_PROBABILITY,
        'INTERACTIVE_MODE': INTERACTIVE_MODE,
        'INTERACTIVE_DELAY': INTERACTIVE_DELAY,
        'OLD_GENOME_BIAS': OLD_GENOME_BIAS,
        'BOUNCE_HEIGHT_ADDITION': BOUNCE_HEIGHT_ADDITION
    }

    state = {'points': {}, 'geo': kdtree.create(dimensions=2), 'steps_completed': 0}
    """
    for i in range(1, 14):
        drop_coord = (-1 + BOUNCE_DISTANCE * i, 0)
        drop_artist = visualize_drop(drop_coord)
        state['geo'].add(drop_coord, value=-1000 + i)
        state['points'][-1000 + i] = {'height': 20, 'artist': drop_artist, 'coord': drop_coord}
    for i in range(1, 14):
        drop_coord = (-1 + BOUNCE_DISTANCE * i + BOUNCE_DISTANCE / 2, BOUNCE_DISTANCE * math.sqrt(3) / 2)
        drop_artist = visualize_drop(drop_coord)
        state['geo'].add(drop_coord, value=-2000 + i)
        state['points'][-2000 + i] = {'height': 20, 'artist': drop_artist, 'coord': drop_coord}
    """
    state = simulate_step(state, DROP_COUNT)

    geo = state['geo']
    points = state['points']

    none_count = 0
    stems = []
    for node in kdtree.level_order(geo):
        # Bug fix for empty root.
        if node.data is None:
            none_count += 1
            assert none_count <= 1
            break
        assert node is not None
        point_id = node.data.ident
        stems.append(point_id)

    print('Number of stems: ', len(stems), file=sys.stderr)
    print('Number of points: ', len(points), file=sys.stderr)

    #print('LEN', len(list(geo.inorder())))
    #kdtreemap.visualize(geo, max_level=5)

    _state = {'points': points, 'stems': stems}
    print(json.dumps({'settings': settings, 'state': _state}))


def visualize_init():
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
    if PLANE_SHAPE == DISK: ax.add_artist(plt.Circle((0,0), radius=1, fill=False))


def visualize_random(count=100):
    fig = plt.gcf()
    fig.clf()
    
    ax = plt.gca()
    ax.cla()
    fig.set_size_inches(12, 12)
    ax.axis('equal', adjustable='datalim')
    ax.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5))

    if PLANE_SHAPE == DISK: ax.add_artist(plt.Circle((0,0), radius=1, fill=False))

    for _ in range(count):
        coord = random_coord(PLANE_SHAPE)
        drop_artist = plt.Circle((coord[0], coord[1]), radius=DROP_RADIUS, fill=True, color=(0, 0, 0, 1))
        ax.add_artist(drop_artist)
        if SHOW_BOUNCE_RADIUS:
            bounce_artist_outer = plt.Circle((coord[0], coord[1]), radius=BOUNCE_DISTANCE + DROP_RADIUS*1, fill=False, color=(0, 0, 0, 1))
            bounce_artist_inner = plt.Circle((coord[0], coord[1]), radius=BOUNCE_DISTANCE - DROP_RADIUS*1, fill=False, color=(0, 0, 0, 1))
            ax.add_artist(bounce_artist_outer)
            ax.add_artist(bounce_artist_inner)

    plt.draw()
    plt.show()


def visualize_state(state):
    points = state['points']
    geo = state['geo']

    fig = plt.gcf()
    fig.clf()
    
    ax = plt.gca()
    ax.cla()
    fig.set_size_inches(12, 12)
    ax.axis('equal', adjustable='datalim')
    ax.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5))

    if PLANE_SHAPE == DISK: ax.add_artist(plt.Circle((0,0), radius=1, fill=False))

    height_max = None
    for point_id in points:
        point = points[point_id]
        height = point['height']
        if height_max is None or height > height_max:
            height_max = height

    none_count = 0
    for node in kdtree.level_order(geo):
        # Bug fix for empty root.
        if node.data is None:
            none_count += 1
            assert none_count <= 1
            break
        assert node is not None
        point_id = node.data.ident
        point = points[point_id]
        coord = point['coord']
        height = point['height']
        color = (height / (height_max + 1))
        if color > 1 or color < 0:
            print('color: ', color)
        drop_artist = plt.Circle((coord[0], coord[1]), radius=DROP_RADIUS, fill=True, color=(color, 0, 0, 1))
        ax.add_artist(drop_artist)
        if SHOW_BOUNCE_RADIUS:
            bounce_artist_outer = plt.Circle((coord[0], coord[1]), radius=BOUNCE_DISTANCE + DROP_RADIUS*1, fill=False, color=(color, 0, 0, 1))
            bounce_artist_inner = plt.Circle((coord[0], coord[1]), radius=BOUNCE_DISTANCE - DROP_RADIUS*1, fill=False, color=(color, 0, 0, 1))
            ax.add_artist(bounce_artist_outer)
            ax.add_artist(bounce_artist_inner)

    plt.draw()
    plt.pause(INTERACTIVE_DELAY)


def visualize_drop(coords):
    fig = plt.gcf()
    ax = plt.gca()
    drop_artist = plt.Circle((coords[0], coords[1]), radius=DROP_RADIUS, fill=True, color=(1, 0, 0, 0.4))
    ax.add_artist(drop_artist)
    plt.draw()
    plt.pause(INTERACTIVE_DELAY)
    return drop_artist


def visualize_drop_bounce(coords):
    fig = plt.gcf()
    ax = plt.gca()
    drop_artist = plt.Circle((coords[0], coords[1]), radius=DROP_RADIUS, fill=True, color=(0, 1, 0, 0.4))
    ax.add_artist(drop_artist)
    plt.draw()
    plt.pause(INTERACTIVE_DELAY)
    return drop_artist


def visualize_drop_active(coords):
    fig = plt.gcf()
    ax = plt.gca()
    drop_artist = plt.Circle((coords[0], coords[1]), radius=DROP_RADIUS, fill=True, color=(0, 0, 1, 0.4))
    ax.add_artist(drop_artist)
    plt.draw()
    plt.pause(INTERACTIVE_DELAY)
    return drop_artist


def unvisualize_drop(artist):
    artist.remove()
    plt.draw()
    #plt.pause(INTERACTIVE_DELAY)


def simulate_step(state, step_count=1):
    """Run `step_count` steps of the simulation on `state`, returning
    the final state."""
    for _ in range(step_count):
        state = _simulate_single_step(state)
    return state


def _simulate_single_step(state):
    """Run a single step of the simulation on `state`, returning the next state."""

    # Recover the important parts of our state.
    geo = state['geo']
    points = state['points']
    steps_completed = state['steps_completed']

    if len(points) != 0 and steps_completed % 500 == 0 and geo.data is not None:
        geo = geo.rebalance()

    if INTERACTIVE_FAST_MODE and len(points) != 0:
        if steps_completed % INTERACTIVE_FAST_INTERVAL == 0:
            visualize_state(state)

    # Create a new drop in the plane.
    drop_coord = random_coord(PLANE_SHAPE)

    drop_artist = None
    if INTERACTIVE_MODE:
        drop_artist = visualize_drop_active(drop_coord)

    # The drop can keep bouncing as long as it intersects a stem
    # and hasn't stuck yet. The bounce probability is determined
    # by bounce_probability(bounce_count).
    drop_stuck = False
    bounce_count = 0
    while not drop_stuck:
        # Check intersection with any stem.
        drop_stem_intersect = False

        # Search the tree for any drop intersections.
        intersections = geo.search_nn_dist(drop_coord, (DROP_RADIUS + STEM_RADIUS) * (DROP_RADIUS + STEM_RADIUS))
        if intersections:
            # The drop has intersected with some other drops that are already there.
            # Find the drop that is the highest up.
            highest_point_height = None
            highest_point = None
            highest_point_id = None
            for node in intersections:
                point_id = node.ident
                point = points[point_id]

                assert node == point['coord']
                
                intersection_height = point['height']
                if highest_point_height is None or intersection_height > highest_point_height:
                    highest_point_height = intersection_height
                    highest_point = point
                    highest_point_id = point_id
            drop_stem_intersect = True

        # Check if the drop bounces.
        if drop_stem_intersect and random_real() <= bounce_probability(bounce_count):
            assert highest_point is not None
            if INTERACTIVE_MODE:
                unvisualize_drop(drop_artist)
            # The drop bounces.
            bounce_count += 1
            bounce_angle = random_theta()
            bounce_offset = polar_to_cartesian(BOUNCE_DISTANCE, bounce_angle)
            #drop_coord = (drop_coord[0] + bounce_offset[0], drop_coord[1] + bounce_offset[1])
            drop_coord = (highest_point['coord'][0] + bounce_offset[0], highest_point['coord'][1] + bounce_offset[1])
            if INTERACTIVE_MODE:
                drop_artist = visualize_drop_bounce(drop_coord)
        else:
            # The drop does not bounce.
            drop_stuck = True
            if drop_stem_intersect:
                # The drop has landed on top of an existing stem. Replace
                # the top of the stem with the new drop.
                if random_real() <= STEM_STICK_PROBABILITY:
                    if INTERACTIVE_MODE:
                        unvisualize_drop(drop_artist)
                        drop_artist = visualize_drop(drop_coord)
                    if INTERACTIVE_MODE:
                        unvisualize_drop(highest_point['artist'])
                        #points[highest_point_id]['artist'] = visualize_drop(highest_point['coord'])
                    geo = geo.remove(highest_point['coord'])
                    assert drop_coord is not None
                    new_coord = ((OLD_GENOME_BIAS * highest_point['coord'][0] + drop_coord[0]) / (1 + OLD_GENOME_BIAS),
                                 (OLD_GENOME_BIAS * highest_point['coord'][1] + drop_coord[1]) / (1 + OLD_GENOME_BIAS))
                    geo.add(Drop(new_coord, ident=steps_completed))
                    new_height = highest_point['height'] + 1 + BOUNCE_HEIGHT_ADDITION
                    points[steps_completed] = {'height': new_height, 'artist': drop_artist, 'coord': new_coord}
            else:
                # The drop has landed outside of any stem. Simply add
                # it as a new stem.
                if random_real() <= GROUND_STICK_PROBABILITY:
                    # Create a new stem for this drop.
                    if INTERACTIVE_MODE:
                        unvisualize_drop(drop_artist)
                        drop_artist = visualize_drop(drop_coord)
                    assert drop_coord is not None
                    geo.add(Drop(drop_coord, ident=steps_completed))
                    points[steps_completed] = {'height': 0, 'artist': drop_artist, 'coord': drop_coord}
                elif INTERACTIVE_MODE:
                    unvisualize_drop(drop_artist)

    new_state = {'points': points, 'geo': geo, 'steps_completed': steps_completed}
    #if steps_completed % MELT_INTERVAL == 0:
    new_state = melt(new_state)

    return {'points': new_state['points'], 'geo': new_state['geo'], 'steps_completed': new_state['steps_completed'] + 1}


def melt(state):
    steps_completed = state['steps_completed']
    geo = state['geo']
    points = state['points']

    # Melt stems from the bottom.
    to_remove = []
    none_count = 0
    if len(points) != 0:
        for node in kdtree.level_order(geo):
            # Bug fix for empty root.
            if node.data is None:
                none_count += 1
                assert none_count <= 1
                break

            #print(type(node))
            point_id = node.data.ident
            #print('found', point_id)
            #print('data', node.data)
            point = points[point_id]

            binom_prob = np.random.binomial(MELT_INTERVAL, MELT_PROBABILITY) / MELT_INTERVAL
            #print(binom_prob)
            #print(random_real(), binom * 0.01)
            #if random_real() <= binom * 0.01:
            if random_real() <= MELT_PROBABILITY:#binom_prob:#MELT_PROBABILITY:
                if (points[point_id]['height'] < 0):
                    print(points[point_id]['height'], point_id)
                assert points[point_id]['height'] >= 0
                points[point_id]['height'] -= 1#MELT_INTERVAL
                if points[point_id]['height'] < 0:
                    #print('made one negative', point_id, points[point_id]['coord'])
                    #geo = geo.remove(point['coord'])
                    to_remove.append(point['coord'])
                    geo = geo.remove(point['coord'])
                    node.deleted = True
                    if INTERACTIVE_MODE:
                        unvisualize_drop(point['artist'])

    return {'points': points, 'geo': geo, 'steps_completed': steps_completed}


# Geometric primitives. ------------------------------------------------------------


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
        return (random_real(), random_real())
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


if __name__ == '__main__':
    #cProfile.run('_main()')
    _main()
