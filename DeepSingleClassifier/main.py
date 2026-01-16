import numpy as np
import cv2
import matplotlib.pyplot as plt

# Function to generate a random texture pattern
def generate_texture_pattern(image_size=(256, 256)):
    # Create a random noise image
    noise = np.random.rand(*image_size)

    # Apply a simple edge-detection effect (like a high-pass filter) to simulate a microtexture
    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])  # Simple edge detection kernel
    texture = cv2.filter2D(noise, -1, kernel)

    # Normalize to the range 0-255
    texture = cv2.normalize(texture, None, 0, 255, cv2.NORM_MINMAX)

    return texture.astype(np.uint8)

# Function to overlay a simple QR code on the pattern
def overlay_qr_code(pattern, size=(50, 50), position=(100, 100)):
    # Create a simple QR code
    qr = np.zeros(size, dtype=np.uint8)
    cv2.putText(qr, "QR", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255), 2, cv2.LINE_AA)

    # Overlay QR code on the pattern at the specified position
    x, y = position
    qr_height, qr_width = qr.shape
    pattern[y:y+qr_height, x:x+qr_width] = cv2.addWeighted(pattern[y:y+qr_height, x:x+qr_width], 0.5, qr, 0.5, 0)

    return pattern

# Generate base anti-counterfeiting pattern
pattern = generate_texture_pattern()

# Overlay a QR code on the pattern
final_pattern = overlay_qr_code(pattern)

# Display the result
plt.imshow(final_pattern, cmap='gray')
plt.title("Generated Anti-Counterfeiting Pattern with QR Code")
plt.axis('off')
plt.show()

# Save the generated image
cv2.imwrite("anti_counterfeit_pattern.png", final_pattern)
