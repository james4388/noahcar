import os
import uuid
import json
import time
import numpy as np

from autorc.nodes import AsyncNode
from autorc.config import config


class BaseRecorder(AsyncNode):
    ''' Record video feed, steering, throttle in jpeg and json format
    '''
    def __init__(self, context, *,
                 inputs=('cam/image-jpeg', 'user/steering', 'user/throttle'),
                 path=config.TRAINING_SET_ROOT, record_on='training/record',
                 file_format='', session=None, **kwargs):
        super(BaseRecorder, self).__init__(context, inputs=inputs, **kwargs)
        self.path = path
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        self.file_format = file_format
        self.counter = 0
        self.session = session
        if self.session is None:
            self.session = str(uuid.uuid4())
        self.record_path = os.path.join(self.path, self.session)
        try:
            os.makedirs(self.record_path)
        except Exception:
            pass
        if not os.path.isdir(self.record_path):
            raise Exception('Could not create session. Please check write'
                            ' permission')
        self.record_on = record_on

    async def write(image, steering, throttle):
        pass

    async def process_loop(self, image, steering, throttle):
        if self.context.get(self.record_on) is True:
            await self.write(image, steering, throttle)
            self.counter += 1


class SimpleRecorder(BaseRecorder):
    async def write(self, image, steering, throttle):
        # TODO calculate file name format here
        # TODO save image as numpy array instead
        file_name = 'frame-%d-%s' % (self.counter, time.time())
        file_path = os.path.join(self.record_path, file_name)
        with open(file_path + '.jpg', 'wb') as f:
            f.write(image)

        with open(file_path + '.json', 'w') as f:
            json.dump({
                'image': file_name + '.jpg',
                'steering': steering,
                'throttle': throttle
            }, f)


class NPRecorder(BaseRecorder):
    def __init__(self, context, *,
                 inputs=('cam/image-np', 'user/steering', 'user/throttle'),
                 **kwargs):
        super(NPRecorder, self).__init__(context, inputs=inputs, **kwargs)

    async def write(self, image, steering, throttle):
        # TODO calculate file name format here
        # TODO save image as numpy array instead
        file_name = 'frame-%d-%s' % (self.counter, time.time())
        file_path = os.path.join(self.record_path, file_name)
        with open(file_path + '.npz', 'wb') as f:
            f.write(image)

        with open(file_path + '.json', 'w') as f:
            json.dump({
                'image': file_name + '.npz',
                'steering': steering,
                'throttle': throttle
            }, f)
