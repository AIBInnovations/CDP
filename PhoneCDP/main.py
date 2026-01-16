"""
Phone-Camera-Friendly CDP Pattern Generator

This module generates Copy Detection Patterns optimized for phone camera verification.
The patterns use macro-scale features that survive phone photography and provide
clear visual differences between originals and copies.

Security Layers:
1. Modulated Gratings - Primary (Moiré detection)
2. PRNG Macro-blocks - Secondary (Statistical verification)
3. RGB Color Perturbations - Color channel security
4. Fiducial Markers - Alignment and geometric security
5. QR Code - Data embedding and server verification
6. Enrollment Averaging - Verification robustness (verification-side)

Pattern Specifications:
- Size: 512x512 pixels (phone-friendly)
- Print DPI: 300 DPI
- Physical size: ~1.7" x 1.7"
- Verification: Phone camera (10-15 DPI effective)
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import qrcode
from datetime import datetime
import os


# ============================================================================
# STEP 1: Modulated Gratings Generator (Primary Security Layer)
# ============================================================================

def generate_sinusoidal_grating(width, height, frequency, orientation, phase=0):
    """
    Generate a sinusoidal grating pattern.

    When this pattern is copied (print→scan→reprint), the rescreening process
    creates visible moiré interference patterns that are easily detected by
    phone cameras.

    Args:
        width: Pattern width in pixels
        height: Pattern height in pixels
        frequency: Cycles per image width (7-15 recommended for phone visibility)
        orientation: Angle in degrees (0-180)
        phase: Phase shift in radians

    Returns:
        Grayscale pattern (0-255)
    """
    # Create coordinate grid
    x = np.arange(width)
    y = np.arange(height)
    X, Y = np.meshgrid(x, y)

    # Convert orientation to radians
    theta = np.radians(orientation)

    # Rotate coordinates based on orientation
    x_rotated = X * np.cos(theta) + Y * np.sin(theta)

    # Generate sinusoidal grating
    grating = np.sin(2 * np.pi * frequency * x_rotated / width + phase)

    # Normalize to 0-255 range
    grating_normalized = ((grating + 1) / 2 * 255).astype(np.uint8)

    return grating_normalized


def generate_frequency_modulated_grating(width, height, base_freq, mod_freq, mod_depth):
    """
    Generate a frequency-modulated (FM) grating.

    The frequency varies across the pattern, making it even harder to reproduce
    accurately. Copies will show irregular moiré patterns.

    Args:
        width: Pattern width in pixels
        height: Pattern height in pixels
        base_freq: Base frequency (cycles per width)
        mod_freq: Modulation frequency
        mod_depth: Modulation depth (0-1)

    Returns:
        Grayscale FM grating pattern
    """
    x = np.arange(width)
    y = np.arange(height)
    X, Y = np.meshgrid(x, y)

    # Calculate instantaneous frequency at each position
    freq_modulation = base_freq * (1 + mod_depth * np.sin(2 * np.pi * mod_freq * X / width))

    # Integrate frequency to get phase
    phase = np.cumsum(freq_modulation, axis=1) * 2 * np.pi / width

    # Generate FM grating
    grating = np.sin(phase)

    # Normalize to 0-255
    grating_normalized = ((grating + 1) / 2 * 255).astype(np.uint8)

    return grating_normalized


def generate_moire_pattern(width, height, freq1, freq2, angle1, angle2):
    """
    Generate a pattern designed to create moiré interference when copied.

    By overlaying two gratings at slightly different frequencies/angles,
    we create a pattern that will show dramatic moiré effects when reprinted.

    Args:
        width, height: Pattern dimensions
        freq1, freq2: Frequencies of the two gratings
        angle1, angle2: Orientations of the two gratings

    Returns:
        Combined moiré pattern
    """
    # Generate two gratings
    grating1 = generate_sinusoidal_grating(width, height, freq1, angle1)
    grating2 = generate_sinusoidal_grating(width, height, freq2, angle2)

    # Combine gratings (multiplication creates moiré)
    combined = cv2.addWeighted(grating1, 0.5, grating2, 0.5, 0)

    return combined


# ============================================================================
# STEP 2: PRNG Macro-Block Generator (Secondary Security Layer)
# ============================================================================

def generate_prng_macro_pattern(width, height, seed, block_size=8):
    """
    Generate PRNG-based pattern with macro-scale blocks.

    Instead of pixel-level randomness, we use larger blocks (8x8 pixels) that
    are visible to phone cameras. Each block is deterministically generated
    from the seed, making the pattern unique and reproducible.

    Args:
        width, height: Pattern dimensions (should be divisible by block_size)
        seed: Integer seed for reproducibility
        block_size: Size of each macro block in pixels (8 recommended)

    Returns:
        Grayscale pattern with macro blocks
    """
    np.random.seed(seed)

    # Calculate number of blocks
    blocks_x = width // block_size
    blocks_y = height // block_size

    # Generate random block values
    block_values = np.random.randint(0, 256, size=(blocks_y, blocks_x), dtype=np.uint8)

    # Upscale blocks to full size
    pattern = np.repeat(np.repeat(block_values, block_size, axis=0), block_size, axis=1)

    # Trim to exact dimensions if needed
    pattern = pattern[:height, :width]

    return pattern


# ============================================================================
# STEP 3: RGB Color Perturbations (Color Security Layer)
# ============================================================================

def add_rgb_perturbations(pattern_gray, seed=42, intensity=25, block_size=8):
    """
    Add subtle RGB color variations at macro-block scale.

    Phone cameras capture color information that degrades predictably during
    copying. This layer exploits color channel differences that are lost when
    a pattern is reprinted.

    Args:
        pattern_gray: Input grayscale pattern
        seed: Random seed for reproducibility
        intensity: Maximum color shift per channel (0-50 recommended)
        block_size: Size of color perturbation blocks (8px recommended)

    Returns:
        RGB pattern with color perturbations

    Verification:
        Original: High inter-channel variance (R≠G≠B per block)
        Copy: Reduced variance (color averaging during reprint)
        Phone metric: Compare R-G, R-B, G-B channel differences
    """
    np.random.seed(seed)
    h, w = pattern_gray.shape

    # Convert grayscale to RGB
    pattern_rgb = cv2.cvtColor(pattern_gray, cv2.COLOR_GRAY2RGB)

    # Apply per-block color perturbations
    blocks_y = h // block_size
    blocks_x = w // block_size

    print(f"  Adding RGB perturbations to {blocks_y}x{blocks_x} blocks...")

    for i in range(blocks_y):
        for j in range(blocks_x):
            y_start = i * block_size
            x_start = j * block_size
            y_end = min(y_start + block_size, h)
            x_end = min(x_start + block_size, w)

            # Generate deterministic color shifts for this block
            r_shift = np.random.randint(-intensity, intensity)
            g_shift = np.random.randint(-intensity, intensity)
            b_shift = np.random.randint(-intensity, intensity)

            # Apply shifts to each channel
            pattern_rgb[y_start:y_end, x_start:x_end, 0] = np.clip(
                pattern_rgb[y_start:y_end, x_start:x_end, 0].astype(np.int16) + r_shift, 0, 255
            ).astype(np.uint8)
            pattern_rgb[y_start:y_end, x_start:x_end, 1] = np.clip(
                pattern_rgb[y_start:y_end, x_start:x_end, 1].astype(np.int16) + g_shift, 0, 255
            ).astype(np.uint8)
            pattern_rgb[y_start:y_end, x_start:x_end, 2] = np.clip(
                pattern_rgb[y_start:y_end, x_start:x_end, 2].astype(np.int16) + b_shift, 0, 255
            ).astype(np.uint8)

    return pattern_rgb


# ============================================================================
# STEP 4: Fiducial Markers (Alignment and Geometric Security)
# ============================================================================

def add_fiducial_markers(pattern, marker_size=20, marker_color=0):
    """
    Add asymmetric alignment markers in corners.

    Fiducial markers help phone apps:
    - Auto-detect pattern boundaries
    - Correct perspective distortion
    - Detect rotation/flip attacks
    - Enable precise alignment for comparison

    Args:
        pattern: Input pattern (grayscale or RGB)
        marker_size: Size of markers in pixels (20 recommended)
        marker_color: Color value (0=black, 255=white)

    Returns:
        Pattern with fiducial markers

    Security:
        - Asymmetric design prevents 180° rotation attacks
        - Enables homography correction for angled photos
        - Detects cropping or geometric manipulation
    """
    h, w = pattern.shape[:2]
    is_rgb = len(pattern.shape) == 3

    print(f"  Adding fiducial markers (size: {marker_size}px)...")

    # Ensure marker_color is tuple for RGB, int for grayscale
    color = (marker_color, marker_color, marker_color) if is_rgb else marker_color

    # Top-left: L-shape marker
    pattern[0:marker_size, 0:5] = color  # Vertical bar
    pattern[0:5, 0:marker_size] = color  # Horizontal bar

    # Top-right: T-shape marker (asymmetric)
    pattern[0:marker_size, w-5:w] = color  # Vertical bar
    pattern[0:5, w-marker_size:w] = color  # Horizontal bar

    # Bottom-left: Inverted L-shape (asymmetric)
    pattern[h-marker_size:h, 0:5] = color  # Vertical bar
    pattern[h-5:h, 0:marker_size] = color  # Horizontal bar

    # Bottom-right: Cross marker (different from others)
    pattern[h-marker_size:h, w-5:w] = color  # Vertical bar
    pattern[h-5:h, w-marker_size:w] = color  # Horizontal bar
    pattern[h-marker_size//2-2:h-marker_size//2+3, w-marker_size:w-5] = color  # Horizontal cross

    return pattern


# ============================================================================
# STEP 5: QR Code Overlay (Data Embedding Layer)
# ============================================================================

def overlay_qr_code(pattern, data="", size=120, position=None):
    """
    Generate and overlay a QR code on the pattern.

    The QR code encodes:
    - Serial number
    - Verification URL
    - Encrypted item ID

    Args:
        pattern: Input pattern (grayscale or RGB)
        data: Data to encode in QR code
        size: QR code size in pixels (120 recommended for phone scanning)
        position: (x, y) position (None = center)

    Returns:
        Pattern with QR code overlay
    """
    # Generate QR code
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

    # Resize QR code
    qr_resized = cv2.resize(qr_array, (size, size), interpolation=cv2.INTER_NEAREST)

    # Handle RGB or grayscale pattern
    is_rgb = len(pattern.shape) == 3

    # Calculate position (center if not specified)
    if position is None:
        h, w = pattern.shape[:2]
        position = ((w - size) // 2, (h - size) // 2)

    # Overlay QR code
    x, y = position
    qr_h, qr_w = qr_resized.shape

    # Blend QR code with pattern (80% QR, 20% pattern for visibility)
    pattern_copy = pattern.copy()

    if is_rgb:
        # For RGB, convert QR to RGB and blend each channel
        qr_rgb = cv2.cvtColor(qr_resized, cv2.COLOR_GRAY2RGB)
        pattern_copy[y:y+qr_h, x:x+qr_w] = cv2.addWeighted(
            pattern_copy[y:y+qr_h, x:x+qr_w], 0.2, qr_rgb, 0.8, 0
        )
    else:
        # For grayscale, blend directly
        pattern_copy[y:y+qr_h, x:x+qr_w] = cv2.addWeighted(
            pattern_copy[y:y+qr_h, x:x+qr_w], 0.2, qr_resized, 0.8, 0
        )

    return pattern_copy


# ============================================================================
# STEP 6: Enrollment Averaging (Verification Robustness Layer)
# ============================================================================

def compute_enrollment_reference(captures):
    """
    Create a robust reference by averaging multiple phone captures.

    During enrollment, the genuine pattern is photographed multiple times.
    This separates:
    - Printing variations (consistent across captures)
    - Photography variations (noise - averages out)

    Args:
        captures: List of phone photos of the same genuine pattern
                 (numpy arrays, aligned)

    Returns:
        Averaged reference pattern

    Usage:
        reference = compute_enrollment_reference([photo1, photo2, photo3, photo4, photo5])
        # Save reference for later verification
    """
    if len(captures) < 3:
        raise ValueError("Need at least 3 captures for reliable enrollment")

    # Ensure all captures are same size
    h, w = captures[0].shape[:2]
    for cap in captures:
        if cap.shape[:2] != (h, w):
            raise ValueError("All captures must be aligned and same size")

    # Average the captures
    reference = np.mean(captures, axis=0).astype(np.uint8)

    print(f"  Created enrollment reference from {len(captures)} captures")

    return reference


def extract_color_channel_features(pattern_rgb):
    """
    Extract color channel statistics for verification.

    Computes inter-channel differences that degrade during copying:
    - R-G difference
    - R-B difference
    - G-B difference
    - Per-channel variance

    Args:
        pattern_rgb: RGB pattern

    Returns:
        Dictionary of color features
    """
    # Split channels
    r, g, b = cv2.split(pattern_rgb)

    # Compute inter-channel differences
    features = {
        'r_g_diff': np.mean(np.abs(r.astype(np.float32) - g.astype(np.float32))),
        'r_b_diff': np.mean(np.abs(r.astype(np.float32) - b.astype(np.float32))),
        'g_b_diff': np.mean(np.abs(g.astype(np.float32) - b.astype(np.float32))),
        'r_variance': np.var(r),
        'g_variance': np.var(g),
        'b_variance': np.var(b),
        'total_color_variance': np.var(r) + np.var(g) + np.var(b)
    }

    return features


def detect_moire_interference(pattern_gray):
    """
    Detect moiré interference patterns using FFT analysis.

    Original patterns have clean frequency spectrum.
    Copied patterns show additional frequency peaks (moiré).

    Args:
        pattern_gray: Grayscale pattern (or converted from RGB)

    Returns:
        moiré_score: 0.0-1.0 (0=clean, 1=heavy moiré)
    """
    # Apply FFT
    f_transform = np.fft.fft2(pattern_gray)
    f_shift = np.fft.fftshift(f_transform)
    magnitude_spectrum = np.abs(f_shift)

    # Analyze spectrum for unexpected peaks (moiré indicators)
    # This is a simplified version - full implementation would be more sophisticated
    h, w = magnitude_spectrum.shape
    center_y, center_x = h // 2, w // 2

    # Exclude DC component (center)
    magnitude_spectrum[center_y-5:center_y+5, center_x-5:center_x+5] = 0

    # Compute energy in mid-frequency bands (where moiré appears)
    mid_freq_energy = np.sum(magnitude_spectrum[center_y-h//4:center_y+h//4,
                                                center_x-w//4:center_x+w//4])
    total_energy = np.sum(magnitude_spectrum)

    # Moiré score: ratio of mid-frequency to total energy
    moire_score = mid_freq_energy / (total_energy + 1e-10)

    # Normalize to 0-1 range (empirically determined threshold)
    moire_score = min(moire_score / 0.5, 1.0)

    return moire_score


# ============================================================================
# Main Generation Function
# ============================================================================

def main():
    """
    Generate phone-camera-friendly CDP pattern step by step.
    """
    # Configuration
    PATTERN_SIZE = (512, 512)  # Phone-friendly size
    SEED = 42
    SERIAL_NUMBER = "SN-2026-00001"
    QR_DATA = f"https://verify.ninehawks.com/{SERIAL_NUMBER}"

    # Create output directory
    output_dir = "generated_patterns"
    os.makedirs(output_dir, exist_ok=True)

    print("="*70)
    print("Phone-Camera-Friendly CDP Pattern Generator")
    print("="*70)
    print(f"Pattern size: {PATTERN_SIZE[0]}x{PATTERN_SIZE[1]} pixels")
    print(f"Serial number: {SERIAL_NUMBER}")
    print(f"Verification URL: {QR_DATA}")
    print(f"Security Seed: {SEED}")
    print()

    # Step 1: Generate modulated grating (Primary Security)
    print("Step 1: Generating modulated grating pattern...")
    print("  Using frequency-modulated grating for enhanced moiré detection")
    grating = generate_frequency_modulated_grating(
        width=PATTERN_SIZE[0],
        height=PATTERN_SIZE[1],
        base_freq=10,      # 10 cycles per width (phone-visible)
        mod_freq=2,        # Modulation frequency
        mod_depth=0.3      # 30% frequency modulation
    )
    print(f"  Generated {PATTERN_SIZE[0]}x{PATTERN_SIZE[1]} FM grating")

    # Step 2: Add PRNG macro blocks (Secondary Security)
    print("\nStep 2: Adding PRNG macro-block pattern...")
    prng_pattern = generate_prng_macro_pattern(
        width=PATTERN_SIZE[0],
        height=PATTERN_SIZE[1],
        seed=SEED,
        block_size=8
    )
    print(f"  Generated {(PATTERN_SIZE[0]//8)}x{(PATTERN_SIZE[1]//8)} blocks (8x8 pixels each)")

    # Combine grating and PRNG (50-50 blend)
    print("  Blending grating with PRNG pattern...")
    combined = cv2.addWeighted(grating, 0.5, prng_pattern, 0.5, 0)

    # Step 3: Add RGB color perturbations (Color Security)
    print("\nStep 3: Adding RGB color perturbations...")
    pattern_rgb = add_rgb_perturbations(
        pattern_gray=combined,
        seed=SEED,
        intensity=25,
        block_size=8
    )

    # Step 4: Add fiducial markers (Alignment & Geometric Security)
    print("\nStep 4: Adding fiducial markers...")
    pattern_with_markers = add_fiducial_markers(
        pattern=pattern_rgb,
        marker_size=20,
        marker_color=0  # Black markers
    )

    # Step 5: Overlay QR code (Data Embedding)
    print("\nStep 5: Overlaying QR code...")
    final_pattern = overlay_qr_code(
        pattern=pattern_with_markers,
        data=QR_DATA,
        size=120
    )
    print(f"  QR code embedded: {QR_DATA}")

    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"phone_cdp_{timestamp}.png")

    # Save the pattern
    print("\nStep 6: Saving pattern...")
    cv2.imwrite(filename, cv2.cvtColor(final_pattern, cv2.COLOR_RGB2BGR))
    print(f"  Saved to: {filename}")

    # Extract and display color features (for reference)
    print("\nPattern Analysis:")
    color_features = extract_color_channel_features(final_pattern)
    print(f"  R-G channel difference: {color_features['r_g_diff']:.2f}")
    print(f"  R-B channel difference: {color_features['r_b_diff']:.2f}")
    print(f"  G-B channel difference: {color_features['g_b_diff']:.2f}")
    print(f"  Total color variance: {color_features['total_color_variance']:.2f}")

    # Display the pattern
    print("\nGenerating visualization...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # Full pattern
    axes[0].imshow(final_pattern)
    axes[0].set_title(f"Phone CDP Pattern\n{SERIAL_NUMBER}", fontsize=12, fontweight='bold')
    axes[0].axis('off')

    # Zoomed region (to show detail)
    zoom_region = final_pattern[100:200, 100:200]
    axes[1].imshow(zoom_region)
    axes[1].set_title("Zoomed Detail (100x100 region)", fontsize=12)
    axes[1].axis('off')

    plt.tight_layout()
    plt.savefig(filename.replace('.png', '_visualization.png'), dpi=150, bbox_inches='tight')
    plt.show()

    print()
    print("="*70)
    print("Pattern Generation Complete!")
    print("="*70)
    print(f"Filename: {filename}")
    print(f"Pattern size: {PATTERN_SIZE[0]}x{PATTERN_SIZE[1]} pixels")
    print(f"Print at 300 DPI: {PATTERN_SIZE[0]/300:.2f}\" x {PATTERN_SIZE[1]/300:.2f}\"")
    print(f"Serial number: {SERIAL_NUMBER}")
    print()
    print("Security Layers Implemented:")
    print("  [+] Layer 1: Modulated gratings (moiré detection)")
    print("  [+] Layer 2: PRNG macro-blocks (uniqueness)")
    print("  [+] Layer 5: RGB color perturbations (color security)")
    print("  [+] Layer 11: Fiducial markers (alignment)")
    print("  [+] QR Code: Data embedding")
    print("  [+] Layer 8: Enrollment averaging (verification-side)")
    print()
    print("Verification Methods:")
    print("  1. Visual: Check for moiré patterns in copies")
    print("  2. QR Scan: Verify serial number")
    print("  3. Phone App: Color + moiré analysis")
    print("="*70)


if __name__ == "__main__":
    main()
