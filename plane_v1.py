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
BOUNCE_DISTANCE = 0.3
# The shape of this 2D plane.
PLANE_SHAPE = DISK
# The probability that any given stem will melt after a single simulation step.
MELT_PROBABILITY = 0.03
# The probability that a drop will stick to the ground.
GROUND_STICK_PROBABILITY = 1#0.0005
# The probability that a drop will stick to a stem if it doesn't bounce.
STEM_STICK_PROBABILITY = 1
# Run in interactive (draw-as-you-go) mode.
INTERACTIVE_MODE = False
# Delay between each draw in INTERACTIVE_MODE.
INTERACTIVE_DELAY = 0.0001


def bounce_probability(bounce_count):
    """Return the probability that a drop will bounce given that it
    has bounced `bounce_count` times already."""
    # TODO: allow bouncing
    return 1 / (math.pow(2, bounce_count + 1))


def melt_probability(x, y):
    return MELT_PROBABILITY


def _main():
    """Run a 2D simulation of life. Chazelle is love. Chazelle is life."""
    visualize_init()

    state = {'points': {}, 'stems': [], 'geo': kdtreemap.create(dimensions=2), 'steps_completed': 0}
    state = simulate_step(state, DROP_COUNT)

    stems = state['stems']
    points = state['points']

    print('Number of stems: ', len(stems), file=sys.stderr)
    print('Number of points: ', len(points), file=sys.stderr)

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
        'INTERACTIVE_DELAY': INTERACTIVE_DELAY
    }
    _state = {'points': state['points'], 'stems': state['stems']}
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


def visualize_drop(coords):
    fig = plt.gcf()
    ax = plt.gca()
    drop_artist = plt.Circle((coords[0], coords[1]), radius=DROP_RADIUS, fill=True, color=(1, 0, 0, 0.4))
    ax.add_artist(drop_artist)
    plt.draw()
    plt.pause(INTERACTIVE_DELAY)
    return drop_artist


def unvisualize_drop(artist):
    artist.remove()
    plt.draw()
    plt.pause(INTERACTIVE_DELAY)


def simulate_step(state, step_count=1):
    """Run `step_count` steps of the simulation on `state`, returning
    the final state."""
    for _ in range(step_count):
        state = _simulate_single_step(state)
    return state


def _simulate_single_step(state):
    """Run a single step of the simulation on `state`, returning the next state."""

    # Recover the important parts of our state.
    stems = state['stems']
    geo = state['geo']
    points = state['points']
    steps_completed = state['steps_completed']

    # Create a new drop in the plane.
    drop_coord = random_coord(PLANE_SHAPE)

    drop_artist = None
    if INTERACTIVE_MODE:
        drop_artist = visualize_drop(drop_coord)

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
                point_id = node.value
                point = points[point_id]

                assert node.data == point['coord']
                
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
                drop_artist = visualize_drop(drop_coord)
        else:
            # The drop does not bounce.
            drop_stuck = True
            if drop_stem_intersect:
                # The drop has landed on top of an existing stem. Replace
                # the top of the stem with the new drop.
                if random_real() <= STEM_STICK_PROBABILITY:
                    intersection_stem = highest_point['stem']
                    assert len(intersection_stem) > 0
                    if INTERACTIVE_MODE:
                        unvisualize_drop(highest_point['artist'])
                        #points[highest_point_id]['artist'] = visualize_drop(highest_point['coord'])
                    geo.remove(points[intersection_stem[-1]]['coord'])
                    geo.add(drop_coord, value=steps_completed)
                    new_height = points[intersection_stem[-1]]['height'] + 1
                    intersection_stem.append(steps_completed)
                    points[steps_completed] = {'height': new_height, 'artist': drop_artist, 'coord': drop_coord, 'stem': intersection_stem}
                    #stems[stem_intersect_index].insert(0, drop_coord)
                    #stems[steps_completed] = stems[stem_intersect_index]
                    #del stems[stem_intersect_index]
            else:
                # The drop has landed outside of any stem. Simply add
                # it as a new stem.
                if random_real() <= GROUND_STICK_PROBABILITY:
                    assert steps_completed not in stems
                    # Create a new stem for this drop.
                    new_stem = [steps_completed]
                    stems.append(new_stem)
                    geo.add(drop_coord, value=steps_completed)
                    points[steps_completed] = {'height': 0, 'artist': drop_artist, 'coord': drop_coord, 'stem': new_stem}
                elif INTERACTIVE_MODE:
                    unvisualize_drop(drop_artist)

    # Melt stems from the bottom.
    to_remove = set()
    for i, stem in enumerate(stems):
        assert stem
        bottom_point_id = stem[0]
        point = points[bottom_point_id]
        if random_real() <= melt_probability(point['coord'][0], point['coord'][1]):
            stem.pop(0)
            height = point['height']
            assert height == 0
            geo.remove(point['coord'])
            del points[bottom_point_id]
            if not stem:
                to_remove.add(i)
                if INTERACTIVE_MODE:
                    unvisualize_drop(point['artist'])
            else:
                for point_id in stem:
                    points[point_id]['height'] -= 1
                    assert points[point_id]['height'] >= 0

    stems = [s for i, s in enumerate(stems) if i not in to_remove]

    return {'points': points, 'stems': stems, 'geo': geo, 'steps_completed': steps_completed + 1}


def print_stem(stem, points):
    for point_id in stem:
        point = points[point_id]
        print(point)


def plotstems(stems):
    plt.clf()
    for stem in stems:
        plt.plot([i[0] for i in stem], [i[1] for i in stem], marker='.')
    plt.axis(xmin=0, xmax=1, ymin=0, ymax=1)
    plt.draw()
    plt.pause(0.01)


def plotstemtops(stems, width, delta):
    # fig = plt.gcf()
    ax = plt.gca()
    ax.cla() 
    plt.axis(xmin=0, xmax=1, ymin=0, ymax=1)
    plt.axis('equal')
    for stem in stems:
        for i in stem:
            ax.plot(i[0], i[1], marker='.')
        ax.plot(stem[-1][0], stem[-1][1], marker='.')
        ax.add_artist(plt.Circle((stem[-1][0], stem[-1][1]), radius=delta, fill=False))
        ax.add_artist(plt.Circle((stem[-1][0], stem[-1][1]), radius=width, fill=False, color='r'))
    plt.show()
    # plt.pause(0.01)


# todo: put the below in separate files.


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
    _main()
