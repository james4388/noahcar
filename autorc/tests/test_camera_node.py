import unittest
from multiprocessing import Process, Manager, Event
from io import BytesIO

from autorc.nodes import Node
from autorc.nodes.camera import CVWebCam, PGWebCam


class TestCameraNode(Node):
    def __init__(self, context, **kwargs):
        from PIL import Image
        self.counter = 0
        self.counter2 = 0
        self.Image = Image
        super(TestCameraNode, self).__init__(context, {
            'on_jpeg_arrive': CVWebCam.OUT_PUT_JPEG,
            'on_np_arrive': CVWebCam.OUT_PUT_NUMPY
        }, **kwargs)

    def on_jpeg_arrive(self, image):
        self.counter += 1
        self.logger.info('Save frame %d', self.counter)
        f = BytesIO(image)
        try:
            self.Image.open(f)
            self.output('test_frame_%d' % self.counter, 'VALID')
        except Exception:
            self.output('test_frame_%d' % self.counter, 'INVALID')

    def on_np_arrive(self, nparr):
        self.counter2 += 1
        self.logger.info('Frame %d has shape %s', self.counter2, nparr.shape)
        self.output('test_np_%d' % self.counter2, nparr.shape)


class CVNodeTestCase(unittest.TestCase):
    camera_class = CVWebCam

    def run(self, result=None):
        with Manager() as manager:
            context = manager.dict()
            stop_event = Event()
            test_node = TestCameraNode(context)
            cam_node = self.camera_class(context, max_loop=10)
            p_cam = Process(target=cam_node.start, args=(stop_event, ))
            p_test = Process(target=test_node.start, args=(stop_event, ))
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
        for i in range(4):
            self.assertEqual(
                self.context.get('test_frame_%d' % (i + 1)), 'VALID')
            self.assertEqual(
                self.context.get('test_np_%d' % (i + 1)), (64, 64, 3)
            )


class PGNodeTestCase(CVNodeTestCase):
    camera_class = PGWebCam
