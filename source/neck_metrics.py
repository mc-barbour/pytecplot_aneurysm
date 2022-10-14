# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 14:55:49 2022

@author: barbourm
"""

import os
import sys
import tecplot
import glob
import numpy as np
import matplotlib.pyplot as plt

from source.tecplot_functions import *




def FlowRate(frame):
    """
    Compute the flowrate across the neck surface where VdotN is positive
    """
	
    BlankVar = frame.dataset.variable('vdotN').index
	
    tecplot.macro.execute_command(r'''
		$!BLANKING
		VALUE
		{
	 		INCLUDE = YES
	 		CONSTRAINT 1
	 		{
	 			INCLUDE = YES
				VARA ='''+str(BlankVar+1)+r'''
				RELOP = GREATERTHAN
				VALUECUTOFF = 0.0
			}
	}
	''')
    return abs(Integrate_Scalar(BlankVar,'FlowRateNeck.txt')*60e6)

def FlowRaten(frame):
    """
    Compute the flowrate across the neck surface where VdotN is negative
    """
	
    BlankVar = frame.dataset.variable('vdotN').index

    tecplot.macro.execute_command(r'''
		$!BLANKING
		VALUE
		{
	 		INCLUDE = YES
	 		CONSTRAINT 1
	 		{
	 			INCLUDE = YES
				VARA ='''+str(BlankVar+1)+r'''
				RELOP = LESSTHAN
				VALUECUTOFF = 0.0
			}
		}
	''')
    return abs(Integrate_Scalar(BlankVar,'FlowRateNeckN.txt')*60e6)


def FlowArea(frame):
	
	BlankVar = frame.dataset.variable('vdotN').index
	
	tecplot.macro.execute_command(r'''
		$!BLANKING
		VALUE
		{
	 		INCLUDE = YES
	 		CONSTRAINT 1
	 		{
	 			INCLUDE = YES
				VARA ='''+str(BlankVar+1)+r'''
				RELOP = LESSTHAN
				VALUECUTOFF = 0.0
			}
		}
	''')
	return abs(Integrate_Area(BlankVar,'posArea.txt'))

def FlowArean(frame):
	
	BlankVar = frame.dataset.variable('vdotN').index
	
	tecplot.macro.execute_command(r'''
		$!BLANKING
		VALUE
		{
	 		INCLUDE = YES
	 		CONSTRAINT 1
	 		{
	 			INCLUDE = YES
				VARA ='''+str(BlankVar+1)+r'''
				RELOP = GREATERTHAN
				VALUECUTOFF = 0.0
			}
		}
	''')
	return abs(Integrate_Area(BlankVar,'negArea.txt'))



def FlowAvg(frame):
	
	BlankVar = frame.dataset.variable('vdotN').index
	
	tecplot.macro.execute_command(r'''
		$!BLANKING
		VALUE
		{
	 		INCLUDE = YES
	 		CONSTRAINT 1
	 		{
	 			INCLUDE = YES
				VARA ='''+str(BlankVar+1)+r'''
				RELOP = LESSTHAN
				VALUECUTOFF = 0.0
			}
		}
	''')
	return abs(Integrate_Average(BlankVar,'FlowAvg.txt')*60e6)

def FlowAvgn(frame):
	
	BlankVar = frame.dataset.variable('vdotN').index
	
	tecplot.macro.execute_command(r'''
		$!BLANKING
		VALUE
		{
	 		INCLUDE = YES
	 		CONSTRAINT 1
	 		{
	 			INCLUDE = YES
				VARA ='''+str(BlankVar+1)+r'''
				RELOP = GREATERTHAN
				VALUECUTOFF = 0.0
			}
		}
	''')
	return abs(Integrate_Avg(BlankVar,'FlowAvgN.txt')*60e6)



def NeckFlowInterpolate(Pt):
    """
    Interpolate velocity field onto neck surface. 
    Export neck surface at each timepoint into a seperate directory
    """
	

    surface_save_dir = Pt.parent_dir / 'NeckQ'
    if not surface_save_dir.exists():
        surface_save_dir.mkdir()
        

    for i in range(len(Pt.datafiles)):
        
        print('Analyzing data file: {:s}'.format(Pt.datafiles[i]))
        filetype = Pt.case[0].split('.')[-1]
        
        if filetype == 'cas':
            tecplot.data.load_fluent(case_filenames=Pt.case,data_filenames=Pt.datafiles[i],
                                     average_to_nodes='Arithmetic', append=False, all_poly_zones=True)
        elif filetype == 'h5':
            tecplot.data.load_fluent_cff(filenames=[Pt.case[0],Pt.datafiles[i]],
                                         read_data_option = tecplot.constant.ReadDataOption.Replace)

        
        tecplot.data.load_tecplot(Pt.neckfile)
        frame = tecplot.active_frame()

        destintion = frame.dataset.zone(Pt.neck_zone_name)
        source = [frame.dataset.zone(Pt.an_vol[0]),frame.dataset.zone(Pt.pv_vol[0])]
        variables_to_interp = [frame.dataset.variable(V)
				     for V in ('X Velocity','Y Velocity','Z Velocity')]

        tecplot.data.operate.interpolate_inverse_distance(destination_zone=destintion,source_zones=source,variables=variables_to_interp)
		
		#tecplot.data.dataset.delete_zone(0)

        tecplot.macro.execute_command(r'''
			$!EXTENDEDCOMMAND 
	  		  COMMANDPROCESSORID = 'CFDAnalyzer4'
	  		  COMMAND = 'Calculate Function=\'GRIDKUNITNORMAL\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'T\''
			$!EXTENDEDCOMMAND 
	  		  COMMANDPROCESSORID = 'CFDAnalyzer4'
	  		  Command = 'Calculate Function=\'CELLVOLUME\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'F\''
			$!ALTERDATA 
				EQUATION = '{vdotN} = {X Velocity}*{X Grid K Unit Normal} + {Y Velocity}*{Y Grid K Unit Normal} + {Z Velocity}*{Z Grid K Unit Normal}'
			''')

        frame = tecplot.active_frame()

        variables_to_save = [frame.dataset.variable(V)
				     for V in ['X','Y','Z','X Velocity','Y Velocity','Z Velocity','Cell Volume','vdotN']]
        outfile = surface_save_dir / ("NeckQ_"+str(i).zfill(3)+".dat")
        zone_to_save = frame.dataset.zone(Pt.neck_zone_name)
        print(outfile)
        tecplot.data.save_tecplot_ascii(outfile, dataset=frame.dataset,
						variables=variables_to_save,
						zones=[zone_to_save])



def NeckFlowMetrics(Pt, flowrate_delta_tol = 1e-5):
    """
    Load neck surfaces with interporated velocity field and perform integration / averaging for metrics
    """

    tecplot.new_layout()

    surface_save_dir = Pt.parent_dir / 'NeckQ'
    NeckPlaneFiles = sorted(surface_save_dir.glob("*.dat"))
    print(NeckPlaneFiles)
	#NeckPlaneFiles = sorted(glob.glob("NeckSurface/*"))
    
    tecplot.data.load_tecplot(NeckPlaneFiles)
    frame = tecplot.active_frame()
    frame.plot_type = tecplot.constant.PlotType.Cartesian3D

    # Area = FlowArea(frame)
    # Arean = FlowArean(frame)

    Flow = FlowRate(frame)
    Flown = FlowRaten(frame)

    print (Flow)
    print (Flown)
    
    if [a > flowrate_delta_tol for a in (Flow - Flown)]:
         ValueError("Flow rate in does not match flow rate out: check definitions")

    Narea = Area_Compute(1, "TotalNeckArea.txt")
    dArea = {'Aneurysm Flow Area (m2)': Narea}

#     tecplot.new_layout()
#     InletFiles = sorted(glob.glob("Inflow/*"))
#     tecplot.data.load_tecplot(InletFiles)
#     frame = tecplot.active_frame()
#     frame.plot_type = PlotType.Cartesian3D
# 	
#     InFlow = InFlowRate(frame)

# 	# Ratio of aneu/pv inflow over ratio of inflow/ostium area 

#     ICI = (Flow*Narea)/(Area*InFlow)
#     Normflow = Flow/InFlow

    Normflow = 0.0
    ICI = 0.0

    dSys = {"Sys. Normalized Aneurysm Flow Rate": np.NAN,
	"Sys. Aneurysm Flow Rate (mL/min)": max(Flow),
	"Sys. Aneurysm Inflow concentration index": np.NAN
	}

    dTA = {"TA Normalized Aneurysm Flow Rate": np.NAN,
	"TA Aneurysm Flow Rate (mL/min)": np.mean(Flow),
	"TA Aneurysm Inflow concentration index": np.NAN
	}

    return dSys, dTA, dArea


def NeckWSSCompute(Pt):
    """
    Calculate WSS and interpolate onto the aneurysm neck. 
    Export neck surface at each timepoint into a seperate directory. 
    """
    
    surface_save_dir = Pt.parent_dir / 'NeckWSS'
    if not surface_save_dir.exists():
        surface_save_dir.mkdir()
    
		
    vdotnMax = np.array([])

    for i in range(len(Pt.datafiles)):
        
        print('Analyzing data file: {:s}'.format(Pt.datafiles[i]))
        filetype = Pt.case[0].split('.')[-1]
        
        if filetype == 'cas':
            tecplot.data.load_fluent(case_filenames=Pt.case,data_filenames=Pt.datafiles[i],
                                     average_to_nodes='Arithmetic', append=False, all_poly_zones=True)
        elif filetype == 'h5':
            tecplot.data.load_fluent_cff(filenames=[Pt.case[0],Pt.datafiles[i]],
                                         read_data_option = tecplot.constant.ReadDataOption.Replace)

        frame = tecplot.active_frame()
		
        tecplot.macro.execute_command(r'''
			$!EXTENDEDCOMMAND 
  				COMMANDPROCESSORID = 'CFDAnalyzer4'
  				COMMAND = 'Calculate Function=\'VELOCITYGRADIENT\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'T\''


			$!ALTERDATA EQUATION = '{s11} = {dUdX}'
			$!ALTERDATA EQUATION = '{s12} = 0.5*({dUdY}+{dVdX})'
			$!ALTERDATA EQUATION = '{s13} = 0.5*({dUdZ}+{dWdX})'
			$!ALTERDATA EQUATION = '{s22} = {dVdY}'
			$!ALTERDATA EQUATION = '{s23} = 0.5*({dVdZ}+{dWdY})'
			$!ALTERDATA EQUATION = '{s33} = {dWdZ}'
			''')

        tecplot.data.load_tecplot(Pt.neckfile)

        destintion = frame.dataset.zone(Pt.neck_zone_name)
        source = [frame.dataset.zone(Pt.an_vol[0]),frame.dataset.zone(Pt.pv_vol[0])]		
        variables_to_interp = [frame.dataset.variable(V)
				     for V in ('X Velocity','Y Velocity','Z Velocity','s11','s12','s13','s22','s23','s33')]
		
        tecplot.data.operate.interpolate_inverse_distance(destination_zone=destintion,source_zones=source,variables=variables_to_interp)

		#delete_zones(0,1)
        tecplot.macro.execute_command(r'''
			$!DELETEZONES [1,2]

			$!EXTENDEDCOMMAND 
	  		  COMMANDPROCESSORID = 'CFDAnalyzer4'
	  		  COMMAND = 'Calculate Function=\'GRIDKUNITNORMAL\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'T\''

	  		$!ALTERDATA 
				EQUATION = '{vdotN} = {X Velocity}*{X Grid K Unit Normal} + {Y Velocity}*{Y Grid K Unit Normal} + {Z Velocity}*{Z Grid K Unit Normal}'
			
			$!ALTERDATA
			    EQUATION = '{Sx} = ({s11}*{X Grid K Unit Normal} + {s12}*{Y Grid K Unit Normal} + {s13}*{Z Grid K Unit Normal})'

			$!ALTERDATA
			    EQUATION = '{Sy} = ({s12}*{X Grid K Unit Normal} + {s22}*{Y Grid K Unit Normal} + {s23}*{Z Grid K Unit Normal})'

			$!ALTERDATA
			    EQUATION = '{Sz} = ({s13}*{X Grid K Unit Normal} + {s23}*{Y Grid K Unit Normal} + {s33}*{Z Grid K Unit Normal})'


			$!ALTERDATA
			    EQUATION = '{Sigma} = ({Sx}*{X Grid K Unit Normal} + {Sy}*{Y Grid K Unit Normal} + {Sz}*{Z Grid K Unit Normal})'


			$!ALTERDATA
				EQUATION = '{Tx} = ({Sx} - {Sigma}*{X Grid K Unit Normal})'

			$!ALTERDATA
			    EQUATION = '{Ty} = ({Sy} - {Sigma}*{Y Grid K Unit Normal})'

			$!ALTERDATA
			    EQUATION = '{Tz} = ({Sz} - {Sigma}*{Z Grid K Unit Normal})'


			$!ALTERDATA
			    EQUATION = '{Tw} = 0.0035*sqrt({Tx}*{Tx} + {Ty}*{Ty} + {Tz}*{Tz})'


			$!ALTERDATA
			    EQUATION = '{WSSG} = 0.0035*sqrt((ddx({Tx}))**2 + (ddy({Ty}))**2 + (ddz({Tz}))**2)'  
			''')

        frame =tecplot.active_frame()


        variables_to_save = [frame.dataset.variable(V)
				     for V in ('X','Y','Z','X Velocity','Y Velocity','Z Velocity','s11','s12','s13','s22','s23','s33','vdotN','Tx','Ty','Tz','Tw','WSSG')]

        outfile = surface_save_dir / ("NeckWSS_"+str(i).zfill(3)+".dat")
        zone_to_save = frame.dataset.zone(Pt.neck_zone_name)
        tecplot.data.save_tecplot_ascii(outfile, dataset=frame.dataset,
						variables=variables_to_save,
						zones=[zone_to_save])
                
        print ("finished neck #" , i+1)


def NeckWSSMetrics(Pt):
    surface_save_dir = Pt.parent_dir / 'NeckWSS'
    NeckPlaneFiles = sorted(surface_save_dir.glob("*.dat"))

    tecplot.new_layout()    	
    tecplot.data.load_tecplot(NeckPlaneFiles)
    frame = tecplot.active_frame()
    frame.plot_type = tecplot.constant.PlotType.Cartesian3D

    WSSid = frame.dataset.variable("Tw").index
    WSSGid = frame.dataset.variable("WSSG").index

    NeckPlaneWSS = Compute_Average(WSSid,"NeckWSS.txt")
    NeckPlaneWSSG = Compute_Average(WSSGid,"NeckWSSG.txt")

	
    dSys = {"Sys. Neck WSS (Pa)": max(NeckPlaneWSS),
            "Sys. Neck WSSG (Pa/m)": max(NeckPlaneWSSG)
	}

    dTA = {"TA Neck WSS (Pa)": np.mean(NeckPlaneWSS),
           "TA Neck WSSG (Pa/m)": np.mean(NeckPlaneWSSG),

	}

    return dSys, dTA





