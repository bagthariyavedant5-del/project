from tensorflow.keras.preprocessing.image import ImageDataGenerator

def get_data_augmenter():
    datagen = ImageDataGenerator(
        rotation_range=20,
        horizontal_flip=True,
        zoom_range=0.2,
        brightness_range=[0.8, 1.2],
        validation_split=0.2 # Reserving 20% for validation
    )
    return datagen
