import numpy as np
import cv2
import matplotlib.pyplot as plt
import qrcode
from datetime import datetime
import os

# Function to generate a random texture pattern
def generate_texture_pattern(image_size=(256, 256)):
    """
    Generate base texture pattern using random noise and edge detection.

    Args:
        image_size: Tuple of (height, width) for the pattern

    Returns:
        Grayscale texture pattern (numpy array)
    """
    # Create a random noise image
    noise = np.random.rand(*image_size)

    # Apply a simple edge-detection effect (like a high-pass filter) to simulate a microtexture
    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])  # Simple edge detection kernel
    texture = cv2.filter2D(noise, -1, kernel)

    # Normalize to the range 0-255
    texture = cv2.normalize(texture, None, 0, 255, cv2.NORM_MINMAX)

    return texture.astype(np.uint8)


# Layer 3: Oriented Micro-Hatching (Directional Security)
def add_micro_hatching(pattern, seed=42, density=0.015, length_range=(3, 10)):
    """
    Add oriented micro-hatching lines at multiple angles.

    This layer provides directional security by exploiting anisotropic degradation
    during the print-scan-reprint process. Different line orientations degrade
    differently, making copies detectable.

    Args:
        pattern: Input grayscale image
        seed: Random seed for reproducibility (deterministic generation)
        density: Density of hatches (0.015 = 1.5% of pixels will be hatch starting points)
        length_range: Min and max length of each hatch stroke in pixels

    Returns:
        Pattern with micro-hatching overlay

    Security Features:
        - 8 distinct orientations (0°, 30°, 45°, 60°, 90°, 120°, 135°, 150°)
        - Anisotropic blur detection (diagonal lines degrade faster)
        - Resistant to vector redraw attacks
        - Exposes rescreening and double halftoning
    """
    np.random.seed(seed)
    h, w = pattern.shape
    output = pattern.copy()

    # Number of hatches based on density
    num_hatches = int(h * w * density)

    # Define angles in degrees (directional security)
    # These angles will degrade differently during print-scan process
    angles = [0, 30, 45, 60, 90, 120, 135, 150]

    print(f"  Adding {num_hatches} micro-hatches at {len(angles)} orientations...")

    for _ in range(num_hatches):
        # Random starting point (avoid edges)
        margin = 15
        y = np.random.randint(margin, h - margin)
        x = np.random.randint(margin, w - margin)

        # Random angle and length
        angle = np.random.choice(angles)
        length = np.random.randint(*length_range)

        # Calculate end point based on angle
        rad = np.radians(angle)
        dx = int(length * np.cos(rad))
        dy = int(length * np.sin(rad))

        # Ensure end point is within bounds
        end_x = min(max(0, x + dx), w - 1)
        end_y = min(max(0, y + dy), h - 1)

        # Draw 1-pixel line (anti-aliased for smooth appearance)
        # Use white (255) for visibility on gray background
        cv2.line(output, (x, y), (end_x, end_y),
                color=255, thickness=1, lineType=cv2.LINE_AA)

    return output


# Function to generate and overlay a real QR code on the pattern
def overlay_qr_code(pattern, data="", size=80, position=None):
    """
    Generate and overlay a QR code with embedded data on the pattern.

    Args:
        pattern: Input grayscale pattern
        data: Data to encode in QR code (URL, serial number, etc.)
        size: Size of QR code in pixels
        position: (x, y) position for QR code overlay (None = center)

    Returns:
        Pattern with QR code overlay
    """
    # Generate QR code with the embedded data
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=2,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_array = np.array(qr_img.convert('L'))

    # Resize QR code to desired size
    qr_resized = cv2.resize(qr_array, (size, size), interpolation=cv2.INTER_NEAREST)

    # Calculate center position if not specified
    if position is None:
        h, w = pattern.shape
        position = ((w - size) // 2, (h - size) // 2)

    # Overlay QR code on the pattern at the specified position
    x, y = position
    qr_height, qr_width = qr_resized.shape

    # Blend QR code with pattern (70% QR, 30% pattern for visibility)
    pattern[y:y+qr_height, x:x+qr_width] = cv2.addWeighted(
        pattern[y:y+qr_height, x:x+qr_width], 0.3, qr_resized, 0.7, 0
    )

    return pattern


def main():
    """
    Main function to generate multi-layer CDP pattern.
    """
    # Configuration
    EMBEDDED_DATA = "www.google.com"
    IMAGE_SIZE = (256, 256)
    QR_SIZE = 80
    SEED = 42  # Deterministic seed for reproducibility (Layer 1)

    # Create output directory if it doesn't exist
    output_dir = "generated_patterns"
    os.makedirs(output_dir, exist_ok=True)

    # Generate base anti-counterfeiting pattern
    print("="*60)
    print("Multi-Layer CDP Pattern Generator")
    print("="*60)
    print(f"Embedded data: {EMBEDDED_DATA}")
    print(f"Pattern size: {IMAGE_SIZE[0]}x{IMAGE_SIZE[1]} pixels")
    print(f"Security layers: Texture + Micro-Hatching (Layer 3) + QR Code")
    print()

    # Step 1: Generate base texture pattern
    print("Step 1: Generating base texture pattern...")
    pattern = generate_texture_pattern(image_size=IMAGE_SIZE)

    # Step 2: Add Layer 3 - Oriented Micro-Hatching (Directional Security)
    print("Step 2: Adding Layer 3 - Oriented Micro-Hatching...")
    pattern_with_hatching = add_micro_hatching(pattern, seed=SEED, density=0.015, length_range=(3, 10))

    # Step 3: Overlay QR code with embedded data
    print("Step 3: Overlaying QR code with embedded data...")
    final_pattern = overlay_qr_code(pattern_with_hatching, data=EMBEDDED_DATA, size=QR_SIZE)

    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"cdp_pattern_layer3_{timestamp}.png")

    # Display the result
    print()
    print("Generating visualization...")
    plt.figure(figsize=(8, 8))
    plt.imshow(final_pattern, cmap='gray')
    plt.title(f"CDP Pattern (Layer 3) - Data: {EMBEDDED_DATA}", fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()

    # Save the generated image
    cv2.imwrite(filename, final_pattern)

    print()
    print("="*60)
    print("CDP Pattern Generation Complete!")
    print("="*60)
    print(f"Filename: {filename}")
    print(f"Pattern size: {IMAGE_SIZE[0]}x{IMAGE_SIZE[1]} pixels")
    print(f"Embedded data: {EMBEDDED_DATA}")
    print(f"Random seed: {SEED}")
    print(f"Security layers implemented:")
    print(f"  [+] Base texture (random noise + edge detection)")
    print(f"  [+] Layer 3: Oriented Micro-Hatching (directional security)")
    print(f"  [+] QR Code overlay (machine-readable data)")
    print("="*60)


if __name__ == "__main__":
    main()
