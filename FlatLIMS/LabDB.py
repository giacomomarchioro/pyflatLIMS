# -*- coding: utf-8 -*-
"""
Created on Fri Jun 03 15:05:00 2016


@author: OPdaTe
"""
import csv
import os
import pandas as pd


class Lab_space:
    def __init__(self):
        pass





class EquipmentDB:
    types = {'0':'Lens','1':'Cable','2':'Camera','3':'Source','4':'Filters&Fibers','5':'Standard'}
    status = {'0':'Available','1':'Outside Lab','2':'Lost','3':'In progress'}
    project = {'0': 'Scan4Reco',}
    lens_header = ['focal length', 'material', 'diameter','transmittance range', ]
    camera_header = ['spectral range', 'pixel size', 'resolution', 'sensitivity', ]



    def __init__(self,path,name='eqipment'):
        self.path=path
        self.name=name
        self.header=['id','status','Name/Model','S/N','Company','type','description','quantity','project',
                     'parents','width','height ','depth','weight','location',
                  'owner','holes','diameter',]



    def create_newDB(self):
        if not os.path.exists(r'%s\LabDatabase' %(self.path)):
            os.makedirs(r'%s\LabDatabase' %(self.path))
            os.makedirs(r'%s\LabDatabase\EquipmentDB' %(self.path))
            os.makedirs(r'%s\LabDatabase\EquipmentDB\Equipment images' %(self.path))
            os.makedirs(r'%s\LabDatabase\EquipmentDB\Equipment history' %(self.path))
            os.makedirs(r'%s\LabDatabase\EquipmentDB\User manuals' %(self.path))
            os.makedirs(r'%s\LabDatabase\EquipmentDB\Equipment characterization' %(self.path))
            os.makedirs(r'%s\LabDatabase\EquipmentDB\Equipment SubTypesdb' %(self.path))

        else:
            if not os.path.exists(r'%s\LabDatabase\EquipmentDB\Equipment images' %(self.path)):
                os.makedirs(r'%s\LabDatabase\EquipmentDB\Equipment images' %(self.path))
                os.makedirs(r'%s\LabDatabase\EquipmentDB\Equipment history' %(self.path))
                os.makedirs(r'%s\LabDatabase\EquipmentDB\User manuals' %(self.path))
                os.makedirs(r'%s\LabDatabase\EquipmentDB\Equipment characterization' %(self.path))
                os.makedirs(r'%s\LabDatabase\EquipmentDB\Equipment SubTypesdb' %(self.path))

            else:
                print 'There is already a database in this directory'


        if not os.path.exists(r'%s\LabDatabase\EquipmentDB\%s.csv' %(self.path,self.name)):
            with open(r'%s\LabDatabase\EquipmentDB\%s.csv' %(self.path,self.name), 'wb') as f:
                writer = csv.writer(f)
                writer.writerow(self.header)


    def check_integrity(self):
        import numpy as np
        ids = pd.read_csv(r'%s\LabDatabase\EquipmentDB\%s.csv'
        %(self.path,self.name)).as_matrix()[:,1]
        if ids.shape == ():
            return ids

        if len(ids) != len(np.unique(ids)):
            print '**CRITICAL WARNING: MULTIPLE IDs FOR EQUIPMENT!!**'

        return ids

    def add_item(self):
        import numpy as np
        global multiplechoice
        ids = self.check_integrity()

        if ids.shape == (0,):
            newid = 1

        else:
            newid = np.max(ids) + 1

        fields = [newid]

        #Inizialize the sample creating image folder and history txt
        samplehist=r'%s\LabDatabase\EquipmentDB\Equipment history\%s.txt' %(self.path,newid)
        sampleimgfold=r'%s\LabDatabase\EquipmentDB\Equipment images\%s' %(self.path,newid)
        os.makedirs(sampleimgfold)



        #Complate the fields regarding the other spec.
        for i in self.header[1:]: #avoid looping over id and link
            fields.append(raw_input('%s : ' %(i)) )

        #Write all the information to the csv file.
        with open(r'%s\LabDatabase\EquipmentDB\%s.csv' %(self.path,self.name), 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)


        answ_um=raw_input('Do you want to add an user manual? y/n')
        if answ_um.lower() =='y':
            print 'Paste this path when you save it:'
            os.makedirs('%s\LabDatabase\EquipmentDB\User manuals\%s' %(self.path,newid))
            print '%s\LabDatabase\EquipmentDB\User manuals\%s' %(self.path,newid)
            import webbrowser
            url = "https://www.google.com.tr/search?q=user manual %s %s" %(fields[2],fields[4])
            webbrowser.open(url)

        answ_img=raw_input('Do you want to add image from webcam? y/n')
        if answ_img=='y':
           print 'Press SPACE to aquire ESC to close'
           counter=0
           names = [i.split('.')[0] for i in os.listdir(sampleimgfold)]
           while str(counter) in names:
               counter+=1
           self.takeimage(newid,str(counter))
           print 'Flip the object'
           name=str(counter)+'_B'
           self.takeimage(newid,name)



    def load_DB(self):
        data = pd.read_csv(r'%s\LabDatabase\EquipmentDB\%s.csv' %(self.path,self.name),delimiter=',',names=True).as_matrix()
        return data

    def modify_item(self,ID):
        pass

    def add_photo_to_item(self,ID):
        pass

    def print_paper_label(self,ID):
        pass

    def takeimage(self,ID,name,camera_port=1):
        '''
        It saves an image using OpenCV and the webcam connected to the second
        port, directly on the sample image folder.

        Parameters
        ----------
        name : str
                 nome of the image
        camera_port : int
                 Define which device will be used for acquiring the image.
                 0 usaully is the built-in webca. 1 any other usb device pluged.
                 (default 1)

        Returns
        -------
        It save an image in the image folder.
        '''
        import cv2
        cv2.namedWindow("preview")
        vc = cv2.VideoCapture(camera_port)

        if vc.isOpened(): # try to get the first frame
            rval, frame = vc.read()
        else:
            rval = False

        while rval:
            cv2.imshow("preview", frame)
            rval, frame = vc.read()
            key = cv2.waitKey(20)
            if key == 27: # exit on ESC
                break
        cv2.destroyWindow("preview")

        rval, im = vc.read()
        ramp_frames=30


        # Captures a single image from the camera and returns it in PIL format
        def get_image():
        # read is the easiest way to get a full image out of a VideoCapture object.
            retval, im = vc.read()
            return im

        # Ramp the camera - these frames will be discarded and are only used to allow v4l2
        # to adjust light levels, if necessary
        for i in xrange(ramp_frames):
            temp = get_image()
        print("Taking image...")
        # Take the actual image we want to keep
        camera_capture = get_image()
        file =r'%s\LabDatabase\EquipmentDB\Equipment images\%s' %(self.path,ID)
        # A nice feature of the imwrite method is that it will automatically choose the
        # correct format based on the file extension you provide. Convenient!
        cv2.imwrite(file, camera_capture)

        # You'll want to release the camera, otherwise you won't be able to create a new
        # capture object until your script exits
        vc.release()
#Create the LabDatabase instance
samplesdb = SamplesDB(r"C:\Users\OPdaTe\Documents")

equipmentdb =  EquipmentDB(r"C:\Users\OPdaTe\Documents")

class Lens:
    def __init__(self):
        pass


class EqTypes:
    def Lens_add(self):
        self.header = ['focal length', 'material', 'diameter','transmittance range', ]


    def Filter_add(self):
        pass


class labDB:
    def __init__(self,path):
        self.path=path
        self.samplesDB = SamplesDB(self.path)
        self.equipmentDB = EquipmentDB(self.path)

    def create_newDB(self):
        self.samplesDB.create_newDB()
        self.equipmentDB.create_newDB()

alabDB =  labDB(r"C:\Users\OPdaTe\Documents")
