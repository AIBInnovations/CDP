import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
from scipy.fftpack import dct, idct

# Step 1: Generate a random CDP pattern (can be replaced with any secure pattern)
def generate_cdp_pattern(width, height):
    # Generate random noise between 0 and 255
    return np.random.rand(height, width) * 255

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

# Step 3: Extract the watermark by comparing the original and watermarked images
def extract_watermark(original_img, watermarked_img, alpha=0.1):
    # Convert to grayscale and to numpy arrays
    original_array = np.array(original_img.convert('L'), dtype=float)
    watermarked_array = np.array(watermarked_img.convert('L'), dtype=float)
    
    # Apply DCT to both images
    dct_original = dct(dct(original_array.T, norm='ortho').T, norm='ortho')
    dct_watermarked = dct(dct(watermarked_array.T, norm='ortho').T, norm='ortho')
    
    # Extract the watermark by comparing low-frequency DCT coefficients
    watermark_extracted = (dct_watermarked[:dct_original.shape[0], :dct_original.shape[1]] - dct_original[:dct_original.shape[0], :dct_original.shape[1]]) / alpha
    
    return watermark_extracted

# Step 4: Save the watermarked image and display the results
def save_and_display_watermarked_image(image, watermark):
    # Create a random CDP pattern as watermark
    cdp_pattern = generate_cdp_pattern(image.width, image.height)
    
    # Embed the watermark into the image
    watermarked_image = embed_watermark(image, cdp_pattern)
    
    # Define folder to save watermarked image
    output_folder = "generated_watermarked_images"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Save the watermarked image
    output_path = os.path.join(output_folder, "watermarked_image.png")
    watermarked_image.save(output_path)
    
    print(f"Watermarked image saved at: {output_path}")
    
    # Display the original and watermarked images
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(image.convert('L'), cmap='gray')
    plt.title("Original Image")
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.imshow(watermarked_image, cmap='gray')
    plt.title("Watermarked Image")
    plt.axis('off')
    
    plt.show()

# Load an example image
image_path = "example_image.jpg"  # Replace this with the path to your image
image = Image.open(image_path)

# Call the function to embed watermark and display/save the results
save_and_display_watermarked_image(image, generate_cdp_pattern)
