# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 12:14:03 2016

@author: OPdaTe
"""

import csv
import os



class Sample:
    def __init__(self,ID,databasefolder):
        self.id = str(ID)
        self.databasefolder = databasefolder
        self.status = None 
        self.label = None 
        self.name = None 
        self.project = None 
        self.description = None 
        self.materials = None 
        self.width = None 
        self.height  = None 
        self.depth = None 
        self.weight = None 
        self.imagefolder_link = '%s\Samples images\%s' %(databasefolder,self.id)
        self.history_link = '%s\Samples history\%s' %(databasefolder,self.id)
        self.location = None 
        self.owner = None
        self.dataset= None
        self.inizialize()
    
    def inizialize(self):
        with open('%s\samples.csv'%(self.databasefolder),'rb') as csvfile:
            spamreader = csv.reader(csvfile,delimiter = ',')
            for i in spamreader:
                if i[0]=='id':
                    header = i
              
                if i[0]==self.id:
                    fields = i
           
                    
        values = dict(zip(header,fields))
        

        self.status = values['Status']
        self.sample = values['Label']
        self.name = values['Name']
        self.project = values['Project']
        self.dataset= values['Dataset']
        self.description = values['Description']
        self.materials = values['Materials']
        self.width = values['Width']
        self.height  = values['Height ']
        self.depth = values['Depth']
        self.weight = values['Weight']
        self.location = values['Location']
        self.owner = values['Owner']
        self.creator = values['Creator']


    
    def show_photo(self,img=0):
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        listimage = os.listdir(self.imagefolder_link)
        imgx=mpimg.imread('%s\\%s' %(self.imagefolder_link,listimage[img]))
        plt.imshow(imgx)
        
    def get_image(img=0)
        import matplotlib.image as mpimg
        listimage = os.listdir(self.imagefolder_link)
        imgx=mpimg.imread('%s\\%s' %(self.imagefolder_link,listimage[img]))
        return imgx

    def open_history(self):
        pass
        
    def print_preparation(self):
        G=False
        with open(self.history_link) as f:
            for i in f:
                if G:
                    if i.split(' ')[0]=='#':
                        G = False
                    else:
                        print i
                                        
                if i.split(' ')[0]=='#>PREPARATION':
                    G = True

    
    def print_analysis(self):       
        with open(self.history_link) as f:
            for i in f:
                if i.split(' ')[0]=='#>ANALISYS':
                    print i

 
