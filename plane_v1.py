"""Simulation of stems on a 2D plane.

TODO: more information here.
"""

import math
from os import sys
import random

import kdtreemap
from matplotlib import pyplot as plt
import matplotlib


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
BOUNCE_DISTANCE = 0.2
# The shape of this 2D plane.
PLANE_SHAPE = DISK
# The probability that any given stem will melt after a single simulation step.
MELT_PROBABILITY = 0.0003
# The probability that a drop will stick to the ground.
GROUND_STICK_PROBABILITY = 0.005
# The probability that a drop will stick to a stem if it doesn't bounce.
STEM_STICK_PROBABILITY = 1
# The probability that all stems under PURGE_MINIMUM_STEM_LENGTH will be destroyed
# in each simulation step.
PURGE_PROBABILITY = 0#0.0005
# The minimum stem length to not be removed during a purge.
PURGE_MINIMUM_STEM_LENGTH = 9
# Run in interactive mode
INTERACTIVE_MODE = True


# TODO: on intersection, add to highest one.


def bounce_probability(bounce_count):
    """Return the probability that a drop will bounce given that it
    has bounced `bounce_count` times already."""
    # TODO: allow bouncing
    return 1 if bounce_count == 0 else 0


def _main():
    """Run a 2D simulation of life. Chazelle is love. Chazelle is life."""
    visualize_init()

    state = {'stems': {}, 'geo': kdtreemap.create(dimensions=2), 'index': {}, 'steps_completed': 0}
    state = simulate_step(state, DROP_COUNT)
    stems = state['stems']
    print('Number of stems: ', len(stems))
    visualize_state(state)


def visualize_init():
    matplotlib.use('TkAgg')
    plt.clf()
    fig = plt.gcf()
    ax = plt.gca()
    plt.axis(xmin=0, xmax=1, ymin=0, ymax=1)
    plt.axis('equal')
    #fname = sys.argv[1] + shape + str(count) + '-' + str(pstick1) + '-' + str(pmelt) + '-' + str(pstick2) + '-' + str(delta) + '-' + str(width) + '-' + str(numdrops) + '-' +  str(minStemLen) + '-' + str(hexa) + '.png'
    ax.set(xlim=(-1, 1), ylim=(-1, 1))
    ax.axis('equal')


def visualize_state(state):
    stems = state['stems']

    plt.clf()

    fig = plt.gcf()
    ax = plt.gca()
    
    ax.cla() 
    if PLANE_SHAPE == DISK: ax.add_artist(plt.Circle((0,0), radius=1, fill=False))
    for stem in stems.values():
        #if len(stem) < 15: continue
        l = len(stem)
        ll = min((l / 100), 1)
        ll = 0.5

        ax.add_artist(plt.Circle((stem[0][0], stem[0][1]), radius=BOUNCE_DISTANCE, fill=False))
        ax.add_artist(plt.Circle((stem[0][0], stem[0][1]), radius=STEM_RADIUS, fill=True, color=(ll, ll, ll)))
        # plt.plot(circle)

    plt.axis(xmin=0, xmax=1, ymin=0, ymax=1)
    plt.axis('equal')
    #fname = sys.argv[1] + shape + str(count) + '-' + str(pstick1) + '-' + str(pmelt) + '-' + str(pstick2) + '-' + str(delta) + '-' + str(width) + '-' + str(numdrops) + '-' +  str(minStemLen) + '-' + str(hexa) + '.png'
    ax.set(xlim=(-1, 1), ylim=(-1, 1))
    ax.axis('equal')
    #plt.show()
    plt.draw()
    plt.pause(0.0001)
    #fig.savefig(fname)


def visualize_drop(coords):
    fig = plt.gcf()
    ax = plt.gca()
    drop_artist = plt.Circle((coords[0], coords[1]), radius=DROP_RADIUS, fill=False)
    ax.add_artist(drop_artist)
    plt.draw()
    plt.pause(0.2)


def unvisualize_drop(artist):
    artist.remove()
    print("REMOVED")


def simulate_step(state, step_count=1):
    """Run `step_count` steps of the simulation on `state`, returning
    the final state."""
    for _ in range(step_count):
        state = _simulate_single_step(state)
    return state


def _simulate_single_step(state):
    """Run a single step of the simulation on `state`, returning the next state."""
    stems = state['stems']
    geo = state['geo']
    index = state['index']
    steps_completed = state['steps_completed']

    #print('stems: ', stems)
    #print('index: ', index)

    # Create a new drop in the plane.
    drop_coord = random_coord(PLANE_SHAPE)

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
        stem_intersect_index = None

        # Search the tree for any drop intersections.
        intersections = geo.search_nn_dist(drop_coord, STEM_RADIUS + DROP_RADIUS)
        if intersections:
            drop_stem_intersect = True
            stem_intersect_index = index[intersections[0]]
            if INTERACTIVE_MODE:
                unvisualize_drop(drop_artist)
            #print('INTERSECTIONS: ', intersections)
            #print('INTERSECT: ', intersections[0])
            #print('INDEX: ', index[intersections[0]])
            #print('STEMS:' , stems)

        # Check if the drop bounces.
        if drop_stem_intersect and random_real() <= bounce_probability(bounce_count):
            #print('BOUNCE')
            # The drop bounces.
            assert stem_intersect_index is not None
            ####
            #if random_real() <= STEM_STICK_PROBABILITY:
            #    state[stem_intersect_index].insert(0, drop_coord)
            ####
            bounce_count += 1
            bounce_angle = random_theta()
            bounce_offset = polar_to_cartesian(BOUNCE_DISTANCE, bounce_angle)
            drop_coord = (drop_coord[0] + bounce_offset[0], drop_coord[1] + bounce_offset[1])
        else:
            # The drop does not bounce.
            drop_stuck = True
            if drop_stem_intersect:
                # The drop has landed on top of an existing stem. Replace
                # the top of the stem with the new drop.
                if random_real() <= STEM_STICK_PROBABILITY:
                    #print('intersected with stem: ', stems[stem_intersect_index])
                    assert len(stems[stem_intersect_index]) > 0
                    # Assign the new drop an index.
                    index[drop_coord] = steps_completed
                    #del index[stems[stem_intersect_index][0]]
                    geo.remove(stems[stem_intersect_index][0])
                    geo.add(drop_coord)
                    stems[stem_intersect_index].insert(0, drop_coord)
                    stems[steps_completed] = stems[stem_intersect_index]
                    del stems[stem_intersect_index]
            else:
                # The drop has landed outside of any stem. Simply add
                # it as a new stem.
                if random_real() <= GROUND_STICK_PROBABILITY:
                    assert drop_coord not in index
                    assert steps_completed not in stems
                    # Assign the new drop an index.
                    index[drop_coord] = steps_completed
                    #print('add')
                    stems[steps_completed] = ([drop_coord])
                    geo.add(drop_coord)

    """
    # Melt stems from the bottom.
    to_delete = []
    for stem_index in stems:
        # Ensure there are no empty stems.
        stem = stems[stem_index]
        assert stem
        if random_real() <= MELT_PROBABILITY:
            # The bottom of the stem is at the end of the list.
            stem.pop()
            # Remove empty stems.
            if not stem:
                to_delete.append(stem_index)

    # The purge.
    if random_real() <= PURGE_PROBABILITY:
        for stem_index in stems:
            stem = stems[stem_index]
            if len(stem) < PURGE_MINIMUM_STEM_LENGTH:
                to_delete.append(stem_index)

    for i in to_delete:
        del index[i]
        geo.remove(stems[i][0])
        geo.add(stems[i][1])
    
    print(stems)
    new_stems = {key: val for (key, val) in stems.items() if key not in to_delete}
    #new_stems = [stems[i] for i in range(len(stems)) if i not in to_delete]
    """
    return {'stems': stems, 'geo': geo, 'index': index, 'steps_completed': steps_completed + 1}


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
