''' Keras model for auto pilot '''
import os
import numpy as np

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
                 input_shape=(160, 120, 3), preprocess_input=None, **kwargs):
        super(KerasSteeringPilot, self).__init__(context, **kwargs)
        self.model = None
        self.input_shape = input_shape
        self.model_path = model_path
        self.preprocess_input = preprocess_input
        self.get_model(model_path)

    def get_model(self, model_path=None):
        if model_path and os.path.isfile(model_path):
            from keras.models import load_model
            self.model = load_model(model_path)
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
            if self.preprocess_input:
                inp = self.preprocess_input(image)
            return self.decode_label(
                self.model.predict(np.array([inp]))
            )
