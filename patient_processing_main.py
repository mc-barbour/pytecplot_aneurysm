import os
import sys
import tecplot
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from source.parameters import *
from source.neck_metrics import *



def save_metrics(data_dict, filename):
    
    if filename.exists() == True:

        df = pd.read_csv(filename)
        dfnew = pd.DataFrame([data_dict])

        for key,value in data_dict.items():
            df[key] = dfnew[key]

        df.to_csv(filename)
        
    else:
        df = pd.DataFrame([data_dict])
        df.to_csv(filename)

def process(Pt):
    
    dataSys = {}
    dataTA = {}
    
    if Pt.NeckWSS:
        print("Processing Neck WSS...")
        NeckWSSCompute(Pt)
        Sys,TA = NeckWSSMetrics(Pt)
        dataSys.update(Sys)
        dataTA.update(TA)
   
    if Pt.NeckFlow:
        print("Processing Aneurysm Flow...")
        NeckFlowInterpolate(Pt)
        Sys, TA, Neck_area = NeckFlowMetrics(Pt)
        dataSys.update(Sys)
        dataTA.update(TA)
        print(dataSys)
        
    if Pt.AneurysmWSS:
        print("Processing Aneurysm WSS...")
        Sys,TA = AneurysmWSS(Pt)
        dataSys.update(Sys)
        dataTA.update(TA)
    
    
    if Pt.AneurysmEps:
    	Sys,TA,dVol = EpsAneurysm(Pt)
    	dataSys.update(Sys)
    	dataTA.update(TA)
    	dataTA.update(dVol)
        
    SysOutFile = Pt.parent_dir / (Pt.id + "_SysData.csv")
    TAOutFile = Pt.parent_dir / (Pt.id + "_TAData.csv")
    
    save_metrics(dataSys, SysOutFile)
    save_metrics(dataSys, TAOutFile)

if __name__ == '__main__':
    process(Pt)




    # if filename.exists() == True:

    #     df = pd.read_csv(filename)
    #     dfnew = pd.DataFrame([data_dict])

    #     for key,value in data_dict.items():
    #         df[key] = dfnew[key]

    #     df.to_csv(filename)
    # else:












