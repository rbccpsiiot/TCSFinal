# -*- coding: utf-8 -*-
"""
Created on Jan 2019

@author: Prakash Hiremath M
"""

import pandas as pd
import numpy as np
import scipy as sp

import csv
import datetime

from matplotlib import pyplot as plt
from matplotlib import dates  as md 
from matplotlib.colors import LogNorm

#==============================================================================================
#Procedure to eliminate the probably spurious PCB detections
print('Start of defining procedure :', datetime.datetime.now())

def elim_spur_pcb(org_binry_sig,pcb_data_df,THRESHOLD):
    """
    Purpose : Eliminate the PCB detections whose durations are below threshold
    Input   : org_binry_sig   - The binary sequence generated from front-end signal processing
              pcb_data_df     - The dataframe with detected PCB data
              -> arvl_index   - the index for the PCB arrival
              -> dptr_index   - the index for the PCB departure
              -> pcb_actv_dur - PCB processing duration in terms of no. of samples 
              THRESHOLD       - The threshold in terms of no. of samples
    Output  : cor_binry_sig   - The corrected binary sequence after eliminating spurious PCB detections          
    """
    
    cor_binry_sig = org_binry_sig

    for i in range(0,len(pcb_data_df)):
        if(pcb_data_df.pcb_actv_dur[i] < THRESHOLD):
            STR_IND = pcb_data_df.arvl_index[i]
            END_IND = pcb_data_df.arvl_index[i] + pcb_data_df.pcb_actv_dur[i]
            #print(i, STR_IND, END_IND)
            cor_binry_sig[STR_IND:END_IND] = 0.0
        #endif
    #endfor
    
    return cor_binry_sig

#end-proc
print('End   of defining procedure :', datetime.datetime.now())