import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Logistic map-based fractal generator for CDP
def logistic_map(width, height, r=3.9, x0=0.5):
    # Initialize a blank canvas
    pattern = np.zeros((height, width), dtype=np.uint8)
    x = x0  # Initial condition for the logistic map

    # Generate the pattern using the logistic map
    for y in range(height):
        for x_pos in range(width):
            x = r * x * (1 - x)  # Logistic map equation
            pattern[y, x_pos] = int(x * 255)  # Map the value to the 0-255 range

    return pattern

# Create a more complex CDP pattern based on the logistic map
width, height = 256, 256  # Dimensions of the pattern
cdp_pattern = logistic_map(width, height)

# Convert the pattern into an image
cdp_image = Image.fromarray(cdp_pattern)

# Define the folder to save the generated CDP pattern
output_folder = "generated_cdp_patterns"  # Folder name where the CDP pattern will be saved

# Create the folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Generate a unique filename using the current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YearMonthDay_HourMinuteSecond
output_path = os.path.join(output_folder, f"cdp_pattern_{timestamp}.png")

# Save the dithered CDP pattern to the folder with a unique filename
cdp_image.save(output_path)

print(f"Fractal-based CDP pattern saved at: {output_path}")

# Display the generated CDP pattern
plt.figure(figsize=(6, 6))
plt.imshow(cdp_image, cmap='gray')
plt.title("Fractal-based CDP Pattern")
plt.axis('off')
plt.show()
