import unittest
import time
from multiprocessing import Process, Manager, Event
from random import random

from autorc.nodes.camera import CVWebCam, PGWebCam
from autorc.nodes.recorder import SimpleRecorder


class CVNodeTestCase(unittest.TestCase):
    camera_class = CVWebCam

    def run(self, result=None):
        with Manager() as manager:
            context = manager.dict()
            stop_event = Event()
            self.stop_event = stop_event
            p_cam = Process(target=self.camera_class.start,
                            args=(context, stop_event, ))
            p_cam.daemon = True
            p_cam.start()
            p_recoder = Process(target=SimpleRecorder.start,
                                args=(context, stop_event, ))
            p_recoder.daemon = True
            p_recoder.start()
            self.manager = manager
            self.context = context
            super(CVNodeTestCase, self).run(result)
            stop_event.set()

    def test_run_mjpeg_server(self):
        self.context['training/record'] = True
        counter = 0
        while counter < 50:
            self.context['user/steering'] = random()
            self.context['user/steering__timestamp'] = time.time()
            self.context['user/throttle'] = random()
            self.context['user/throttle__timestamp'] = time.time()
            counter += 1
            time.sleep(0.1)
        self.stop_event.set()
        time.sleep(2)


class PGNodeTestCase(CVNodeTestCase):
    camera_class = PGWebCam
