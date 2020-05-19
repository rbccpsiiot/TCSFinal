# -*- coding: utf-8 -*-
"""
Created on Apr 2019

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

#=====================================================================================

#Merging algorithm using proximity data

print('Start of defining procedure :', datetime.datetime.now())
print('Version : 2019-04-09 21:59')

def merge_pxmty_algo(inp_df,pxmty_df,inp_binry_sig,THRESHOLD,HIGH_END):
    
    STR_TIME = datetime.datetime.now()
    
    print('=======================================================')
    print("START : ", STR_TIME)
    print('=======================================================')
    
    #Create an array of timestamps where proximity sensor identifies PCB
    spike_df  = pxmty_df.query('data_proximity == 0').loc[:,['timestamp']]
    spike_arr = np.array(spike_df.timestamp)

    out_df = pd.DataFrame(columns=['arvl_index','arvl_tmstmp','dptr_index','dptr_tmstmp','no_of_parts','proc_dur','maint_dur','weightage'])
    out_binry_sig = 1.0 * inp_binry_sig

    i                 = 0
    END_FLAG          = 0
    no_of_merged_pcbs = 0
    
    while (END_FLAG == 0):
    
        merge_flag = 0                             #initialization
        if (i >= len(inp_df)):                     #already reached end of dataframe
            END_FLAG = 1
        elif (i == len(inp_df) - 1):              #last entry of the dataframe  
            merge_flag = 0
        else:    
            if (inp_df.weightage[i] <= THRESHOLD):
                str_tmstmp = str(pd.Timestamp(inp_df.arvl_tmstmp[i]) - pd.Timedelta('0 days 00:00:10.000000'))
                str_tmstmp = str_tmstmp.replace(' ','T')                
                end_tmstmp = str(pd.Timestamp(inp_df.arvl_tmstmp[i]) + pd.Timedelta('0 days 00:00:10.000000'))              
                end_tmstmp = end_tmstmp.replace(' ','T')
                
                spk_i_num = np.sum((spike_arr >= str_tmstmp) & (spike_arr <= end_tmstmp))
                
                print(i, '|', str_tmstmp, ':', end_tmstmp, '|', spk_i_num) 
                
                if (spk_i_num > 0): #valid and first part of pcb
                    if (inp_df.weightage[i+1] <= THRESHOLD):
                        str_tmstmp = str(pd.Timestamp(inp_df.arvl_tmstmp[i+1]) - pd.Timedelta('0 days 00:00:10.000000'))
                        str_tmstmp = str_tmstmp.replace(' ','T')                
                        end_tmstmp = str(pd.Timestamp(inp_df.arvl_tmstmp[i+1]) + pd.Timedelta('0 days 00:00:10.000000'))              
                        end_tmstmp = end_tmstmp.replace(' ','T')
                
                        spk_ipl_num = np.sum((spike_arr >= str_tmstmp) & (spike_arr <= end_tmstmp))
                        
                        print((i+1), '|', str_tmstmp, ':', end_tmstmp, '|', spk_ipl_num)
                        
                        if (spk_ipl_num == 0): #not a first part of pcb processing
                            cumul_weightage = inp_df.weightage[i] + inp_df.weightage[i+1]
                            if (cumul_weightage <= HIGH_END):
                                merge_flag = 1
                                print('i =', i, '| merge_flag =', merge_flag)
                            #endif
                        #endif
                    #endif
                #endif
            #endif
        #endif
    
        if (END_FLAG == 0):
            if (merge_flag == 1):
                arvl_index  = inp_df.arvl_index[i]
                arvl_tmstmp = inp_df.arvl_tmstmp[i]
                dptr_index  = inp_df.dptr_index[i+1]
                dptr_tmstmp = inp_df.dptr_tmstmp[i+1]
                no_of_parts = inp_df.no_of_parts[i] + 1
                proc_dur    = inp_df.proc_dur[i] + inp_df.proc_dur[i+1]
                maint_dur   = inp_df.maint_dur[i] + pd.Timedelta(pd.Timestamp(inp_df.arvl_tmstmp[i+1]) - pd.Timestamp(inp_df.dptr_tmstmp[i])).total_seconds()
                weightage   = inp_df.weightage[i] + inp_df.weightage[i+1]
                
                #Indication for maintenance duration
                STR = inp_df.dptr_index[i]
                END = inp_df.arvl_index[i+1]
                out_binry_sig[STR:END] = 0.5
                
                i = i + 2
                no_of_merged_pcbs = no_of_merged_pcbs + 1
            else:
                arvl_index  = inp_df.arvl_index[i]
                arvl_tmstmp = inp_df.arvl_tmstmp[i]
                dptr_index  = inp_df.dptr_index[i]
                dptr_tmstmp = inp_df.dptr_tmstmp[i]
                no_of_parts = inp_df.no_of_parts[i]
                proc_dur    = inp_df.proc_dur[i]
                maint_dur   = inp_df.maint_dur[i]
                weightage   = inp_df.weightage[i]
                i = i + 1  
            #endif
        
            data = pd.DataFrame([[arvl_index,arvl_tmstmp,dptr_index,dptr_tmstmp,no_of_parts,proc_dur,maint_dur,weightage]],columns=['arvl_index','arvl_tmstmp','dptr_index','dptr_tmstmp','no_of_parts','proc_dur','maint_dur','weightage'])
            out_df = out_df.append(data)
            del data
        #endif
        
    #endwhile
        
    out_df = out_df.reset_index()
    out_df = out_df.iloc[:,1:len(out_df.columns)]
    
    print ('No. of merged PCBS =', no_of_merged_pcbs)
    
    END_TIME = datetime.datetime.now()
    
    print('=======================================================')
    print("END   : ", END_TIME)
    print('=======================================================')
    
    DUR_TS    = pd.Timestamp(END_TIME) - pd.Timestamp(STR_TIME)
    EXEC_TIME = pd.Timedelta(DUR_TS).total_seconds()
    
    print("Execution time =",EXEC_TIME/60,"mins")
    print('=======================================================')
    
    return out_df,out_binry_sig,no_of_merged_pcbs

#endproc
print('End   of defining procedure :', datetime.datetime.now())