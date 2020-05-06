"""Simulation of stems on a 2D plane.

TODO: more information here.
"""

import json
import math
from os import sys

import kdtree
from matplotlib import pyplot as plt
import matplotlib
import matplotlib.patches
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from drop import Drop
from util import *

import cProfile


__author__ = "Jeremey Chizewer, Joseph Rubin"


# The number of drops to generate.
DROP_COUNT = 100000
# The radius of a drop.
DROP_RADIUS = 0.03
# The radius of a stem.
STEM_RADIUS = DROP_RADIUS
# The distance that a drop will bounce.
BOUNCE_DISTANCE = 5 * DROP_RADIUS
# The shape of this 2D plane.
PLANE_SHAPE = DISK
# The probability that any given stem will melt after a single simulation step.
MELT_PROBABILITY = 0.03
# The probability that a drop will stick to the ground.
GROUND_STICK_PROBABILITY = 0.05
# The probability that a drop will stick to a stem if it doesn't bounce.
STEM_STICK_PROBABILITY = 1
# Run in interactive (draw-as-you-go) mode.
INTERACTIVE_MODE = False
# Delay between each draw in INTERACTIVE_MODE.
INTERACTIVE_DELAY = 0.2
#
INTERACTIVE_FAST_MODE = False
#
INTERACTIVE_FAST_INTERVAL = 20000
#
BOUNCE_HEIGHT_ADDITION = 20
#
OLD_GENOME_BIAS = 40
#
SHOW_BOUNCE_RADIUS = False
#
MELT_INTERVAL = 30
#
PERIODIC_BOUNDARY = False


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
        'BOUNCE_HEIGHT_ADDITION': BOUNCE_HEIGHT_ADDITION,
        'MELT_INTERVAL': MELT_INTERVAL,
        'PERIODIC_BOUNDARY': PERIODIC_BOUNDARY
    }

    state = {'points': {}, 'geo': kdtree.create(dimensions=2), 'steps_completed': 0}
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

    _state = {'points': points, 'stems': stems}
    print(json.dumps({'settings': settings, 'state': _state}))


def visualize_init():
    matplotlib.use('TkAgg')
    plt.clf()
    fig = plt.gcf()
    ax = plt.gca()
    fig.set_size_inches(12, 12)
    ax.axis('equal', adjustable='datalim')
    ax.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5))
    if PLANE_SHAPE == DISK: ax.add_artist(plt.Circle((0,0), radius=1, fill=False))
    elif PLANE_SHAPE == SQUARE:
        border = matplotlib.patches.Rectangle((-1, -1), 2, 2, fill=False)
        ax.add_patch(border)


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


last_fast_draw_artists = []
def visualize_state(state):
    global last_fast_draw_artists
    for artist in last_fast_draw_artists:
        artist.remove()
    last_fast_traw = []

    points = state['points']
    geo = state['geo']

    fig = plt.gcf()
    
    ax = plt.gca()

    if PLANE_SHAPE == DISK:
        border = plt.Circle((0,0), radius=1, fill=False)
        ax.add_artist(border)
        last_fast_draw_artists.append(border)
    elif PLANE_SHAPE == SQUARE:
        border = matplotlib.patches.Rectangle((-1, -1), 2, 2, fill=False)
        ax.add_patch(border)
        last_fast_draw_artists.append(border)

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
        if height < 0.5 * height_max:
            continue
        color = (height / (height_max + 1))
        drop_artist = plt.Circle((coord[0], coord[1]), radius=DROP_RADIUS, fill=True, color=(color, 0, 0, 1))
        ax.add_artist(drop_artist)
        last_fast_draw_artists.append(drop_artist)
        if SHOW_BOUNCE_RADIUS:
            bounce_artist_outer = plt.Circle((coord[0], coord[1]), radius=BOUNCE_DISTANCE + DROP_RADIUS*1, fill=False, color=(color, 0, 0, 1))
            bounce_artist_inner = plt.Circle((coord[0], coord[1]), radius=BOUNCE_DISTANCE - DROP_RADIUS*1, fill=False, color=(color, 0, 0, 1))
            ax.add_artist(bounce_artist_outer)
            ax.add_artist(bounce_artist_inner)

    plt.draw()
    #plt.savefig("gallery1/{}.png".format(state['steps_completed']))
    plt.pause(INTERACTIVE_DELAY)


def visualize_drop(coords):
    """Draw a single drop on the screen."""
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
    """Draw a single drop on the screen."""
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

    # We're constantly removing and adding to our kdtree, so rebalance it every
    # so often for efficiency.
    if len(points) != 0 and steps_completed % 600 == 0 and geo.data is not None:
        geo = geo.rebalance()

    # In interactive fast mode we draw the state every so often.
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
        if PERIODIC_BOUNDARY:
            phantom_drops = [
                (drop_coord[0] + 2, drop_coord[1]),
                (drop_coord[0] - 2, drop_coord[1]),
                (drop_coord[0], drop_coord[1] + 2),
                (drop_coord[0], drop_coord[1] - 2),
                (drop_coord[0] + 2, drop_coord[1] + 2),
                (drop_coord[0] + 2, drop_coord[1] - 2),
                (drop_coord[0] - 2, drop_coord[1] + 2),
                (drop_coord[0] - 2, drop_coord[1] - 2)
            ]
            for phantom_drop in phantom_drops:
                intersections.extend(geo.search_nn_dist(phantom_drop, (DROP_RADIUS + STEM_RADIUS) * (DROP_RADIUS + STEM_RADIUS)))

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

            # For periodic boundary conditions we roll over from the end + bounce_offset[1])
            if PERIODIC_BOUNDARY:
                drop_coord = [highest_point['coord'][0] + bounce_offset[0], highest_point['coord'][1] + bounce_offset[1]]
                if drop_coord[0] > 1:
                    drop_coord[0] -= 2
                if drop_coord[1] > 1:
                    drop_coord[1] -= 2
                if drop_coord[0] < -1:
                    drop_coord[0] += 2
                if drop_coord[1] < -1:
                    drop_coord[1] += 2
                drop_coord = tuple(drop_coord)
            else:
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
                        unvisualize_drop(highest_point['artist'])
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
                elif settings['INTERACTIVE_MODE']:
                    unvisualize_drop(drop_artist)

    new_state = {'points': points, 'geo': geo, 'steps_completed': steps_completed}
    if steps_completed % settings['MELT_INTERVAL'] == 0:
        new_state = melt(new_state)

    return {'points': new_state['points'], 'geo': new_state['geo'], 'steps_completed': new_state['steps_completed'] + 1}


def melt(state):
    steps_completed = state['steps_completed']
    geo = state['geo']
    points = state['points']

    # Melt stems from the bottom.
    none_count = 0
    if len(points) != 0:
        for node in kdtree.level_order(geo):
            # Bug fix for empty root.
            if node.data is None:
                none_count += 1
                assert none_count <= 1
                break

            point_id = node.data.ident
            point = points[point_id]

            # Calculate the proper melt amount probabalistically.
            binom_melt_amount = np.random.binomial(MELT_INTERVAL, MELT_PROBABILITY)

            # There shouldn't be any stems that should have already been removed.
            assert points[point_id]['height'] >= 0

            # Melt the stem and remove it if its height has decreased past zero.
            points[point_id]['height'] -= binom_melt_amount
            if points[point_id]['height'] < 0:
                geo = geo.remove(point['coord'])
                if INTERACTIVE_MODE:
                    unvisualize_drop(point['artist'])

    return {'points': points, 'geo': geo, 'steps_completed': steps_completed}


if __name__ == '__main__':
    #cProfile.run('_main()')
    _main()
