# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 13:49:39 2022

@author: barbourm
"""


class Parameters():
    
    def __init__(self,datafiles, case, patient_number, sim_type, processing_boolean, zone_ids, surface_files, zone_names, parent_dir, datafile_start_num=0):
        
        self.datafiles = datafiles
        self.case = case
        self.id = patient_number
        self.sim_type = sim_type
        self.parent_dir = parent_dir
        self.post_process_dir = self.parent_dir / 'post_process' / self.sim_type
        self.datafile_start_num = datafile_start_num
        
        if (len(datafiles) == 0 or len(case) == 0):
            raise ValueError("No data files found. Please check defined file locations and working directory")

        
        if not (self.parent_dir / 'post_process').exists():
            (self.parent_dir / 'post_process').mkdir()
            self.post_process_dir.mkdir()
        
        if not self.post_process_dir.exists():
            self.post_process_dir.mkdir()
            
        
        self.AneurysmAvgVel = processing_boolean['AneurysmAvgVel']
        self.AneurysmWSS = processing_boolean['AneurysmWSS']
        self.NeckWSS = processing_boolean['NeckWSS']
        self.AneurysmEps = processing_boolean['AneurysmEps']
        self.NeckFlow = processing_boolean['NeckFlow']
        self.SummarizeNeckMetrics = processing_boolean["SummarizeNeckMetrics"]
        self.SummarizeExcelMetrics = processing_boolean["SummarizeExcelMetrics"]
        self.TimeAverage = processing_boolean['TimeAverage']


        self.pv_vol = zone_ids['pv_vol']
        self.pv_surf = zone_ids['pv_surf']
        self.an_vol = zone_ids['an_vol']
        self.an_surf = zone_ids['an_surf']

        if self.NeckWSS or self.NeckFlow:
            
            if len(surface_files['neck']) == 0:
                raise ValueError("No neck file found. Check file location")
            else:
                self.neckfile = surface_files['neck']
                self.neck_zone_name = zone_names['neck']
        
        self.aneurysm_zone_name = zone_names['aneurysm']
        self.pv_zone_name = zone_names['pv']
        self.aneurysm_surf_name = zone_names['aneurysm-wall']
        
        # self.velfile = surface_files['velocity']
        # self.vel_surf = surface_files['vel_name']
        
        # self.neckfile = neckfile
        # self.neck_surf = neck_surf
        # self.aneurysmfile = aneurysmfile
        # self.aneurysm_surf = aneurysm_surf
        # self.aneurysmvolfile = aneurysmvolfile
        # self.aneurysm_vol = aneurysm_vol


