

import numpy as np
import random
import os
from os.path import dirname
from sklearn.model_selection import train_test_split
from Training.utils import low_pass_filter_weight
from random import shuffle
from Preprocessing.tools_preprocessing import get_speakers_per_corpus

corpus = ["mocha","MNGU0","usc","Haskins"]
for co in corpus:
    for speaker in get_speakers_per_corpus(co):
        print(" SPEAKER : {}".format(speaker))
        root_path = os.path.join(os.path.dirname(os.getcwd()), "Preprocessed_data" , speaker)
        EMA_files_names = sorted([name[:-4] for name in os.listdir(os.path.join(root_path, "ema")) if name.endswith('.npy')])

        N_files = len(EMA_files_names)
        rmse_all =[]
        for i in range(N_files):
            ema = np.load(os.path.join(os.path.join(root_path ,"ema"), EMA_files_names[i]+".npy"))
            ema_smoothed = np.load(os.path.join(os.path.join(root_path ,"ema_filtered"), EMA_files_names[i]+".npy"))
            rmse = np.sqrt(np.mean(np.square(ema - ema_smoothed), axis=0))  # calcule du rmse à la main
            rmse_all.append(rmse)

        rmse_all = np.array(rmse_all).reshape((N_files,len(rmse_all[0])))
        mean_rmse = np.mean(rmse_all,axis=0)
        std_rmse = np.std(rmse_all,axis=0)
        print("mean rmse ," , mean_rmse)
        print("std rmse ," , std_rmse)

