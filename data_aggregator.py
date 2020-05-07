"""Aggregate sim data and produce results."""


import json
import numpy as np
import os
import os.path
import subprocess
import sys
import util

import stat_v1


PATH = 'collected_data/'


def _main():
    if not os.path.isdir(PATH):
        print('Data path not found: {}'.format(PATH))
        exit(1)

    test_names = os.listdir(PATH)
    print('Found these tests:', ', '.join(test_names))

    tests = {}
    for test_name in test_names:
        tests[test_name] = {}

        test_dir_name = PATH + test_name + '/'
        test_file_names = os.listdir(test_dir_name)
        for test_file_name in test_file_names:
            if test_file_name == 'config':
                continue
            trial, part = test_file_name.split('_')
            assert part.endswith('.json')
            part = part[:-5]

            if trial not in tests[test_name]:
                tests[test_name][trial] = []

            tests[test_name][trial].append(test_dir_name + test_file_name)

    output = {}
    for test_name in tests.keys():
        output[test_name] = {}

        trials = tests[test_name]
        print(test_name)
        for trial in trials.keys():
            output[test_name][trial] = {}

            file_names = trials[trial]
            #print(trial)

            stem_angle_std_devs = []
            random_angle_std_devs = []
            stem_side_std_devs = []
            random_side_std_devs = []

            skip = False
            for file_name in file_names:
                #print(file_name)
                try:
                    output_data_file_name = 'temp.json'
                    stat_v1.public_main(file_name, output_data_file_name)
                    with open(output_data_file_name) as output_file:
                        data = json.loads(output_file.read())
                    stem_angle_std_devs.append(data['STEM_ANGLE_STD_DEV'])
                    random_angle_std_devs.append(data['RANDOM_ANGLE_STD_DEV'])
                    stem_side_std_devs.append(data['STEM_SIDE_STD_DEV'])
                    random_side_std_devs.append(data['RANDOM_SIDE_STD_DEV'])
                except:
                    # Not enough points to get data in all likelihood,
                    # since triangulation has a minimum.
                    print('Couldn\'t get data for', test_name, trial)
                    # Skip the data for a trial if one part cannot be analysed.
                    skip = True
                    break

            if not skip:
                a1 = np.mean(stem_angle_std_devs)
                a2 = np.mean(random_angle_std_devs)
                a3 = np.mean(stem_side_std_devs)
                a4 = np.mean(random_side_std_devs)
                output[test_name][trial]['STEM_ANGLE_STD_DEV'] = a1
                output[test_name][trial]['RANDOM_ANGLE_STD_DEV'] = a2
                output[test_name][trial]['STEM_SIDE_STD_DEV'] = a3
                output[test_name][trial]['RANDOM_SIDE_STD_DEV'] = a4

    print(json.dumps(output))


if __name__ == "__main__":
    _main()