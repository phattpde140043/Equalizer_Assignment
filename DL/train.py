import numpy as np
import pandas as pd
import tensorflow as tf
import keras as k
import joblib
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

SEED = 12

df = pd.read_csv("features_3_sec.csv")
data = df.iloc[0:, 1:]
y = data['label']
X = data.loc[:, data.columns != 'label']

cols = X.columns
min_max_scaler = MinMaxScaler()
min_max_scaler.fit(X)

joblib.dump(min_max_scaler, "min_max_scaler.save")

X_scaled = min_max_scaler.transform(X)

label_index = dict()
index_label = dict()
for i, x in enumerate(df.label.unique()):
    label_index[x] = i
    index_label[i] = x
df.label = [label_index[l] for l in df.label]

df_shuffle = df.sample(frac=1, random_state=SEED).reset_index(drop=True)
df_shuffle.drop(['filename', 'length'], axis=1, inplace=True)
df_y = df_shuffle.pop('label')
df_X = df_shuffle
X_train, df_test_valid_X, y_train, df_test_valid_y = train_test_split(df_X, df_y, train_size=0.7, random_state=SEED, stratify=df_y)
X_dev, X_test, y_dev, y_test = train_test_split(df_test_valid_X, df_test_valid_y, train_size=0.66, random_state=SEED, stratify=df_test_valid_y)

standard_scaler = StandardScaler()
standard_scaler.fit(X_train)
joblib.dump(standard_scaler, "standard_scaler.save")
X_train = pd.DataFrame(standard_scaler.transform(X_train), columns=X_train.columns)
X_dev = pd.DataFrame(standard_scaler.transform(X_dev), columns=X_train.columns)
X_test = pd.DataFrame(standard_scaler.transform(X_test), columns=X_train.columns)


ACCURACY_THRESHOLD = 0.94

class myCallback(k.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if(logs.get('val_accuracy') > ACCURACY_THRESHOLD):
            print("\n\nStopping training as we have reached %2.2f%% accuracy!" %(ACCURACY_THRESHOLD*100))
            self.model.stop_training = True

def trainModel(model, epochs, optimizer):
    batch_size = 128
    callback = myCallback()
    model.compile(optimizer=optimizer,
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy']
    )
    return model.fit(X_train, y_train, validation_data=(X_dev, y_dev), epochs=epochs,
                     batch_size=batch_size, callbacks=[callback])

def plotHistory(history):
    print("Max. Validation Accuracy",max(history.history["val_accuracy"]))
    pd.DataFrame(history.history).plot(figsize=(12,6))
    plt.show()


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

model_history = trainModel(model=model, epochs=500, optimizer="rmsprop")
model.save_weights('./model.weights.h5')

plotHistory(model_history)