#! /usr/bin/env python
''' Main input of program, cli, etc... '''
import os
import argparse
import glob
import importlib

from autorc.config import config


def get_profiles():
    ''' List all vehicle profiles '''
    return [
        os.path.basename(path)[:-3]
        for path in glob.glob(os.path.join(config.PROFILES_ROOT, "*.py"))
        if os.path.isfile(path) and not path.endswith('__init__.py')
    ]


''' ============ ACTIONS ============ '''


def list_profile(args):
    ''' Print all vehicle profiles '''
    print("Available profiles:", ','.join(get_profiles()))
    print("Usage: ./manage.py -p <profile_name> start")


def reset_servo(args):
    ''' Set all servos to 90 degree (middle) position '''
    print('Set servos to 90 degree...')
    from autorc.picar3.Servo import Servo
    for i in range(16):     # 16 pins
        servo = Servo(i)
        servo.setup()
        servo.write(90)


def start(args):
    ''' Run a vehicle profile '''
    profile = args.profile
    mod = importlib.import_module('autorc.profiles.' + profile)
    if not hasattr(mod, 'vehicle'):
        print('Profile', profile, 'does not has vehicle instance')
    else:
        print('Start', profile, 'vehicle.')
        getattr(mod, 'vehicle').start()


ALLOWED_ACTIONS = {
    'reset-servo': reset_servo,
    'list-profile': list_profile,
    'start': start
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Noahcar cli.')

    parser.add_argument('-p', '--profile', default='default',
                        choices=get_profiles(), dest='profile',
                        help='Vehicle profile to load')

    parser.add_argument('action', help='Action to run', nargs='?')

    args = parser.parse_args()

    if not args.action or args.action not in ALLOWED_ACTIONS:
        parser.print_help()
        print("Available actions:")
        for action, method in ALLOWED_ACTIONS.items():
            print(' ', action, method.__doc__)
    else:
        ALLOWED_ACTIONS[args.action](args)
