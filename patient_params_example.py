# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 15:17:04 2022

@author: barbourm
"""

import os
import glob
from pathlib import Path

from source.parameters import *
from patient_processing_main import process

# save_dir = os.getcwd()
parent_dir = Path.cwd()
patient_number = 'S115'
simulation_type = 'simplePM_coilWrappedNeck'



# Specify which processing routines you'd like to run
processing_boolean = {"AneurysmAvgVel": False,
                      'AneurysmWSS':    False,
		              'NeckWSS':        True,
		              'AneurysmEps':    False, 	
		              'NeckFlow':       True,
                      'SummarizeNeckMetrics': True,
                      "TimeAverage":      False
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
datafiles = sorted(glob.glob("simplePM_datafiles/*.dat.h5"))[2:4]
Case = sorted(glob.glob("simplePM_datafiles/S115_coilWrapNeck_simplePM-4.cas.h5"))

neckfile = glob.glob("neck.dat")

neck_surf_name = 'neck'
aneurysm_vol_name = 'aneu'
pv_vol_name = 'pv2'


#----------------------------------------------------------------------
# Create dictionaries for passing to processing script - don't modify anything below here
surface_files = {'neck'     : neckfile,
                 }

zone_names = {'neck'    :  neck_surf_name,
              'aneurysm':  aneurysm_vol_name,
              'pv'      :  pv_vol_name
                 }

Pt = Parameters(datafiles, Case, patient_number, simulation_type, processing_boolean, zones, surface_files, zone_names, parent_dir)
process(Pt)