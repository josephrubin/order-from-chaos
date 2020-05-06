"""Configuration options for the simulation and their descriptions, along with sample values."""


import json
import util


# The number of drops to generate.
DROP_COUNT = 1000000
# The radius of a drop.
DROP_RADIUS = 0.03
# The radius of a stem.
STEM_RADIUS = DROP_RADIUS
# The distance that a drop will bounce.
BOUNCE_DISTANCE = 5 * DROP_RADIUS
# The shape of this 2D plane.
PLANE_SHAPE = util.DISK
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
# Draw the state every INTERACTIVE_FAST_INTERVAL steps.
INTERACTIVE_FAST_MODE = False
# Interval for INTERACTIVE_FAST_MODE.
INTERACTIVE_FAST_INTERVAL = 20000
# Additional height to add to a stem if a drop lands on it after a bounce.
BOUNCE_HEIGHT_ADDITION = 20
# Weight to apply to old genome when creting a new one after a drop lands on a stem.
OLD_GENOME_BIAS = 40
# In INTERACTIVE_FAST_MODE, show bounce radius as circles around stems.
SHOW_BOUNCE_RADIUS = False
# Number of steps before doing a relatively larger melt (for efficiency).
MELT_INTERVAL = 30
# Use a looping boundary (only when PLANE_SHAPE == DISK).
PERIODIC_BOUNDARY = False


with open('the_config.json', 'w') as config_file:
    config_file.write(json.dumps({"settings": {
        "DROP_COUNT": DROP_COUNT,
        "DROP_RADIUS": DROP_RADIUS,
        "STEM_RADIUS": STEM_RADIUS,
        "BOUNCE_DISTANCE": BOUNCE_DISTANCE,
        "PLANE_SHAPE": PLANE_SHAPE,
        "MELT_PROBABILITY": MELT_PROBABILITY,
        "GROUND_STICK_PROBABILITY": GROUND_STICK_PROBABILITY,
        "STEM_STICK_PROBABILITY": STEM_STICK_PROBABILITY,
        "INTERACTIVE_MODE": INTERACTIVE_MODE,
        "INTERACTIVE_DELAY": INTERACTIVE_DELAY,
        "INTERACTIVE_FAST_MODE": INTERACTIVE_FAST_MODE,
        "INTERACTIVE_FAST_INTERVAL": INTERACTIVE_FAST_INTERVAL,
        "BOUNCE_HEIGHT_ADDITION": BOUNCE_HEIGHT_ADDITION,
        "OLD_GENOME_BIAS": OLD_GENOME_BIAS,
        "SHOW_BOUNCE_RADIUS": SHOW_BOUNCE_RADIUS,
        "MELT_INTERVAL": MELT_INTERVAL,
        "PERIODIC_BOUNDARY": PERIODIC_BOUNDARY
    }}))