import csv
import os
import pandas as pd
import sys
benc = 'w'
aenc = 'a'
# This if for compatibility with python 2.7
if sys.version_info[0] < 3:
    benc = 'wb'
    aenc = 'ab'


class SamplesDB:


    def __init__(self,path,name='samples'):
        self.path=path
        self.name=name
        self.header=['id','Status','Name','Label','Project','Dataset',
                    'Description','Materials','Width','Height ','Depth',
                    'Weight','Location','Creator','Owner']
        self._autocommit = False
        self.camera_port = 1
        self.path_labDB = os.path.join(self.path,'LabDatabase')
        self.path_samplesDB = os.path.join(self.path_labDB,'SamplesDB')
        self.path_imagesDB = os.path.join(self.path_samplesDB,'Samples images')
        self.path_histDB = os.path.join(self.path_samplesDB,'Samples history')
        self.path_csv = os.path.join(self.path_samplesDB,'%s.csv'%(self.name))
        self.path_config = os.path.join(self.path_labDB,'.config.txt')




    def create_newDB(self,inizializeGIT=False):
        if not os.path.exists(self.path_labDB):
            os.makedirs(self.path_labDB)
            os.makedirs(self.path_samplesDB)
            os.makedirs(self.path_imagesDB)
            os.makedirs(self.path_histDB)

        else:
            if not os.path.exists(self.path_samplesDB):
                os.makedirs(self.path_imagesDB)
                os.makedirs(self.path_histDB)

            else:
                print('There is already a database in this directory')


        if not os.path.exists(self.path_csv):
            with open(self.path_csv, benc) as f:
                writer = csv.writer(f)
                writer.writerow(self.header)

        if not os.path.exists(self.path_config):
            with open(self.path_config, benc) as f:
                f.write('DEFAULT CAMERA COM: %s')
                f.write('GIT AUTO COMMIT: %s' %(inizializeGIT))


    def check_integrity(self):
        '''
        This is the main method to keep your database healthy:
          > it checks if the uniqueness
        '''
        def getIDs():
            ids = pd.read_csv(self.path_csv).as_matrix()[:,0]
            IDset = set(ids)
            return ids, IDset

        ids, IDset = getIDs()

        if ids.shape == ():
            return ids

        if len(ids) != len(IDset):
            print('**CRITICAL WARNING: MULTIPLE IDs FOR SAMPLE!!**')
            multipleID =  set([x for x in ids if ids.count(x) > 1])
            print(multipleID)

        smp_hist = {int(i.split('.')[0]) for i in os.listdir(self.path_histDB)}
        images= {int(i) for i in os.listdir(self.path_imagesDB)}
        set_folders = images | smp_hist

        if set_folders - IDset != set():
            ans = input('Do you want to delete unlinked files? y/n ')
            if ans.lower() == 'y':
                for idx in (set_folders - IDset):
                    self.delete_samplefiles(idx)
            ids, IDset = getIDs()

        if IDset - set_folders != set():
            ans = input('Do you want to add linked files? y/n ')
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
                print( ' %s - %s' %(i, dictionary[i]))
            answ = input('Select number or type new option: ')
            if answ in dictionary.keys():
                return dictionary[answ]
            else:
                return answ

        #Complate the fields regarding the other spec.
        for i in self.header[1:]: #avoid looping over id and link
            if i in multiplechoice:
                print( '%s : ' %(i))
                fields.append(dictchoose(multiplechoice[i]))
            else:
                fields.append(input('%s : ' %(i)) )


        with open(self.path_csv, aenc) as f:
            writer = csv.writer(f)
            writer.writerow(fields)

        #create the imagefolder and ask for taking the photo
        self.create_hist_imgfolder(newid)
        print( 'Sample %s has been added to LabDatabase in %s with ID:%s'
               %(fields[2],self.path,newid))

    def create_hist_imgfolder(self,newid):
        #Inizialize the sample creating image folder and history txt
        samplehist = os.path.join(self.path_histDB,'%s.txt'%(newid))
        sampleimgfold = os.path.join(self.path_imagesDB,str(newid))
        with open(samplehist,benc) as t:
            t.write('#PREPARATION: \n')
            preparation = input('Preparation: ')
            t.writelines(preparation)
        os.makedirs(sampleimgfold)
        answ_img=input('Do you want to add image from webcam? y/n ')
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
        answ = input('Are you sure you want to delete sample %s linked files? y/n' %(ID))
        if answ.lower() == 'y':
            os.remove(os.path.join(self.path_histDB,'%s.txt'%(ID)))
            shutil.rmtree(os.path.join(self.path_imagesDB,str(ID)),
                          ignore_errors=False, onerror=None)



    def load_DB(self):
        import numpy as np
        data = np.genfromtxt(self.path_csv,delimiter=',',names=True)
        return data

    def modify_sample(self,ID):
        pass

    def add_photo_to_sample(self,ID):
        print( 'Press SPACE to aquire ESC to close')
        sampleimgfold=os.path.join(self.path_imagesDB,str(ID))
        counter=0
        names = [i.split('.')[0] for i in os.listdir(sampleimgfold)]
        while str(counter) in names:
            counter+=1
        self.takeimage(ID,str(counter))
        print( 'Flip the object')
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
        file = os.path.join(self.path_imagesDB,str(ID),name)
        # A nice feature of the imwrite method is that it will automatically choose the
        # correct format based on the file extension you provide. Convenient!
        cv2.imwrite(file, camera_capture)
        # You'll want to release the camera, otherwise you won't be able to create a new
        # capture object until your script exits
        vc.release()
