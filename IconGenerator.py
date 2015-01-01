"""

.. module:: IconGenerator
   :platform: Unix,
   :synopsis: Module Description

.. moduleauthor:: Theodore Brown <TheoBrown0@gmail.com>

Created on Dec 31, 2014

"""
import cv2
import cv2.cv as cv
import numpy as np
from PyCV.ImageManipulation import showimg,save,resizeimg

class deviceAsset(object):
    def __init__(self,description,multiplier):
        self.description=description
        self.multiplier=multiplier
        

class iconAsset(object):
    def __init__(self):
        self.devices = []

def resizeImage(img,scale=1.0,shape=None):
    return cv2.resize(img,shape,interpolation=cv2.INTER_CUBIC)
    
def createIconSetForImage(imagePath):
    mainImage = cv2.imread(imagePath,-1)
    showimg(mainImage)
    icon = resizeImage(mainImage,shape= (180,180))
    save(icon,"180x180_th.png") 
    showimg(icon)
    
if __name__=="__main__":
    p6p=deviceAsset("iPhone 6 Plus (@3x)",3)
    p6=deviceAsset("iPhone 6 and iPhone 5 (@2x)",2)
    p4 = deviceAsset("iPhone 4s (@2x)",2)
    t1 = deviceAsset(" iPad and iPad mini (@2x)",2)
    t2 = deviceAsset("iPad 2 and iPad mini (@1x)",1)
    createIconSetForImage("playing_card_suits.png")