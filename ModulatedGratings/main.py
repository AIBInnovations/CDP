import numpy as np
import matplotlib.pyplot as plt
import os
import time
from math import sin, cos, pi

# Function to create sinusoidal grating
def sinusoidal_grating(width, height, frequency, orientation, phase):
    pattern = np.zeros((height, width), dtype=np.float32)

    for y in range(height):
        for x in range(width):
            # Rotate the coordinates based on orientation
            x_rot = x * cos(orientation) + y * sin(orientation)
            value = (sin(2 * pi * frequency * x_rot + phase) + 1) / 2  # Normalize to [0, 1]
            pattern[y, x] = value

    return pattern

# Function to create frequency-modulated grating
def fm_grating(width, height, base_freq, modulation_freq, modulation_depth):
    pattern = np.zeros((height, width), dtype=np.float32)

    for y in range(height):
        for x in range(width):
            # Calculate instantaneous frequency at each position
            inst_freq = base_freq + modulation_depth * sin(2 * pi * modulation_freq * x)
            # Integrate the frequency over the x-axis to get phase
            phase = inst_freq * x
            value = (sin(phase) + 1) / 2  # Normalize to [0, 1]
            pattern[y, x] = value

    return pattern

# Function to create phase-modulated grating
def pm_grating(width, height, frequency, phase_pattern, modulation_depth):
    pattern = np.zeros((height, width), dtype=np.float32)

    for y in range(height):
        for x in range(width):
            # Get the local phase from the phase pattern
            local_phase = phase_pattern[y, x] * modulation_depth
            value = (sin(2 * pi * frequency * x + local_phase) + 1) / 2  # Normalize to [0, 1]
            pattern[y, x] = value

    return pattern

# Function to create Moiré pattern by combining two sinusoidal gratings
def moire_pattern(width, height, freq1, freq2, angle1, angle2):
    grating1 = sinusoidal_grating(width, height, freq1, angle1, 0)
    grating2 = sinusoidal_grating(width, height, freq2, angle2, 0)

    # Combine the two gratings
    combined = np.multiply(grating1, grating2)
    return combined

# Function to ensure the directory for saving images exists
def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to save the generated pattern as an image
def save_pattern(pattern, filename):
    plt.imshow(pattern, cmap='gray')
    plt.axis('off')  # Turn off axis
    plt.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()

# Main function to generate and save patterns
def generate_and_save_patterns():
    # Get the current time to create unique folder name
    current_time = time.strftime("%Y%m%d-%H%M%S")
    folder_name = f"patterns_{current_time}"
    ensure_directory(folder_name)

    # Parameters for pattern generation
    width, height = 51, 51  # Image size
    frequency = 20  # Frequency of the grating
    modulation_freq = 0.05  # Frequency modulation rate
    modulation_depth = 0.1  # Modulation depth for FM
    phase_pattern = np.random.rand(height, width) * 2 * pi  # Random phase pattern for PM

    # Generate and save sinusoidal grating
    pattern = sinusoidal_grating(width, height, frequency, 45 * pi / 180, 0)
    save_pattern(pattern, os.path.join(folder_name, "sinusoidal_grating.png"))

    # Generate and save frequency-modulated grating
    fm_pattern = fm_grating(width, height, frequency, modulation_freq, modulation_depth)
    save_pattern(fm_pattern, os.path.join(folder_name, "fm_grating.png"))

    # Generate and save phase-modulated grating
    pm_pattern = pm_grating(width, height, frequency, phase_pattern, modulation_depth)
    save_pattern(pm_pattern, os.path.join(folder_name, "pm_grating.png"))

    # Generate and save moiré pattern
    moire = moire_pattern(width, height, 30, 32, 0, pi / 6)
    save_pattern(moire, os.path.join(folder_name, "moire_pattern.png"))

    print(f"Patterns saved in folder: {folder_name}")

# Run the main function to generate and save patterns
generate_and_save_patterns()
