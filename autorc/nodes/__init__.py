import time
import logging

__version__ = '0.1'


__all__ = (
    'Node',
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

    def __init__(self, context, input_callback: dict=None, **kwargs):
        self.logger = logging.getLogger(__name__)
        super(Node, self).__init__()
        self.context = context
        self.__input_timestamps = {}
        if (input_callback):
            self.__input_callback = input_callback
        # Convert callback name to class method
        for cb in self.__input_callback.keys():
            cb_method = getattr(self, cb, None)
            if not callable(cb_method):
                raise Exception('Callback %s does not existed in %s' % (
                    cb, self.__class__.__name__))
            self.__input_callback[cb_method] = self.__input_callback[cb]
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

    # Overwrite as you own risk
    def start(self, stop_event, *args):
        if not self.__init:
            raise Exception(
                'Node base class has not been propper init. '
                'Call super() from %s.__init__' % self.__class__.__name__)
        self.logger.debug('Process %s started!' % self.__class__.__name__)
        while not stop_event.is_set():  # Listen for stop event
            # Check and call callback on input updated
            for callback, inputs in self.__input_callback.items():
                if self.input_updated(inputs):
                    cbargs = [self.context.get(input) for input in inputs]
                    callback(*cbargs)

            self.process_loop(*args)

        if callable(getattr(self, 'shutdown', None)):
            self.shutdown()
    start.__do_not_over_write__ = True      # Overwrite as you own risk

    def shutdown(self):
        ''' Free all resource '''
        self.output = None
