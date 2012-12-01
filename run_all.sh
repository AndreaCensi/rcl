#!/bin/bash
set -e 
set -x
echo Running all experiments

files="data/nov26b/*aedat data/nov28/*aedat"

run="nice -n 10 aer_blink_detect --console"

$run --suffix abd02 --log $files --interval 0.002  
#$run --suffix abd05 --log $files --interval 0.005 


