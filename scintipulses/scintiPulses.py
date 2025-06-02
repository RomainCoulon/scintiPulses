# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 16:52:24 2024

@author: romain.coulon
"""

import numpy as np
import scipy.ndimage as sp
from scipy.signal import butter, filtfilt
from scipy.stats import truncnorm

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
    # noise = np.random.uniform(-0.5, 0.5, size=len(v)) * quantization_step_size
    
    # Add the noise to the original signal
    v_noisy = np.round(v/quantization_step_size)*quantization_step_size
    
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

def scintiPulses(Y, tN=1e-4, fS=500e6, tau1 = 100e-9, tau2 = 2000e-9, p_delayed = 0,
                                 lambda_ = 1e5, L = 1, C1 = 1, sigma_C1 = 0, I=-1,
                                 tauS = 1e-9,
                                 afterPulses = False, pA = 1e-3, tauA = 5e-6, sigmaA = 1e-6,
                                 darkNoise=False, fD = 1e-4,
                                 electronicNoise=False, sigmaRMS = 0.01,
                                 pream = False, G1 = 1, tauRC = 10e-6,
                                 ampli = False, G2 = 1, tauCR = 2e-6, nCR=1,                                 
                                 digitization=False, fc = 2e8, R=14, Vs=2,
                                 returnPulse = False):
    """
    This function simulate a signal from a scintillation detector.

    Parameters
    ----------
    Y : list
        vector of deposited energies in keV.
    tN : float, optional
        duration of the signal frame in s. The default is 1e-4.
    fS : float, optional
        sampling rate in S/s. The default is 500 MS/s.
    tau1 : float, optional
        decay period of the fluorescence. The default is 100e-9.
    tau2 : float, optional
        decay period of the delayed fluorescence. The default is 2000e-9.
    p_delayed : float, optional
        ratio of energy converted in delayed fluorescence. The default is 0.
    lambda_ : float, optional
        input count rate in s-1. The default is 1e5.
    L : float, optional
        scintillation light yield in keV-1
    C1 : float, optional
        capacitance of the phototube in elementary charge per volt unit (in 1.6e-19 F). The default is 1.
    sigma_C1 : float, optional
        standard deviation of the capaciance fluctuation in elementary charge per volt unit (in 1.6e-19 F). The default is 0.
    I : integer
        voltage invertor to display positive pulses. The default is -1.
    tauS : float, optional
        pulse width of single electron in s. The default is 1e-9.
    
    afterPulses : boolean, optional
        add after-pulses. The default is False.
    pA : float, optional
        The probability that a primary charge contributes to an interaction with a molecule of residual gas during its multiplication process. The default is 1e-3.
    tauA : float, optional
        mean delay of after-pulses in second. The default is 5e-6 s.
    sigmaA: float, optional
        time-spread of after-pulses in second. The default is 1e-6 s.
    
    electronicNoise : boolean, optional
        add a gaussian white noise (Johnson-Nyquist noise). The default is False.
    sigmaRMS : float, optional
        root mean square value of the Johnson-Nyquist noise in volt. The default is 0.01 V.
    
    darkNoise : boolean, optional
        activate the thermoionic noise (dark noise) from PMT. The default is False.
    fD : float, optional
        frequancy of the thermoionic noise in s-1. The default is 1e4.
        
    pream : boolean, optional
        activate the signal filtering through the RC filter of a preamplifier. The default is False.
    G1 : float, optional
        gain of the preamplifier. The default is 1.
    tauRC : float, optional
        time period of the preamplifier in s. The default is 10e-6.
    
    ampli : boolean, optional
        activate the signal filtering through the CR filter of a fast amplifier. The default is False.
    G2 : float, optional
        gain of the fast amplifier. The default is 1.
    tauCR : float, optional
        time period of the fast amplifier in s. The default is 2e-6 s.
    nCR : float, optional
        order of the CR filter of the fast amplifier. The default is 1.
    
    digitization : boolean, optional
        simulate the digitizer. The default is False.
    fc : float, optional
        cutoff frequency of the anti-aliasing filter in s-1. 0.4*fS is recommanded. The default is 2e8 Hz.
    R : integer
        resoltion of the ADC in bit. The default is 14 bits.
    Vs:
        voltage dynamic range (+/-) in volt. The defaut is 2 V.
    
    returnPulse : boolean, optional
        to return a single pulse for observation. The default is False.

    Returns
    -------
    t : list
        time vector in s.
    v0 : list
        simulated charge density from the theoretical illumination function (in e).
    v1 : list
        simulated charge density with the shot noise from the quantum illumination function (in e).
    v2 : list
        simulated charge density with the after-pulses (in e).
    v3 : list
        simulated charge density with the dark noise (in e).
    v4 : list
        simulated volatge signal of the photodetector anode (in V).
    v5 : list
        simulated volatge signal of the photodetector anode with the Johnson-Nyquist noise (in V).
    v6 : list
        simulated volatge signal of the preamplifier (in V).
    v7 : list
        simulated volatge signal of the fast amplifier (in V).
    v8 : list
        simulated volatge signal encoded by the digitizer (in V).
    y0 : list
        Dirac brush of energy (in keV).
    y1 : list
        Dirac brush of mean charges (in e).

    """

    arrival_times = [0]
    while arrival_times[-1]<tN:
        arrival_times.append(arrival_times[-1] + np.random.exponential(scale=1/lambda_, size=1))
    arrival_times=arrival_times[1:-1]
    
    N = len(arrival_times)
    if N>len(Y):
        print(f"boostrap {100*len(Y)/N} %")
        Y = np.random.choice(Y, N, replace=True) # boostraping
    
    timeStep = 1/fS
    
    t = np.arange(0,tN,timeStep)
    n = len(t)
    
    
    Y = np.asarray(Y)
    # Nphe = np.random.poisson(Y*L) # nb de photoelectron / decay
    Nphe = Y*L # nb de photoelectron / decay
    
    # Illumination function (v0)
    v0=np.zeros(n)
    y0 =np.zeros(n)
    y1 = np.zeros(n)
    for i, ti in enumerate(arrival_times):
        IllumFCT0 = (1-p_delayed)*(Nphe[i]/tau1) * np.exp(-t/tau1)+p_delayed*(Nphe[i]/tau2) * np.exp(-t/tau2) # Exponential law x the nb of PHE
        IllumFCT0 *= timeStep
        IllumFCT0 *= Nphe[i]/sum(IllumFCT0)
        # print(sum(IllumFCT0), Nphe[i])
        # cumCharge = np.cumsum(IllumFCT0)
        flag0 = int(ti[0]/timeStep)
        y0[flag0] += Y[i]
        if Nphe[i] > 0:
            if returnPulse:
                v0=np.concatenate((np.zeros(len(IllumFCT0)),IllumFCT0))
                t = np.arange(-tN,tN,timeStep)
                n = len(t)
                break
            else:
                flag = int(ti[0]/timeStep)
                v0 += np.concatenate((np.zeros(flag),IllumFCT0[:n-flag]))
                y1[flag] += Nphe[i]
                
    
    # Quantum illumination function
    # v=voltageBaseline*np.ones(n)
    v1=np.zeros(n)
    for i, l in enumerate(v0):
        # ne = int(l) + np.random.binomial(n=1, p=l-int(l))
        ne = np.random.poisson(l)
        if ne>0:
            # vi = np.random.normal(se_pulseCharge,pulseSpread,ne)
            # v1[i]+=sum(vi)
            v1[i]+=ne
            # print("here",i, l, v1[i])

    # After-pulses
    v2=v1.copy()
    if afterPulses:
        for i, l in enumerate(v1):
            # ne = int(l) + np.random.binomial(n=1, p=l-int(l))
            if l>0:
                a, b = (0 -tauA) / sigmaA, ((n-i)*timeStep - tauA) / sigmaA
                delta_A = truncnorm.rvs(a, b, loc=tauA, scale=sigmaA)
                t_iAP = int(delta_A/timeStep)
                if i+t_iAP<n :
                    # v2[i+t_iAP]+=np.random.poisson(pA*l)
                    v2[i+t_iAP]+=np.random.binomial(l, pA)
    
    # Thermoionic noise
    v3=v2.copy()
    if darkNoise:
        arrival_times2 = [0]
        while arrival_times2[-1]<tN:
            arrival_times2.append(arrival_times2[-1] + np.random.exponential(scale=1/fD, size=1))
        arrival_times2=arrival_times2[1:-1]
        for i, ti in enumerate(arrival_times2):
            flag = int(ti[0]/timeStep)
            # vi = 1np.random.normal(se_pulseCharge,pulseSpread,1)
            v3[flag]+=1#vi[0]
            # print("noise",flag, v3[flag]-v2[flag])
    
    # Voltage conversion
    kC = np.random.normal(1,sigma_C1,1)
    v4 = -I*(kC/C1)*sp.gaussian_filter1d(v3,tauS/timeStep)
    
    # thermal noise
    v5=v4.copy()
    if electronicNoise: v5+=sigmaRMS*np.random.normal(0,1,n)
    
    # preamplifier
    v6=v5.copy()
    if pream: v6 = G1*rc_filter(v5, tauRC, timeStep)
    
    # amplifier
    v7=v6.copy()
    if ampli:
        for i in range(nCR):
            v7 = G2*cr_filter(v6, tauCR, timeStep)
       
    # digitizer
    v8=v7.copy()
    if digitization:
        v8 = low_pass_filter(v7, timeStep, fc)
        v8 = add_quantization_noise(v8, R, Vs)
        v8 = saturate(v8, Vs*2)
    return t, v0, v1, v2, v3, v4, v5, v6, v7, v8, y0, y1



# import tdcrpy as td
# import matplotlib.pyplot as plt
# Y = 100*np.ones(1000) #td.TDCR_model_lib.readRecQuenchedEnergies()[0]

# fS = 1e8
# sigmaRMS = 0.00
# tauS = 10e-9
# Niter=1000
# v1sum = []
# for i in range(Niter):
#     t, v0, v1, v2, v3, v4, v5, v6, v7, v8, y0, y1 = scintiPulses(Y, tN=20e-6,
#                                   fS=fS, tau1 = 25e-9,
#                                   tau2 = 2000e-9, p_delayed = 0,
#                                   lambda_ = 1e7, L = 1, C1 = 1, sigma_C1 = 0, I=-1,
#                                   tauS = tauS,
#                                   electronicNoise=False, sigmaRMS = sigmaRMS,
#                                   afterPulses = False, pA = 500e-3, tauA = 10e-6, sigmaA = 1e-7,
#                                   digitization=False, fc = fS*0.4, R=14, Vs=2,
#                                   darkNoise=False, fD = 10e-6,
#                                   pream = False, G1=10, tauRC = 10e-6,
#                                   ampli = False, G2=10, tauCR = 2e-6, nCR=1,
#                                   returnPulse = True)
#     v1sum.append(sum(v1))

# print(np.mean(v1sum), np.std(v1sum))


# plt.figure("plot")
# plt.clf()
# plt.title("signal")
# plt.plot(t, v0,"-", label="illumation function")
# # plt.plot(t, y0,"-", label="Energy")
# # plt.plot(t, y1,"-", label="charges")
# # plt.plot(t, v1,"-", alpha=0.4, label="shot noise")
# # plt.plot(t, v2,"-", alpha=0.4, label="after-pulses")
# # plt.plot(t, v3,"-", alpha=0.4, label="dark noise")
# # plt.plot(t, v4,"-", alpha=0.4, label="transimp")
# # plt.plot(t, v5,"-", alpha=0.4, label="therm. noise")
# # plt.plot(t, v6,"-", alpha=0.4, label="preamp.")
# #plt.plot(t, v8,"-", alpha=0.4, label="amp.")
# # plt.xlim([0,5e-6])
# # plt.legend()
# plt.xlabel(r"$t$ /s")
# plt.ylabel(r"$v$ /V")
# plt.savefig("figure_0.svg")
# plt.show()