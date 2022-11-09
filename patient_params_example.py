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
patient_number = 'S206'
simulation_type = 'simplePM_coilWrappedNeck'



# Specify which processing routines you'd like to run
processing_boolean = {"AneurysmAvgVel": False,
                      'AneurysmWSS':    False,
		              'NeckWSS':        True,
		              'AneurysmEps':    False, 	
		              'NeckFlow':       True,
                      'SummarizeNeckMetrics': True,
                      "SummarizeExcelMetrics": False,
                      "TimeAverage":      True
                     
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
Case = sorted(glob.glob("simplePM_datafiles/S206_simplePM_coilWrappedNeck-2.cas.h5"))
neckfile = glob.glob("neck.dat")


process_start_number = 1 # typically 0 unless restarting

neck_surf_name = 'interface-neck-2'
aneurysm_vol_name = 'aneu'
pv_vol_name = 'pv2'
aneurysm_surf_name = 'aneu-2'


#----------------------------------------------------------------------
# Create dictionaries for passing to processing script - don't modify anything below here
surface_files = {'neck'     : neckfile,
                 }

zone_names = {'neck'    :  neck_surf_name,
              'aneurysm':  aneurysm_vol_name,
              'pv'      :  pv_vol_name,
              'aneurysm-wall': aneurysm_surf_name
                 }

Pt = Parameters(datafiles, Case, patient_number, simulation_type, processing_boolean, zones, surface_files, zone_names, parent_dir, process_start_number)
process(Pt)