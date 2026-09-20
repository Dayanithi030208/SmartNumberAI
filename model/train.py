import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np


print("TensorFlow version:", tf.__version__)
print("Loading MNIST dataset...")


# -----------------------------------
# 1. Load MNIST
# -----------------------------------

(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

print("Training samples:", len(x_train))
print("Testing samples:", len(x_test))


# -----------------------------------
# 2. Normalize images
# -----------------------------------

x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0


# CNN expects:
# (samples, height, width, channels)

x_train = np.expand_dims(x_train, -1)
x_test = np.expand_dims(x_test, -1)


print("Input shape:", x_train.shape)


# -----------------------------------
# 3. Build CNN
# -----------------------------------

model = keras.Sequential([

    layers.Input(shape=(28, 28, 1)),

    layers.Conv2D(32, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(64, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),

    layers.Flatten(),

    layers.Dense(128, activation="relu"),

    layers.Dropout(0.3),

    layers.Dense(10, activation="softmax")
])


# -----------------------------------
# 4. Compile
# -----------------------------------

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


model.summary()


# -----------------------------------
# 5. Train
# -----------------------------------

print("\nTraining model...\n")


history = model.fit(
    x_train,
    y_train,
    epochs=5,
    batch_size=128,
    validation_split=0.1
)


# -----------------------------------
# 6. Evaluate
# -----------------------------------

test_loss, test_accuracy = model.evaluate(
    x_test,
    y_test,
    verbose=0
)


print("\n-----------------------------")
print("MODEL EVALUATION")
print("-----------------------------")

print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy * 100:.2f}%")


# -----------------------------------
# 7. Save model
# -----------------------------------

model.save("model/digit_model.keras")

print("\nModel saved successfully!")
print("Location: model/digit_model.keras")