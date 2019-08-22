import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)


from Apprentissage.train import train_model
from Traitement.fonctions_utiles import get_speakers_per_corpus
import sys
from multiprocessing import Process
import argparse
corpus = "[Haskins]"
speakers = get_speakers_per_corpus("Haskins")
def cross_val_for_type_filter_has(speaker): #0 1 ou 2
    patience = 3
    n_epochs = 50
    select_arti = True
    corpus_to_train_on = str(corpus)
    batch_norma = False
    loss_train = "both_90"
    for filter_type in [1,2]:
        train_model(test_on=speaker, n_epochs=n_epochs, loss_train=loss_train, patience=patience,
                    select_arti=select_arti, corpus_to_train_on=corpus_to_train_on,
                    batch_norma=batch_norma, filter_type=filter_type)


def cross_val_for_alpha_has(speaker):
    patience = 3
    n_epochs = 50
    select_arti = True
    corpus_to_train_on = corpus
    only_one_sp = False
    filter_type = 1
    batch_norma = False
    for alpha in [0,20,40,60,80,100] :
        loss_train = "both_" + str(alpha)
        train_model(test_on=speaker, n_epochs=n_epochs, loss_train=loss_train, patience=patience,
                    select_arti=select_arti, corpus_to_train_on=corpus_to_train_on,
                    batch_norma=batch_norma, filter_type=filter_type)


def cross_val_for_bn_has(speaker):
    patience = 3
    n_epochs = 50
    select_arti = True
    corpus_to_train_on = corpus
    filter_type = 1
    loss_train ="both_90"
    train_model(test_on=speaker, n_epochs=n_epochs, loss_train=loss_train, patience=patience,
                    select_arti=select_arti, corpus_to_train_on=corpus_to_train_on,
                    batch_norma=False, filter_type=filter_type)

    train_model(test_on=speaker, n_epochs=n_epochs, loss_train=loss_train, patience=patience,
                    select_arti=select_arti, corpus_to_train_on=corpus_to_train_on,
                    batch_norma=True, filter_type=filter_type)

if __name__=='__main__':
    experience = sys.argv[1]
    if experience == "filter":
        procs = []
        for j in range(3):
            for sp in speakers:
                proc = Process(target=cross_val_for_type_filter_has,args = (sp,))
                procs.append(proc)
                proc.start()

            for proc in procs:
                proc.join()

    elif experience == "alpha":
        procs = []
        for j in range(3):
            for sp in speakers:
                proc = Process(target=cross_val_for_alpha_has, args=(sp,))
                procs.append(proc)
                proc.start()

            for proc in procs:
                proc.join()

    elif experience == "bn":
        procs = []
        for j in range(3):
            for sp in speakers:
                proc = Process(target=cross_val_for_bn_has(), args=(sp,))
                procs.append(proc)
                proc.start()

            for proc in procs:
                proc.join()