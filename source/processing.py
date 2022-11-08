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



def analyze_aneurysm_vel(Pt,count):
    
    print("Calculating average velocity of aneurysm volume...")
    frame = tecplot.active_frame()
    
    #compute Velocity Magnitude
    if not ('VelMag' in frame.dataset.variable_names):
        velmag()
    

    aneurysm_zone_id = frame.dataset.zone(Pt.aneurysm_zone_name).index
    variable_id = frame.dataset.variable("VelMag").index
    
    text_save_dir = Pt.post_process_dir / 'Velocity_Magnitude_textfiles'
    if not text_save_dir.exists():
        text_save_dir.mkdir()
        
    tecplot_save_name = str(text_save_dir / ('vel_mag' + str(count) + '.txt'))
   
    if os.name == 'nt':
        tecplot_save_name = tecplot_save_name.replace('\\','/')
    
    velm = compute_average_singlezone(aneurysm_zone_id, variable_id, tecplot_save_name)
    solution_time = frame.dataset.solution_times[-1]
    velm_filename = Pt.post_process_dir / "Velocity_Magnitude.csv"
    print(solution_time, velm)
    

    update_dataframe(velm_filename, velm, solution_time, "Velocity Magnitude (m/s)")

def analyze_aneurysm_WSS(Pt,count):
    
    print("Calculating aneurysm dome WSS...")
    frame = tecplot.active_frame()
    
    #compute Velocity Magnitude
    if not ('WSS (Pa)' in frame.dataset.variable_names):
        filetype = Pt.case[0].split('.')[-1]
    
        if filetype == 'cas':
            domeWSS_old()
        elif filetype == 'h5':
            domeWSS_h5()

    aneurysm_zone_id = frame.dataset.zone(Pt.aneurysm_surf_name).index
    variable_id = frame.dataset.variable("WSS (Pa)").index
    variable_idG = frame.dataset.variable("WSSG (Pa/m)").index
    
    text_save_dir = Pt.post_process_dir / 'Dome_WSS_WSSG_textfiles'
    if not text_save_dir.exists():
        text_save_dir.mkdir()

            
    wss_save_name = str(text_save_dir / ('wss' + str(count) + '.txt'))
    wssg_save_name = str(text_save_dir / ('wssg' + str(count) + '.txt'))

    if os.name == 'nt':
        wss_save_name = wss_save_name.replace('\\','/')
        wssg_save_name = wssg_save_name.replace('\\','/')

    
    wss = compute_average_singlezone(aneurysm_zone_id, variable_id, wss_save_name)
    wssg = compute_average_singlezone(aneurysm_zone_id, variable_idG, wssg_save_name)
    solution_time = frame.dataset.solution_times[-1]
    wss_filename = Pt.post_process_dir / "WSS.csv"
    wssg_filename = Pt.post_process_dir / "WSSG.csv"
    print(solution_time, wss, wssg)
    
    update_dataframe(wss_filename, wss, solution_time, "Dome WSS (Pa)")
    update_dataframe(wssg_filename, wssg, solution_time, "Dome WSSG (Pa/m)")


def compute_neck_flow(Pt, count):
    
    surface_save_dir = Pt.post_process_dir / 'NeckQ'
    if not surface_save_dir.exists():
        surface_save_dir.mkdir()
    
    print("Calculating neck flow...")
    tecplot.data.load_tecplot(Pt.neckfile)
    frame = tecplot.active_frame()
    
    destintion = frame.dataset.zone(Pt.neck_zone_name)
    if Pt.aneurysm_zone_name == "SingleZone":
        print("Using single zone for interpolation onto neck")
        source = [frame.dataset.zone(Pt.pv_zone_name)]
    else:
        source = [frame.dataset.zone(Pt.aneurysm_zone_name), frame.dataset.zone(Pt.pv_zone_name)]
        print("Using 2 zones for interpolation onto neck")

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

    tecplot_save_name = str(text_save_dir / ('dissipation' + str(count) + '.txt'))
   
    if os.name == 'nt':
        tecplot_save_name = tecplot_save_name.replace('\\','/')
    
    eps = integrate_scalar_singlezone(aneurysm_zone_id, variable_id, tecplot_save_name)
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
    
    if Pt.aneurysm_zone_name == "SingleZone":
        source = [frame.dataset.zone(Pt.pv_zone_name)]
        print('Single Zone')
    else:
        print('2-zones')
        source = [frame.dataset.zone(Pt.aneurysm_zone_name), frame.dataset.zone(Pt.pv_zone_name)]
    
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
        

        if Pt.AneurysmAvgVel:
            analyze_aneurysm_vel(Pt,i)
            
        if Pt.AneurysmWSS:
            analyze_aneurysm_WSS(Pt,i)

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

def summarize_excel_metrics(Pt):
    
    filenames = ["Viscous_Dissipation.csv", "Velocity_Magnitude.csv", "WSS.csv", "WSSG.csv"]
    variables = ["Viscous Dissipation (W)", "Velocity Magnitude (m/s)", "Dome WSS (Pa)", "Dome WSSG (Pa/m)"]
    dfs = []
    dSys = {}
    dTA = {}
    
    for file in filenames:
        dfs.append(pd.read_csv(Pt.post_process_dir / file))
    
    for count, df in enumerate(dfs):
        if len(df["Time"].unique()) < len(df):
            print("Warning! multiple rows with the same timestep in ", filenames[count])
        
        if len(df["Time"]) == 1:
            dSys["Sys. " + variables[count]] = float(df[variables[count]])
            print("Warning! only setting one variable to max")
        else:
            dSys["Sys. " + variables[count]] = max(df[variables[count]])
            
        if Pt.TimeAverage:
            dTA["TA "+ variables[count]] = np.mean(df[variables[count]])
    
    print(dSys, dTA)
    return dSys, dTA
    
    
    df_eps = pd.read_csv(Pt.post_process_dir / "Viscous_Dissipation.csv")
    df_aneurysm_vel = pd.read_csv(Pt.post_process_dir / "Velocity_Magnistude.csv")
    df_aneurysm_wss = pd.read_csv(Pt.post_process_dir / "WSS.csv")
    df_aneurysm_wssg = pd.read_csv(Pt.post_process_dir / "WSSG.csv")

    
    
    
    
            