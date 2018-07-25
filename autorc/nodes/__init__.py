import time
import logging

__version__ = '0.1'


__all__ = (
    'Node'
)


class Node(object):
    ''' Base class for vehicle nodes
        A node will be run in it own process or managed by main vehicle loop
        Check for new input data by comparing timestamps header
        input_callback = [
            'on_image_update': 'image',
            'on_driving': ('steering', 'steering')
        ]
        When image is update (based on timestamp) on_image_update will be call
        image become arg for on_image_update
        on_driving only called when both steering and throttle is updated
    '''
    __input_callback = None         # Input call back
    __input_timestamps = None       # Cache last input timestamp for updated
    __output = None                 # Output cache
    __init = False
    __max_loop = None               # Use for testing, exit process after loops
    __process_rate = 24             # process loop should be call per second

    def __init__(self, context, input_callback: dict=None, process_rate=24,
                 max_loop=None, **kwargs):
        super(Node, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__max_loop = max_loop
        self.context = context
        self.__input_timestamps = {}
        if (input_callback):
            self.__input_callback = input_callback
        # Convert callback name to class method
        if self.__input_callback:
            for cb, inputs in list(self.__input_callback.items()):
                if not isinstance(inputs, (list, tuple)):
                    inputs = (inputs, )
                if isinstance(cb, str):
                    cb_method = getattr(self, cb, None)
                    if not callable(cb_method):
                        raise Exception('Callback %s does not existed in %s' %
                                        (cb, self.__class__.__name__))
                    self.__input_callback[cb_method] = inputs
                    del self.__input_callback[cb]
        self.__init = True

    def make_timestamp_key(self, key):
        return key + '__timestamp'

    def output(self, key, value):
        ''' Write output to current context, add timestamp to track updates '''
        key_timestamp = self.make_timestamp_key(key)
        self.context.update({
            key: value,
            key_timestamp: time.time()
        })

    def outputs(self, data: dict):
        ''' Update multiple key, values '''
        updater = {}
        timestamp = time.time()
        for k, v in data.items():
            updater[k] = v
            updater[k + '__timestamp'] = timestamp
        self.context.update(updater)

    def input_updated(self, inputs):
        if not isinstance(inputs, (list, tuple)):
            inputs = (inputs, )
        updated_ts = {}
        for key in inputs:
            key_ts = self.make_timestamp_key(key)
            if (key not in self.context or
                self.__input_timestamps.get(key_ts, -1) >=
                    self.context.get(key_ts, 0)):
                return False
            updated_ts[key_ts] = self.context.get(key_ts, 0)
        self.__input_timestamps.update(updated_ts)
        return True

    def process_loop(self, *args):
        ''' This method is call by main loop to update data '''
        pass

    def start_up(self):
        pass

    # Overwrite as you own risk
    def start(self, stop_event, *args):
        if not self.__init:
            raise Exception(
                'Node base class has not been propper init. '
                'Call super() from %s.__init__' % self.__class__.__name__)
        self.logger.info('Process %s started!' % self.__class__.__name__)
        self.start_up()
        loop_count = 0
        max_sleep_time = 1.0 / self.__process_rate
        while not stop_event.is_set():  # Listen for stop event
            start_time = time.time()
            # Check and call callback on input updated
            if self.__input_callback:
                for callback, inputs in self.__input_callback.items():
                    if self.input_updated(inputs):
                        cbargs = [self.context.get(input) for input in inputs]
                        callback(*cbargs)

            self.process_loop(*args)
            loop_count += 1

            if self.__max_loop and self.__max_loop <= loop_count:
                self.logger.info('Max loop exceeded, Exit')
                break

            sleep_time = max_sleep_time - (time.time() - start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

        if callable(getattr(self, 'shutdown', None)):
            self.shutdown()
    start.__do_not_over_write__ = True      # Overwrite as you own risk

    def shutdown(self):
        ''' Free all resource '''
        self.logger.info('Shutting down.')
        self.output = None
        self.__input_callback = None
        self.__input_timestamps = None
