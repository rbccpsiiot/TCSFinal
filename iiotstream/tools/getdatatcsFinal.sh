#!/bin/bash

#start_time=$(date +"%s") #current time in epoch 
#echo "Current time : $start_time"

for machine in LL SP PP1 PP2 PP3 LUL
do
	curl -G 'http://192.168.8.100:8086/query?db=IIOT&precision=rfc3339' --data-urlencode "q=SELECT * FROM IMU WHERE Machine = '${machine}' AND time > now() - 15m  AND time <= now()" | jq -r "(.results[0].series[0].columns), (.results[0].series[0].values[]) | @csv" >> /home/tcsgoa/Desktop/iiotstream/tools/data/${machine}"_IMU.csv"
done

for machine in SP PP1 PP2 PP3 RO
do
	curl -G 'http://192.168.8.100:8086/query?db=IIOT&precision=rfc3339' --data-urlencode "q=SELECT * FROM EM WHERE Machine = '${machine}' AND time > now() - 15m AND time <= now()" | jq -r "(.results[0].series[0].columns), (.results[0].series[0].values[]) | @csv" >> /home/tcsgoa/Desktop/iiotstream/tools/data/${machine}"_EM.csv"
done

curl -G 'http://192.168.8.100:8086/query?db=IIOT&precision=rfc3339' --data-urlencode "q=SELECT SPExit FROM PS WHERE time > now() - 15m AND time <= now()" | jq -r "(.results[0].series[0].columns), (.results[0].series[0].values[]) | @csv" >> /home/tcsgoa/Desktop/iiotstream/tools/data/"SP_prox.csv"
curl -G 'http://192.168.8.100:8086/query?db=IIOT&precision=rfc3339' --data-urlencode "q=SELECT PP1Entry FROM PS WHERE time > now() - 15m AND time <= now()" | jq -r "(.results[0].series[0].columns), (.results[0].series[0].values[]) | @csv" >> /home/tcsgoa/Desktop/iiotstream/tools/data/"PP1_prox.csv"
curl -G 'http://192.168.8.100:8086/query?db=IIOT&precision=rfc3339' --data-urlencode "q=SELECT PP2Entry FROM PS WHERE time > now() - 15m AND time <= now()" | jq -r "(.results[0].series[0].columns), (.results[0].series[0].values[]) | @csv" >> /home/tcsgoa/Desktop/iiotstream/tools/data/"PP2_prox.csv"
curl -G 'http://192.168.8.100:8086/query?db=IIOT&precision=rfc3339' --data-urlencode "q=SELECT PP3Entry FROM PS WHERE time > now()- 15m AND time <= now()" | jq -r "(.results[0].series[0].columns), (.results[0].series[0].values[]) | @csv" >> /home/tcsgoa/Desktop/iiotstream/tools/data/"PP3_prox.csv"
curl -G 'http://192.168.8.100:8086/query?db=IIOT&precision=rfc3339' --data-urlencode "q=SELECT ROExit1 FROM PS WHERE time > now() - 15m AND time <= now()" | jq -r "(.results[0].series[0].columns), (.results[0].series[0].values[]) | @csv" >> /home/tcsgoa/Desktop/iiotstream/tools/data/"RO_prox.csv"
