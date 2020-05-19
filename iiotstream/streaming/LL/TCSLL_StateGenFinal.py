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

ldfile=sys.argv[1]

if not os.path.isfile(ldfile):

        print("File not found!")
# ldfile = pd.read_csv('LL_IMU4.csv')

# raw_ll=pd.read_csv('LL_IMU11.csv', usecols=['time', 'ax', 'az'])

try:
        
         raw_ll=pd.read_csv(ldfile, usecols=['time', 'ax', 'az'])

except:

        print("Invalid file!")
        exit(2)


raw_ll['time'] =  pd.to_datetime(raw_ll['time'])
raw_ll=raw_ll.rename(columns={'time':'timestamp'})
raw_ll['ist_time']=raw_ll['timestamp']+datetime.timedelta(hours=5, minutes=30)

raw_ll["acc"] = ( raw_ll["ax"]**2 + raw_ll["az"]**2 ) ** 0.5

acc=raw_ll[["timestamp", "acc"]]
acc.set_index('timestamp')
test_ll=acc

rolling_window = 150
test_ll['rlg_acc']=pd.Series.to_frame(test_ll['acc'].rolling(rolling_window, center=True).std())

time_thresh=15
height_thresh = 0.04
sampling_rate = 100
board=scipy.signal.find_peaks(test_ll.rlg_acc, height=(height_thresh), distance=time_thresh*sampling_rate, width=1)
differ=np.diff(board[0])
differ=differ.tolist()

loading_delays_rawdf=pd.DataFrame({"sample_number":board[0], "working_time":board[1]['widths']/sampling_rate})
LL_events=pd.DataFrame({"timestamp":test_ll.iloc[loading_delays_rawdf.sample_number].timestamp, "event":1, "working_time":(loading_delays_rawdf.working_time).tolist()})

# LL_events.index=LL_events.timestamp.apply(lambda x: x.isoformat())
# LL_events.drop('timestamp', axis=1, inplace=True)
LL_events['energy']=float('0')
LL_events['device']='loader'

print(LL_events)

######Get Parameters required for Simpy Parameter file ###### 

# timestr = time.strftime("%H-%M")
# print('LL loading time mode: ', LL_events.working_time.mode().mean())
# parameters=open('/home/tcsgoa/Desktop/LiveParameters/LLparameters.txt','a+')
# parameters.write(timestr +'\tLL loading time mode: ' + str(LL_events.working_time.mode().mean())+'\n')
# parameters.close()


####If you want to save LL states/events to a file  ######

# if not os.path.exists('/mnt/UltraHD/streamingStates/LL'):

#     os.makedirs('/mnt/UltraHD/streamingStates/LL')

# directory='/mnt/UltraHD/streamingStates/LL'

# timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
# print("Saving States with file name -", timestr+"_LL.csv")
# LL_events.to_csv('/mnt/UltraHD/streamingStates/LL/'+ timestr+"_LL.csv")



### Pushing states, times and energy to Influx DB #####

from influxdb import InfluxDBClient
import json

IFhost="localhost"
IFport=8086
IFdbname = 'IIOT'

client = InfluxDBClient(host=IFhost, port=IFport,database=IFdbname)

events_batch=[]

# events_batch = json.loads(LL_events.to_json())

for i,row in LL_events.iterrows():
    events_batch.append({ 'measurement': 'EVENTS','tags':{'Machine':'LL'}, 'time':row.timestamp ,'fields': {'Loading event':int(row.event),'Loading Time':float(row.working_time)}})


client.write_points(events_batch,batch_size=len(LL_events))


# def get_events():
# 	events_batch.append({ 'measurement': 'EVENTS','tags':{'Machine':'LL'},'fields': {'Loading event':int(event),'working_time':float(working_time),'energy':float(energy),'sample':int(i)}})




# def send_events():
#     global client
#     while(1):
