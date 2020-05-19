import pandas as pd
import os
import sys
import time
import matplotlib.pyplot as plt
import scipy.signal
import numpy as np
import seaborn as sns
import datetime


if len(sys.argv) <  2:

        print("No filename passed. Place the CSV file in the same folder.")

        exit(2)

spfile=sys.argv[1]

if not os.path.isfile(spfile):

        print("File not found!")

#         exit(1)

try:
    raw_sp = pd.read_csv(spfile, usecols =['time', 'c1'])

except:

        print("Invalid file!")
        exit(3)

# raw_sp = pd.read_csv('SP_EM11.csv', usecols =['time', 'c1'])

raw_sp['time'] =  pd.to_datetime(raw_sp['time'])
raw_sp=raw_sp.rename(columns={'time':'timestamp'})
raw_sp['ist_time']=raw_sp['timestamp']+datetime.timedelta(hours=5, minutes=30)

test_sp=raw_sp

printing_rolling_window = 6
cleaning_rolling_window = 12
test_sp['sum']=pd.Series.to_frame(test_sp['c1'].rolling(printing_rolling_window, center=True).sum())
test_sp['sum_forcleaning']=pd.Series.to_frame(test_sp['c1'].rolling(cleaning_rolling_window, center=True).sum())

#make a new column in test_sp called idle, and set everything to 0.5 
test_sp['idle']=0.5

#make first and last row of dataframe 0 so that peaks are detected 
test_sp.ix[0, 'idle']=(test_sp.ix[0, 'idle'])=0
test_sp.ix[-1, 'idle']=(test_sp.ix[0, 'idle'])=0

sptime_thresh=20
printing_height_thresh = 10,15
cleaning_height_thresh = 30

#find peaks to identify printing and cleaning events
printing_delays_raw=scipy.signal.find_peaks(test_sp['sum'],height=(printing_height_thresh),distance=sptime_thresh, width=1)
printing_delays_raw_df=pd.DataFrame({"sample_number":printing_delays_raw[0], "working_time":printing_delays_raw[1]['widths']})

cleaning_delays_raw=scipy.signal.find_peaks(test_sp['sum_forcleaning'], height=cleaning_height_thresh, distance=sptime_thresh, width=1)
cleaning_delays_raw_df=pd.DataFrame({"sample_number":cleaning_delays_raw[0], "working_time":cleaning_delays_raw[1]['widths']})

#make all the area of peaks identified for both printing and cleaning [idle column] value = 0 
for index, i in enumerate(printing_delays_raw[0]):
    test_sp.ix[int(printing_delays_raw[1]['left_ips'][index]) : int(printing_delays_raw[1]['right_ips'][index]), 'idle']=0


for index, i in enumerate(cleaning_delays_raw[0]):
    test_sp.ix[int(cleaning_delays_raw[1]['left_ips'][index]) : int(cleaning_delays_raw[1]['right_ips'][index]), 'idle']=0


idle_height_thresh = 0.25
#identify idle periods with height thresh =0.25 as all printing and cleaning periods have been set to 0 and 
#remaining [idle] values in test_sp are all 0.5
idle_delays_raw=scipy.signal.find_peaks(test_sp['idle'], height=(idle_height_thresh), width=1)
idle_delays_raw_df=pd.DataFrame({"sample_number":idle_delays_raw[0], "working_time":idle_delays_raw[1]['widths']})

#create separate dfs for printing, cleaning and idle periods with columns timestamp, event, working time
printings=pd.DataFrame({"timestamp":test_sp.iloc[printing_delays_raw_df.sample_number].timestamp, "event":1, "working_time":printing_delays_raw_df.working_time.tolist()})
printings.reset_index(inplace=True)
printings.drop('index', axis=1, inplace=True)
cleanings=pd.DataFrame({"timestamp":test_sp.iloc[cleaning_delays_raw_df.sample_number].timestamp, "event":2, "working_time":cleaning_delays_raw_df.working_time.tolist()})
cleanings.reset_index(inplace=True)
cleanings.drop('index', axis=1, inplace=True)
idles=pd.DataFrame({"timestamp":test_sp.iloc[idle_delays_raw_df.sample_number].timestamp, "event":0, "working_time":idle_delays_raw_df.working_time.tolist()})
idles.reset_index(inplace=True)
idles.drop('index', axis=1, inplace=True)

#add energy column for each event (printing,cleaning and idle) to each df
for x, row in printings.iterrows():
    printings.ix[x,'energy']=test_sp.ix[int(printing_delays_raw[1]['left_ips'][x]):int(printing_delays_raw[1]['right_ips'][x]), 'c1'].sum()*230/3600000

for x, row in cleanings.iterrows():
    cleanings.ix[x,'energy']=test_sp.ix[int(cleaning_delays_raw[1]['left_ips'][x]):int(cleaning_delays_raw[1]['right_ips'][x]), 'c1'].sum()*230/3600000

for x, row in idles.iterrows():
    idles.ix[x,'energy']=test_sp.ix[int(idle_delays_raw[1]['left_ips'][x]):int(idle_delays_raw[1]['right_ips'][x]), 'c1'].sum()*230/3600000


# SP_events.index=SP_events.time
# SP_events.drop('time', axis=1, inplace=True) #do we finally want it as time or timestamp to reinsert into DB
# SP_events.drop('index', axis=1, inplace=True)

# cleanings.index=cleanings.timestamp
# cleanings.drop('timestamp', axis=1, inplace=True)
# cleanings.drop('index', axis=1, inplace=True)

# idles.index=idles.time
# idles.drop('time', axis=1, inplace=True)
# idles.drop('index', axis=1, inplace=True)

# SP_events=SP_events.append(cleanings)
# SP_events=SP_events.append(idles)

# SP_events.reset_index(inplace=True)
# SP_events.drop('index', axis=1, inplace=True)
# SP_events.drop('level_0', axis=1, inplace=True)

# SP_events['device']='screenprinter'
# print(SP_events)


######Get Parameters required for Simpy Parameter file ###### 

# timestr = time.strftime("%H-%M")
# print('Printing time Mode: ', printings.working_time[printings['event']==1].mode().mean())
# print('Cleaning time Mode: ', cleanings.working_time[cleanings['event']==2].mode().mean())
# parameters=open('/home/tcsgoa/Desktop/LiveParameters/SPparameters.txt','a+')
# parameters.write(timestr +'\tSP printing time mode: ' + str(printings.working_time[printings['event']==1].mode().mean())+'\n')
# parameters.write(timestr +'\tSP cleaning time mode: ' + str(cleanings.working_time[cleanings['event']==2].mode().mean())+'\n')
# parameters.close()

####If you want to save SP states/events to a file (Also need to uncomment SP_events portion above) ######

# if not os.path.exists('/mnt/UltraHD/streamingStates/SP'):

#     os.makedirs('/mnt/UltraHD/streamingStates/SP')


# directory='/mnt/UltraHD/streamingStates/SP'

# timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
# print("Saving States with file name -", timestr+"_SP.csv")
# SP_events.to_csv('/mnt/UltraHD/streamingStates/SP/'+ timestr+"_SP.csv")


#### Pushing states, times and energy to Influx DB ###
from influxdb import InfluxDBClient
import json

IFhost="localhost"
IFport=8086
IFdbname = 'IIOT'

client = InfluxDBClient(host=IFhost, port=IFport,database=IFdbname)

events_batch=[]

# events_batch = json.loads(LL_events.to_json())

for i,row in printings.iterrows():
    events_batch.append({ 'measurement': 'EVENTS','tags':{'Machine':'SP'}, 'time':row.timestamp ,'fields': {'Printing event':int(row.event),'Printing Time':float(row.working_time),"Printing Energy":float(row.energy)}})

    
for i,row in cleanings.iterrows():
    events_batch.append({ 'measurement': 'EVENTS','tags':{'Machine':'SP'}, 'time':row.timestamp ,'fields': {'Cleaning event':int(row.event),'Cleaning Time':float(row.working_time),"Cleaning Energy":float(row.energy)}})

    
for i,row in idles.iterrows():
    events_batch.append({ 'measurement': 'EVENTS','tags':{'Machine':'SP'}, 'time':row.timestamp ,'fields': {'Idle event':int(row.event),'Idle Time':float(row.working_time),"Idle Energy":float(row.energy)}})


client.write_points(events_batch,batch_size=len(printings))
client.write_points(events_batch,batch_size=len(cleanings))
client.write_points(events_batch,batch_size=len(idles))