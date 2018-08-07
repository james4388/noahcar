import time
import signal
import logging
from multiprocessing import Process
import multiprocessing
from multiprocessing.managers import SyncManager

from autorc.config import config


class VehicleManager(SyncManager):
    pass


class Vehicle(object):
    ''' Managed non blocking node
        Node can subcribe to channels
    '''
    def __init__(self, name='NoahCar', loglevel=logging.DEBUG,
                 allow_remote=True, address='', port=9999,
                 authkey: bytes=None):
        self.processes = []
        logging.basicConfig(
            level=loglevel,
            format='%(levelname)s(%(processName)s): %(message)s. %(asctime)s')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = name
        self.nodes = []
        # Remote manager
        self.allow_remote = allow_remote
        self.address = address
        self.port = port
        self.authkey = authkey or multiprocessing.current_process().authkey

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

        manager_opts = {}
        if self.allow_remote:
            context_holder = {}
            VehicleManager.register('get_context_holder',
                                    callable=lambda: context_holder)
            manager_opts = {
                'address': (self.address, self.port),
                'authkey': self.authkey
            }
        # Start up nodes process
        with VehicleManager(**manager_opts) as manager:
            self.manager = manager
            self.stop_event = manager.Event()
            self.context = manager.dict(vehicle_name=self.name)
            if self.allow_remote:
                ctx_holder = manager.get_context_holder()
                ctx_holder.update({'context': self.context})

            # TODO: report error if process unable to start. Node failed
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
            if self.allow_remote:
                print('Sync Server: %s:%s' % (self.address, self.port))
                print('Auth:', self.authkey)
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


class RemoteVehicle(Vehicle):
    def __init__(self, loglevel=logging.DEBUG, address='', port=9999,
                 authkey: bytes=None):
        super(RemoteVehicle, self).__init__(
            name='RemoteVehicle', loglevel=loglevel, allow_remote=False,
            address=address, port=port, authkey=authkey)

    def start(self):
        ''' Start the vehicle '''
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)

        # Get main context
        VehicleManager.register('get_context_holder')
        remote = VehicleManager(
            address=(self.address, self.port), authkey=self.authkey)
        remote.connect()
        ctx_holder = remote.get_context_holder()
        self.context = ctx_holder.get('context')

        # Start up nodes process
        with VehicleManager() as manager:
            self.manager = manager
            self.stop_event = manager.Event()

            # TODO: report error if process unable to start. Node failed
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
            if self.allow_remote:
                print('Server: %s:%s' % (self.address, self.port))
                print('Auth:', self.authkey)
            self.main_loop()
            self.stop_event.set()
            self.shutdown()
