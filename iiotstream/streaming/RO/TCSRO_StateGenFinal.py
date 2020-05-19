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

rffile=sys.argv[1]

if not os.path.isfile(rffile):

	print("File not found!")

	exit(1)

try:

	rf_raw=pd.read_csv(rffile, usecols =['time', 'c1', 'c2', 'c3'])

except:

	print("Invalid file!")



# rf_raw=pd.read_csv('RO_EM11.csv', usecols =['time', 'c1', 'c2', 'c3'])

rf_raw['time'] =  pd.to_datetime(rf_raw['time'])
rf_raw=rf_raw.rename(columns={'time':'timestamp'})
rf_raw['ist_time']=rf_raw['timestamp']+datetime.timedelta(hours=5, minutes=30)
rf_raw['total_current']=rf_raw['c1']+rf_raw['c2']+rf_raw['c3']

rolling_sum_window = 10
rolling_sum_std_window = 100
rf_raw['rolling_sum']=pd.Series.to_frame(rf_raw['total_current'].rolling(rolling_sum_window, center=True).sum())
rf_raw['rolling_sum_std']=pd.Series.to_frame(rf_raw['rolling_sum'].rolling(rolling_sum_std_window, center=True).std())

#instantiates state column giving all rows 0 value
rf_raw['state']=0

#converts raw/processed data to states 0,1,2 based on given thresholds
idle_state_thresh = 1
maintain_state_lower_thresh = 10
maintain_state_upper_thresh = 200
heating_state_thresh = 400 

rf_raw['state'][rf_raw['rolling_sum_std']<=idle_state_thresh]=0
rf_raw['state'][rf_raw['rolling_sum_std']>= heating_state_thresh]=2
rf_raw['state'][(rf_raw['rolling_sum_std']>maintain_state_lower_thresh) & (rf_raw['rolling_sum_std']<maintain_state_upper_thresh)]=1

rf_raw.ix[0, 'state']=(rf_raw.ix[0, 'state']+1)%3 # gives 1
rf_raw.ix[-1, 'state']=(rf_raw.ix[0, 'state']+1)%3 #gives 2

heating_height_thresh = 1.5
#find peaks is performed on rf_raw [state column] which allocated 0,1,2 based on thresholds on raw data
heating_times=scipy.signal.find_peaks(rf_raw.state, height=heating_height_thresh, width=1) #finds peaks using the state column (everything above 1.5) not the raw data 
heating_times_df=pd.DataFrame({"sample_number":heating_times[0], "working_time":heating_times[1]['widths']})

idle_height_thresh = -0.5
#creating temp dfs to detect states separately 
idle_temp=rf_raw[['state']]
idle_temp['state'][rf_raw.state!=0]=-1 #makes all the states that are not 0 -1 so idle states can be detected with anything above -0.5 as -1 is below -0.5
idle_times=scipy.signal.find_peaks(idle_temp.state, height=idle_height_thresh, width=1)
idle_times_df=pd.DataFrame({"sample_number":idle_times[0], "working_time":idle_times[1]['widths']})

maintain_height_thresh = 0.5
maintain_temp=rf_raw[['state']]
maintain_temp['state'][rf_raw.state==2]=0 #makes all the heating 2 states =0 in maintain_temp df so all the maintain 1 states can be detected with 0.5 height 
maintain_times=scipy.signal.find_peaks(maintain_temp.state, height=maintain_height_thresh, width=1)
maintain_times_df=pd.DataFrame({"sample_number":maintain_times[0], "working_time":maintain_times[1]['widths']})

#finding start, end and timestamps of each state (heating, maintain, idle)
for x, row in heating_times_df.iterrows():
    heating_times_df.ix[x,'start_time']=rf_raw.iloc[int(heating_times[1]['left_ips'][x])].timestamp
    heating_times_df.ix[x,'end_time']=rf_raw.iloc[int(heating_times[1]['right_ips'][x])].timestamp
    heating_times_df.ix[x,'timestamp']=rf_raw.iloc[int(heating_times[0][x])].timestamp
    heating_times_df.ix[x,'state']=rf_raw.iloc[int(heating_times[0][x])].state
    
for x, row in maintain_times_df.iterrows():
    maintain_times_df.ix[x,'start_time']=rf_raw.iloc[int(maintain_times[1]['left_ips'][x])].timestamp
    maintain_times_df.ix[x,'end_time']=rf_raw.iloc[int(maintain_times[1]['right_ips'][x])].timestamp
    maintain_times_df.ix[x,'timestamp']=rf_raw.iloc[int(maintain_times[0][x])].timestamp
    maintain_times_df.ix[x,'state']=rf_raw.iloc[int(maintain_times[0][x])].state
    
for x, row in idle_times_df.iterrows():
    idle_times_df.ix[x,'start_time']=rf_raw.iloc[int(idle_times[1]['left_ips'][x])].timestamp
    idle_times_df.ix[x,'end_time']=rf_raw.iloc[int(idle_times[1]['right_ips'][x])].timestamp
    idle_times_df.ix[x,'timestamp']=rf_raw.iloc[int(idle_times[0][x])].timestamp
    idle_times_df.ix[x,'state']=rf_raw.iloc[int(idle_times[0][x])].state

#finding energy for each occurence of each state by taking timestamps in raw df between start and end times calculated 
idle_times_df['energy'] = idle_times_df.apply(lambda x: rf_raw.loc[(rf_raw.timestamp <= x.end_time) & 
                                                            (x.start_time <= rf_raw.timestamp),
                                                            ['total_current']].sum()*230/3600000, axis=1)
maintain_times_df['energy'] = maintain_times_df.apply(lambda x: rf_raw.loc[(rf_raw.timestamp <= x.end_time) & 
                                                            (x.start_time <= rf_raw.timestamp),
                                                            ['total_current']].sum()*230/3600000, axis=1)
heating_times_df['energy'] = heating_times_df.apply(lambda x: rf_raw.loc[(rf_raw.timestamp <= x.end_time) & 
                                                            (x.start_time <= rf_raw.timestamp),
                                                            ['total_current']].sum()*230/3600000, axis=1)

print(idle_times_df)
print(maintain_times_df)
print(heating_times_df)

# RF_states=pd.DataFrame()
# RF_states=RF_states.append(idle_times_df[['timestamp','state', 'working_time', 'energy']])
# RF_states=RF_states.append(maintain_times_df[['timestamp','state', 'working_time', 'energy']])
# RF_states=RF_states.append(heating_times_df[['timestamp','state', 'working_time', 'energy']])

# RF_states['device']='reflowoven'
# RF_states.reset_index(inplace=True)
# RF_states.drop('index', axis=1, inplace=True)

#Pushing states, times and energy to Influx DB###

from influxdb import InfluxDBClient
import json

IFhost="localhost"
IFport=8086
IFdbname = 'IIOT'

client = InfluxDBClient(host=IFhost, port=IFport,database=IFdbname)

events_batch=[]

# events_batch = json.loads(LL_events.to_json())

for i,row in idle_times_df.iterrows():
    events_batch.append({ 'measurement': 'EVENTS','tags':{'Machine':'RO'}, 'time':row.timestamp ,'fields': {'Idle state':int(row.state),'Idle Time':float(row.working_time),"Idle Energy":float(row.energy)}})

    
for i,row in maintain_times_df.iterrows():
    events_batch.append({ 'measurement': 'EVENTS','tags':{'Machine':'RO'}, 'time':row.timestamp ,'fields': {'Maintain state':int(row.state),'Maintain Time':float(row.working_time),"Maintain Energy":float(row.energy)}})

    
for i,row in heating_times_df.iterrows():
    events_batch.append({ 'measurement': 'EVENTS','tags':{'Machine':'RO'}, 'time':row.timestamp ,'fields': {'Heating state':int(row.state),'Heating Time':float(row.working_time),"Heating Energy":float(row.energy)}})


client.write_points(events_batch,batch_size=len(idle_times_df))
client.write_points(events_batch,batch_size=len(maintain_times_df))
client.write_points(events_batch,batch_size=len(heating_times_df))


######If you want to save RO states/events to a file (Also need to uncomment RF_states portion above to create DF) ######

# if not os.path.exists('/mnt/UltraHD/streamingStates/RO'):

#     os.makedirs('/mnt/UltraHD/streamingStates/RO')


# # directory='/mnt/UltraHD/streamingStates/RF'


# timestr = time.strftime("%Y-%m-%d_%H-%M-%S")

# print("Saving States with file name - ", timestr+'_RO.csv')

# RF_states.to_csv('/mnt/UltraHD/streamingStates/RO/'+ timestr+"_RO.csv")