# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 13:59:37 2022

@author: barbourm
"""
import os
import glob
from source.parameters import *

save_dir = os.getcwd()
patient_id = 'test'

# Specify which processing routines you'd like to run
processing_boolean = {"AneurysmAvgVel": True,
                      'AneurysmWSS':    True,
		              'NeckWSS':       False,
		              'AneurysmEps':    True, 	
		              'NeckFlow':       True,
		              'InletFlowrate': False
                      }

# Specify tecplot zone numbers
zones = {'an_vol'  :[1],
         'pv_vol'  :[3],
         'an_surf' :[6],
         'pv_surf' :[8],
         'inlet'   :[11]
         }

# Specify data and case file locations
Datafiles = sorted(glob.glob("simplePM_datfiles/*.dat.h5"))
Case = sorted(glob.glob("s209_coilWrappedNeck_simplePM-4.cas.h5"))

neckfile = glob.glob("neck.dat")
neck_surf = 'stent_dist'

velfile = glob.glob('../ostium_distal.dat')
vel_surf = 'ostium'

aneurysmfile = glob.glob("../aneu_distal.dat")
aneurysm_surf = 'aneuo'

aneurysmvolfile = glob.glob("../ostium_only_distal.dat")
aneurysm_vol = 'ostium_only_distal'

surface_files = {'neck'     : neckfile,
                 'aneursym' : aneurysmfile,
                 'velocity' : velfile
                 }

surface_names = {'neck_name': neck_surf,
                 'velocity_name': vel_surf,
                 'aneurysm_name': aneurysm_surf}


Pt = Parameters(Datafiles, Case, patient_id, processing_boolean, zones, surface_files, surface_names, save_dir)