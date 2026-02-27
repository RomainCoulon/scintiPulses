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

def scintiPulses(Y, arrival_times=False, tN=1e-4, fS=500e6, nChannel=1,
                                 tau1 = 5e-9, tau2 = 80e-9, p_Etype = 0, tau3 = 80e-9, p_TTA = 0,
                                 F=1, lambda_ = 1e5, L = 1, C1 = 1, sigma_C1 = 0, I=-1,
                                 tauS = 1e-9, rendQ = 1,
                                 afterPulses = False, pA = 1e-3, tauA = 5e-6, sigmaA = 1e-6,
                                 darkNoise=False, fD = 1e-4,
                                 electronicNoise=False, sigmaRMS = 0.01,
                                 pream = False, G1 = 1, tauRC = 1000e-6,
                                 ampli = False, G2 = 1, tauCR = 2e-6, nCR=1,                                 
                                 digitization=False, fc = 2e8, R=14, Vs=2):
    """
    This function simulate a signal from a scintillation detector.

    Parameters
    ----------
    Y : list
        vector of deposited energies in keV.
    arrival_times : boolean or list
        list of events times in s. The default is False
    tN : float, optional
        duration of the signal frame in s. The default is 1e-4.
    fS : float, optional
        sampling rate in S/s. The default is 500 MS/s.
    tau1 : float, optional
        decay period of the fluorescence. The default is 5e-9.
    tau2 : float, optional
        decay period of the delayed fluorescence through type-E (T1->S1) transition. The default is 80e-9.
    p_Etype : float, optional
        addtional fraction of energy converted in delayed fluorescence through type-E (T1->S1) transition. The default is 0.
    tau3 : float, optional
            decay period of the delayed fluorescence through TTA (T1+T1->S1) transition. The default is 200e-9.
    p_TTA : float, optional
            addtional fraction of energy converted in delayed fluorescence through TTA (T1+T1->S1) transition. The default is 0.
    F : float, optional
        Fano factor. The default is 1.
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
    rendQ : float, optional
        quantum efficiency of the photon-to-charge conversion. The default is 1.
    nChannel : integer, optional
        number of shared photodetectors read the scintillation signal. The default is 1.
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
    ######################################
    ## INTERACTION EVENTS ARRIVAL TIMES ##
    ######################################
    if arrival_times:
        arrival_times = [t for t in arrival_times if t <= tN]
    else:
        arrival_times = [0]
        while arrival_times[-1]<tN:
            arrival_times.append(arrival_times[-1] + np.random.exponential(scale=1/lambda_))
        arrival_times=arrival_times[1:-1]
    
    #####################################################
    ## BOOSTRAPPING TO ATTRIBUTE ENERGY TO EACH EVENTS ##
    #####################################################
    N = len(arrival_times)
    if N>len(Y):
        # print(f"boostrap {100*len(Y)/N} %")
        Y = np.random.choice(Y, N, replace=True) # boostraping
    
    ##############################################
    ## INITIALISATION OF THE SIGNAL TIME FRAMES ##
    ##############################################
    timeStep = 1/fS
    t = np.arange(0,tN,timeStep)
    n = len(t)
    Y = np.asarray(Y)
    Nph = Y*L                      # nb de photon / decay
    v0=np.zeros(n); y0 =np.zeros(n); y1 = np.zeros(n); v1=np.zeros((nChannel, n))
    
    ###########################################################
    ## SIMULATION OF THE DETERMINISTIC ILLUMINATION FUNCTION ##
    ###########################################################
    for i, ti in enumerate(arrival_times):
        IllumFCT0 = (Nph[i]/tau1) * np.exp(-t/tau1) + p_Etype*(Nph[i]/tau2)*np.exp(-t/tau2) + p_TTA*(Nph[i]/tau3)*np.exp(-t/tau3)# Exponential law x the nb of PHE
        IllumFCT0 *= timeStep
        IllumFCT0 *= Nph[i]*(1+p_Etype)*(1+p_TTA)/sum(IllumFCT0)
        flag0 = int(ti/timeStep)
        y0[flag0] += Y[i]
        if Nph[i] > 0:
            flag = int(ti/timeStep)
            v0 += np.concatenate((np.zeros(flag),IllumFCT0[:n-flag]))
            y1[flag] += Nph[i]
    
    #####################################################
    ## SIMULATION OF THE QUANTUM ILLUMINATION FUNCTION ##
    #####################################################
    n_tp = 1-np.exp(-1/(fS*tau1)) # prompt transition probability
    n_td = 1-np.exp(-1/(fS*tau2)) # delayed transition probability    
    for k, ti in enumerate(arrival_times):
        
        flag = int(ti/timeStep)       # indice of the decay event
                
        mean_n_s_prompt = Nph[k] # mean number of exited states leading to prompt photons
        mean_n_s_delayed = p_Etype*Nph[k]+p_TTA*Nph[k]    # mean number of exited states leading to delayed photons
        
        if F==1:
            n_s_prompt = np.random.poisson(mean_n_s_prompt)   # number of exited states leading to prompt photons
            n_s_delayed = np.random.poisson(mean_n_s_delayed) # number of exited states leading to delayed photons
        else:
            n_s_prompt = truncnorm.rvs((0 - mean_n_s_prompt) / F*mean_n_s_prompt, np.inf, loc=mean_n_s_prompt, scale=F*mean_n_s_prompt)   # number of exited states leading to prompt photons
            n_s_delayed = truncnorm.rvs((0 - mean_n_s_delayed) / F*mean_n_s_delayed, np.inf, loc=mean_n_s_delayed, scale=F*mean_n_s_delayed) # number of exited states leading to delayed photons
        
        i = 0; n_e_prompt=[]
        while n_s_prompt>0 or ti+i*timeStep<t[-1]:            
            n_p_prompt = np.random.binomial(n_s_prompt,n_tp)         # number of prompt transitions during the interval
            # if nChannel>1:
            n_p_prompt_z = np.random.multinomial(n_p_prompt, np.ones(nChannel)/nChannel)  # shared number of prompt transitions during the interval
            n_e_prompt.append(np.random.binomial(n_p_prompt_z, rendQ))  # number of measured charges during the interval
            n_s_prompt -= n_p_prompt                                 # update of the number of exited states leading to prompt photons
            i += 1                                                   # move to next interval
        
        l = 0; n_e_delayed=[]
        while n_s_delayed>0 or ti+i*timeStep<t[-1]:
            n_p_delayed = np.random.binomial(n_s_delayed, n_td)         # number of delayed transitions during the interval
            n_p_delayed_z = np.random.multinomial(n_p_delayed, np.ones(nChannel)/nChannel)  # shared number of delayed transitions during the interval
            n_e_delayed.append(np.random.binomial(n_p_delayed_z, rendQ))  # number of measured charges during the interval
            n_s_delayed -= n_p_delayed                                 # update of the number of exited states leading to delayed photons
            l += 1                                                     # move to next interval
            
        # if sum(IllumFCT0) > 0: # if at least one charge
        
        for z in range(nChannel):     # for each channel
            n_e_prompt = np.asarray(n_e_prompt)     # convert the frames in arrays
            n_e_delayed = np.asarray(n_e_delayed)
            
            if len(n_e_prompt)>0:
                if n < flag+len(n_e_prompt[:,z]):
                    # cut = flag+len(n_e_prompt[:,z])-n
                    cut = n - flag
                    # v1[z,flag:flag+len(n_e_prompt[0:n-cut,z])] += n_e_prompt[0:-cut,z]
                    v1[z,flag:n] += n_e_prompt[0:cut,z]
                else:
                    v1[z,flag:flag+len(n_e_prompt[:,z])] += n_e_prompt[:,z]
            # else:
            #     print("p",n_e_prompt)
            
            if len(n_e_delayed)>0:
                if n < flag+len(n_e_delayed[:,z]):
                    # cut = flag+len(n_e_delayed[:,z])-n
                    cut = n - flag
                    # v1[z,flag:flag+len(n_e_delayed[0:n-cut,z])] += n_e_delayed[0:-cut,z]
                    v1[z,flag:n] += n_e_delayed[0:cut,z]
                else:
                    v1[z,flag:flag+len(n_e_delayed[:,z])] += n_e_delayed[:,z]
            # else:
            #     print("d", n_e_delayed)
                            
    # fast version (deprecated)
    # for i, l in enumerate(v0):
    #     nph = np.random.poisson(l)
    #     if nChannel == 1:
    #         ne = np.random.binomial(nph, rendQ)
    #         if ne>0:
    #             v1[(nChannel-1,i)]+=ne
    #     else:
    #         pVec = [1/nChannel for j in range(nChannel)]
    #         ne = np.random.multinomial(nph, pVec)
    #         for j in range(nChannel):
    #             v1[(j,i)]+=np.random.binomial(ne[j], rendQ)
            
    ####################################
    ## SIMUALTION OF THE AFTER-PULSES ##
    ####################################
    v2=v1.copy()
    if afterPulses:
        for j in range(nChannel):
            for i, l in enumerate(v1[j]):
                if l>0:
                    a, b = (0 -tauA) / sigmaA, ((n-i)*timeStep - tauA) / sigmaA
                    delta_A = truncnorm.rvs(a, b, loc=tauA, scale=sigmaA)
                    t_iAP = int(delta_A/timeStep)
                    if i+t_iAP<n :
                        v2[(j, i+t_iAP)]+=np.random.binomial(l, pA)
    
    #########################################
    ## SIMULATION OF THE THERMOIONIC NOISE ##
    #########################################
    v3=v2.copy()
    if darkNoise:
        for j in range(nChannel):
            arrival_times2 = [0]
            while arrival_times2[-1]<tN:
                arrival_times2.append(arrival_times2[-1] + np.random.exponential(scale=1/fD, size=1))
            arrival_times2=arrival_times2[1:-1]
            for i, ti in enumerate(arrival_times2):
                flag = int(ti/timeStep)
                v3[(j,flag)]+=1
    
    ########################
    ## VOLTAGE CONVERSION ##
    ########################
    kC = np.random.normal(1,sigma_C1,1)
    v4 = -I*(kC/C1)*sp.gaussian_filter1d(v3,tauS/timeStep)
    
    #####################################
    ## SIMULATION OF THE THERMAL NOISE ##
    #####################################
    v5=v4.copy()
    if electronicNoise:
        for z in range(nChannel):
            v5[z]+=sigmaRMS*np.random.normal(0,1,n)
    
    ##########################################
    ## SIMULATION OF THE PREAMPLIFIER STAGE ##
    ##########################################
    v6=v5.copy()
    if pream:
        for z in range(nChannel):
            v6[z] = G1*rc_filter(v5[z], tauRC, timeStep)
    
    ###########################################
    ## SIMULATION OF THE AMPLIFICATION STAGE ##
    ###########################################
    v7=v6.copy()
    if ampli:
        for i in range(nCR):
            for z in range(nChannel):
                v7[z] = G2*cr_filter(v6[z], tauCR, timeStep)
       
    #################################
    ## SIMULATION OF THE DIGITIZER ##
    #################################
    v8=v7.copy()
    if digitization:
        for z in range(nChannel):
            v8[z] = low_pass_filter(v7[z], timeStep, fc)
            v8[z] = add_quantization_noise(v8[z], R, Vs)
            v8[z] = saturate(v8[z], Vs*2)
    
    if nChannel==1:
        v1=v1[0]; v2=v2[0]; v3=v3[0]; v4=v4[0]; v5=v5[0]; v6=v6[0]; v7=v7[0]; v8=v8[0]
    
    return t, v0, v1, v2, v3, v4, v5, v6, v7, v8, y0, y1



# # import tdcrpy as td
# import matplotlib.pyplot as plt
# Y = [10] #td.TDCR_model_lib.readRecQuenchedEnergies()[0]

# fS = 1e9
# sigmaRMS = 0.01
# tauS = 10e-9
# Niter=1
# v1sum = []
# arrt = [1e-8, 2e-8]
# nc = 3
# for i in range(Niter):
#     t, v0, v1, v2, v3, v4, v5, v6, v7, v8, y0, y1 = scintiPulses(Y, tN=1e-7,
#                                   arrival_times = arrt, nChannel=nc,
#                                   fS=fS, tau1 = 5.44e-9, F=1,
#                                   tau2 = 254.5e-9, p_delayed = 0.5,
#                                   lambda_ = 1e6, L = 1.2, C1 = 1, sigma_C1 = 0, I=-1,
#                                   tauS = tauS, rendQ=0.25,
#                                   electronicNoise=False, sigmaRMS = sigmaRMS,
#                                   afterPulses = False, pA = 50e-3, tauA = 20e-6, sigmaA = 1e-7,
#                                   digitization=True, fc = fS*0.4, R=8, Vs=2,
#                                   darkNoise=False, fD = 10e6,
#                                   pream = True, G1=2, tauRC = 10e-6,
#                                   ampli = True, G2=2, tauCR = 0.5e-6, nCR=1)
#     v1sum.append(sum(v1))

# print(np.mean(v1sum), np.std(v1sum))


# fig, axes = plt.subplots(nrows=nc, ncols=1, figsize=(8, 2 * nc), sharex=True)
# fig.suptitle("Signal per Channel")

# # Ensure axes is iterable even if nc == 1
# if nc == 1:
#     # plt.plot(t, v0, "-", alpha=0.4, label="illum fct")
#     # plt.plot(t, v1, "-", alpha=0.6, label="shot noise")
#     # plt.plot(t, v2,"-", alpha=0.4, label="after-pulses")
#     # plt.plot(t, v3,"-", alpha=0.4, label="dark noise")
#     # plt.plot(t, v4,"-", alpha=0.4, label="transimp")
#     # plt.plot(t, v5,"-", alpha=0.4, label="therm. noise")
#     plt.plot(t, v6,"-", alpha=0.4, label="preamp.")
#     plt.plot(t, v7,"-", alpha=0.4, label="amp.")
#     plt.plot(t, v8,"-", alpha=0.4, label="dig.")
#     plt.ylabel(r"$v$ /V")
#     plt.legend(loc="upper right")
#     plt.grid(True)
#     plt.xlabel(r"$t$ /s")  # Set x-axis label only on last plot
#     plt.savefig("figure_0.svg")
#     plt.show()
# else:
#     for i in range(nc):
#         ax = axes[i]
#         ax.plot(t, v0, "-", alpha=0.4, label="illum fct")
#         ax.plot(t, v1[i], "-", alpha=0.6, label=f"shot noise - channel {i}")
#         # ax.plot(t, v2[i], "-", alpha=0.6, label=f"after-pulses - channel {i}")
#         # ax.plot(t, v3[i], "-", alpha=0.6, label=f"dark noise - channel {i}")
#         # ax.plot(t, v4[i], "-", alpha=0.6, label=f"transimp - channel {i}")
#         # ax.plot(t, v5[i], "-", alpha=0.6, label=f"therm. noise - channel {i}")
#         # ax.plot(t, v6[i], "-", alpha=0.6, label=f"preamp. - channel {i}")
#         # ax.plot(t, v7[i], "-", alpha=0.6, label=f"amp. - channel {i}")
#         # ax.plot(t, v8[i], "-", alpha=0.6, label=f"dig. - channel {i}")
#         ax.set_ylabel(r"$v$ /V")
#         ax.legend(loc="upper right")
#         ax.grid(True)
#     axes[-1].set_xlabel(r"$t$ /s")  # Set x-axis label only on last plot
#     plt.tight_layout(rect=[0, 0, 1, 0.96])  # Leave space for suptitle
#     plt.savefig("figure_0.svg")
#     plt.show()