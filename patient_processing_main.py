# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 15:17:04 2022

@author: barbourm
"""

import os
import sys
import tecplot
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from source.parameters import *
from source.neck_metrics import *
from source.processing import *



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
    
    if (Pt.AneurysmAvgVel or Pt.AneurysmWSS or Pt.NeckWSS or Pt. NeckFlow or Pt.AneurysmEps):
        
        perform_tecplot_analysis(Pt)
    
    if Pt.SummarizeNeckMetrics:
        Sys, TA = summarize_neck_metrics(Pt)
        dataSys.update(Sys)
        dataTA.update(TA)
    if Pt.SummarizeExcelMetrics:
        Sys, TA = summarize_excel_metrics(Pt)
        dataSys.update(Sys)
        dataTA.update(TA)

    SysOutFile = Pt.post_process_dir / (Pt.id + "_" + Pt.sim_type + "_SysData.csv")
    TAOutFile = Pt.post_process_dir / (Pt.id + "_" + Pt.sim_type +"_TAData.csv")
    
    save_metrics(dataSys, SysOutFile)
    
    if Pt.TimeAverage:
        save_metrics(dataTA, TAOutFile)

if __name__ == '__main__':
    process(Pt)



