#!/bin/bash
set -e 
set -x
echo Running all experiments

files="data/nov26b/*aedat data/nov28/*aedat"

run="nice -n 10 aer_blink_detect --console"

# files=data/nov26b/h50_a0_c.aedat

$run --suffix i02p3d5 --log $files --interval 0.002  --npeaks 3 --min_led_distance 5 


# aer_blink_detect --log data/nov28/m8.aedat --suffix d0i5 --interval 0 --npeaks 3 --min_led_distance 5 -c "make"