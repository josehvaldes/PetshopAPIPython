import pandas as pd
import tensorflow as tf 
import numpy as np
from keras.models import Sequential
from keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout


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
    Dense(5, activation='softmax') 
])


# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Print the model summary
model.summary()


# Now you can train the model with your data:
# model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))


ptbdb_normal_df = pd.read_csv('./data/ptbdb_normal.csv', header=None)
ptbdb_abnormal_df = pd.read_csv('./data/ptbdb_abnormal.csv', header=None)

combined_df = pd.concat([ptbdb_normal_df, ptbdb_abnormal_df], ignore_index=True)
print(combined_df.head())

labels = combined_df.iloc[:, -1]  # The last column is the label
features = combined_df.drop(combined_df.columns[-1], axis=1)  # Drop the label column from features

# Convert to NumPy and reshape to (samples, 187, 1)
X = np.array(features).reshape(-1, 187, 1)
y = np.array(labels).flatten()

print("X shape:", X.shape)  # Should be (num_samples, 187, 1)
print("y shape:", y.shape)  # Should be (num_samples,)

print("First few labels:", y[:5])
print("Unique labels:", np.unique(y))  # Should show 5 classes if you're using mitbih
print("Unique classes:", np.unique(y))


model.fit(features, labels, epochs=10, validation_split=0.2)
# Save the model
model.save('one_d_cnn_model.keras')