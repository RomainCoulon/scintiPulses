# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 09:38:10 2024

@author: romain.coulon
"""

import scintiPulses as sp
import tdcrpy as td
import matplotlib.pyplot as plt

# enerVec = td.TDCR_model_lib.readRecQuenchedEnergies()[0] # energy vector of deposited quenched energies in keV
ei = 1000
arrt = [1e-8] # arrival time vector

tN = 0.3e-6                # duration of the sequence in s
fS = 500e6            # sampling rate of the digitizer is S/s

ICR = 1e5                       # imput count rate in s-1

tau1 = 5e-9                    # time constant of the prompt fluorescence in s
tau2 = 100e-9                  # time constant of the delayed fluorescence in s
tau3 = 100e-9
p2 = 0                    # fraction of energy converted in delayed fluorescence
p3 = 0.7
ndiff = 1

L = 10                           # light yield (free parameter) charges per keV

se_pulseCharge = 1              # output voltage of a charge pulse in V
pulseSpread = 0.1               # spread parameter of charge pulses in V sigma C1
pulseWidth = 50e-9              # time width of charge pulses in s tau_S
voltageBaseline = 0             # constant voltage basline in V


afterPulses = False
rA = 1e-2
tauA = 20e-6
sigmaA = 5e-7

thermalNoise=True               # add thermal noise 
sigmathermalNoise = 0.01         # rms of the thermal noise (sigma of Normal noise)
antiAliasing = True             # add antiAliasing Butterworth low-pass filter
bandwidth = fS*0.1    # bandwidth of the antiAliasing filter (in Hz)
quantiz = True                  # add quatizaion noise
coding_resolution_bits = 14     # encoding resolution in bits
full_scale_range = 2            # voltage scale range in V
thermonionic = True           # thermoinic noise
thermooinicPeriod = 1e6      # time constant of the thermooinic noise (s)

pream = True                  # add preamplificator filtering
tauPream = 10e-6                # shaping time (RC parameter) in s

ampli = True                   # add amplifier filtering
tauAmp = 0.5e-6                   # shaping time (CR parameter) in s
CRorder=1                       # order of the CR filter

returnPulse = False              # to return one pulse

t, v0, v1, v2, v3, v4, v5, v6, v7, v8, y0, y1 = sp.scintiPulses([ei], arrival_times=arrt, tN=tN, fS=fS,
            tau1=tau1, tau2=tau2, tau3=tau3,
            p2=p2, p3=p3, ndiff=ndiff,
            lambda_=ICR, L=L, C1=1, sigma_C1=0, I=-1,
            nChannel=3, F=1, tauS=1e-9, rendQ=0.2,
            afterPulses=False, pA=1e-3, tauA=5e-6, sigmaA=1e-6,
            darkNoise=False, fD=1e-4,
            electronicNoise=False, sigmaRMS=0.01,
            pream=False, G1=1, tauRC=10e-6,
            ampli=False, G2=1, tauCR=2e-6, nCR=1,
            digitization=False, fc=2e8, R=14, Vs=2
    )
                                    


"""
Filtrage par Moyenne Mobile
"""
import numpy as np 
# def moving_average_filter(signal, window_size):
#     return np.convolve(signal, np.ones(window_size)/window_size, mode='same')

# window_size = 10
# filtered_signal = moving_average_filter(noisy_signal, window_size)


# """
# Filtrage de Wiener
# """
# from scipy.signal import wiener

# filtered_signal = wiener(noisy_signal, mysize=3, noise=noise_std_dev)

# plt.plot(filtered_signal)
# plt.title('Signal filtré par Wiener')
# plt.show()


plt.figure("plot #1")
plt.clf()
# plt.plot(t, v0*8,"-", label=r"$v^{(0)}$")
plt.plot(t, v1[0],"-", alpha=0.7, label=r"$v^{(1)} PMT A$")
plt.plot(t, v1[1],"-", alpha=0.7, label=r"$v^{(1)} PMT B$")
plt.plot(t, v1[2],"-", alpha=0.7, label=r"$v^{(1)} PMT C$")
plt.legend()
plt.xlabel(r"$t$ /s")
plt.ylabel(r"$v$ /s$^{-1}$")
plt.savefig("Figs/figure_1.svg")

# plt.figure("plot #2")
# plt.clf()
# plt.plot(t*1e6, v1,"-", label=r"$v^{(1)}$")
# plt.plot(t*1e6, v2,'-', alpha=0.7, label=r"$v^{(2)}$")
# plt.legend()
# plt.xlabel(r"$t$ /µs")
# plt.ylabel(r"$v$ /s$^{-1}$")
# plt.savefig("Figs/figure_2.svg")

# plt.figure("plot #3")
# plt.clf()
# plt.plot(t*1e6, v2,"-", label=r"$v^{(2)}$")
# plt.plot(t*1e6, v3,'-', alpha=0.7, label=r"$v^{(3)}$")
# plt.legend()
# plt.xlabel(r"$t$ /µs")
# plt.ylabel(r"$v$ /s$^{-1}$")
# plt.savefig("Figs/figure_3.svg")

# plt.figure("plot #4")
# plt.clf()
# plt.plot(t, v4,'-', alpha=0.7, label=r"$v^{(4)}$")
# plt.legend()
# plt.xlabel(r"$t$ /s")
# plt.ylabel(r"$v$ /V")
# plt.savefig("Figs/figure_4.svg")

# plt.figure("plot #5")
# plt.clf()
# # Plot the first dataset
# fig, ax1 = plt.subplots()
# ax1.plot(t, v4, "-", label=r"$v^{(4)}$")
# ax1.set_xlabel(r"$t$ /s")
# ax1.set_ylabel(r"$v$ /s$^{-1}$", color='b')
# ax1.tick_params(axis='y', labelcolor='b')
# # Create a second y-axis
# ax2 = ax1.twinx()
# ax2.plot(t, v5, '-', alpha=0.7, label=r"$v^{(5)}$", color='r')
# ax2.set_ylabel(r"$v$ /V", color='r')
# ax2.tick_params(axis='y', labelcolor='r')
# # Add legends
# # plt.xlim([0.000001, 0.0001])
# fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
# plt.savefig("Figs/figure_5.svg")
# plt.show()

# plt.figure("plot #6")
# plt.clf()
# # Plot the first dataset
# fig, ax1 = plt.subplots()
# ax1.plot(t, v5, "-", label=r"$v^{(5)}$")
# ax1.set_xlabel(r"$t$ /s")
# ax1.set_ylabel(r"$v$ /s$^{-1}$", color='b')
# ax1.tick_params(axis='y', labelcolor='b')
# # Create a second y-axis
# ax2 = ax1.twinx()
# ax2.plot(t, v6, '-', alpha=0.7, label=r"$v^{(6)}$", color='r')
# ax2.set_ylabel(r"$v$ /V", color='r')
# ax2.tick_params(axis='y', labelcolor='r')
# # Add legends
# # plt.xlim([0.000001, 0.0001])
# fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
# plt.savefig("Figs/figure_6.svg")
# plt.show()

# plt.figure("plot #7")
# plt.clf()
# # Plot the first dataset
# fig, ax1 = plt.subplots()
# ax1.plot(t, v6, "-", label=r"$v^{(6)}$")
# ax1.set_xlabel(r"$t$ /s")
# ax1.set_ylabel(r"$v$ /s$^{-1}$", color='b')
# ax1.tick_params(axis='y', labelcolor='b')
# # Create a second y-axis
# ax2 = ax1.twinx()
# ax2.plot(t, v7, '-', alpha=0.7, label=r"$v^{(7)}$", color='r')
# ax2.set_ylabel(r"$v$ /V", color='r')
# ax2.tick_params(axis='y', labelcolor='r')
# # Add legends
# # plt.xlim([0.000001, 0.0001])
# fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
# plt.savefig("Figs/figure_7.svg")
# plt.show()