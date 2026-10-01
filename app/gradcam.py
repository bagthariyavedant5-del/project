import tensorflow as tf
import numpy as np
import cv2
from tf_keras_vis.gradcam import Gradcam
from tf_keras_vis.utils.model_modifiers import ReplaceToLinear
from tf_keras_vis.utils.scores import CategoricalScore
import matplotlib.cm as cm

def generate_gradcam_heatmap(model, img_array, class_index):
    """
    Generate Grad-CAM heatmap for a given image array and model.
    """
    # Replace the activation of the last layer to linear
    replace2linear = ReplaceToLinear()
    
    # We want to focus on the class predicted by the model
    score = CategoricalScore([class_index])
    
    # Create Gradcam object
    gradcam = Gradcam(model, model_modifier=replace2linear, clone=True)
    
    # Generate heatmap
    cam = gradcam(score, img_array, penultimate_layer=-1)
    
    # cam is currently shape (1, 224, 224), get the first element
    heatmap = cam[0]
    
    return heatmap

def overlay_heatmap(img_array, heatmap, alpha=0.4, colormap_name="jet"):
    """
    Overlay Grad-CAM heatmap onto the original image.
    """
    # Rescale heatmap to a range 0-255
    heatmap = np.uint8(255 * heatmap)
    
    # Use selected colormap to colorize heatmap
    try:
        import matplotlib.pyplot as plt
        cmap = plt.get_cmap(colormap_name)
    except Exception:
        try:
            cmap = cm.get_cmap(colormap_name)
        except Exception:
            cmap = cm.get_cmap("jet")
    
    # Use RGB values of the colormap
    jet_colors = cmap(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]
    
    # Create an image with RGB colorized heatmap
    jet_heatmap = tf.keras.preprocessing.image.array_to_img(jet_heatmap)
    jet_heatmap = jet_heatmap.resize((img_array.shape[1], img_array.shape[0]))
    jet_heatmap = tf.keras.preprocessing.image.img_to_array(jet_heatmap)
    
    # Superimpose the heatmap on original image
    superimposed_img = jet_heatmap * alpha + img_array
    superimposed_img = tf.keras.preprocessing.image.array_to_img(superimposed_img)
    
    return superimposed_img
