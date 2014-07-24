#!/bin/bash

audio_bandwidth="96000" 
video_bandwidth1="2500000"
video_bandwidth2="4000000"

for i in `seq 23821645 23821738`
do
    wget -P 'Vbandwidth1' "http://dash.edgesuite.net/dash264/TestCases/1b/thomson-networks/1/video_${i}_${video_bandwidth1}bps.mp4"
    wget -P 'Vbandwidth2' "http://dash.edgesuite.net/dash264/TestCases/1b/thomson-networks/1/video_${i}_${video_bandwidth2}bps.mp4"
    wget -P 'Abandwidth1' "http://dash.edgesuite.net/dash264/TestCases/1b/thomson-networks/1/audio_${i}_${audio_bandwidth}bps_Input_2.mp4"
done
