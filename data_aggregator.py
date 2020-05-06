"""Aggregate sim data and produce results."""


import json
import os
import os.path
import subprocess
import sys
import util


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

            #if test_name not in tests:
            #    tests[test_name] = {}

            if trial not in tests[test_name]:
                tests[test_name][trial] = []

            tests[test_name][trial].append(test_dir_name + test_file_name)

    for test_name in tests.keys():
        trials = tests[test_name]
        print(test_name)
        for trial in trials.keys():
            file_names = trials[trial]
            print(trial)
            for file_name in file_names:
                print(file_name)


if __name__ == "__main__":
    _main()