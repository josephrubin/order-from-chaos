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


def bounce_probability(bounce_count):
    """Return the probability that a drop will bounce given that it
    has bounced `bounce_count` times already."""
    return 1 / (math.pow(2, bounce_count + 1))


def _main():
    """Run a 2D simulation of life."""
    # Validate the cmd args.
    if len(sys.argv) > 3 or len(sys.argv) < 2 or '--help' in sys.argv:
        print('usage: {} <json_config_file_name> [output_file_name]'.format(sys.argv[0]), file=sys.stderr)
        exit(1)
    if len(sys.argv) < 3:
        output_file_name = '/dev/null'
    else:
        output_file_name = sys.argv[2]

    # Load the simulation settings from the JSON config file.
    json_config_file_name = sys.argv[1]
    with open(json_config_file_name, 'r') as json_config_file:
        settings = json.loads(json_config_file.read())['settings']
    
    public_entry(settings, output_file_name)


def public_entry(settings, output_file_name):
    # Define the initial state.
    state = {'points': {}, 'geo': kdtree.create(dimensions=2), 'steps_completed': 0, 'settings': settings}

    visualize_init(settings)

    # Run the simulation.
    state = simulate_step(state, settings['DROP_COUNT'])

    geo = state['geo']
    points = state['points']

    # Collect all of the stems for later analysis.
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
        point = points[point_id]
        stems.append({'coord': point['coord'], 'height': point['height']})

    #print('Number of stems: ', len(stems), file=sys.stderr)
    #print('Number of points: ', len(points), file=sys.stderr)

    # Output the relevant parts of the state.
    _state = {'settings': settings, 'stems': stems}
    with open(output_file_name, 'w') as output_file:
        output_file.write(json.dumps(_state))


def visualize_init(settings):
    matplotlib.use('TkAgg')
    plt.clf()
    fig = plt.gcf()
    ax = plt.gca()
    fig.set_size_inches(12, 12)
    ax.axis('equal', adjustable='datalim')
    ax.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5))
    if settings['PLANE_SHAPE'] == DISK:
        ax.add_artist(plt.Circle((0,0), radius=1, fill=False))
    elif settings['PLANE_SHAPE'] == SQUARE:
        border = matplotlib.patches.Rectangle((-1, -1), 2, 2, fill=False)
        ax.add_patch(border)


def visualize_random(settings, count=100):
    fig = plt.gcf()
    fig.clf()
    
    ax = plt.gca()
    ax.cla()
    fig.set_size_inches(12, 12)
    ax.axis('equal', adjustable='datalim')
    ax.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5))

    if settings['PLANE_SHAPE'] == DISK:
        ax.add_artist(plt.Circle((0,0), radius=1, fill=False))
    elif settings['PLANE_SHAPE'] == SQUARE:
        border = matplotlib.patches.Rectangle((-1, -1), 2, 2, fill=False)
        ax.add_patch(border)

    for _ in range(count):
        coord = random_coord(settings['PLANE_SHAPE'])
        drop_artist = plt.Circle((coord[0], coord[1]), radius=settings['DROP_RADIUS'], fill=True, color=(0, 0, 0, 1))
        ax.add_artist(drop_artist)
        if settings['SHOW_BOUNCE_RADIUS']:
            bounce_artist_outer = plt.Circle((coord[0], coord[1]),
                                             radius=settings['BOUNCE_DISTANCE'] + settings['DROP_RADIUS'],
                                             fill=False, color=(0, 0, 0, 1))
            bounce_artist_inner = plt.Circle((coord[0], coord[1]),
                                             radius=settings['BOUNCE_DISTANCE'] - settings['DROP_RADIUS'],
                                             fill=False, color=(0, 0, 0, 1))
            ax.add_artist(bounce_artist_outer)
            ax.add_artist(bounce_artist_inner)

    plt.draw()
    plt.show()


last_fast_draw_artists = []
def visualize_state(state):
    global last_fast_draw_artists
    for artist in last_fast_draw_artists:
        artist.remove()
    last_fast_draw_artists = []

    points = state['points']
    geo = state['geo']
    settings = state['settings']


    fig = plt.gcf()    
    ax = plt.gca()

    if settings['PLANE_SHAPE'] == DISK:
        border = plt.Circle((0,0), radius=1, fill=False)
        ax.add_artist(border)
        last_fast_draw_artists.append(border)
    elif settings['PLANE_SHAPE'] == SQUARE:
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
        drop_artist = plt.Circle((coord[0], coord[1]), radius=settings['DROP_RADIUS'], fill=True, color=(color, 0, 0, 1))
        ax.add_artist(drop_artist)
        last_fast_draw_artists.append(drop_artist)
        if settings['SHOW_BOUNCE_RADIUS']:
            bounce_artist_outer = plt.Circle((coord[0], coord[1]),
                                             radius=settings['BOUNCE_DISTANCE'] + settings['DROP_RADIUS'],
                                             fill=False, color=(color, 0, 0, 1))
            bounce_artist_inner = plt.Circle((coord[0], coord[1]),
                                             radius=settings['BOUNCE_DISTANCE'] - settings['DROP_RADIUS'],
                                             fill=False, color=(color, 0, 0, 1))
            ax.add_artist(bounce_artist_outer)
            ax.add_artist(bounce_artist_inner)

    plt.draw()
    #plt.savefig("gallery1/{}.png".format(state['steps_completed']))
    plt.pause(settings['INTERACTIVE_DELAY'])


def visualize_drop(coords, settings):
    """Draw a single drop on the screen."""
    fig = plt.gcf()
    ax = plt.gca()
    drop_artist = plt.Circle((coords[0], coords[1]), radius=settings['DROP_RADIUS'], fill=True, color=(1, 0, 0, 0.4))
    ax.add_artist(drop_artist)
    plt.draw()
    plt.pause(settings['INTERACTIVE_DELAY'])
    return drop_artist


def visualize_drop_bounce(coords, settings):
    fig = plt.gcf()
    ax = plt.gca()
    drop_artist = plt.Circle((coords[0], coords[1]), radius=settings['DROP_RADIUS'], fill=True, color=(0, 1, 0, 0.4))
    ax.add_artist(drop_artist)
    plt.draw()
    plt.pause(settings['INTERACTIVE_DELAY'])
    return drop_artist


def visualize_drop_active(coords, settings):
    """Draw a single drop on the screen."""
    fig = plt.gcf()
    ax = plt.gca()
    drop_artist = plt.Circle((coords[0], coords[1]), radius=settings['DROP_RADIUS'], fill=True, color=(0, 0, 1, 0.4))
    ax.add_artist(drop_artist)
    plt.draw()
    plt.pause(settings['INTERACTIVE_DELAY'])
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
    settings = state['settings']

    PLANE_SHAPE = settings['PLANE_SHAPE']
    DROP_RADIUS = settings['DROP_RADIUS']
    STEM_RADIUS = settings['STEM_RADIUS']
    STEM_STICK_PROBABILITY = settings['STEM_STICK_PROBABILITY']
    GROUND_STICK_PROBABILITY = settings['GROUND_STICK_PROBABILITY']
    OLD_GENOME_BIAS = settings['OLD_GENOME_BIAS']
    MELT_INTERVAL = settings['MELT_INTERVAL']
    INTERACTIVE_MODE = settings['INTERACTIVE_MODE']
    PERIODIC_BOUNDARY = settings['PERIODIC_BOUNDARY']
    BOUNCE_DISTANCE = settings['BOUNCE_DISTANCE']

    # We're constantly removing and adding to our kdtree, so rebalance it every
    # so often for efficiency.
    if len(points) != 0 and steps_completed % 600 == 0 and geo.data is not None:
        geo = geo.rebalance()

    # In interactive fast mode we draw the state every so often.
    if settings['INTERACTIVE_FAST_MODE'] and len(points) != 0:
        if steps_completed % settings['INTERACTIVE_FAST_INTERVAL'] == 0:
            visualize_state(state)

    # Create a new drop in the plane.
    drop_coord = random_coord(PLANE_SHAPE)

    drop_artist = None
    if settings['INTERACTIVE_MODE']:
        drop_artist = visualize_drop_active(drop_coord, settings)

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
        if settings['PERIODIC_BOUNDARY']:
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
            if settings['INTERACTIVE_MODE']:
                unvisualize_drop(drop_artist)
            # The drop bounces.
            bounce_count += 1
            bounce_angle = random_theta()
            bounce_offset = polar_to_cartesian(BOUNCE_DISTANCE, bounce_angle)

            # For periodic boundary conditions we roll over from the edges of the boundary.
            if PERIODIC_BOUNDARY:
                assert PLANE_SHAPE == SQUARE
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
                    new_height = highest_point['height'] + 1 + settings['BOUNCE_HEIGHT_ADDITION']
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

    new_state = {'points': points, 'geo': geo, 'steps_completed': steps_completed, 'settings': settings}
    if steps_completed % MELT_INTERVAL == 0:
        new_state = melt(new_state)

    return {'points': new_state['points'], 'geo': new_state['geo'], 'steps_completed': new_state['steps_completed'] + 1, 'settings': settings}


def melt(state):
    steps_completed = state['steps_completed']
    geo = state['geo']
    points = state['points']
    settings = state['settings']
    MELT_INTERVAL = settings['MELT_INTERVAL']
    MELT_PROBABILITY = settings['MELT_PROBABILITY']
    INTERACTIVE_MODE = settings['INTERACTIVE_MODE']

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

    return {'points': points, 'geo': geo, 'steps_completed': steps_completed, 'settings': settings}


if __name__ == '__main__':
    #cProfile.run('_main()')
    _main()
