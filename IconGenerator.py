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
from PyCV.ImageManipulation import newShowImg,save,resizeimg,getShape,makeCImg
from PyUtils.csvHandler import csvHandler

class iconCatalog(object):
    """tracks each iOS device type with specifications for image asset types
    Parameters:
        name - project identifier
        devices - 
        
    """
    def __init__(self,name):
        self.name = name
        self.devices = dict()
        self.sourceImages = dict()
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
        """adds iconDetail objects to deviceAsset objects
        """
        iconTypes = self.parseIconTypes(iconData.keys())
        for device in self.devices.itervalues():
            for icon in iconTypes:
                specificIcon = copy.deepcopy(icon)
                sizeDetail= iconData[specificIcon.description][device.position]
                iconDetails=self.parseIconSizeDetail(sizeDetail)
                specificIcon.setIconDetail(iconDetails)
                device.addIcon(specificIcon)


            
    def parseIconSizeDetail(self,detailString):
        """ method to get icon size attributes from apples table in csv format
        Returns array of iconDetailObjectcs for each specification per device icon
        
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



class deviceAsset(object):
    """Stores specification about each device
    Parameters:
        name - device name (iphone 6)
        description - full device specification string
        multiplier - icon resolution id (@2)
        icons - dict of icon assets 
    """
    def __init__(self,description,multiplier,position):
        self.name = description
        self.description=description
        self.multiplier=multiplier
        self.position = position
        self.icons = dict()
    def addIcon(self,icon):
        self.icons[icon.name]=icon
        
class iconAsset(object):
    """a type of image used by an ios device
    e.g. app icon, launch image, appstore icon, etc
    
    Parameters:
        keystring- the description of the icon which is parsed to determine the icons name and if its required or not
    """
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
        self.needsImage = False
#         print self.name,self.importance,self.level
        
    def setSize(self,sizeObject):
        self.size = sizeObject
        
    def setIconDetail(self,detailArray):
        """details of this icon class such as its size-and iconDetail object
        """
        self.iconDetails=detailArray
        if len(detailArray) >1:
            self.multipleConfigs = True
        else: 
            self.detail = detailArray[0]
        for item in self.iconDetails:
            if item.size != None:
                self.needsImage=True

class iconDetail(object):
    """specifications for the image attributes of an icon
    if size is None this icon is not an image
    """
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
        self.image = None
        
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


def resizeImage(img,shape=None):
    return cv2.resize(img,shape,interpolation=cv2.INTER_CUBIC)

def createIconSetForImage(imagePath):
    mainImage = cv2.imread(imagePath,-1)
    newShowImg(mainImage)
    icon = resizeImage(mainImage,shape= (180,180))
    save(icon,"180x180_th.png") 
    newShowImg(icon)
    
def extractBracketsFromString(someString,returnSplitString = False):
    if ("(" in someString) and (")" in someString):
        content = someString.split("(")[-1].split(")")[0]
        print content
        return content
    else:
        return None

def createIconSets():
    csvPath="appStoreIcons.csv"
    keys = list()
    csvH = csvHandler(keys, mode='r', outputfile=None, inputfile = csvPath, buffers = None) 
    headers = csvH.readFirstLine()
    data = csvH.readDataWithRowHeaders()
    
    icSet = iconCatalog("videoEditor")
    deviceClasses = headers[1:]
    deviceSizes = [extractBracketsFromString(x) for x in deviceClasses]
    index=0
    for device,mult in zip(deviceClasses,deviceSizes):
        deviceObj = deviceAsset(device,mult,index)
        icSet.addDevice(deviceObj)
        index+=1
        
    icSet.addIconRequirements(data)
    print '##################################################'
    icSet.makeIconsSet("Farmeral_video-icon.png")
    print 'All Icons SuccwhiteImgesfuly Created'

    return icSet

#     icSet.debugGroup()
#     icSet.parseIcons()
def blankAlphaChannel(src,dst):
    mainImage=src
    x,y,z=getShape(mainImage)
    whiteImg=makeCImg(x, y)

    b,g,r,a = cv2.split(mainImage)
    for i in range(x):
        for j in range(y):
            if a[i,j]==255:
                whiteImg[i,j]=mainImage[i,j][:3]#copy color channels
            elif a[i,j]==0:
                whiteImg[i,j]=[255,255,255] #blank out transparency with white pixels
    return whiteImg

def changeBackgroundColor(imagePath):
    mainImage = cv2.imread(imagePath,-1)
    newShowImg(mainImage,'start')
    x,y,z=getShape(mainImage)

    whiteImg=makeCImg(x, y)
    newImg=blankAlphaChannel(mainImage,whiteImg)



    newShowImg(newImg, 'corrected 22 ')

    newShowImg(whiteImg, 'corrected')
#     white2 = cv2.cvtColor(whiteImg,cv2.COLOR_BGR2BGRA)
#     newShowImg(white2,'bgra')
#     pp(whiteImg[0,0])
#     pp(white2[0,0])
# 
#     pp(mainImage[0,0])
# 
#     fromTo=( 0,0, 1,1, 2,2, 3,3)
#     np.asarray(fromTo)
#     cv2.mixChannels(mainImage,white2,[(1,0)])
# #     whiteImg[:,:,:]=mainImage
#     newShowImg(whiteImg, 'blank')
#     save(icon,"180x180_th.png") 
if __name__=="__main__":
    path = "Farmeral_video-icon.png"
    path = "playing_card_suits.png"
    changeBackgroundColor(path)
#     mySet = createIconSets()
