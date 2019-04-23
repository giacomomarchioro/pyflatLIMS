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



class SamplesDB:
       
    
    def __init__(self,path,name='samples'):
        self.path=path
        self.name=name
        self.header=['id','Status','Name','Label','Project','Dataset','Description',
                  'Materials','Width','Height ','Depth','Weight','Location',
                  'Creator','Owner']
        self._autocommit=False
        self.camera_port = 1
        
        
        
    
    def create_newDB(self,inizializeGIT=False):
        if not os.path.exists(r'%s\LabDatabase' %(self.path)):
            os.makedirs(r'%s\LabDatabase' %(self.path))
            os.makedirs(r'%s\LabDatabase\SamplesDB' %(self.path))
            os.makedirs(r'%s\LabDatabase\SamplesDB\Samples images' %(self.path))
            os.makedirs(r'%s\LabDatabase\SamplesDB\Samples history' %(self.path))
        
        else:
            if not os.path.exists(r'%s\LabDatabase\SamplesDB' %(self.path)):
                os.makedirs(r'%s\LabDatabase\SamplesDB\Samples images' %(self.path))
                os.makedirs(r'%s\LabDatabase\SamplesDB\Samples history' %(self.path))
            
            else:
                print 'There is already a database in this directory'
            

        if not os.path.exists(r'%s\LabDatabase\SamplesDB\%s.csv' %(self.path,self.name)):
            with open(r'%s\LabDatabase\SamplesDB\%s.csv' %(self.path,self.name), 'wb') as f:
                writer = csv.writer(f)
                writer.writerow(self.header)
        
        if not os.path.exists(r'%s\LabDatabase\SamplesDB\.config.txt' %(self.path)):
            with open(r'%s\LabDatabase\SamplesDB\.config.txt' %(self.path), 'wb') as f:
                f.write('DEFAULT CAMERA COM: %s')
                f.write('GIT AUTO COMMIT: %s' %(inizializeGIT))
        
    
    def check_integrity(self):
        '''
        This is the main method to keep your database healthy:
          > it checks if the uniqueness 
        '''
        def getIDs():
            ids = pd.read_csv(r'%s\LabDatabase\SamplesDB\%s.csv' 
            %(self.path,self.name)).as_matrix()[:,0]
            IDset = set(ids)
            return ids, IDset
        
        ids, IDset = getIDs()
        
        if ids.shape == ():        
            return ids
            
        if len(ids) != len(IDset):
            print '**CRITICAL WARNING: MULTIPLE IDs FOR SAMPLE!!**'
            multipleID =  set([x for x in ids if ids.count(x) > 1])
            print multipleID
            
        smp_hist = {int(i.split('.')[0]) for i in 
        os.listdir(r'%s\LabDatabase\SamplesDB\Samples history' %(self.path))}
        images= {int(i) for i in 
        os.listdir(r'%s\LabDatabase\SamplesDB\Samples images' %(self.path))}
        set_folders = images | smp_hist        
        
        if set_folders - IDset != set():
            ans = raw_input('Do you want to delete unlinked files? y/n ')
            if ans.lower() == 'y':
                for idx in (set_folders - IDset):
                    self.delete_samplefiles(idx)
            ids, IDset = getIDs()
        
        if IDset - set_folders != set():
            ans = raw_input('Do you want to add linked files? y/n ')
            if ans.lower() == 'y':
                for idx in (IDset - set_folders):
                    self.create_hist_imgfolder(idx)
            ids, IDset = getIDs()
        
        return ids
        
    def add_sample(self):
        actors = {'0':'UniVR','1':'OPD','2':'Giacomo Marchioro',
        '3':'Marcella Formaggio','4':'Francesco Weisner'}
        status = {'0':'Available','1':'Outside Lab','2':'Lost','3':'In progress'}
        project = {'0':'Scan4Reco','1':'Tesi Nicola','3':'LabTest',
        '2':'FSE Microscopia','4':'Tesi Giacomo','5':'SUPSI'}
        dataset = {'0':'Silvers','1':'Bronzes','2':'Coins','3':'SanRocco'}        
        multiplechoice = {'Project':project,'Status':status,'Creator':actors,'Owner':actors,'Dataset':dataset}

        import numpy as np
        ids = self.check_integrity()
               
        if ids.shape == (0,):
            newid = 1
 
        else:
            newid = np.max(ids) + 1
        
        #This is the array where all the fields will be stored
        fields = [newid]
                       
        def dictchoose(dictionary):
            for i in sorted(dictionary):
                print ' %s - %s' %(i, dictionary[i])
            answ = raw_input('Select number or type new option: ')
            if answ in dictionary.keys():
                return dictionary[answ]               
            else:
                return answ
        
        #Complate the fields regarding the other spec.
        for i in self.header[1:]: #avoid looping over id and link
            if i in multiplechoice:
                print '%s : ' %(i)
                fields.append(dictchoose(multiplechoice[i]))
            else:
                fields.append(raw_input('%s : ' %(i)) )

        
        with open(r'%s\LabDatabase\SamplesDB\%s.csv' %(self.path,self.name), 'ab') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
        
        #create the imagefolder and ask for taking the photo
        self.create_hist_imgfolder(newid)
        print 'Sample %s has been added to LabDatabase in %s with ID:%s' %(fields[2],self.path,newid)
    
    def create_hist_imgfolder(self,newid):
         #Inizialize the sample creating image folder and history txt
        samplehist=r'%s\LabDatabase\SamplesDB\Samples history\%s.txt' %(self.path,newid)
        sampleimgfold=r'%s\LabDatabase\SamplesDB\Samples images\%s' %(self.path,newid)

        
        with open(samplehist,'w') as t:
            t.write('#PREPARATION: \n')
            preparation = raw_input('Preparation: ')
            t.writelines(preparation)
        
        os.makedirs(sampleimgfold)
       
        answ_img=raw_input('Do you want to add image from webcam? y/n ')
        if answ_img.lower() == 'y':
           self.add_photo_to_sample(newid)
        else:
            pass
           
    def delete_samplefiles(self,ID):
        '''
        This method remove all the filed linked with a specific ID. 
        To remove a sample just delete it directly from the .csv file. There is
        no need to run this method becuase it is called automatically
        before adding another sample by the .check_integrity method. 
        '''
        import shutil
        answ = raw_input('Are you sure you want to delete sample %s linked files? y/n' %(ID))
        if answ.lower() == 'y':           
            os.remove(r'%s\LabDatabase\SamplesDB\Samples history\%s.txt' %(self.path,ID))
            shutil.rmtree(r'%s\LabDatabase\SamplesDB\Samples images\%s' %(self.path,ID),
                          ignore_errors=False, onerror=None)
                                                    
        
        
    def load_DB(self):
        import numpy as np
        data = np.genfromtxt(r'%s\LabDatabase\SamplesDB\%s.csv' 
        %(self.path,self.name),delimiter=',',names=True)
        return data
        
    def modify_sample(self,ID):
        pass
    
    def add_photo_to_sample(self,ID):
        print 'Press SPACE to aquire ESC to close'
        sampleimgfold=r'%s\LabDatabase\SamplesDB\Samples images\%s' %(self.path,ID)
        counter=0
        names = [i.split('.')[0] for i in os.listdir(sampleimgfold)]
        while str(counter) in names:
            counter+=1
        self.takeimage(ID,str(counter))
        print 'Flip the object'
        name=str(counter)+'_B'
        self.takeimage(ID,name)
    
    def print_paper_label(self,ID):
        pass
    
    def takeimage(self,ID,name,camera_port=None):
        '''
        It saves an image using OpenCV and the webcam connected to the 
        second port, directly on the sample image folder.
    
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
        if camera_port == None:
            camera_port = self.camera_port
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
            if key == 27:
                cv2.destroyWindow("preview")
                return
                
            if key == 32: # exit on ESC
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
        file =r'%s\LabDatabase\SamplesDB\Samples images\%s\%s.png' %(self.path,ID,name)
        # A nice feature of the imwrite method is that it will automatically choose the
        # correct format based on the file extension you provide. Convenient!
        cv2.imwrite(file, camera_capture)
        # You'll want to release the camera, otherwise you won't be able to create a new
        # capture object until your script exits
        vc.release()


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
