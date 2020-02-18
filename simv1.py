#
#   Jeremy Chizewer
#   COS IW    
#   Sipmeltlation Version 1
#   February 16, 2020
#


import random
from os import sys
import math
import numpy as np
from matplotlib import pyplot as plt
# from matplotlib import patches.Circle as Circle

# count = int(sys.argv[1])
# points = []
# chooses between disk or square

def main():
    # for j in range(4):
        # if j!=3: continue
    # environment parameters
    count = 200000
    shape = 'box'
    pdrop = 1
    numdrops = 5
    pmelt = 0.0002
    pstick1 = 1
    pstick2 = 0.05
    delta = 0.2
    width = 0.05
    fromTop = 1
    hexa = 0
    minStemLen = 5
    # p1count = 1000
    # bounceCount = 1
    stems = [] # phase1(p1count, width, shape)
    # ax = plt.gca()
    # ax.cla() 
    # if shape == 'disk': ax.add_artist(plt.Circle((0,0), radius=1, fill=False))
    # for stem in stems:
    #     ax.plot(stem[-1][0], stem[-1][1], marker='o')
    #     ax.add_artist(plt.Circle((stem[-1][0], stem[-1][1]), radius=delta/2, fill=False))
    #     ax.add_artist(plt.Circle((stem[-1][0], stem[-1][1]), radius=width, fill=False, color='r'))
    #     # plt.plot(circle)
    # plt.axis(xmin=0, xmax=1, ymin=0, ymax=1)
    # plt.axis('equal')
    # fname = 'temp.png'
    # ax.set(xlim=(-1, 1), ylim=(-1, 1))
    # ax.axis('equal')
    # fig = plt.gcf()
    # fig.savefig(fname)
    for i in range(count):
        for j in range(numdrops):
            if random.random() < pdrop: 
                drop = makerandom(shape, 1, 0)
                # bounce(stems, bounceCount, shape, delta, hexa, pstick1, pstick2, width, drop)
                intersect = checkintersect(drop, stems, width)
                if intersect == 1:
                    bounce=makerandom('disk', delta, hexa)
                    if shape == 'disk': drop = [(drop[0]+bounce[0]), (drop[1]+bounce[1])]
                    else: drop = [(drop[0]+bounce[0])%1, (drop[1]+bounce[1])%1]
                    addtostems(drop, stems, width, pstick1)
                elif intersect == 0: 
                    addtostems(drop, stems, width, pstick2)
            shrinkstems(stems, pmelt, fromTop)
        # plotstems(stems)
    # plotstemtops(stems, width, delta)
    print(len(stems))
    fig = plt.gcf()
    ax = plt.gca()
    ax.cla() 
    if shape == 'disk': ax.add_artist(plt.Circle((0,0), radius=1, fill=False))
    for stem in stems:
        if len(stem) < minStemLen: continue
        ax.plot(stem[-1][0], stem[-1][1], marker='o')
        ax.add_artist(plt.Circle((stem[-1][0], stem[-1][1]), radius=delta/2, fill=False))
        ax.add_artist(plt.Circle((stem[-1][0], stem[-1][1]), radius=width, fill=False, color='r'))
        # plt.plot(circle)
    plt.axis(xmin=0, xmax=1, ymin=0, ymax=1)
    plt.axis('equal')
    fname = sys.argv[1] + shape + str(count) + '-' + str(pstick1) + '-' + str(pmelt) + '-' + str(pstick2) + '-' + str(delta) + '-' + str(width) + '-' + str(numdrops) + '-' +  str(minStemLen) + '-' + str(hexa) + '.png'
    ax.set(xlim=(-1, 1), ylim=(-1, 1))
    ax.axis('equal')
    # plt.show()
    fig.savefig(fname)

def phase1(p1count, width, shape):
    stems = []
    for i in range(p1count):
        drop = makerandom(shape, 1, 0)
        intersect = checkintersect(drop, stems, width)
        if intersect == 0:
            stems.append([drop])
    return stems

def bounce(stems, bounceCount, shape, delta, hexa, pstick1, pstick2, width, drop):
    bc = bounceCount
    while(bc > 0):
        intersect = checkintersect(drop, stems, width)
        if intersect == 1:
            bounce=makerandom('disk', delta, hexa)
            if shape == 'disk': drop = [(drop[0]+bounce[0]), (drop[1]+bounce[1])]
            else: drop = [(drop[0]+bounce[0])%1, (drop[1]+bounce[1])%1]
            bc-=1
            if bc == 0: 
                addtostems(drop, stems, width, pstick1)
                return
        elif intersect == 0: 
            addtostems(drop, stems, width, pstick2)
            return
        else: return


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

def makerandom(shape, radius, hexa):
    if shape != 'disk': 
        return [radius*random.random(), radius*random.random()]
    else:
        R = 0
        t = 0
        if radius != 1:
            R = radius
        else: R = random.random()
        if hexa==1: t = np.random.randint(6)/6
        else: t = random.random()
        return [math.sqrt(R)*math.cos(2*math.pi*t), math.sqrt(R)*math.sin(2*math.pi*t)]


def checkintersect(drop, stems, width):
    for stem in stems:
        dist = math.pow(stem[-1][0]-drop[0],2)+math.pow(stem[-1][1]-drop[1],2)
        if dist < math.pow(width, 2):
            return 1
        elif dist < math.pow(3*width, 2):
            return -1
        for i in stem[:-1]:
            dist = math.pow(i[0]-drop[0],2)+math.pow(i[1]-drop[1],2)
            if dist < math.pow(3*width, 2):
                return -1
    return 0

def addtostems(drop, stems, width, pstick):
    for stem in stems:
        dist = math.pow(stem[-1][0]-drop[0],2)+math.pow(stem[-1][1]-drop[1],2)
        if dist < math.pow(width, 2):
            if random.random() < pstick: 
                stem.append(drop)
                return 
        if dist < math.pow(3*width, 2):
            return
    if random.random() < pstick: stems.append([drop])


def shrinkstems(stems, pmelt, fromTop):
    for stem in stems:
        if random.random() < pmelt:
            if fromTop == 1: del stem[-1]
            else: del stem[0]
            if len(stem) == 0:
                stems.remove(stem)

# def analyzestems(stems, width, delta):
#     checker = [stems[0]]

main()