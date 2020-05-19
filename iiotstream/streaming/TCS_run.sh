#!/bin/bash

batch_size=15

while [ 1 ]
do
	start=`date +%s`
        end=`date  +%s`
        duration=0

	cd /home/tcsgoa/Desktop/iiotstream/tools
	sh getdatatcsFinal.sh

	mkdir -p "/mnt/UltraHD/RAW/`date '+%Y-%m-%dT%H-%M-%S'`"
	cd /mnt/UltraHD/RAW/
	foldername=$(ls -t | head -n1)
	cd /home/tcsgoa/Desktop/iiotstream/tools/data

	cp *.csv "/mnt/UltraHD/RAW/$foldername/"
	cp PP2_prox.csv "/home/tcsgoa/Desktop/iiotstream/streaming/PP1"
	cp PP1_EM.csv "/home/tcsgoa/Desktop/iiotstream/streaming/PP1"
	cp PP2_prox.csv "/home/tcsgoa/Desktop/iiotstream/streaming/PP2"
	cp PP2_EM.csv "/home/tcsgoa/Desktop/iiotstream/streaming/PP2"
	cp PP3_prox.csv "/home/tcsgoa/Desktop/iiotstream/streaming/PP3"
	cp PP3_EM.csv "/home/tcsgoa/Desktop/iiotstream/streaming/PP3"

	cd /home/tcsgoa/Desktop/iiotstream/streaming/LL
	python TCSLL_StateGenFinal.py /mnt/UltraHD/RAW/$foldername/LL_IMU.csv

	cd /home/tcsgoa/Desktop/iiotstream/streaming/SP
	python TCSSP_StateGenFinal.py /mnt/UltraHD/RAW/$foldername/SP_EM.csv

	cd /home/tcsgoa/Desktop/iiotstream/streaming/PP1
	python TCSPP1_StateGenFinal.py /mnt/UltraHD/RAW/$foldername/PP1_IMU.csv

	cd /home/tcsgoa/Desktop/iiotstream/streaming/PP2
	python TCSPP2_StateGenFinal.py /mnt/UltraHD/RAW/$foldername/PP2_IMU.csv

	cd /home/tcsgoa/Desktop/iiotstream/streaming/PP3
	python TCSPP3_StateGenFinal.py /mnt/UltraHD/RAW/$foldername/PP3_IMU.csv

	cd /home/tcsgoa/Desktop/iiotstream/streaming/RO
	python TCSRO_StateGenFinal.py /mnt/UltraHD/RAW/$foldername/RO_EM.csv

	cd /home/tcsgoa/Desktop/iiotstream/streaming/LUL
	python TCSLUL_StateGenFinal.py /mnt/UltraHD/RAW/$foldername/LUL_IMU.csv


	cd /home/tcsgoa/Desktop/iiotstream/streaming/PP1
	rm *.csv

	cd /home/tcsgoa/Desktop/iiotstream/streaming/PP2
	rm *.csv

	cd /home/tcsgoa/Desktop/iiotstream/streaming/PP3
	rm *.csv

	cd /home/tcsgoa/Desktop/iiotstream/tools/data
	rm *

	while [ $duration -lt $((batch_size*60)) ]
        do
            end=`date  +%s`
            duration=$((end-start))
        done

done
