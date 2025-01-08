# Publishes an image service to a machine "myserver" from a folder of ortho images
# this code first author a mosaic dataset from the images, then publish it as an image service.
# A connection to ArcGIS Server must be established in the Catalog window of ArcMap
# before running this script

import arcpy, os, time, sys
import arceditor #this is required to create a mosaic dataset from images

# Define local variables:
ImageSource=r"\\myserver\data\SourceData\Portland"  # the folder of input images
MyWorkspace=r"\\myserver\Data\DemoData\ArcPyPublishing" # the folder for mosaic dataset and the service defintion draft file
GdbName="fgdb1.gdb"
GDBpath = os.path.join(MyWorkspace,GdbName) #File geodatabase used to store a mosaic dataset
Name = "OrthoImages"
Md = os.path.join(GDBpath, Name)
Sddraft = os.path.join(MyWorkspace,Name+".sddraft")
Sd = os.path.join(MyWorkspace,Name+".sd")
con = os.path.join(MyWorkspace, "arcgis on myserver_6080 (admin).ags")
SrsLookup = {
  'Mercator': "PROJCS['World_Mercator',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Mercator'],PARAMETER['False_Easting',0],PARAMETER['False_Northing',0],PARAMETER['Central_Meridian',0],PARAMETER['Standard_Parallel_1',0],UNIT['Meter',1]]",
  'WGS84': "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]]",
  'GZ4': "PROJCS['Germany_Zone_4',GEOGCS['GCS_Deutsches_Hauptdreiecksnetz',DATUM['D_Deutsches_Hauptdreiecksnetz',SPHEROID['Bessel_1841',6377397.155,299.1528128]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',4500000],PARAMETER['False_Northing',0],PARAMETER['Central_Meridian',12],PARAMETER['Scale_Factor',1],PARAMETER['Latitude_Of_Origin',0],UNIT['Meter',1]]",
  'GCS_NAD83': "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]]",
  'PUG': "PROJCS['PUG1',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1640416.666666667],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-87.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Foot_US',0.3048006096012192]]",
  'Florida_East': "PROJCS['NAD_1983_StatePlane_Florida_East_FIPS_0901_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.0174532925199432955]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',656166.6666666665],PARAMETER['False_Northing',0],PARAMETER['Central_Meridian',-81],PARAMETER['Scale_Factor',0.9999411764705882],PARAMETER['Latitude_Of_Origin',24.33333333333333],UNIT['Foot_US',0.304800609601219241]]",
  'SoCalNad83': "PROJCS['NAD_1983_StatePlane_California_V_FIPS_0405',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.0174532925199432955]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',2000000],PARAMETER['False_Northing',500000],PARAMETER['Central_Meridian',-118],PARAMETER['Standard_Parallel_1',34.03333333333333],PARAMETER['Standard_Parallel_2',35.46666666666667],PARAMETER['Latitude_Of_Origin',33.5],UNIT['Meter',1]]"
}

# First author a mosaic dataset from a folder of images
try:
    print("Creating fgdb")
    arcpy.CreateFileGDB_management(MyWorkspace, GdbName)

    print("Creating mosaic dataset")
    arcpy.CreateMosaicDataset_management(GDBpath, Name, SrsLookup['Mercator'], "", "", "NONE", "")

    print("Adding images to mosaic dataset") # also caculate cell size range, build boundary, and build overviews
    arcpy.AddRastersToMosaicDataset_management(Md, "Raster Dataset", ImageSource, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "UPDATE_OVERVIEWS", "#", "0", "1500", "#", "#", "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE")
except:
    print(arcpy.GetMessages()+ "\n\n")
    sys.exit("Failed in authoring a mosaic dataset")

# Create service definition draft
try:
    print("Creating SD draft")
    arcpy.CreateImageSDDraft(Md, Sddraft, Name, 'ARCGIS_SERVER', con, False, None, "Ortho Images","ortho images,image service")
except:
    print(arcpy.GetMessages()+ "\n\n")
    sys.exit("Failed in creating SD draft")

# Analyze the service definition draft
analysis = arcpy.mapping.AnalyzeForSD(Sddraft)
print("The following information was returned during analysis of the image service:")
for key in ('messages', 'warnings', 'errors'):
  print('----' + key.upper() + '---')
  vars = analysis[key]
  for ((message, code), layerlist) in vars.iteritems():
    print('    ', message, ' (CODE %i)' % code)
    print('       applies to:'),
    for layer in layerlist:
        print(layer.name),
    print()

# Stage and upload the service if the sddraft analysis did not contain errors
if analysis['errors'] == {}:
    try:
        print("Adding data path to data store to avoid data copy")
        arcpy.AddDataStoreItem(con, "FOLDER","Images",MyWorkspace,MyWorkspace)

        print("Staging service to create service definition")
        arcpy.StageService_server(Sddraft, Sd)

        print("Uploading the service definition and publishing image service")
        arcpy.UploadServiceDefinition_server(Sd, con)

        print("Service successfully published")
    except:
        print(arcpy.GetMessages()+ "\n\n")
        sys.exit("Failed to stage and upload service")
else:
    print("Service could not be published because errors were found during analysis.")
    print(arcpy.GetMessages())