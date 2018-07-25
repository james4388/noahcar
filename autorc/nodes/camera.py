from io import BytesIO
import time
from autorc.nodes import Node


class BaseWebCam(Node):
    '''
        USB webcam interface, get image from camera and update:
            jpeg for client streaming
            numpy image array for deep learning
    '''
    OUT_PUT_JPEG = 'cam/image-jpeg'
    OUT_PUT_NUMPY = 'cam/image-np'

    def __init__(self, context, size=(160, 120), framerate=20,
                 numpy_size=(64, 64), **kwargs):
        '''
            size for raw record and jpeg stream size
            numpy_size size of array for deep learning
        '''
        self.size = size
        self.numpy_size = numpy_size
        super(BaseWebCam, self).__init__(context, process_rate=framerate,
                                         **kwargs)

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
            self.outputs({
                self.OUT_PUT_JPEG: jpeg,
                self.OUT_PUT_NUMPY: np_array
            })
        else:
            self.logger.debug('Got empty frame')


class CVWebCam(BaseWebCam):
    ''' USB webcam interface using open CV
    '''
    cam = None      # open CV cam instance

    def __init__(self, context, size=(160, 120), framerate=20,
                 numpy_size=(64, 64), capture_device=0, jpeg_quality=90,
                 use_rgb=True, **kwargs):
        super(CVWebCam, self).__init__(context, size=size, framerate=framerate,
                                       numpy_size=numpy_size, **kwargs)
        self.use_rgb = use_rgb
        self.framerate = framerate
        self.capture_device = capture_device
        self.jpeg_quality = jpeg_quality

    def start_up(self):
        import cv2
        self.cv2 = cv2
        self.cam = cv2.VideoCapture(self.capture_device)
        if self.size:
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
        if self.size and self.size != self.numpy_size:
            # Resize
            new_frame = self.cv2.resize(
                frame, self.numpy_size, self.cv2.INTER_LINEAR)
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
                 numpy_size=(64, 64), capture_device=None, jpeg_quality=90,
                 use_bgr=False, **kwargs):
        super(PGWebCam, self).__init__(context, size=size, framerate=framerate,
                                       numpy_size=numpy_size, **kwargs)
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
            self.surface = self.pygame.transform.rotate(self.surface, 90)
            # need resize?
            # pygame.transform.scale(self.surface, self.size)
            return self.pygame.surfarray.pixels3d(self.surface)

    def get_jpeg(self, frame):
        if frame is not None:
            tmpfile = BytesIO()
            img = self.Image.fromarray(frame)
            img.save(tmpfile, format='jpeg')
            return tmpfile.getvalue()

    def get_np_array(self, frame):
        scaled = self.pygame.transform.scale(self.surface, self.numpy_size)
        return self.pygame.surfarray.pixels3d(scaled)

    def shutdown(self):
        if self.cam:
            self.cam.stop()
