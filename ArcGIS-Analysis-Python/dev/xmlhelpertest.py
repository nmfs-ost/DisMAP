# -*- coding: utf-8 -*-
# https://gis.stackexchange.com/questions/209324/editing-arcgis-metadata-elements-using-python

import importlib
import xmlhelper # make sure this is importable, if not use sys.path.append(r'path_to_module_parent_folder') first
importlib.reload(xmlhelper); del importlib # force reload of the module
from os.path import join
from time import time, localtime, strftime
import glob

#ws    = r"./April 1 2023/Export Metadata"
ws    = r"./April 1 2023/ArcGIS Metadata"
local_time = localtime()



# That's where you would want to use the .iterTags('linkage') method. This will
# iterate over all of the linkage tags. You can also take advantage of the kwargs
# argument (keyword arguments) to further narrow down the search on one or more elements.
# For example, if you had two linkage elements who had a type property with
# different values, you could find the find the first like this:
# doc.getElm('linkage', type='Type A') and the second the same way:
# doc.getElm('linkage', type='Type B'). Most of the selectors use that same
# kwargs option, so you could use it with iterTags() too. –

# find all metadata files in path
for f in glob.glob(join(ws, '*.xml')):

    # user wrapper here
    doc = xmlhelper.BaseXML(f)

    # ###--->>> Esri
    # Get the CreaDate
    CreaDate = doc.getElm("CreaDate")
    CreaDate.text = "20230401"
    del CreaDate

    # Get the CreaTime
    CreaTime = doc.getElm("CreaTime")
    CreaTime.text = "00000000"
    del CreaTime

##    # Get SyncDate (update revise) 'mod' date
##    SyncDate = doc.getElm("SyncDate")
##    #SyncDate.text = strftime("%Y%m%d", local_time)
##    SyncDate = "20230401"
##    del SyncDate

    # Get SyncTime
    SyncTime = doc.getElm("SyncTime")
    #SyncTime.text = strftime("%H:%M:%S", local_time)
    SyncTime = "00000000"
    del SyncTime

##    # Get ModDate (update revise) 'mod' date
##    ModDate = doc.getElm("ModDate")
##    #ModDate.text = strftime("%Y%m%d", local_time)
##    #ModDate.text = "20230401"
##    del ModDate

    # Get ModTime
    ModTime = doc.getElm("ModTime")
    #ModTime.text = strftime("%H:%M:%S", local_time)
    ModTime = "00000000"
    del ModTime

    # ###--->>> Esri

    # ###--->>> dataIdInfo

    # Get pubDate
    pubDate = doc.getElm("pubDate")
    #pubDate.text = strftime("%H:%M:%S", local_time)
    pubDate.text = "2023-04-01T00:00:00"
    del pubDate

    # ###--->>> dataIdInfo


    # Get mdDateSt (edition date) and set it
    mdDateSt = doc.getElm("mdDateSt")
    #mdDateSt.text = strftime("%Y%m%d", local_time)
    mdDateSt.text = "20230401"
    del mdDateSt

    #tags = doc.iterTags("attr")
    #print(tags.)

    # update title
    # title = doc.getElm("resTitle")  # should be the same, regardless of shapefile?

    # may want to be a little more explicit with if statement here....
    # if f.endswith("A.shp.xml"):
    #     title.text = "MCMS (polygon)"
    # elif f.endswith("Zones.shp.xml"):
    #     title.text = "MCMS Exclusion Zones"

    # save it
    doc.save()

del ws #, local_time

print('done')