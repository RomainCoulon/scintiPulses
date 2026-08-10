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

  * **Physics-Based Modeling:** Simulates time-dependent fluorescence including prompt and delayed components, with Fano factor support.
  * **Ionisation Quenching:** Optional Birks-law quenching of the prompt yield, driven by an electron stopping-power model (Bethe + Joy-Luo).
  * **Delayed (TTA) Fluorescence:** independently selectable yield model (dE/dx-dependent triplet-triplet annihilation, or a legacy fixed-fraction model) and kinetics model (non-exponential Voltz bimolecular, or plain exponential), so any combination can be paired. See [docs/photophysics_model.md](docs/photophysics_model.md) for the full derivation.
  * **Multi-Channel Support:** Simulate signals across multiple independent detector channels.
  * **Photodetector Physics:** Incorporates quantum shot noise, after-pulses, and thermionic (dark) noise.
  * **PMT Modeling:** Configurable gain, gain fluctuation, signal inversion, and charge spreading.
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

The following example simulates a single 10 keV energy deposition with a fixed arrival time, using a fast scintillator (e.g. LSO/LYSO-like), and plots the transimpedance amplifier output of the PMT.

```python
import scintiPulses as sp
import matplotlib.pyplot as plt

t, v0, v1, v2, v3, v4, v5, v6, v7, v8, y0, y1 = sp.scintiPulses(
    # Source parameters
    [10],               # Energy deposition(s) in keV
    tN=1e-6,            # Total simulation duration (s)
    arrival_times=[1e-9],  # Fixed arrival time; if False, times are drawn from Poisson process
    lambda_=1e4,        # Input count rate (s⁻¹), used when arrival_times=False
    fS=1e9,             # Sampling frequency (Hz)
    # Scintillation parameters
    nChannel=1,         # Number of detector channels
    tau1=4.6e-9,        # Prompt fluorescence decay time (s)
    tau2=120e-9,        # Delayed-component characteristic time (s)
    quenching=False,    # Enable Birks ionisation quenching of the prompt yield
    kB=0.01,            # Birks constant (cm/MeV), used if quenching=True
    TTA_yield=True,     # Use the dE/dx-dependent TTA delayed-yield model
    TTA_kinetics=True,  # Use Voltz bimolecular kinetics for the delayed-component time shape
    Sd=0.005,           # TTA efficiency factor, used if TTA_yield=True
    kd=0.01,            # TTA saturation constant (cm/MeV), used if TTA_yield=True
    p2=0.1,             # Fraction of delayed component, used only if TTA_yield=False
    nE=100,             # Discretization points for the quenching/TTA integrals
    F=1,                # Fano factor of the scintillator
    L=5,                # Light yield (photons/keV)
    # PMT parameters
    C=5e-12,            # PMT capacitance (F)
    G0=20e6,            # PMT gain
    sigma_G=0,          # PMT gain fluctuation (std dev)
    I=-1,               # Voltage inverter (+1 or -1)
    tauS=2.23e-9,       # Charge spreading time (s)
    afterPulses=False,  # Enable after-pulses
    pA=1e-3,            # After-pulse probability
    tauA=5e-6,          # Mean after-pulse delay (s)
    sigmaA=1e-6,        # Std dev of after-pulse delay (s)
    darkNoise=False,    # Enable thermionic dark noise
    fD=1e-4,            # Dark count rate (s⁻¹)
    # Analog electronics
    electronicNoise=False,  # Enable Johnson-Nyquist noise
    sigmaRMS=0.01,      # Electronic noise RMS (V)
    pream=False,        # Enable RC preamplifier
    G1=1,               # Preamplifier gain
    tauRC=1e-3,         # Preamplifier RC time constant (s)
    ampli=False,        # Enable fast amplifier (shaper)
    G2=1,               # Amplifier gain
    tauCR=2e-6,         # Amplifier CR time constant (s)
    nCR=1,              # Order of the CR filter
    # Digitization
    digitization=False, # Enable ADC simulation
    fc=0.4e9,           # Anti-aliasing filter cut-off frequency (Hz)
    R=10,               # ADC resolution (bits)
    Vs=0.5,             # ADC voltage range (V)
)

# Plot the PMT transimpedance output (v4)
plt.figure(figsize=(8, 3))
plt.plot(t, v4, "-", alpha=0.7, label="Transimpedance output")
plt.xlabel(r"$t$ /s")
plt.ylabel(r"$v$ /V")
plt.title("Simulated Scintillation Pulse")
plt.legend(loc="upper right")
plt.grid(True)
plt.tight_layout()
plt.show()
```

-----

## 📡 The Signal Chain (Outputs)

The function returns a 12-element tuple. This allows inspection of the signal at every stage of the processing chain.

| Variable | Unit | Stage Description |
| :--- | :--- | :--- |
| **t** | s | Time base vector. |
| **v0** | $e^-$ | Idealized scintillation signal (charge). |
| **v1** | $e^-$ | **Shot Noise:** Quantized photons added. |
| **v2** | $e^-$ | **After-pulses:** Spurious pulses added (if enabled). |
| **v3** | $e^-$ | **Dark Noise:** Thermionic noise added (if enabled). |
| **v4** | V | **PMT Output:** Transimpedance conversion to voltage. |
| **v5** | V | **Thermal Noise:** Electronic white noise added (if enabled). |
| **v6** | V | **Preamplifier:** Post-RC filter signal (if enabled). |
| **v7** | V | **Shaper:** Post-CR$^n$ fast amplifier signal (if enabled). |
| **v8** | V | **ADC:** Final output after filtering, quantization & saturation (if enabled). |
| **y0** | — | Auxiliary output (channel-level intermediate). |
| **y1** | — | Auxiliary output (channel-level intermediate). |

-----

## ⚙️ Configuration Parameters

### 1\. Source & Timing

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `Y` | array | `None` | Energy deposition samples (keV). |
| `arrival_times` | array / bool | `False` | Explicit particle arrival times (s). If `False`, times are drawn from a Poisson process at rate `lambda_`. |
| `tN` | float | `20e-6` | Total simulation duration (s). |
| `lambda_` | float | `1e4` | Input count rate for random arrivals (s$^{-1}$). |
| `fS` | float | `1e8` | Sampling frequency (Hz). |

### 2\. Physics & Scintillation

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `nChannel` | int | `1` | Number of detector channels. |
| `tau1` | float | `4.6e-9` | Decay constant for the **prompt** component (s). |
| `tau2` | float | `120e-9` | Characteristic time of the **delayed** component (s). Sets the decay time of a Voltz bimolecular kinetics $1/(1+t/\tau_2)^2$ if `TTA_kinetics=True`, or a plain exponential if `TTA_kinetics=False`. |
| `F` | float | `1` | Fano factor of the scintillator. |
| `L` | float | `5` | Scintillation light yield (photons/keV). |
| `quenching` | bool | `False` | Enable Birks ionisation quenching (Sn→S1 internal conversion) of the **prompt** yield only. See `kB`. |
| `kB` | float | `0.01` | Birks constant (cm/MeV), used only if `quenching=True`. |
| `TTA_yield` | bool | `True` | Delayed-**yield** model selector. If `True`, use the dE/dx-dependent triplet-triplet-annihilation model (`Sd`, `kd`); if `False`, fall back to the legacy fixed-fraction model (`p2`). Independent of `TTA_kinetics`. |
| `TTA_kinetics` | bool | `True` | Delayed-**time-shape** model selector. If `True`, use Voltz bimolecular kinetics $1/(1+t/\tau_2)^2$; if `False`, use a plain exponential (decay time `tau2`). Independent of `TTA_yield`, so any combination is valid (e.g. fixed-fraction yield with Voltz kinetics). |
| `Sd` | float | `0.005` | TTA efficiency factor (delayed photons/keV in the low dE/dx limit), used only if `TTA_yield=True`. |
| `kd` | float | `0.01` | Saturation constant of the triplet interaction density (cm/MeV), used only if `TTA_yield=True`. |
| `p2` | float | `0.1` | Fraction of the prompt yield converted to delayed fluorescence ($0 \le p2 \le 1$), used only if `TTA_yield=False`. |
| `nE` | int | `100` | Number of points used to discretize the Birks (`quenching`) and TTA integrals. |

See [docs/photophysics_model.md](docs/photophysics_model.md) for the full mathematical model, including the electron stopping-power model and the discrete-time hazard functions used for the stochastic photon simulation.

### 3\. Photodetector (PMT)

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `C` | float | `5e-12` | PMT capacitance (F). |
| `G0` | float | `20e6` | PMT gain. |
| `sigma_G` | float | `0` | Standard deviation of PMT gain fluctuation. |
| `I` | float | `−1` | Voltage inverter factor (+1 or −1). |
| `tauS` | float | `10e-9` | Charge bunch spreading time (s). |
| `darkNoise` | bool | `False` | Enable thermionic dark noise. |
| `fD` | float | `1e-4` | Dark noise count rate (s$^{-1}$). |
| `afterPulses` | bool | `False` | Enable after-pulses. |
| `pA` | float | `1e-3` | Probability of an after-pulse. |
| `tauA` | float | `5e-6` | Mean after-pulse delay (s). |
| `sigmaA` | float | `1e-6` | Standard deviation of after-pulse delay (s). |

### 4\. Analog Electronics

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `electronicNoise` | bool | `False` | Enable Johnson-Nyquist noise. |
| `sigmaRMS` | float | `0.0` | RMS value of electronic noise (V). |
| `pream` | bool | `False` | Enable RC preamplifier simulation. |
| `G1` | float | `1` | Preamplifier gain. |
| `tauRC` | float | `1e-3` | Preamplifier RC time constant (s). |
| `ampli` | bool | `False` | Enable fast amplifier (shaper). |
| `G2` | float | `1` | Fast amplifier gain. |
| `tauCR` | float | `2e-6` | Fast amplifier CR time constant (s). |
| `nCR` | int | `1` | Order of the CR filter. |

### 5\. Digitization (ADC)

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `digitization` | bool | `False` | Enable ADC simulation stage. |
| `fc` | float | `4e7` | Anti-aliasing filter cut-off frequency (Hz). |
| `R` | int | `14` | ADC resolution (bits). |
| `Vs` | float | `2` | Dynamic range / saturation voltage (V). |

-----

## 📚 Citations

If you use **scintiPulses** in your research, please cite:

> **Simulation of scintillation detector signals**
> *EPJ Web of Conferences* (2025)
> DOI: [10.1051/epjconf/202533810001](https://doi.org/10.1051/epjconf/202533810001)

You can also look at:
> **Simulation of stochastic jittering in liquid scintillation counters**
> *RAD Conference - abstract* (2026)
> DOI: [10.21175/rad.abstr.book.2026.28.5](https://doi.org/10.21175/rad.abstr.book.2026.28.5)

-----

## ⚖ License

This project is licensed under the **MIT License**.
