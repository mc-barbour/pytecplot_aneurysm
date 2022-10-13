# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 13:49:39 2022

@author: barbourm
"""


class Parameters():
    
    def __init__(self,datafiles, case, patient_id, processing_boolean, zones, surface_files, surface_names, parent_dir):
        
        self.datafiles = datafiles
        self.case = case
        self.id = patient_id
        self.parent_dir = parent_dir
        
        self.AneurysmAvgVel = processing_boolean['AneurysmAvgVel']
        self.AneurysmWSS = processing_boolean['AneurysmWSS']
        self.NeckWSS = processing_boolean['NeckWSS']
        self.AneurysmEps = processing_boolean['AneurysmEps']
        self.NeckFlow = processing_boolean['NeckFlow']
        self.InletFlowrate = processing_boolean['InletFlowRate']


        self.pv_vol = zones['pv_vol']
        self.pv_surf = zones['pv_surf']
        self.an_vol = zones['an_vol']
        self.an_surf = zones['an_surf']
        self.inlet = zones['inlet']
        
        if self.NeckWSS or self.NeckFlow:
            self.neckfile = surface_files['neck']
            self.neck_zone_name = surface_names['neck_name']
        
        # self.velfile = surface_files['velocity']
        # self.vel_surf = surface_files['vel_name']
        
        # self.neckfile = neckfile
        # self.neck_surf = neck_surf
        # self.aneurysmfile = aneurysmfile
        # self.aneurysm_surf = aneurysm_surf
        # self.aneurysmvolfile = aneurysmvolfile
        # self.aneurysm_vol = aneurysm_vol


