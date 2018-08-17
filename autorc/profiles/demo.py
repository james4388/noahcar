import os
from autorc.config import config
from autorc.vehicle import Vehicle
from autorc.nodes.camera import CVWebCam  # , PGWebCam
from autorc.nodes.engine import Engine
from autorc.nodes.web import WebController
from autorc.nodes.recorder import SimpleRecorder
from autorc.nodes.pilot import KerasSteeringPilot


vehicle = Vehicle()
vehicle.add_node(CVWebCam, size=(320, 240), jpeg_size=(160, 160),
                 numpy_size=(160, 160), disable_numpy_stream=True)
vehicle.add_node(WebController)
vehicle.add_node(Engine)
vehicle.add_node(SimpleRecorder)
vehicle.add_node(
    KerasSteeringPilot, camera_feed='cam/image-jpeg', camera_feed_jpeg=True,
    input_shape=(160, 160, 3),
    model_path=os.path.join(config.MODELS_ROOT, 'donkey2-lines.mdl'),
    prewarm_model=True)
