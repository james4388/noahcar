import cv2
import time
from datetime import datetime

from base import Component


class WebCam(Component):
    ''' USB webcam interface '''
    def __init__(self, size=(160, 120), framerate=20):
        self.cam = cv2.VideoCapture(0)
        if size:
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
        self.framerate = framerate

    def process(self, *args, **kwargs):
        if self.cam:
            start = datetime.now()
            ret, frame = self.cam.read()
            stop = datetime.now()
            s = 1 / self.framerate - (stop - start).total_seconds()
            if s > 0:
                time.sleep(s)   # Drop frame
            return frame

    def shutdown(self):
        self.cam.release()
