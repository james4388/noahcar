from io import BytesIO
import time
from autorc.nodes import Node
import numpy as np
from skimage.transform import resize as skresize

'''
    Supported resolution
    160.0 x 120.0
    176.0 x 144.0
    320.0 x 240.0
    352.0 x 288.0
    640.0 x 480.0
    1024.0 x 768.0
    1280.0 x 1024.0
'''


class BaseWebCam(Node):
    '''
        USB webcam interface, get image from camera and update:
            jpeg for client streaming
            size=(width, height): Camera caoture size, also the size
                                  of jpeg frame
            numpy_size: (height, width) image array for deep learning
    '''

    def __init__(self, context,
                 outputs=('cam/image-jpeg', 'cam/image-np'),
                 size=(160, 120), numpy_size=None,
                 framerate=20, **kwargs):
        '''
            size for raw record and jpeg stream size
        '''
        self.size = size
        if (isinstance(numpy_size, (tuple, list)) and
                size[0] < numpy_size[1] or size[1] < numpy_size[0]):
            raise Exception('Capture size must larger than numpy size')
        self.numpy_size = numpy_size
        super(BaseWebCam, self).__init__(
            context, outputs=outputs,
            process_rate=framerate, **kwargs)

    def get_frame(self):
        raise Exception('Not yet implemented')

    def get_jpeg(self, frame):
        raise Exception('Not yet implemented')

    def get_np_array(self, frame):
        raise Exception('Not yet implemented')

    def process_loop(self):
        frame = self.get_frame()
        if frame is not None:
            jpeg = self.get_jpeg(frame)
            np_array = self.get_np_array(frame)
            return jpeg, np_array


class CVWebCam(BaseWebCam):
    ''' USB webcam interface using open CV
    '''
    cam = None      # open CV cam instance

    def __init__(self, context, size=(160, 120), framerate=20,
                 capture_device=0, jpeg_quality=90,
                 use_rgb=True, **kwargs):
        super(CVWebCam, self).__init__(context, size=size, framerate=framerate,
                                       **kwargs)
        self.use_rgb = use_rgb
        self.framerate = framerate
        self.capture_device = capture_device
        self.jpeg_quality = jpeg_quality

    def start_up(self):
        import cv2
        self.cv2 = cv2
        self.cam = cv2.VideoCapture(self.capture_device)
        if self.size:   # Not working or camera is not supported
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.size[0])
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.size[1])
        self.encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality)
        time.sleep(1)   # Camera warm up

    def get_frame(self):
        if self.cam:
            ret, frame = self.cam.read()
            return frame

    def get_jpeg(self, frame):
        if frame is not None:
            ret, jpeg = self.cv2.imencode('.jpg', frame, self.encode_param)
            return jpeg.tostring()

    def get_np_array(self, frame):
        new_frame = frame
        if self.numpy_size:
            # CV resize use col, row (width, height)
            new_frame = self.cv2.resize(
                frame, (self.numpy_size[1], self.numpy_size[0]),
                self.cv2.INTER_LINEAR)
        if self.use_rgb:
            new_frame = self.cv2.cvtColor(new_frame, self.cv2.COLOR_BGR2RGB)
        return new_frame

    def shutdown(self):
        if self.cam:
            self.cam.release()


class PGWebCam(BaseWebCam):
    '''
        USB webcam interface using Pygame
    '''
    def __init__(self, context, size=(160, 120), framerate=20,
                 capture_device=None, jpeg_quality=90,
                 use_bgr=False, **kwargs):
        super(PGWebCam, self).__init__(context, size=size, framerate=framerate,
                                       **kwargs)
        self.use_bgr = use_bgr
        self.framerate = framerate
        self.capture_device = capture_device
        self.jpeg_quality = jpeg_quality

    def start_up(self):
        import pygame
        import pygame.camera
        import pygame.image
        import pygame.surfarray
        from PIL import Image
        self.pygame = pygame
        self.Image = Image
        pygame.init()
        pygame.camera.init()
        try:
            if not self.capture_device:
                cam_list = pygame.camera.list_cameras()
                self.logger.debug(cam_list)
                self.cam = pygame.camera.Camera(cam_list[0], self.size, "RGB")
            else:
                self.cam = pygame.camera.Camera(
                    self.capture_device, self.size, "RGB")
            self.cam.start()
        except Exception as e:
            raise Exception('Camera init error')
        self.blank_surface = pygame.surface.Surface(self.size)
        self.surface = None    # To store image
        time.sleep(1)   # Camera warm up

    def get_frame(self):
        if self.cam and self.cam.query_image():
            self.surface = self.cam.get_image(self.blank_surface)
            # Since pygame cam switch width and height, we have to flip back
            # self.surface = self.pygame.transform.rotate(
            # self.pygame.transform.flip(self.surface, True, False), 90)
            # need resize?
            # pygame.transform.scale(self.surface, self.size)
            frame = self.pygame.surfarray.pixels3d(self.surface)
            # Since numpy rotate image 90 degree, need to use numpy to
            # image transpose back
            return np.transpose(frame, (1, 0, 2))   # HxWxC

    def get_jpeg(self, frame):
        if frame is not None:
            tmpfile = BytesIO()
            img = self.Image.fromarray(frame)
            img.save(tmpfile, format='jpeg')
            return tmpfile.getvalue()

    def get_np_array(self, frame):
        if self.size != self.numpy_size:
            # HxWxD
            return skresize(frame, self.numpy_size, mode='reflect',
                            anti_aliasing=False)
        return frame

    def shutdown(self):
        if self.cam:
            self.cam.stop()
