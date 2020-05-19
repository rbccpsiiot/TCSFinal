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

#Procedure to determine the PCB processing durations

print('Start of defining procedure :', datetime.datetime.now())
def get_pcb_dur(binry_sig):
    """
    Purpose : Determine PCB processing durations from the binary sequence
    Input   : binry_sig   - The binary sequence generated from front-end signal processing
    Output  : pcb_data_df - Output dataframe with detected PCB data
              -> arvl_index   - the index for the PCB arrival
              -> dptr_index   - the index for the PCB departure
              -> pcb_actv_dur - PCB processing duration in terms of no. of samples 
    """
    
    grad = binry_sig.diff()
    grad[0] = 0

    arvl_time = np.argwhere(grad > 0)
    dept_time = np.argwhere(grad < 0)

    pcb_data_df = pd.DataFrame(columns=['arvl_index','dptr_index','pcb_actv_dur'])

    #Initialization
    i = 0
    j = 0
    END_OF_PROCESSING = 0

    while (END_OF_PROCESSING == 0):
    
        if (i >= len(arvl_time)) or (j >= len(dept_time)):
            END_OF_PROCESSING = 1
            print('End of processing at i =', i, 'j =', j)
        else:
            if (dept_time[j] < arvl_time[i]):  #departure instant before arrival instant
                j = j + 1
            if (i >= len(arvl_time)) or (j >= len(dept_time)):
                END_OF_PROCESSING = 1
                print('End of processing at i =', i, 'j =', j)
            else: 
                #print('i = ', i, ': j = ', j)
                arvl_index   = np.asscalar(arvl_time[i])
                dptr_index   = np.asscalar(dept_time[j])
                pcb_actv_dur = np.asscalar(dept_time[j]) - np.asscalar(arvl_time[i]) 
                
                data = pd.DataFrame([[arvl_index,dptr_index,pcb_actv_dur]],columns=['arvl_index','dptr_index','pcb_actv_dur'])
                pcb_data_df = pcb_data_df.append(data)
                del data
                
                i = i + 1
                j = j + 1
            #endif
        #endif
    #end-while  
    
    pcb_data_df = pcb_data_df.reset_index()
    pcb_data_df = pcb_data_df.iloc[:,1:len(pcb_data_df.columns)]
    return pcb_data_df
#end-proc
print('End   of defining procedure :', datetime.datetime.now())