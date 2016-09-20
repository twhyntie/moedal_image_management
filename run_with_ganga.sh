#!/bin/bash
#
# CVMFS for Python
export PYTHONPATH=/cvmfs/cernatschool.egi.eu/lib/python2.6/site-packages/:/cvmfs/cernatschool.egi.eu/lib64/python2.6/site-packages/
#
# Run the splitting code.
python split_raw.py --subject-width=200 --subject-height=100 ./.
#
tar -cvf images.tar MoEDAL-IMG-001_*.png
