import time
import logging
import asyncio
import typing

__version__ = '0.1'


__all__ = (
    'Node'
)


class Node(object):
    ''' Base class for vehicle nodes
        A node will be run in it own process or managed by main vehicle loop
        Check for new input data by comparing timestamps header
        inputs = {
            'on_image_update': 'image',
            'on_driving': ('steering', 'steering')
        }
        or
        input = ['image', 'steering'] without method will be pass to
        process loop
        same for process
        When image is update (based on timestamp) on_image_update will be call
        image become arg for on_image_update
        on_driving only called when both steering and throttle is updated
    '''
    inputs = None                 # Input call back
    input_timestamps = None       # Cache last input timestamp for updated
    outputs = None                # Output
    max_loop = None               # Use for testing, exit process after loops
    process_rate = 24             # process loop should be call per second
    input_output_mapping = None

    def __init__(self, context, *,
                 inputs: typing.Union[dict, list, tuple]=None,
                 outputs: typing.Union[dict, list, tuple]=None,
                 process_rate=24, max_loop=None, logger=None, **kwargs):
        super(Node, self).__init__()
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.max_loop = max_loop
        self.context = context
        self.input_timestamps = {}
        if (inputs):
            self.inputs = inputs
        if (outputs):
            self.outputs = outputs
        # Convert callback name to class method
        self.input_output_mapping = {}
        self._prepare_mapping(self.inputs, 'inputs')
        self._prepare_mapping(self.outputs, 'outputs')
        process_loop = getattr(self, 'process_loop', None)
        if process_loop and process_loop not in self.input_output_mapping:
            # Process loop just need to run
            self.input_output_mapping[process_loop] = {}

    def _prepare_mapping(self, keys, mtype='inputs'):
        if keys:
            if isinstance(keys, (list, tuple)):
                keys = {'process_loop': keys}
            for cb, args in keys.items():
                if not isinstance(args, (list, tuple)):
                    args = (args, )
                if isinstance(cb, str):
                    cb_method = getattr(self, cb, None)
                    if not callable(cb_method):
                        raise Exception('Method %s does not existed in %s' %
                                        (cb, self.__class__.__name__))
                    if cb_method not in self.input_output_mapping:
                        self.input_output_mapping[cb_method] = {}
                    self.input_output_mapping[cb_method][mtype] = args

    def __repr__(self):
        return self.__class__.__name__

    def make_timestamp_key(self, key):
        return key + '__timestamp'

    def update(self, key, value):
        ''' Write output to current context, add timestamp to track updates '''
        self.updates({key: value})

    def updates(self, data: dict):
        ''' Update multiple key, values '''
        updater = {}
        timestamp = time.time()
        for k, v in data.items():
            updater[k] = v
            updater[self.make_timestamp_key(k)] = timestamp
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

    @classmethod
    def start(cls, context, stop_event, *args, **kwargs):
        self = cls(context, *args, **kwargs)
        self.logger.info('Process %s started!' % self.__class__.__name__)
        self.start_up()
        loop_count = 0
        max_sleep_time = 1.0 / self.process_rate
        mapper = tuple(
            (callback, innout.get('inputs'), innout.get('outputs'))
            for callback, innout in self.input_output_mapping.items()
        )
        while not stop_event.is_set():  # Listen for stop event
            start_time = time.time()
            # Check and call callback on input updated
            if mapper:
                for callback, inputs, outputs in mapper:
                    ret = None
                    if inputs is not None:
                        if self.input_updated(inputs):
                            cbargs = [self.context.get(input)
                                      for input in inputs]
                            ret = callback(*cbargs)
                    else:
                        ret = callback()
                    if ret is not None:
                        if not isinstance(ret, tuple):
                            ret = (ret, )
                        if outputs is not None and len(ret) == len(outputs):
                            self.updates({
                                key: ret[i] for i, key in enumerate(outputs)
                            })
                        else:
                            self.logger.error(
                                'Outputs and keys mismatch in %s', callback)

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
        # TODO enforce callback as coroutine function
        # asyncio.iscoroutinefunction(callback)
        self.loop = loop

    async def process_loop(self, *args):
        pass

    async def start_up(self):
        pass

    async def async_loop(self, stop_event, *args):
        await self.start_up()
        loop_count = 0
        max_sleep_time = 1.0 / self.process_rate
        mapper = tuple(
            (callback, innout.get('inputs'), innout.get('outputs'))
            for callback, innout in self.input_output_mapping.items()
        )
        while not stop_event.is_set():  # Listen for stop event
            start_time = time.time()
            # Check and call callback on input updated
            if mapper:
                for callback, inputs, outputs in mapper:
                    ret = None
                    if inputs:
                        if self.input_updated(inputs):
                            cbargs = [self.context.get(input)
                                      for input in inputs]
                            ret = await callback(*cbargs)
                    else:
                        ret = await callback()
                    if ret is not None:
                        if not isinstance(ret, tuple):
                            ret = (ret, )
                        if outputs and len(ret) == len(outputs):
                            self.updates({
                                key: ret[i] for i, key in enumerate(outputs)
                            })
                        else:
                            self.logger.error(
                                'Outputs and keys mismatch in %s', callback)
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

    @classmethod
    def start(cls, context, stop_event, *args, **kwargs):
        self = cls(context, *args, **kwargs)
        if self.loop is None:
            self.loop = asyncio.get_event_loop()
        self.logger.info('Process %s started!' % self.__class__.__name__)
        self.loop.run_until_complete(self.async_loop(stop_event, *args))
        self.loop.close()
