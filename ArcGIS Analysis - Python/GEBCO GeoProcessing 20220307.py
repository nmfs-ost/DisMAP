#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     29/10/2021
# Copyright:   (c) john.f.kennedy 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from __future__ import print_function
import os
import arcpy
from time import time, localtime, strftime, sleep, gmtime

def main():
    try:
        function = "main"
        # Set a start time so that we can see how log things take
        start_time = time()

        # Get workspace
        tmp_workspace = arcpy.env.workspace
        # Change workspace to direcory
        arcpy.env.workspace = GEBCO_DIRECTORY


        # Gulf of Mexico   = N 31 W -98 S 18 E -79   - GOM
        # East Coast       = N 46 W -82 S 25 E -65   - NEUS_F, NEUS_S, SEUS_SPR, SEUS_SUM, SEUS_FALL
        # West Coast       = N 50 W -130 S 29 E -118 - WC_ANN, WC_TRI
        # Aleutian Islands = N 57 W 163 S 47 E 197   - AI
        # Gulf of Alaska   = N 64 W -167 S 50 E -123 - GOA
        # East Bering Sea  = N 67 W 175 S 52 E 204   - EBS

##        gebco_dict = {
##                      'gebco_2021_n31.0_s18.0_w-98.0_e-79.0.asc' : 'Gulf of Mexico',
##                      'gebco_2021_n46.0_s28.0_w-84.0_e-64.0.asc' : 'East Coast',
##                      'gebco_2021_n50.0_s35.0_w-131.0_e-117.0.asc' : 'West Coast',
##                      'gebco_2021_n57.0_s47.0_w163.0_e197.0.asc' : 'Aleutian Islands',
##                      'gebco_2021_n64.0_s50.0_w-167.0_e-123.0.asc' : 'Gulf of Alaska',
##                      'gebco_2021_n67.0_s52.0_w175.0_e204.0.asc' : 'East Bering Sea',
##                     }

##        gebco_srs = {
##                     'Aleutian Islands' : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Aleutian Islands
##                     'East Bering Sea'  : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Eastern Bering Sea
##                     'Gulf of Alaska'   : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Gulf of Alaska
##                     'West Coast'       : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # West Coast
##                     'East Coast'       : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Gulf of Mexico
##                     'Gulf of Mexico'   : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Southeast US
##                    }

        gebco_srs = {
                     #'AI'        : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Aleutian Islands
                     #'EBS'       : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Eastern Bering Sea
                     #'GOA'       : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Gulf of Alaska
                     'GOM'       : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Southeast US
                     'NEUS_F'    : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Gulf of Mexico
                     'NEUS_S'    : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Gulf of Mexico
                     'SEUS_FALL' : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Gulf of Mexico
                     'SEUS_SPR'  : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Gulf of Mexico
                     'SEUS_SUM'  : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Gulf of Mexico
                     'WC_ANN'    : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # West Coast
                     'WC_TRI'    : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # West Coast

                    }

##        dismap_dict = {
##                       'AI' : 'Aleutian Islands',
##                       'EBS' : 'East Bering Sea',
##                       'GOA' : 'Gulf of Alaska',
##                       'GOM' : 'Gulf of Mexico',
##                       'NEUS_F' : 'East Coast',
##                       'NEUS_S' : 'East Coast',
##                       'SEUS_SPR' : 'East Coast',
##                       'SEUS_SUM' : 'East Coast',
##                       'SEUS_FALL' : 'East Coast',
##                       'WC_ANN' : 'West Coast',
##                       'WC_TRI' : 'West Coast',
##                      }

        dismap_dict = {
                       #'AI' : 'gebco_2021_n64.0_s46.0_w164.0_e196.0.asc',
                       #'EBS' : 'gebco_2021_n67.0_s52.0_w-180.0_e-157.0.asc',
                       #'GOA' : 'gebco_2021_n70.0_s42.0_w-171.0_e-131.0.asc',
                       'GOM' : 'gebco_2021_n34.0_s20.0_w-99.0_e-79.0.asc',
                       'NEUS_F' : 'gebco_2021_n46.0_s28.0_w-84.0_e-64.0.asc',
                       'NEUS_S' : 'gebco_2021_n46.0_s28.0_w-84.0_e-64.0.asc',
                       'SEUS_FALL' : 'gebco_2021_n46.0_s28.0_w-84.0_e-64.0.asc',
                       'SEUS_SPR' : 'gebco_2021_n46.0_s28.0_w-84.0_e-64.0.asc',
                       'SEUS_SUM' : 'gebco_2021_n46.0_s28.0_w-84.0_e-64.0.asc',
                       'WC_ANN' : 'gebco_2021_n50.0_s35.0_w-131.0_e-117.0.asc',
                       'WC_TRI' : 'gebco_2021_n50.0_s35.0_w-131.0_e-117.0.asc',
                      }

        # Get a list of rasters to process
        rasters = [r for r in arcpy.ListRasters() if r in dismap_dict.values()]

        regions = dismap_dict.keys()

        # Loop through rasters
        for region in regions:
            # Print raster name
            print(region)
            msg = "> ProjectRaster_management"
            print(msg); del msg
            gebco_raster = os.path.join(GebcoGDB, "{}_GEBCO".format(region))
            #region_snap_raster = os.path.join(ProjectGDB, region+'_Snap_Raster')
            #arcpy.env.snapRaster = region_snap_raster
            #arcpy.env.mask = region_snap_raster
            # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
            #arcpy.env.extent = arcpy.Describe(region_snap_raster).extent
            #arcpy.env.cellSize = "MINOF"
            #arcpy.env.resamplingMethod = "NEAREST"

            arcpy.management.BuildPyramids(in_raster_dataset=dismap_dict[region], pyramid_level="-1", SKIP_FIRST="NONE", resample_technique="NEAREST", compression_type="DEFAULT", compression_quality="75", skip_existing="OVERWRITE")

            # ProjectRaster_management
            #arcpy.ProjectRaster_management(in_raster = dismap_dict[region], out_raster = gebco_raster+'_tmp', out_coor_system = gebco_srs[region], resampling_type="NEAREST", cell_size="", geographic_transform="", Registration_Point="", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", vertical="NO_VERTICAL")
            arcpy.management.ProjectRaster(in_raster = dismap_dict[region], out_raster = gebco_raster, out_coor_system = gebco_srs[region], resampling_type="NEAREST", cell_size="", geographic_transform="", Registration_Point="", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", vertical="NO_VERTICAL")
            #arcpy.gp.Times_sa(gebco_raster+'_tmp', "1.0", gebco_raster)
            #arcpy.Delete_management(gebco_raster+'_tmp')
            arcpy.management.BuildPyramids(in_raster_dataset=gebco_raster, pyramid_level="-1", SKIP_FIRST="NONE", resample_technique="NEAREST", compression_type="DEFAULT", compression_quality="75", skip_existing="OVERWRITE")
            msg = arcpy.GetMessages()
            msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
            print(msg); del msg
            #print(gebco_dict[raster])
            #print(gebco_srs[gebco_dict[raster]])
            msg = arcpy.GetMessages()
            msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
            print(msg); del msg
            del gebco_raster
            #del region_snap_raster
        del regions


        # Change workspace
        arcpy.env.workspace = GebcoGDB

        for region in dismap_dict:
            print(region)
            gebco_raster = os.path.join(GebcoGDB, "{}_GEBCO".format(region))
            if arcpy.Exists(gebco_raster):
                #region_snap_raster = os.path.join(ProjectGDB, region+'_Snap_Raster')
                #arcpy.env.snapRaster = region_snap_raster
                #arcpy.env.mask = region_snap_raster
                # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
                #arcpy.env.extent = arcpy.Describe(region_snap_raster).extent
                #arcpy.env.cellSize = "MINOF"
                #arcpy.env.resamplingMethod = "NEAREST"

                region_bathymetry = "{0}_Bathymetry".format(region)
                #arcpy.gp.SetNull_sa(gebco_raster, gebco_raster, region_bathymetry, "Value > 0.0")
                tmp_grid = arcpy.sa.SetNull(gebco_raster, gebco_raster, "Value >= 0.0")
                tmp_grid.save(region_bathymetry)
                del tmp_grid
                msg = arcpy.GetMessages()
                msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
                print(msg)

                arcpy.management.BuildPyramids(in_raster_dataset=region_bathymetry, pyramid_level="-1", SKIP_FIRST="NONE", resample_technique="NEAREST", compression_type="DEFAULT", compression_quality="75", skip_existing="OVERWRITE")
                msg = arcpy.GetMessages()
                msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
                print(msg)

                arcpy.management.Copy(region_bathymetry, os.path.join(BathymetryGDB, "{0}_Bathymetry".format(region)))
                msg = arcpy.GetMessages()
                msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
                print(msg)


            del region, gebco_raster, region_bathymetry

        # Revert workspace
        arcpy.env.workspace = tmp_workspace
        del tmp_workspace
        del gebco_srs
        del dismap_dict

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"\n#-> Elapsed Time for {0} {1} (H:M:S)\n".format(function, strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        localKeys =  [key for key in locals().keys() if key not in ['function']]

        if localKeys:
            msg = "#-> Local Keys in function {0}: {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo


if __name__ == '__main__':
    try:
        # Set a start time so that we can see how log things take
        start_time = time()

        # Write a message to the log file
        msg = "STARTING PROGRAM ON {}".format(strftime("%a %b %d %I:%M:%S %p", localtime()))
        print(msg)

        # This is a list of local and global variables that are exclude from
        # lists of variables
        exclude_keys = ['arcgis', 'arcpy', 'date', 'datetime', 'exclude_keys', 'main', 'math',
                        'numpy', 'np', 'os', 'pd', 'sys', 'time', 'localtime',
                        'strftime', 'sleep', 'gmtime', 'shutil', 'scipy',
                        'stats', 'copysign', "logging", "MakeInt", "getDate",
                        "removeSpaces"]

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"
        ##!!WARNING!!:::::::SET THE OVERWRITE TO ON - ANY ITEMS THAT GET SAVED WILL BE OVERWRITTEN
        arcpy.env.overwriteOutput = True
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011;WGS_1984_(ITRF00)_To_NAD_1983"
        #
        arcpy.env.pyramid = "PYRAMIDS -1 CUBIC DEFAULT 75 NO_SKIP"
        arcpy.env.cellSizeProjectionMethod = "PRESERVE_RESOLUTION"
        # Use the minimum value of the data at the coincident location.
        arcpy.env.coincidentPoints = "INCLUDE_ALL"
        # Set the resampling method environment to bilinear interpolation
        arcpy.env.resamplingMethod = "NEAREST"
        # Set the raster statistics
        arcpy.env.rasterStatistics = "STATISTICS 1 1"
        # Statistics using a skip factor of 100 for x and y, and
        # ignore values of 0 and 255
        #arcpy.env.rasterStatistics = 'STATISTICS 100 100 (0 255)'
        # Set the cell size environment using a number. In this case 10,000 m
        #cell_size = 2000
        #arcpy.env.cellSize = cell_size
        # The directory this script is in.
        # cwd = os.getcwd()
        # The directory this script is in (ArcGIS_Analysis_Files).
        # or os.path.dirname(sys.argv[0])

        # May 2 2022
        Version = "May 2 2022"
        DateCode = "20220502"

        # March 7 2022
        #Version = "March 7 2022"
        #DateCode = "20220307"

        # March 1 2022
        #Version = "March 1 2022"
        #DateCode = "20220301"

        # February 1 2022
        #Version = "February 1 2022"
        #DateCode = "20220201"

        # March 1 2021
        #Version = "March 1 2021"
        #DateCode = "20210301"

        ProjectName = "DisMap {0}".format(Version)

        BASE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
        BASE_DIRECTORY = os.path.join(BASE_DIRECTORY, Version)
        GEBCO_DIRECTORY = os.path.join(BASE_DIRECTORY, "GEBCO")

        #ProjectName = "DisMap"

        # ###--->>> Software Environment Level
        SoftwareEnvironmentLevel = "Dev"
        # SoftwareEnvironmentLevel = "Test"
        # SoftwareEnvironmentLevel = "Prod"

        DefaultGDB = os.path.join(BASE_DIRECTORY, "Default.gdb")
        #ProjectGDB = os.path.join(BASE_DIRECTORY, "{0}.gdb".format(ProjectName + SoftwareEnvironmentLevel))
        GebcoGDB = os.path.join(BASE_DIRECTORY, "GEBCO.gdb")
        ScratchGDB = os.path.join(BASE_DIRECTORY, "Scratch {0} {1}".format(Version, SoftwareEnvironmentLevel), "scratch.gdb")
        ScratchFolder = os.path.join(BASE_DIRECTORY, "Scratch {0} {1}".format(Version, SoftwareEnvironmentLevel))
        BathymetryGDB = os.path.join(BASE_DIRECTORY, "Bathymetry.gdb")

        if not os.path.isdir(ScratchFolder): os.makedirs(ScratchFolder)
        if not arcpy.Exists(GebcoGDB): arcpy.CreateFileGDB_management(BASE_DIRECTORY, "GEBCO")
        if not arcpy.Exists(BathymetryGDB): arcpy.CreateFileGDB_management(BASE_DIRECTORY, "Bathymetry")

        # Set the workspace to the GebcoGDB
        arcpy.env.workspace = GebcoGDB

        #if not os.path.isdir(ScratchFolder):
        #    #shutil.rmtree(ScratchFolder)
        #    arcpy.CreateFileGDB_management(ScratchGDB)
        # Scratch workspace
        arcpy.env.scratchWorkspace = ScratchGDB
        # If the scratch workspace is missing, referencing the env will create the workspace
        msg = arcpy.env.scratchFolder
        arcpy.AddMessage(msg)
        msg = arcpy.env.scratchGDB
        arcpy.AddMessage(msg)
        del msg


        main()



        del print_function, BASE_DIRECTORY, GEBCO_DIRECTORY #, ProjectName
        #del SoftwareEnvironmentLevel
        del DefaultGDB, GebcoGDB, ScratchGDB
        del ScratchFolder
        #del ProjectGDB
        del BathymetryGDB
        del Version, DateCode, ProjectName
        del SoftwareEnvironmentLevel

        #Final benchmark for the region.
        msg = "PROGRAM COMPLETED ON {}".format(strftime("%a %b %d %I:%M:%S %p", localtime()))
        print(msg)

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"Elapsed Time {0} (H:M:S)\n".format(strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        globalKeys = [key for key in globals().keys() if not key.startswith('__') and key not in exclude_keys]

        if globalKeys:
            #msg = "Global Keys: {0}".format(u", ".join(globalKeys))
            msg = "Global Keys: {0}".format(u', '.join('"{0}"'.format(gk) for gk in globalKeys))
            #' + '.join('"{0}"'.format(cr) for cr in arcpy.ListRasters("Con*"))
            print(msg)
            print(', '.join(globalKeys))
            del msg
        del globalKeys

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo