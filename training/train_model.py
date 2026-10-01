import os
import tensorflow as tf
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from augmentation import get_data_augmenter

def build_model():
    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(224, 224, 3)
    )
    
    # Unfreeze top 20 layers for fine-tuning
    base_model.trainable = True
    for layer in base_model.layers[:-20]:
        layer.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.5)(x)
    output = Dense(5, activation="softmax")(x)

    model = Model(inputs=base_model.input, outputs=output)

    model.compile(
        optimizer=Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model

if __name__ == "__main__":
    dataset_path = os.path.join(os.path.dirname(__file__), "../dataset")
    if not os.path.exists(dataset_path) or not os.listdir(dataset_path):
        print(f"Dataset path {dataset_path} does not exist or is empty.")
        print("Please download the APTOS 2019 dataset and extract it into the 'dataset' folder.")
        exit(1)
        
    print("Building model...")
    model = build_model()
    
    datagen = get_data_augmenter()
    
    print("Loading training data...")
    train_data = datagen.flow_from_directory(
        dataset_path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='training'
    )
    
    print("Loading validation data...")
    val_data = datagen.flow_from_directory(
        dataset_path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='validation'
    )
    
    early_stop = EarlyStopping(
        monitor='val_loss', 
        patience=4, 
        restore_best_weights=True,
        verbose=1
    )
    
    print("Computing class weights to fix dataset imbalance...")
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_data.classes),
        y=train_data.classes
    )
    class_weights_dict = dict(enumerate(class_weights))
    
    print("Starting training...")
    model.fit(
        train_data,
        validation_data=val_data,
        epochs=20,
        class_weight=class_weights_dict,
        callbacks=[early_stop]
    )
    
    model.save(os.path.join(os.path.dirname(__file__), "../app/dr_model.h5"))
    print("Model saved as dr_model.h5 in the app directory.")
