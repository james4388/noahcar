import time
import logging
from multiprocessing import Process, Manager


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
        while True:
            time.sleep(1)

    def start(self):
        ''' Start the vehicle '''

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
            print('Engine started! (Press CTRL+C to quit)')
            try:
                self.main_loop()
            except KeyboardInterrupt:
                self.stop_event.set()
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
    from autorc.nodes.camera import CVWebCam, PGWebCam
    from autorc.nodes.engine import Engine
    from autorc.nodes.web import WebController
    from autorc.nodes.recorder import SimpleRecorder
    noahcar = Vehicle()
    noahcar.add(CVWebCam)
    noahcar.add(WebController)
    noahcar.add(Engine)
    noahcar.add(SimpleRecorder)
    noahcar.start()
