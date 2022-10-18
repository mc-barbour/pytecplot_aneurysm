# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 15:34:07 2022

@author: barbourm


"""

import os
import sys
import tecplot
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from source.tecplot_functions import *

def update_dataframe(filename, variable, time, variable_name):
    

    if filename.exists():
        
        df = pd.read_csv(filename)
        data = {"Time": [time],
            variable_name: [variable]}
        df_new = pd.DataFrame(data)
        df = df.append(df_new, ignore_index=True)
        df.to_csv(filename, index=False)
        print(df)

    else:
            
        data = {"Time": [time],
            variable_name: [variable]}
        df_new = pd.DataFrame(data)
        df_new.to_csv(filename, index=False)


def analyze_aneurysm_WSS(Pt):
    
    print("Nothing here yet")
    

def compute_neck_flow(Pt, count):
    
    surface_save_dir = Pt.post_process_dir / 'NeckQ'
    if not surface_save_dir.exists():
        surface_save_dir.mkdir()
    
    print("Calculating neck flow...")
    tecplot.data.load_tecplot(Pt.neckfile)
    frame = tecplot.active_frame()
    
    destintion = frame.dataset.zone(Pt.neck_zone_name)
    source = [frame.dataset.zone(Pt.aneurysm_zone_name),frame.dataset.zone(Pt.pv_zone_name)]
    variables_to_interp = [frame.dataset.variable(V)
                           for V in ('X Velocity','Y Velocity','Z Velocity')]

    tecplot.data.operate.interpolate_inverse_distance(destination_zone=destintion,source_zones=source,variables=variables_to_interp)
    
    #compute V dot N
    if not ('vdotN' in frame.dataset.variable_names):
        vdotN()

    variables_to_save = [frame.dataset.variable(V)
                         for V in ['X','Y','Z','X Velocity','Y Velocity','Z Velocity','Cell Volume','vdotN']]
    
    outfile = surface_save_dir / ("NeckQ_"+str(count).zfill(3)+".dat")
    
    zone_to_save = frame.dataset.zone(Pt.neck_zone_name)
    print(outfile)
    tecplot.data.save_tecplot_ascii(outfile, dataset=frame.dataset,
		variables=variables_to_save,
		zones=[zone_to_save])

def compute_viscous_dissipation(Pt, count):
    
    print('Computing viscous dissipation...')
    frame = tecplot.active_frame()
    if not ('s11'  in frame.dataset.variable_names):
        print('computing strain rate tensor...')
        strain_rate_tensor()
    else:
        print('viscous tensor already computed.')
        
    aneurysm_zone_id = frame.dataset.zone(Pt.aneurysm_zone_name).index
    variable_id = frame.dataset.variable("epsilon").index
    
    text_save_dir = Pt.post_process_dir / 'Viscous_Dissipation_textfiles'
    if not text_save_dir.exists():
        text_save_dir.mkdir()
    
    eps = integrate_scalar_singlezone(aneurysm_zone_id, variable_id, 'temp_dissipation' + str(count) + '.txt')
    solution_time = frame.dataset.solution_times[-1]
    eps_filename = Pt.post_process_dir / "Viscous_Dissipation.csv"
    print(solution_time, eps)
    
    # somethings broken - this is negative??
    update_dataframe(eps_filename, eps, solution_time, "Viscous Dissipation (W)")


def compute_neck_WSS(Pt, count):
    """
    Calculate WSS and interpolate onto the aneurysm neck. 
    Export neck surface at each timepoint into a seperate directory. 
    """
    
    frame = tecplot.active_frame()

    surface_save_dir = Pt.post_process_dir / 'NeckWSS'
    print("Starting Neck WSS routine...")
    
    if not surface_save_dir.exists():
        surface_save_dir.mkdir()
    
    if not ('s11'  in frame.dataset.variable_names):
        print('Computing strain rate tensor...')
        strain_rate_tensor()
    else:
        print('Viscous tensor already computed.')

    tecplot.data.load_tecplot(Pt.neckfile)

    neck_zone = frame.dataset.zone(Pt.neck_zone_name)
    source = [frame.dataset.zone(Pt.aneurysm_zone_name),frame.dataset.zone(Pt.pv_zone_name)]		
    variables_to_interp = [frame.dataset.variable(V)
                           for V in ('X Velocity','Y Velocity','Z Velocity','s11','s12','s13','s22','s23','s33')]
    print('interpotatling')
    tecplot.data.operate.interpolate_inverse_distance(destination_zone=neck_zone,source_zones=source,variables=variables_to_interp)

    # Execute neck shear metric
    neck_shear(zoneid = neck_zone.index)

    variables_to_save = [frame.dataset.variable(V)
                         for V in ('X','Y','Z','X Velocity','Y Velocity','Z Velocity','s11','s12','s13','s22','s23','s33','vdotN','Tx','Ty','Tz','Tw','WSSG')]
    
    outfile = surface_save_dir / ("NeckWSS_"+str(count).zfill(3)+".dat")
    zone_to_save = frame.dataset.zone(Pt.neck_zone_name)
    tecplot.data.save_tecplot_ascii(outfile, dataset=frame.dataset,
                                    variables=variables_to_save,
                                    zones=[zone_to_save])
            
    print ("Finished neck #" , count+1)

def perform_tecplot_analysis(Pt):
    
    
    for i in range(Pt.datafile_start_num, len(Pt.datafiles)):
        
        print('Analyzing data file: {:s}'.format(Pt.datafiles[i]))
        
        filetype = Pt.case[0].split('.')[-1]
        
        if filetype == 'cas':
            tecplot.data.load_fluent(case_filenames=Pt.case,data_filenames=Pt.datafiles[i],
                                     average_to_nodes='Arithmetic', append=False, all_poly_zones=True)
        elif filetype == 'h5':
            tecplot.data.load_fluent_cff(filenames=[Pt.case[0],Pt.datafiles[i]],
                                         read_data_option = tecplot.constant.ReadDataOption.Replace)
            
        frame = tecplot.active_frame()
        frame.plot_type = tecplot.constant.PlotType.Cartesian3D
        
        

        # delete everythin except aneurysm and pv next to aneurysm
        # zone_ids = list(np.arange(frame.dataset.num_zones))
        # zone_ids.remove(Pt.an_vol[0])
        # zone_ids.remove(Pt.pv_vol[0])
        # delete_zones = [frame.dataset.zone(a) for a in zone_ids]
        # frame.dataset.delete_zones(delete_zones) 


        if Pt.NeckFlow:
            compute_neck_flow(Pt, i)
            
        if Pt.AneurysmEps:
            compute_viscous_dissipation(Pt, i)
            
        if Pt.NeckWSS:
            compute_neck_WSS(Pt, i)
        

def summarize_neck_metrics(Pt, flowrate_delta_tol = 1):
    
    neckWSS_dir =  Pt.post_process_dir / 'NeckWSS'
    neckWSS_files = sorted(neckWSS_dir.glob("*.dat"))
    
    # Add exception handling
    tecplot.new_layout()    	
    tecplot.data.load_tecplot(neckWSS_files)
    frame = tecplot.active_frame()
    frame.plot_type = tecplot.constant.PlotType.Cartesian3D

    WSSid = frame.dataset.variable("Tw").index
    WSSGid = frame.dataset.variable("WSSG").index

    NeckPlaneWSS = Compute_Average(WSSid,"NeckWSS.txt")
    NeckPlaneWSSG = Compute_Average(WSSGid,"NeckWSSG.txt")
    
    print(NeckPlaneWSS)
    print(NeckPlaneWSSG)
    
    tecplot.new_layout()

    # Neck Flow
    surface_save_dir = Pt.post_process_dir / 'NeckQ'
    NeckPlaneFiles = sorted(surface_save_dir.glob("*.dat"))
    print(NeckPlaneFiles)
    
    tecplot.data.load_tecplot(NeckPlaneFiles)
    frame = tecplot.active_frame()
    frame.plot_type = tecplot.constant.PlotType.Cartesian3D

    Flow = FlowRate(frame)
    Flown = FlowRaten(frame)

    print (Flow)
    print (Flown)
    
    # if [a > flowrate_delta_tol for a in abs(Flow - Flown)]:
    #     raise ValueError("Flow rate in does not match flow rate out: check definitions")

    Narea = Area_Compute(0, "TotalNeckArea.txt")
    dArea = {'Aneurysm Flow Area (m2)': Narea}
    
    if NeckPlaneWSS.size == 1:
        print("Warning: only one scalar value / neck being processed")
        dSys = {"Sys. Neck WSS": NeckPlaneWSS,
                "Sys. Neck WSSG (Pa/m)": NeckPlaneWSSG,
                "Sys. Aneurysm Flow Rate (mL/min)": Flow,
    	}
        
    else:
        print("Finding max values of {:g}".format(NeckPlaneWSS.size))
        dSys = {"Sys. Neck WSS": max(NeckPlaneWSS),
                "Sys. Neck WSSG (Pa/m)": max(NeckPlaneWSSG),
                "Sys. Aneurysm Flow Rate (mL/min)": max(Flow),
                }   
    if Pt.TimeAverage:
        dTA = {"TA Neck WSS (Pa)": np.mean(NeckPlaneWSS),
               "TA Neck WSSG (Pa/m)": np.mean(NeckPlaneWSSG),
               "TA Aneurysm Flow Rate (mL/min)": np.mean(Flow),
    	}
    else:
        dTA = {"TA Neck WSS (Pa)": 0,
               "TA Neck WSSG (Pa/m)": 0,
               "TA Aneurysm Flow Rate (mL/min)":0,
    	}

    return dSys, dTA
            