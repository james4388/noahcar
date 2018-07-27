import time
import logging
from multiprocessing import Process, Manager, Event


class Vehicle(object):
    ''' Managed non blocking node
        Node can subcribe to channels
    '''
    def __init__(self, name='NoahCar'):
        self.processes = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = name
        self.nodes = []
        self.channels = {}

    def add_node(self, node_cls, inputs: list=None):
        pass

    def main_loop(self):
        while True:
            time.sleep(1)

    def start(self):
        ''' Start the vehicle '''

        # Start up nodes process
        with Manager() as manager:
            self.manager = manager
            self.stop_event = Event()

            for node in self.nodes:
                p = Process(target=node.start)
                p.daemon = True
                self.processes.append(p)
                self.logger.info('Starting %s up', node)
                p.start()

            # Begin main vehicle loop?
            print('Engine started! (Press CTRL+C to quit)')
            try:
                self.main_loop()
            except KeyboardInterrupt:
                pass
            print('Shutting down.')
            self.stop_event.set()
