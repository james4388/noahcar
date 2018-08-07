import json
import importlib
import logging
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

# ======= DEFAULT CONFIG GOES HERE ============
''' Default car config
    will be override with user config.json
'''

''' These setting only good for picar setup, other hardware may require
    different settings. These setup may be moved to actuators controller later
'''
FRONT_WHEEL_CHANNEL = 0             # Front wheel pin channel
LEFT_REAR_WHEEL_CHANNEL = 17        # Rear wheel pin channel
RIGHT_REAR_WHEEL_CHANNEL = 27       # Rear wheel pin channel
LEFT_REAR_WHEEL_PWM = 4
RIGHT_REAR_WHEEL_PWM = 5
LEFT_REAR_WHEEL_DIR_OFFSET = 1      # Turning direction
RIGHT_REAR_WHEEL_DIR_OFFSET = 1     # Turning direction

PWM_MIN = 0                 # Pulse width
PWM_MAX = 4095
PWM_BUS_NUMBER = 1          # PWM bus pin
PWM_FREQUENCY = 60          # pulse width modulation frequency


MIN_SPEED = 40              # Speed range
MAX_SPEED = 100
MIN_TURN_ANGLE = 70         # LEFT turn
MAX_TURN_ANGLE = 110        # RIGHT turn
TURN_OFFSET = 0

# Web controller
WEB_CONTROLLER_HOST = '0.0.0.0'
WEB_CONTROLLER_PORT = 8080
WEB_CONTROLLER_COLLECT_STATIC = False   # Do not collect static before run
# SECRET_KEY Must be 32 chars
WEB_CONTROLLER_SECRET_KEY = 'Very secret KEY, keep safe !@#%*'
SESSION_KEY = 'session_key'

# Training set location
TRAINING_SET_ROOT = os.path.join(BASE_DIR, 'training-set')
MODELS_ROOT = os.path.join(BASE_DIR, 'models')
PROFILES_ROOT = os.path.join(BASE_DIR, 'profiles')
# ========== END DEFAULT CONFIG ===============


class Config(object):
    ''' Load config from module or in json format '''
    def __init__(self, *, config_module=None, config_file=None):
        if config_module:
            mod = importlib.import_module(config_module)
            for setting in dir(mod):
                if setting.isupper():
                    setattr(self, setting, getattr(mod, setting))
        if config_file:
            try:
                with open(config_file) as f:
                    mod = json.load(f)
                    for setting, value in mod.items():
                        if setting.isupper():
                            setattr(self, setting, value)
            except (FileNotFoundError, ValueError) as ex:
                logger.warning('Config file %s has invalid format or file does'
                               ' not exist. Using default settings. '
                               'Exception: %s', config_file, ex)


config = Config(config_module=__name__, config_file=os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'config.json'))
