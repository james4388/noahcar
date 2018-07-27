from autorc.nodes import Node
from autorc.config import config
from autorc.utils import range_map

from autorc.picar3.hardware import PCA9685
from autorc.picar3.hardware.front_wheels import Front_Wheels
from autorc.picar3.hardware.back_wheels import Back_Wheels


class Engine(Node):
    def __init__(self, context, **kwargs):
        super(Engine, self).__init__(context, **kwargs)
        # Test car
        pwm = PCA9685.PWM(bus_number=1)
        pwm.setup()
        pwm.frequency = 60
        self.pwm = pwm
        self.fw = Front_Wheels()
        self.bw = Back_Wheels()
        self.steering = None
        self.throttle = None

    def process_loop(self, *args):
        if self.input_updated(('user/steering', )):
            steering_percent = self.context.get('user/steering', 0)
            steering = range_map(
                steering_percent, -1, 1, 70, 110, int_only=True)
            self.fw.turn(steering)
        if self.input_updated(('user/throttle', )):
            throttle_percent = self.context.get('user/throttle', 0)
            throttle = range_map(
                abs(throttle_percent), 0, 1, 50, 100, int_only=True)
            self.bw.speed = throttle
            if throttle_percent > 0:
                self.bw.forward()
            elif throttle_percent < 0:
                self.bw.backward()
            else:
                self.bw.stop()
