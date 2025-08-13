import numpy as np
import tensorflow as tf
import keras as k
import process

index_label = {0: 'blues', 1: 'classical', 2: 'country', 3: 'disco', 4: 'hiphop', 5: 'jazz', 6: 'metal', 7: 'pop', 8: 'reggae', 9: 'rock'}

model = k.models.Sequential([
    k.layers.Dense(1024, activation='relu', input_shape=(57,)),
    k.layers.Dropout(0.3),

    k.layers.Dense(512, activation='relu'),
    k.layers.Dropout(0.3),

    k.layers.Dense(256, activation='relu'),
    k.layers.Dropout(0.3),

    k.layers.Dense(128, activation='relu'),
    k.layers.Dropout(0.3),

    k.layers.Dense(64, activation='relu'),
    k.layers.Dropout(0.3),

    k.layers.Dense(10, activation='softmax'),
])

model.load_weights('./model.weights.h5')

pred_proba = model.predict(process.features_scaled)
pred_class = np.argmax(pred_proba, axis=1)
print(index_label[pred_class[0]])
