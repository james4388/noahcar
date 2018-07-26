import time
import logging
import asyncio

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
    input_callback = None         # Input call back
    input_timestamps = None       # Cache last input timestamp for updated
    output_cache = None                 # Output cache
    inititalized = False
    max_loop = None               # Use for testing, exit process after loops
    process_rate = 24             # process loop should be call per second

    def __init__(self, context, *, input_callback: dict=None, process_rate=24,
                 max_loop=None, **kwargs):
        super(Node, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_loop = max_loop
        self.context = context
        self.input_timestamps = {}
        if (input_callback):
            self.input_callback = input_callback
        # Convert callback name to class method
        if self.input_callback:
            for cb, inputs in list(self.input_callback.items()):
                if not isinstance(inputs, (list, tuple)):
                    inputs = (inputs, )
                if isinstance(cb, str):
                    cb_method = getattr(self, cb, None)
                    if not callable(cb_method):
                        raise Exception('Callback %s does not existed in %s' %
                                        (cb, self.__class__.__name__))
                    self.input_callback[cb_method] = inputs
                    del self.input_callback[cb]
        self.inititalized = True

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
                self.input_timestamps.get(key_ts, -1) >=
                    self.context.get(key_ts, 0)):
                return False
            updated_ts[key_ts] = self.context.get(key_ts, 0)
        self.input_timestamps.update(updated_ts)
        return True

    def process_loop(self, *args):
        ''' This method is call by main loop to update data '''
        pass

    def start_up(self):
        pass

    # Overwrite as you own risk
    def start(self, stop_event, *args):
        if not self.inititalized:
            raise Exception(
                'Node base class has not been propper init. '
                'Call super() from %s.__init__' % self.__class__.__name__)
        self.logger.info('Process %s started!' % self.__class__.__name__)
        self.start_up()
        loop_count = 0
        max_sleep_time = 1.0 / self.process_rate
        while not stop_event.is_set():  # Listen for stop event
            start_time = time.time()
            # Check and call callback on input updated
            if self.input_callback:
                for callback, inputs in self.input_callback.items():
                    if self.input_updated(inputs):
                        cbargs = [self.context.get(input) for input in inputs]
                        callback(*cbargs)

            self.process_loop(*args)
            loop_count += 1

            if self.max_loop and self.max_loop <= loop_count:
                self.logger.info('Max loop exceeded, Exit')
                break

            sleep_time = max_sleep_time - (time.time() - start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

        if callable(getattr(self, 'shutdown', None)):
            self.shutdown()

    def shutdown(self):
        ''' Free all resource '''
        self.logger.info('Shutting down.')
        self.output = None
        self.input_callback = None
        self.input_timestamps = None


class AsyncNode(Node):
    ''' Just like Node but using async io '''
    def __init__(self, context, *, loop=None, **kwargs):
        super(AsyncNode, self).__init__(context, **kwargs)
        self.loop = loop

    async def process_loop(self, *args):
        pass

    async def start_up(self):
        pass

    async def main_loop(self, stop_event, *args):
        await self.start_up()
        loop_count = 0
        max_sleep_time = 1.0 / self.process_rate
        while not stop_event.is_set():  # Listen for stop event
            start_time = time.time()
            # Check and call callback on input updated
            if self.input_callback:
                for callback, inputs in self.input_callback.items():
                    if self.input_updated(inputs):
                        cbargs = [self.context.get(input) for input in inputs]
                        callback(*cbargs)

            await self.process_loop(*args)
            loop_count += 1

            if self.max_loop and self.max_loop <= loop_count:
                self.logger.info('Max loop exceeded, Exit')
                break

            sleep_time = max_sleep_time - (time.time() - start_time)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

        if callable(getattr(self, 'shutdown', None)):
            await self.shutdown()

    async def shutdown(self):
        ''' Free all resource '''
        self.logger.info('Shutting down.')
        self.output = None
        self.input_callback = None
        self.input_timestamps = None

    def start(self, stop_event, *args):
        if not self.inititalized:
            raise Exception(
                'Node base class has not been propper init. '
                'Call super() from %s.__init__' % self.__class__.__name__)
        if self.loop is None:
            self.loop = asyncio.get_event_loop()
        self.logger.info('Process %s started!' % self.__class__.__name__)
        self.loop.run_until_complete(self.main_loop(stop_event, *args))
        self.loop.close()
