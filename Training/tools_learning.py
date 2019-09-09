# TODO: ah bon c'est un code facebook ? Je pense pas... change l'entête
# Copyright (c) 2018-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy import signal
from scipy.fftpack import fft, ifft

from os.path import dirname
from numpy.random import choice

def load_filenames(train_on,batch_size,part=["train"]):
    """
    # TODO: description en anglais
    :param train_on:  liste des locuteurs sur lesquels on apprend (parmis "fsew0","msak0","MNGU0")
    :param batch_size: nombre de phrase sur lesquelles on veut apprendre au sein d'un batch
    :return: x,y deux listes de longueur batch_size. x contient des numpy array de format (K,429) et y de format (K, nombre_arti)

    choisi #batch_size phrases au hasard parmis tous les locuteurs en respectant la proporition de chaque locuteur dans
    le train set. Plus un locuteur aura de phrases dans le train set, plus il a de chances d'avoir de phrases dans le
    batch.
    """
    path_files = os.path.join(os.path.dirname(os.getcwd()),"Donnees_pretraitees","fileset")

    if len(train_on)==1:
        files = []
        for p in part :
            files = files + open(os.path.join(path_files,train_on[0]+"_"+p+".txt"), "r").read().split()
        index = np.random.choice(len(files),batch_size)
        train_files = [files[i] for i in index]
    else :
        proba_speakers = {}
        total_number=0
        for speaker in train_on:
            N_speaker = 0
            for p in part :
                train_speaker = open(os.path.join(path_files,speaker+"_"+p+".txt"), "r").read().split()
                N_speaker = N_speaker + len(train_speaker)

            total_number += N_speaker
            proba_speakers[speaker] = N_speaker

        for speaker in train_on:
            proba_speakers[speaker] = proba_speakers[speaker]/total_number

        speaker_files_chosen = choice(train_on,  batch_size, p=list(proba_speakers.values()))
        train_files=[]
        for speaker in train_on:
            train_speaker = []
            for p in part :
                train_speaker =  train_speaker + open(os.path.join(path_files, speaker + "_"+p+".txt"), "r").read().split()
            n_train = list(speaker_files_chosen).count(speaker)
            index = np.random.choice(len(train_speaker), n_train)
            train_files.extend([train_speaker[i] for i in index])
    return train_files

def load_filenames_deter(train_on,part=["train"]):
    # TODO
    path_files = os.path.join(os.path.dirname(os.getcwd()),"Donnees_pretraitees","fileset")
    filenames = []
    for speaker in train_on:
        for p in part:
            names = open(os.path.join( path_files , speaker + "_" + p + ".txt"), "r").read().split()
            filenames = filenames + names
    return filenames


def load_data(files_names,filtered=True):
    """
    TODO: description
    :param files_names: liste des n
    :param filtered:
    :return:
    """
    folder = os.path.join(os.path.dirname(os.getcwd()), "Donnees_pretraitees")
    x = []
    y = []
    speakers = ["F01", "F02", "F03", "F04", "M01", "M02", "M03", "M04","F1", "F5", "M1", "M3"
        , "maps0", "faet0", 'mjjn0', "ffes0", "MNGU0", "fsew0", "msak0","falh0"]
    suff =""
    if filtered :
        suff = "_final"

    for file_name in files_names :
        speaker = [s  for s in speakers if s.lower() in file_name.lower()][0] # normalement un seul speaker dans le nom du fichier
        files_path = os.path.join(folder,speaker)
        the_ema_file = np.load(os.path.join(files_path, "ema"+suff, file_name + ".npy"))
        the_mfcc_file = np.load(os.path.join(files_path, "mfcc", file_name+ ".npy"))
        x.append(the_mfcc_file)
        y.append(the_ema_file)
    return x , y

#speakers =  ["MNGU0","fsew0","msak0","F1","F5","M1","M3","maps0","faet0",'mjjn0',"ffes0"]
#files_for_train = load_filenames(speakers, 30, part=["train"])
#x, y = load_data(files_for_train, filtered=1,VT=False)
#for i in range(30):
 #   print(files_for_train[i],x[i].shape,y[i].shape)

#filenames = load_filenames(["fsew0","msak0","MNGU0"],10)
#x,y = load_data(filenames)
#print(x[0].shape,y[0].shape)

def chirp(f0, f1, T, fs):
    # TODO: description propre
    # f0 is the lower bound of the frequency range, in Hz
    # f1 is the upper bound of the frequency range, in Hz
    # T is the duration of the chirp, in seconds
    # fs is the sampling rate
    slope = (f1-f0)/float(T)

    def chirp_wave(t):
        # TODO: pq imbriqué ?
        return np.cos((0.5*slope*t+f0)*2*np.pi*t)
    return [chirp_wave(t) for t in np.linspace(0, T, T*fs).tolist()]


def window(window_type, N):
    # TODO
    def hanning(n):
        # TODO: pq imbriqué ? Fait une classe plutot
        return 0.5*(1 - np.cos(2 * np.pi * (n - 1) / (N - 1)))

    def hamming(n):
        # TODO idem
        return 0.54 - 0.46 * np.cos(2 * np.pi * (n - 1) / (N - 1))

    if window_type == 'hanning':
        return np.asarray([hanning(n) for n in range(N)])
    else:
        return np.asarray([hamming(n) for n in range(N)])


def low_pass_filter_weight_old(cut_off,sampling_rate,len_window,window_type="hanning"):
    # TODO
    N=len_window-1
    if cut_off>sampling_rate/2:
        raise Exception("La frequence de coupure doit etre au moins deux fois la frequence dechantillonnage")
    def hanning_un_point(n):
        # TODO
        value=0.5*(1 - np.cos(2 * np.pi * n/N))
        return value
    hanning_weights = [hanning_un_point(n) for n in range(len_window)]
    cut_off_norm = cut_off/sampling_rate
    def sinc_un_point(n):
        # TODO
        if n!= len_window/2:
            value = np.sin(2*np.pi*cut_off_norm*(n-N/2))/(np.pi*(n-N/2))
        else :
            value=2*cut_off_norm
        return value
    print(cut_off_norm)

    sinc_weights = [sinc_un_point(n) for n in range(len_window)]
    final_weights = [a*b for a,b in zip(hanning_weights,sinc_weights)]
    final_weights = final_weights/np.sum(final_weights)
   # plt.plot(range(len_window),hanning_weights)
   # plt.plot(range(len_window),sinc_weights)
   # plt.plot(range(len_window),final_weights)
   # plt.legend(['hanning','sinc','final'])
   # plt.show()
    return final_weights
#low_pass_filter_weight(cut_off=70,sampling_rate=200,len_window=100)

def low_pass_filter_weight(cut_off,sampling_rate):
    # TODO
    fc = cut_off/sampling_rate # Cutoff frequency as a fraction of the sampling rate (in (0, 0.5)).
    print(fc)
    if fc > 0.5:
        raise Exception("La frequence de coupure doit etre au moins deux fois la frequence dechantillonnage")
    b = 0.08  # Transition band, as a fraction of the sampling rate (in (0, 0.5)).

    N = int(np.ceil((4 / b))) #le window
    if not N % 2:
        N += 1  # Make sure that N is odd.
    n = np.arange(N) #int of [0,N]
    h = np.sinc(2*fc * (n - (N - 1) / 2))  # Compute sinc filter.

    w_hanning = 0.5 * (1 - np.cos(2 * np.pi * n / (N-1))) # Compute hanning window.
    w_blackman = 0.42 - 0.5 * np.cos(2 * np.pi * n / (N - 1)) +  0.08 * np.cos(4 * np.pi * n / (N - 1))

    h = h * w_hanning  # Multiply sinc filter with window.
    h = h / np.sum(h)
    h_hanning  = h

    h = h * w_blackman  # Multiply sinc filter with window.
    h = h / np.sum(h)
    h_blackman = h

    to_plot= True
    if to_plot :
        plt.plot(h, ".-", c="b")
        plt.xlabel("reduced frequency ")
        plt.title("sinus cardinal filter, with cutoff {} and sr {}".format(cut_off, sampling_rate))
        plt.show()

        plt.plot(w_hanning, ".-", c="b")
        plt.plot(w_blackman, ".-", c='r')
        plt.title("hanning and blackman filter, with cutoff {} sr {} and N {}".format(cut_off, sampling_rate, N))
        plt.legend(['hanning', "blackman"])
        plt.show()

        plt.plot(h_hanning, ".-", c="b")
        plt.plot(h_blackman, ".-", c="r")

        plt.title("filter (sinc + window ), with cutoff {} and sr {}".format(cut_off, sampling_rate))
        plt.legend(['hanning', 'blackman'])
        plt.show()

        freqs, h_blackman_f = signal.freqz(h_blackman)
        freqs, h_hanning_f = signal.freqz(h_hanning) #The normalized frequencies at which h was computed, in radians/sample en Hz ?
        freqs = freqs*sampling_rate /(2*np.pi )# freq in hz
        plt.plot(freqs, 20 * np.log10(abs(h_blackman_f)), 'r')
        plt.plot(freqs, 20 * np.log10(abs(h_hanning_f)), 'b')
        plt.title("frequency response of filteres for wituff {} and sr {}".format(cut_off,sampling_rate))
        plt.legend(["blackman","hanning"])
        plt.ylabel('Amplitude [dB]')
        plt.xlabel("real frequency")
        plt.show()

    return h_hanning



# TODO: si inutile à supprimer
#weights = low_pass_filter_weight(30,500)
"""
f_1=20
s_r = 500
signal_1 = [np.sin(2*np.pi*f_1*n/s_r) for n in range(300)]
f_2 = f_1*3
signal_2 = [np.sin(2*np.pi*f_2*n/s_r) for n in range(300)]
signal =  [a+b for a,b in zip(signal_1,signal_2)]
#plt.plot(signal_1,alpha=0.5)
#plt.plot(signal_2,alpha=0.5)
#plt.plot(signal)
weights = low_pass_filter_weight(cut_off=30,sampling_rate=s_r)
#print(len(weights),len(signal))
signal_filtre = np.convolve(signal,weights,mode='same')
#print(len(signal_filtre))

€signal_filtre = signal_filtre*np.std(signal_1)/np.std(signal_filtre)
#plt.plot(signal_filtre)
#plt.legend(['s1','s2','somme','filtre'])
#plt.show()


"""