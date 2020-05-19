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

lulfile=sys.argv[1]

if not os.path.isfile(lulfile):

        print("File not found!")
# ldfile=sys.argv[1]
# ldfile = pd.read_csv('LL_IMU4.csv')

# raw_lul=pd.read_csv('LUL_IMU11.csv', usecols=['time', 'ax', 'az'])

try:
        
         raw_lul=pd.read_csv(lulfile, usecols=['time', 'ax', 'az'])

except:

        print("Invalid file!")
        exit(2)


raw_lul['time'] =  pd.to_datetime(raw_lul['time'])
raw_lul=raw_lul.rename(columns={'time':'timestamp'})
raw_lul['ist_time']=raw_lul['timestamp']+datetime.timedelta(hours=5, minutes=30)

raw_lul["acc"] = ( raw_lul["ax"]**2 + raw_lul["az"]**2 ) ** 0.5

acc=raw_lul[["timestamp", "acc"]]
acc.set_index('timestamp')
test_lul=acc

rolling_window = 100
test_lul['rlg_acc']=pd.Series.to_frame(test_lul['acc'].rolling(rolling_window, center=True).std())

time_thresh=10
height_thresh = 0.02
sampling_rate = 100

board=scipy.signal.find_peaks(test_lul.rlg_acc, height=(height_thresh), distance=time_thresh*sampling_rate, width=1)

differ=np.diff(board[0])
differ=differ.tolist()

unloading_delays_rawdf=pd.DataFrame({"sample_number":board[0], "working_time":board[1]['widths']/sampling_rate})
LUL_events=pd.DataFrame({"timestamp":test_lul.iloc[unloading_delays_rawdf.sample_number].timestamp, "event":1, "working_time":(unloading_delays_rawdf.working_time).tolist()})

LUL_events['energy']=float('0')
LUL_events['device']='unloader'

print(LUL_events)


######Get Parameters required for Simpy Parameter file ###### 

# timestr = time.strftime("%H-%M")
# print('LUL unloading time mode: ', LUL_events.working_time.mode().mean())
# parameters=open('/home/tcsgoa/Desktop/LiveParameters/LULparameters.txt','a+')
# parameters.write(timestr +'\tLUL loading time mode: ' + str(LUL_events.working_time.mode().mean())+'\n')
# parameters.close()


####If you want to save LUL states/events to a file ######

# if not os.path.exists('/mnt/UltraHD/streamingStates/LUL'):

#     os.makedirs('/mnt/UltraHD/streamingStates/LUL')

# directory='/mnt/UltraHD/streamingStates/LUL'

# timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
# print("Saving States with file name -", timestr+"_LUL.csv")
# LUL_events.to_csv('/mnt/UltraHD/streamingStates/LUL/'+ timestr+"_LUL.csv")

# print("Saving States with file name -","LUL.csv")
# LUL_events.to_csv('/Desktop/TCS/iiotstream2/streaming2/LUL/'"test_LUL.csv")

# LUL_events.to_csv('/mnt/UltraHD/streamingStates/LUL/'"LUL.csv")


#### Pushing states, times and energy to Influx DB ###

from influxdb import InfluxDBClient
import json

IFhost="localhost"
IFport=8086
IFdbname = 'IIOT'

client = InfluxDBClient(host=IFhost, port=IFport,database=IFdbname)

events_batch=[]

# events_batch = json.loads(LL_events.to_json())

for i,row in LUL_events.iterrows():
    events_batch.append({ 'measurement': 'EVENTS','tags':{'Machine':'LUL'}, 'time':row.timestamp ,'fields': {'Unloading event':int(row.event),'Unloading Time':float(row.working_time)}})


client.write_points(events_batch,batch_size=len(LUL_events))