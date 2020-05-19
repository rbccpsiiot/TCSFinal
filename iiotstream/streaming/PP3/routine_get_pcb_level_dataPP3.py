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

#Procedure to display vital statistics and get dataframe at pcb level
print('Start of defining procedure :', datetime.datetime.now())
print('Version : 2019-04-23 12:50')
def get_pcb_level_data(filt_sig_df,pcb_data_df,HISTBIN_WINDOW):
    """
    Purpose : Obtain PCB level data from the filtered vibration data
    Inputs  : filt_sig_df  - The dataframe containing filtered vibration data
              pcb_data_df  - The dataframe containing initially identified PCB data
              HISTBIN_WINDOW - the window for histogram to calculate mode
    Output  : pcb_level_df - The dataframe that contains PCB level data       
    """
    
    STR_TIME = datetime.datetime.now()
    
    print('=======================================================')
    print("START : ", STR_TIME)
    print('=======================================================')

    #Method-1 to obtain mode
    #a = plt.hist(pcb_data_df.pcb_actv_dur,50)
    #a1 = a[0]
    #a2 = a[1]
    #ind = np.argmax(a1)
    #mod_actv_dur = a2[ind]

    #Method-2 to obtain mode
    THRESHOLD = 2000000
    mode_df = get_mode_df(pcb_data_df,THRESHOLD,HISTBIN_WINDOW)
    
    print('Mode calculated at :', datetime.datetime.now())
    
    if (len(pcb_data_df) > 0):
        avg_actv_dur = np.mean(pcb_data_df.pcb_actv_dur)
        med_actv_dur = np.median(pcb_data_df.pcb_actv_dur)
        dev_actv_dur = np.std(pcb_data_df.pcb_actv_dur)
        util_factor  = np.sum(pcb_data_df.pcb_actv_dur) / len(filt_sig_df) 
        
        print('Number of boards detected        =', len(pcb_data_df))
        print('Machine utilization factor       =', util_factor*100, '%')
        print('Average   board active duration  =', avg_actv_dur / 75, 'secs')
        print('Median    board active duration  =', med_actv_dur / 75, 'secs')
        print('Deviation board active duration  =', dev_actv_dur / 75, 'secs')
    else: 
        print('No PCB identified.')
    #endif
    
    #Load pcb data onto dataframe
    pcb_level_df = pd.DataFrame(columns=['arvl_index','arvl_tmstmp','dptr_index','dptr_tmstmp','no_of_parts','proc_dur','maint_dur','weightage'])
    
    for i in range (0,len(pcb_data_df)):
    
        arvl_index  = pcb_data_df.arvl_index[i]
        dptr_index  = pcb_data_df.dptr_index[i]
        arvl_tmstmp = filt_sig_df.timestamp[arvl_index]
        dptr_tmstmp = filt_sig_df.timestamp[dptr_index]
        proc_dur = pd.Timedelta(pd.Timestamp(dptr_tmstmp) - pd.Timestamp(arvl_tmstmp)).total_seconds()
        
        mod_actv_dur = np.asscalar(mode_df.query('(str_index <= @arvl_index) & (end_index >= @dptr_index)').loc[:,'local_mode'])
        weightage   = pcb_data_df.pcb_actv_dur[i] / mod_actv_dur
        
        no_of_parts = 1
        maint_dur   = 0.0
        
        data = pd.DataFrame([[arvl_index,arvl_tmstmp,dptr_index,dptr_tmstmp,no_of_parts,proc_dur,maint_dur,weightage]],columns=['arvl_index','arvl_tmstmp','dptr_index','dptr_tmstmp','no_of_parts','proc_dur','maint_dur','weightage'])
        pcb_level_df = pcb_level_df.append(data)
        del data
    #end-for    

    pcb_level_df = pcb_level_df.reset_index()
    pcb_level_df = pcb_level_df.iloc[:,1:len(pcb_level_df.columns)]
    
    END_TIME = datetime.datetime.now()
    
    print('=======================================================')
    print("END   : ", END_TIME)
    print('=======================================================')
    
    DUR_TS    = pd.Timestamp(END_TIME) - pd.Timestamp(STR_TIME)
    EXEC_TIME = pd.Timedelta(DUR_TS).total_seconds()
    
    print("Execution time =",EXEC_TIME/60,"mins")
    print('=======================================================')
    
    return pcb_level_df

#end-proc 
print('End   of defining procedure :', datetime.datetime.now())

#-----------------------------------------------------

def get_mode_df(pcb_data_df,THRESHOLD,HISTBIN_WINDOW):
    mode_df = pd.DataFrame(columns=['str_index','end_index','local_mode'])

    LOCAL_STR_FLAG = 1

    for i in range(1,len(pcb_data_df)):
        if (LOCAL_STR_FLAG == 1):
            str_index = pcb_data_df.arvl_index[i-1]
            local_str = i-1
            LOCAL_STR_FLAG = 0
            print('str_index =', str_index)
            print('local_str =', local_str)
        #end-if
    
        samp_diff = pcb_data_df.arvl_index[i] - pcb_data_df.dptr_index[i-1]
    
        if ((i == len(pcb_data_df)-1) | (samp_diff >= THRESHOLD)): 
            if (i == len(pcb_data_df)-1): #last entry of dataframe
                end_index = pcb_data_df.dptr_index[i]
                local_end = i
            elif (samp_diff >= THRESHOLD):
                end_index = pcb_data_df.dptr_index[i-1]
                local_end = i-1
            #end-if
            LOCAL_STR_FLAG = 1
            print('end_index =', end_index)
            print('local_end =', local_end)
            pcb_srs = pcb_data_df
            local_mode = get_mode(pcb_data_df.pcb_actv_dur[local_str:local_end+1],HISTBIN_WINDOW)
            print('local_mode =', local_mode)
            print('------------------------')
            data = pd.DataFrame([[str_index,end_index,local_mode]],columns=['str_index','end_index','local_mode'])
            mode_df = mode_df.append(data)
            del data
        #end-if    
    #end-for
    
    return mode_df

#end-proc

#--------------------------------------------

def get_mode(inp_srs,HISTBIN_WINDOW):
    hist_df = pd.DataFrame(columns=['start','end','no_occur'])
    start = 0
    while (start <= np.max(inp_srs)):
        end = start + HISTBIN_WINDOW
        no_occur = np.sum((inp_srs >= start) & (inp_srs < end))
        data = pd.DataFrame([[start,end,no_occur]],columns=['start','end','no_occur'])
        hist_df = hist_df.append(data)
        del data
        start = end
    #end-while   

    hist_df = hist_df.reset_index()
    hist_df = hist_df.iloc[:,1:len(hist_df.columns)]

    #plt.figure(figsize=(18,6));
    #plt.stem(hist_df.start,hist_df.no_occur); plt.grid();
    
    MAX_OCCUR = hist_df.no_occur.max()
    a = hist_df.index[hist_df.no_occur == MAX_OCCUR]
    max_ind = np.asscalar(a[0])
    #max_ind = np.asscalar(hist_df.index[hist_df.no_occur == MAX_OCCUR])
    mode = (hist_df.start[max_ind] + hist_df.end[max_ind]) / 2
    print('Mode =', mode)
    
    return mode
#end-proc
