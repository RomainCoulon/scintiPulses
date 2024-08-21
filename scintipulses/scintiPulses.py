# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 16:52:24 2024

@author: romain.coulon
"""

import numpy as np
import scipy.ndimage as sp
from scipy.signal import butter, filtfilt

def low_pass_filter(v, timeStep, bandwidth):
    # Calculate the Nyquist frequency
    nyquist = 0.5 / timeStep
    
    # Normalize the bandwidth with respect to the Nyquist frequency
    normal_cutoff = bandwidth / nyquist
    
    # Create a Butterworth low-pass filter
    b, a = butter(N=4, Wn=normal_cutoff, btype='low', analog=False)
    
    # Apply the filter to the voltage signal
    v_filtered = filtfilt(b, a, v)
    
    return v_filtered

def add_quantization_noise(v, coding_resolution_bits, full_scale_range):
    # Calculate the number of quantization levels
    num_levels = 2**coding_resolution_bits
    
    # Determine the quantization step size
    quantization_step_size = full_scale_range / num_levels
    
    # Generate noise uniformly distributed between -0.5 and 0.5 of the quantization step size
    noise = np.random.uniform(-0.5, 0.5, size=len(v)) * quantization_step_size
    
    # Add the noise to the original signal
    v_noisy = v + noise
    
    return v_noisy

def saturate(v, full_scale_range):
    v_clipped = np.clip(v, -full_scale_range / 2, full_scale_range / 2)
    return v_clipped

def rc_filter(v, tau, dt):
    """
    Apply an RC filter to the voltage signal v.

    Parameters:
    v (numpy array): Input voltage signal.
    tau (float): Time constant of the RC filter.
    dt (float): Sampling interval.

    Returns:
    numpy array: Filtered voltage signal.
    """
    alpha = dt / (tau + dt)
    v_out = np.zeros_like(v)
    v_out[0] = v[0]  # Initial condition

    for i in range(1, len(v)):
        v_out[i] = alpha * v[i] + (1 - alpha) * v_out[i-1]

    return v_out

def cr_filter(v, tau, dt):
    """
    Apply a CR filter to the voltage signal v.

    Parameters:
    v (numpy array): Input voltage signal.
    tau (float): Time constant of the CR filter.
    dt (float): Sampling interval.

    Returns:
    numpy array: Filtered voltage signal.
    """
    alpha = tau / (tau + dt)
    v_out = np.zeros_like(v)
    v_out[0] = v[0]  # Initial condition

    for i in range(1, len(v)):
        v_out[i] = alpha * (v_out[i-1] + v[i] - v[i-1])
        # v_out[i] = (v[i] - v[i-1])

    return v_out

def scintiPulses(enerVec, timeFrame=1e-4,
                                 timeStep=1e-9, tau = 100e-9,
                                 tau2 = 2000e-9, pdelayed = 0,
                                 ICR = 1e5, L = 1, se_pulseCharge = 1,
                                 pulseSpread = 0.1, voltageBaseline = 0,
                                 pulseWidth = 1e-9,
                                 thermalNoise=False, sigmathermalNoise = 0.01,
                                 antiAliasing = False, bandwidth = 2e8, 
                                 quantiz=False, coding_resolution_bits=14, full_scale_range=2,
                                 thermonionic=False, thermooinicPeriod = 1e-4,
                                 pream = False, tauPream = 10e-6,
                                 ampli = False, tauAmp = 2e-6, CRorder=1,
                                 returnPulse = False):
    """
    This function simulate a signal from a scintillation detector.
    It implements a quantum illumation function
    It is parametrized by the parameters explained below.

    Parameters
    ----------
    enerVec : list
        vector of deposited energies in keV.
    timeFrame : float, optional
        duration of the signal frame in s. The default is 1e-4.
    timeStep : float, optional
        sampling rate in s. The default is 1e-9.
    tau : float, optional
        decay period of the fluorescence. The default is 100e-9.
    tau2 : float, optional
        decay period of the delayed fluorescence. The default is 2000e-9.
    pdelayed : float, optional
        ratio of energy converted in delayed fluorescence. The default is 0.
    ICR : float, optional
        input count rate in s-1. The default is 1e5.
    L : float, optional
        scintillation light yield in keV-1. The default is 1.
    se_pulseCharge : float, optional
        charge of a single photoelectron in Vs. The default is 1.
    pulseSpread : float, optional
        spreading of single photoelectron charges. The default is 0.1.
    voltageBaseline : float, optional
        baseline voltage (offset) in V. The default is 0.
    pulseWidth : float, optional
        pulse width of single electron in s. The default is 1e-9.
    thermalNoise : boolean, optional
        add a gaussian white noise. The default is False.
    sigmathermalNoise : float, optional
        amplitude of the gaussian white noise (std parameter). The default is 0.01.
    antiAliasing : boolean, optional
        add a low pass filtering from anti-aliasing filter. The default is False.
    bandwidth : float, optional
        cutting frequency of the anti-aliasing filter in s-1. The default is 2e8.
    quantiz : boolean, optional
        add a quantization noise. The default is False.
    coding_resolution_bits : integer, optional
        resolution of voltage encoding in bit. The default is 14.
    full_scale_range : float, optional
        voltage dynamic of the electronics (+/-). The default is 2.
    thermonionic : boolean, optional
        activate the thermoionic noise from PMT. The default is False.
    thermooinicPeriod : float, optional
        time period of the thermoionic noise in s. The default is 1e-4.
    pream : boolean, optional
        activate the signal filtering through the RC filter of a preamplifier. The default is False.
    tauPream : float, optional
        time period of the preamplifier in s. The default is 10e-6.
    ampli : boolean, optional
        activate the signal filtering through the CR filter of a fast amplifier. The default is False.
    tauAmp : float, optional
        time period of the fast amplifier in s. The default is 2e-6.
    CRorder : float, optional
        order of the CR filter of the fast amplifier. The default is 1.
    returnPulse : boolean, optional
        to return a single pulse for observation. The default is False.

    Returns
    -------
    t : list
        time vector in s.
    v : list
        simulated scintillation signal in V.
    IllumFCT : list
        illumination function in V.

    """

    arrival_times = [0]
    while arrival_times[-1]<timeFrame:
        arrival_times.append(arrival_times[-1] + np.random.exponential(scale=1/ICR, size=1))
    arrival_times=arrival_times[1:-1]
    
    N = len(arrival_times)
    if N>len(enerVec):
        print(f"boostrap {100*len(enerVec)/N} %")
        enerVec = np.random.choice(enerVec, N, replace=True) # boostraping
        
    t = np.arange(0,timeFrame,timeStep)
    n = len(t)
    
    
    enerVec = np.asarray(enerVec)
    Nphe = np.random.poisson(enerVec*L) # nb de photoelectron / decay
    
    # Illumination function
    IllumFCT=np.zeros(len(t))
    for i, ti in enumerate(arrival_times):
        IllumFCT0 = (1-pdelayed)*(Nphe[i]/tau) * np.exp(-t/tau)+pdelayed*(Nphe[i]/tau2) * np.exp(-t/tau2) # Exponential law x the nb of PHE
        IllumFCT0 *= timeStep
        if Nphe[i] > 0:
            # print(type(ti), type(timeStep))
            if returnPulse:
                IllumFCT=IllumFCT0
                break
            else:
                flag = int(ti[0]/timeStep)
                IllumFCT += np.concatenate((np.zeros(flag),IllumFCT0[:n-flag]))
    
    # Quantum illumination function
    v=voltageBaseline*np.ones(n)
    for i, l in enumerate(IllumFCT):
        ne = int(l) + np.random.binomial(n=1, p=l-int(l))
        if ne>0:
            vi = np.random.normal(se_pulseCharge,pulseSpread,ne)
            v[i]+=sum(vi)
    
    # Thermoionic noise
    if thermonionic:
        arrival_times2 = [0]
        while arrival_times2[-1]<timeFrame:
            arrival_times2.append(arrival_times2[-1] + np.random.exponential(scale=thermooinicPeriod, size=1))
        arrival_times2=arrival_times2[1:-1]
        for i, ti in enumerate(arrival_times2):
            flag = int(ti[0]/timeStep)
            vi = np.random.normal(se_pulseCharge,pulseSpread,1)
            v[flag]+=vi[0]
    
    v=sp.gaussian_filter1d(v,pulseWidth/timeStep)
    if thermalNoise: v=v+sigmathermalNoise*np.random.normal(0,1,n)
    if antiAliasing: v = low_pass_filter(v, timeStep, bandwidth)
    if quantiz: v = add_quantization_noise(v, coding_resolution_bits, full_scale_range)
    if pream: v = rc_filter(v, tauPream, timeStep)
    if ampli:
        for i in range(CRorder):
            v = cr_filter(v, tauAmp, timeStep)
    if quantiz: v = saturate(v, full_scale_range)
    return t, v, IllumFCT