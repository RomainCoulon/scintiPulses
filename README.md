# `scintiPulses`

## Overview

The `scintiPulses.py` package simulates pulse signal from a scintillation detector. It implements a quantum illumination function and is parameterized by various parameters to customize the simulation.
The quantum illumination function accounts for shot noise induced by the inhomogeneous Poisson process of fluorescence [1]. Thanks to its faithful description of the scintillation signal, scintiPulse.py can be used to train AI models.

[1] https://doi.org/10.1109/NSSMIC.2017.8533083 

## Parameters

- **enerVec** (list): Vector of deposited energies in keV.
- **timeFrame** (float, optional): Duration of the signal frame in seconds. Default is 1e-4.
- **samplingRate** (float, optional): Sampling rate in samples per second. Default is 500 MS/s.
- **tau** (float, optional): Decay period of the fluorescence in seconds. Default is 100e-9.
- **tau2** (float, optional): Decay period of the delayed fluorescence in seconds. Default is 2000e-9.
- **pdelayed** (float, optional): Ratio of energy converted in delayed fluorescence. Default is 0.
- **ICR** (float, optional): Input count rate in s⁻¹. Default is 1e5.
- **L** (float, optional): Scintillation light yield in keV⁻¹. Default is 1.
- **se_pulseCharge** (float, optional): Charge of a single photoelectron in Vs. Default is 1.
- **pulseSpread** (float, optional): Spreading of single photoelectron charges. Default is 0.1.
- **voltageBaseline** (float, optional): Baseline voltage (offset) in V. Default is 0.
- **pulseWidth** (float, optional): Pulse width of single electron in seconds. Default is 1e-9.
- **thermalNoise** (boolean, optional): Add Gaussian white noise. Default is False.
- **sigmathermalNoise** (float, optional): Amplitude of the Gaussian white noise (standard deviation). Default is 0.01.
- **antiAliasing** (boolean, optional): Add a low-pass filter for anti-aliasing. Default is False.
- **bandwidth** (float, optional): Cutoff frequency of the anti-aliasing filter in Hz. Default is 2e8.
- **quantiz** (boolean, optional): Add quantization noise. Default is False.
- **coding_resolution_bits** (int, optional): Resolution of voltage encoding in bits. Default is 14.
- **full_scale_range** (float, optional): Voltage dynamic range of the electronics (+/-). Default is 2.
- **thermonionic** (boolean, optional): Activate thermionic noise from PMT. Default is False.
- **thermooinicPeriod** (float, optional): Time period of the thermionic noise in seconds. Default is 1e-4.
- **pream** (boolean, optional): Activate signal filtering through the RC filter of a preamplifier. Default is False.
- **tauPream** (float, optional): Time period of the preamplifier in seconds. Default is 10e-6.
- **ampli** (boolean, optional): Activate signal filtering through the CR filter of a fast amplifier. Default is False.
- **tauAmp** (float, optional): Time period of the fast amplifier in seconds. Default is 2e-6.
- **CRorder** (float, optional): Order of the CR filter of the fast amplifier. Default is 1.
- **returnPulse** (boolean, optional): Return a single pulse for observation. Default is False.

## Returns

- **t** (list): Time vector in seconds.
- **v** (list): Simulated scintillation signal in volts.
- **IllumFCT** (list): Illumination function in volts.
- **Y** (list): Dirac brush with the number of photoelectrons per pulse.

## Example Usage

```python
enerVec = [10, 20, 30]  # Example energy vector in keV
timeFrame = 1e-4  # Duration of the signal frame in seconds
samplingRate = 500e6  # Sampling rate in samples per second

t, v, IllumFCT, quantumIllumFCT, quantumIllumFCTdark, Y = scintiPulses(enerVec, timeFrame, samplingRate)
```
