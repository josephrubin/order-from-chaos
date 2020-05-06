"""Run a lot of simulations and collect data."""


import json
import os
import subprocess
import util


PATH = 'collected_data/'


SETTINGS = {
    "DROP_COUNT": 10000,
    "DROP_RADIUS": 0.03,
    "STEM_RADIUS": 0.03,
    "BOUNCE_DISTANCE": 0.15,
    "PLANE_SHAPE": util.DISK,
    "MELT_PROBABILITY": 0.03,
    "GROUND_STICK_PROBABILITY": 0.05,
    "STEM_STICK_PROBABILITY": 1,
    "INTERACTIVE_MODE": False,
    "INTERACTIVE_DELAY": 0.01,
    "INTERACTIVE_FAST_MODE": False,
    "INTERACTIVE_FAST_INTERVAL": 20000,
    "BOUNCE_HEIGHT_ADDITION": 20,
    "OLD_GENOME_BIAS": 40,
    "SHOW_BOUNCE_RADIUS": False,
    "MELT_INTERVAL": 30,
    "PERIODIC_BOUNDARY": False
}


def _main():
    os.mkdir(PATH)

    def vary_old_genom_bias(settings, trial_number):
        settings.OLD_GENOME_BIAS = 1 + trial_number
    run_test('Vary_OLD_GENOME_BIAS', 5, 5, vary_old_genom_bias)


def run_test(test_name, trial_count, average_count, callback):
    # Copy the settings.
    settings = dict(settings)

    # Create a directory for this test.
    dir_name = PATH + test_name + '/'
    os.mkdir(dir_name)

    # Run the test trials.
    for i in range(trial_count):
        # Get the new trial settings.
        callback(settings, i)

        trial_name = '{}_trial_{}'.format(test_name, str(i).zfill(5))
        trial_config_file_name = dir_name + trial_name + '_config.json'
        trial_output_file_name = dir_name + trial_name + '_output.json'

        # For each trial, save a config file.
        with open(trial_config_file_name, 'w') as trial_config_file:
            trial_config_file.write(json.dumps(settings))

        # Start the trial.
        subprocess.run(['plane_v1.py', trial_config_file_name, trial_output_file_name])

        #for j in range(average_count):
            # do with settings


if __name__ == "__main__":
    _main()