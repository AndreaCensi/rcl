#!/bin/bash
set -e 
set -x
echo Running all experiments

# Create videos

# aer_video --log data/dec6/*aedat --interval 0.03 0.005 0.001 


# files="data/nov26b/*aedat data/nov28/*aedat"
files="data/dec6/*aedat"

run="nice -n 10 aer_blink_detect --contracts --console"

# files=data/nov26b/h50_a0_c.aedat

# $run --suffix i02p3d5 --log $files --interval 0.002  --npeaks 3 --min_led_distance 5 

$run --suffix i02p3d15 --log $files --interval 0.002  --npeaks 3 --min_led_distance 15 


# aer_blink_detect --log data/nov28/m8.aedat --suffix d0i5 --interval 0 --npeaks 3 --min_led_distance 5 -c "make"