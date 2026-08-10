# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 09:38:10 2024

@author: romain.coulon
"""

import scintiPulses as sp
import matplotlib.pyplot as plt

t, v0, v1, v2, v3, v4, v5, v6, v7, v8, y0, y1 = sp.scintiPulses(
    # source parameters
    [10], # energy in keV
    tN = 1e-6, # total time in seconds
    arrival_times = [1e-9], # if False, arrival times are generated randomly according to lambda_
    lambda_ = 1e4, # input count rate in s^-1
    fS = 1e9, # sampling frequency in seconds
    # scintillation parameters
    nChannel=1, # number of channels
    tau1 = 4.6e-9, # prompt fluorescence decay time in seconds
    tau2 = 120e-9, # characteristic time of the delayed component (Voltz kinetics if TTA_kinetics=True, else exponential)
    p2 = 0.1, # only used if TTA_yield=False: fixed fraction of the prompt yield converted to delayed fluorescence
    quenching = True, # if True, Birks' ionisation quenching (Sn->S1) reduces the prompt fluorescence yield
    kB = 0.01, # Birks constant in cm/MeV (prompt channel only)
    nE = 100, # number of points used to discretize the Birks and TTA integrals
    TTA_yield = True, # if True, the delayed yield follows the dE/dx-dependent TTA model; if False, the legacy p2 model
    TTA_kinetics = True, # if True, the delayed component follows Voltz bimolecular kinetics; if False, plain exponential decay
    Sd = 0.005, # TTA efficiency factor (delayed photons per keV in the low dE/dx limit), used if TTA_yield=True
    kd = 0.01, # saturation constant of the triplet interaction density in cm/MeV, used if TTA_yield=True
    F = 1, # Fano factor of the scintillator
    L = 5, # light yield of the scintillator in keV^-1
    # PMT parameters
    C = 5e-12, # capacitance of the PMT in Farads
    G0 = 20e6, # gain of the PMT
    sigma_G = 0, # gain fluctuation of the PMT
    I = -1, # voltage invertor
    tauS = 2.23e-9, # spreading time of the PMT in seconds
    afterPulses = False, # if True, afterpulses are generated
    pA = 1e-3, # probability of afterpulses
    tauA = 5e-6, # mean delay time of afterpulses in seconds
    sigmaA = 1e-6, # standard deviation of afterpulses delay time in seconddar
    darkNoise= False, # if True, dark noise is generated
    fD = 1e-4, # dark count rate in s^-1
    electronicNoise=False, # if True, electronic noise is generated
    sigmaRMS = 0.01, # RMS of the electronic noise in Volts
    # preamplifier and amplifier parameters
    pream = False, # if True, preamplifier response is applied
    G1 = 1, # gain of the preamplifier
    tauRC = 1e-3, # RC time constant of the preamplifier in seconds
    ampli = False, # if True, amplifier response is applied
    G2 = 1, # gain of the amplifier
    tauCR = 2e-6, # RC time constant of the amplifier in seconds
    nCR=1, # order of the CR filter of the amplifier
    # digitization parameters        
    digitization=False, # if True, digitization is applied
    fc = 0.4e9, # cutoff frequency of the anti-aliasing filter in seconds
    R= 10, # resolution of the ADC in bits
    Vs=0.5, # voltage range of the ADC in Volts
)
                           
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 2 * 1), sharex=True)
fig.suptitle("Signal per Channel")

# plt.plot(t, v0, "-", alpha=0.4, label="illum fct")
# plt.plot(t, v1, "-", alpha=0.6, label="shot noise")
# plt.plot(t, v2,"-", alpha=0.4, label="after-pulses")
# plt.plot(t, v3,"-", alpha=0.4, label="dark noise")
plt.plot(t, v4,"-", alpha=0.4, label="transimp")
# plt.plot(t, v5,"-", alpha=0.4, label="therm. noise")
# plt.plot(t, v6,"-", alpha=0.4, label="preamp.")
# plt.plot(t, v7,"-", alpha=0.4, label="amp.")
# plt.plot(t, v8,"-", alpha=0.4, label="dig.")
plt.ylabel(r"$v$ /V")
plt.legend(loc="upper right")
plt.grid(True)
plt.xlabel(r"$t$ /s")  # Set x-axis label only on last plot
plt.show()
