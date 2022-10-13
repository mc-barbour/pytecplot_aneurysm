# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 07:59:45 2022

@author: barbourm

Functions that execute tecplot macros

"""
import tecplot
import numpy as np




def Integrate_Scalar(IntZone,OutFile):
    """
    Integrate a scalar across IntZone for all time points. Data is saved in Outfile
    """
    
    tecplot.macro.execute_command(r'''
	$!EXTENDEDCOMMAND 
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'Integrate VariableOption=\'Scalar\' ScalarVar='''+str(IntZone+1)+r''' Absolute=\'F\' ExcludeBlanked=\'T\' IntegrateOver=\'Cells\''
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
	   COMMAND = 'Integrate VariableOption=\'Average\' ScalarVar='''+str(IntZone+1)+r''' Absolute=\'F\' ExcludeBlanked=\'F\' IntegrateOver=\'Cells\''
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
	   COMMAND = 'Integrate VariableOption=\'LengthAreaVolume\' ScalarVar='''+str(IntZone+1)+r''' Absolute=\'F\' ExcludeBlanked=\'T\' IntegrateOver=\'Cells\''
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
	   COMMAND = 'Integrate ['''+str(zoneid+1)+r''']VariableOption=\'LengthAreaVolume\' ScalarVar=1 Absolute=\'F\' ExcludeBlanked=\'F\' IntegrateOver=\'Cells\''
	$!EXTENDEDCOMMAND
	   COMMANDPROCESSORID = 'CFDAnalyzer4'
	   COMMAND = 'SaveIntegrationResults FileName=\'''' + OutFile + r'''\' '

	 ''')
 
    data = np.genfromtxt(OutFile,skip_header=1,skip_footer=1,usecols=2)
    print (OutFile,data)
    return data
