#!/bin/bash
set -e
set -x 
f=data/noise_led-100k.aer.txt,data/noise_led-10k.aer.txt
aer_stats_freq_phase  --log $f 
aer_stats_freq        --log $f 
aer_blink_detect      --log $f --video


#pg -m procgraph_aer aer_events_show --filename data/andrea.aedata --interval 0.03 --out data/andrea-30fps.mp4