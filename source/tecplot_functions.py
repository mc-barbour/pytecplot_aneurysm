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
                DATATYPE = DOUBLE
                
                ''')
                
def velmag():
    tecplot.macro.execute_command(r'''
            $!EXTENDEDCOMMAND
	  		  COMMANDPROCESSORID = 'CFDAnalyzer4'
	  		  COMMAND = 'Calculate Function=\'VELOCITYMAG\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'T\' UseMorePointsForFEGradientCalculations=\'T\''
            $!ALTERDATA
    	      EQUATION = '{VelMag} = {Velocity Magnitude}'
                ''')

def domeWSS_h5():
    tecplot.macro.execute_command(r'''
            $!ALTERDATA
              VALUELOCATION=NODAL
              EQUATION = '{WSS (Pa)} = sqrt({Wall Shear Stress-1}**2 + {Wall Shear Stress-2}**2 + {Wall Shear Stress-3}**2)'
            $!ALTERDATA
              VALUELOCATION=NODAL
              EQUATION = '{WSSG (Pa/m)} = sqrt((ddx({Wall Shear Stress-1}))**2 + (ddy({Wall Shear Stress-2}))**2 + (ddz({Wall Shear Stress-3}))**2)'
                    ''')

def domeWSS_old():
    tecplot.macro.execute_command(r'''
            $!ALTERDATA
              VALUELOCATION=NODAL
              EQUATION = '{WSS (Pa)} = sqrt({Wall Shear-1}**2 + {Wall Shear-2}**2 + {Wall Shear-3}**2)'
            $!ALTERDATA
              VALUELOCATION=NODAL
              EQUATION = '{WSSG (Pa/m)} = sqrt((ddx({Wall Shear-1}))**2 + (ddy({Wall Shear-2}))**2 + (ddz({Wall Shear-3}))**2)'
              
              ''')

def strain_rate_tensor(viscosity = 0.0035):
    tecplot.macro.execute_command(r'''
			
            $!ExtendedCommand 
              CommandProcessorID = 'CFDAnalyzer4'
              Command = 'Calculate Function=\'VELOCITYGRADIENT\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'T\''
			
            $!ALTERDATA 
                EQUATION = '{s11} = {dUdX}'
                DATATYPE = DOUBLE
                
			$!ALTERDATA 
                EQUATION = '{s12} = 0.5*({dUdY}+{dVdX})'
                DATATYPE = DOUBLE
                
			$!ALTERDATA 
                EQUATION = '{s13} = 0.5*({dUdZ}+{dWdX})'
                DATATYPE = DOUBLE
                
			$!ALTERDATA 
                EQUATION = '{s22} = {dVdY}'
                DATATYPE = DOUBLE
                
			$!ALTERDATA 
                EQUATION = '{s23} = 0.5*({dVdZ}+{dWdY})'
                DATATYPE = DOUBLE
                
			$!ALTERDATA 
                EQUATION = '{s33} = {dWdZ}'
                DATATYPE = DOUBLE
                
            $!ALTERDATA 
                EQUATION = '{epsilon_temp} = 2*({s12}**2 + {s13}**2 + {s23}**2) + {s11}**2 + {s22}**2 + {s33}**2 '	
                DATATYPE = DOUBLE
                
            $!ALTERDATA 
                EQUATION = '{epsilon} = 2 * ''' + str(viscosity) + r'''* {epsilon_temp} '
                DATATYPE = DOUBLE
            
			''')
            
def neck_shear(zoneid):
    print("Computing neck shear")
    tecplot.macro.execute_command(r'''


			$!EXTENDEDCOMMAND 
	  		  COMMANDPROCESSORID = 'CFDAnalyzer4'
	  		  COMMAND = 'Calculate Function=\'GRIDKUNITNORMAL\' Normalization=\'None\' ValueLocation=\'Nodal\' CalculateOnDemand=\'F\' UseMorePointsForFEGradientCalculations=\'T\''

	  		$!ALTERDATA ['''+str(zoneid+1)+r''']
				EQUATION = '{vdotN} = {X Velocity}*{X Grid K Unit Normal} + {Y Velocity}*{Y Grid K Unit Normal} + {Z Velocity}*{Z Grid K Unit Normal}'
                DATATYPE = DOUBLE
                
            $!ALTERDATA ['''+str(zoneid+1)+r''']
			    EQUATION = '{Sx} = ({s11}*{X Grid K Unit Normal} + {s12}*{Y Grid K Unit Normal} + {s13}*{Z Grid K Unit Normal})'
                DATATYPE = DOUBLE
                
			$!ALTERDATA ['''+str(zoneid+1)+r''']
			    EQUATION = '{Sy} = ({s12}*{X Grid K Unit Normal} + {s22}*{Y Grid K Unit Normal} + {s23}*{Z Grid K Unit Normal})'
                DATATYPE = DOUBLE
                
			$!ALTERDATA ['''+str(zoneid+1)+r''']
			    EQUATION = '{Sz} = ({s13}*{X Grid K Unit Normal} + {s23}*{Y Grid K Unit Normal} + {s33}*{Z Grid K Unit Normal})'
                DATATYPE = DOUBLE

			$!ALTERDATA ['''+str(zoneid+1)+r''']
			    EQUATION = '{Sigma} = ({Sx}*{X Grid K Unit Normal} + {Sy}*{Y Grid K Unit Normal} + {Sz}*{Z Grid K Unit Normal})'
                DATATYPE = DOUBLE

			$!ALTERDATA ['''+str(zoneid+1)+r''']
				EQUATION = '{Tx} = ({Sx} - {Sigma}*{X Grid K Unit Normal})'
                DATATYPE = DOUBLE
                
			$!ALTERDATA ['''+str(zoneid+1)+r''']
			    EQUATION = '{Ty} = ({Sy} - {Sigma}*{Y Grid K Unit Normal})'
                DATATYPE = DOUBLE
                
			$!ALTERDATA ['''+str(zoneid+1)+r''']
			    EQUATION = '{Tz} = ({Sz} - {Sigma}*{Z Grid K Unit Normal})'
                DATATYPE = DOUBLE

			$!ALTERDATA ['''+str(zoneid+1)+r''']
			    EQUATION = '{Tw} = 0.0035*sqrt({Tx}*{Tx} + {Ty}*{Ty} + {Tz}*{Tz})'
                DATATYPE = DOUBLE

			$!ALTERDATA ['''+str(zoneid+1)+r''']
			    EQUATION = '{WSSG} = 0.0035*sqrt((ddx({Tx}))**2 + (ddy({Ty}))**2 + (ddz({Tz}))**2)'  
                IGNOREDIVIDEBYZERO = YES
                DATATYPE = DOUBLE
            
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
  

def compute_average_singlezone(IntZone, scalar, OutFile):
    """
    Compute the average of a scalar across IntZones for all time points. Data is saved in Outfile
    """
    print(OutFile)
    
    tecplot.macro.execute_command(r'''
	$!EXTENDEDCOMMAND 
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'Integrate '''+str(IntZone+1)+r''' VariableOption=\'Average\' ScalarVar='''+str(scalar+1)+r''' Absolute=\'T\' ExcludeBlanked=\'F\' XOrigin=0 YOrigin=0 ZOrigin=0 XVariable=1 YVariable=2 ZVariable=3 IntegrateOver=\'Cells\' IntegrateBy=\'Zones\' '
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
    # print (OutFile, "Sys: ", max(data), "TA: ", np.mean(data))
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
    # print(data)
    # if len(data) >= 1:
    #     print (OutFile, "Sys: ", max(data), "TA: ", np.mean(data))
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


