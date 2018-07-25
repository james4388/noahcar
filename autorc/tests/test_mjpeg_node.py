import unittest
import time
from multiprocessing import Process, Manager, Event

from autorc.nodes.camera import CVWebCam, PGWebCam
from autorc.nodes.mjpeg import MjpegStreamer


class CVNodeTestCase(unittest.TestCase):
    camera_class = CVWebCam

    def run(self, result=None):
        with Manager() as manager:
            context = manager.dict()
            stop_event = Event()
            cam_node = self.camera_class(context)
            p_cam = Process(target=cam_node.start, args=(stop_event, ))
            p_cam.daemon = True
            p_cam.start()
            mjpeg_node = MjpegStreamer(context)
            p_mjpeg = Process(target=mjpeg_node.start, args=(stop_event, ))
            p_mjpeg.daemon = True
            p_mjpeg.start()
            self.manager = manager
            self.context = context
            super(CVNodeTestCase, self).run(result)
            stop_event.set()

    def test_run_mjpeg_server(self):
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break


class PGNodeTestCase(CVNodeTestCase):
    camera_class = PGWebCam
