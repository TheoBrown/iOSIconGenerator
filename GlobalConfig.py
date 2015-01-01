import sys
from os import getcwd
import socket

hostname = socket.gethostname()





logLevel = 'info'
consoledbg = 'warning'

rootpath = getcwd()
sys.path.append(rootpath)
datapath = rootpath + '/Data/'
logpath = rootpath + '/Logs/'
imgpath = rootpath + '/img/'
resultpath = datapath + 'Results/'
blobpath = imgpath + 'blobs/'

testpath = resultpath #placeholder to be set
#Note = rootlog only goes to steam above warning, dunno why
datadir = {'dtDeskMNT':{'db':'iReport',
                     'picklepath':'/var/www/iReport/data/',
                     'debug':True
                     },
        'li614-103':{'db':'Diagnostics', 
                     'picklepath' : '/var/www/remoteProcessor/data/',
                    'debug':False

                     },
        'dante-EX58-UD4P':{'db':'Diagnostics', 
                     'picklepath' : '/var/www/remoteProcessor/data/',
                    'debug':True

                     }
        }




database = datadir[hostname]['db']
picklepath = datadir[hostname]['picklepath']
isDebug = datadir[hostname]['debug']
