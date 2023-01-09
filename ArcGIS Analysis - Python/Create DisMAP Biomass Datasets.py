# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Create DisMAP Biomass Datasets
# Purpose:
#
# Author:      john.f.kennedy@noaa.gov
#
# Created:     12/09/2022
# Copyright:   (c) john.f.kennedy@noaa.gov 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# ############################################################################################
# NOAA DisMAP - http://
# Generate Biomass Rasters
#
# This script was made to generate the time series, interpolateed biomass maps
# by fish species and region for use on NOAA DisMAP. If you require additional
# information or would like to see the script refined further for more general
# and public use, please contact Melissa Karp at ( melissa.karp@noaa.gov ).
# For questions specific to the python code, please contact John Kennedy at:
# john.f.kennedy@noaa.gov
#
# Help Contact(s):
#       Melissa Karp ( melissa.karp@noaa.gov )
#       John Kennedy ( john.f.kennedy@noaa.gov )
#
# Additional Items:
#       If you want to completly recreate the maps on your own or run the script
#       as-is, you can download the supplement here:
#       http:
#       *Please make sure to create the CSV data (as it is significantly large)
#       and place it in the CSV_DIRECTORY folder you specify below.
#
# Version:
#       x.x Public Beta
#
# Version Description:
#       This is the start of a cleaned up script (code and comment wise) beta
#       version for the public to use in their own programs or to generate their
#       own maps. Some variables may be deprecated. Some items still need to be
#       cleaned up code wise, and possibly optimized, mainly the more intesive
#       parts of the code.
#
# Tested on:
#       Windows 10, ArcGIS Pro 2.9.5 / Python 3.7.11
#
# Recommended Settings:
#  *These settings are what the author has specifically tested on. This script
#   may work on prior versions of the specifications listed, however they were
#   not tested on those specifications.
#  *In addition: Versions higher than the specifications listed should work,
#   however, the code was not tested on those specifications
#       ArcGIS Pro 2.9.x
#       ArcPy Spatial Extension
#       Python 3.7.11
#       Windows Machine (Windows 10)
# ############################################################################################

import os
import arcpy
from time import time, localtime, strftime, gmtime
import logging

# Get the name of the running fuction using inspect
import inspect
function_name = lambda: inspect.stack()[1][3]

# ###--->>> Defs
def addMetadata(item):
    try:
        pass
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)
        # Set a start time so that we can see how log things take
        start_time = time()

        #print(os.path.basename(item))


        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime("%a %b %d %I %M %S %p", localtime())
        log_file = os.path.join(log_file_folder, f"{function} for {os.path.basename(item)} on {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = "STARTING {0} for {1} ON {2}".format(function, os.path.basename(item), strftime("%a %b %d %I:%M:%S %p", localtime()))
        logFile(log_file, msg); del msg

        # Get the target item's Metadata object
        md = arcpy.metadata.Metadata(item)

        md.synchronize('ACCESSED', 1)

        md.title = os.path.basename(item)

        md.tags = "Tags"

        md.summary = "Summary"

        md.description = "Description"

        md.credits = "Credits"

        md.save()
        md.reload()

        msg = f"\t Dataset: {item}\n"

        msg = msg + "\t\t Title: {0}\n".format(md.title)

        msg = msg + "\t\t Tags: {0}\n".format(md.tags)

        msg = msg + "\t\t Summary: {0}\n".format(md.summary)

        msg = msg + "\t\t Description: {0}\n".format(md.description)

        msg = msg + "\t\t Credits: {0}\n".format(md.credits)
        logFile(log_file, msg); del msg


        # Delete all geoprocessing history and any enclosed files from the item's metadata
        if not md.isReadOnly:
            md.deleteContent('GPHISTORY')
            md.deleteContent('ENCLOSED_FILES')
            md.save()
            md.reload()

        del md, item

        #Final benchmark for the region.
        msg = "ENDING {0} COMPLETED ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time)))
        logFile(log_file, msg); del msg

        del log_file, start_time, end_time, elapse_time

    except: # This code is executed only if an exception was raised in the
            # try block. Code executed in this block is just like normal code:
            # if there is an exception, it will not be automatically caught
            # (and probably stop the program).
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        py_msg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        arcpy_msg = "Arcpy Errors:\n" + arcpy.GetMessages(2) + "\n"
        #arcpy.AddError(py_msg)
        #arcpy.AddError(arcpy_msg)
        logFile(log_file.replace(".log", " ERROR.log"), py_msg)
        logFile(log_file.replace(".log", " ERROR.log"), arcpy_msg)
        del tb, tbinfo, py_msg, arcpy_msg, sys, traceback

    else: # This code is executed only if no exceptions were raised in the try
          # block. Code executed in this block is just like normal code: if
          # there is an exception, it will not be automatically caught
          # (and probably stop the program). Notice that if the else block is
          # executed, then the except block is not, and vice versa. This block
          # is optional.
        # Use pass to skip this code block
        pass

    finally: # This code always executes after the other blocks, even if there
             # was an uncaught exception (that didn’t cause a crash, obviously)
             # or a return statement in one of the other blocks. Code executed
             # in this block is just like normal code: if there is an exception,
             # it will not be automatically caught (and probably stop the
             # program). This block is also optional.

        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if "function" not in key]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

def clearFolder(folder):
    # Clear Log Directory
    # elif ClearLogDirectory:
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
        del filename, file_path

def compactGDB(gdb):
    arcpy.management.Compact(gdb)
    msg = arcpy.GetMessages()
    msg = ">->-> {0}".format(msg.replace('\n', '\n>->-> '))
    logFile(log_file, msg); del msg

def createTemplateTables():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime("%a %b %d %I %M %S %p", localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = "STARTING {0} ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
        logFile(log_file, msg); del msg

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the ScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Table Field dictionary
        # geomTypes: "Polygon", "PolyLine", "Point", "Table"
        tb_dict = {
                   "_Template_CSV_Data" : {"Table" : {0 : {"Region" : {"type" : "TEXT",
                                                                       "precision" : "",
                                                                       "scale" : "",
                                                                       "length" : 50,
                                                                       "aliasName" : "Region"}},
                                                      1 : {"SampleID" : {"type" : "TEXT",
                                                                       "precision" : "",
                                                                       "scale" : "",
                                                                       "length" : 20,
                                                                       "aliasName" : "Sample ID"}},
                                                      2 : {"Species" : {"type" : "TEXT",
                                                                        "precision" : "",
                                                                        "scale" : "",
                                                                        "length" : 50,
                                                                        "aliasName" : "Species"}},
                                                      3 : {"CommonName" : {"type" : "TEXT",
                                                                           "precision" : "",
                                                                           "scale" : "",
                                                                           "length" : 100,
                                                                           "aliasName" : "Common Name"}},
                                                      4 : {"SpeciesCommonName" : {"type" : "TEXT",
                                                                                  "precision" : "",
                                                                                  "scale" : "",
                                                                                  "length" : 200,
                                                                                  "aliasName" : "Species (Common Name)"}},
                                                      5 : {"CommonNameSpecies" : {"type" : "TEXT",
                                                                                  "precision" : "",
                                                                                  "scale" : "",
                                                                                  "length" : 200,
                                                                                  "aliasName" : "Common Name (Species)"}},
                                                      6 : {"CoreSpecies" : {"type" : "TEXT",
                                                                            "precision" : "",
                                                                            "scale" : "",
                                                                            "length" : 5,
                                                                            "aliasName" : "Core Species"}},
                                                      7 : {"Year" : {"type" : "SHORT",
                                                                     "precision" : "",
                                                                     "scale" : "",
                                                                     "length" : 4,
                                                                     "aliasName" : "Year"}},
                                                      8 : {"StdTime" : {"type" : "DATE",
                                                                        "precision" : "",
                                                                        "scale" : "",
                                                                        "length" : 8,
                                                                        "aliasName" : "StdTime"}},
                                                      9 : {"WTCPUE" : {"type" : "DOUBLE",
                                                                       "precision" : "",
                                                                       "scale" : "",
                                                                       "length" : 8,
                                                                       "aliasName" : "WTCPUE"}},
                                                     10 : {"WTCPUECubeRoot" : {"type" : "DOUBLE",
                                                                               "precision" : "",
                                                                               "scale" : "",
                                                                               "length" : 8,
                                                                               "aliasName" : "WTCPUE Cube Root"}},
                                                     11 : {"Stratum" : {"type" : "TEXT",
                                                                        "precision" : "",
                                                                        "scale" : "",
                                                                        "length" : 25,
                                                                        "aliasName" : "Stratum"}},
                                                     12 : {"StratumArea" : {"type" : "DOUBLE",
                                                                            "precision" : "",
                                                                            "scale" : "",
                                                                            "length" : 8,
                                                                            "aliasName" : "Stratum Area"}},
                                                     13 : {"Depth" : {"type" : "DOUBLE",
                                                                      "precision" : "",
                                                                      "scale" : "",
                                                                      "length" : 8,
                                                                      "aliasName" : "Depth"}},
                                                     14 : {"Latitude" : {"type" : "DOUBLE",
                                                                         "precision" : "",
                                                                         "scale" : "",
                                                                         "length" : 8,
                                                                         "aliasName" : "Latitude"}},
                                                     15 : {"Longitude" : {"type" : "DOUBLE",
                                                                          "precision" : "",
                                                                          "scale" : "",
                                                                          "length" : 8,
                                                                          "aliasName" : "Longitude"}},
                                                  }},
                   "_Template_Indicators" : {"Table" : {1 : {"Region" : {"type" : "TEXT",
                                                                         "precision" : "",
                                                                         "scale" : "",
                                                                         "length" : 50,
                                                                         "aliasName" : "Region"}},
                                                        2 : {"DisMapRegionCode": {"type" : "TEXT",
                                                                                  "precision" : "",
                                                                                  "scale" : "",
                                                                                  "length" : 50,
                                                                                  "aliasName" : "DisMAP Region Code"}},
                                                        3 : {"DisMapSeasonCode": {"type" : "TEXT",
                                                                                  "precision" : "",
                                                                                  "scale" : "",
                                                                                  "length" : 10,
                                                                                  "aliasName" : "DisMAP Season Code"}},
                                                        4 : {"Species" : {"type" : "TEXT",
                                                                          "precision" : "",
                                                                          "scale" : "",
                                                                          "length" : 50,
                                                                          "aliasName" : "Species"}},
                                                        5 : {"CommonName" : {"type" : "TEXT",
                                                                             "precision" : "",
                                                                             "scale" : "",
                                                                             "length" : 50,
                                                                             "aliasName" : "Common Name"}},
                                                        6 : {"CoreSpecies" : {"type" : "TEXT",
                                                                              "precision" : "",
                                                                              "scale" : "",
                                                                              "length" : 5,
                                                                              "aliasName" : "Core Species"}},
                                                        7 : {"TaxonomicGroup" : {"type" : "TEXT",
                                                                                 "precision" : "",
                                                                                 "scale" : "",
                                                                                 "length" : 50,
                                                                                 "aliasName" : "Taxonomic Group"}},
                                                        8 : {"Year" : {"type" : "SHORT",
                                                                       "precision" : "",
                                                                        "scale" : "",
                                                                       "length" : 4,
                                                                       "aliasName" : "Year"}},
                                                        9 : {"FisheryManagementCouncil" : {"type" : "TEXT",
                                                                                           "precision" : "",
                                                                                           "scale" : "",
                                                                                           "length" : 50,
                                                                                           "aliasName" : "Fishery Management Council"}},
                                                       10 : {"FisheryManagementPlan" : {"type" : "TEXT",
                                                                                        "precision" : "",
                                                                                        "scale" : "",
                                                                                        "length" : 50,
                                                                                        "aliasName" : "Fishery Management Plan"}},
                                                       # product name (only IDW Interpolation for now)
                                                       11 : {"ProductName" : {"type" : "TEXT",
                                                                              "precision" : "",
                                                                              "scale" : "",
                                                                              "length" : 25,
                                                                              "aliasName" : "Product Name"}},
                                                       12 : {"CenterOfGravityLatitude" : {"type" : "DOUBLE",
                                                                                          "precision" : "",
                                                                                          "scale" : "",
                                                                                          "length" : "",
                                                                                          "aliasName" : "Center of Gravity Latitude"}},
                                                       13 : {"MinimumLatitude" : {"type" : "DOUBLE",
                                                                                  "precision" : "",
                                                                                  "scale" : "",
                                                                                  "length" : "",
                                                                                  "aliasName" : "Minimum Latitude"}},
                                                       14 : {"MaximumLatitude" : {"type" : "DOUBLE",
                                                                                  "precision" : "",
                                                                                  "scale" : "",
                                                                                  "length" : "",
                                                                                  "aliasName" : "Maximum Latitude"}},
                                                       15 : {"OffsetLatitude" : {"type" : "DOUBLE",
                                                                                 "precision" : "",
                                                                                 "scale" : "",
                                                                                 "length" : "",
                                                                                 "aliasName" : "Offset Latitude"}},
                                                       16 : {"CenterOfGravityLatitudeSE" : {"type" : "DOUBLE",
                                                                                            "precision" : "",
                                                                                            "scale" : "",
                                                                                            "length" : "",
                                                                                            "aliasName" : "Center of Gravity Latitude Standard Error"}},
                                                       17 : {"CenterOfGravityLongitude" : {"type" : "DOUBLE",
                                                                                           "precision" : "",
                                                                                           "scale" : "",
                                                                                           "length" : "",
                                                                                           "aliasName" : "Center of Gravity Longitude"}},
                                                       18 : {"MinimumLongitude" : {"type" : "DOUBLE",
                                                                                   "precision" : "",
                                                                                   "scale" : "",
                                                                                   "length" : "",
                                                                                   "aliasName" : "Minimum Longitude"}},
                                                       19 : {"MaximumLongitude" : {"type" : "DOUBLE",
                                                                                   "precision" : "",
                                                                                   "scale" : "",
                                                                                   "length" : "",
                                                                                   "aliasName" : "Maximum Longitude"}},
                                                       20 : {"OffsetLongitude" : {"type" : "DOUBLE",
                                                                                  "precision" : "",
                                                                                  "scale" : "",
                                                                                  "length" : "",
                                                                                  "aliasName" : "Offset Longitude"}},
                                                       21 : {"CenterOfGravityLongitudeSE" : {"type" : "DOUBLE",
                                                                                             "precision" : "",
                                                                                             "scale" : "",
                                                                                             "length" : "",
                                                                                             "aliasName" : "Center of Gravity Longitude Standard Error"}},
                                                       22 : {"CenterOfGravityDepth" : {"type" : "DOUBLE",
                                                                                       "precision" : "",
                                                                                       "scale" : "",
                                                                                       "length" : "",
                                                                                       "aliasName" : "Center of Gravity Depth"}},
                                                       23 : {"MinimumDepth" : {"type" : "DOUBLE",
                                                                               "precision" : "",
                                                                               "scale" : "",
                                                                               "length" : "",
                                                                               "aliasName" : "Minimum Depth"}},
                                                       24 : {"MaximumDepth" : {"type" : "DOUBLE",
                                                                               "precision" : "",
                                                                               "scale" : "",
                                                                               "length" : "",
                                                                               "aliasName" : "Maximum Depth"}},
                                                       25 : {"OffsetDepth" : {"type" : "DOUBLE",
                                                                              "precision" : "",
                                                                              "scale" : "",
                                                                              "length" : "",
                                                                              "aliasName" : "Offset Depth"}},
                                                       26 : {"CenterOfGravityDepthSE" : {"type" : "DOUBLE",
                                                                                         "precision" : "",
                                                                                         "scale" : "",
                                                                                         "length" : "",
                                                                                         "aliasName" : "Center of Gravity Depth Standard Error"}},
                                                       }},
                   "_Template_MasterSpeciesInformation" : {"Table" : {0 : {"Species" : {"type" : "TEXT",
                                                                                        "precision" : "",
                                                                                        "scale" : "",
                                                                                        "length" : 50,
                                                                                        "aliasName" : "Species"}},
                                                                      1 : {"CommonName" : {"type" : "TEXT",
                                                                                           "precision" : "",
                                                                                           "scale" : "",
                                                                                           "length" : 50,
                                                                                           "aliasName" : "Common Name"}},
                                                                      2 : {"SpeciesCommonName" : {"type" : "TEXT",
                                                                                                  "precision" : "",
                                                                                                  "scale" : "",
                                                                                                  "length" : 100,
                                                                                                  "aliasName" : "Species (Common Name)"}},
                                                                      3 : {"CommonNameSpecies" : {"type" : "TEXT",
                                                                                                  "precision" : "",
                                                                                                  "scale" : "",
                                                                                                  "length" : 100,
                                                                                                  "aliasName" : "Common Name (Species)"}},
                                                                      4 : {"TaxonomicGroup" : {"type" : "TEXT",
                                                                                               "precision" : "",
                                                                                               "scale" : "",
                                                                                               "length" : 50,
                                                                                               "aliasName" : "Taxonomic Group"}},
                                                                      5 : {"FisheryManagementCouncil" : {"type" : "TEXT",
                                                                                                         "precision" : "",
                                                                                                         "scale" : "",
                                                                                                         "length" : 50,
                                                                                                         "aliasName" : "Fishery Management Council"}},
                                                                      6 : {"FisheryManagementPlan" : {"type" : "TEXT",
                                                                                                      "precision" : "",
                                                                                                      "scale" : "",
                                                                                                      "length" : 50,
                                                                                                      "aliasName" : "Fishery Management Plan"}},
                                                                      }},
                   "_Template_RegionSpeciesYearImageName" : {"Table" : {1 : {"Region" : {"type" : "TEXT",
                                                                                         "precision" : "",
                                                                                         "scale" : "",
                                                                                         "length" : 50,
                                                                                         "aliasName" : "Region"}},
                                                                        2 : {"Species" : {"type" : "TEXT",
                                                                                          "precision" : "",
                                                                                          "scale" : "",
                                                                                          "length" : 50,
                                                                                          "aliasName" : "Species"}},
                                                                        3 : {"CommonName" : {"type" : "TEXT",
                                                                                             "precision" : "",
                                                                                             "scale" : "",
                                                                                             "length" : 50,
                                                                                             "aliasName" : "Common Name"}},
                                                                        4 : {"SpeciesCommonName" : {"type" : "TEXT",
                                                                                                    "precision" : "",
                                                                                                    "scale" : "",
                                                                                                    "length" : 100,
                                                                                                    "aliasName" : "Species (Common Name)"}},
                                                                        5 : {"CoreSpecies" : {"type" : "TEXT",
                                                                                              "precision" : "",
                                                                                              "scale" : "",
                                                                                              "length" : 5,
                                                                                              "aliasName" : "Core Species"}},
                                                                        6 : {"Year" : {"type" : "SHORT",
                                                                                       "precision" : "",
                                                                                       "scale" : "",
                                                                                       "length" : 4,
                                                                                       "aliasName" : "Year"}},
                                                                        7 : {"StdTime" : {"type" : "DATE",
                                                                                          "precision" : "",
                                                                                          "scale" : "",
                                                                                          "length" : "",
                                                                                          "aliasName" : "StdTime"}},
                                                                        8 : {"Variable" : {"type" : "TEXT",
                                                                                           "precision" : "",
                                                                                           "scale" : "",
                                                                                           "length" : 50,
                                                                                           "aliasName" : "Variable"}},
                                                                        9 : {"Dimensions" : {"type" : "TEXT",
                                                                                             "precision" : "",
                                                                                             "scale" : "",
                                                                                             "length" : 10,
                                                                                             "aliasName" : "Dimensions"}},
                                                                       10 : {"ImageName" : {"type" : "TEXT",
                                                                                            "precision" : "",
                                                                                            "scale" : "",
                                                                                            "length" : 200,
                                                                                            "aliasName" : "Image Name"}},
                                                                       }},
                   "_Template_SpeciesRegionSeason" : {"Table" : {1 : {"Region" : {"type" : "TEXT",
                                                                                  "precision" : "",
                                                                                  "scale" : "",
                                                                                  "length" : 50,
                                                                                  "aliasName" : "Region"}},
                                                                 2 : {"Species" : {"type" : "TEXT",
                                                                                   "precision" : "",
                                                                                   "scale" : "",
                                                                                   "length" : 50,
                                                                                   "aliasName" : "Species"}},
                                                                 3 : {"CommonName" : {"type" : "TEXT",
                                                                                      "precision" : "",
                                                                                      "scale" : "",
                                                                                      "length" : 50,
                                                                                      "aliasName" : "Common Name"}},
                                                                 4 : {"SpeciesCommonName" : {"type" : "TEXT",
                                                                                             "precision" : "",
                                                                                             "scale" : "",
                                                                                             "length" : 100,
                                                                                             "aliasName" : "Species (Common Name)"}},
                                                                 5 : {"CommonNameSpecies" : {"type" : "TEXT",
                                                                                             "precision" : "",
                                                                                             "scale" : "",
                                                                                             "length" : 100,
                                                                                             "aliasName" : "Common Name (Species)"}},
                                                                 6 : {"CoreSpecies" : {"type" : "TEXT",
                                                                                       "precision" : "",
                                                                                       "scale" : "",
                                                                                       "length" : 5,
                                                                                       "aliasName" : "Core Species"}},
                                                                 7 : {"DisMapRegionCode": {"type" : "TEXT",
                                                                                           "precision" : "",
                                                                                           "scale" : "",
                                                                                           "length" : 50,
                                                                                           "aliasName" : "DisMAP Region Code"}},
                                                                 8 : {"DisMapSeasonCode": {"type" : "TEXT",
                                                                                           "precision" : "",
                                                                                           "scale" : "",
                                                                                           "length" : 10,
                                                                                           "aliasName" : "DisMAP Season Code"}}
                                                                }},
                  }

        for tb in tb_dict:
            msg = "Dataet: {0}".format(tb)
            logFile(log_file, msg); del msg

            geomTypes = tb_dict[tb]
            for geomType in geomTypes:
                msg = "\t Geometry Type: {0}".format(geomType)
                logFile(log_file, msg); del msg
                #if arcpy.Exists(tb):
                #    arcpy.management.Delete(tb)

                if "Table" in geomType:
                    # Create table
                    arcpy.management.CreateTable(ProjectGDB, tb)
                    msg = arcpy.GetMessages()
                    msg = "\t\t {0}\n".format(msg.replace('\n', '\n\t\t '))
                    logFile(log_file, msg); del msg

                else:
                    # Create feature classes
                    arcpy.management.CreateFeatureclass(ProjectGDB, tb, "{0}".format(geomType.upper()), spatial_reference = sp_ref)
                    msg = arcpy.GetMessages()
                    msg = "\t\t {0}\n".format(msg.replace('\n', '\n\t\t '))
                    logFile(log_file, msg); del msg

                ids = geomTypes[geomType]
                for id in ids:
                    msg = "\t\t ID: {0}\n".format(id)
                    # Get fields from dictionary
                    fields = ids[id]
                    for field in fields:
                        msg = msg + "\t\t\t Field: {0}\n".format(field)

                        fieldName = field
                        items = fields[field]
                        fieldtype = items["type"]
                        msg = msg + "\t\t\t\t fieldtype: {0}\n".format(fieldtype)

                        fieldprecision = items["precision"]
                        msg = msg + "\t\t\t\t fieldprecision: {0}\n".format(fieldprecision)

                        fieldscale = items["scale"]
                        msg = msg + "\t\t\t\t fieldscale: {0}\n".format(fieldscale)

                        fieldlength = items["length"]
                        msg = msg + "\t\t\t\t fieldlength: {0}\n".format(fieldlength)

                        fieldAliasName = items["aliasName"]
                        msg = msg + "\t\t\t\t fieldAliasName: {0}\n".format(fieldAliasName)

                        # Write to log file
                        logFile(log_file, msg); del msg

                        # Add Field
                        arcpy.management.AddField(tb, fieldName, fieldtype, fieldprecision, fieldscale, fieldlength, fieldAliasName)
                        msg = arcpy.GetMessages()
                        msg = "\t\t\t\t {0}\n".format(msg.replace('\n', '\n\t\t\t\t '))
                        logFile(log_file, msg); del msg

                        del field, fieldName, items, fieldtype
                        del fieldprecision, fieldscale, fieldlength
                        del fieldAliasName
                    del id, fields
                del ids
            # Add Metadata
            addMetadata(tb)
        #
        del tb_dict, tb, geomTypes, geomType

        #Final benchmark for the region.
        msg = "ENDING {0} COMPLETED ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time)))
        logFile(log_file, msg); del msg

        del log_file, start_time, end_time, elapse_time


    except: # This code is executed only if an exception was raised in the
            # try block. Code executed in this block is just like normal code:
            # if there is an exception, it will not be automatically caught
            # (and probably stop the program).
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        py_msg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        arcpy_msg = "Arcpy Errors:\n" + arcpy.GetMessages(2) + "\n"
        #arcpy.AddError(py_msg)
        #arcpy.AddError(arcpy_msg)
        logFile(log_file.replace(".log", " ERROR.log"), py_msg)
        logFile(log_file.replace(".log", " ERROR.log"), arcpy_msg)
        del tb, tbinfo, py_msg, arcpy_msg, sys, traceback

    else: # This code is executed only if no exceptions were raised in the try
          # block. Code executed in this block is just like normal code: if
          # there is an exception, it will not be automatically caught
          # (and probably stop the program). Notice that if the else block is
          # executed, then the except block is not, and vice versa. This block
          # is optional.
        # Use pass to skip this code block
        # pass

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    finally: # This code always executes after the other blocks, even if there
             # was an uncaught exception (that didn’t cause a crash, obviously)
             # or a return statement in one of the other blocks. Code executed
             # in this block is just like normal code: if there is an exception,
             # it will not be automatically caught (and probably stop the
             # program). This block is also optional.

        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if "function" not in key]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

def createCSVTables():
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        #
        import pandas as pd
        import numpy as np

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime("%a %b %d %I %M %S %p", localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = "STARTING {0} ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
        logFile(log_file, msg); del msg

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the ScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Start looping over the dataset_names array as we go region by region.
        for dataset_name in dataset_names:
            # Assigning variables from items in the chosen table list
            region_abb = dataset_name[0]
            region = dataset_name[1]
            csv_file = dataset_name[2]
            region_shape = dataset_name[3]
            region_boundary = dataset_name[4]
            region_georef = dataset_name[5]
            region_contours = dataset_name[6]
            region_cell_size = dataset_name[7]

            # Make Geodatabase friendly name
            region_name = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "")

            region_start_time = time()

            # Write a message to the log file
            msg = "STARTING REGION {0} ON {1}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg); del msg

            # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
            msg = '> Generating the {0} CSV Table.'.format(region)
            logFile(log_file, msg); del msg

            #
            out_table = os.path.join(ProjectGDB, csv_file)
            msg = f'> {out_table}'
            logFile(log_file, msg); del msg

            input_csv_file = os.path.join(CSV_DIRECTORY, csv_file + ".csv")
            # https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/09_timeseries.html?highlight=datetime
            # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
            #df = pd.read_csv('my_file.tsv', sep='\t', header=0)  ## not setting the index_col
            #df.set_index(['0'], inplace=True)

            df = pd.read_csv(input_csv_file,
                             index_col = 0,
                             encoding="utf-8",
                             #encoding = "ISO-8859-1",
                             #engine='python',
                             delimiter = ',',
                             #dtype = None,
                             dtype = {
                                      "region" : str,
                                      "sampleid" : str,
                                      "year" : 'uint16',
                                      # 'TrawlDate' : 'uint16',
                                      # 'SurfaceTemperature' : float,
                                      # 'BottomTemperature' : float,
                                      "spp" : str,
                                      "wtcpue" : float,
                                      "common" : str,
                                      "stratum" : str,
                                      "stratumarea" : float,
                                      "lat" : float,
                                      "lon" : float,
                                      "depth" : float,
                                      },
                             )
            del input_csv_file

            # TODO: add new fields:
            # new fields:
            #   sea surface temperature (float), 'SurfaceTemperature'
            #   bottom temperature (float), 'BottomTemperature'
            #   Date of Trawl (Date) (Day-MO-Year of the trawl) 'TrawlDate'

            msg = '>-> Defining the column name.'
            logFile(log_file, msg); del msg

            # The original column names from the CSV files are not very
            # reader friendly, so we are making some changes here
            #df.columns = [u'Region', u'HUALID', u'Year', u'Species', u'WTCPUE', u'CommonName', u'Stratum', u'StratumArea', u'Latitude', u'Longitude', u'Depth']
            df.columns = ['Region', 'SampleID', 'Year', 'Species', 'WTCPUE', 'CommonName', 'Stratum', 'StratumArea', 'Latitude', 'Longitude', 'Depth']

            # Test if we are filtering on species. If so, a new species list is
            # created with the selected species remaining in the list
            #if FilterSpecies and ReplaceTable:
            if FilterSpecies:
                msg = '>->-> Filtering table on selected species for {0} Table'.format(region)
                logFile(log_file, msg); del msg
                # Filter data frame
                df = df.loc[df['Species'].isin(selected_species.keys())]
            else:
                msg = '>->-> No species filtering of selected species for {0} Table'.format(region)
                logFile(log_file, msg); del msg

            #-->> Species and CommonName
            msg = '>->->  Setting Nulls in Species and CommonName to empty strings.'
            logFile(log_file, msg); del msg
            # Replace NaN with an empty string. When pandas reads a cell
            # with missing data, it asigns that cell with a Null or nan
            # value. So, we are changing that value to an empty string of ''.
            # Seems to be realivent for Species and CommonName only
            df.Species    = df.Species.fillna('')
            df.CommonName = df.CommonName.fillna('')
            df.Species    = df.Species.replace('Na', '')
            df.CommonName = df.CommonName.replace('Na', '')
            #msg = '>->->  Droping row where Species have an empty string.'
            #logFile(log_file, msg); del msg
            # Drop rows based on a condition. Rows without a species name are not of use
            #df = df[df.Species != '']

            #-->> SpeciesCommonName
            msg = '>->->  Adding SpeciesCommonName and setting it to "Species (CommonName)".'
            logFile(log_file, msg); del msg
            # Insert column
            df.insert(df.columns.get_loc('CommonName')+1, 'SpeciesCommonName', df['Species'] + ' (' + df['CommonName'] + ')')

            #-->> CommonNameSpecies
            msg = '>->->  Adding CommonNameSpecies and setting it to "CommonName (Species)".'
            logFile(log_file, msg); del msg
            # Insert column
            df.insert(df.columns.get_loc('SpeciesCommonName')+1, 'CommonNameSpecies', df['CommonName'] + ' (' + df['Species'] + ')')

            #-->> CoreSpecies
            msg = '>->->  Adding CoreSpecies and setting it to "No".'
            logFile(log_file, msg); del msg
            # Insert column
            df.insert(df.columns.get_loc('CommonNameSpecies')+1, 'CoreSpecies', "No")

            # ###-->> Depth
            # msg = '>->->  Setting the Depth to float16.'
            # logFile(log_file, msg); del msg
            # # The Depth column in the CSV files contain a mix of integer and
            # # double. This converts all to float values to be consistant
            # #df.Depth = df.Depth.astype(np.float16) # or np.float32 or np.float64
            # df.Depth = df.Depth.astype(float)

            #-->> WTCPUE
            msg = '>->->  Replacing Infinity values with Nulls.'
            logFile(log_file, msg); del msg
            # Replace Inf with Nulls
            # For some cell values in the 'WTCPUE' column, there is an Inf
            # value representing an infinit
            df.replace([np.inf, -np.inf], np.nan, inplace=True)

            #-->> WTCPUECubeRoot
            msg = '>->->  Adding the WTCPUECubeRoot column and calculating values.'
            logFile(log_file, msg); del msg
            # Insert a column to the right of a column and then do a calculation
            df.insert(df.columns.get_loc('WTCPUE')+1, 'WTCPUECubeRoot', df['WTCPUE'].pow((1.0/3.0)))

            msg = '>-> Creating the {0} Geodatabase Table'.format(region)
            logFile(log_file, msg); del msg

            # ###--->>> Numpy Datatypes
            # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm

            #OARegion_Max: 20
            #HUALID_Max: 15
            #Species_Max: 23
            #CommonName_Max: 18
            #Stratum_Max: 14

####                # This works in Python 3.x unicode issue
####                # names = df.dtypes.index.tolist()
####                # Consider using import platform and platform.python_version()
####                # to get Python version number i.e. '2.7.18'
####                # This works for Python 2.7.x non-unicode issue
####                names = [str(n) for n in df.dtypes.index.tolist()]
####                names = ', '.join(names)
####                formats = '<i4, S50, S20, S50, S50, <i4, <f8, <f8, S25, <f8, <f8, <f8, <f8'
####                # This step takes the pandas dataframe and converts it to a numpy
####                # array so that the array can be converted to a ArcGIS table
####                # CSVFILEID, OARegion, HUALID, Year, Species, WTCPUE, WTCPUECubeRoot, CommonName, Stratum, StratumArea, Latitude, Longitude, Depth
####                CSVFILEID, Integer, 4 <i4
####                Region, String, 20 S50 ##
####                HUALID, String, 14 S20
####                Species, String, 23 S50
####                CommonName, String, 15 S50
####                Year, Integer, 4 <i4
####                WTCPUE, Double, 8 <f8
####                WTCPUECubeRoot, Double, 8 <f8
####                Stratum, String, 8 S25
####                StratumArea, Double, 8 <f8
####                Depth, Double, 8 <f8
####                Latitude, Double, 8 <f8
####                Longitude, Double, 8 <f8
####                '<i4, S50,  S20, S50, S50, <i4, <f8, <f8, S25, <f8, <f8, <f8, <f8'
####
######              #  'S10,S8,S4,<f8,<f8,S5,S5,<i4,S5'
####
####                array = np.array(np.rec.fromrecords(df.values, names = names, formats = formats))
####                #array = np.array(np.rec.fromrecords(recs, ,
####                del formats
####
####                array.dtype.names = tuple(names)

            #print('DataFrame\n----------\n', df.head(10))
            #print('\nDataFrame datatypes :\n', df.dtypes)
            #columns = [str(c) for c in df.dtypes.index.tolist()]
            column_names = list(df.columns)
            #print(column_names)
            # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
            # column_formats = [u'S50', u'S20', 'u2', u'S50', 'f4', 'f4', u'S50', u'S100', u'S25', 'f4', 'f4', 'f4', 'f4']
            #column_formats = ['S50', 'S20', '<i4', 'S50', '<f8', '<f8', 'S50', 'S100', 'S100', 'S5', 'S25', '<f8', '<f8', '<f8', '<f8']
            column_formats = ['S50', 'S20', '<i4', 'S50', '<f8', '<f8', 'U1000', 'U200', 'U200', 'S5', 'S25', '<f8', '<f8', '<f8', '<f8']
            dtypes = list(zip(column_names, column_formats))

            df['CommonName'] = df['CommonName'].astype('unicode')

            #print(df)
            try:
                array = np.array(np.rec.fromrecords(df.values), dtype = dtypes)
            except:
                import sys, traceback
                # Get the traceback object
                tb = sys.exc_info()[2]
                #tb = sys.exc_info()
                tbinfo = traceback.format_tb(tb)[0]
                # Concatenate information together concerning the error into a message string
                pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
                logFile(log_file.replace(".log", " ERROR.log"), pymsg)
                del pymsg, tb, sys, tbinfo

            del df, column_names, column_formats, dtypes

            # Temporary table
            tmp_table = out_table + '_tmp'
            if arcpy.Exists(tmp_table):
                arcpy.management.Delete(tmp_table)

            try:
                arcpy.da.NumPyArrayToTable(array, tmp_table)
                del array
                #print(column_names)
                #arcpy.da.NumPyArrayToTable(records, tmp_table, column_names)

            except IOError:
                print("Something went wrong: IOError")
            except:
                import sys, traceback
                # Get the traceback object
                tb = sys.exc_info()[2]
                #tb = sys.exc_info()
                tbinfo = traceback.format_tb(tb)[0]
                # Concatenate information together concerning the error into a message string
                pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
                #print(pymsg)
                logFile(log_file.replace(".log", " ERROR.log"), pymsg)
                del pymsg, tb, sys, tbinfo

            #del array

            if region_abb in ['WC_ANN', 'WC_TRI',]:
                msg = '>-> Updating the Region Field for {0}'.format(region)
                logFile(log_file, msg); del msg

                arcpy.management.CalculateField(in_table=tmp_table, field="Region", expression="'{0}'".format(region), expression_type="PYTHON", code_block="")


            msg = '>-> Adding the StdTime column to the {0} Table and calculating the datetime value'.format(region)
            logFile(log_file, msg); del msg

        # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
        # The following inputs are layers or table views: "NEUS_S_Layer"
        #
        # https://community.esri.com/t5/arcgis-online-questions/arcgis-online-utc-time-zone-converting-to-local-timezone/m-p/188515
        # https://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/convert-timezone.htm
        # https://support.esri.com/en/technical-article/000015224
        # https://community.esri.com/t5/arcgis-online-blog/mastering-the-space-time-continuum-2-0-more-about-date-fields/ba-p/891203?searchId=e9792f70-29cb-43d4-a2f5-289e42701d7a&searchIndex=4&sr=search
        # https://community.esri.com/t5/arcgis-online-blog/golden-rules-to-mastering-space-and-time-on-the-web/ba-p/891069?searchId=2e78f04a-625c-4456-9dd7-27362e4136c9&searchIndex=0&sr=search
        # https://stackoverflow.com/questions/36623786/in-python-how-do-i-create-a-timezone-aware-datetime-from-a-date-and-time
        # http://pytz.sourceforge.net/

            arcpy.management.AddField(in_table=tmp_table, field_name="StdTime", field_type="DATE", field_precision="", field_scale="", field_length="", field_alias="StdTime", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

            # The following calculates the time stamp for the feature class
            codeBlock = """def getDate(region, year):
                              from datetime import datetime
                              import pytz
                              regionDateDict = {# Region : Month, Day, Hour, Minute, Second, Time Zone
                                                'Aleutian Islands'   : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                'Eastern Bering Sea' : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                'Gulf of Alaska' : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                'Gulf of Mexico' : [1, 1, 0, 0, 0, 'US/Central'],
                                                'Hawaii Islands' : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                "Hawai'i Islands" : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                'Hawaii' : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                'Northeast US Fall' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Northeast US Spring' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Southeast US Spring' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Southeast US Summer' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Southeast US Fall' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'West Coast Annual' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Triennial' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Annual 2003-Present' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Triennial 1977-2004' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Annual (2003-Present)' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Triennial (1977-2004)' : [1, 1, 0, 0, 0, 'US/Pacific'],}
                              month, day, hour, min, sec, timeZone = regionDateDict[region]
                              fmt = "%m/%d/%Y %H:%M:%S"
                              local = pytz.timezone(timeZone)
                              naive = datetime.strptime("{0}/{1}/{2} {3}:{4}:{5}".format(month, day, year, hour, min, sec), fmt)
                              #local_dt = local.localize(naive, is_dst=True)
                              local_dt = local.localize(naive, is_dst=False)
                              utc_dt = local_dt.astimezone(pytz.utc)
                              #return utc_dt.strftime(fmt)
                              return utc_dt"""

            arcpy.management.CalculateField(tmp_table, "StdTime", expression="getDate( !Region!, !Year! )", expression_type="PYTHON", code_block=codeBlock)
            del codeBlock

            # new_field_order = ["field2", "field3", "field1"]
            # reorder_fields(in_fc, out_fc, new_field_order)

            # A new order of fields that put like things together
            # new_field_order = ['OBJECTID', 'CSVFILEID', 'OARegion', 'HUALID', 'Species', 'CommonName', 'Year', 'WTCPUE', 'WTCPUECubeRoot', 'Stratum', 'StratumArea', 'Depth', 'Latitude', 'Longitude', 'StdTime']
            # new_field_order = ['OBJECTID', 'CSVFILEID', 'OARegion', 'HUALID', 'Species', 'CommonName', 'SpeciesCommonName', 'CommonNameSpecies', 'Year', 'WTCPUE', 'WTCPUECubeRoot', 'Stratum', 'StratumArea', 'Depth', 'Latitude', 'Longitude', 'StdTime']
            # Drops'CSVFILEID',
            new_field_order = ['OBJECTID', 'Region', 'SampleID', 'Species', 'CommonName', 'SpeciesCommonName', 'CommonNameSpecies', 'CoreSpecies', 'Year', 'StdTime', 'WTCPUE', 'WTCPUECubeRoot', 'Stratum', 'StratumArea', 'Depth', 'Latitude', 'Longitude',]


            # Sends the input feature class to the field reorder function
            msg = '>-> Reordering the fields in the {0} Table'.format(region)
            logFile(log_file, msg); del msg
            #
            reorder_fields(tmp_table, out_table, new_field_order)

            # Cleanup
            del new_field_order

            # Remove the temporary feature class
            arcpy.management.Delete(tmp_table)
            del tmp_table

            msg = "Table: {0}".format(csv_file)
            logFile(log_file, msg); del msg
            all_years = unique_values(csv_file, "Year")
            #print(all_years)
            min_year = min(all_years)
            max_year = max(all_years)
            msg = "\t Years: {0}".format(', '.join([str(y) for y in all_years]))
            logFile(log_file, msg); del msg
            msg = "\t Min Year: {0}".format(min_year)
            logFile(log_file, msg); del msg
            msg = "\t Max Year: {0}".format(max_year)
            logFile(log_file, msg); del msg

            #species = unique_values(csv_file, "Species")

            species_lyr = arcpy.management.MakeTableView(csv_file, '{0} Table View'.format(csv_file))

            species = unique_values(species_lyr, "Species")

            for specie in species:
                msg = "\t Species: {0}".format(specie)
                logFile(log_file, msg); del msg
                #specie_lyr = arcpy.management.MakeTableView(csv_file, '{0} Table View'.format(csv_file), "Species = '{0}'".format(specie))

                # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
                # The following inputs are layers or table views: "ai_csv"
                arcpy.management.SelectLayerByAttribute(in_layer_or_view=species_lyr, selection_type="NEW_SELECTION", where_clause="Species = '{0}' AND WTCPUE > 0.0".format(specie))

                all_specie_years = unique_values(species_lyr, "Year")
                msg = "\t\t Years: {0}".format(', '.join([str(y) for y in all_specie_years]))
                logFile(log_file, msg); del msg

                arcpy.management.SelectLayerByAttribute(in_layer_or_view=species_lyr, selection_type="NEW_SELECTION", where_clause="Species = '{0}'".format(specie))

                if all_years == all_specie_years:
                    msg = "\t\t Match for: {0}".format(specie)
                    logFile(log_file, msg); del msg
                    arcpy.management.CalculateField(in_table=species_lyr, field="CoreSpecies", expression="'Yes'", expression_type="PYTHON", code_block="")
                else:
                    msg = "\t\t @@@@ No Match for: {0} @@@@".format(specie)
                    logFile(log_file, msg); del msg
                    arcpy.management.CalculateField(in_table=species_lyr, field="CoreSpecies", expression="'No'", expression_type="PYTHON", code_block="")

                arcpy.management.SelectLayerByAttribute(species_lyr, "CLEAR_SELECTION")
                #arcpy.management.Delete("Species = '{0}'".format(specie))
                #del specie_lyr
                del specie, all_specie_years

            arcpy.management.Delete('{0} Table View'.format(csv_file))
            del species_lyr

            del all_years, min_year, max_year, species

            # field_alias = {'CSVFILEID' : '',
            #                'Region' : '',
            #                'SampleID' : '',
            #                'Species' : '',
            #                'CommonName' : '',
            #                'Year' : '',
            #                'WTCPUE' : '',
            #                'WTCPUECubeRoot' : '',
            #                'Stratum' : '',
            #                'StratumArea' : '',
            #                'Depth' : '',
            #                'Latitude' : '',
            #                'Longitude' : ''
            #                'StdTime' : ''}

            msg = '>-> Updating the field alias in the {0} Table'.format(region)
            logFile(log_file, msg); del msg

            fields = arcpy.ListFields(out_table)
            for field in fields:
                if '_' in field.aliasName:
                    arcpy.management.AlterField(out_table, field.name, new_field_alias = field.aliasName.replace('_', ' '))
            del field, fields

            # Add Metadata
            addMetadata(out_table)

            msg = '> Generating {0} Table complete ON {1}'.format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg); del msg

##        elif arcpy.Exists(out_table):
##            msg = '>-> {0} CSV Table Exists'.format(region)
##            logFile(log_file, msg); del msg
##        else:
##            msg = '>-> Nothing to do {0} CSV Table'.format(region)
##            logFile(log_file, msg); del msg

            # Cleanup

            del out_table

            #Final benchmark for the region.
            msg = "ENDING REGION {} COMPLETED ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg); del msg

            # Elapsed time
            end_time = time()
            elapse_time =  end_time - region_start_time
            msg = u"Elapsed Time {0} (H:M:S)\n".format(strftime("%H:%M:%S", gmtime(elapse_time)))
            logFile(log_file, msg); del msg, end_time, elapse_time, region_start_time

            # Clean up
            del region_abb, region, csv_file, region_shape, region_boundary
            del region_georef, region_contours, region_cell_size, region_name
            del dataset_name

        del pd, np
        #Final benchmark for the function.
        msg = "ENDING {0} COMPLETED ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time)))
        logFile(log_file, msg); del msg, end_time, elapse_time

        del log_file, start_time

    except: # This code is executed only if an exception was raised in the
            # try block. Code executed in this block is just like normal code:
            # if there is an exception, it will not be automatically caught
            # (and probably stop the program).
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        py_msg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        arcpy_msg = "Arcpy Errors:\n" + arcpy.GetMessages(2) + "\n"
        #arcpy.AddError(py_msg)
        #arcpy.AddError(arcpy_msg)
        logFile(log_file.replace(".log", " ERROR.log"), py_msg)
        logFile(log_file.replace(".log", " ERROR.log"), arcpy_msg)
        del tb, tbinfo, py_msg, arcpy_msg, sys, traceback

    else: # This code is executed only if no exceptions were raised in the try
          # block. Code executed in this block is just like normal code: if
          # there is an exception, it will not be automatically caught
          # (and probably stop the program). Notice that if the else block is
          # executed, then the except block is not, and vice versa. This block
          # is optional.
        # Use pass to skip this code block
        # pass

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    finally: # This code always executes after the other blocks, even if there
             # was an uncaught exception (that didn’t cause a crash, obviously)
             # or a return statement in one of the other blocks. Code executed
             # in this block is just like normal code: if there is an exception,
             # it will not be automatically caught (and probably stop the
             # program). This block is also optional.

        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if "function" not in key]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

def listEnvironments():
    environments = arcpy.ListEnvironments()
    #print(environments)
    # Sort the environment names
    environments.sort()
    for environment in environments:
        # Format and print each environment and its current setting.
        # (The environments are accessed by key from arcpy.env.)
        print("{0:<30}: {1}".format(environment, arcpy.env[environment]))
        del environment
    del environments

def listFolder(folder):
    # List folder contents
    filenames = os.listdir(folder)
    return True if filenames else False
    del filenames

def logFile(log_file, msg):
    try:
        arcpy.AddMessage(msg)
        my_log = open(log_file, "a+")
        my_log.write(msg + '\n')
        my_log.close
        del my_log
    except:
        print("Log Folder / File  may be missing.")
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        py_msg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        arcpy_msg = "Arcpy Errors:\n" + arcpy.GetMessages(2) + "\n"
        #arcpy.AddError(py_msg)
        #arcpy.AddError(arcpy_msg)
        #print(py_msg)
        #print(arcpy_msg)
        logFile(log_file, py_msg); del py_msg
        logFile(log_file, arcpy_msg); del arcpy_msg
        del tb, tbinfo, traceback

def main():
    # Done: - Remove Indicator columns for standard error? Done: Replaced
    #         StandardError with SE
    # TODO: - new NOAA GP feature table for master species information (Melissa
    #         provides data)
    # Done: - Add column(s) to Indicator table to accommodate product name (e.g.
    #         only IDW Interpolation for now)
    # Done: - Add columns for species filtering: Taxonomic grouping, Fishery
    #         Management Council, Fishery Management Plan (comes from master
    #         species table)
    # TODO: - update DisMAP data based on new survey data
    # TODO: - InPort metadata changes as needed

    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # The Base Directory folder is the output location for project folders.
        global BASE_DIRECTORY
        BASE_DIRECTORY = os.path.join(cwd, Version)
        # If the Base_Folder is missing, create the folder
        if not os.path.exists( BASE_DIRECTORY ) and not os.path.isdir( BASE_DIRECTORY ):
            os.makedirs( BASE_DIRECTORY )

        # The Log Folder is the output location for log files.
        global LOG_DIRECTORY
        #LOG_DIRECTORY = os.path.join(BASE_DIRECTORY, "Log Folder {0}".format(Version))
        LOG_DIRECTORY = os.path.join(BASE_DIRECTORY, "Log Folder")
        if not os.path.exists( LOG_DIRECTORY ) and not os.path.isdir( LOG_DIRECTORY ):
            os.makedirs( LOG_DIRECTORY )

        # The Analysis Folder is the output location for raster images.
        global IMAGE_DIRECTORY
        #IMAGE_DIRECTORY = os.path.join(BASE_DIRECTORY, "Analysis Folder {0} {1}".format(Version, SoftwareEnvironmentLevel))
        IMAGE_DIRECTORY = os.path.join(BASE_DIRECTORY, "Image Folder")
        # If the Analysis_Folder is missing, create the folder
        if not os.path.exists( IMAGE_DIRECTORY ) and not os.path.isdir( IMAGE_DIRECTORY ):
            os.makedirs( IMAGE_DIRECTORY )

        # This folder contains the CSV files needed to run this script.
        global CSV_DIRECTORY
        #CSV_DIRECTORY = os.path.join(BASE_DIRECTORY, "Fish Data {0}".format(Version))
        CSV_DIRECTORY = os.path.join(BASE_DIRECTORY, "CSV Data Folder")
        # If the Fish Data is missing, create the folder
        if not os.path.exists( CSV_DIRECTORY ) and not os.path.isdir( CSV_DIRECTORY ):
            os.makedirs( CSV_DIRECTORY )
        else:
            if not listFolder(CSV_DIRECTORY):
                print("###--->>> CSV Data Folder is empty")

        # The Map Folder contains source data needed for this script. The source
        # data was provided by Ocean Adapt in the original download file.
        # Updates shape files replace the oroginal data as needed.
        global REGION_SHAPEFILE_DIRECTORY
        REGION_SHAPEFILE_DIRECTORY = os.path.join(BASE_DIRECTORY, "Region Shapefile Folder")
        # If the Map_Shapefiles is missing, create the folder
        if not os.path.exists( REGION_SHAPEFILE_DIRECTORY ) and not os.path.isdir( REGION_SHAPEFILE_DIRECTORY ):
            os.makedirs( REGION_SHAPEFILE_DIRECTORY )
        else:
            if not listFolder( REGION_SHAPEFILE_DIRECTORY ):
                print("###--->>> Region Shapefile Folder is empty")

        # The Mosaic Folder is the output location for the Cloud Raster Format
        # mosaics created from GDB Mosaics using this script
        global MOSAIC_DIRECTORY
        #MOSAIC_DIRECTORY = os.path.join(BASE_DIRECTORY, "Mosaic Folder {0} {1}".format(Version, SoftwareEnvironmentLevel))
        MOSAIC_DIRECTORY = os.path.join(BASE_DIRECTORY, "Mosaic Folder")
        # If Raster_Folder is missing, create the folder
        if not os.path.exists( MOSAIC_DIRECTORY ) and not os.path.isdir( MOSAIC_DIRECTORY ):
            os.makedirs( MOSAIC_DIRECTORY )

        # The EXPORT_METADATA_DIRECTORY Folder is the output location for export
        # metadata
        global EXPORT_METADATA_DIRECTORY
        EXPORT_METADATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "Export Metadata")
        # If EXPORT_METADATA_DIRECTORY is missing, create the folder
        if not os.path.exists( EXPORT_METADATA_DIRECTORY ) and not os.path.isdir( EXPORT_METADATA_DIRECTORY ):
            os.makedirs( EXPORT_METADATA_DIRECTORY )

        # The ARCGIS_METADATA_DIRECTORY Folder is the location for ArcGIS
        # template metadata
        global ARCGIS_METADATA_DIRECTORY
        ARCGIS_METADATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "ArcGIS Metadata")
        # If ARCGIS_METADATA_DIRECTORY is missing, create the folder
        if not os.path.exists( ARCGIS_METADATA_DIRECTORY ) and not os.path.isdir( ARCGIS_METADATA_DIRECTORY ):
            os.makedirs( ARCGIS_METADATA_DIRECTORY )
        else:
            if not listFolder(ARCGIS_METADATA_DIRECTORY):
                print("###--->>> ArcGIS Metadata Folder is empty")

        # The INPORT_METADATA_DIRECTORY Folder is the output location for InPort
        # metadata
        global INPORT_METADATA_DIRECTORY
        INPORT_METADATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "InPort Metadata")
        # If INPORT_METADATA_DIRECTORY is missing, create the folder
        if not os.path.exists( INPORT_METADATA_DIRECTORY ) and not os.path.isdir( INPORT_METADATA_DIRECTORY ):
            os.makedirs( INPORT_METADATA_DIRECTORY )

        # Project Name
        global ProjectName
        #ProjectName = "DisMAP"
        ProjectName = "DisMAP {0}".format(Version)

        # The name of the ArcGIS Pro Project
        global ProjectGIS
        ProjectGIS = os.path.join(BASE_DIRECTORY, "{0}.aprx".format(ProjectName + " " + SoftwareEnvironmentLevel))

        # The name of the ArcGIS Pro Project Toolbox
        global ProjectToolBox
        ProjectToolBox = os.path.join(BASE_DIRECTORY, "{0}.tbx".format(ProjectName + " " + SoftwareEnvironmentLevel))
        #DefaultGDB = os.path.join(BASE_DIRECTORY, "Default.gdb")

        # The ProjectGDB is the output location for data
        global ProjectGDB
        #ProjectGDB = os.path.join(BASE_DIRECTORY, "{0}.gdb".format(ProjectName + " " + SoftwareEnvironmentLevel))
        ProjectGDB = os.path.join(BASE_DIRECTORY, "{0}.gdb".format(ProjectName + " " + SoftwareEnvironmentLevel))
        # If the ProjectGDB is missing, create the folder
        if not os.path.exists(ProjectGDB):
            arcpy.management.CreateFileGDB(BASE_DIRECTORY, ProjectName + " " + SoftwareEnvironmentLevel)

        # Template ArcGIS Pro Project
        template_project = os.path.join(os.path.dirname(BASE_DIRECTORY), "DisMAP Project Template", "DisMAP Project Template.aprx")
        aprx = arcpy.mp.ArcGISProject(template_project)

        # print( aprx.defaultGeodatabase )
        # print( aprx.defaultToolbox )
        # print( aprx.homeFolder )

        if not os.path.exists( ProjectGIS ):
            aprx.defaultGeodatabase = ProjectGDB
            aprx.homeFolder = BASE_DIRECTORY
            #aprx.defaultToolbox = ProjectToolBox
            aprx.saveACopy(ProjectGIS)

        del aprx, template_project

        # The BathymetryGDB is the output location for data
        global BathymetryGDB
        BathymetryGDB = os.path.join(BASE_DIRECTORY, "Bathymetry.gdb")
        # If the BathymetryGDB is missing, create the folder
        if not os.path.exists(BathymetryGDB):
            print(os.path.exists(BathymetryGDB))
            arcpy.management.CreateFileGDB(BASE_DIRECTORY, "Bathymetry")

        # The ScratchFolder is the output location for scratch data
        global ScratchFolder
        #ScratchFolder = os.path.join(BASE_DIRECTORY, "Scratch {0} {1}".format(Version, SoftwareEnvironmentLevel))
        ScratchFolder = os.path.join(BASE_DIRECTORY, "Scratch Folder")
        # If the ScratchFolder is missing, create the folder
        if not os.path.exists( ScratchFolder ) and not os.path.isdir( ScratchFolder ):
            os.makedirs( ScratchFolder )

        # The ScratchGDB is the output location for scratch data
        global ScratchGDB
        ScratchGDB = os.path.join(ScratchFolder, "scratch.gdb")
        if not os.path.exists( ScratchGDB ) and not os.path.isdir( ScratchGDB ):
            arcpy.management.CreateFileGDB(ScratchFolder, "scratch")

        # Get ArcGIS Product Information
        # print(arcpy.GetInstallInfo()['Version'])
        # ## Use the dictionary iteritems to iterate through
        # ##   the key/value pairs from GetInstallInfo
        # d = arcpy.GetInstallInfo()
        # for key, value in list(d.items()):
        #     # Print a formatted string of the install key and its value
        #     #
        #     print("{:<13} : {}".format(key, value))
        #     del key, value
        # del d

        # For testing
        # test = 1/0

        # ###--->>> Declaring Dataset Names
        # The dataset_names variable includes the following information:
        #        dataset_names[0]: The abbreviation of the region (for file/folder structure)
        #        dataset_names[1]: The actual name of the region
        #        dataset_names[2]: The CSV file that contains this region's data
        #        dataset_names[3]: The region shape that gets used for the mask and extent of the environment variable, and the output coordinate system
        #        dataset_names[4]: The boundary shape file ( a single Polyline ) that gets used by arcpy.gp.Idw_sa
        #        dataset_names[5]: ??? The PRJ datum used by the region shapefile (dataset_names[0]). These are included within the ArcGIS installation. Please see
        #                            https://desktop.arcgis.com/en/arcmap/10.5/map/projections/pdf/projected_coordinate_systems.pdf
        #                            for valid Projection Names or inside arcgis itself.
        #                            The variable itself does not appear to be used, it's just there for my reference.
        #        dataset_names[6]: A shapefile containing contour lines for outputting pictures.
        #        dataset_names[7]: Raster cell size
        # In order to automate generating raster files and pictures for the Ocean Adapt website, This array of information was used to allow controlled and regulated so all regions are treated the exact same way.
        global dataset_names
        dataset_names = [
                         [ 'AI', 'Aleutian Islands', 'ai_csv', 'AI_Shape', 'AI_Boundary', 'NAD_1983_2011_UTM_Zone_1N', 'contour_ai', 2000],
                         [ 'EBS', 'Eastern Bering Sea', 'ebs_csv', 'EBS_Shape', 'EBS_Boundary', 'NAD_1983_2011_UTM_Zone_3N', 'contour_ebs', 2000],
                         [ 'GOA', 'Gulf of Alaska', 'goa_csv','GOA_Shape', 'GOA_Boundary', 'NAD_1983_2011_UTM_Zone_5N', 'contour_goa', 2000],

                         [ 'GOM', 'Gulf of Mexico', 'gmex_csv', 'GOM_Shape', 'GOM_Boundary', 'NAD_1983_2011_UTM_Zone_15N', 'contour_gom', 2000],

                         #[ 'HI', 'Hawaii Islands', 'hi_csv','HI_Shape', 'HI_Boundary', 'WGS_1984_UTM_Zone_4N', 'contour_hi', 500],
                         [ 'HI', "Hawai'i Islands", 'hi_csv','HI_Shape', 'HI_Boundary', 'WGS_1984_UTM_Zone_4N', 'contour_hi', 500],

                         [ 'NEUS_F', 'Northeast US Fall', 'neusf_csv', 'NEUS_Fall_Shape', 'NEUS_Fall_Boundary', 'NAD_1983_2011_UTM_Zone_18N', 'contour_neus', 2000],
                         [ 'NEUS_S', 'Northeast US Spring', 'neus_csv', 'NEUS_Spring_Shape', 'NEUS_Spring_Boundary', 'NAD_1983_2011_UTM_Zone_18N', 'contour_neus', 2000],

                         [ 'SEUS_SPR', 'Southeast US Spring', 'seus_spr_csv', 'SEUS_Shape', 'SEUS_Boundary', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],
                         [ 'SEUS_SUM', 'Southeast US Summer', 'seus_sum_csv', 'SEUS_Shape', 'SEUS_Boundary', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],
                         [ 'SEUS_FALL', 'Southeast US Fall', 'seus_fal_csv', 'SEUS_Shape', 'SEUS_Boundary', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],

                         [ 'WC_ANN', 'West Coast Annual 2003-Present', 'wcann_csv', 'WC_Ann_Shape', 'WC_Ann_Boundary', 'NAD_1983_2011_UTM_Zone_10N', 'contour_wc', 2000],
                         [ 'WC_TRI', 'West Coast Triennial 1977-2004', 'wctri_csv', 'WC_Tri_Shape', 'WC_Tri_Boundary', 'NAD_1983_2011_UTM_Zone_10N', 'contour_wc', 2000]
                        ]

        # Test if True
        if FilterDatasets:
            # selected_regions = ['AI', 'EBS', 'GOA', 'GOM', 'HI', 'NEUS_F', 'NEUS_S', 'SEUS_FALL', 'SEUS_SPR', 'SEUS_SUM', 'WC_ANN', 'WC_TRI',]
            # Below are lists used to test different regions
            #selected_datasets = ['HI',]
            # New dataset_names list of lists #-> https://stackoverflow.com/questions/21507319/python-list-comprehension-list-of-lists
            dataset_names = [[r for r in group] for group in dataset_names if group[0] in selected_datasets]
            #del selected_datasets
        #else:
        #    dataset_names = [[r for r in group] for group in dataset_names if group[0] in selected_datasets]

        # Spatial Reference Dictionary
        global dataset_srs
        dataset_srs = {
                       'NAD_1983_2011_UTM_Zone_1N'  : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Aleutian Islands
                       'NAD_1983_2011_UTM_Zone_3N'  : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Eastern Bering Sea
                       'NAD_1983_2011_UTM_Zone_5N'  : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Gulf of Alaska
                       'NAD_1983_2011_UTM_Zone_10N' : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # West Coast
                       'WGS_1984_UTM_Zone_4N'       : "PROJCS['WGS_1984_UTM_Zone_4N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-159.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-5120900 -9998100 450445547.391054;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision", # Hawaii
                       'NAD_1983_2011_UTM_Zone_15N' : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Gulf of Mexico
                       'NAD_1983_2011_UTM_Zone_17N' : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Southeast US
                       'NAD_1983_2011_UTM_Zone_18N' : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Northeast US
                      }

        # Geographic Regions Dictionary
        global geographic_regions
        geographic_regions = {
                              'AI'        : 'Aleutian Islands',
                              'EBS'       : 'Eastern Bering Sea, Bering Sea',
                              'GOA'       : 'Gulf of Alaska',
                              'GOM'       : 'Gulf of Mexico',
                              'GMEX'      : 'Gulf of Mexico',
                              #'HI'        : 'Hawaii Islands',
                              'HI'        : "Hawai'i Islands",
                              'NEUS_F'    : 'Northeast US, East Coast',
                              'NEUSF'     : 'Northeast US, East Coast',
                              'NEUS_S'    : 'Northeast US, East Coast',
                              'NEUS'      : 'Northeast US, East Coast',
                              'SEUS_SPR'  : 'Southeast US, East Coast',
                              'SEUS_SUM'  : 'Southeast US, East Coast',
                              'SEUS_FALL' : 'Southeast US, East Coast',
                              'SEUS_FAL'  : 'Southeast US, East Coast',
                              'WC_ANN'    : 'West Coast',
                              'WCANN'     : 'West Coast',
                              'WC_TRI'    : 'West Coast',
                              'WCTRI'     : 'West Coast',
                              'Aleutian_Islands'    : 'Aleutian Islands',
                              'Eastern_Bering_Sea'  : 'Eastern Bering Sea, Bering Sea',
                              'Gulf_of_Alaska'      : 'Gulf of Alaska',
                              'Gulf_of_Mexico'      : 'Gulf of Mexico',
                              #'Hawaii_Islands'    : 'Hawaii Islands',
                              'Hawaii_Islands'    : "Hawai'i Islands",
                              #'Northeast_US_Fall'   : 'Northeast US, East Coast',
                              'Northeast_US'   : 'Northeast US, East Coast',
                              #'Northeast_US_Spring' : 'Northeast US, East Coast',
                              'Southeast_US'        : 'Southeast US, East Coast',
                              #'Southeast_US_Summer' : 'Southeast US, East Coast',
                              'West_Coast'          : 'West Coast',
                             }

        # Test if SoftwareEnvironmentLevel is Dev or Test, if so, then set
        # selected species. Dev gets a short list and Test gets a longer list.
        # Prod processes all species
        global selected_species
        global FilterSpecies
        if SoftwareEnvironmentLevel in  ["Dev", "Test"]:
            FilterSpecies = True
            if SoftwareEnvironmentLevel == "Dev":
                # TODO: Consider using sets instead
                selected_species = {
                                    # 'AI', 'Aleutian Islands'
                                    # 'EBS', 'Eastern Bering Sea'
                                    # 'GOA', 'Gulf of Alaska'
                                    # 'WC_ANN', 'West Coast Annual (2003-present)'
                                    # 'WC_TRI', 'West Coast Triennial (1977-2004)',
                                    'Acesta sphoni' : 'Limid clam sp.',
                                    'Anthopleura xanthogrammica' : 'Giant green anemone',
                                    'Citharichthys sordidus' : 'Pacific sanddab',
                                    'Doryteuthis (Loligo) opalescens' : 'California market squid',
                                    'Gadus chalcogrammus' : 'Walleye Pollock',
                                    # 'GOM', 'Gulf of Mexico'
                                    'Lutjanus campechanus' : 'red snapper',
                                    # 'HI', 'Hawaii'
                                    'Etelis coruscans' : 'Onaga',
                                    'Hyporthodus quernus' : 'HapuÊ»upuÊ»u',
                                    # 'NEUS_F', 'Northeast US Fall'
                                    # 'NEUS_S', 'Northeast US Spring'
                                    # 'SEUS_SPR', 'Southeast US Spring'
                                    # 'SEUS_SUM', 'Southeast US Summer'
                                    # 'SEUS_FALL', 'Southeast US Fall'
                                    'Centropristis striata' : 'black sea bass',
                                   }
            if SoftwareEnvironmentLevel == "Test":
                # TODO: Consider using sets instead
                selected_species = {
                                    # 'AI', 'Aleutian Islands'
                                    # 'EBS', 'Eastern Bering Sea'
                                    # 'GOA', 'Gulf of Alaska'
                                    # 'WC_ANN', 'West Coast Annual (2003-present)'
                                    # 'WC_TRI', 'West Coast Triennial (1977-2004)',
                                    'Acesta sphoni' : 'Limid clam sp.',
                                    'Anthopleura xanthogrammica' : 'Giant green anemone',
                                    'Calinaticina oldroydii' : "Oldroyd's Fragile Moon Snail",
                                    'Citharichthys sordidus' : 'Pacific sanddab',
                                    'Doryteuthis (Loligo) opalescens' : 'California market squid',
                                    'Gadus chalcogrammus' : 'Walleye Pollock',
                                    'Gadus macrocephalus' : 'Pacific Cod',
                                    'Hippoglossus stenolepis' : 'Pacific Halibut',
                                    'Limanda aspera' : 'yellowfin sole',
                                    # 'GOM', 'Gulf of Mexico'
                                    'Ancylopsetta dilecta' : 'three-eye flounder',
                                    'Ancylopsetta ommata': 'ocellated flounder',
                                    'Chicoreus florifer-dilectus' : '',
                                    'Lutjanus campechanus' : 'red snapper',
                                    'Scomberomorus maculatus' : 'Spanish Mackerel',
                                    # 'HI', 'Hawaii'
                                    'Aphareus rutilans' : 'Lehi',
                                    'Etelis carbunculus' : 'Ehu',
                                    'Etelis coruscans' : 'Onaga',
                                    'Hyporthodus quernus' : 'HapuÊ»upuÊ»u',
                                    'Pristipomoides filamentosus' : 'Opakapaka',
                                    'Pristipomoides sieboldii' : 'Kalekale',
                                    'Pristipomoides zonatus' : 'Gindai',
                                    # 'NEUS_F', 'Northeast US Fall'
                                    # 'NEUS_S', 'Northeast US Spring'
                                    'Centropristis striata' : 'black sea bass',
                                    'Geryon (Chaceon) quinquedens' : 'Red Deep Sea Crab',
                                    'Homarus americanus' : 'American Lobster',
                                    # 'SEUS_SPR', 'Southeast US Spring'
                                    # 'SEUS_SUM', 'Southeast US Summer'
                                    # 'SEUS_FALL', 'Southeast US Fall'
                                    'Brevoortia tyrannus' : 'Atlantic menhaden',
                                    'Micropogonias undulatus' : 'Atlantic croaker',
                                    'Rachycentron canadum' : 'Cobia',
                                   }
        else:
            FilterSpecies = False
            selected_species = {}

        # For filtering on years
        global selected_years
        if FilterYears:
            year_min = 1983; year_max = 1987
            selected_years = [yr for yr in range(year_min, year_max+1)]
            del year_min, year_max
        else:
            selected_years = []

    except: # This code is executed only if an exception was raised in the
            # try block. Code executed in this block is just like normal code:
            # if there is an exception, it will not be automatically caught
            # (and probably stop the program).
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        py_msg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        arcpy_msg = "Arcpy Errors:\n" + arcpy.GetMessages(2) + "\n"
        #arcpy.AddError(py_msg)
        #arcpy.AddError(arcpy_msg)
        logFile(log_file.replace(".log", " ERROR.log"), py_msg)
        logFile(log_file.replace(".log", " ERROR.log"), arcpy_msg)
        del tb, tbinfo, py_msg, arcpy_msg, sys, traceback

    else: # This code is executed only if no exceptions were raised in the try
          # block. Code executed in this block is just like normal code: if
          # there is an exception, it will not be automatically caught
          # (and probably stop the program). Notice that if the else block is
          # executed, then the except block is not, and vice versa. This block
          # is optional.
        # Use pass to skip this code block
        pass

    finally: # This code always executes after the other blocks, even if there
             # was an uncaught exception (that didn’t cause a crash, obviously)
             # or a return statement in one of the other blocks. Code executed
             # in this block is just like normal code: if there is an exception,
             # it will not be automatically caught (and probably stop the
             # program). This block is also optional.

        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if "function" not in key]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function



def reorder_fields(table, out_table, field_order, add_missing=True):
    try:
        # From http://joshwerts.com/blog/2014/04/17/arcpy-reorder-fields/
        """
        Reorders fields in input featureclass/table
        :table:         input table (fc, table, layer, etc)
        :out_table:     output table (fc, table, layer, etc)
        :field_order:   order of fields (objectid, shape not necessary)
        :add_missing:   add missing fields to end if True (leave out if False)
        -> path to output table
        """
        existing_fields = arcpy.ListFields(table)
        existing_field_names = [field.name for field in existing_fields]

        existing_mapping = arcpy.FieldMappings()
        existing_mapping.addTable(table)

        new_mapping = arcpy.FieldMappings()

        def add_mapping(field_name):
            mapping_index = existing_mapping.findFieldMapIndex(field_name)

            # required fields (OBJECTID, etc) will not be in existing mappings
            # they are added automatically
            if mapping_index != -1:
                field_map = existing_mapping.fieldMappings[mapping_index]
                new_mapping.addFieldMap(field_map)

        # add user fields from field_order
        for field_name in field_order:
            if field_name not in existing_field_names:
                raise Exception("Field: {0} not in {1}".format(field_name, table))

            add_mapping(field_name)

        # add missing fields at end
        if add_missing:
            missing_fields = [f for f in existing_field_names if f not in field_order]
            for field_name in missing_fields:
                add_mapping(field_name)

        # use merge with single input just to use new field_mappings
        arcpy.management.Merge(table, out_table, new_mapping)
        return out_table
        ##Usage:
        ##
        ##new_field_order = ["field2", "field3", "field1"]
        ##reorder_fields(in_fc, out_fc, new_field_order)

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

# #
# Function: select_by_fish
#       Selects the rows of fish species data in a 5 year span for use by the
#       Inverse Distance Weighted (IDW) function.
# @param string table: The name of the layer that contains the fish information
# @param string which_fish: The scientific name (Species) of the fish species to look at
# @param string base_year: The origin year (as a string) to get a five year range
#       (-2 to +2) of data for this fish.
# @return integer 1: returns 1 on complete
# #
def select_by_fish(table, which_fish, base_year):
    # This clears the selection just incase it is not empty, even though
    # "NEW_SELECTION" should theroetically take care of this
    # base_year should already be converted to string using str()
    #DEBUG_OUTPUT(3, "Selecing from table `"+ table.name +"`")
    DEBUG_OUTPUT(3, "Selecing from table `"+ str(table) +"`")
    DEBUG_OUTPUT(3, "With Statement:`\"Species\"='"+ which_fish +"' AND \"Year\" >= ("+base_year+"-2 ) AND \"Year\" <= (" + base_year+ "+2)`" )

    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", "\"Species\"='"+ which_fish +"' AND \"Year\" >= ("+base_year+"-2 ) AND \"Year\" <= ("+base_year+"+2 ) " )
    return 1

##
# Function: select_by_fish_no_years
#       Does same thing as @function select_by_fish, just all of the years worth of data.
# @param string table: The name of the layer that contains the fish information
# @param string which_fish: The scientific name (Species) of the fish species to look at
# @return boolean True: returns True on complete.
##
def select_by_fish_no_years(table, which_fish):
    #DEBUG_OUTPUT(3, "Selecing from table `"+ table.name +"`")
    DEBUG_OUTPUT(3, "Selecing from table `"+ str(table) +"`")
    DEBUG_OUTPUT(3, "With Statement:`\"Species\"='"+ which_fish + "'`" )

    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", "\"Species\"='"+ which_fish +"'" )
    return 1

def tableAndFieldReport(workspace, wildcard, datatype, type):
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)
        # Set a start time so that we can see how log things take
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime("%a %b %d %I %M %S %p", localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = "STARTING {0} ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
        logFile(log_file, msg); del msg

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = workspace

        # Set the scratch workspace to the ScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Get a list of tables
        msg = f"Workspace: {workspace}"
        logFile(log_file, msg); del msg


        # Get a list of tables
        msg = 'Get a list of Datasets'
        logFile(log_file, msg); del msg

        fieldNames = []

        arcGISfields = ['Shape', 'Shape_Length', 'Tag', 'HighPS', 'ZOrder',
                        'CenterX', 'Name', 'CenterY', 'ProductName', 'Raster',
                        'UriHash', 'MinPS', 'ServiceName', 'TypeID', 'OBJECTID',
                        'MaxPS', 'Uri', 'LowPS', 'Shape_Area', 'Thumbnail',
                        'ItemTS', 'GroupName', 'Category',]

        dataSets = []

        walk = arcpy.da.Walk(workspace, topdown=True, datatype=datatype, type=type)

        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                if wildcard.lower() in filename.lower():
                    #dataSets.append(os.path.join(dirpath, filename))
                    dataSets.append(filename)

        for dataSet in dataSets:
            # Describe dataset
            desc = arcpy.Describe(dataSet)
            # Print selected dataset and describe object properties
            msg = "Data Set: {0} Data Type: {1}".format(desc.name, desc.dataType)
            logFile(log_file, msg); del msg
            del desc

            # Get list of fields in the table
            fields = arcpy.ListFields(dataSet)

            # Loop through fields
            for field in fields:
                fieldName = field.name
                fieldAliasName = field.aliasName
                fieldType = field.type
                fieldLength = field.length
                fieldEditable = field.editable
                fieldRequired = field.required
                fieldScale = field.scale
                fieldPrecision = field.precision

                fieldNames.append(fieldName)

                state = "Esri" if field.name in arcGISfields else "DisMAP"

                msg = "\t Field:       {0} ({1})\n".format(fieldName, state)
                msg = msg + "\t Alias:       {0}\n".format(fieldAliasName)
                msg = msg + "\t Type:        {0}\n".format(fieldType)
                msg = msg + "\t Length:      {0}\n".format(fieldLength)
                msg = msg + "\t Editable:    {0}\n".format(fieldEditable)
                msg = msg + "\t Required:    {0}\n".format(fieldRequired)
                msg = msg + "\t Scale:       {0}\n".format(fieldScale)
                msg = msg + "\t Precision:   {0}\n".format(fieldPrecision)
                logFile(log_file, msg); del msg

                # This is for printing a list of attributes for the XML metadata file
                # msg = msg + '\t\t\t\t<attrlabl Sync="TRUE">{0}</attrlabl>\n'.format(fieldName))
                # msg = msg + '\t\t\t\t<attalias Sync="TRUE">{0}</attalias>\n'.format(fieldAliasName))
                # msg = msg + '\t\t\t\t<attrtype Sync="TRUE">{0}</attrtype>\n'.format(fieldType))
                # msg = msg + '\t\t\t\t<attwidth Sync="TRUE">{0}</attwidth>\n'.format(fieldLength))
                # msg = msg + '\t\t\t\t<atprecis Sync="TRUE">{0}</atprecis>\n'.format(fieldPrecision))
                # msg = msg + '\t\t\t\t<attscale Sync="TRUE">0</attscale>\n')
                # msg = msg + '\t\t\t\t<attrdef>{0}</attrdef>\n'.format(fieldAliasName))
                # msg = msg + '\t\t\t\t<attrdefs>{0}</attrdefs>\n'.format(state))
                # logFile(log_file, msg); del msg

                del field, fieldName, fieldAliasName, fieldType
                del fieldLength, fieldEditable, fieldRequired, fieldScale
                del fieldPrecision, state

            del dataSet, fields

        del workspace, wildcard, fieldNames, arcGISfields, dataSets
        del walk, dirpath, dirnames, filenames, filename, datatype, type

        #Final benchmark for the region.
        msg = "ENDING {0} COMPLETED ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time)))
        logFile(log_file, msg); del msg

        del log_file, start_time, end_time, elapse_time

    except: # This code is executed only if an exception was raised in the
            # try block. Code executed in this block is just like normal code:
            # if there is an exception, it will not be automatically caught
            # (and probably stop the program).
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        py_msg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        arcpy_msg = "Arcpy Errors:\n" + arcpy.GetMessages(2) + "\n"
        #arcpy.AddError(py_msg)
        #arcpy.AddError(arcpy_msg)
        logFile(log_file.replace(".log", " ERROR.log"), py_msg)
        logFile(log_file.replace(".log", " ERROR.log"), arcpy_msg)
        del tb, tbinfo, py_msg, arcpy_msg, sys, traceback

    else: # This code is executed only if no exceptions were raised in the try
          # block. Code executed in this block is just like normal code: if
          # there is an exception, it will not be automatically caught
          # (and probably stop the program). Notice that if the else block is
          # executed, then the except block is not, and vice versa. This block
          # is optional.
        # Use pass to skip this code block
        # pass

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    finally: # This code always executes after the other blocks, even if there
             # was an uncaught exception (that didn’t cause a crash, obviously)
             # or a return statement in one of the other blocks. Code executed
             # in this block is just like normal code: if there is an exception,
             # it will not be automatically caught (and probably stop the
             # program). This block is also optional.

        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if "function" not in key]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

# #
# Function: unique_field
#       Generic function to return all the unique values within a specified field
# @param string table: The name of the layer that contains the field to be searched
# @param string field: which field to look
# @return array: a sorted array of unique values.
# #
def unique_field(table,field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

# #
# Function: unique_fish
#       Gets the unique fish species within a dataset
# @param string table: The name of the layer that contains the fish information
# @return array: a sorted array of unique fish species.
# #
def unique_fish(table):
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    with arcpy.da.SearchCursor(table, ["Species"]) as cursor:
        return sorted({row[0] for row in cursor})

# #
# Function: unique_fish_dict
#       Gets the unique fish species and common name within a dataset
# @param string table: The name of the layer that contains the fish information
# @return array: a sorted array of unique fish species and common name.
# #
def unique_fish_dict(table):
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    with arcpy.da.SearchCursor(table, ["Species", "CommonName", "CoreSpecies"]) as cursor:
        return {row[0] : [row[1], row[2]] for row in cursor if row[0] not in ['NA', '']}

# #
# Function: unique_year
#       Gets the unique years (that have data) for a fish species
# @param string table: The name of the layer that contains the fish information
# @param string which_fish: The scientific name (Species) of the fish species to look at
# @return array: a sorted year array so we can go in order.
# #
def unique_year(table, which_fish):
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    with arcpy.da.SearchCursor(table, ["Year"], "\"Species\"='"+ which_fish +"'") as cursor:
        return sorted({row[0] for row in cursor})

# #
# Function: unique_years
#       Gets the unique years in a table
# @param string table: The name of the layer
# @return array: a sorted year array so we can go in order.
# #
def unique_years(table):
    #print("in table function")
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    #msg = arcpy.GetMessages()
    #msg = ">->->-> {0}".format(msg.replace('\n', '\n>->->-> '))
    #print(msg)
    #arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", "Year IS NOT NULL AND Variable NOT IN ('Species Richness')")
    arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", "Year IS NOT NULL")
    #msg = arcpy.GetMessages()
    #msg = ">->->-> {0}".format(msg.replace('\n', '\n>->->-> '))
    #print(msg)
    #with arcpy.da.SearchCursor(table, ["year"]) as cursor:
    with arcpy.da.SearchCursor(table, ["Year"]) as cursor:
        #for row in cursor: print(row[0])
        return sorted({row[0] for row in cursor})

def unique_values(table, field):  ##uses list comprehension
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

if __name__ == '__main__':
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        # Set Current Working Directory to the path of this Python script
        cwd = os.path.dirname(__file__)
        # Change the path to the Current Working Directory
        os.chdir(cwd)

        # Specify the Log File Folder (directory)
        log_file_folder = os.path.join(cwd, "Log Files")

        # If the Log Files folder is missing, create the folder
        if not os.path.exists( log_file_folder ) and not os.path.isdir( log_file_folder ):
            os.makedirs( log_file_folder )
        else:
            # Clear Folder first
            clearFolder(log_file_folder)
            pass

        # Get the name of the script
        script_file = os.path.basename(__file__).strip('.py')

        # The timestr variable capture the current date and time the script is
        # executed
        # timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime("%a %b %d %I %M %S %p", localtime())

        # The log file is For benchmarking, capturing general messages and
        # errors.
        log_file = os.path.join(log_file_folder, f"{script_file} {timestr}.log")
        # Clean-up
        del timestr

        # Write a message to the log file
        msg = "STARTING {0} ON {1}".format(script_file, strftime("%a %b %d %I:%M:%S %p", localtime()))
        logFile(log_file, msg); del msg

# ###--->>>

        # Version and Date Code
        # December 1 2022
        # Version = "December 1 2022"
        # DateCode = "20221201"

        # December 15 2022
        Version = "December 15 2022"
        DateCode = "20221215"

        # Software Environment Level
        SoftwareEnvironmentLevel = "Dev" # For use on Local laptop
        #SoftwareEnvironmentLevel = "Test" # For use on Local laptop and Windows Instance
        #SoftwareEnvironmentLevel = "Prod" # For use on Windows Instance

        # Set to True if we want to filter on certian one or more regions, else
        # False to process all regions
        FilterDatasets = False
        # selected_regions = ['AI', 'EBS', 'GOA', 'GOM', 'HI', 'NEUS_F', 'NEUS_S', 'SEUS_FALL', 'SEUS_SPR', 'SEUS_SUM', 'WC_ANN', 'WC_TRI',]
        # Below are lists used to test different regions
        selected_datasets = ['HI',]

        # Set to True if we want to filter on certian years, else False to
        # process all years
        FilterYears = False

        # The main() is for testing and project setup
        main()

    # ###--->>> Step #1
    # ###--->>> Create Tables Start
        # Create Tables: True or False
        CreateTemplateTables = False
        # Create empty tables, if CreateTemplateTables is set to True
        if CreateTemplateTables:
            createTemplateTables()
        del createTemplateTables, CreateTemplateTables
    # ###--->>> Create Tables End

    # ###--->>> Step #2
    # ###--->>> Import CSV Tables Start
        # Generate Tables True or False
        CreateCSVTables = False
        # Set ReplaceTable to True or False
        #ReplaceTable = True
        # Generate Tables -- Needs to run next so that Feature classes can be
        # created in the following step.
        if CreateCSVTables:
            createCSVTables()
        del CreateCSVTables, createCSVTables
    # ###--->>> Import CSV Tables End


    # ###--->>> Step #
    # ###--->>> Table and Field Report Start
        # Table and Field Report: True or False
        TableAndFieldReport = False
        # Workspace: ws
        ws = ProjectGDB
        # Wildcard: wc
        # wc = ""
        # wc = "HI_CSV"
        #wc = "_Template"
        wc = "_csv"
        # Data Type: dt
        # dt = ["Any",]
        # dt = ["Table", "FeatureClass"]
        dt = ["Table"]
        # Type: t
        t = ["Any",]
        #t = ["Polygon",]

        if TableAndFieldReport: tableAndFieldReport(ws, wc, dt, t)
        del tableAndFieldReport, TableAndFieldReport, ws, wc, dt, t

    # ###--->>> Table and Field Report End



        del Version, DateCode, SoftwareEnvironmentLevel
        del FilterDatasets, FilterYears

# ###--->>>
        # Compact GDB
        compactGDB(ProjectGDB)

        # Final benchmark
        msg = "ENDING {0} COMPLETED ON {1}".format(script_file, strftime("%a %b %d %I:%M:%S %p", localtime()))
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time)))
        logFile(log_file, msg); del msg

        # Clean up
        del cwd, script_file, start_time, end_time, elapse_time

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        py_msg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        arcpy_msg = "Arcpy Errors:\n" + arcpy.GetMessages(2) + "\n"
        #arcpy.AddError(py_msg)
        #arcpy.AddError(arcpy_msg)
        logFile(log_file, py_msg); del py_msg
        logFile(log_file, arcpy_msg); del arcpy_msg
        del tb, tbinfo, traceback
    else: # This code is executed only if no exceptions were raised in the try
          # block. Code executed in this block is just like normal code: if
          # there is an exception, it will not be automatically caught
          # (and probably stop the program). Notice that if the else block is
          # executed, then the except block is not, and vice versa. This block
          # is optional.
        # Use pass to skip this code block
        pass

    finally:
        # Remove imported modules
        del sys, time, datetime, math, numpy
        del os, inspect, function_name, function
        del localtime, strftime, gmtime

        # Remove defined functions
        del compactGDB, listEnvironments, clearFolder, addMetadata
        del reorder_fields, select_by_fish, select_by_fish_no_years
        del unique_field, unique_fish, unique_fish_dict, unique_year
        del unique_years, unique_values, FilterSpecies

        # Remove declared globals
        del BASE_DIRECTORY, IMAGE_DIRECTORY, CSV_DIRECTORY, REGION_SHAPEFILE_DIRECTORY
        del MOSAIC_DIRECTORY, ProjectGIS, ProjectToolBox, ProjectGDB, ProjectName
        del BathymetryGDB, ScratchGDB, ScratchFolder, EXPORT_METADATA_DIRECTORY
        del ARCGIS_METADATA_DIRECTORY, INPORT_METADATA_DIRECTORY, LOG_DIRECTORY
        del dataset_names, dataset_srs, geographic_regions, selected_species
        del selected_years, selected_datasets, listFolder

        # This is a list of local and global variables that are exclude from
        # lists of variables
        exclude_keys = [ "logging", "main", "exclude_keys", "arcpy", "logFile",
                        "log_file_folder", "log_file" ]

        globalKeys = [key for key in globals().keys() if not key.startswith('__') and key not in exclude_keys]

        if globalKeys:
            msg = "Global Keys: {0}".format(u", ".join(globalKeys))
            #msg = "Global Keys: {0}".format(u', '.join('"{0}"'.format(gk) for gk in globalKeys))
            logFile(log_file, msg); del msg
        del globalKeys, exclude_keys, logFile, log_file, log_file_folder, arcpy

        import gc
        gc.collect()
        del gc