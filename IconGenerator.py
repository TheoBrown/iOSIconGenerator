"""

.. module:: IconGenerator
   :platform: Unix,
   :synopsis: Module Description

.. moduleauthor:: Theodore Brown <TheoBrown0@gmail.com>

Created on Dec 31, 2014

"""
from pprint import pprint as pp

import cv2
import cv2.cv as cv
import numpy as np
from PyCV.ImageManipulation import showimg,save,resizeimg
from PyUtils.csvHandler import csvHandler

class iconCatalog(object):
    def __init__(self,name):
        self.name = name
        self.devices = dict()

    def addDevice(self,device):
        self.devices[device.name]= device
        
    def parseIconTypes(self,iconDataKeys):
        iconClasses = []
        for key in iconDataKeys:
            iconInfo = iconAsset(key)
            iconClasses.append(iconInfo)
        return iconClasses
            
    def addIconRequirements(self,iconData):
        iconTypes = self.parseIconTypes(iconData.keys())
        pp(iconTypes)
        for device in self.devices.itervalues():
            for icon in iconTypes:
#                 pp(iconData[icon.description])
#                 print device.position
                sizeDetail= iconData[icon.description][device.position]
                (w,h)=self.parseIconSizeDetail(sizeDetail)
                icon.setSize(size(w,h))
                device.addIcon(icon)
            
    def parseIconSizeDetail(self,detailString):
        detailLines = detailString.strip().split('\n')
        pp(detailLines)
        h = 0
        w = 0
        if len(detailLines) ==1:
            detail = detailLines[0]
            if 'about' in detail.lower():
            values = detail.split(' x ')
            w = int(values[0])
            h=int(values[1])
        return (w,h)
   

class deviceAsset(object):
    def __init__(self,description,multiplier,position):
        self.name = description
        self.description=description
        self.multiplier=multiplier
        self.position = position
        self.icons = dict()
    def addIcon(self,icon):
        self.icons[icon.name]=icon
        
class iconAsset(object):
    _levels = ["optional","recommended","required"]
    
    def __init__(self,keyString):
        self.description=keyString
        for level in self._levels:
            if level in self.description:
                self.importance=level
#         self.importance=extractBracketsFromString(keyString)
        self.level =self._levels.index(self.importance)
        self.name = self.description.split("("+self.importance+")")[0]
#         print self.name
#         print self.name,self.level,self.importance
        print self.name,self.importance,self.level
        
    def setSize(self,sizeObject):
        self.size = sizeObject
    def setIconDetail(self,detail):
        self.size = detail.size
        self.details = detail

class iconDetail(object):
    def __init__(self,size,importance=None,notes=None):
        self.size=size
        self.importance=importance
        self.notes=notes
        
class size(object):
    def __init__(self,height,width):
        self.height=height
        self.width=width
        self.x=width
        self.y=height
#------------------------------------------------------------------------------ Helpers

def extractBracketsFromString(someString,returnSplitString = False):
    if ("(" in someString) and (")" in someString):
        content = someString.split("(")[-1].split(")")[0]
        print content
        return content
    else:
        return None
    

def resizeImage(img,scale=1.0,shape=None):
    return cv2.resize(img,shape,interpolation=cv2.INTER_CUBIC)

def loadAssetDataCSV(csvPath):
    keys = list()
    csvH = csvHandler(keys, mode='r', outputfile=None, inputfile = csvPath, buffers = None) 
    columnHeaders = csvH.readFirstLine()
    csvData = csvH.readDataWithRowHeaders()
    return columnHeaders,csvData

def createIconSetForImage(imagePath):
    mainImage = cv2.imread(imagePath,-1)
    showimg(mainImage)
    icon = resizeImage(mainImage,shape= (180,180))
    save(icon,"180x180_th.png") 
    showimg(icon)
    

    

        
def organizeIconRequirementData(dataHeader,data):
    deviceClasses = dataHeader[1:]
    deviceSizes = [extractBracketsFromString(x) for x in deviceClasses]
    devices = []
    index=0
    for device,mult in zip(deviceClasses,deviceSizes):
        devices.append(deviceAsset(device,mult,index))
        index+=1
    return devices

def createIconSets():
    csvPath="appStoreIcons.csv"
    headers,data = loadAssetDataCSV(csvPath)
    icSet = iconCatalog("texasHoldem")
    devices = organizeIconRequirementData(headers,data)
    for device in devices:
        icSet.addDevice(device)
    print headers
    pp(data)
    icSet.addIconRequirements(data)
#     icSet.parseIcons()
if __name__=="__main__":
    createIconSets()

#     p6p=deviceAsset("iPhone 6 Plus (@3x)",3)
#     p6=deviceAsset("iPhone 6 and iPhone 5 (@2x)",2)
#     p4 = deviceAsset("iPhone 4s (@2x)",2)
#     t1 = deviceAsset(" iPad and iPad mini (@2x)",2)
#     t2 = deviceAsset("iPad 2 and iPad mini (@1x)",1)
#     createIconSetForImage("playing_card_suits.png")