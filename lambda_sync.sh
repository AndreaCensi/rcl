#!/bin/bash
set -e
set -x
here=andrea@lambda:/home/andrea/scm/bentobox-boot11env/src/rcl/data/
there=~/Dropbox/work/12-aer-tracking-data/
# rsync $here/nov26b/\*mp4 $there/nov26b/
rsync -av --progress $here/nov28/\*mp4 $there/nov28-tracks/