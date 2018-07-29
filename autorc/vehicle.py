import time
import signal
import logging
import os
from multiprocessing import Process, Manager

from autorc.config import config


class Vehicle(object):
    ''' Managed non blocking node
        Node can subcribe to channels
    '''
    def __init__(self, name='NoahCar', loglevel=logging.DEBUG):
        self.processes = []
        logging.basicConfig(
            level=loglevel,
            format='%(levelname)s(%(processName)s): %(message)s. %(asctime)s')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = name
        self.nodes = []

    def add_node(self, node_cls, *args, **kwargs):
        kwargs['logger'] = self.logger
        self.nodes.append((node_cls, args, kwargs))

    def main_loop(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            return

    def start(self):
        ''' Start the vehicle '''
        #
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)

        # Start up nodes process
        with Manager() as manager:
            self.manager = manager
            self.stop_event = manager.Event()
            self.context = manager.dict(vehicle_name=self.name)

            for node_cls, args, kwargs in self.nodes:
                p = Process(target=node_cls.start,
                            args=(self.context, self.stop_event, *args),
                            kwargs=kwargs)
                p.daemon = True
                self.processes.append(p)
                self.logger.info('Starting %s up', node_cls)
                p.start()

            # Begin main vehicle loop?
            signal.signal(signal.SIGINT, original_sigint_handler)
            print('Engine started! (Press CTRL+C to quit)')
            self.main_loop()
            self.stop_event.set()
            self.shutdown()

    def shutdown(self):
        print('Shutting down.')
        # Waiting for all process to stop on it self
        time.sleep(2)
        for p in self.processes:
            try:
                p.terminate()
            except Exception as ex:
                self.logger.error(ex)
                pass


if __name__ == '__main__':
    from autorc.nodes.camera import CVWebCam  # , PGWebCam
    from autorc.nodes.engine import Engine
    from autorc.nodes.web import WebController
    from autorc.nodes.recorder import SimpleRecorder
    from autorc.nodes.pilot import KerasSteeringPilot
    noahcar = Vehicle()
    noahcar.add_node(CVWebCam)
    noahcar.add_node(WebController)
    noahcar.add_node(Engine)
    noahcar.add_node(SimpleRecorder)
    noahcar.add_node(
        KerasSteeringPilot,
        model_path=os.path.join(config.MODELS_ROOT, 'donkey2.mdl'))
    noahcar.start()
