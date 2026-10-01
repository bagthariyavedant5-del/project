import os
import numpy as np
import cv2

dataset_dir = "c:/Users/davul/.vscode/dr-retinopathy-ai/dataset"
classes = ["0", "1", "2", "3", "4"]
images_per_class = 40  # Increase dataset size

os.makedirs(dataset_dir, exist_ok=True)

def generate_retina(dr_stage):
    # Base image: Dark background with an orange/red circle in the middle (retina)
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    
    # Retina base color (b, g, r) somewhat orange-red
    base_color = (60, 100, 200)
    center = (112, 112)
    radius = 100
    cv2.circle(img, center, radius, base_color, -1)
    
    # Add varying numbers of lesions based on DR stage to force the model to learn features
    num_exudates = dr_stage * np.random.randint(5, 15)  # Yellow/White spots
    num_hemorrhages = dr_stage * np.random.randint(5, 15) # Dark Red spots
    
    # Exudates (Hard/Soft)
    for _ in range(num_exudates):
        x = np.random.randint(center[0]-radius+10, center[0]+radius-10)
        y = np.random.randint(center[1]-radius+10, center[1]+radius-10)
        # Check if inside circle
        if (x-center[0])**2 + (y-center[1])**2 < (radius-10)**2:
            color = (np.random.randint(180, 255), np.random.randint(220, 255), np.random.randint(240, 255))
            size = np.random.randint(1, 4)
            cv2.circle(img, (x, y), size, color, -1)
            
    # Hemorrhages/Microaneurysms
    for _ in range(num_hemorrhages):
        x = np.random.randint(center[0]-radius+10, center[0]+radius-10)
        y = np.random.randint(center[1]-radius+10, center[1]+radius-10)
        if (x-center[0])**2 + (y-center[1])**2 < (radius-10)**2:
            color = (np.random.randint(10, 40), np.random.randint(10, 40), np.random.randint(100, 150))
            size = np.random.randint(2, 6)
            cv2.circle(img, (x, y), size, color, -1)
            
    # Add some random noise and blur to simulate varied scan qualities
    noise = np.random.randn(*img.shape) * np.random.randint(5, 20)
    noisy_img = np.clip(img + noise, 0, 255).astype(np.uint8)
    blurred = cv2.GaussianBlur(noisy_img, (3, 3), 0)
            
    return blurred

for stage_idx, cls in enumerate(classes):
    cls_dir = os.path.join(dataset_dir, cls)
    os.makedirs(cls_dir, exist_ok=True)
    
    for i in range(images_per_class):
        img = generate_retina(stage_idx)
        filename = f"sample_{cls}_{i}.jpg"
        cv2.imwrite(os.path.join(cls_dir, filename), img)

print(f"Generated {len(classes) * images_per_class} MORE REALISTIC synthetic images in {dataset_dir}")

