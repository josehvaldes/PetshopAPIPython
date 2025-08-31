import pandas as pd
import tensorflow as tf 
import numpy as np
from keras.models import Sequential
from keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

model = Sequential([
    # Convolutional Layer: Learns features from the signal
    # 64 filters, kernel size of 3
    tf.keras.Input(shape=(187, 1)), # Input shape: 187 time steps, 1 feature
    Conv1D(filters=64, kernel_size=3, activation='relu'),
    
    # Pooling Layer: Reduces the size of the data
    MaxPooling1D(pool_size=2),
    
    # Flatten Layer: Converts the 2D data to 1D for the final layers
    Flatten(),
    
    # Dense (Fully Connected) Layers: Perform the final classification
    Dense(128, activation='relu'),
    Dropout(0.5), # Helps prevent overfitting
    
    # Output Layer: 5 units for 5 classes (for mitbih)
    # Use 'softmax' for multi-class classification
    #Dense(5, activation='softmax') 
    
    # For binary classification (normal vs abnormal)
    Dense(2, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

ptbdb_normal_df = pd.read_csv('./data/ptbdb_normal.csv', header=None)
ptbdb_abnormal_df = pd.read_csv('./data/ptbdb_abnormal.csv', header=None)

combined_df = pd.concat([ptbdb_normal_df, ptbdb_abnormal_df], ignore_index=True)
print(combined_df.head())

labels = combined_df.iloc[:, -1]  # The last column is the label
features = combined_df.drop(combined_df.columns[-1], axis=1)  # Drop the label column from features

# Convert to NumPy and reshape to (samples, 187, 1)
X = np.array(features).reshape(-1, 187, 1)
y = np.array(labels).flatten()


# Split into train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("X shape:", X_train.shape)  # Should be (num_samples, 187, 1)
print("y shape:", y_train.shape)  # Should be (num_samples,)

print("First few labels:", y_train[:5])
print("Unique labels:", np.unique(y_train)) 

model.fit(X_train, y_train, epochs=10, validation_split=0.2)
# Save the model
model.save('one_d_cnn_model.keras')

# Print the model summary again to confirm
model.summary()

# Evaluate the model on the test set
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy:.2f}")

predictions = model.predict(X_test)
confidences = np.max(predictions, axis=1)
print("First few predictions:", np.argmax(predictions, axis=1)[:5])
print("First few confidence scores:", confidences[:5])

# Save test features and labels to CSV files
if not isinstance(X_test, pd.DataFrame):
    X_test = pd.DataFrame(X_test.reshape(X_test.shape[0], X_test.shape[1]))
if not isinstance(y_test, pd.DataFrame):
    y_test = pd.DataFrame(y_test) 

X_test.to_csv('data/ptbdb_test_features.csv', index=False, header=False)
y_test.to_csv('data/ptbdb_test_labels.csv', index=False, header=False)

