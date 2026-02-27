-----

# scintiPulses

<div align="center">

<img src="scintiPulses_logo.jpg" alt="scintiPulses Logo" width="300"/>

**Realistic Simulation of Scintillation Detector Signals**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-stable-green)
![BIPM](https://img.shields.io/badge/maintained%20by-BIPM-005696)

</div>

-----

## 📖 Overview

**scintiPulses** is a Python package designed to generate high-fidelity photodetector signals from scintillation detectors. It models the complete signal chain—from the initial energy deposition to the final digitized output—incorporating key photochemical processes, electronic effects, and digitization artifacts.

This tool is ideal for post-processing data from Monte Carlo simulation frameworks (e.g., Geant4, MCNP, FLUKA), transforming raw energy deposition timestamps into realistic pulse waveforms for algorithm testing and detector design.

-----

## ✨ Key Features

  * **Physics-Based Modeling:** Simulates time-dependent fluorescence including prompt and delayed components.
  * **Photodetector Physics:** Incorporates Quantum shot noise, after-pulses, and thermionic (dark) noise.
  * **Electronic Simulation:** Models Johnson-Nyquist thermal noise and signal shaping.
  * **Analog Filtering:** Simulates RC preamplifiers and CR$^{n}$ fast shapers.
  * **Digitization:** Includes anti-aliasing low-pass filtering, ADC quantization, and saturation effects.

Technical details and validation can be found in:

> **DOI:** [https://doi.org/10.1051/epjconf/202533810001](https://doi.org/10.1051/epjconf/202533810001)

-----

## 📦 Installation

You can install `scintiPulses` directly via pip:

```bash
pip install scintiPulses
```

-----

## 🚀 Quick Start

The following example demonstrates how to simulate a pulse from a 100 keV energy deposition, including electronic shaping and digitization.

```python
import numpy as np
import matplotlib.pyplot as plt
import scintipulses.scintiPulses as sp

# 1. Define Energy Deposition (1000 events of 100 keV)
Y = 100 * np.ones(1000)

# 2. Run Simulation
# Returns the time vector (t) and signal stages (v0 to v8)
results = sp.scintiPulses(
    Y,
    tN=20e-6,           # Duration: 20 us
    fS=1e8,             # Sample Rate: 100 MHz
    tau1=250e-9,        # Scintillator decay constant
    L=1,                # Light yield
    electronicNoise=True,
    sigmaRMS=0.005,     # Add electronic noise
    pream=True,         # Enable Preamplifier
    tauRC=10e-6,
    digitization=True,  # Enable Digitization
    R=14,               # 14-bit ADC
    fc=4e7
)

# Unpack key results (t is index 0, v8 is final digitized output)
time_axis = results[0]
final_signal = results[8]

# 3. Visualization
plt.figure(figsize=(10, 6))
plt.plot(time_axis * 1e6, final_signal, label='Digitized Output (v8)')
plt.xlabel("Time ($\mu$s)")
plt.ylabel("Voltage (V)")
plt.title("Simulated Scintillation Pulse")
plt.grid(True, alpha=0.5)
plt.legend()
plt.show()
```

-----

## 📡 The Signal Chain (Outputs)

The function returns a tuple containing the time vector and the signal at various stages of processing. This allows you to inspect the signal evolution.

| Variable | Unit | Stage Description |
| :--- | :--- | :--- |
| **t** | s | Time base vector. |
| **v0** | $e^-$ | Idealized scintillation signal (charge). |
| **v1** | $e^-$ | **Shot Noise:** Quantized photons added. |
| **v2** | $e^-$ | **After-pulses:** Spurious pulses added (if enabled). |
| **v3** | $e^-$ | **Dark Noise:** Thermionic noise added (if enabled). |
| **v4** | V | **PMT Output:** Conversion to voltage. |
| **v5** | V | **Thermal Noise:** Electronic white noise added. |
| **v6** | V | **Preamplifier:** Post-RC filter signal. |
| **v7** | V | **Shaper:** Post-CR$^n$ fast amplifier signal. |
| **v8** | V | **ADC:** Final output after filtering, quantization & saturation. |

-----

## ⚙️ Configuration Parameters

### 1\. Physics & Scintillation

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `Y` | array | `None` | Samples of deposited energy (keV). |
| `arrival_times` | array/bool | `False` | Explicit arrival times of particles (s). |
| `tN` | float | `20e-6` | Total simulation duration (s). |
| `lambda_` | float | `1e5` | Poisson rate parameter (s$^{-1}$). |
| `tau1` | float | `250e-9` | Decay constant for **prompt** component (s). |
| `tau2` | float | `2e-6` | Decay constant for **delayed** component (s). |
| `p_delayed` | float | `0` | Probability of the delayed component ($0 \le p \le 1$). |
| `L` | float | `1` | Scintillation light yield (photons/keV). |

### 2\. Photodetector & Noise

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `rendQ` | float | `1` | Quantum efficiency (photon-to-charge). |
| `C1` | float | `1` | Capacitance (in $1.6 \times 10^{-19}$ F). |
| `sigma_C1` | float | `0` | Standard deviation of capacitance. |
| `tauS` | float | `10e-9` | Charge bunch spreading time (s). |
| `darkNoise` | bool | `False` | Enable thermionic dark noise. |
| `fD` | float | `1e4` | Dark noise rate (s$^{-1}$). |
| `afterPulses` | bool | `False` | Enable after-pulses. |
| `pA` | float | `0.5` | Probability of after-pulse. |
| `tauA` | float | `10e-6` | Mean after-pulse delay (s). |

### 3\. Analog Electronics

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `electronicNoise`| bool | `False` | Enable Johnson-Nyquist noise. |
| `sigmaRMS` | float | `0.0` | RMS value of electronic noise (V). |
| `pream` | bool | `False` | Enable RC Preamplifier simulation. |
| `G1` | float | `1` | Preamplifier Gain. |
| `tauRC` | float | `10e-6` | Preamplifier time constant (s). |
| `ampli` | bool | `False` | Enable Fast Amplifier (Shaper). |
| `G2` | float | `1` | Fast Amplifier Gain. |
| `tauCR` | float | `2e-6` | Fast Amplifier time constant (s). |
| `nCR` | int | `1` | Order of the CR filter. |

### 4\. Digitization (ADC)

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `digitization` | bool | `False` | Enable ADC simulation stage. |
| `fS` | float | `1e8` | Sampling frequency (Hz). |
| `fc` | float | `4e7` | Anti-aliasing filter cut-off frequency (Hz). |
| `R` | int | `14` | ADC Resolution (bits). |
| `Vs` | float | `2` | Dynamic Range / Saturation voltage (V). |

-----

## 📚 Citations

If you use **scintiPulses** in your research, please cite:

> **Simulation of scintillation detector signals**
> *EPJ Web of Conferences* (2025)
> DOI: [10.1051/epjconf/202533810001](https://doi.org/10.1051/epjconf/202533810001)

-----

## ⚖ License

This project is licensed under the **MIT License**.
