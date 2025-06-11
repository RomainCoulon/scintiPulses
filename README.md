# scintiPulses

**Simulate scintillation detector signals with photodetector effects, noise sources, and digitization modeling.**

`scintiPulses` is a Python package that provides high-fidelity simulation of photodetector outputs from scintillation detectors. It allows modeling of physical, electronic, and digitization processes, including quantum noise, after-pulses, dark noise, preamplification, amplification, and ADC digitization.

---

## Features

- Simulates realistic pulse shapes from energy depositions in scintillation materials
- Models time-dependent fluorescence (prompt + delayed components)
- Quantum shot noise and after-pulse modeling
- Thermionic (dark) noise and Johnson-Nyquist noise
- RC and CR analog filtering stages (preamplifier & fast amplifier)
- Digitization including low-pass filtering, quantization, and saturation

---

## Installation

Install via pip:

```bash
pip install scintiPulses
