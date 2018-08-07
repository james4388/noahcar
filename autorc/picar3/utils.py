from __future__ import print_function

from autorc.picar3 import constants


def get_pi_revision():
    ''' Gets the version number of the Raspberry Pi board '''
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Revision'):
                    try:
                        revision = line.split(':')[1].strip()
                        return constants.RPI_REVISION_MODEL[revision]
                    except KeyError:
                        print("Unrecognize Pi revision module number: %s" %
                              revision)
    except IOError as ex:
        print(ex)
    return None


def get_bus_number(pi_revision):
    ''' Return bus number based on pi version '''
    pi_revision = pi_revision or get_pi_revision()
    if pi_revision in {constants.RPI_MODEL_ZERO, constants.RPI_MODEL_B,
                       constants.RPI_MODEL_A, constants.RPI_MODEL_AP}:
        return 0
    elif pi_revision in {constants.RPI_MODEL_BP, constants.RPI_2_MODEL_B,
                         constants.RPI_3_MODEL_B, constants.RPI_3_MODEL_BP}:
        return 1
