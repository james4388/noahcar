''' Keras model for auto pilot '''
import os
import numpy as np
from io import BytesIO

from autorc.nodes import Node


class PilotBase(Node):

    def __init__(self, context, camera_feed='cam/image-np',
                 outputs=('pilot/throttle', 'pilot/steering'),
                 pilot_on='pilot/engage',
                 **kwargs):
        inputs = {
            'process_loop': camera_feed,
            'on_pilot_enable': pilot_on
        }
        super(PilotBase, self).__init__(
            context, inputs=inputs, outputs=outputs, **kwargs)
        self.enabled = False

    def on_pilot_enable(self, value):
        self.enabled = value

    def predict(self, image):
        raise Exception('Not yet implement')

    def process_loop(self, image):
        if self.enabled:
            return self.predict(image)


class KerasSteeringPilot(PilotBase):
    ''' Donkey based '''
    def __init__(self, context, model_path=None,
                 input_shape=(160, 120, 3), preprocess_input=None,
                 prewarm_model=False, camera_feed_jpeg=False, **kwargs):
        super(KerasSteeringPilot, self).__init__(context, **kwargs)
        from keras.preprocessing.image import load_img, img_to_array
        self.model = None
        self.input_shape = input_shape
        self.model_path = model_path
        self.preprocess_input = preprocess_input
        self.prewarm_model = prewarm_model
        self.camera_feed_jpeg = camera_feed_jpeg
        self.get_model(model_path)
        self.load_img = load_img
        self.img_to_array = img_to_array

    def get_model(self, model_path=None):
        if model_path and os.path.isfile(model_path):
            from keras.models import load_model
            self.logger.info('Loading keras model %s' % model_path)
            self.model = load_model(model_path)
            self.logger.info('Model ready')
            if self.prewarm_model:
                self.logger.info('Prewarm model')
                image = np.zeros((1, *self.input_shape))
                self.model.predict(image)
                self.logger.info('Model warmed')
        if self.model is None:
            from keras.models import Model
            from keras.layers import (
                Input, Dense, Flatten, Convolution2D, Dropout
            )

            img_in = Input(shape=self.input_shape, name='input')
            x = Convolution2D(24, (5, 5), strides=(2, 2), activation='relu',
                              name='conv1')(img_in)
            x = Convolution2D(32, (5, 5), strides=(2, 2), activation='relu',
                              name='conv2')(x)
            x = Convolution2D(64, (5, 5), strides=(2, 2), activation='relu',
                              name='conv3')(x)
            x = Convolution2D(64, (3, 3), strides=(2, 2), activation='relu',
                              name='conv4')(x)
            x = Convolution2D(64, (3, 3), strides=(1, 1), activation='relu',
                              name='conv5')(x)
            x = Flatten(name='flattened')(x)
            x = Dense(100, activation='relu', name='dense1')(x)
            x = Dropout(.1)(x)
            x = Dense(50, activation='relu', name='dense2')(x)
            x = Dropout(.1)(x)
            angle_out = Dense(21, activation='softmax', name='angle_out')(x)

            model = Model(inputs=[img_in], outputs=[angle_out])
            model.compile(optimizer='adam',
                          loss={'angle_out': 'categorical_crossentropy'},
                          loss_weights={'angle_out': 0.9},
                          metrics=['accuracy'])

            self.model = model
        return self.model

    def encode_label(self, throttle, steering):
        ''' Transform from angle [-1, 1] to 21 classes of steering angle '''
        y = np.zeros(21)
        index = round((steering + 1) / (2 / 20))
        y[index] = 1
        return y, None

    def decode_label(self, predict):
        # No throttle for now
        index = np.argmax(predict)
        return None, index * (2 / 20) - 1

    def predict(self, image):
        if self.model is not None:
            inp = image
            if self.camera_feed_jpeg:
                bytes = BytesIO(inp)
                inp = self.img_to_array(
                    self.load_img(bytes, target_size=self.input_shape[:-1]))
            if self.preprocess_input:
                # np.asarray(img, dtype=backend.floatx())
                inp = self.preprocess_input(inp.astype(np.float32))
            return self.decode_label(
                self.model.predict(np.array([inp]))
            )
