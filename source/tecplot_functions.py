# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 07:59:45 2022

@author: barbourm

Functions that execute tecplot macros

"""
import tecplot
import numpy as np



def vdotN():
    tecplot.macro.execute_command(r'''
			$!EXTENDEDCOMMAND 
	  		  COMMANDPROCESSORID = 'CFDAnalyzer4'
	  		  COMMAND = 'Calculate Function=\'GRIDKUNITNORMAL\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'T\''
			$!EXTENDEDCOMMAND 
	  		  COMMANDPROCESSORID = 'CFDAnalyzer4'
	  		  Command = 'Calculate Function=\'CELLVOLUME\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'T\''
			$!ALTERDATA 
				EQUATION = '{vdotN} = {X Velocity}*{X Grid K Unit Normal} + {Y Velocity}*{Y Grid K Unit Normal} + {Z Velocity}*{Z Grid K Unit Normal}'
			''')

def strain_rate_tensor(viscosity = 0.0035):
    tecplot.macro.execute_command(r'''
			
            $!ExtendedCommand 
              CommandProcessorID = 'CFDAnalyzer4'
              Command = 'Calculate Function=\'VELOCITYGRADIENT\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'T\''
			$!ALTERDATA EQUATION = '{s11} = {dUdX}'
			$!ALTERDATA EQUATION = '{s12} = 0.5*({dUdY}+{dVdX})'
			$!ALTERDATA EQUATION = '{s13} = 0.5*({dUdZ}+{dWdX})'
			$!ALTERDATA EQUATION = '{s22} = {dVdY}'
			$!ALTERDATA EQUATION = '{s23} = 0.5*({dVdZ}+{dWdY})'
			$!ALTERDATA EQUATION = '{s33} = {dWdZ}'
            $!ALTERDATA EQUATION = '{epsilon_temp} = 2*({s12}**2 + {s13}**2 + {s23}**2) + {s11}**2 + {s22}**2 + {s33}**2 '	
            $!ALTERDATA EQUATION = '{epsilon} = 2 * ''' + str(viscosity) + r'''* {epsilon_temp} '
            
            # '{epsilon} = 2 * ''' + str(viscosity) + r'''* (2 * ({s12}**2 + {s13}**2 + {s23}**2) + {s11}**2 + {s22}**2 + {s33}**2) '	

			''')
            
def neck_shear():
    print("Computing neck shear")
    tecplot.macro.execute_command(r'''
# 			$!DELETEZONES [1,2]

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



  
def integrate_scalar_singlezone(IntZone, scalar, OutFile):
    """
    Integrate a scalar across IntZone for all time points. Data is saved in Outfile
    """

    tecplot.macro.execute_command(r'''
	$!EXTENDEDCOMMAND 
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'Integrate '''+str(IntZone+1)+r''' VariableOption=\'Scalar\' ScalarVar='''+str(scalar+1)+r''' Absolute=\'T\' ExcludeBlanked=\'F\' XOrigin=0 YOrigin=0 ZOrigin=0 XVariable=1 YVariable=2 ZVariable=3 IntegrateOver=\'Cells\' IntegrateBy=\'Zones\' '
	$!EXTENDEDCOMMAND
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'SaveIntegrationResults FileName=\'''' + OutFile + r'''\' '

	 ''')

    data = np.genfromtxt(OutFile,skip_header=1,skip_footer=1,usecols=2)
    print (OutFile, "Sys: ", data )
    return data    
  
    


def Integrate_Scalar(IntZone, OutFile):
    """
    Integrate a scalar across IntZone for all time points. Data is saved in Outfile
    """
    
    tecplot.macro.execute_command(r'''
	$!EXTENDEDCOMMAND 
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'Integrate VariableOption=\'Scalar\' ScalarVar='''+str(IntZone+1)+r''' Absolute=\'T\' ExcludeBlanked=\'T\' IntegrateOver=\'Cells\''
	$!EXTENDEDCOMMAND
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'SaveIntegrationResults FileName=\'''' + OutFile + r'''\' '

	 ''')

    data = np.genfromtxt(OutFile,skip_header=1,skip_footer=1,usecols=2)
    print (OutFile, "Sys: ", max(data), "TA: ", np.mean(data))
    return data

def Compute_Average(IntZone,OutFile):
    """
    Compute the average of a scalar across IntZones for all time points. Data is saved in Outfile
    """
    tecplot.macro.execute_command(r'''
	$!EXTENDEDCOMMAND 
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'Integrate VariableOption=\'Average\' ScalarVar='''+str(IntZone+1)+r''' Absolute=\'T\' ExcludeBlanked=\'F\' IntegrateOver=\'Cells\''
	$!EXTENDEDCOMMAND
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'SaveIntegrationResults FileName=\'''' + OutFile + r'''\' '

	 ''')

    data = np.genfromtxt(OutFile,skip_header=1,skip_footer=1,usecols=2)
    print (OutFile, "Sys: ", max(data), "TA: ", np.mean(data))
    return data


def Integrate_Area(IntZone,OutFile):
    """
    Compute the area IntZone for all time points. Data is saved in Outfile
    """
    
    tecplot.macro.execute_command(r'''
	$!EXTENDEDCOMMAND 
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'Integrate VariableOption=\'LengthAreaVolume\' ScalarVar='''+str(IntZone+1)+r''' Absolute=\'T\' ExcludeBlanked=\'T\' IntegrateOver=\'Cells\''
	$!EXTENDEDCOMMAND
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'SaveIntegrationResults FileName=\'''' + OutFile + r'''\' '

	 ''')

    data = np.genfromtxt(OutFile,skip_header=1,skip_footer=1,usecols=2)
    print (OutFile, "Sys: ", max(data), "TA: ", np.mean(data))
    return data	

def Area_Compute(zoneid, OutFile):

    tecplot.macro.execute_command(r'''
	$!EXTENDEDCOMMAND 
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'Integrate ['''+str(zoneid+1)+r''']VariableOption=\'LengthAreaVolume\' ScalarVar=1 Absolute=\'T\' ExcludeBlanked=\'F\' IntegrateOver=\'Cells\''
	$!EXTENDEDCOMMAND
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'SaveIntegrationResults FileName=\'''' + OutFile + r'''\' '

	 ''')
 
    data = np.genfromtxt(OutFile,skip_header=1,skip_footer=1,usecols=2)
    print (OutFile,data)
    return data

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


