# Copy Detection Pattern (CDP) Methods

## Overview

Copy Detection Patterns (CDPs) are security features designed to prevent counterfeiting by exploiting the inherent information loss that occurs during the print-scan-reprint process. This document covers the major algorithmic approaches for creating and verifying CDPs.

---

## Table of Contents

1. [Pseudo-Random Noise Generation](#1-pseudo-random-noise-generation)
2. [Stochastic Halftoning / Dithering](#2-stochastic-halftoning--dithering)
3. [Gabor Filter-Based Patterns](#3-gabor-filter-based-patterns)
4. [Fractal and Chaotic Systems](#4-fractal-and-chaotic-systems)
5. [Digital Watermarking Hybrids](#5-digital-watermarking-hybrids)
6. [Machine Learning Approaches](#6-machine-learning-approaches)
7. [Guilloche / Spirograph Algorithms](#7-guilloche--spirograph-algorithms)
8. [Modulated Gratings](#8-modulated-gratings)
9. [Verification Algorithms](#9-verification-algorithms)
10. [Comparison Matrix](#10-comparison-matrix)

---

## 1. Pseudo-Random Noise Generation

### Description

Generate deterministic noise patterns using cryptographic seeds or keys. The pattern appears random but is fully reproducible given the same seed, enabling verification without storing the full pattern.

### Techniques

#### 1.1 PRNG-Based Generation

Uses cryptographically secure pseudo-random number generators seeded with a secret key.

**Common PRNGs:**
- AES in Counter Mode (AES-CTR)
- ChaCha20
- Mersenne Twister (less secure, faster)
- Xorshift family

**Algorithm:**
```
function generate_prng_pattern(width, height, seed):
    prng = initialize_prng(seed)
    pattern = empty_matrix(width, height)

    for y in range(height):
        for x in range(width):
            pattern[x, y] = prng.next() % 256  # 8-bit grayscale

    return pattern
```

#### 1.2 Hash-Based Generation

Hash position coordinates concatenated with a secret key to determine pixel values.

**Algorithm:**
```
function generate_hash_pattern(width, height, secret_key):
    pattern = empty_matrix(width, height)

    for y in range(height):
        for x in range(width):
            input = concatenate(secret_key, x, y)
            hash_value = SHA256(input)
            pattern[x, y] = hash_value[0]  # First byte as pixel value

    return pattern
```

### Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| Seed/Key | Secret value for reproducibility | 128-256 bits |
| Resolution | Pattern density | 300-1200 DPI |
| Bit depth | Grayscale levels | 1-8 bits |

### Advantages

- Compact storage (only seed needed)
- Cryptographically secure
- Fast generation
- Easy verification against reference

### Disadvantages

- Requires secure key management
- Pattern quality depends on PRNG quality
- No inherent error correction

### Use Cases

- Document authentication
- Product labels
- Secure tickets

---

## 2. Stochastic Halftoning / Dithering

### Description

Convert continuous-tone images into binary dot patterns where the precise placement of dots is extremely sensitive to reproduction. The spatial distribution of dots carries the authentication information.

### Techniques

#### 2.1 Error Diffusion

Distributes quantization error to neighboring pixels, creating organic-looking patterns.

**Floyd-Steinberg Algorithm:**
```
function floyd_steinberg_dither(image):
    for y in range(height):
        for x in range(width):
            old_pixel = image[x, y]
            new_pixel = round(old_pixel / 255) * 255
            image[x, y] = new_pixel
            error = old_pixel - new_pixel

            # Distribute error to neighbors
            image[x+1, y  ] += error * 7/16
            image[x-1, y+1] += error * 3/16
            image[x,   y+1] += error * 5/16
            image[x+1, y+1] += error * 1/16

    return image
```

**Error Diffusion Kernels:**

| Algorithm | Kernel Size | Visual Quality |
|-----------|-------------|----------------|
| Floyd-Steinberg | 2x2 | Good |
| Jarvis-Judice-Ninke | 3x5 | Better |
| Stucki | 3x5 | Better |
| Burkes | 2x3 | Moderate |
| Sierra | 3x5 | Good |

#### 2.2 Blue Noise Dithering

Produces visually pleasing patterns with minimal low-frequency content.

**Void-and-Cluster Algorithm:**
```
function void_and_cluster(width, height):
    # Initialize with white noise
    pattern = random_binary_matrix(width, height)

    # Iteratively move pixels from clusters to voids
    while not converged:
        cluster_pos = find_tightest_cluster(pattern)
        void_pos = find_largest_void(pattern)
        swap(pattern[cluster_pos], pattern[void_pos])

    return pattern
```

#### 2.3 Ordered Dithering with Randomization

Combines structured dithering with random perturbations.

```
function randomized_ordered_dither(image, threshold_matrix, randomness):
    for y in range(height):
        for x in range(width):
            threshold = threshold_matrix[x % matrix_size, y % matrix_size]
            noise = random(-randomness, randomness)
            if image[x, y] > threshold + noise:
                output[x, y] = 1
            else:
                output[x, y] = 0

    return output
```

### Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| Kernel type | Error distribution pattern | Floyd-Steinberg, JJN |
| Threshold | Binarization threshold | 0.5 (normalized) |
| Noise injection | Additional randomness | 0-10% |

### Advantages

- Visually appealing patterns
- Well-understood degradation characteristics
- Works with existing print infrastructure

### Disadvantages

- Sensitive to print quality variations
- Requires careful calibration per printer
- Limited information density

### Use Cases

- Printed photographs with embedded authentication
- Artistic prints
- Packaging graphics

---

## 3. Gabor Filter-Based Patterns

### Description

Generate textures using oriented Gabor wavelets at specific frequencies and orientations. The human visual system is particularly sensitive to these patterns, making tampering visible, while the precise frequency content is difficult to reproduce.

### Mathematical Foundation

**2D Gabor Function:**
```
g(x, y) = exp(-(x'^2 + γ²y'^2) / (2σ²)) × cos(2πx'/λ + ψ)

where:
    x' = x·cos(θ) + y·sin(θ)
    y' = -x·sin(θ) + y·cos(θ)
```

**Parameters:**
- λ (lambda): Wavelength of the sinusoidal component
- θ (theta): Orientation of the normal to the parallel stripes
- ψ (psi): Phase offset
- σ (sigma): Standard deviation of the Gaussian envelope
- γ (gamma): Spatial aspect ratio

### Algorithm

```
function generate_gabor_pattern(width, height, params_list):
    pattern = zeros(width, height)

    for params in params_list:
        λ, θ, ψ, σ, γ = params

        for y in range(height):
            for x in range(width):
                x_centered = x - width/2
                y_centered = y - height/2

                x_prime = x_centered * cos(θ) + y_centered * sin(θ)
                y_prime = -x_centered * sin(θ) + y_centered * cos(θ)

                gaussian = exp(-(x_prime² + γ² * y_prime²) / (2 * σ²))
                sinusoid = cos(2π * x_prime / λ + ψ)

                pattern[x, y] += gaussian * sinusoid

    return normalize(pattern)
```

### Multi-Scale Gabor Patterns

```
function multi_scale_gabor(width, height, secret_key):
    pattern = zeros(width, height)

    # Derive parameters from key
    orientations = derive_orientations(secret_key, count=4)
    frequencies = derive_frequencies(secret_key, count=3)

    for θ in orientations:
        for λ in frequencies:
            weight = derive_weight(secret_key, θ, λ)
            gabor = generate_single_gabor(width, height, λ, θ)
            pattern += weight * gabor

    return normalize(pattern)
```

### Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| λ (wavelength) | Spatial frequency | 4-16 pixels |
| θ (orientation) | Pattern angle | 0°, 45°, 90°, 135° |
| σ (sigma) | Gaussian spread | λ × 0.5 |
| γ (aspect ratio) | Ellipticity | 0.5-1.0 |
| Num. filters | Complexity | 4-16 |

### Advantages

- Tunable to specific printer/scanner characteristics
- Grounded in human visual perception research
- Good resistance to geometric distortions

### Disadvantages

- Computationally intensive generation
- Requires frequency analysis for verification
- May produce visible artifacts

### Use Cases

- High-security documents
- Biometric templates
- Currency features

---

## 4. Fractal and Chaotic Systems

### Description

Leverage the extreme sensitivity to initial conditions exhibited by chaotic dynamical systems. Small changes in the reproduction process cause cascading differences that are easily detectable.

### Techniques

#### 4.1 Logistic Map

Simple one-dimensional chaotic system.

```
function logistic_map_pattern(width, height, r, x0):
    pattern = empty_matrix(width, height)
    x = x0  # Initial condition (0 < x0 < 1)

    for i in range(width * height):
        x = r * x * (1 - x)  # Logistic equation
        pixel_value = int(x * 255)
        pattern[i % width, i // width] = pixel_value

    return pattern

# Chaotic regime: r ≈ 3.9-4.0
```

#### 4.2 Arnold Cat Map

Area-preserving 2D chaotic transformation.

```
function arnold_cat_map(image, iterations):
    N = image.size
    result = image.copy()

    for _ in range(iterations):
        new_result = empty_like(result)
        for x in range(N):
            for y in range(N):
                new_x = (2*x + y) % N
                new_y = (x + y) % N
                new_result[new_x, new_y] = result[x, y]
        result = new_result

    return result
```

#### 4.3 Henon Map

Two-dimensional discrete-time dynamical system.

```
function henon_map_pattern(width, height, a, b, x0, y0):
    pattern = empty_matrix(width, height)
    x, y = x0, y0

    for i in range(width * height):
        x_new = 1 - a * x² + y
        y_new = b * x
        x, y = x_new, y_new

        # Map to pixel coordinates
        px = int((x + 1.5) / 3 * 255)
        py = int((y + 0.5) / 1 * 255)
        pattern[i % width, i // width] = (px + py) % 256

    return pattern

# Classic parameters: a = 1.4, b = 0.3
```

#### 4.4 Lorenz System

Continuous 3D chaotic system, discretized for pattern generation.

```
function lorenz_pattern(width, height, σ, ρ, β, initial_state, dt):
    x, y, z = initial_state
    pattern = empty_matrix(width, height)

    for i in range(width * height):
        # Euler integration
        dx = σ * (y - x)
        dy = x * (ρ - z) - y
        dz = x * y - β * z

        x += dx * dt
        y += dy * dt
        z += dz * dt

        # Project to pixel value
        value = int((x + 30) / 60 * 255) % 256
        pattern[i % width, i // width] = value

    return pattern

# Classic parameters: σ = 10, ρ = 28, β = 8/3
```

### Parameters

| System | Parameters | Chaotic Range |
|--------|------------|---------------|
| Logistic | r | 3.57 - 4.0 |
| Arnold Cat | iterations | Any positive integer |
| Henon | a, b | a ≈ 1.4, b ≈ 0.3 |
| Lorenz | σ, ρ, β | σ = 10, ρ = 28, β = 8/3 |

### Advantages

- High sensitivity to initial conditions
- Deterministic but unpredictable appearance
- Strong cryptographic properties
- Compact parameterization

### Disadvantages

- May require many iterations for visual randomness
- Some systems have periodic windows
- Numerical precision issues in floating-point

### Use Cases

- Cryptographic applications
- Tamper-evident seals
- Unique identifier generation

---

## 5. Digital Watermarking Hybrids

### Description

Embed authentication information in either the spatial or frequency domain of the pattern. Combines traditional watermarking techniques with CDP-specific requirements for print-scan resilience.

### Techniques

#### 5.1 DCT-Based Embedding

Modify Discrete Cosine Transform coefficients.

```
function dct_embed_pattern(image, message, strength):
    blocks = split_into_8x8_blocks(image)
    message_bits = to_binary(message)
    bit_index = 0

    for block in blocks:
        dct_block = DCT2D(block)

        # Embed in mid-frequency coefficients
        for (i, j) in mid_frequency_positions:
            if bit_index < len(message_bits):
                if message_bits[bit_index] == 1:
                    dct_block[i, j] = abs(dct_block[i, j]) + strength
                else:
                    dct_block[i, j] = -abs(dct_block[i, j]) - strength
                bit_index += 1

        block[:] = IDCT2D(dct_block)

    return reconstruct_image(blocks)
```

#### 5.2 DWT-Based Embedding

Embed in Discrete Wavelet Transform domain.

```
function dwt_embed_pattern(image, message, strength):
    # Perform 2-level DWT
    LL, (LH1, HL1, HH1), (LH2, HL2, HH2) = DWT2D(image, levels=2)

    message_bits = to_binary(message)

    # Embed in LH2 subband (horizontal details)
    for i, bit in enumerate(message_bits):
        x, y = index_to_position(i, LH2.shape)
        if bit == 1:
            LH2[x, y] += strength
        else:
            LH2[x, y] -= strength

    # Inverse transform
    return IDWT2D(LL, (LH1, HL1, HH1), (LH2, HL2, HH2))
```

#### 5.3 Spread Spectrum Embedding

Spread the signal across multiple frequencies for robustness.

```
function spread_spectrum_embed(image, message, key, chip_rate):
    # Generate spreading sequences
    prng = initialize_prng(key)

    for bit in message:
        # Generate pseudo-random spreading sequence
        sequence = [prng.next_float() - 0.5 for _ in range(chip_rate)]

        # Modulate by message bit
        if bit == 0:
            sequence = [-s for s in sequence]

        # Add to image in pseudo-random locations
        positions = generate_positions(prng, chip_rate, image.shape)
        for i, pos in enumerate(positions):
            image[pos] += sequence[i] * strength

    return image
```

### Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| Embedding strength | Signal magnitude | 5-50 (8-bit scale) |
| Chip rate | Spreading factor | 100-1000 |
| Frequency band | DCT/DWT region | Mid-frequency |
| Redundancy | Repetition factor | 3-10x |

### Advantages

- Can embed arbitrary data
- Well-studied robustness properties
- Supports error correction coding

### Disadvantages

- Trade-off between capacity and robustness
- May introduce visible artifacts
- Requires careful tuning for print-scan

### Use Cases

- Documents with embedded serial numbers
- Traceability applications
- Combined authentication and data storage

---

## 6. Machine Learning Approaches

### Description

Use neural networks to learn optimal pattern generation that maximizes distinguishability between original and copied versions while considering real-world printing and scanning variations.

### Techniques

#### 6.1 Generative Adversarial Networks (GANs)

Train competing networks for pattern generation and copy detection.

**Architecture:**
```
Generator G:
    Input: Random noise z, secret key k
    Output: CDP pattern

Discriminator D:
    Input: Pattern (original or copy)
    Output: Probability of being original

Print-Scan Simulator S:
    Input: Digital pattern
    Output: Simulated printed-and-scanned pattern
```

**Training Loop:**
```
function train_cdp_gan(epochs, batch_size):
    for epoch in range(epochs):
        # Generate patterns
        z = random_noise(batch_size)
        generated_patterns = G(z)

        # Simulate print-scan process
        simulated_copies = S(generated_patterns)

        # Train discriminator
        real_labels = ones(batch_size)
        fake_labels = zeros(batch_size)

        D_loss = binary_crossentropy(D(generated_patterns), real_labels) +
                 binary_crossentropy(D(simulated_copies), fake_labels)

        update_discriminator(D_loss)

        # Train generator to maximize discriminability
        G_loss = -binary_crossentropy(D(simulated_copies), fake_labels)

        update_generator(G_loss)
```

#### 6.2 Adversarial Training

Optimize patterns against multiple simulated attacks.

```
function adversarial_pattern_training(base_pattern, attack_models):
    pattern = base_pattern.clone()
    pattern.requires_grad = True

    optimizer = Adam([pattern])

    for iteration in range(max_iterations):
        total_loss = 0

        for attack in attack_models:
            attacked_pattern = attack(pattern)

            # Maximize difference between original and attacked
            difference = compute_difference(pattern, attacked_pattern)
            loss = -difference  # Negative because we maximize

            total_loss += loss

        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()

        # Clip to valid range
        pattern.data.clamp_(0, 255)

    return pattern
```

#### 6.3 CNN-Based Verification

Train a classifier to distinguish originals from copies.

```
class CDPVerifier(nn.Module):
    def __init__(self):
        self.conv1 = Conv2d(1, 32, kernel_size=3)
        self.conv2 = Conv2d(32, 64, kernel_size=3)
        self.conv3 = Conv2d(64, 128, kernel_size=3)
        self.pool = MaxPool2d(2)
        self.fc1 = Linear(128 * 8 * 8, 256)
        self.fc2 = Linear(256, 2)  # Original vs Copy

    def forward(self, x):
        x = relu(self.conv1(x))
        x = self.pool(x)
        x = relu(self.conv2(x))
        x = self.pool(x)
        x = relu(self.conv3(x))
        x = self.pool(x)
        x = flatten(x)
        x = relu(self.fc1(x))
        x = softmax(self.fc2(x))
        return x
```

#### 6.4 Print-Scan Simulation Network

Learn the print-scan degradation process.

```
class PrintScanSimulator(nn.Module):
    def __init__(self):
        # Encoder: capture print characteristics
        self.encoder = Sequential(
            Conv2d(1, 64, 3, padding=1),
            ReLU(),
            Conv2d(64, 128, 3, padding=1),
            ReLU()
        )

        # Noise injection
        self.noise_layer = GaussianNoise(std=0.1)

        # Decoder: simulate scan artifacts
        self.decoder = Sequential(
            Conv2d(128, 64, 3, padding=1),
            ReLU(),
            Conv2d(64, 1, 3, padding=1),
            Sigmoid()
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.noise_layer(x)
        x = self.decoder(x)
        return x
```

### Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| Network depth | Number of layers | 5-20 |
| Learning rate | Optimization step | 1e-4 to 1e-3 |
| Batch size | Training samples | 32-128 |
| Training epochs | Iterations | 100-1000 |

### Advantages

- Adapts to specific printer/scanner combinations
- Can optimize for multiple attack vectors
- Potentially superior performance to hand-crafted methods

### Disadvantages

- Requires large training datasets
- Computationally expensive training
- Black-box nature reduces interpretability
- May overfit to training conditions

### Use Cases

- High-volume authentication systems
- Adaptive security for evolving threats
- Research and development

---

## 7. Guilloche / Spirograph Algorithms

### Description

Generate intricate geometric patterns using parametric equations. The fine line work is extremely difficult to reproduce accurately, and the parameters serve as a secret key.

### Mathematical Foundation

**Basic Spirograph Equation:**
```
x(t) = (R - r) × cos(t) + d × cos((R - r)/r × t)
y(t) = (R - r) × sin(t) - d × sin((R - r)/r × t)
```

**Extended Multi-Frequency Form:**
```
x(t) = Σᵢ Aᵢ × cos(fᵢ × t + φᵢ)
y(t) = Σᵢ Bᵢ × sin(gᵢ × t + ψᵢ)
```

### Techniques

#### 7.1 Classic Spirograph

```
function spirograph(R, r, d, num_points):
    points = []

    # Calculate period
    period = 2π × LCM(R, r) / R

    for i in range(num_points):
        t = i × period / num_points

        x = (R - r) × cos(t) + d × cos((R - r)/r × t)
        y = (R - r) × sin(t) - d × sin((R - r)/r × t)

        points.append((x, y))

    return points
```

#### 7.2 Multi-Layer Guilloche

```
function multi_layer_guilloche(params_list, width, height):
    image = new_image(width, height)

    for params in params_list:
        R, r, d, amplitude, frequency, phase, line_width, color = params

        points = spirograph(R, r, d, num_points=10000)

        # Apply wave modulation
        modulated_points = []
        for i, (x, y) in enumerate(points):
            t = i / len(points) × 2π
            offset = amplitude × sin(frequency × t + phase)

            # Offset perpendicular to curve direction
            dx, dy = compute_normal(points, i)
            new_x = x + offset × dx
            new_y = y + offset × dy

            modulated_points.append((new_x, new_y))

        draw_curve(image, modulated_points, line_width, color)

    return image
```

#### 7.3 Lissajous-Based Patterns

```
function lissajous_pattern(a, b, delta, num_points):
    points = []

    for i in range(num_points):
        t = i × 2π / num_points

        x = sin(a × t + delta)
        y = sin(b × t)

        points.append((x, y))

    return points
```

#### 7.4 Rose Curves

```
function rose_curve(k, num_points, modulation_params):
    points = []

    for i in range(num_points):
        θ = i × 2π × k / num_points

        # Base rose curve
        r = cos(k × θ)

        # Apply modulation
        r += modulation_params.amplitude × sin(modulation_params.freq × θ)

        x = r × cos(θ)
        y = r × sin(θ)

        points.append((x, y))

    return points
```

### Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| R (outer radius) | Fixed circle radius | 100-500 |
| r (inner radius) | Rolling circle radius | 10-100 |
| d (pen distance) | Offset from center | 0-r |
| Line width | Stroke thickness | 0.1-1.0 pt |
| Layers | Number of overlays | 3-10 |

### Advantages

- Visually appealing and professional
- Long history in security printing
- Parameters form natural secret key
- Scalable to any resolution

### Disadvantages

- Computationally intensive for fine detail
- Requires high-resolution printing
- Limited information density

### Use Cases

- Certificates and diplomas
- Currency and bonds
- Official documents
- Brand protection

---

## 8. Modulated Gratings

### Description

Create line patterns with controlled frequency and phase modulation. When copied, the precise modulation is lost, and the resulting moiré patterns or frequency shifts reveal tampering.

### Techniques

#### 8.1 Sinusoidal Gratings

```
function sinusoidal_grating(width, height, frequency, orientation, phase):
    pattern = empty_matrix(width, height)

    for y in range(height):
        for x in range(width):
            # Rotate coordinate system
            x_rot = x × cos(orientation) + y × sin(orientation)

            # Generate sinusoidal value
            value = (sin(2π × frequency × x_rot + phase) + 1) / 2

            pattern[x, y] = int(value × 255)

    return pattern
```

#### 8.2 Frequency-Modulated Gratings

```
function fm_grating(width, height, base_freq, modulation_freq, modulation_depth):
    pattern = empty_matrix(width, height)

    for y in range(height):
        for x in range(width):
            # Instantaneous frequency varies with position
            inst_freq = base_freq + modulation_depth × sin(2π × modulation_freq × x)

            # Integrate frequency to get phase
            phase = integrate_frequency(inst_freq, x)

            value = (sin(phase) + 1) / 2
            pattern[x, y] = int(value × 255)

    return pattern
```

#### 8.3 Phase-Modulated Gratings

```
function pm_grating(width, height, frequency, phase_pattern, modulation_depth):
    pattern = empty_matrix(width, height)

    for y in range(height):
        for x in range(width):
            # Phase varies according to secret pattern
            local_phase = phase_pattern[x, y] × modulation_depth

            value = (sin(2π × frequency × x + local_phase) + 1) / 2
            pattern[x, y] = int(value × 255)

    return pattern
```

#### 8.4 Moiré-Inducing Patterns

```
function moire_pattern(width, height, freq1, freq2, angle1, angle2):
    # Two slightly different gratings that create moiré when copied
    grating1 = sinusoidal_grating(width, height, freq1, angle1, 0)
    grating2 = sinusoidal_grating(width, height, freq2, angle2, 0)

    # Multiplicative combination
    combined = (grating1 / 255.0) × (grating2 / 255.0) × 255

    return combined.astype(uint8)
```

### Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| Base frequency | Line density | 50-200 lines/inch |
| Modulation depth | Variation amplitude | 5-20% |
| Orientation | Grating angle | 0°-180° |
| Phase offset | Initial phase | 0-2π |

### Advantages

- Strong theoretical foundation
- Visible tampering through moiré
- Works with standard printing

### Disadvantages

- Sensitive to print alignment
- May create visual distractions
- Limited to certain design contexts

### Use Cases

- Background patterns
- Security papers
- Hologram-like effects
- Anti-photocopy features

---

## 9. Verification Algorithms

### Overview

Verification algorithms determine whether a scanned pattern is an original print or a copy. These methods complement the generation algorithms described above.

### Techniques

#### 9.1 Correlation-Based Verification

```
function correlation_verify(scanned, reference, threshold):
    # Normalize both images
    scanned_norm = (scanned - mean(scanned)) / std(scanned)
    reference_norm = (reference - mean(reference)) / std(reference)

    # Compute normalized cross-correlation
    correlation = sum(scanned_norm × reference_norm) / size(scanned)

    # Original prints have high correlation
    # Copies have degraded correlation
    return correlation > threshold

# Typical threshold: 0.7-0.9
```

#### 9.2 Structural Similarity Index (SSIM)

```
function ssim_verify(scanned, reference, threshold):
    # Constants for stability
    C1 = (0.01 × 255)²
    C2 = (0.03 × 255)²

    # Compute means
    μ_s = gaussian_filter(scanned, σ=1.5)
    μ_r = gaussian_filter(reference, σ=1.5)

    # Compute variances and covariance
    σ_s² = gaussian_filter(scanned², σ=1.5) - μ_s²
    σ_r² = gaussian_filter(reference², σ=1.5) - μ_r²
    σ_sr = gaussian_filter(scanned × reference, σ=1.5) - μ_s × μ_r

    # SSIM formula
    ssim = ((2×μ_s×μ_r + C1) × (2×σ_sr + C2)) /
           ((μ_s² + μ_r² + C1) × (σ_s² + σ_r² + C2))

    return mean(ssim) > threshold
```

#### 9.3 Histogram Analysis

```
function histogram_verify(scanned, expected_histogram, threshold):
    # Compute histogram of scanned pattern
    scanned_hist = compute_histogram(scanned, bins=256)

    # Print-scan process typically:
    # - Reduces contrast (histogram narrows)
    # - Shifts midtones
    # - Loses extreme values

    # Compute histogram distance
    distance = earth_movers_distance(scanned_hist, expected_histogram)

    # Originals have small distance, copies have large distance
    return distance < threshold
```

#### 9.4 Frequency Domain Analysis

```
function frequency_verify(scanned, reference, threshold):
    # Compute 2D FFT
    scanned_fft = fft2d(scanned)
    reference_fft = fft2d(reference)

    # Compare magnitude spectra
    scanned_mag = abs(scanned_fft)
    reference_mag = abs(reference_fft)

    # High frequencies are lost in copying
    high_freq_ratio = compare_high_frequencies(scanned_mag, reference_mag)

    return high_freq_ratio > threshold
```

#### 9.5 Machine Learning Classification

```
function ml_verify(scanned, model):
    # Preprocess
    normalized = normalize_for_model(scanned)

    # Run through trained classifier
    prediction = model.predict(normalized)

    # Output: [probability_original, probability_copy]
    return prediction[0] > 0.5, prediction[0]
```

### Verification Decision Framework

```
function comprehensive_verify(scanned, reference, thresholds):
    scores = {}

    # Run multiple verification methods
    scores['correlation'] = correlation_verify(scanned, reference)
    scores['ssim'] = ssim_verify(scanned, reference)
    scores['histogram'] = histogram_verify(scanned, reference)
    scores['frequency'] = frequency_verify(scanned, reference)

    # Weighted voting
    weights = {'correlation': 0.3, 'ssim': 0.3,
               'histogram': 0.2, 'frequency': 0.2}

    final_score = sum(scores[k] × weights[k] for k in scores)

    # Multi-level decision
    if final_score > 0.8:
        return "AUTHENTIC", final_score
    elif final_score > 0.5:
        return "SUSPICIOUS", final_score
    else:
        return "COUNTERFEIT", final_score
```

---

## 10. Comparison Matrix

### Generation Methods Comparison

| Method | Complexity | Security | Visual Appeal | Print Requirements | Verification Ease |
|--------|------------|----------|---------------|-------------------|-------------------|
| PRNG Noise | Low | High | Low | Standard | Easy |
| Halftoning | Medium | Medium | High | Standard | Medium |
| Gabor Filters | High | High | Medium | High-res | Complex |
| Chaotic Systems | Medium | High | Low | Standard | Medium |
| Watermarking | High | Medium | Invisible | Standard | Complex |
| Machine Learning | Very High | Very High | Variable | Standard | Complex |
| Guilloche | Medium | High | Very High | High-res | Medium |
| Modulated Gratings | Medium | Medium | Medium | High-res | Easy |

### Use Case Recommendations

| Application | Recommended Methods |
|-------------|---------------------|
| Currency | Guilloche + Gabor + ML Verification |
| ID Documents | PRNG Noise + Watermarking |
| Product Labels | Halftoning + QR Integration |
| Certificates | Guilloche + Modulated Gratings |
| Tickets | PRNG Noise + Simple Correlation |
| Pharmaceuticals | Chaotic Patterns + ML Verification |

### Implementation Complexity

| Method | Development Time | Expertise Required | Infrastructure |
|--------|------------------|-------------------|----------------|
| PRNG Noise | Low | Basic crypto | Standard |
| Halftoning | Low-Medium | Image processing | Standard |
| Gabor Filters | Medium | Signal processing | Standard |
| Chaotic Systems | Medium | Math/Crypto | Standard |
| Watermarking | Medium-High | DSP expertise | Standard |
| Machine Learning | High | ML expertise | GPU training |
| Guilloche | Medium | Graphics/Math | Vector graphics |
| Modulated Gratings | Medium | Physics/Optics | High-res print |

---

## References

1. Picard, J. (2004). Digital authentication with copy-detection patterns. *Optical Security and Counterfeit Deterrence Techniques V*.

2. Tkachenko, I., et al. (2016). Two-level QR code for private message sharing and document authentication. *IEEE Transactions on Information Forensics and Security*.

3. Chu, D., et al. (2013). Randomized local binary features for copy detection patterns. *Document Recognition and Retrieval XX*.

4. Villán, R., et al. (2006). Text authentication using localized stochastic halftoning. *Security, Steganography, and Watermarking of Multimedia Contents VIII*.

5. Wong, P. W., & Memon, N. (2001). Secret and public key image watermarking schemes for image authentication and ownership verification. *IEEE Transactions on Image Processing*.

---

## Appendix A: Implementation Checklist

### Before Implementation
- [ ] Define security requirements
- [ ] Analyze print/scan characteristics of target system
- [ ] Choose appropriate method(s)
- [ ] Design key management strategy

### During Implementation
- [ ] Implement generation algorithm
- [ ] Implement verification algorithm
- [ ] Test with actual print/scan hardware
- [ ] Calibrate thresholds
- [ ] Test against various copy methods

### After Implementation
- [ ] Document parameters and thresholds
- [ ] Establish monitoring for false positives/negatives
- [ ] Plan for algorithm updates
- [ ] Train verification operators

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| CDP | Copy Detection Pattern - A security feature that degrades detectably when copied |
| DPI | Dots Per Inch - Measure of print resolution |
| PSA | Print-Scan Attack - The process of copying by printing then scanning |
| PRNG | Pseudo-Random Number Generator |
| DCT | Discrete Cosine Transform |
| DWT | Discrete Wavelet Transform |
| SSIM | Structural Similarity Index Measure |
| Moiré | Interference pattern created when two gratings overlap |
| Guilloche | Intricate repetitive design using parametric curves |
| Halftoning | Converting continuous tone to binary dots |
