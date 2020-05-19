#******************************************************************************************************************************************
# TITLE     : ROUTINE_RAWACCL_TO_BINRYSEQ
# AUTHOR    : PRAKASH HIREMATH M
# DATE      : AUG 2018 - JUN 2019
# INSTITUTE : INDIAN INSTITUTE OF SCIENCE
#******************************************************************************************************************************************


#******************************************************************************************************************************************
# VERSION HISTORY
#******************************************************************************************************************************************
# DATE (YYYY-MM-DD) | AUTHOR              | COMMENTS
#------------------------------------------------------------------------------------------------------------------------------------------
# 2019-10-11        | PRAKASH HIREMATH M  | Initial version
#******************************************************************************************************************************************

#Transform raw acceleration data to a feature-extracted binary sequence

import pandas as pd
import numpy as np
import scipy as sp

import csv
import datetime

from matplotlib import pyplot as plt
from matplotlib import dates  as md 
from matplotlib.colors import LogNorm

#==============================================================================================

#PROCEDURE FOR CONVERTING FROM RAW ACCELERATION TO BINARY SEQUENCE

print('Start of definition of the rawaccl_to_binryseq procedure', datetime.datetime.now())
print('Version currently used was compiled at 2019-06-25 17:08')
print('Inputs are inp_vibr_df,downsample_rate,use_filt_accl_flag,use_quant_sig_flag,HYS_LOW_THRESH,HYS_HIGH_THRESH')

def rawaccl_to_binryseq(inp_vibr_df,downsample_rate,use_filt_accl_flag,use_quant_sig_flag,HYS_LOW_THRESH,HYS_HIGH_THRESH):
    """
    Purpose : Conversion of raw acceleration data to binary sequence
    Inputs  : inp_vibr_df        - The dataframe contains the vibration data
              downsample_rate    - The downsampling rate (default = 1)
              use_filt_accl_flag - Flag to say whether to use filtered acceleration or not
              use_quant_sig_flag - Flag to say whether to use quantized signal or not
              HYS_LOW_THRESH     - lower threshold for hysteresis
              HYS_HIGH_THRESH    - higher threshold for hysteresis
    Output  : filt_accl_df       - Output dataframe with filtered signals      
    """
    
    STR_TIME = datetime.datetime.now()
    
    print('=======================================================')
    print("START : ", STR_TIME)
    print('=======================================================')
    
    from scipy import signal
    
    
    
    sig = inp_vibr_df.net_accl
    nrm = (sig - np.mean(sig)) / np.std(sig)
    print('Mean      of normalized signal =', np.mean(nrm))
    print('Deviation of normalized signal =', np.std(nrm))
    print('-------------------------------------------------------')
    
    #Perform the rolling-deviation
    ROLL_DEV_WIN = 300
    rlgdev = nrm.rolling(window=ROLL_DEV_WIN,center=True).std()
    
    #Perform Wiener filtering
    LOSS = np.ceil(ROLL_DEV_WIN / 2).astype(int)

    #Store the timestamps
    tmstmp_arr = np.array(inp_vibr_df.timestamp[0+LOSS:len(inp_vibr_df)-LOSS])[:,np.newaxis]
    
    print('Performing Wiener filtering')
    WIEN_FILT_WIN = 36
    x = np.array(rlgdev[0+LOSS:len(inp_vibr_df)-LOSS])  
    y = signal.wiener(x,mysize=WIEN_FILT_WIN)
    
    x = x[:,np.newaxis]
    y = y[:,np.newaxis]

    filt_sig_df = pd.DataFrame(columns=['timestamp','rlng_accl','filt_accl'])
    filt_sig_df['timestamp'] = tmstmp_arr[:,0]
    filt_sig_df['rlng_accl'] = x[:,0] 
    filt_sig_df['filt_accl'] = y[:,0] 

    #Downsampling
    print('Performing downsampling by :', downsample_rate)
    filt_sig_df = filt_sig_df[filt_sig_df.index % downsample_rate == 0]
    filt_sig_df = filt_sig_df.reset_index()
    filt_sig_df = filt_sig_df.iloc[:,1:len(filt_sig_df.columns)]
    
    if (use_filt_accl_flag == 'Y'):
        acc_sig = filt_sig_df.filt_accl
    else:
        acc_sig = filt_sig_df.rlng_accl
    #end-if
    
    print('Performing quantization')
    
    quant_sig \
    = 0.00 * ((acc_sig >= 0.00) & (acc_sig < 0.05)) \
    + 0.05 * ((acc_sig >= 0.05) & (acc_sig < 0.10)) \
    + 0.10 * ((acc_sig >= 0.10) & (acc_sig < 0.15)) \
    + 0.15 * ((acc_sig >= 0.15) & (acc_sig < 0.20)) \
    + 0.20 * ((acc_sig >= 0.20) & (acc_sig < 0.25)) \
    + 0.25 * ((acc_sig >= 0.25) & (acc_sig < 0.30)) \
    + 0.30 * ((acc_sig >= 0.30) & (acc_sig < 0.35)) \
    + 0.35 * ((acc_sig >= 0.35) & (acc_sig < 0.40)) \
    + 0.40 * ((acc_sig >= 0.40) & (acc_sig < 0.45)) \
    + 0.45 * ((acc_sig >= 0.45) & (acc_sig < 0.50)) \
    + 0.50 * ((acc_sig >= 0.50) & (acc_sig < 0.55)) \
    + 0.55 * ((acc_sig >= 0.55) & (acc_sig < 0.60)) \
    + 0.60 * ((acc_sig >= 0.60) & (acc_sig < 0.65)) \
    + 0.65 * ((acc_sig >= 0.65) & (acc_sig < 0.70)) \
    + 0.70 * ((acc_sig >= 0.70) & (acc_sig < 0.75)) \
    + 0.75 * ((acc_sig >= 0.75) & (acc_sig < 0.80)) \
    + 0.80 * ((acc_sig >= 0.80) & (acc_sig < 0.85)) \
    + 0.85 * ((acc_sig >= 0.85) & (acc_sig < 0.90)) \
    + 0.90 * ((acc_sig >= 0.90) & (acc_sig < 0.95)) \
    + 0.95 * ((acc_sig >= 0.95) & (acc_sig < 1.00)) \
    + 1.00 * ((acc_sig >= 1.00) & (acc_sig < 1.05)) \
    + 1.05 * ((acc_sig >= 1.05) & (acc_sig < 1.10)) \
    + 1.10 * ((acc_sig >= 1.10) & (acc_sig < 1.15)) \
    + 1.15 * ((acc_sig >= 1.15) & (acc_sig < 1.20)) \
    + 1.20 * ((acc_sig >= 1.20) & (acc_sig < 1.25)) \
    + 1.25 * ((acc_sig >= 1.25) & (acc_sig < 1.30)) \
    + 1.30 * ((acc_sig >= 1.30) & (acc_sig < 1.35)) \
    + 1.35 * ((acc_sig >= 1.35) & (acc_sig < 1.40)) \
    + 1.40 * ((acc_sig >= 1.40) & (acc_sig < 1.45)) \
    + 1.45 * ((acc_sig >= 1.45) & (acc_sig < 1.50)) \
    + 1.50 * (acc_sig >= 1.50)\
    ;
    
    '''
    quant_sig \
    = 0.0 * ((acc_sig >= 0.0) & (acc_sig < 0.1)) \
    + 0.1 * ((acc_sig >= 0.1) & (acc_sig < 0.2)) \
    + 0.2 * ((acc_sig >= 0.2) & (acc_sig < 0.3)) \
    + 0.3 * ((acc_sig >= 0.3) & (acc_sig < 0.4)) \
    + 0.4 * ((acc_sig >= 0.4) & (acc_sig < 0.5)) \
    + 0.5 * ((acc_sig >= 0.5) & (acc_sig < 0.6)) \
    + 0.6 * ((acc_sig >= 0.6) & (acc_sig < 0.7)) \
    + 0.7 * ((acc_sig >= 0.7) & (acc_sig < 0.8)) \
    + 0.8 * ((acc_sig >= 0.8) & (acc_sig < 0.9)) \
    + 0.9 * ((acc_sig >= 0.9) & (acc_sig < 1.0)) \
    + 1.0 * ((acc_sig >= 1.0) & (acc_sig < 1.1)) \
    + 1.1 * ((acc_sig >= 1.1) & (acc_sig < 1.2)) \
    + 1.2 * ((acc_sig >= 1.2) & (acc_sig < 1.3)) \
    + 1.3 * ((acc_sig >= 1.3) & (acc_sig < 1.4)) \
    + 1.4 * ((acc_sig >= 1.4) & (acc_sig < 1.5)) \
    + 1.5 * (acc_sig >= 1.5)\
    ;
    '''
    
    filt_sig_df['quant_sig'] = quant_sig
    
    #Obtain histogram
    if (use_quant_sig_flag == 'Y'):
        h1_df,h1_mode = gen_histogram(quant_sig,0,0.05)
    else:
        h1_df,h1_mode = gen_histogram(acc_sig,0,0.05)
    #end-if
    
    for i in range (0,len(h1_df)):
        print(h1_df.start[i], ':', h1_df.end[i], '|', h1_df.no_occur[i])
    #end-for
    
    # plt.figure(figsize=(18,6));
    # plt.stem(h1_df.start,h1_df.no_occur); plt.grid();
    
    #Determine lower threshold
    # a = h1_df.query('(start >= 0.3) & (start <= 0.6) & (no_occur > 0)')
    # b = a.sort_values('no_occur',ascending=True)
    # b = b.reset_index()
    # b = b.iloc[:,1:len(b.columns)]
    
    # if (len(b) > 0):
    #     if (HYS_LOW_THRESH > 0.3):
    #         HYS_LOW_THRESH = np.round(b.start[0],2) #Precision 2 places after decimal point 
    #     else:
    #         HYS_LOW_THRESH = HYS_LOW_THRESH  #Set to the level specified in input
    #     #end-if    
    # else:
    #     HYS_LOW_THRESH = 0.3      #Set to default low level
    #end-if
    
    print('Hysteresis Thresholds | HYS_LOW_THRESH =', HYS_LOW_THRESH, '| HYS_HIGH_THRESH =', HYS_HIGH_THRESH)
    
    if (use_quant_sig_flag == 'Y'):
        trnry_sig \
        = 1.0 * (quant_sig >= HYS_HIGH_THRESH) \
        + 0.0 * (quant_sig <= HYS_LOW_THRESH)  \
        + 0.5 * ((quant_sig > HYS_LOW_THRESH) & (quant_sig < HYS_HIGH_THRESH)) 
    else:
        trnry_sig \
        = 1.0 * (acc_sig >= HYS_HIGH_THRESH) \
        + 0.0 * (acc_sig <= HYS_LOW_THRESH)  \
        + 0.5 * ((acc_sig > HYS_LOW_THRESH) & (acc_sig < HYS_HIGH_THRESH))
    #endif 
    
    filt_sig_df['trnry_sig'] = trnry_sig
    
    #Obtain binary sequence
    print('Conversion from ternary sequence to binary sequence')
    
    binry_sig = trnry_sig * 1.0
    
    if (trnry_sig[0] >= 0.5):
        binry_sig[0] = 1.0
    else:
        binry_sig[0] = 0.0
    #endif    
    
    for i in range(1,len(trnry_sig)):
        if (trnry_sig[i] == 0.5):  
            binry_sig[i] = binry_sig[i-1]
        #endif
        
        if (i % 1000000 == 0):
            print('Processing at i = ',i)
        #end-if  
    #end-for
    
    filt_sig_df['binry_sig'] = binry_sig
    
    END_TIME = datetime.datetime.now()
    
    print('=======================================================')
    print("END   : ", END_TIME)
    print('=======================================================')
    
    DUR_TS    = pd.Timestamp(END_TIME) - pd.Timestamp(STR_TIME)
    EXEC_TIME = pd.Timedelta(DUR_TS).total_seconds()
    
    print("Execution time =",EXEC_TIME/60,"mins")
    print('=======================================================')
    
    return filt_sig_df

#endproc
print('End   of definition of the procedure', datetime.datetime.now())


#==========================================================================================
def gen_histogram(inp_series,START,HISTBIN_WINDOW):
    
    hist_df = pd.DataFrame(columns=['start','end','no_occur'])
    start = START
    while (start <= np.max(inp_series)):
        end = start + HISTBIN_WINDOW
        no_occur = np.sum((inp_series >= start) & (inp_series < end))
        data = pd.DataFrame([[start,end,no_occur]],columns=['start','end','no_occur'])
        hist_df = hist_df.append(data)
        del data
        start = end
    #end-while   

    hist_df = hist_df.reset_index()
    hist_df = hist_df.iloc[:,1:len(hist_df.columns)]

    MAX_OCCUR = hist_df.no_occur.max()
    a = hist_df.index[hist_df.no_occur == MAX_OCCUR]
    max_ind = np.asscalar(a[0])
    mode = (hist_df.start[max_ind] + hist_df.end[max_ind]) / 2
    print('Mode =', mode)
    
    return hist_df,mode

#end-proc