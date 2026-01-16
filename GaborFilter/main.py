import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
from datetime import datetime

# Function to generate a single Gabor filter at a specific frequency, orientation, and other parameters
def generate_single_gabor(width, height, wavelength, orientation, phase, sigma, gamma):
    # Create an empty pattern array
    pattern = np.zeros((height, width))

    # Center coordinates
    x_centered = np.arange(width) - width / 2
    y_centered = np.arange(height) - height / 2
    X, Y = np.meshgrid(x_centered, y_centered)
    
    # Rotate coordinates based on orientation
    x_prime = X * np.cos(orientation) + Y * np.sin(orientation)
    y_prime = -X * np.sin(orientation) + Y * np.cos(orientation)
    
    # Gaussian envelope
    gaussian = np.exp(-(x_prime**2 + gamma**2 * y_prime**2) / (2 * sigma**2))
    
    # Sinusoidal component
    sinusoid = np.cos(2 * np.pi * x_prime / wavelength + phase)
    
    # Gabor filter response
    pattern = gaussian * sinusoid
    return pattern

# Function to generate multi-scale Gabor pattern (using multiple orientations and frequencies)
def multi_scale_gabor(width, height, secret_key, num_orientations=4, num_frequencies=3):
    # Placeholder for the final pattern
    pattern = np.zeros((height, width))
    
    # Deriving orientations and frequencies from the secret key (or just set manually for example)
    orientations = np.linspace(0, np.pi, num_orientations, endpoint=False)  # Example: 0°, 45°, 90°, 135°
    frequencies = np.linspace(4, 16, num_frequencies)  # Wavelengths (frequencies)

    # Assume the secret key provides randomness (use the secret key for advanced pattern generation)
    for theta in orientations:
        for lambda_ in frequencies:
            # Parameters for each filter
            phase = np.random.uniform(0, 2*np.pi)  # Random phase shift
            sigma = lambda_ * 0.5  # Set sigma as a function of wavelength
            gamma = 1.0  # Aspect ratio (circular symmetry)

            # Generate single Gabor filter for each orientation/frequency
            gabor_filter = generate_single_gabor(width, height, lambda_, theta, phase, sigma, gamma)
            
            # Add to final pattern
            weight = np.random.uniform(0.5, 1.5)  # Random weight (can be derived from secret key)
            pattern += weight * gabor_filter

    # Normalize the result to have values between 0 and 255
    pattern = np.abs(pattern)  # Ensure all values are non-negative
    pattern = np.clip(pattern, 0, 255)  # Clip values to valid image range (0-255)
    pattern = (pattern / np.max(pattern)) * 255  # Normalize to 0-255 range
    
    return pattern

# Function to save the pattern to an image file
def save_pattern_to_image(pattern, folder_path, file_prefix="gabor_pattern"):
    # Create folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Generate a unique filename using current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{file_prefix}_{timestamp}.png"
    file_path = os.path.join(folder_path, file_name)
    
    # Convert pattern to an 8-bit image
    image = Image.fromarray(pattern.astype(np.uint8))
    
    # Save the image
    image.save(file_path)
    print(f"Pattern saved as {file_path}")

# Function to visualize the generated pattern (optional)
def display_pattern(pattern):
    plt.imshow(pattern, cmap='gray')
    plt.axis('off')
    plt.show()

# Example usage of the multi-scale Gabor pattern generator
width, height = 51, 51
secret_key = "example_secret_key"  # For simplicity, the key is not used in the current version

# Number of times you want to generate patterns (for example, 5 times)
num_patterns_to_generate = 5

# Folder to store the generated patterns
folder_path = "generated_patterns"

# Generate and save multiple patterns
for i in range(num_patterns_to_generate):
    pattern = multi_scale_gabor(width, height, secret_key)
    
    # Display the generated pattern (optional)
    display_pattern(pattern)
    
    # Save the pattern to the folder
    save_pattern_to_image(pattern, folder_path)
