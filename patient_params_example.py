# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 10:20:10 2022

@author: barbourm
"""


import os
import glob
from pathlib import Path

from source.parameters import *
from patient_processing_main import process

# save_dir = os.getcwd()
parent_dir = Path.cwd()
patient_number = 'S114'
simulation_type = 'simplePM_coilWrappedNeck'



# Specify which processing routines you'd like to run
processing_boolean = {"AneurysmAvgVel": False,
                      'AneurysmWSS':    False,
		              'NeckWSS':        True,
		              'AneurysmEps':    False, 	
		              'NeckFlow':       True,
                      'SummarizeNeckMetrics': False
                      }

# Specify tecplot zone numbers
#!! Warning: zero based indexing (subtract 1 from what's listed in Tecplot)
zones = {'an_vol'  :[0],
         'pv_vol'  :[2],
         'an_surf' :[5],
         'pv_surf' :[7],
         'inlet'   :[10]
         }

# Specify data and case file locations
datafiles = sorted(glob.glob("simplePM_datafiles/*.dat.h5"))
Case = sorted(glob.glob("simplePM_datafiles/s114_coilWrappedNeck_simplePM-2.cas.h5"))

neckfile = glob.glob("neck.dat")

neck_surf_name = 'neck'
aneurysm_vol_name = 'aneu'
pv_vol_name = 'pv-2'


#----------------------------------------------------------------------
# Create dictionaries for passing to processing script - don't modify
surface_files = {'neck'     : neckfile,
                 }

zone_names = {'neck'    :  neck_surf_name,
              'aneurysm':  aneurysm_vol_name,
              'pv'      :  pv_vol_name
                 }

Pt = Parameters(datafiles, Case, patient_number, simulation_type, processing_boolean, zones, surface_files, zone_names, parent_dir)
process(Pt)