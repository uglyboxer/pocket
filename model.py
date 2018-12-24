

import numpy as np

import tensorflow as tf
import tensorflow_hub as hub

from keras import backend as K
from keras.engine import Layer
from keras.models import Model
from keras.layers import Dense, Input, LSTM
from keras.callbacks import EarlyStopping, ModelCheckpoint

from data import load_data, PAD_STRING, MAX_LEN, NUM_CATEGORIES


class ElmoEmbeddingLayer(Layer):
    def __init__(self, **kwargs):
        self.dimensions = 1024
        super(ElmoEmbeddingLayer, self).__init__(trainable=True, **kwargs)

    def build(self, input_shape):
        self.elmo = hub.Module('https://tfhub.dev/google/elmo/2', trainable=True,
                               name="{}_module".format(self.name))

        self.trainable_weights += K.tf.trainable_variables(scope="^{}_module/.*".format(self.name))
        super(ElmoEmbeddingLayer, self).build(input_shape)

    def call(self, x, mask=None):
        lengths = K.cast(K.argmax(K.cast(K.equal(x, PAD_STRING), 'uint8')), 'int32')
        result = self.elmo(inputs=dict(tokens=x, sequence_len=lengths),
                      as_dict=True,
                      signature='tokens',
                      )['elmo']
        return result

    def compute_mask(self, inputs, mask=None):
        return K.not_equal(inputs, PAD_STRING)

    def compute_output_shape(self, input_shape):
        return input_shape + (self.dimensions,)


x_train, y_train, x_test, y_test, IDX_TO_LABEL, LABEL_TO_IDX = load_data()
_input = Input((MAX_LEN,), dtype=tf.string)
x = ElmoEmbeddingLayer()(_input)
x = LSTM(100, return_sequences=True)(x)
x = LSTM(100)(x)
x = Dense(NUM_CATEGORIES)(x)
model = Model(inputs=_input, outputs=x)
model.compile(loss='categorical_crossentropy', optimizer='RMSProp', metrics=['acc'])
model.fit(x_train, y_train, epochs=10, validation_split=0.2, callbacks=[EarlyStopping(patience=4)])
