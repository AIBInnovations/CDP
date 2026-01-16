import numpy as np
from Crypto.Cipher import ChaCha20
from PIL import Image
import os
from datetime import datetime

# Step 1: PRNG Pattern Generation (Noise-based pattern)
def initialize_prng(seed):
    """
    Initialize ChaCha20 PRNG with a secret seed (key).
    :param seed: 32-byte seed (secret key) to initialize the PRNG.
    :return: ChaCha20 cipher object.
    """
    nonce = bytes(8)  # 8-byte nonce (can be randomized as well)
    prng = ChaCha20.new(key=seed, nonce=nonce)
    return prng

def generate_prng_pattern(width, height, seed):
    """
    Generate a PRNG-based noise pattern using ChaCha20 (large distinguishable pixels).
    :param width: Width of the pattern (in pixels).
    :param height: Height of the pattern (in pixels).
    :param seed: 32-byte secret key for the PRNG.
    :return: Generated pattern as a 2D numpy array (grayscale).
    """
    prng = initialize_prng(seed)
    pattern = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            # Generate a random value between 0-255 (grayscale)
            random_byte = prng.encrypt(bytes([0]))[0]  # Encrypting a single byte with PRNG
            pattern[y, x] = random_byte  # Store the byte value as the pixel value (grayscale)

    return pattern

# Step 2: Embed the link into the PRNG pattern using LSB encoding
def encode_link_in_pattern(pattern, link):
    """
    Embed a link into the PRNG pattern using LSB (Least Significant Bit) encoding.
    :param pattern: The pattern (2D array of pixel values).
    :param link: The link (string) to embed into the pattern.
    :return: The pattern with the embedded link.
    """
    # Convert the link into binary
    link_binary = ''.join(format(ord(c), '08b') for c in link)
    
    # Ensure the pattern has enough pixels to store the link
    if len(link_binary) > pattern.size:
        raise ValueError("Link is too long to fit in the given pattern size")

    # Embed the link into the pattern
    flat_pattern = pattern.flatten()  # Flatten the pattern into a 1D array
    for i, bit in enumerate(link_binary):
        flat_pattern[i] = (flat_pattern[i] & 0xFE) | int(bit)  # Modify the LSB

    return pattern.reshape((pattern.shape[0], pattern.shape[1]))  # Reshape back to 2D pattern

# Step 3: Dithering (introduce error-prone distortion for reprinting)
def dithering_pattern(pattern, threshold=128):
    """
    Apply dithering to introduce intentional degradation to the pattern for reprinting.
    :param pattern: The pattern to apply dithering.
    :param threshold: The threshold for dithering to create a binary pattern.
    :return: Dithered pattern.
    """
    # Convert the pattern to a binary pattern based on the threshold
    dithered = np.where(pattern > threshold, 255, 0).astype(np.uint8)  # Ensure the type is uint8
    return dithered

# Step 4: Save the Pattern with the Hidden Link
def save_pattern_with_link(pattern, folder='outputs', dpi=300, link="https://yourpaymentgateway.com/pay?amount=10.00&currency=USD"):
    """
    Save the generated pattern with an embedded link as an image.
    The link will be hidden in the pattern using LSB encoding.
    :param pattern: The PRNG pattern (2D array of pixel values).
    :param folder: Folder to save the image (default 'outputs').
    :param dpi: DPI value to set for the image (default 300).
    :param link: The link to encode in the pattern (default payment URL).
    """
    # Embed the link into the PRNG pattern
    pattern_with_link = encode_link_in_pattern(pattern, link)

    # Apply dithering (error-prone intentional degradation)
    pattern_with_link_dithered = dithering_pattern(pattern_with_link)

    # Convert to uint8 before passing to PIL
    pattern_with_link_dithered = pattern_with_link_dithered.astype(np.uint8)

    # Save the image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    filename = f"{timestamp}_pattern_with_link.png"
    filepath = os.path.join(folder, filename)
    
    # Convert the pattern to an image
    image = Image.fromarray(pattern_with_link_dithered)
    image.save(filepath, format='PNG', dpi=(dpi, dpi))  # Save with specified DPI

    print(f"Pattern with link saved as {filepath}")

# Step 5: Main Function to Run Everything
def main():
    # Generate the 128x128 PRNG pattern with large distinguishable pixels (small height)
    width, height = 128, 128  # 128x128 pattern with larger pixels
    seed = os.urandom(32)  # Random 32-byte secret key
    
    # Generate the PRNG pattern
    pattern = generate_prng_pattern(width, height, seed)
    
    # Save the pattern with the hidden link and dithering applied
    save_pattern_with_link(pattern, folder='outputs', dpi=300, link="https://yourpaymentgateway.com/pay?amount=10.00&currency=USD")

if __name__ == '__main__':
    main()
