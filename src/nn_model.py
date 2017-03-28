import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from full_model import main_engine_parallel, csv_batch_extractor
from helper_tools import shuffler


#########################################
############# Keras import ##############
#########################################

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D, Conv2D
from keras.utils import np_utils
from keras.datasets import mnist


#########################################
############# Helper tools ##############
#########################################

def train_test_snippets(X, y):
    '''
    Takes in buckets of snippets each representing a song, splitting them into
    training and test sets and then flattening the arrays.
    '''
    X_train_songs, X_test_songs, y_train_songs, y_test_songs = train_test_split(X, y)
    X_train = reduce(lambda x, y: np.concatenate((x,y)), X_train_songs)
    X_test = reduce(lambda x, y: np.concatenate((x,y)), X_test_songs)
    y_train = reduce(lambda x, y: np.concatenate((x,y)), y_train_songs)
    y_test = reduce(lambda x, y: np.concatenate((x,y)), y_test_songs)
    return X_train, X_test, y_train, y_test


if __name__ == '__main__':
    #########################################
    ############# Loading data ##############
    #########################################
    X, y = main_engine_parallel('../data/pickles/full_songs/', splits=120, song_limit=100, artist_limit=2, n_mfcc=8, full_mfccs=True)

    X_train, X_test, y_train, y_test = train_test_snippets(X, y)

    X_train = X_train.reshape(X_train.shape[0], 1, 8, 44)
    X_test = X_test.reshape(X_test.shape[0], 1, 8, 44)

    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')

    y_train = np_utils.to_categorical(y_train, 2)
    y_test = np_utils.to_categorical(y_test, 2)

    #########################################
    ############# Building CNN ##############
    #########################################

    model = Sequential()

    model.add(Conv2D(20, (3, 3), activation='tanh', input_shape=(1,8,44), dim_ordering="th"))

    model.add(Conv2D(20, (3, 3), activation='tanh'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(100, activation='tanh'))
    model.add(Dropout(0.5))
    model.add(Dense(2, activation='softmax'))


    model.compile(loss='categorical_crossentropy',
                optimizer='adam',
                metrics=['accuracy'])

    model.fit(X_train, y_train,
              batch_size=32, epochs=10, verbose=1)

    print model.evaluate(X_test, y_test)