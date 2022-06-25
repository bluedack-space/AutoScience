# coding:utf-8
#!python3
from objc_util import *
from ctypes import c_void_p
from PIL import Image
from PIL import ImageOps
from queue import Queue
import ui
import io
import os
import time
import math
import photos
import tempfile
import concurrent.futures
import webbrowser
import platform
import datetime
import motion

import re

from iOSMotionHandler import *
from ImageMetaDataHandler import *

try:
    from Pythonista_Silent_camera.Gestures import Gestures
except:
    from Gestures import Gestures

# for test
import inspect

AVCaptureSession = ObjCClass('AVCaptureSession')
AVCaptureDevice = ObjCClass('AVCaptureDevice')
AVCaptureDeviceInput = ObjCClass('AVCaptureDeviceInput')
AVCaptureVideoDataOutput = ObjCClass('AVCaptureVideoDataOutput')
AVCaptureVideoPreviewLayer = ObjCClass('AVCaptureVideoPreviewLayer')

CMSampleBufferGetImageBuffer = c.CMSampleBufferGetImageBuffer
CMSampleBufferGetImageBuffer.argtypes = [c_void_p]
CMSampleBufferGetImageBuffer.restype = c_void_p

CVPixelBufferLockBaseAddress = c.CVPixelBufferLockBaseAddress
CVPixelBufferLockBaseAddress.argtypes = [c_void_p, c_int]
CVPixelBufferLockBaseAddress.restype = None

CVPixelBufferUnlockBaseAddress = c.CVPixelBufferUnlockBaseAddress
CVPixelBufferUnlockBaseAddress.argtypes = [c_void_p, c_int]
CVPixelBufferUnlockBaseAddress.restype = None

c.UIImagePNGRepresentation.argtypes = [c_void_p]
c.UIImagePNGRepresentation.restype = c_void_p
c.UIImageJPEGRepresentation.argtypes = [c_void_p, CGFloat]
c.UIImageJPEGRepresentation.restype = c_void_p

CIImage = ObjCClass('CIImage')
UIImage = ObjCClass('UIImage')

dispatch_get_current_queue = c.dispatch_get_current_queue
dispatch_get_current_queue.restype = c_void_p


class camera():
    
    def __init__(self, format='JPEG', save_to_album=True, return_Image=False):
        self._que = Queue()
        self.ciimage = None
        self._counter = 0
        self._captureFlag = 0
        self._isiPad = False
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.whiteWaiter = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self._saveAlbum = save_to_album
        self._fileformat = format
        self._autoclose = return_Image
        cannotSaveAlbumFormarts = ['PIL', 'CIImage', 'UIImage']
        if format in cannotSaveAlbumFormarts:
            self._saveAlbum = False

        self._init_mainview()

        print('init camera Settings')

        sampleBufferDelegate = create_objc_class(
            'sampleBufferDelegate',
            methods=[
                self.captureOutput_didOutputSampleBuffer_fromConnection_],
            protocols=['AVCaptureVideoDataOutputSampleBufferDelegate'])
        self._delegate = sampleBufferDelegate.new()

        self._session = AVCaptureSession.alloc().init()
        cameraTypes = ['AVCaptureDeviceTypeBuiltInTripleCamera', 'AVCaptureDeviceTypeBuiltInDualCamera',
                       'AVCaptureDeviceTypeBuiltInDualWideCamera', 'AVCaptureDeviceTypeBuiltInWideAngleCamera']

        self.cameraMaxZoom = [16, 16, 2, 2]
        self._defeaultZoom = [1.0, 0.5, 1.0, 0.5]
        self.typeNum = 0

        for camtype in cameraTypes:
            self.device = AVCaptureDevice.defaultDeviceWithDeviceType_mediaType_position_(
                camtype, 'vide', 0)
            _input = AVCaptureDeviceInput.deviceInputWithDevice_error_(
                self.device, None)
            if _input:
                self._session.addInput_(_input)
                print(camtype)
                break
            else:
                self.typeNum += 1

        else:
            print('Failed to create input')
            return

        self.device._setVideoHDREnabled_ = True
        self.device.isVideoHDREnabled = True
        self.device.isVideoStabilizationSupported = True
        self.device.isLensStabilizationSupported = True

        self._output = AVCaptureVideoDataOutput.alloc().init()
        queue = ObjCInstance(dispatch_get_current_queue())
        self._output.setSampleBufferDelegate_queue_(self._delegate, queue)
        self._output.alwaysDiscardsLateVideoFrames = True

        self._session.addOutput_(self._output)
        self._session.sessionPreset = 'AVCaptureSessionPreset3840x2160'

        prev_layer = AVCaptureVideoPreviewLayer.layerWithSession_(
            self._session)
        prev_layer.frame = ObjCInstance(self.mainView).bounds()
        prev_layer.setVideoGravity_('AVLayerVideoGravityResizeAspectFill')

        ObjCInstance(self.mainView).layer().addSublayer_(prev_layer)

        self._init_whitenView()
        self._init_shootbutton()
        self._init_latestPhotoView()
        self._init_savingPhotoView()
        self._init_openPhotoapp()
        self._init_closeButton()
        self._init_gestureView()
        self._init_zoomView()
        self._init_changeZoomButton()
        self._init_zoomLevelLabel()
        self._mettya_subView()

    def launch(self):
        print('Starting silent camera...')
        self._session.startRunning()
        self._changeZoom(self._defeaultZoom[self.typeNum])
        self.oldZoomScale = self._defeaultZoom[self.typeNum]
        self.currentZoomScale = self._defeaultZoom[self.typeNum]
        motion.start_updates()

        self.mainView.present(
            style='sheet', title_bar_color='black', hide_title_bar=True, orientations=['portrait'])
        self.mainView.wait_modal()

    def close(self):
        print('Stop running...')
        motion.stop_updates()
        self.mainView.close()
        self._session.stopRunning()
        self._delegate.release()
        self._session.release()
        self._output.release()

    def getData(self):
        return self.data

    def _pinchChange(self, recog):
        pinchZoomScale = recog.scale
        self.currentZoomScale = self.oldZoomScale - \
            (1-pinchZoomScale)*self.oldZoomScale

        if self.currentZoomScale <= 0.5:
            self.currentZoomScale = 0.5

        if self.currentZoomScale >= self.cameraMaxZoom[self.typeNum]:
            self.currentZoomScale = self.cameraMaxZoom[self.typeNum]

        self._changeZoom(self.currentZoomScale)

        if recog.state == 3:
            self.oldZoomScale = self.currentZoomScale

    def _changeZoom(self, scale):
        self.device.lockForConfiguration(None)
        self.device.videoZoomFactor = scale*2
        self.device.unlockForConfiguration()

        if self.typeNum == 1 or self.typeNum == 3:
            self.zoomLevelLabel.text = str('x{}'.format(round(scale*2, 1)))
            return scale

        self.zoomLevelLabel.text = str('x{}'.format(round(scale, 1)))
        return scale

    def _zoomAnimation(self, scale):
        d = scale - self.oldZoomScale
        s = 0

        for i in range(99):
            i += 1
            s = math.log(i)/math.log(100)*d+self.oldZoomScale
            self._changeZoom(s)
            time.sleep(0.001)

        return scale

    def _openPhotoapp(self, sender):
        self.mainView.close()
        webbrowser.open('photos-redirect://')
        exit()

    def _closeButton(self, sender):
        self.close()

    def _whiteWaiter(self):
        def animation():
            self.whitenView.alpha = 0.0
        ui.animate(animation, duration=0.2)

    def _button_tapped(self, sender):
        self.whitenView.alpha = 1.0
        self._captureFlag +=1
        #self._take_photo(self._que.qsize())
        self.executor.submit(self._take_photo,self._que.qsize())

    def _changeZoom_Button_tapped(self, sender):
        if self.oldZoomScale >= 2.0:
            i = self._zoomAnimation(0.5)
        elif self.oldZoomScale >= 1.0:
            if self.typeNum == 0 or self.typeNum == 1:
                i = self._zoomAnimation(2.0)
            else:
                i = self._zoomAnimation(0.5)
        elif self.oldZoomScale >= 0.5:
            i = self._zoomAnimation(1.0)
            self._changeZoom(1.2)
            self._changeZoom(1.0)

        self.oldZoomScale = i

    def _take_photo(self,size):
        while size == self._que.qsize():
            pass
        self.whiteWaiter.submit(self._whiteWaiter)
        self.savingPhotoView.alpha = 0.5

        # motion.start_updates()
        motionData = motion.get_gravity()
        # motion.stop_updates()
        
        roll, pitch, yaw = iOSMotionHandler.getAttitude(inDegrees=True)
        
        print("Roll: "+str(roll))
        print("Pitch:"+str(pitch))
        print("Yaw:  "+str(yaw))
        
        if motionData[0] >= 0.5:
            rot = 1
        elif motionData[0] <= -0.5:
            rot = 0
        else:
            rot = 3
        # delta = time.time() - self.shoot
        # print('shooted time:{}'.format(delta))
        ciimage = self._que.get()

        uiImg = UIImage.imageWithCIImage_scale_orientation_(ciimage, 1.0, rot)

        if self._fileformat == 'PNG':
            data = ObjCInstance(c.UIImagePNGRepresentation(uiImg.ptr))
            fmt = 'png'
        elif self._fileformat == 'CIImage':
            data = uiImg.CIImage()
        elif self._fileformat == 'UIImage':
            data = uiImg
        else:
            quality = 0.8
            data = ObjCInstance(c.UIImageJPEGRepresentation(uiImg.ptr, quality))
            fmt = 'jpg'

        if self._saveAlbum:
            temppath = self._saveData2temp(data,fmt)
            photos.create_image_asset(temppath)
            
            print("temppath:"+str(temppath))
            filename = temppath
            tag = "Roll"+str(roll)+";"+"Pitch"+str(pitch)+";"+"Yaw"+str(yaw)
            print(tag)
            ImageMetaDataHandler.setEXIF_Comment(fileNameImage=filename,comment="Hello this is inserted comment !")
            ImageMetaDataHandler.setEXIF_Tag(fileNameImage=filename,tag=tag)
            
            #-- Check Resulting Tag
            imgMetaHdl = ImageMetaDataHandler()
            imgMetaHdl.openImage(fileNameImage=filename)
            tag = imgMetaHdl.getEXIF_Tag()
            print("Tag:"+str(tag))

        if self._fileformat == 'PIL':
            temppath = self._saveData2temp(data,'pil')
            data = self._temp2pil(temppath)
            
        self._que.task_done()
        
        if self._autoclose:
            self.data = data
            time.sleep(1)
            self.close()
        
        if self._que.all_tasks_done:
            self.latestPhotoView.image = self._get_latest_photo_from_path(temppath)
            self.savingPhotoView.alpha = 0.0

        

    def _saveData2temp(self, data,fmt):
        today = datetime.datetime.now().strftime("%Y%m%d-%H%M-%f")
        temp_path = os.path.join(
            tempfile.gettempdir(), '{0}.{1}'.format(today, fmt))
        data.writeToFile_atomically_(temp_path, True)

        return temp_path

    def _pil2ui(self, imgIn):
        with io.BytesIO() as bIO:
            imgIn.save(bIO, 'PNG')
            imgOut = ui.Image.from_data(bIO.getvalue())
        del bIO
        return imgOut

    def _temp2pil(self, temppath):
        pilImg = Image.open(temppath)
        return pilImg

    def _get_latest_photo(self):
        all_assets = photos.get_assets()
        last_asset = all_assets[-1]
        img = last_asset.get_image()

        if img.width >= img.height:
            img = img.resize((100, round(img.height/img.width*100)))
        else:
            img = img.resize((round(img.width/img.height*100), 100))

        return self._pil2ui(img)
    
    def _get_latest_photo_from_path(self,path):

        img = Image.open(path)

        if img.width >= img.height:
            img = img.resize((100, round(img.height/img.width*100)))
        else:
            img = img.resize((round(img.width/img.height*100), 100))

        return self._pil2ui(img)

    def _rotateViewsAnimation(self):
        motionData = motion.get_gravity()
        # print(motionData)
        if motionData[0] >= 0.5:

            rad = math.pi/2*-1
        elif motionData[0] <= -0.5:
            rad = math.pi/2
        else:
            rad = 0

        def animation():
            self.zoomView.transform = ui.Transform.rotation(rad)
            self.latestPhotoView.transform = ui.Transform.rotation(rad)
        ui.animate(animation, duration=0.3)

    def captureOutput_didOutputSampleBuffer_fromConnection_(self, _self, _cmd, _output, _sample_buffer, *args):

        if self._isiPad == False:
            self._counter += 1
            if self._counter == 45:
                self._rotateViewsAnimation()
                self._counter = 0

        if self._captureFlag != 0:
            self._captureFlag-=1
            imagebuffer = CMSampleBufferGetImageBuffer(_sample_buffer)

            # バッファをロック
            CVPixelBufferLockBaseAddress(imagebuffer, 0)
            #self.ciimage = CIImage.imageWithCVPixelBuffer_(
                #ObjCInstance(imagebuffer))
            self._que.put(CIImage.imageWithCVPixelBuffer_(ObjCInstance(imagebuffer)))
            # バッファのロックを解放
            CVPixelBufferUnlockBaseAddress(imagebuffer, 0)
            #self._captureFlag = False
            
    
        

    def _init_mainview(self):
        self.mainView = ui.View()
        self.mainView.background_color = 'black'
        self.mainView.height = ui.get_screen_size()[0]*1.78
        self.mainView.width = ui.get_screen_size()[0]
        self.mainView.name = 'Silent Camera'

        if 'iPad' in platform.machine():  # overwrite
            self._isiPad = True
            self.mainView.height = ui.get_screen_size()[0]
            self.mainView.width = ui.get_screen_size()[0] / 1.78
            if ui.get_screen_size()[0] > ui.get_screen_size()[1]:
                self.mainView.height = ui.get_screen_size()[1]
                self.mainView.width = ui.get_screen_size()[1] / 1.78

    def _init_whitenView(self):
        print('init whitenView')
        self.whitenView = ui.View()
        self.whitenView.height = self.mainView.height
        self.whitenView.width = self.mainView.width
        self.whitenView.background_color = 'white'
        self.whitenView.alpha = 0.0

    def _init_shootbutton(self):
        print('init shootButton')
        self.shootButton = ui.Button()
        self.shootButton.flex = 'T'
        self.shootButton.width = 90
        self.shootButton.height = self.shootButton.width
        self.shootButton.center = (self.mainView.width*0.5,
                                   self.mainView.height*0.874)
        self.shootButton.action = self._button_tapped
        self.shootButton.background_image = ui.Image(
            'iow:ios7_circle_filled_256')

    def _init_latestPhotoView(self):
        print('init latestPhotoView')
        self.latestPhotoView = ui.ImageView()
        self.latestPhotoView.background_color = 'white'
        self.latestPhotoView.flex = 'T'
        self.latestPhotoView.height = 50
        self.latestPhotoView.width = self.latestPhotoView.height
        self.latestPhotoView.center = (
            self.mainView.width*0.14, self.mainView.height*0.872)
        self.latestPhotoView.image = self._get_latest_photo()

    def _init_savingPhotoView(self):
        print('init savingPhotoView')
        self.savingPhotoView = ui.ImageView()
        self.savingPhotoView.background_color = 'black'
        self.savingPhotoView.flex = 'T'
        self.savingPhotoView.height = 50
        self.savingPhotoView.width = self.savingPhotoView.height
        self.savingPhotoView.center = self.latestPhotoView.center
        self.savingPhotoView.image = ui.Image('iow:load_d_32')
        self.savingPhotoView.alpha = 0.0

    def _init_openPhotoapp(self):
        print('init openPhotoApp')
        self.openPhotoapp = ui.Button()
        self.openPhotoapp.flex = 'T'
        self.openPhotoapp.height = 50
        self.openPhotoapp.width = self.openPhotoapp.height
        self.openPhotoapp.center = self.latestPhotoView.center
        self.openPhotoapp.action = self._openPhotoapp

    def _init_closeButton(self):
        print('init closeButton')
        self.closeButton = ui.Button()
        self.closeButton.flex = 'RB'
        self.closeButton.center = (self.mainView.width*0.09,
                                   self.mainView.height*0.09)
        self.closeButton.image = ui.Image('iow:close_32')
        self.closeButton.height = 24
        self.closeButton.width = 24
        self.closeButton.tint_color = 'white'
        self.closeButton.action = self._closeButton

    def _init_gestureView(self):
        print('init gestureView')
        self.gestureView = ui.View()
        self.gestureView.multitouch_enabled = True
        self.gestureView.width = self.mainView.width
        self.gestureView.height = self.mainView.height
        Gestures.Gestures().add_pinch(self.gestureView, self._pinchChange)

    def _init_zoomView(self):
        print('init zoomView')
        self.zoomView = ui.View()
        self.zoomView.flex = 'T'
        self.zoomView.center = (self.mainView.width*0.88,
                                self.mainView.height*0.898)
        self.zoomView.height = 72
        self.zoomView.width = 72
        # self.zoomView.background_color='red'

    def _init_changeZoomButton(self):
        self.changeZoomButton = ui.Button()
        self.changeZoomButton.flex = 'WH'
        self.changeZoomButton.center = (self.zoomView.width*0,
                                        self.zoomView.height * 0)
        self.changeZoomButton.height = self.zoomView.height * 0.76
        self.changeZoomButton.width = self.zoomView.width
        self.changeZoomButton.action = self._changeZoom_Button_tapped
        self.changeZoomButton.image = ui.Image('iow:ios7_camera_32')
        self.changeZoomButton.tint_color = 'white'

        self.zoomView.add_subview(self.changeZoomButton)

    def _init_zoomLevelLabel(self):
        self.zoomLevelLabel = ui.Label()
        self.zoomLevelLabel.flex = 'LT'
        self.zoomLevelLabel.width = self.zoomView.width
        self.zoomLevelLabel.center = (self.zoomView.width*0.81,
                                      self.zoomView.height * 0.64)
        self.zoomLevelLabel.text = 'x1.0'
        self.zoomLevelLabel.text_color = 'white'
        self.zoomView.add_subview(self.zoomLevelLabel)
        self.zoomLevelLabel.font = ('DIN Alternate', 16)

    def _mettya_subView(self):
        print('add subViews')

        self.mainView.add_subview(self.gestureView)
        self.mainView.add_subview(self.zoomView)
        self.mainView.add_subview(self.whitenView)
        self.mainView.add_subview(self.shootButton)
        self.mainView.add_subview(self.closeButton)
        self.mainView.add_subview(self.openPhotoapp)
        self.mainView.add_subview(self.latestPhotoView)
        self.mainView.add_subview(self.savingPhotoView)


if __name__ == '__main__':
    camera(format='JPEG', save_to_album=True,
           return_Image=False).launch()


# usage example, if you import it

    # cam = muon.camera(format = 'JPEG',save_to_album=False,return_Image=True,auto_close = True)
    # cam.launch()
    # data = cam.getData()
    # print(data)
