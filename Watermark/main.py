import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
from scipy.fftpack import dct, idct
import time

# Step 1: Generate a unique pattern (CDP) using geometric functions
def generate_unique_pattern(width, height):
    # Create a sinusoidal pattern using sine and cosine to create an interesting design
    x = np.linspace(0, 2 * np.pi, width)
    y = np.linspace(0, 2 * np.pi, height)
    X, Y = np.meshgrid(x, y)

    # Use sine and cosine to create a wave-like pattern
    pattern = (np.sin(X) + np.cos(Y)) * 128 + 128  # Normalize to 0-255
    return pattern

# Step 2: Embed the watermark using DCT (Spread Spectrum Watermarking)
def embed_watermark(image, watermark, alpha=0.1):
    # Convert image to grayscale
    gray_image = image.convert('L')
    img_array = np.array(gray_image, dtype=float)
    
    # Apply DCT to the image
    dct_img = dct(dct(img_array.T, norm='ortho').T, norm='ortho')
    
    # Embed the watermark into the DCT coefficients (low-frequency region)
    watermark_resized = np.resize(watermark, img_array.shape)  # Resize watermark to fit image size
    dct_img[:watermark_resized.shape[0], :watermark_resized.shape[1]] += alpha * watermark_resized  # Embed watermark
    
    # Apply inverse DCT to get the watermarked image
    watermarked_img = idct(idct(dct_img.T, norm='ortho').T, norm='ortho')
    
    # Clip the values to be between 0 and 255
    watermarked_img = np.clip(watermarked_img, 0, 255)
    
    return Image.fromarray(np.uint8(watermarked_img))

# Step 3: Save the pattern and watermark it
def save_and_display_watermarked_image():
    # Generate a unique pattern (CDP)
    unique_pattern = generate_unique_pattern(256, 256)  # Adjust size as needed
    
    # Convert the pattern into an image
    pattern_image = Image.fromarray(np.uint8(unique_pattern))

    # Embed the watermark (CDP pattern) into the image
    watermarked_image = embed_watermark(pattern_image, unique_pattern)
    
    # Define the folder to save the generated images
    output_folder = "generated_watermarked_images"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Generate a unique filename using timestamp to avoid overwriting
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    pattern_filename = os.path.join(output_folder, f"pattern_{timestamp}.png")
    watermarked_image_filename = os.path.join(output_folder, f"watermarked_image_{timestamp}.png")
    
    # Save the pattern and the watermarked image
    pattern_image.save(pattern_filename)
    watermarked_image.save(watermarked_image_filename)
    
    print(f"Pattern saved at: {pattern_filename}")
    print(f"Watermarked image saved at: {watermarked_image_filename}")
    
    # Display the original pattern and the watermarked image
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(pattern_image, cmap='gray')
    plt.title("Generated Pattern (CDP)")
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.imshow(watermarked_image, cmap='gray')
    plt.title("Watermarked Image")
    plt.axis('off')
    
    plt.show()

# Call the function to save and display the pattern and watermarked image
save_and_display_watermarked_image()
