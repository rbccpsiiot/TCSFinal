import pandas as pd
import numpy as np
import scipy as sp
import os
import sys
import time
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import datetime

from matplotlib import pyplot as plt
from matplotlib import dates  as md 
from matplotlib.colors import LogNorm

#Import routines
import routine_rawaccl_to_binryseqPP1  
import routine_get_pcb_durPP1          
import routine_elim_spur_pcbPP1        
import routine_get_pcb_level_dataPP1   
import routine_merging_algoPP1  
import routine_rev_merge_pxmty_algoPP1


if len(sys.argv) <  2:

        print("No filename passed. Place the CSV file in the same folder.")

        exit(2)

pp1file=sys.argv[1]

if not os.path.isfile(pp1file):

        print("File not found!")

        exit(1)

try:
    pp1_vibr_file = pd.read_csv(pp1file, usecols = ['time','ax','ay','az'])
    raw_pp_current=pd.read_csv('PP1_EM11.csv', usecols=['time', 'c1', 'c2', 'c3'])
    pp1_pxstr_file = pd.read_csv('PP2_prox11.csv',usecols=['time','PP2Entry'])
except:
        print("Invalid file!")
        exit(3)

#Vibration file 
pp1_vibr_file = pp1_vibr_file.sort_values(by="time")
pp1_vibr_file = pp1_vibr_file.reset_index()
pp1_vibr_file = pp1_vibr_file.assign(net_accl = np.sqrt(pp1_vibr_file['ax']**2 + pp1_vibr_file['ay']**2 + pp1_vibr_file['az']**2))
pp1_vibr_file['time']=pd.to_datetime(pp1_vibr_file['time'])
pp1_vibr_file=pp1_vibr_file.rename(columns={'time':'timestamp'})

#Current File 
raw_pp_current['time']=pd.to_datetime(raw_pp_current['time'])
raw_pp_current=raw_pp_current.rename(columns={'time':'timestamp'})
raw_pp_current['total_current']=raw_pp_current['c1']+raw_pp_current['c2']+raw_pp_current['c3']

#Proximity File 
pp1_pxstr_file=pp1_pxstr_file.rename(columns={'time':'timestamp'})

#-------------------------------------------------------------------------
#Raw-acceleration to binary sequene conversion
filt_sig_pp1 = routine_rawaccl_to_binryseqPP1.rawaccl_to_binryseq(pp1_vibr_file,1,'N','Y',0.2,0.4)

#Detect PCBs and obtain PCB processing durations
pcb_data_pp1 = routine_get_pcb_durPP1.get_pcb_dur(filt_sig_pp1.binry_sig)

#Eliminate spurious PCB detections
filt_sig_pp1['cor_binry_sig'] = routine_elim_spur_pcbPP1.elim_spur_pcb(filt_sig_pp1.binry_sig,pcb_data_pp1,950)

#Recalculate PCB processing durations
pcb_data_pp1 = routine_get_pcb_durPP1.get_pcb_dur(filt_sig_pp1.cor_binry_sig)

#Obtain PCB level dataframe with weightages
pcb_level_pp1 = routine_get_pcb_level_dataPP1.get_pcb_level_data(filt_sig_pp1,pcb_data_pp1,50)

#Splitting algorithm to split detections that are counting more than 1 board as 1 
pcb_level_pp1.reset_index(inplace=True)
pcb_level_pp1.drop('index', axis=1, inplace=True)

tempdf=pcb_level_pp1
tempdf['nmodes']=0

#using the mode of the processing of 1 board to split those which are multiples of the mode
mod_actv_dur = routine_get_pcb_level_dataPP1.get_mode(pcb_data_pp1.pcb_actv_dur,50)/100
print(mod_actv_dur)

tseries = np.zeros(tempdf.shape[0])

#if the remainder (frac) after finding nmodes is more than 0.85, then nmodes becomes nmodes +1 
#else it remains as nmodes 
#if nmodes = 1 (regular detection) keep it as 1 board
for i, row in pcb_level_pp1.iterrows():
    nmodes=row.proc_dur/mod_actv_dur
    frac=nmodes%1
    nmodes=np.floor(nmodes)
    
    if (1-frac) <= .15:
        nmodes=np.floor(nmodes)+1
    
    if nmodes==1.0:
        continue
    tseries[i] = nmodes
tempdf['nmodes'] = tseries

print(tseries)

#taking only those boards which are counting multiple detections as 1 
temp_df1=tempdf[tempdf['nmodes']>1]

#finding the times of the split board detections by using numpy linspace 
# timestamps are converted to epoch times
split_times=[]
for i, row in temp_df1.iterrows():
    nmodes=int(row.nmodes)
    split_times.append(np.linspace(row.arvl_tmstmp.to_datetime64().astype('int'),row.dptr_tmstmp.to_datetime64().astype('int'),num=row.nmodes+1))

temp_df1.reset_index(inplace=True)

#new df PP_boards Split to indicate new board detections after splitting 
#board 1s dept timestamp == board 2s arvl timestamp 
#boards are split exactly by the number of modes 
PP_boardeventsSplit = pd.DataFrame()
for i, row in temp_df1.iterrows():
    nmodes=int(row.nmodes)
    wt=row.proc_dur/nmodes
#     en=row.energy/nmodes
#     if nmodes%2==0:
    for j in range(len(split_times[i])-1):
        ts1=pd.to_datetime(split_times[i][j])
        ts2=pd.to_datetime(split_times[i][j+1])
        PP_boardeventsSplit=PP_boardeventsSplit.append({"arvl_index":row.arvl_index, "arvl_tmstmp":ts1, "dptr_index":row.dptr_index, "dptr_tmstmp":ts2, "no_of_parts":1, "proc_dur": wt, "maint_dur":row.maint_dur, "weightage":wt/mod_actv_dur, "nmodes":1}, ignore_index=True)

print(PP_boardeventsSplit)

#dropping those that are counted as 1 board but should be more than 1
pcb_level_pp1.drop(tempdf[tempdf['nmodes']>1].index, inplace=True)

#adding those detections after splitting the boards based on the number of modes
pcb_level_pp1=pcb_level_pp1.append(PP_boardeventsSplit, ignore_index=True)
pcb_level_pp1 = pcb_level_pp1.sort_values(by="arvl_tmstmp")
pcb_level_pp1.reset_index(inplace=True)

pcb_level_pp1.drop('index', axis=1, inplace=True)
pcb_level_pp1.drop('nmodes', axis=1, inplace=True)

#newly created pcb_level df ready for merging 
pcb_merge_pp1 = pcb_level_pp1
mrg_binry_pp1 = filt_sig_pp1.cor_binry_sig

THRESHOLD = 0.95
HIGH_END  = 1.50

iter_one = 0
iter_two = 0

#reverse merging proximity sensor fusion using PP2 proximity triggers
PROC_ONE_END_FLAG = 0
while (PROC_ONE_END_FLAG == 0):
    
    iter_one = iter_one + 1
    print('PROC-ONE-ITERATION :', iter_one)
    
    pcb_merge_pp1,mrg_binry_pp1,no_of_merged_pcbs = routine_rev_merge_pxmty_algoPP1.rev_merge_pxmty_algo    \
    (inp_df        = pcb_merge_pp1                                      \
    ,pxmty_df      = pp1_pxstr_file      \
    ,inp_binry_sig = mrg_binry_pp1                         \
    ,THRESHOLD     = THRESHOLD                                               \
    ,HIGH_END      = HIGH_END                                                \
    )
    
    if (no_of_merged_pcbs == 0):
        PROC_ONE_END_FLAG = 1
    #end-if
    
    print ('=============================================')

#merging without proximity triggers,just based on weightages 
PROC_TWO_END_FLAG = 0
while(PROC_TWO_END_FLAG == 0):
    
    iter_two = iter_two + 1
    print('PROC-TWO-ITERATION :', iter_two)
    
    pcb_merge_pp1,mrg_binry_pp1,no_of_merged_pcbs = routine_merging_algoPP1.merging_algo  \
    (inp_df        = pcb_merge_pp1                                   \
    ,inp_binry_sig = mrg_binry_pp1                                   \
    ,THRESHOLD     = THRESHOLD                                            \
    ,HIGH_END      = HIGH_END                                             \
    ) 
    
    if(no_of_merged_pcbs == 0):
        PROC_TWO_END_FLAG = 1
    #end-if
    
    print ('=============================================')

print(pcb_merge_pp1)


filt_sig_pp1['mrg_binry_sig'] = mrg_binry_pp1

#Energy Consumption calculations to find energy consumed per board and in various states (working and idle)
working_times_df=pd.DataFrame()

working_times_df['timestamp']=pcb_merge_pp1['arvl_tmstmp']
working_times_df['working_time']=pcb_merge_pp1['proc_dur']
working_times_df['event']=1
working_times_df['energy'] = pcb_merge_pp1.apply(lambda x: raw_pp_current.loc[(raw_pp_current.timestamp <= x.dptr_tmstmp) & (x.arvl_tmstmp <= raw_pp_current.timestamp), ['total_current']].sum()*230/3600000, axis=1)
print(working_times_df)
# working_times_df.drop('level_0', axis=1, inplace=True)

PP_temp_idle=filt_sig_pp1[['timestamp', 'mrg_binry_sig']]
PP_temp_idle['mrg_binry_sig']=PP_temp_idle['mrg_binry_sig']*-1

PP_temp_idle['mrg_binry_sig'].iloc[0]=(PP_temp_idle['mrg_binry_sig'].iloc[1]+1)%2*-1
PP_temp_idle['mrg_binry_sig'].iloc[-1]=(PP_temp_idle['mrg_binry_sig'].iloc[-2]+1)%2*-1

idle_times_raw=sp.signal.find_peaks(PP_temp_idle.mrg_binry_sig, height=(-0.4), width=1)
idle_times_raw_df=pd.DataFrame({"sample_number":idle_times_raw[0], "working_time":idle_times_raw[1]['widths']/100})

for x, row in idle_times_raw_df.iterrows():
    idle_times_raw_df.ix[x,'start_time']=PP_temp_idle.iloc[int(idle_times_raw[1]['left_ips'][x])].timestamp
    idle_times_raw_df.ix[x,'end_time']=PP_temp_idle.iloc[int(idle_times_raw[1]['right_ips'][x])].timestamp
    idle_times_raw_df.ix[x,'timestamp']=PP_temp_idle.iloc[int(idle_times_raw[0][x])].timestamp

idle_times_raw_df['event']=0
idle_times_raw_df['energy'] = idle_times_raw_df.apply(lambda x: raw_pp_current.loc[(raw_pp_current.timestamp <= x.end_time) & 
                                                            (x.start_time <= raw_pp_current.timestamp),
                                                            ['total_current']].sum()*230/3600000, axis=1)

print(idle_times_raw_df)

working_times_df=working_times_df[['event', 'working_time', 'energy','timestamp']]
idle_times_df=idle_times_raw_df[['event', 'working_time', 'energy', 'timestamp']]

print(idle_times_df['energy'].sum(axis = 0, skipna = True))
print(working_times_df['energy'].sum(axis = 0, skipna = True))


#Pushing states, times and energy to Influx DB 
from influxdb import InfluxDBClient
import json

IFhost="localhost"
IFport=8086
IFdbname = 'IIOT'

client = InfluxDBClient(host=IFhost, port=IFport,database=IFdbname)

events_batch=[]

# events_batch = json.loads(LL_events.to_json())

for i,row in idle_times_df.iterrows():
    events_batch.append({ 'measurement': 'EVENTS','tags':{'Machine':'PP1'}, 'time':row.timestamp ,'fields': {'PP1 Idle Event':int(row.event),'PP1 Idle Time':float(row.working_time),"PP1 Idle Energy":float(row.energy)}})
    
for i,row in working_times_df.iterrows():
    events_batch.append({ 'measurement': 'EVENTS','tags':{'Machine':'PP1'}, 'time':row.timestamp ,'fields': {'PP1 Processing Event':int(row.event),'PP1 Processing Time':float(row.working_time),"PP1 Processing Energy":float(row.energy)}})


client.write_points(events_batch,batch_size=len(idle_times_df))
client.write_points(events_batch,batch_size=len(working_times_df))


# PP_events=pd.DataFrame()

# try:
#     PP_events=PP_events.append(working_times_df)
# except:
#     print()
# try:    
#     PP_events=PP_events.append(idle_times_df)
# except:
#     print()

# try:
#     PP_events.index=PP_events.timestamp
#     PP_events.drop('timestamp', axis=1, inplace=True)
#     PP_events['device']='pickandplace1'
#     print(PP_events)
# except:
#     print('No events found')
#     sys.exit(1)

######Get Parameters required for Simpy Parameter file ######

# timestr = time.strftime("%H-%M")
# print('PP1 working time mode: ', PP_events[PP_events.event==1].working_time.mode().mean())
# parameters=open('/home/richard/Desktop/LiveParameters/PP1parameters.txt','a+')
# parameters.write(timestr +'\tPP1 working time mode: ' + str(PP_events[PP_events.event==1].working_time.mode().mean())+'\n')
# parameters.close()


####If you want to save PP2 states/events to a file (Also need to uncomment PP_events portion above to create new DF) ######

# if not os.path.exists('/mnt/UltraHD/streamingStates/merging/PP1'):

#     os.makedirs('/mnt/UltraHD/streamingStates/merging/PP1')

# directory='/mnt/UltraHD/streamingStates/PP1'

# timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
# print("Saving States with file name -", timestr+"_PP1.csv")
# PP_events.to_csv('/mnt/UltraHD/streamingStates/PP1/'+ timestr+"_PP1.csv")
# pcb_merge_pp1.to_csv('/mnt/UltraHD/streamingStates/merging/PP1/'+ timestr+"_merging_correction_PP1.csv")