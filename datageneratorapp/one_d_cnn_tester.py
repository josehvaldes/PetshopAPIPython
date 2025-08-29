import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import random


# --- 1. Configuration ---
MODEL_PATH = './one_d_cnn_model.keras'
TEST_DATA_PATH = './data/mitbih_test.csv' # Make sure you have this file
# Define the class names based on the dataset description
CLASS_NAMES = ['Normal Beat (N)', 
               'Abnormal Beat (N)']

# --- 2. Load the Pre-trained Model ---
print(f"Loading model from: {MODEL_PATH}")
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully!")
    model.summary()
except Exception as e:
    print(f"Error loading model: {e}")
    exit()


# --- 3. Load and Prepare the Test Data ---
print(f"\nLoading test data from: {TEST_DATA_PATH}")

X_test_loaded = pd.read_csv("./data/ptbdb_test_features.csv", header=None).values.reshape(-1, 187, 1)
y_test_loaded = pd.read_csv("./data/ptbdb_test_labels.csv", header=None).values.flatten()

print(f"Test data shape: {X_test_loaded.shape}")
print(f"Test labels shape: {y_test_loaded.shape}")

# --- 4. Evaluate the Model on the Entire Test Set ---
print("\nEvaluating model performance on the test set...")

# Get raw predictions (probabilities for each class)
y_pred_probs = model.predict(X_test_loaded)
# Convert probabilities to class labels (the index with the highest probability)
y_pred = np.argmax(y_pred_probs, axis=1)

# Generate and print the classification report
print("\nClassification Report:")

print(classification_report(y_test_loaded, y_pred, target_names=CLASS_NAMES))
# Generate and visualize the confusion matrix
print("\nConfusion Matrix:")
cm = confusion_matrix(y_test_loaded, y_pred)
print(cm)

# Plotting the confusion matrix for better visualization
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
plt.title('Confusion Matrix')
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.show(block =False)


# --- 5. Test with a Single Random Sample ---
print("\n--- Testing on a single random sample ---")

# Select a random index from the test set
random_index = random.randint(0, len(X_test_loaded) - 1)
single_sample = X_test_loaded[random_index]
true_label_index = int(y_test_loaded[random_index])

# The model expects a batch of data, so we add an extra dimension
single_sample_batch = np.expand_dims(single_sample, axis=0)

# Make a prediction
prediction_probs = model.predict(single_sample_batch)
predicted_label_index = np.argmax(prediction_probs)

# Get the class names
true_label_name = CLASS_NAMES[true_label_index]
predicted_label_name = CLASS_NAMES[predicted_label_index]

print(f"Random sample index: {random_index}")
print(f"True Label: {true_label_name} (Class {true_label_index})")
print(f"Predicted Label: {predicted_label_name} (Class {predicted_label_index})")
print(f"Prediction Confidence: {prediction_probs[0][predicted_label_index]:.4f}")

# Plot the ECG signal of the random sample
plt.figure(figsize=(12, 4))
plt.plot(single_sample)
plt.title(f'ECG Signal\nTrue: {true_label_name} | Predicted: {predicted_label_name}')
plt.xlabel('Time Step')
plt.ylabel('Signal Value')
plt.grid(True)
plt.show()
