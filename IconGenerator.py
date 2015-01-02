"""

.. module:: IconGenerator
   :platform: Unix,
   :synopsis: Module Description

.. moduleauthor:: Theodore Brown <TheoBrown0@gmail.com>

Created on Dec 31, 2014

"""
from os import mkdir
# from sys.path import join
from os.path import join,exists
from pprint import pprint as pp
import re
import cv2
import cv2.cv as cv
import numpy as np
import copy
from PyCV.ImageManipulation import showimg,save,resizeimg
from PyUtils.csvHandler import csvHandler

class iconCatalog(object):
    def __init__(self,name):
        self.name = name
        self.devices = dict()
        
    def makeIconsSet(self,image):
        sourceImg = cv2.imread(image)
        dirName = "%s iconSet" %self.name
        if not exists(dirName): mkdir(dirName)
        for device in self.devices.itervalues():
            deviceDirName = device.name.replace(" ","_")
            deviceDir = join(dirName,deviceDirName)
#             mkdir(deviceDir)
            if not exists(deviceDir): mkdir(deviceDir)

            for icon in device.icons.itervalues():
                if icon.multipleConfigs == False:
                    if icon.detail.size != None:
                        imgName="%s_%s_(%dx%d).png"%(icon.name,device.name,icon.detail.size.height,icon.detail.size.width)
                        print imgName,icon.detail.size.getTup()
                        resizedImg=resizeImage(sourceImg, shape=icon.detail.size.getTup())
                        imgPath = deviceDir+"/"+imgName
                        save(resizedImg, imgPath)
                else: pass
                
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
                specificIcon = copy.deepcopy(icon)
                sizeDetail= iconData[specificIcon.description][device.position]
                iconDetails=self.parseIconSizeDetail(sizeDetail)
                specificIcon.setIconDetail(iconDetails)
                device.addIcon(specificIcon)
#                 icon.setSize(size(w,h))
#                 device.addIcon(icon)
    def debugGroup(self):
        for device in self.devices.itervalues():
            for icon in device.icons.itervalues():
                print device.name,icon.name
                if icon.detail!=None: print icon.detail.size.debug()
            
    def parseIconSizeDetail(self,detailString):
        """
        data details
        if singe line:
            /d[2-4] ' x ' /d[2-4]
            'About ' ^
            ^ /(maximum: /d/d x /d/d/)
        if multi lines:
            /d[2-4] ' x ' /d[2-4] (/(portrait/) | (/(landscape/)) 
        """
        detailArray = []
#         iconDetailItem = iconDetail(detailString)
        detailLines = detailString.strip().split('\n')
        
#         pp(detailLines)
        h = 0
        w = 0
#         if len(detailLines) ==1:
        
        for detailLine in detailLines:
#             print "LINE: %s" %detailLine
            detail = detailLine.strip()
            iconDetailItem = iconDetail(detail)
            p = re.compile('^(\d{2,5})( x )(\d{2,5})$')
            m = p.match(detail)
            if m !=None:
                iconDetailItem.importance="absolute"
#                 print m.group(1),m.group(2),m.group(3)
                iconDetailItem.size = size(m.group(1),m.group(3))
                detailArray.append(iconDetailItem)
            elif re.compile('^(\d{2,5})( x )(\d{2,5}).\((portrait|landscape)\)$',re.IGNORECASE).match(detail)!= None:
                match=re.compile('^(\d{2,5})( x )(\d{2,5}).\((portrait|landscape)\)$',re.IGNORECASE).match(detail)
                iconDetailItem.importance="approximate"
                iconDetailItem.size = size(match.group(1),match.group(3))
                iconDetailItem.orientation=match.group(4)
#                 print iconDetailItem.orientation
                detailArray.append(iconDetailItem)
            elif re.compile('^.*(iPhone \d).*$',re.IGNORECASE).match(detail)!= None:
                match = re.compile('^.*(iPhone \d)(.*)$',re.IGNORECASE).match(detail)
                iconDetailItem.device=match.group(1)
                if re.compile('^.*(\d{2,5})( x )(\d{2,5})$').match(match.group(2)) != None:
                    sizeMatch= re.compile('^.*(\d{2,5})( x )(\d{2,5})$').match(match.group(2))
                    iconDetailItem.size=size(sizeMatch.group(1),sizeMatch.group(3))
                detailArray.append(iconDetailItem)
#                 print match.group(2)
            elif re.compile('^(about.)(\d{2,5})( x )(\d{2,5})$',re.IGNORECASE).match(detail) != None: #not simple string
                mod = re.compile('^(about.)(\d{2,5})( x )(\d{2,5})$',re.IGNORECASE)
                m =mod.match(detail) 
                iconDetailItem.importance="approximate"
                iconDetailItem.size = size(m.group(2),m.group(4))
                detailArray.append(iconDetailItem)
            elif re.compile('^(about.)(\d{2,5})( x )(\d{2,5}).\(maximum:.(\d{2,5})( x )(\d{2,5})\)$',re.IGNORECASE).match(detail) != None:
                mod2 = re.compile('^(about.)(\d{2,5})( x )(\d{2,5}).\(maximum:.(\d{2,5})( x )(\d{2,5})\)$',re.IGNORECASE)
                m2 = mod2.match(detail)
                iconDetailItem.importance="approximate"
                iconDetailItem.size = size(m2.group(2),m2.group(4))
                iconDetailItem.maxSize=size(m2.group(5),m2.group(7))
                detailArray.append(iconDetailItem)
            else:
#                 print detail,"no matching expression found"
                detailArray.append(iconDetailItem)
        return detailArray
    
    def extractIconDetail(self,string,iconDetailItem):
        
        if "about" in string.lower():
            iconDetailItem.importance = "approximate"
        else:
            iconDetailItem.importance = "absolute"
        p = re.compile('^(\d{2,5})( x )(\d{2,5})$')
        m = p.match(string)
#         p = re.search(r'^(\d+)( x )(\d+)$',string)
        if m !=None: print "only number %s" %m.group(1)
        
#         p = re.search(r'\(.*\)',string)
#         if p !=None: print "brackets  %s" %p.group()

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
        self.iconDetails = []
        self.detail=None
        self.multipleConfigs=False
#         print self.name,self.importance,self.level
        
    def setSize(self,sizeObject):
        self.size = sizeObject
    def setIconDetail(self,detailArray):
        self.iconDetails=detailArray
        if len(detailArray) >1:
            self.multipleConfigs = True
        else: self.detail = detailArray[0]

class iconDetail(object):
    _levels = ["approximate","absolute"]

#    def __init__(self,size,maxsize = None,device=None,orientation=None,importance=None,notes=None):

    def __init__(self,fullDetail):
        self.details = fullDetail
        self.size=None
        self.maxSize=None
        self.importance=None #can be "approximate" or "absolute"
        self.notes=None
        self.device=None #phone version if specified
        self.orientation =None#orientation (portrait/landscape) if specified
        
class size(object):
    def __init__(self,height,width):
        self.height=int(height)
        self.width=int(width)
        self.x=self.height
        self.y=self.width
    def getTup(self):
        return (self.x,self.y)
    def debug(self):
        return "x:%d y:%d" %(self.height,self.width)
#------------------------------------------------------------------------------ Helpers
def testRE(string):
#     print string
    p = re.search(r'\d+( x )\d+',string)
    if p !=None: print p.group()

    p = re.search(r'\(.*\)',string)
    if p !=None: print p.group()
    
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
    print '##################################################'
    return icSet
#     icSet.debugGroup()
#     icSet.parseIcons()
if __name__=="__main__":
    mySet = createIconSets()
#     for device in mySet.devices.itervalues():
#         for icon in device.icons.itervalues():
#             if icon.multipleConfigs == False:
#                 if icon.detail.size != None:
#                     imgName="%s_%s_(%dx%d)"%(icon.name,device.name,icon.detail.size.height,icon.detail.size.width)
#                     print imgName
#             else: pass
    mySet.makeIconsSet("playing_card_suits.png")
#     p6p=deviceAsset("iPhone 6 Plus (@3x)",3)
#     p6=deviceAsset("iPhone 6 and iPhone 5 (@2x)",2)
#     p4 = deviceAsset("iPhone 4s (@2x)",2)
#     t1 = deviceAsset(" iPad and iPad mini (@2x)",2)
#     t2 = deviceAsset("iPad 2 and iPad mini (@1x)",1)
#     createIconSetForImage("playing_card_suits.png")