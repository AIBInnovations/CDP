import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os

# Floyd-Steinberg dithering algorithm
def floyd_steinberg_dither(image):
    # Convert the image to grayscale (if it's not already)
    gray_image = image.convert('L')
    # Convert image to a NumPy array
    img_array = np.array(gray_image)
    
    # Get the dimensions of the image
    height, width = img_array.shape

    # Apply Floyd-Steinberg dithering
    for y in range(height - 1):  # Loop through all but the last row
        for x in range(1, width - 1):  # Loop through all but the last column
            old_pixel = img_array[y, x]
            new_pixel = round(old_pixel / 255) * 255  # Round to either 0 or 255
            img_array[y, x] = new_pixel
            error = old_pixel - new_pixel

            # Distribute the error to neighboring pixels
            img_array[y, x + 1] += error * 7 / 16
            img_array[y + 1, x - 1] += error * 3 / 16
            img_array[y + 1, x] += error * 5 / 16
            img_array[y + 1, x + 1] += error * 1 / 16

    # Return the dithered image as a new image object
    return Image.fromarray(img_array)

# Create a random noise pattern as the base for the CDP
width, height = 256, 256  # Dimensions of the pattern
random_noise = np.random.rand(height, width) * 255  # Random noise between 0 and 255

# Convert the random noise array to a PIL image
random_noise_image = Image.fromarray(np.uint8(random_noise))

# Apply Floyd-Steinberg dithering to the random noise to create the CDP
dithered_cdp = floyd_steinberg_dither(random_noise_image)

# Define the folder where the image will be saved
output_folder = "generated_cdp_patterns"  # Folder name where the CDP pattern will be saved

# Create the folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Define the output path
output_path = os.path.join(output_folder, "cdp_pattern.png")

# Save the dithered CDP pattern to the folder
dithered_cdp.save(output_path)

print(f"CDP pattern saved at: {output_path}")

# Display the random noise pattern and the resulting CDP
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
axes[0].imshow(random_noise_image, cmap='gray')
axes[0].set_title("Random Noise Pattern")
axes[0].axis('off')

axes[1].imshow(dithered_cdp, cmap='gray')
axes[1].set_title("Dithered CDP Pattern")
axes[1].axis('off')

plt.show()
