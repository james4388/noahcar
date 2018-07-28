import unittest
from multiprocessing import Process, Manager, Event
from io import BytesIO

from autorc.nodes import Node
from autorc.nodes.camera import CVWebCam, PGWebCam

try:
    import pygame
    from pygame import _camera
    pycam_test = True
except ImportError:
    pycam_test = False


class TestCameraNode(Node):
    def __init__(self, context, **kwargs):
        from PIL import Image
        self.counter = 0
        self.counter2 = 0
        self.Image = Image
        super(TestCameraNode, self).__init__(context, inputs={
            'on_jpeg_arrive': 'cam/jpeg',
            'on_np_arrive': 'cam/np'
        }, outputs={
            'on_jpeg_arrive': 'tested_frame'
        }, **kwargs)

    def on_jpeg_arrive(self, image):
        self.counter += 1
        self.logger.info('Save frame %d', self.counter)
        f = BytesIO(image)
        try:
            self.Image.open(f)
            self.update('test_frame_%d' % self.counter, 'VALID')
        except Exception:
            self.update('test_frame_%d' % self.counter, 'INVALID')
        return self.counter

    def on_np_arrive(self, nparr):
        self.counter2 += 1
        self.logger.info('Frame %d has shape %s', self.counter2, nparr.shape)
        self.update('test_np_%d' % self.counter2, nparr.shape)


class CVNodeTestCase(unittest.TestCase):
    camera_class = CVWebCam

    def run(self, result=None):
        with Manager() as manager:
            context = manager.dict()
            stop_event = Event()
            p_cam = Process(
                target=self.camera_class.start,
                args=(context, stop_event),
                kwargs={'max_loop': 10, 'numpy_size': (64, 64),
                        'outputs': ('cam/jpeg', 'cam/np')}
            )
            p_test = Process(
                target=TestCameraNode.start, args=(context, stop_event, ))
            p_test.daemon = True
            p_test.start()
            p_cam.daemon = True
            p_cam.start()
            p_cam.join()
            self.manager = manager
            self.context = context
            super(CVNodeTestCase, self).run(result)
            stop_event.set()

    def test_capture_image(self):
        tested_frame = self.context.get('tested_frame', -1)
        self.assertEqual(tested_frame > 0, True)
        for i in range(tested_frame):
            self.assertEqual(
                self.context.get('test_frame_%d' % (i + 1)), 'VALID')
            self.assertEqual(
                self.context.get('test_np_%d' % (i + 1)), (64, 64, 3)
            )


class PGNodeTestCase(CVNodeTestCase):
    camera_class = PGWebCam

    @unittest.skipIf(not pycam_test, 'Pygame is not present')
    def run(self, result=None):
        super(PGNodeTestCase, self).run(result)
