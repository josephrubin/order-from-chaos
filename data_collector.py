"""Run a lot of simulations in parallel and collect data."""


import json
import os
import os.path
import subprocess
import sys
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


MAX_PROC_COUNT = 7


def _main():
    if not os.path.isdir(PATH):
        os.mkdir(PATH)

    def vary_old_genom_bias(settings, trial_number):
        settings['OLD_GENOME_BIAS'] = 10 * trial_number
    run_test('Vary_OLD_GENOME_BIAS', 10, 5, vary_old_genom_bias)

    def vary_ground_stick_prob(settings, trial_number):
        settings['GROUND_STICK_PROBABILITY'] = 0.05 + 0.05 * trial_number
    run_test('Vary_GROUND_STICK_PROBABILITY', 10, 5, vary_ground_stick_prob)

    def vary_melt_prob(settings, trial_number):
        settings['MELT_PROBABILITY'] = 0.01 + 0.01 * trial_number
    run_test('Vary_MELT_PROBABILITY', 10, 5, vary_melt_prob)
    
    def vary_drop_radius(settings, trial_number):
        settings['DROP_RADIUS'] = 0.03 + 0.02 * trial_number
        settings['STEM_RADIUS'] = 0.03 + 0.02 * trial_number
    run_test('Vary_DROP_RADIUS', 5, 5, vary_drop_radius)

    def vary_bounce_bonus(settings, trial_number):
        settings['BOUNCE_HEIGHT_ADDITION'] = 5 + 5 * trial_number
    run_test('Vary_BOUNCE_BONUS', 10, 5, vary_bounce_bonus)


def run_test(test_name, trial_count, average_count, callback):
    print('Running test {}'.format(test_name))
    sys.stdout.flush()

    # Copy the settings.
    settings = dict(SETTINGS)

    # Create a directory for this test.
    dir_name = PATH + test_name + '/'
    config_dir_name = dir_name + 'config/'
    os.mkdir(dir_name)
    os.mkdir(config_dir_name)

    # Run the test trials.
    procs = []
    for i in range(trial_count):
        # Get the new trial settings.
        callback(settings, i)

        trial_name = '{}_trial_{}'.format(test_name, str(i).zfill(5))
        trial_config_file_name = config_dir_name + str(i).zfill(5) + '.json'

        # For each trial, save a config file.
        with open(trial_config_file_name, 'w') as trial_config_file:
            trial_config_file.write(json.dumps({'settings': settings}))

        # Start the trial.
        for j in range(average_count):
            trial_part_output_file_name = dir_name + str(i).zfill(5) + '_' + str(j).zfill(2) + '.json'
            schedule_process(['python', 'plane_v1.py', trial_config_file_name, trial_part_output_file_name],
                             procs,
                             i, j, test_name, trial_count, average_count)
            print('> Running {} trial {}/{} part {}/{}'.format(test_name, i, trial_count - 1, j, average_count - 1))
            sys.stdout.flush()

    while procs:
        assert len(procs) <= MAX_PROC_COUNT
        wait_on_procs(procs, test_name, trial_count, average_count)

    print()
    sys.stdout.flush()


def schedule_process(proc_args, procs, trial, part, test_name, trial_count, average_count):
    """Wait until there are fewer than MAX_PROC_COUNT procs running then schedule another one."""
    while len(procs) >= MAX_PROC_COUNT:
        exited_proc = wait_on_procs(procs, test_name, trial_count, average_count)

    assert len(procs) <= MAX_PROC_COUNT
    proc = subprocess.Popen(proc_args)
    procs.append({'proc': proc, 'trial': trial, 'part': part})

    
def wait_on_procs(procs, test_name, trial_count, average_count):
    """Wait for a single proc to exit and return the one that did."""
    while procs:
        proc_data = procs.pop(0)
        proc = proc_data['proc']
        trial = proc_data['trial']
        part = proc_data['part']
        try:
            proc.wait(0.5)
            print('< Done with {} trial {}/{} part {}/{}'.format(test_name, trial, trial_count - 1, part, average_count - 1))
            sys.stdout.flush()
            return proc_data
        except:
            procs.append(proc_data)


if __name__ == "__main__":
    _main()
