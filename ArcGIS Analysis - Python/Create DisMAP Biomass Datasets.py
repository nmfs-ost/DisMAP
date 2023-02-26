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
# ### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #
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
# ### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #

import os
import arcpy
import multiprocessing
from time import time, localtime, strftime, gmtime

# Get the name of the running fuction using inspect
import inspect
function_name = lambda: inspect.stack()[1][3]

##import logging
### Create a logger to report
##logger = logging.getLogger()
##logger.setLevel(logging.DEBUG)
##formatter = logging.Formatter('%(asctime)s - %(message)s')
##ch = logging.StreamHandler()
##ch.setLevel(logging.DEBUG)
##ch.setFormatter(formatter)
##logger.addHandler(ch)

# ###--->>> Defs
def addMetadata(item, log_file):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

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

        #msg = f"\t Dataset: {os.path.basename(item)}\n"

        #msg = msg + f"\t\t Title: {md.title}\n"

        #msg = msg + f"\t\t Tags: {md.tags}\n"

        #msg = msg + f"\t\t Summary: {md.summary}\n"

        #msg = msg + f"\t\t Description: {md.description}\n"

        #msg = msg + f"\t\t Credits: {md.credits}\n"
        #logFile(log_file, msg); del msg


        # Delete all geoprocessing history and any enclosed files from the item's metadata
        if not md.isReadOnly:
            md.deleteContent('GPHISTORY')
            md.deleteContent('ENCLOSED_FILES')
            md.save()
            md.reload()

        del md, item

        #Final benchmark for the region.
        #msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        #logFile(log_file, msg); del msg

        # Elapsed time
        #end_time = time()
        #elapse_time =  end_time - start_time
        #msg = f"Elapsed Time {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        #logFile(log_file, msg); del msg

        #del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    finally: # This code always executes after the other blocks, even if there
             # was an uncaught exception (that didn’t cause a crash, obviously)
             # or a return statement in one of the other blocks. Code executed
             # in this block is just like normal code: if there is an exception,
             # it will not be automatically caught (and probably stop the
             # program). This block is also optional.

        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            logFile(log_file, msg); del msg

        del localKeys, function

def alterFieldAlias(tb, alias_dict, log_file):
    try:
        msg = f'>-> Updating the field alias in the Table'
        logFile(log_file, msg); del msg

        fields = arcpy.ListFields(tb)
        for field in fields:
            if field.name in alias_dict.keys():
                arcpy.management.AlterField(tb, field.name, new_field_alias = alias_dict[field.name])
            del field
        del fields

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg, sys

def calculateCoreSpecies(csv_table, log_file):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        #timestr = strftime('%a %b %d %I %M %S %p', localtime())
        #log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        #del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        msg = f"Table: {os.path.basename(csv_table)}"
        logFile(log_file, msg); del msg

        # Get  unique list of years from the table
        all_years = unique_values(csv_table, "Year")

        PrintListOfYears = False
        if PrintListOfYears:
            # Print list of years
            msg = f"\t Years: {', '.join([str(y) for y in all_years])}"
            logFile(log_file, msg); del msg

            # Get minimum year (first year) and maximum year (last year)
            min_year, max_year = min(all_years), max(all_years)

            # Print min year
            msg = f"\t Min Year: {min_year} and Max Year: {max_year}"
            logFile(log_file, msg); del msg
            del min_year, max_year

            # Identify core species
            #print(csv_table)

        del PrintListOfYears

        msg = f"\t Creating {os.path.basename(csv_table)} Table View"
        logFile(log_file, msg); del msg

        species_table_view = arcpy.management.MakeTableView(csv_table, f'{os.path.basename(csv_table)} Table View')

        unique_species = unique_values(species_table_view, "Species")

        for unique_specie in unique_species:
            msg = f"\t Species: {unique_specie}"
            logFile(log_file, msg); del msg

            # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
            # The following inputs are layers or table views: "ai_csv"
            arcpy.management.SelectLayerByAttribute(in_layer_or_view=species_table_view, selection_type="NEW_SELECTION", where_clause=f"Species = '{unique_specie}' AND WTCPUE > 0.0")

            all_specie_years = unique_values(species_table_view, "Year")
            #msg = f"\t\t Years: {', '.join([str(y) for y in all_specie_years])}"
            #logFile(log_file, msg); del msg

            msg = f"\t Select Species ({unique_specie}) by attribute"
            logFile(log_file, msg); del msg

            arcpy.management.SelectLayerByAttribute(in_layer_or_view=species_table_view, selection_type="NEW_SELECTION", where_clause=f"Species = '{unique_specie}'")

            #msg = f"\t Set CoreSpecies to Yes or No"
            #logFile(log_file, msg); del msg

            if all_years == all_specie_years:
                msg = f"\t\t {unique_specie} is a Core Species"
                logFile(log_file, msg); del msg
                arcpy.management.CalculateField(in_table=species_table_view, field="CoreSpecies", expression="'Yes'", expression_type="PYTHON", code_block="")
            else:
                msg = f"\t\t @@@@ {unique_specie} is not a Core Species @@@@"
                logFile(log_file, msg); del msg
                arcpy.management.CalculateField(in_table=species_table_view, field="CoreSpecies", expression="'No'", expression_type="PYTHON", code_block="")

            arcpy.management.SelectLayerByAttribute(species_table_view, "CLEAR_SELECTION")
            del unique_specie, all_specie_years

        msg = f"\t Deleteing {os.path.basename(csv_table)} Table View"
        logFile(log_file, msg); del msg

        arcpy.management.Delete(f'{csv_table} Table View')
        del species_table_view, unique_species, all_years
        del csv_table

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def clearFolder(folder):
    try:
        # Clear Log Directory
        # elif ClearLogDirectory:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
            del filename, file_path

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg, sys

def compactGDB(gdb, log_file):
    try:
        base_name = os.path.basename(gdb) #.strip('.gdb')
        msg = f"\n###--->>> Compacting GDB: {base_name} <<<---###"
        logFile(log_file, msg); del msg
        arcpy.Compact_management(gdb)
        msg = arcpy.GetMessages().replace('chr(10)', f'chr(10)#---> Compact {base_name} ')
        msg = f"#---> {msg}chr(10)"
        logFile(log_file, msg); del msg

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

##def CreateIDWRasters():
##    try: # The code with the exception that you want to catch. If an exception
##         # is raised, control flow leaves this block immediately and goes to
##         # the except block
##
##        # Uses the inspect module and a lamda to find name of this function
##        function = function_name()
##        # arcpy.AddMessage(function)
##
##        # Set a start time so that we can see how log things take
##        start_time = time()
##
##        # For benchmarking.
##        #timestr = strftime("%Y%m%d-%H%M%S")
##        timestr = strftime('%a %b %d %I %M %S %p', localtime())
##        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
##        del timestr
##
##        # Write a message to the log file
##        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##        # Set the workspace to the workspace
##        arcpy.env.workspace = ProjectGDB
##
##        # Set the scratch workspace to the ScratchGDB
##        arcpy.env.scratchWorkspace = ScratchGDB
##
##        # Set the overwriteOutput to True
##        arcpy.env.overwriteOutput = True
##
##        # Use all of the cores on the machine.
##        arcpy.env.parallelProcessingFactor = "100%"
##
##        # Set Log Metadata to False in order to not record all geoprocessing
##        # steps in metadata
##        arcpy.SetLogMetadata(False)
##
##        # Set the compression environment to LZ77
##        arcpy.env.compression = "LZ77"
##
##        # Start looping over the datasets array as we go region by region.
##        for dataset in datasets:
##            # Assigning variables from items in the chosen table list
##            layercode = dataset[0]
##            region = dataset[1]
##            #layercode_csv_table = dataset[2]
##            #layercode_shape = dataset[3]
##            #layercode_boundary = dataset[4]
##            layercode_georef = dataset[5]
##            #layercode_contours = dataset[6]
##            cellsize = dataset[7]
##            del dataset
##
##            layercode_start_time = time()
##
##            # Write a message to the log file
##            msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg
##
##            # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
##            msg = f'> Generating {region} Biomass Rasters'
##            logFile(log_file, msg); del msg
##
##            # Get the reference system defined for the region in datasets
##            #layercode_sr = dataset_srs[layercode_georef]
##            layercode_sr = arcpy.SpatialReference(layercode_georef)
##            arcpy.env.outputCoordinateSystem = layercode_sr
##            arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
##
##            # Delete after last use
##            del layercode_georef, layercode_sr
##
##            arcpy.env.cellSize = cellsize
##
##            layercode_raster_mask = f"{layercode}_Raster_Mask"
##
##            # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
##            arcpy.env.extent = arcpy.Describe(layercode_raster_mask).extent
##            arcpy.env.mask = layercode_raster_mask
##            arcpy.env.snapRaster = layercode_raster_mask
##            del layercode_raster_mask
##
##            msg = f">-> Make Feature Layer for {layercode}_Sample_Locations"
##            logFile(log_file, msg); del msg
##
##            # Prepare the points layer
##            layercode_sample_locations = os.path.join(ProjectGDB, f"{layercode}_Sample_Locations")
##            layercode_sample_locations_layer = arcpy.management.MakeFeatureLayer(layercode_sample_locations, "Region Sample Locations Layer")
##            del layercode_sample_locations
##
##            # Add the YearWeights feild
##            fields =  [f.name for f in arcpy.ListFields(layercode_sample_locations_layer)]
##            if "YearWeights" not in fields:
##                # Add the YearWeights field to the Dataset. This is used for the IDW modeling later
##                arcpy.management.AddField(layercode_sample_locations_layer, "YearWeights", "SHORT", field_alias = "Year Weights")
##            del fields
##
##            result = arcpy.management.GetCount(layercode_sample_locations_layer)
##            msg = f'>-> {layercode}_Sample_Locations has {result[0]} records'
##            logFile(log_file, msg); del msg, result
##
##            layercode_unique_species = unique_species( layercode_sample_locations_layer )
##            # print(f"{', '.join(layercode_unique_species)}\n")
##
##            # Finally we will start looping of the uniquely identified fish in this csv.
##            for layercode_unique_specie in layercode_unique_species:
##                # We prepare a place so that we can place fish data relevant to the fish species we're looking at.
##                #print(layercode_unique_specie)
##
##                layercode_unique_specie_dir = layercode_unique_specie.replace('(','').replace(')','')
##
##                msg = f"#---> Creating Raster Files for {layercode_unique_specie} in directory: {layercode_unique_specie_dir}"
##                logFile(log_file, msg); del msg
##
##                # Create a special folder for them
##                layercode_unique_specie_dir_path = os.path.join(IMAGE_DIRECTORY, layercode, layercode_unique_specie_dir)
##                if not os.path.exists( layercode_unique_specie_dir_path  ) and not os.path.isdir( layercode_unique_specie_dir_path ):
##                    os.makedirs( layercode_unique_specie_dir_path )
##                #print(f"\n#-> {layercode_unique_specie_dir_path}")
##                #print(f"###--->>> {arcpy.ValidateTableName(layercode_unique_specie_dir, layercode_unique_specie_dir_path)}\n")
##                del layercode_unique_specie_dir_path
##
##                msg = f"#---> Select from {layercode}_Sample_Locations all records for {layercode_unique_specie}"
##                logFile(log_file, msg); del msg
##
##                # We are pretty much going to set min to 0, max to STD(OVER YEARS)*2+AVG(OVER YEARS), and the other two shouldn't matter, but we'll set those anyways.
##                select_by_specie_no_years(layercode_sample_locations_layer, layercode_unique_specie, log_file)
##
##                msg = f"#---> Get a list of years for the selected species {layercode_unique_specie}"
##                logFile(log_file, msg); del msg
##
##                # Get all of the unique years
##                specie_unique_years = unique_year(layercode_sample_locations_layer, layercode_unique_specie)
##
##                # Note: in the previous script there was an attemp to find the
##                # earliest year of data, but that doesn't make since as the
##                # unique year list is sorted (ordered).
##                # set the year to the future, where no data should exist.
##                # We will update this variable as we loop over the uniquely
##                # identified years for later.
##                # year_smallest = date.today().year + 100
##                # Since the goal is to get the first (or smallest) year in the list
##                # year_smallest = min(specie_unique_years)
##
##                #print(f"Year smallest in the future: {year_smallest}"
##                for specie_unique_year in specie_unique_years:
##                    msg =  f"#-----> Processing {layercode}_Sample_Locations for {layercode_unique_specie} and year: {specie_unique_year}"
##                    logFile(log_file, msg); del msg
##
##                    msg =  f"#-------> Select from {layercode}_Sample_Locations all records for {layercode_unique_specie} and year {specie_unique_year}"
##                    logFile(log_file, msg); del msg
##
##                    # select the fish species data by the year provided.
##                    #select_by_specie(layercode_sample_locations_layer, layercode_unique_specie, str(specie_unique_year), log_file)
##                    select_by_specie(layercode_sample_locations_layer, layercode_unique_specie, specie_unique_year, log_file)
##
##                    # Calculate YearWeights=3-(abs(Tc-Ti))
##                    arcpy.management.CalculateField(in_table=layercode_sample_locations_layer, field="YearWeights", expression=f"3 - (abs({int(specie_unique_year)} - !Year!))", expression_type="PYTHON", code_block="")
##
##                    # Get the count of records for selected species
##                    result = arcpy.management.GetCount(layercode_sample_locations_layer)
##                    msg = f"#-------> {layercode}_Sample_Locations has {result[0]} records for {layercode_unique_specie} and year {specie_unique_year}"
##                    logFile(log_file, msg); del msg, result
##
##                    # Set variables for search neighborhood
##                    #majSemiaxis = 200000
##                    #minSemiaxis = 200000
##                    majSemiaxis = cellsize * 1000
##                    minSemiaxis = cellsize * 1000
##                    angle = 0
##                    maxNeighbors = 15
##                    minNeighbors = 10
##                    sectorType = "ONE_SECTOR"
##                    searchNeighbourhood = arcpy.SearchNeighborhoodStandard(majSemiaxis, minSemiaxis,
##                                                                           angle, maxNeighbors,
##                                                                           minNeighbors, sectorType)
##
##                    del majSemiaxis, minSemiaxis, angle
##                    del maxNeighbors, minNeighbors, sectorType
##
##                    # Check out the ArcGIS Geostatistical Analyst extension license
##                    arcpy.CheckOutExtension("GeoStats")
##
##                    # Generate the interpolated Raster file and store it on the local hard drive. Can now be used in other ArcGIS Documents
##                    # No special character used, replace spaces, '(', ')' '.', '-' with '_' (underscores)
##                    specie_unique_year_raster = f"{layercode}_{layercode_unique_specie_dir.replace(' ','_')}_{specie_unique_year}"
##                    del specie_unique_year
##
##                    #tmp_raster = os.path.join(ScratchGDB, f"{specie_unique_year_raster.replace('_','')}")
##                    #tmp_raster = os.path.join(ScratchFolder, f"tmp_{specie_unique_year_raster}")
##                    tmp_raster = os.path.join(ScratchFolder, f"{specie_unique_year_raster.replace('_','')}.tif")
##
##                    # Execute IDW using the selected selected species, years, and WTCPUECubeRoot
##                    arcpy.IDW_ga(in_features = layercode_sample_locations_layer,
##                                 z_field = 'WTCPUECubeRoot',
##                                 out_ga_layer = '',
##                                 out_raster = tmp_raster,
##                                 cell_size = '',
##                                 power = 2,
##                                 search_neighborhood = searchNeighbourhood,
##                                 weight_field = "YearWeights")
##
##                    del searchNeighbourhood
##
##                    # Check In GeoStats Extension
##                    arcpy.CheckInExtension("GeoStats")
##
##                    msg =  f"#-------> Creating Raster File {specie_unique_year_raster}.tif for {layercode_unique_specie}"
##                    logFile(log_file, msg); del msg
##
##                    specie_unique_year_raster_path = os.path.join(IMAGE_DIRECTORY, layercode, layercode_unique_specie_dir, specie_unique_year_raster+".tif")
##                    del specie_unique_year_raster
##                    #print()
##                    #print(f"\n#-> {specie_unique_year_raster_path}")
##                    #print(f"###--->>> {arcpy.ValidateTableName(specie_unique_year_raster, specie_unique_year_raster_path)}\n")
##                    #print()
##
##                    # Execute Power to convert the raster back to WTCPUE from WTCPUECubeRoot
##                    out_cube = arcpy.sa.Power(tmp_raster, 3)
##                    #out_cube.save(tmp_raster_power)
##                    out_cube.save(specie_unique_year_raster_path)
##                    #arcpy.management.Delete(out_cube)
##                    del out_cube
##
##                    arcpy.management.Delete(tmp_raster)
##                    del tmp_raster
##
##                    # Add Metadata
##                    addMetadata(specie_unique_year_raster_path, log_file)
##
##                    del specie_unique_year_raster_path
##
##                    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
##                    # The following inputs are layers or table views: "Aleutian_Islands"
##                    arcpy.management.CalculateField(in_table=layercode_sample_locations_layer, field="YearWeights", expression="None", expression_type="PYTHON", code_block="")
##
##                del specie_unique_years, layercode_unique_specie, layercode_unique_specie_dir
##
##            msg = f'>-> Delete non-required fields from {layercode}_Sample_Locations.'
##            logFile(log_file, msg); del msg
##            arcpy.management.DeleteField(layercode_sample_locations_layer, ["YearWeights"])
##            del layercode
##
##            # Delete layercode_sample_locations_layer
##            arcpy.management.Delete(layercode_sample_locations_layer)
##            del layercode_sample_locations_layer
##
##            # Clean up
##            del cellsize, layercode_unique_species,
##
##            # Delete after last use
##
##            # Resets a specific environment setting to its default
##            arcpy.ClearEnvironment("cellSize")
##            arcpy.ClearEnvironment("extent")
##            arcpy.ClearEnvironment("mask")
##            arcpy.ClearEnvironment("outputCoordinateSystem")
##            arcpy.ClearEnvironment("geographicTransformations")
##            arcpy.ClearEnvironment("snapRaster")
##
##            #Final benchmark for the region.
##            msg = f"ENDING REGION {region} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg, region
##
##            # Elapsed time
##            end_time = time()
##            elapse_time =  end_time - layercode_start_time
##            msg = f"Elapsed Time for {region}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)\n"
##            logFile(log_file, msg); del msg, end_time, elapse_time, layercode_start_time
##
##         #Final benchmark for the region.
##        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Elapsed time
##        end_time = time()
##        elapse_time =  end_time - start_time
##        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
##        logFile(log_file, msg); del msg
##
##        del start_time, end_time, elapse_time
##
##    except: # This code is executed only if an exception was raised in the
##            # try block. Code executed in this block is just like normal code:
##            # if there is an exception, it will not be automatically caught
##            # (and probably stop the program).
##        import sys, traceback
##        # Get the traceback object
##        tb = sys.exc_info()[2]
##        tbinfo = traceback.format_tb(tb)[0]
##        # Concatenate information together concerning the error into a message string
##        py_msg = f"PYTHON ERRORS:{chr(10)}Traceback info:{chr(10)}{tbinfo}{chr(10)}Error Info:{chr(10)}{str(sys.exc_info()[1])}"
##        arcpy_msg = f"Arcpy Errors: {chr(10)}{arcpy.GetMessages(2)}{chr(10)}"
##        #arcpy.AddError(py_msg)
##        #arcpy.AddError(arcpy_msg)
##        logFile(log_file.replace(".log", " ERROR.log"), py_msg)
##        logFile(log_file.replace(".log", " ERROR.log"), arcpy_msg)
##        del tb, tbinfo, py_msg, arcpy_msg, sys, traceback
##
##    else: # This code is executed only if no exceptions were raised in the try
##          # block. Code executed in this block is just like normal code: if
##          # there is an exception, it will not be automatically caught
##          # (and probably stop the program). Notice that if the else block is
##          # executed, then the except block is not, and vice versa. This block
##          # is optional.
##        # Use pass to skip this code block
##        # pass
##
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##    finally: # This code always executes after the other blocks, even if there
##             # was an uncaught exception (that didn’t cause a crash, obviously)
##             # or a return statement in one of the other blocks. Code executed
##             # in this block is just like normal code: if there is an exception,
##             # it will not be automatically caught (and probably stop the
##             # program). This block is also optional.
##
##        # Get list of local keys that may need to be deleted.
##        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]
##
##        # If there is a list of local keys, print the list, and then delete
##        # variables
##        if localKeys:
##            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
##            logFile(log_file, msg); del msg
##
##        del localKeys, function

##def CreateIDWTables():
##    try: # The code with the exception that you want to catch. If an exception
##         # is raised, control flow leaves this block immediately and goes to
##         # the except block
##
##        import pandas as pd
##        import numpy as np
##        import warnings
##
##        # Uses the inspect module and a lamda to find name of this function
##        function = function_name()
##        # arcpy.AddMessage(function)
##
##        # Set a start time so that we can see how log things take
##        start_time = time()
##
##        # For benchmarking.
##        #timestr = strftime("%Y%m%d-%H%M%S")
##        timestr = strftime('%a %b %d %I %M %S %p', localtime())
##        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
##        del timestr
##
##        # Write a message to the log file
##        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##        # Set the workspace to the workspace
##        arcpy.env.workspace = ProjectGDB
##
##        # Set the scratch workspace to the ScratchGDB
##        arcpy.env.scratchWorkspace = ScratchGDB
##
##        # Set the overwriteOutput to True
##        arcpy.env.overwriteOutput = True
##
##        # Use all of the cores on the machine.
##        arcpy.env.parallelProcessingFactor = "100%"
##
##        # Set Log Metadata to False in order to not record all geoprocessing
##        # steps in metadata
##        arcpy.SetLogMetadata(False)
##
##        # Start looping over the datasets array as we go region by region.
##        for dataset in datasets:
##            import pandas as pd
##            import numpy as np
##            import warnings
##            # Assigning variables from items in the chosen table list
##            layercode = dataset[0]
##            region = dataset[1]
##            layercode_csv_table = dataset[2]
##            #layercode_shape = dataset[3]
##            #layercode_boundary = dataset[4]
##            #layercode_georef = dataset[5]
##            #layercode_contours = dataset[6]
##            #cellsize = dataset[7]
##            del dataset
##
##            layercode_start_time = time()
##
##
##            # Set the workspace to the workspace
##            arcpy.env.workspace = ProjectGDB
##
##            # Set the scratch workspace to the ScratchGDB
##            arcpy.env.scratchWorkspace = ScratchGDB
##
##            # Write a message to the log file
##            msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg
##
##            input_layercode_csv_table = os.path.join(CSV_DIRECTORY, layercode_csv_table + ".csv")
##
##            # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
##            msg = f'> CSV Table: {os.path.basename(input_layercode_csv_table)}'
##            logFile(log_file, msg); del msg
##
##            # https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/09_timeseries.html?highlight=datetime
##            # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
##            #df = pd.read_csv('my_file.tsv', sep='\t', header=0)  ## not setting the index_col
##            #df.set_index(['0'], inplace=True)
##
##            # C:\. . .\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\lib\site-packages\numpy\lib\arraysetops.py:583:
##            # FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
##            # mask |= (ar1 == a)
##            # A fix: https://www.youtube.com/watch?v=TTeElATMpoI
##            # TLDR: pandas are Jedi; numpy are the hutts; and python is the galatic empire
##            with warnings.catch_warnings():
##                warnings.simplefilter(action='ignore', category=FutureWarning)
##                # DataFrame
##                df = pd.read_csv(input_layercode_csv_table,
##                                 index_col = 0,
##                                 encoding="utf-8",
##                                 #encoding = "ISO-8859-1",
##                                 #engine='python',
##                                 delimiter = ',',
##                                 #dtype = None,
##                                 dtype = {
##                                          "region" : str,
##                                          "sampleid" : str,
##                                          "year" : 'uint16',
##                                          # 'TrawlDate' : 'uint16',
##                                          # 'SurfaceTemperature' : float,
##                                          # 'BottomTemperature' : float,
##                                          "spp" : str,
##                                          "wtcpue" : float,
##                                          "common" : str,
##                                          "stratum" : str,
##                                          "stratumarea" : float,
##                                          "lat" : float,
##                                          "lon" : float,
##                                          "depth" : float,
##                                          },
##                                 )
##            del input_layercode_csv_table
##
##            msg = f'>-> Defining the column names.'
##            logFile(log_file, msg); del msg
##
##            # The original column names from the CSV files are not very
##            # reader friendly, so we are making some changes here
##            #df.columns = [u'Region', u'HUALID', u'Year', u'Species', u'WTCPUE', u'CommonName', u'Stratum', u'StratumArea', u'Latitude', u'Longitude', u'Depth']
##            df.columns = ['OARegion', 'SampleID', 'Year', 'Species', 'WTCPUE', 'CommonName', 'Stratum', 'StratumArea', 'Latitude', 'Longitude', 'Depth']
##
##            # Test if we are filtering on species. If so, a new species list is
##            # created with the selected species remaining in the list
##            #if FilterSpecies and ReplaceTable:
##            if FilterSpecies:
##                msg = f'#---> Filtering table on selected species for {region} Table'
##                logFile(log_file, msg); del msg
##                # Filter data frame
##                df = df.loc[df['Species'].isin(selected_species.keys())]
##            else:
##                msg = f'#---> No species filtering of selected species for {region} Table'
##                logFile(log_file, msg); del msg
##
##            #-->> Species and CommonName
##            msg = f'#--->  Setting Nulls in Species and CommonName to empty strings.'
##            logFile(log_file, msg); del msg
##            # Replace NaN with an empty string. When pandas reads a cell
##            # with missing data, it asigns that cell with a Null or nan
##            # value. So, we are changing that value to an empty string of ''.
##            # Seems to be realivent for Species and CommonName only
##            df.Species    = df.Species.fillna('')
##            df.CommonName = df.CommonName.fillna('')
##            df.Species    = df.Species.replace('Na', '')
##            df.CommonName = df.CommonName.replace('Na', '')
##
##            # Example of how to drop rows in a Data Frame
##            # msg = f'#--->  Droping row where Species have an empty string.'
##            # logFile(log_file, msg); del msg
##            # Drop rows based on a condition. Rows without a species name are not of use
##            # df = df[df.Species != '']
##
##            #-->> Region
##            msg = f'#--->  Adding Region.'
##            logFile(log_file, msg); del msg
##            # Insert column
##            df.insert(df.columns.get_loc('OARegion')+1, 'Region', f"{geographic_regions[layercode]}")
##
##            #-->> SpeciesCommonName
##            msg = f'#--->  Adding SpeciesCommonName and setting it to "Species (CommonName)".'
##            logFile(log_file, msg); del msg
##            # Insert column
##            df.insert(df.columns.get_loc('CommonName')+1, 'SpeciesCommonName', df['Species'] + ' (' + df['CommonName'] + ')')
##
##            #-->> CommonNameSpecies
##            msg = f'#--->  Adding CommonNameSpecies and setting it to "CommonName (Species)".'
##            logFile(log_file, msg); del msg
##            # Insert column
##            df.insert(df.columns.get_loc('SpeciesCommonName')+1, 'CommonNameSpecies', df['CommonName'] + ' (' + df['Species'] + ')')
##
##            #-->> CoreSpecies
##            msg = f'#--->  Adding CoreSpecies and setting it to "No".'
##            logFile(log_file, msg); del msg
##            # Insert column
##            df.insert(df.columns.get_loc('CommonNameSpecies')+1, 'CoreSpecies', "No")
##
##            # ###-->> Depth
##            # msg = f'#--->  Setting the Depth to float16.'
##            # logFile(log_file, msg); del msg
##            # # The Depth column in the CSV files contain a mix of integer and
##            # # double. This converts all to float values to be consistant
##            # #df.Depth = df.Depth.astype(np.float16) # or np.float32 or np.float64
##            # df.Depth = df.Depth.astype(float)
##
##            #-->> WTCPUE
##            msg = f'#--->  Replacing Infinity values with Nulls.'
##            logFile(log_file, msg); del msg
##            # Replace Inf with Nulls
##            # For some cell values in the 'WTCPUE' column, there is an Inf
##            # value representing an infinit
##            df.replace([np.inf, -np.inf], np.nan, inplace=True)
##
##            #-->> WTCPUECubeRoot
##            msg = f'#--->  Adding the WTCPUECubeRoot column and calculating values.'
##            logFile(log_file, msg); del msg
##            # Insert a column to the right of a column and then do a calculation
##            df.insert(df.columns.get_loc('WTCPUE')+1, 'WTCPUECubeRoot', df['WTCPUE'].pow((1.0/3.0)))
##
##            msg = f'>-> Creating the {region} Geodatabase Table'
##            logFile(log_file, msg); del msg
##
##            # ###--->>> Numpy Datatypes
##            # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm
##
##            #print('DataFrame\n----------\n', df.head(10))
##            #print('\nDataFrame datatypes :\n', df.dtypes)
##            #columns = [str(c) for c in df.dtypes.index.tolist()]
##            column_names = list(df.columns)
##            #print(column_names)
##            # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
##            column_formats = ['S50', 'S50', 'S20', '<i4', 'S50', '<f8', '<f8', 'U50', 'U100', 'U100', 'S5', 'S5', 'S25', '<f8', '<f8', '<f8', '<f8']
##            dtypes = list(zip(column_names, column_formats))
##            del column_names, column_formats
##
##            # Cast text as Unicode in the CommonName field
##            df['CommonName'] = df['CommonName'].astype('unicode')
##
##            #print(df)
##            try:
##                array = np.array(np.rec.fromrecords(df.values), dtype = dtypes)
##            except:
##                import sys, traceback
##                # Get the traceback object
##                tb = sys.exc_info()[2]
##                #tb = sys.exc_info()
##                tbinfo = traceback.format_tb(tb)[0]
##                # Concatenate information together concerning the error into a message string
##                pymsg = f"PYTHON ERRORS:{chr(10)}Traceback info:{chr(10)}{tbinfo}{chr(10)}Error Info:{chr(10)}{str(sys.exc_info()[1])}"
##                logFile(log_file.replace(".log", " ERROR.log"), pymsg)
##                del pymsg, tb, sys, tbinfo
##
##            del df, dtypes
##
##            # Temporary table
##            tmp_table = f'memory\{layercode_csv_table}_tmp'
##            #tmp_table = os.path.join(RegionScratchGDB, f'{layercode_csv_table}_tmp'
##
##            try:
##                arcpy.da.NumPyArrayToTable(array, tmp_table)
##                del array
##            except IOError:
##                print(f"Something went wrong: IOError")
##            except:
##                import sys, traceback
##                # Get the traceback object
##                tb = sys.exc_info()[2]
##                #tb = sys.exc_info()
##                tbinfo = traceback.format_tb(tb)[0]
##                # Concatenate information together concerning the error into a message string
##                pymsg = f"PYTHON ERRORS:{chr(10)}Traceback info:{chr(10)}{tbinfo}{chr(10)}Error Info:{chr(10)}{str(sys.exc_info()[1])}"
##                logFile(log_file.replace(".log", " ERROR.log"), pymsg)
##                del pymsg, tb, sys, tbinfo
##
##            msg = f'>-> Adding the StdTime column to the {region} Table and calculating the datetime value'
##            logFile(log_file, msg); del msg
##
##            # Notes on Date/Time fields
##            # https://community.esri.com/t5/arcgis-online-questions/arcgis-online-utc-time-zone-converting-to-local-timezone/m-p/188515
##            # https://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/convert-timezone.htm
##            # https://support.esri.com/en/technical-article/000015224
##            # https://community.esri.com/t5/arcgis-online-blog/mastering-the-space-time-continuum-2-0-more-about-date-fields/ba-p/891203?searchId=e9792f70-29cb-43d4-a2f5-289e42701d7a&searchIndex=4&sr=search
##            # https://community.esri.com/t5/arcgis-online-blog/golden-rules-to-mastering-space-and-time-on-the-web/ba-p/891069?searchId=2e78f04a-625c-4456-9dd7-27362e4136c9&searchIndex=0&sr=search
##            # https://stackoverflow.com/questions/36623786/in-python-how-do-i-create-a-timezone-aware-datetime-from-a-date-and-time
##            # http://pytz.sourceforge.net/
##
##            arcpy.management.AddField(in_table=tmp_table, field_name="StdTime", field_type="DATE", field_precision="", field_scale="", field_length="", field_alias="StdTime", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
##
##            # The following calculates the time stamp for the Dataset
##            # Use Update Cursor instead of Calculate Field
##            with arcpy.da.UpdateCursor(tmp_table, ["StdTime", "OARegion", "Year",]) as cursor:
##                for row in cursor:
##                    row[0] = getDate(row[1], row[2])
##                    cursor.updateRow(row)
##                    del row
##            del cursor
##
##            msg = f'>-> Calculate Core Species for the {region} Table'
##            logFile(log_file, msg); del msg
##
##            # Calculate Core Species
##            calculateCoreSpecies(tmp_table, log_file)
##
##            msg = f'>-> Copying the {region} Table from memory to the GDB'
##            logFile(log_file, msg); del msg
##
##            #out_table = os.path.join(ProjectGDB, layercode_csv_table)
##            out_table = os.path.join(RegionGDB, layercode_csv_table)
##
##            # Execute CreateTable
##            #arcpy.management.CreateTable(ProjectGDB, layercode_csv_table, "_Template_CSV_Data", "", "")
##            arcpy.management.CreateTable(RegionGDB, layercode_csv_table, os.path.join(ProjectGDB, "_Template_CSV_Data"), "", "")
##
##            arcpy.CopyRows_management(tmp_table, out_table, "")
##
##            # Remove the temporary table
##            arcpy.management.Delete(tmp_table)
##            del tmp_table
##
##            msg = f'>-> Updating the field aliases for the {region} Table'
##            logFile(log_file, msg); del msg
##
##            # Field Alias Dictionary
##            field_alias = {
##                           'Region' : 'Region',
##                           'SampleID' : 'Sample ID',
##                           'Species' : 'Species',
##                           'CommonName' : 'Common Name',
##                           'SpeciesCommonName' : 'Species (Common Name)',
##                           'CommonNameSpecies' : 'Common Name (Species)',
##                           'CoreSpecies' : 'Core Species',
##                           'Year' : 'Year',
##                           'WTCPUE' : 'WTCPUE',
##                           'WTCPUECubeRoot' : 'WTCPUE Cube Root',
##                           'Stratum' : '',
##                           'StratumArea' : 'Stratum Area',
##                           'Latitude' : 'Latitude',
##                           'Longitude' : 'Longitude',
##                           'Depth' : 'Depth',
##                           'StdTime' : 'StdTime',
##                          }
##
##            # Alter Field Alias
##            alterFieldAlias(out_table, field_alias, log_file)
##            #
##            del field_alias
##
##            msg = f'>-> Adding metadata to the {region} Table'
##            logFile(log_file, msg); del msg
##
##            # Add Metadata
##            addMetadata(out_table, log_file)
##
##            # Cleanup
##            del out_table
##
##            #Final benchmark for the region.
##            msg = f"ENDING REGION {region} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg
##
##            # Elapsed time
##            end_time = time()
##            elapse_time =  end_time - layercode_start_time
##            msg = f"Elapsed Time for {region}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)\n"
##            logFile(log_file, msg); del msg, end_time, elapse_time, layercode_start_time
##
##            #
##            arcpy.management.Delete(RegionScratchGDB)
##            del RegionScratchGDB, RegionGDB
##
##            # Clean up
##            del layercode, region, layercode_csv_table
##
##        del pd, np, warnings
##
##        #Final benchmark for the function.
##        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Elapsed time
##        end_time = time()
##        elapse_time =  end_time - start_time
##        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
##        logFile(log_file, msg); del msg, end_time, elapse_time
##
##        del log_file, start_time
##
##    # This code is executed only if an exception was raised in the try block.
##    # Code executed in this block is just like normal code: if there is an
##    # exception, it will not be automatically caught (and probably stop the
##    # program).
##    except arcpy.ExecuteError:
##        # Geoprocessor threw an error
##        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
##        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
##        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
##        logFile(log_file.replace(".log", " ERROR.log"), msg); del msg
##    except Exception as e:
##        # Capture all other errors
##        #print(sys.exc_info()[2].tb_lineno)
##        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
##        logFile(log_file.replace(".log", " ERROR.log"), msg); del msg
##
##    # This code is executed only if no exceptions were raised in the try block.
##    # Code executed in this block is just like normal code: if there is an
##    # exception, it will not be automatically caught (and probably stop the
##    # program). Notice that if the else block is executed, then the except block
##    # is not, and vice versa. This block is optional.
##    else:
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##    # This code always executes after the other blocks, even if there was an
##    # uncaught exception (that didn’t cause a crash, obviously) or a return
##    # statement in one of the other blocks. Code executed in this block is just
##    # like normal code: if there is an exception, it will not be automatically
##    # caught (and probably stop the program). This block is also optional.
##    finally:
##        # Get list of local keys that may need to be deleted.
##        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]
##
##        # If there is a list of local keys, print the list, and then delete
##        # variables
##        if localKeys:
##            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
##            logFile(log_file, msg); del msg
##        del localKeys, function

##def createDisMapRegions():
##    try: # The code with the exception that you want to catch. If an exception
##         # is raised, control flow leaves this block immediately and goes to
##         # the except block
##
##        # Uses the inspect module and a lamda to find name of this function
##        function = function_name()
##        # arcpy.AddMessage(function)
##
##        # Set a start time so that we can see how log things take
##        start_time = time()
##
##        # For benchmarking.
##        #timestr = strftime("%Y%m%d-%H%M%S")
##        timestr = strftime('%a %b %d %I %M %S %p', localtime())
##        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
##        del timestr
##
##        # Write a message to the log file
##        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##        # Set the workspace to the workspace
##        arcpy.env.workspace = ProjectGDB
##
##        # Set the scratch workspace to the ScratchGDB
##        arcpy.env.scratchWorkspace = ScratchGDB
##
##        # Set the overwriteOutput to True
##        arcpy.env.overwriteOutput = True
##
##        # Use all of the cores on the machine.
##        arcpy.env.parallelProcessingFactor = "100%"
##
##        # Set Log Metadata to False in order to not record all geoprocessing
##        # steps in metadata
##        arcpy.SetLogMetadata(False)
##
##        # Creating the DisMAP Regions Dataset
##        msg = f'Creating the DisMAP Regions Dataset'
##        logFile(log_file, msg); del msg
##
### ###--->>> DisMAP Regions
##        dismap_regions = os.path.join(ProjectGDB, u"DisMAP_Regions")
##        sp_ref = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]];-20037700 -30241100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
##        arcpy.management.CreateFeatureclass(out_path = ProjectGDB,
##                                            out_name = "DisMAP_Regions",
##                                            geometry_type="POLYLINE",
##                                            template="_Template_DisMAP_Regions",
##                                            has_m="DISABLED",
##                                            has_z="DISABLED",
##                                            spatial_reference=sp_ref,
##                                            config_keyword="",
##                                            spatial_grid_1="0",
##                                            spatial_grid_2="0",
##                                            spatial_grid_3="0")
##        del sp_ref
##
##        # Start looping over the datasets array as we go region by region.
##        for dataset in datasets:
##            # Assigning variables from items in the chosen table list
##            layercode = dataset[0]
##            region = dataset[1]
##            #layercode_csv_table = dataset[2]
##            layercode_shape = dataset[3]
##            #layercode_boundary = dataset[4]
##            layercode_georef = dataset[5]
##            #layercode_contours = dataset[6]
##            #cellsize = dataset[7]
##            del dataset
##
##            layercode_start_time = time()
##
##            # Write a message to the log file
##            msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg
##
##            # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
##            msg = f'> Generating {region} Dataset'
##            logFile(log_file, msg); del msg
##
##            # Get the reference system defined for the region in datasets
##            #layercode_sr = dataset_srs[layercode_georef]
##            layercode_sr = arcpy.SpatialReference(layercode_georef)
##
##            # Delete after last use
##            del layercode_georef
##
##            # Set the output coordinate system to what is needed for the
##            # DisMAP project
##            arcpy.env.outputCoordinateSystem = layercode_sr
##            arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
##
##            # The shapefile used to create the extent and mask for the environment variable
##            layercode_shape_file = os.path.join(REGION_SHAPEFILE_DIRECTORY, layercode, layercode_shape + ".shp")
##            layercode_shape_scratch = os.path.join(ScratchGDB, layercode_shape)
##
##            # Delete after last use
##            del layercode_shape
##
##            msg = f'>-> Copy {region} Shape File to a Dataset.'
##            logFile(log_file, msg); del msg
##            arcpy.management.CopyFeatures(layercode_shape_file, layercode_shape_scratch)
##
##            # Delete after use
##            del layercode_shape_file
##
##            # Get a list of non-required fields
##            fields = [f.name for f in arcpy.ListFields(layercode_shape_scratch) if not f.required]
##
##            msg = f'>-> Delete non-required fields from {region} Dataset.'
##            logFile(log_file, msg); del msg
##            arcpy.management.DeleteField(layercode_shape_scratch, fields)
##
##            # Delete after last use
##            del fields
##
##            msg = f'>-> Adding the "OARegion" field to the {region} Dataset'
##            logFile(log_file, msg); del msg
##
##            # Process: Add Region Field
##            arcpy.management.AddField(layercode_shape_scratch, "OARegion", "TEXT", "", "", "50", "Region", "NULLABLE", "NON_REQUIRED", "")
##
##            msg = f">-> Calculating the 'OARegion' field in the {region} Dataset"
##            logFile(log_file, msg); del msg
##            # Process: Calculate Region Field
##            arcpy.management.CalculateField(layercode_shape_scratch, "OARegion", f'"{region}"', "PYTHON", "")
##
##            msg = f'>-> Adding the "Region" field to the {region} Dataset'
##            logFile(log_file, msg); del msg
##
##            # Process: Add Region Field
##            arcpy.management.AddField(layercode_shape_scratch, "Region", "TEXT", "", "", "50", "Region", "NULLABLE", "NON_REQUIRED", "")
##
##            msg = f">-> Calculating the 'Region' field in the {region} Dataset"
##            logFile(log_file, msg); del msg
##            # Process: Calculate Region Field
##            arcpy.management.CalculateField(layercode_shape_scratch, "Region", f'"{geographic_regions[layercode]}"', "PYTHON", "")
##
##            msg = f">-> Adding the 'ID' field in the {region} Dataset"
##            logFile(log_file, msg); del msg
##            arcpy.management.AddField(layercode_shape_scratch, "ID", "LONG","","","","ID","NULLABLE","NON_REQUIRED")
##
##            msg = f">-> Calculating the 'ID' field in the {region} Dataset"
##            logFile(log_file, msg); del msg
##            # Set ID field value
##            arcpy.management.CalculateField(layercode_shape_scratch, "ID", 1, "PYTHON")
##
##            layercode_survey_area = f"{layercode}_Survey_Area"
##            layercode_boundary_line = f"{layercode}_Boundary_Line"
##
##            msg = f">-> Projecting the {region} Dataset"
##            logFile(log_file, msg); del msg
##            # Project Region Shape File to Region GDB Dataset
##            arcpy.management.Project(layercode_shape_scratch, layercode_survey_area, layercode_sr, "", preserve_shape = "PRESERVE_SHAPE")
##
##            # Delete after use
##            arcpy.management.Delete(layercode_shape_scratch)
##            del layercode_shape_scratch, layercode_sr
##
##            msg = f">-> Converting the {region} Dataset from Polygon to Polyline"
##            logFile(log_file, msg); del msg
##            # Process: Feature To Line
##            arcpy.management.FeatureToLine(in_features = layercode_survey_area, out_feature_class = layercode_boundary_line, cluster_tolerance="", attributes="ATTRIBUTES")
##
##            # Delete after last use
##            del layercode_survey_area
##
##            msg = f">-> Appending the {region} Dataset to the DisMAP Regions Dataset"
##            logFile(log_file, msg); del msg
##            # Process: Append
##            arcpy.management.Append(inputs = layercode_boundary_line,
##                                    target = dismap_regions,
##                                    schema_type="NO_TEST",
##                                    field_mapping="",
##                                    subtype="")
##
##            # Delete after last use
##            del layercode_boundary_line
##
##            #Final benchmark for the region.
##            msg = f"ENDING REGION {region} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg
##
##            # Elapsed time
##            end_time = time()
##            elapse_time =  end_time - layercode_start_time
##            msg = f"Elapsed Time for {region}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)\n"
##            logFile(log_file, msg); del msg, end_time, elapse_time, layercode_start_time
##
##            # Clean up
##            del layercode, region
##
##        msg = f"> Delete Identical features in DisMAP Regions"
##        logFile(log_file, msg); del msg
##        # Process: arcpy.management.DeleteIdentical
##        arcpy.DeleteIdentical_management(in_dataset = dismap_regions,
##                                         fields = "Shape;Shape_Length;OARegion",
##                                         xy_tolerance="",
##                                         z_tolerance="0")
##
##        # Add Metadata
##        addMetadata(dismap_regions, log_file)
##
##        # Delete after last use
##        del dismap_regions
##
##         #Final benchmark for the region.
##        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Elapsed time
##        end_time = time()
##        elapse_time =  end_time - start_time
##        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
##        logFile(log_file, msg); del msg
##
##        del start_time, end_time, elapse_time
##
##    # This code is executed only if an exception was raised in the try block.
##    # Code executed in this block is just like normal code: if there is an
##    # exception, it will not be automatically caught (and probably stop the
##    # program).
##    except arcpy.ExecuteError:
##        # Geoprocessor threw an error
##        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
##        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
##        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
##        logFile(log_file.replace(".log", " ERROR.log"), msg); del msg
##    except Exception as e:
##        # Capture all other errors
##        #print(sys.exc_info()[2].tb_lineno)
##        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
##        logFile(log_file.replace(".log", " ERROR.log"), msg); del msg
##
##    # This code is executed only if no exceptions were raised in the try block.
##    # Code executed in this block is just like normal code: if there is an
##    # exception, it will not be automatically caught (and probably stop the
##    # program). Notice that if the else block is executed, then the except block
##    # is not, and vice versa. This block is optional.
##    else:
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##    # This code always executes after the other blocks, even if there was an
##    # uncaught exception (that didn’t cause a crash, obviously) or a return
##    # statement in one of the other blocks. Code executed in this block is just
##    # like normal code: if there is an exception, it will not be automatically
##    # caught (and probably stop the program). This block is also optional.
##    finally:
##        # Get list of local keys that may need to be deleted.
##        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]
##
##        # If there is a list of local keys, print the list, and then delete
##        # variables
##        if localKeys:
##            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
##            logFile(log_file, msg); del msg
##        del localKeys, function

##def createIndicatorsTable():
##    try:
##        temp_workspace = arcpy.env.workspace
##
##        # Set a start time so that we can see how log things take
##        start_time = time()
##
# #       - getting the test CenterOfGravityLat and CenterOfGravityDepth into the Indicators table
# #       - working on new procedures for calculating CenterOfGravityLat and CenterOfGravityDepth:
# #          - ensuring that the interpolated biomass, latitude, and depth rasters all share the same grid (via a snap raster??)
# #          - develop latitude raster
# #          - develop depth raster
# #          - pseudo code for CenterOfGravityLat
# #            for each region
# #                for each season
# #                    for each species
# #                        for each year
# #                            sumWtCpue = sum of all wtcpue values (get this from raster stats??)
# #                            weightedLat = wtcpue raster * latitude raster
# #                            sumWeightedLat = sum of all weightedLat values
# #                            CenterOfGravityLatitude = sumWeightedLat/sumWtCpue
### #
# #       - pseudo code for CenterOfGravityDepth
### #
# #            same as CenterOfGravityLat except you'll be weighting depth by wtcpue
##
##        # This is s dictionary that maps 'season' codes used as part of the CSV
##        # file names. An R script, created by OceanAdap (ref?), parses a data-
##        # table to create a set of CSV files that indivdually  contains data
##        # for a region/season
##        DisMapSeasonCodeDict = {"F" : "Fall",
##                                "S" : "Spring",
##                                "SPR" : "Spring",
##                                "SUM" : "Summer",
##                                "FALL" : "Fall",
##                                "ANN" : "Annual",
##                                "TRI" : "Triennial",
##                                "Spring" : "Spring",
##                                "Summer" : "Summer",
##                                "Fall" : "Fall",
##                                "Winter" : "Winter",
##                                "Annual" : "Annual",
##                                "Triennial" : "Triennial",
##                                None : None,
##                                '' : ''}
##
##        # Create an empty list to gather tuples
##        # row_values = []
##
##        indicators_template = os.path.join(ProjectGDB, u"Indicators_Template")
##        indicators = os.path.join(ProjectGDB, u"Indicators")
##
##        if not arcpy.Exists(indicators):
##            arcpy.management.Delete(indicators)
##            arcpy.management.CreateTable(ProjectGDB, u"Indicators", indicators_template, "" ,"")
##            msg = f">-----> {arcpy.GetMessages()}"
##            logFile(log_file, msg)
##            #print(msg)
##
##        # Start looping over the table_name array as we go region by region.
##        for table_name in table_names:
##            # Assigning variables from items in the chosen table list
##            # layercode_shape = table_name[0]
##            # layercode_boundary = table_name[1]
##            layercode = table_name[2]
##            region = table_name[3]
##            csv_file = table_name[4]
##            layercode_georef = table_name[5]
##            # layercode_contours = table_name[6]
##
##            del table_name
##
##            # Start with empty row_values list of list
##            #row_values = []
##
##            # Make Geodatabase friendly name
##            layercode_name = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "")
##
##            # List of varaibles for the table
##            # OARegionCode = layercode
##            OARegion = region[:region.find("(")].strip() if "(" in region else region
##            #Species = ''
##            #CommonName = ''
##            DisMapRegionCode = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "").lower()
##            #RegionText = region
##            OASeasonCode = layercode[layercode.find('_')+1:] if '_' in layercode else None
##            DisMapSeasonCode = DisMapSeasonCodeDict[OASeasonCode]
##
# #           Region
# #           DisMapRegionCode
# #           DisMapSeasonCode
# #           Species
# #           CommonName
# #           Year
# #           CenterOfGravityLatitude
# #           MinimumLatitude
# #           MaximumLatitude
# #           CenterOfGravityLatitudeStandardError
# #           CenterOfGravityLongitude
# #           MinimumLongitude
# #           MaximumLongitude
# #           CenterOfGravityLongitudeStandardError
# #           CenterOfGravityDepth
# #           MinimumDepth
# #           MaximumDepth
# #           CenterOfGravityDepthStandardError
# #           EffectiveAreaOccupied
# #           CoreHabitatArea
##
##            # Clean up
##            del OASeasonCode
##
##            # For benchmarking.
##            #log_file = os.path.join(LOG_DIRECTORY, region + ".log")
##            log_file = os.path.abspath(os.path.join(LOG_DIRECTORY, region + ".log"))
##
##            if os.path.isfile(log_file):
##                print(log_file)
##                #os.makedirs(log_file)
##            # Start with removing the log file if it exists
##            #if os.path.isfile(log_file):
##            #    os.remove(log_file)
##
##            # Write a message to the log file
##            msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg)
##
##            # Set the output coordinate system to what is available for us.
##            layercode_sr = srs[layercode_georef]
##            arcpy.env.outputCoordinateSystem = layercode_sr
##            arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
##            #del layercode_sr
##
##            # region abbreviated path
##            layercode_folder = os.path.join(ANALYSIS_DIRECTORY, layercode)
##
##            # Region Indicators
##            layercode_indicators = os.path.join(ProjectGDB, "{0}_Indicators".format(layercode))
##
##            # Region Bathymetry
##            layercode_bathymetry = os.path.join(ProjectGDB, "{0}_Bathymetry".format(layercode))
##
##            # Region Latitude
##            layercode_latitude = os.path.join(ProjectGDB, "{0}_Latitude".format(layercode))
##
##            # Region Longitude
##            layercode_longitude = os.path.join(ProjectGDB, "{0}_Longitude".format(layercode))
##
##            # Region Snap Raster
##            layercode_snap_raster = os.path.join(ProjectGDB, "{0}_Snap_Raster".format(layercode))
##
##            # Region Snap Raster
##            layercode_raster_mask = os.path.join(ProjectGDB, "{0}_Raster_Mask".format(layercode))
##
##            #arcpy.env.scratchWorkspace = ScratchGDB
##            arcpy.env.overwriteOutput = True
##            arcpy.env.snapRaster = layercode_snap_raster
##            arcpy.env.extent = arcpy.Describe(layercode_snap_raster).extent
##            arcpy.env.mask = layercode_raster_mask
##
##            # Tests if the abbreviated region folder exists and if it is in
##            # selected regions
##            if os.path.isdir(layercode_folder):
##                # msg = ">-> Region (abb): {0}\n\t Region:  {1}\n\t CSV File: {2}\n\t Geo Reference: {3}"\
##                #      .format(layercode, region, csv_file, layercode_sr)
##                msg = f">-> Region (abb): {layercode}\n\t Region:  {region}\n\t CSV File: {csv_file}"
##                logFile(log_file, msg)
##                # List of folders in the region dictory
##                species_folders = [d for d in os.listdir(layercode_folder) if \
##                               os.path.isdir(os.path.join(layercode_folder, d))]
##                if species_folders:
##                    msg = '>-> There are {0} species folders for the {1} region folder.'.format(len(species_folders), region)
##                    logFile(log_file, msg)
##                    if FilterSpecies:
##                        # Convert the selected species list to matcv the species
##                        # folder name by removing haphens and periods
##                        selected_species_keys = [ss.replace(".","").replace("-"," ").replace("(","").replace(")","").replace("/","and") for ss in selected_species.keys()]
##
##                        # Find the intersection between the list of specie folders and the filtered list
##                        selected_species_folders = list(set(species_folders) & set(selected_species_keys))
##                        del selected_species_keys
##                        # Sort the list
##                        selected_species_folders.sort()
##                        if selected_species_folders:
##                            # Replace the list
##                            species_folders = selected_species_folders[:]
##                            msg = '>-> There are {0} selected species in the {1} region folder to process.'.format(len(species_folders), region)
##                            logFile(log_file, msg)
##                        else:
##                            msg = '>-> There are no selected species in the {0} region folder to process.'.format(region)
##                            logFile(log_file, msg)
##                            msg = '>-> Need to change the selected species list for this region.'
##                            logFile(log_file, msg)
##                            return
##                        del selected_species_folders
##
##                    # Get a disctionary of species and common names from the
##                    # CVS Table in the Project GDB
##                    csv_file_table = os.path.join(ProjectGDB, csv_file)
##                    # Dictionary of species and common names that are in the tables
##                    species_common_name_dict = unique_fish_dict(csv_file_table)
##                    #print( species_common_name_dict )
##                    #print("Is the")
##
##                    # Clean up
##                    del csv_file_table
##                else:
##                    msg = '>-> There are no species folders in the region ({0}) folder.'.format(region)
##                    logFile(log_file, msg)
##                    msg = '>-> Need to run generateRasters to create images.'
##                    logFile(log_file, msg)
##                    return
##            else:
##                msg = '>-> The folder for this region ({0}) is missing from the Analysis Folder and needs to be created.'.format(region)
##                logFile(log_file, msg)
##                return
##
##            # Cleanup
##            del layercode_georef
##
##            # Creating the region indicator table to be used. We output this to the file system in the appropriate folder.
##            msg = '> Creating the {} Indicators Table'.format(region)
##            logFile(log_file, msg)
##
##            if not arcpy.Exists( layercode_indicators ):
##                #
##                if arcpy.Exists(layercode_indicators):
##                    msg = '>-> Removing the {0} Region Indicators Table'.format(region)
##                    logFile(log_file, msg)
##
##                    # Geoprocessing tools return a result object of the derived
##                    # output dataset.
##                    result = arcpy.management.Delete(layercode_indicators)
##                    msg = arcpy.GetMessages()
##                    msg = ">---> {0}\n".format(msg.replace('\n', '\n>---> '))
##                    logFile(log_file, msg)
##                    del msg
##                    del result
##
##                else:
##                    msg = ">-> Replace Indicator Datasets set to True, but {0} Indicator Dataset is missing".format(region)
##                    logFile(log_file, msg)
##
##                indicators_view = arcpy.management.MakeTableView(indicators, 'Indicators_View', "OARegion = '{0}'".format(region.replace("'", "''")))
##                arcpy.management.DeleteRows('Indicators_View')
##                msg = arcpy.GetMessages()
##                msg = ">---> {0}\n".format(msg.replace('\n', '\n>---> '))
##                logFile(log_file, msg)
##                result = arcpy.management.Delete('Indicators_View')
##                msg = arcpy.GetMessages()
##                msg = ">---> {0}\n".format(msg.replace('\n', '\n>---> '))
##                logFile(log_file, msg)
##                del indicators_view
##                del result
##
##                msg = '>-> Creating the {} Indicator Table'.format(region)
##                logFile(log_file, msg)
##
##                # Set local variables
##                out_path = ProjectGDB
##                out_name = "{0}_Indicators".format(layercode)
##                template = indicators_template
##                config_keyword = ""
##
##                # Execute CreateTable
##                arcpy.management.CreateTable(out_path, out_name, template, config_keyword)
##                msg = arcpy.GetMessages()
##                msg = ">---> {0}".format(msg.replace('\n', '\n>-----> '))
##                logFile(log_file, msg)
##
##                del out_path, out_name, template, config_keyword
##
##                # Loading images into the Mosaic.
##                # msg = '> Loading the {} Indicator Dataset'.format(region)
##                # logFile(log_file, msg)
##
##                # Start with empty row_values list of list
##                row_values = []
##
##                # Loop through dictionary
##                for Species in species_common_name_dict:
##                    # Speices folders do not include the '.' that can be a part
##                    # of the name, so remove
##                    species_folder = Species.replace(".","").replace("-"," ").replace("(","").replace(")","").replace("/","and")
##                    # The common name is the value in the dictionary
##                    CommonName = species_common_name_dict[Species][0]
##                    #print(CommonName)
##                    CoreSpecies = species_common_name_dict[Species][1]
##                    #print(CoreSpecies)
##                    # Create an item for multidimensional variable list
##                    #speciesCommonName = "'{0}' '{1}' #".format(species, common)
##                    # print("\t\t '{0}'".format(speciesCommonName))
##                    # 'Centropristis striata' 'Centropristis striata' #
##                    # Append that item to speciesCommonNameRegionList
##                    #speciesCommonNameRegionList.append(speciesCommonName)
##                    #del speciesCommonName
##
##                    # Test of the speices folder name from the dictionary is in
##                    # the list of folders in the region folder. The species
##                    # folder may not have been created, so need to test
##                    # if species_folder in species_folders first, then as a filter see
##                    # if species is in a shorter list. Will need to change this later
##
##                    # This test is species is in selected species
##                    if species_folder in species_folders: # and species_folder in selected_species.keys():
##
##                        # Test if there a corresponding folder in RASTER DIRECTORY, if
##                        # not create the folder
##                        #out_species_folder = os.path.join(MOSAIC_DIRECTORY, layercode, species_folder)
##                        # Make the speices folder in the raster directory if missing
##                        #if not os.path.isdir(out_species_folder):
##                        #    os.makedirs(out_species_folder)
##                        msg = ">---> Species: {0}, Common Name: {1}".format(Species, CommonName)
##                        logFile(log_file, msg)
##
##                        input_folder = os.path.join(layercode_folder, species_folder)
##
##                        msg = ">---> Processing Biomass Rasters"
##                        logFile(log_file, msg)
##
##                        arcpy.env.workspace = input_folder
##                        biomassRasters = arcpy.ListRasters("*.tif")
##                        #print(biomassRasters)
##                        #print(selected_years)
##                        # Test if we are filtering on years. If so, a new year list is
##                        # created with the selected years remaining in the list
##                        if FilterYears:
##                            # Get a shorter list
##                            #biomassRasters = [r for r in biomassRasters if int(r.replace(".tif", "")) in selected_years]
##                            biomassRasters = [r for r in biomassRasters if int(r[-8:-4]) in selected_years]
##                        else:
##                            pass
##                        #print(biomassRasters)
##
##                        # ###--->>> This is to get a median biomass value for all years
##                        biomassBigArray = np.array([])
##                        for biomassRaster in sorted(biomassRasters):
##                            # Get maximumBiomass value to filter out "zero" rasters
##                            maximumBiomass = float(arcpy.management.GetRasterProperties(biomassRaster,"MAXIMUM").getOutput(0))
##                            # If maximumBiomass greater than zero, then process raster
##                            if maximumBiomass > 0.0:
##                                # Use Raster To NumPy Array
##                                biomassArray = arcpy.RasterToNumPyArray(biomassRaster, nodata_to_value=np.nan)
##                                # Set zero and smaller values to NaN
##                                biomassArray[biomassArray <= 0.0] = np.nan
##                                # make the biomass arrays one dimensional
##                                flatBiomassArray = biomassArray.flatten()
##                                # Remove NaN values from flatten (1-D) array
##                                flatBiomassArray = flatBiomassArray[~np.isnan(flatBiomassArray)]
##                                # Append Yearly Flatten Biomass Array to the big array (for all years)
##                                biomassBigArray = np.append(biomassBigArray, flatBiomassArray)
##                        # After processing all years, get the median value
##                        medianBiomass  = np.median(flatBiomassArray)
##                        # Cleanup
##                        del biomassBigArray, maximumBiomass, biomassArray, flatBiomassArray
##                        # ###--->>> This is to get a median biomass value for all years
##
##                        first_year = 9999
##                        # Process rasters
##                        for biomassRaster in sorted(biomassRasters):
##                            # Get year from raster name
##                            Year = int(biomassRaster[-8:-4])
##
##                            msg = ">-----> Processing {0} Biomass Raster".format(biomassRaster)
##                            logFile(log_file, msg)
##
##                            # Get maximumBiomass value to filter out "zero" rasters
##                            maximumBiomass = float(arcpy.management.GetRasterProperties(biomassRaster,"MAXIMUM").getOutput(0))
##
##                            msg = ">-------> Biomass Raster Maximum: {0}".format(maximumBiomass)
##                            logFile(log_file, msg)
##                            del msg
##
##                            # If maximumBiomass greater than zero, then process raster
##                            if maximumBiomass > 0.0:
##                                msg = ">-------> Calculating indicators"
##                                logFile(log_file, msg)
##
##                                # Test is for first year
##                                if Year < first_year:
##                                    first_year = Year
##
##                            # ###--->>> Biomass Start
##
##                                #biomassArray = arcpy.RasterToNumPyArray(masked_biomass_raster, nodata_to_value=np.nan)
##                                biomassArray = arcpy.RasterToNumPyArray(biomassRaster, nodata_to_value=np.nan)
##                                biomassArray[biomassArray <= 0.0] = np.nan
##                                #biomassArray[biomassArray <= 0.001] = np.nan
##
##                                #arcpy.management.Delete(masked_biomass_raster)
##                                #del masked_biomass_raster
##
##                                #sumWtCpue = sum of all wtcpue values (get this from biomassRaster stats??)
##                                sumBiomassArray = np.nansum(biomassArray)
##
##                                #msg = ">-------> sumBiomassArray: {0}".format(sumBiomassArray)
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                #msg = ">-------> biomassArray non-nan count: {0}".format(np.count_nonzero(~np.isnan(biomassArray)))
##                                #logFile(log_file, msg)
##                                #del msg
##                            # ###--->>> Biomass End
##
##                            # ###--->>> Latitude Start
##                                #latitudeArray = arcpy.RasterToNumPyArray(masked_latitude_raster, nodata_to_value = np.nan)
##                                #arcpy.management.Delete(masked_latitude_raster)
##                                #del masked_latitude_raster
##
##                                # Latitude
##                                latitudeArray = arcpy.RasterToNumPyArray(layercode_latitude, nodata_to_value=np.nan)
##                                #print(latitudeArray.shape)
##                                latitudeArray[np.isnan(biomassArray)] = np.nan
##                                #print(latitudeArray.shape)
##
##                            ##    msg = ">-------> latitudeArray non-nan count: {0}".format(np.count_nonzero(~np.isnan(latitudeArray)))
##                            ##    logFile(log_file, msg)
##                            ##    del msg
##
##                            ##    msg = ">-------> Latitude Min: {0}".format(np.nanmin(latitudeArray))
##                            ##    logFile(log_file, msg)
##                            ##    del msg
##                            ##    msg = ">-------> Latitude Max: {0}".format(np.nanmax(latitudeArray))
##                            ##    logFile(log_file, msg)
##                            ##    del msg
##
##                                # make the biomass and latitude arrays one dimensional
##
##                                flatBiomassArray = biomassArray.flatten()
##
##                                flatLatitudeArray = latitudeArray.flatten()
##
##                                # latsInds is an array of indexes representing the sort
##
##                                latsInds = flatLatitudeArray.argsort()
##
##                                # sort biomass and latitude arrays by lat sorted index
##
##                                sortedBiomassArray = flatBiomassArray[latsInds]
##                                sortedLatitudeArray = flatLatitudeArray[latsInds]
##
##                                # calculate the cumulative sum of the sorted biomass values
##
##                                sortedBiomassArrayCumSum = np.nancumsum(sortedBiomassArray)
##
##                                # quantile is cumulative sum value divided by total biomass
##
##                                sortedBiomassArrayQuantile = sortedBiomassArrayCumSum / np.nansum(flatBiomassArray)
##
##                                # find the difference between 0.95 and each cumulative sum value ... asbolute value gives the closest distance
##
##                                diffArray = np.abs(sortedBiomassArrayQuantile - 0.95)
##
##                                # find the index of the smallest difference
##
##                                minIndex = diffArray.argmin()
##
##                                # get the lat at that index
##
##                                #maxLat = sortedLatitudeArray[minIndex]
##                                MaximumLatitude = sortedLatitudeArray[minIndex]
##
##                                # do the same for 0.05
##
##                                diffArray = np.abs(sortedBiomassArrayQuantile - 0.05)
##
##                                minIndex = diffArray.argmin()
##
##                                #minLat = sortedLatitudeArray[minIndex]
##                                MinimumLatitude = sortedLatitudeArray[minIndex]
##
##                                del sortedBiomassArrayCumSum, sortedBiomassArrayQuantile, diffArray, minIndex
##                                del sortedLatitudeArray, sortedBiomassArray, flatBiomassArray
##                                del latsInds, flatLatitudeArray
##
##                                weightedLatitudeArray = np.multiply(biomassArray, latitudeArray)
##
##                                sumWeightedLatitudeArray = np.nansum(weightedLatitudeArray)
##
##                                #msg = ">-------> Sum Weighted Latitude: {0}".format(sumWeightedLatitudeArray)
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                #CenterOfGravityLatitude = round(sumWeightedLatitudeArray / sumBiomassArray, 6)
##                                CenterOfGravityLatitude = sumWeightedLatitudeArray / sumBiomassArray
##
##                                if Year == first_year:
##                                    first_year_offset_latitude = CenterOfGravityLatitude
##
##                                OffsetLatitude = CenterOfGravityLatitude - first_year_offset_latitude
##
##                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$X1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
##                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$NEUS_F_Centropristis_striata_1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
##                                # cog st err is 0.00395
##
##                                weightedLatitudeArrayVariance = np.nanvar(weightedLatitudeArray)
##                                weightedLatitudeArrayCount = np.count_nonzero(~np.isnan(weightedLatitudeArray))
##
##                                CenterOfGravityLatitudeStandardError = math.sqrt(weightedLatitudeArrayVariance) / math.sqrt(weightedLatitudeArrayCount)
##
##                                del weightedLatitudeArrayVariance, weightedLatitudeArrayCount
##
##                                #msg = ">-------> Center of Gravity Latitude: {0}".format(round(CenterOfGravityLatitude,6))
##                                msg = ">-------> Center of Gravity Latitude: {0}".format(CenterOfGravityLatitude)
##                                logFile(log_file, msg)
##                                del msg
##
##                                msg = ">-------> Minimum Latitude (5th Percentile): {0}".format(MinimumLatitude)
##                                logFile(log_file, msg)
##                                del msg
##
##                                msg = ">-------> Maximum Latitude (95th Percentile): {0}".format(MaximumLatitude)
##                                logFile(log_file, msg)
##                                del msg
##
##                                msg = ">-------> Offset Latitude: {0}".format(OffsetLatitude)
##                                logFile(log_file, msg)
##                                del msg
##
##                                msg = ">-------> Center of Gravity Latitude Standard Error: {0}".format(CenterOfGravityLatitudeStandardError)
##                                logFile(log_file, msg)
##                                del msg
##
##                                del latitudeArray, weightedLatitudeArray, sumWeightedLatitudeArray
##
##                            # ###--->>> Latitude End
##
##                            # ###--->>> Longitude Start
##                                #longitudeArray = arcpy.RasterToNumPyArray(masked_longitude_raster, nodata_to_value = np.nan)
##                                #arcpy.management.Delete(masked_longitude_raster)
##                                #del masked_longitude_raster
##
##                                # Longitude
##                                # Doesn't work for International Date Line
##                                #longitudeArray = arcpy.RasterToNumPyArray(layercode_longitude, nodata_to_value=np.nan)
##                                #longitudeArray[np.isnan(biomassArray)] = np.nan
##
##                                # For issue of international date line
##                                # Added/Modified by JFK June 15, 2022
##                                longitudeArray = arcpy.RasterToNumPyArray(layercode_longitude, nodata_to_value=np.nan)
##                                longitudeArray = np.mod(longitudeArray, 360.0)
##                                longitudeArray[np.isnan(biomassArray)] = np.nan
##
##                                #msg = ">-------> longitudeArray non-nan count: {0}".format(np.count_nonzero(~np.isnan(longitudeArray)))
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                #msg = ">-------> Longitude Min: {0}".format(np.nanmin(longitudeArray))
##                                #logFile(log_file, msg)
##                                #del msg
##                                #msg = ">-------> Longitude Max: {0}".format(np.nanmax(longitudeArray))
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                # make the biomass and latitude arrays one dimensional
##
##                                flatBiomassArray = biomassArray.flatten()
##
##                                flatLongitudeArray = longitudeArray.flatten()
##
##                                # longsInds is an array of indexes representing the sort
##
##                                longsInds = flatLongitudeArray.argsort()
##
##                                # sort biomass and latitude arrays by long sorted index
##
##                                sortedBiomassArray = flatBiomassArray[longsInds]
##                                sortedLongitudeArray = flatLongitudeArray[longsInds]
##
##                                # calculate the cumulative sum of the sorted biomass values
##
##                                sortedBiomassArrayCumSum = np.nancumsum(sortedBiomassArray)
##
##                                # quantile is cumulative sum value divided by total biomass
##
##                                sortedBiomassArrayQuantile = sortedBiomassArrayCumSum / np.nansum(flatBiomassArray)
##
##                                # find the difference between 0.95 and each cumulative sum value ... asbolute value gives the closest distance
##
##                                diffArray = np.abs(sortedBiomassArrayQuantile - 0.95)
##
##                                # find the index of the smallest difference
##
##                                minIndex = diffArray.argmin()
##
##                                # get the lat at that index
##
##                                #maxLat = sortedLongitudeArray[minIndex]
##                                MaximumLongitude = sortedLongitudeArray[minIndex]
##
##                                # do the same for 0.05
##
##                                diffArray = np.abs(sortedBiomassArrayQuantile - 0.05)
##
##                                minIndex = diffArray.argmin()
##
##                                #minLat = sortedLongitudeArray[minIndex]
##                                MinimumLongitude = sortedLongitudeArray[minIndex]
##
##                                del sortedBiomassArrayCumSum, sortedBiomassArrayQuantile, diffArray, minIndex
##                                del sortedLongitudeArray, sortedBiomassArray, flatBiomassArray
##                                del longsInds, flatLongitudeArray
##
##                                weightedLongitudeArray = np.multiply(biomassArray, longitudeArray)
##
##                                sumWeightedLongitudeArray = np.nansum(weightedLongitudeArray)
##
##                                #CenterOfGravityLongitude = round(sumWeightedLongitudeArray / sumBiomassArray, 6)
##                                CenterOfGravityLongitude = sumWeightedLongitudeArray / sumBiomassArray
##
##                                if Year == first_year:
##                                    first_year_offset_longitude = CenterOfGravityLongitude
##
##                                OffsetLongitude = CenterOfGravityLongitude - first_year_offset_longitude
##
##                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$X1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
##                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$NEUS_F_Centropristis_striata_1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
##                                # cog st err is 0.00395
##
##                                weightedLongitudeArrayVariance = np.nanvar(weightedLongitudeArray)
##                                weightedLongitudeArrayCount = np.count_nonzero(~np.isnan(weightedLongitudeArray))
##
##                                CenterOfGravityLongitudeStandardError = math.sqrt(weightedLongitudeArrayVariance) / math.sqrt(weightedLongitudeArrayCount)
##
##                                del weightedLongitudeArrayVariance, weightedLongitudeArrayCount
##
##                                # Convert 360 back to 180
##                                # Added/Modified by JFK June 15, 2022
##                                CenterOfGravityLongitude = np.mod(CenterOfGravityLongitude - 180.0, 360.0) - 180.0
##                                MinimumLongitude = np.mod(MinimumLongitude - 180.0, 360.0) - 180.0
##                                MaximumLongitude = np.mod(MaximumLongitude - 180.0, 360.0) - 180.0
##
##                                #msg = ">-------> Sum Weighted Longitude: {0}".format(sumWeightedLongitudeArray)
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                #msg = ">-------> Center of Gravity Longitude: {0}".format(round(CenterOfGravityLongitude,6))
##                                msg = ">-------> Center of Gravity Longitude: {0}".format(CenterOfGravityLongitude)
##                                logFile(log_file, msg)
##                                del msg
##
##                                #msg = ">-------> Center of Gravity Longitude: {0}".format(np.mod(CenterOfGravityLongitude - 180.0, 360.0) -180.0)
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                msg = ">-------> Minimum Longitude (5th Percentile): {0}".format(MinimumLongitude)
##                                logFile(log_file, msg)
##                                del msg
##
##                                msg = ">-------> Maximum Longitude (95th Percentile): {0}".format(MaximumLongitude)
##                                logFile(log_file, msg)
##                                del msg
##
##                                msg = ">-------> Offset Longitude: {0}".format(OffsetLongitude)
##                                logFile(log_file, msg)
##                                del msg
##
##                                msg = ">-------> Center of Gravity Longitude Standard Error: {0}".format(CenterOfGravityLongitudeStandardError)
##                                logFile(log_file, msg)
##                                del msg
##
##                                del longitudeArray, weightedLongitudeArray, sumWeightedLongitudeArray
##
##                            # ###--->>> Center of Gravity Depth Start
##                                # ###--->>> Bathymetry (Depth)
##                                #bathymetryArray = arcpy.RasterToNumPyArray(masked_bathymetry_raster, nodata_to_value = np.nan)
##                                #arcpy.management.Delete(masked_bathymetry_raster)
##                                #del masked_bathymetry_raster
##
##                                # Bathymetry
##                                bathymetryArray = arcpy.RasterToNumPyArray(layercode_bathymetry, nodata_to_value=np.nan)
##                                # If biomass cells are Null, make bathymetry cells Null as well
##                                bathymetryArray[np.isnan(biomassArray)] = np.nan
##                                # For bathymetry values zero are larger, make zero
##                                bathymetryArray[bathymetryArray >= 0.0] = 0.0
##
##                                #msg = ">-------> bathymetryArray non-nan count: {0}".format(np.count_nonzero(~np.isnan(bathymetryArray)))
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                #msg = ">-------> Bathymetry Min: {0}".format(np.nanmin(bathymetryArray))
##                                #logFile(log_file, msg)
##                                #del msg
##                                #msg = ">-------> Bathymetry Max: {0}".format(np.nanmax(bathymetryArray))
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                # make the biomass and latitude arrays one dimensional
##
##                                flatBiomassArray = biomassArray.flatten()
##
##                                flatBathymetryArray = bathymetryArray.flatten()
##
##                                # bathyInds is an array of indexes representing the sort
##
##                                bathyInds = flatBathymetryArray.argsort()
##
##                                # sort biomass and latitude arrays by lat sorted index
##
##                                sortedBiomassArray = flatBiomassArray[bathyInds]
##                                sortedBathymetryArray = flatBathymetryArray[bathyInds]
##
##                                # calculate the cumulative sum of the sorted biomass values
##
##                                sortedBiomassArrayCumSum = np.nancumsum(sortedBiomassArray)
##
##                                # quantile is cumulative sum value divided by total biomass
##
##                                sortedBiomassArrayQuantile = sortedBiomassArrayCumSum/np.nansum(flatBiomassArray)
##
##                                # find the difference between 0.95 and each cumulative sum value ... asbolute value gives the closest distance
##
##                                diffArray = np.abs(sortedBiomassArrayQuantile - 0.95)
##
##                                # find the index of the smallest difference
##
##                                minIndex = diffArray.argmin()
##
##                                # get the lat at that index
##
##                                #maxLat = sortedBathymetryArray[minIndex]
##                                MaximumDepth = sortedBathymetryArray[minIndex]
##
##                                # do the same for 0.05
##
##                                diffArray = np.abs(sortedBiomassArrayQuantile - 0.05)
##
##                                minIndex = diffArray.argmin()
##
##                                #minLat = sortedBathymetryArray[minIndex]
##                                MinimumDepth = sortedBathymetryArray[minIndex]
##
##                                del sortedBiomassArrayCumSum, sortedBiomassArrayQuantile, diffArray, minIndex
##                                del sortedBathymetryArray, sortedBiomassArray, flatBiomassArray
##                                del bathyInds, flatBathymetryArray
##
##                                weightedBathymetryArray = np.multiply(biomassArray, bathymetryArray)
##
##                                sumWeightedBathymetryArray = np.nansum(weightedBathymetryArray)
##
##                                #msg = ">-------> Sum Weighted Bathymetry: {0}".format(sumWeightedBathymetryArray)
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                #CenterOfGravityDepth = round(sumWeightedBathymetryArray / sumBiomassArray, 6)
##                                CenterOfGravityDepth = sumWeightedBathymetryArray / sumBiomassArray
##
##                                if Year == first_year:
##                                    first_year_offset_depth = CenterOfGravityDepth
##
##                                OffsetDepth = CenterOfGravityDepth - first_year_offset_depth
##
##                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$X1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
##                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$NEUS_F_Centropristis_striata_1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
##                                # cog st err is 0.00395
##
##                                weightedBathymetryArrayVariance = np.nanvar(weightedBathymetryArray)
##                                weightedBathymetryArrayCount = np.count_nonzero(~np.isnan(weightedBathymetryArray))
##
##                                CenterOfGravityDepthStandardError = math.sqrt(weightedBathymetryArrayVariance) / math.sqrt(weightedBathymetryArrayCount)
##
##                                del weightedBathymetryArrayVariance, weightedBathymetryArrayCount
##
##                                #msg = ">-------> Center of Gravity Depth: {0}".format(round(CenterOfGravityDepth,6))
##                                msg = ">-------> Center of Gravity Depth: {0}".format(CenterOfGravityDepth)
##                                logFile(log_file, msg)
##                                del msg
##
##                                msg = ">-------> Minimum Depth (5th Percentile): {0}".format(MinimumDepth)
##                                logFile(log_file, msg)
##                                del msg
##
##                                msg = ">-------> Maximum Depth (95th Percentile): {0}".format(MaximumDepth)
##                                logFile(log_file, msg)
##                                del msg
##
##                                msg = ">-------> Offset Depth: {0}".format(OffsetDepth)
##                                logFile(log_file, msg)
##                                del msg
##
##                                msg = ">-------> Center of Gravity Depth Standard Error: {0}".format(CenterOfGravityDepthStandardError)
##                                logFile(log_file, msg)
##                                del msg
##
##                                del bathymetryArray, weightedBathymetryArray, sumWeightedBathymetryArray
##
##                            # ###--->>> Center of Gravity Depth End
##
##                            # ###--->>> Effective Area Occupied Start
##
##                                # biomassSquaredArray = biomassArray * biomassArray (use numpy.multiply?)
##                                biomassSquaredArray = np.multiply(biomassArray, biomassArray)
##
##                                # sumBiomassSquared = sum of biomassSquaredArray (use numpy.sum?)
##                                sumBiomassSquared = np.nansum(biomassSquaredArray)
##
##                                # Clean-up
##                                del biomassSquaredArray
##
##                                #msg = ">-------> Sum (total) Biomass: {0} WTCPUE".format(sumBiomassArray)
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                #msg = ">-------> Sum of Biomass Squared Array: {0}".format(sumBiomassSquared)
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                # ###--->>> Effective Area Occupied
##                                #EffectiveAreaOccupied = (sumBiomassArray * sumBiomassArray) / sumBiomassSquared
##
##                                #msg = ">-------> Effective Area Occupied: {0}".format(EffectiveAreaOccupied)
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                # Clean-up
##                                del sumBiomassSquared
##
##                            # ###--->>> Effective Area Occupied End
##
##                            # ###--->>> Core Habitat Area Start
##                                #msg = ">-------> biomassArray min: {0}".format(np.nanmin(biomassArray))
##                                #logFile(log_file, msg)
##                                #del msg
##                                #msg = ">-------> biomassArray max: {0}".format(np.nanmax(biomassArray))
##                                #logFile(log_file, msg)
##                                #del msg
##                                #msg = ">-------> biomassArray mean: {0}".format(np.nanmean(biomassArray))
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                # cellArea = 2000 x 2000 (... or 2 x 2 to for square km)
##                                #cellArea = cell_size * cell_size
##                                #cell_size = 2000
##                                #cellArea = cell_size/1000 * cell_size/1000
##
##                                # medianBiomass = median of biomassArray (use numpy.median?)
##                                # medianBiomass = np.nanmedian(biomassArray)
##
##                                # biomassGTMedianArray = only those biomassArray values GT medianBiomass (not sure how)
##                                biomassGTMedianArray = np.copy(biomassArray)
##                                biomassGTMedianArray[biomassArray < medianBiomass] = np.nan
##
##                                # countValues = count of non-null values in biomassGTMedianArray
##                                countValues = np.count_nonzero(~np.isnan(biomassGTMedianArray))
##
##                                # CoreHabitatArea = countValues * cellArea
##                                #CoreHabitatArea = countValues * cellArea
##
##                                #msg = ">-------> Cell Area: {0} sqr km".format(cellArea)
##                                #logFile(log_file, msg)
##                                #del msg
##                                #msg = ">-------> Median Biomass: {0}".format(medianBiomass)
##                                #logFile(log_file, msg)
##                                #del msg
##                                #msg = ">-------> Count Values: {0}".format(countValues)
##                                #logFile(log_file, msg)
##                                #del msg
##                                #msg = ">-------> Core Habitat Area: {0} sqr km".format(CoreHabitatArea)
##                                #logFile(log_file, msg)
##                                #del msg
##
##                                #del cellArea
##                                del biomassGTMedianArray
##                                del countValues, biomassRaster, biomassArray, sumBiomassArray
##                            # ###--->>> Core Habitat Area End
##
##
##                            elif maximumBiomass == 0.0:
##                               CenterOfGravityLatitude = None
##                               MinimumLatitude = None
##                               MaximumLatitude = None
##                               OffsetLatitude = None
##                               CenterOfGravityLatitudeStandardError = None
##                               CenterOfGravityLongitude = None
##                               MinimumLongitude = None
##                               MaximumLongitude = None
##                               OffsetLongitude = None
##                               CenterOfGravityLongitudeStandardError = None
##                               CenterOfGravityDepth = None
##                               MinimumDepth = None
##                               MaximumDepth = None
##                               OffsetDepth = None
##                               CenterOfGravityDepthStandardError = None
##                               #EffectiveAreaOccupied = None
##                               #CoreHabitatArea = None
##                               del biomassRaster
##                            else:
##                                print('Something wrong with biomass raster')
##
##                            row = [OARegion,
##                                   DisMapRegionCode,
##                                   DisMapSeasonCode,
##                                   Species,
##                                   CommonName,
##                                   CoreSpecies,
##                                   Year,
##                                   CenterOfGravityLatitude,
##                                   MinimumLatitude,
##                                   MaximumLatitude,
##                                   OffsetLatitude,
##                                   CenterOfGravityLatitudeStandardError,
##                                   CenterOfGravityLongitude,
##                                   MinimumLongitude,
##                                   MaximumLongitude,
##                                   OffsetLongitude,
##                                   CenterOfGravityLongitudeStandardError,
##                                   CenterOfGravityDepth,
##                                   MinimumDepth,
##                                   MaximumDepth,
##                                   OffsetDepth,
##                                   CenterOfGravityDepthStandardError,
##                                   #EffectiveAreaOccupied,
##                                   #CoreHabitatArea
##                                   ]
##
##                            # Append to list
##                            row_values.append(row)
##                            del row
##
##                            # Clean-up
##                            del maximumBiomass
##                            del Year, CenterOfGravityLatitude, MinimumLatitude, MaximumLatitude
##                            del CenterOfGravityLatitudeStandardError, CenterOfGravityLongitude
##                            del MinimumLongitude, MaximumLongitude
##                            del CenterOfGravityLongitudeStandardError, CenterOfGravityDepth
##                            del MinimumDepth, MaximumDepth, CenterOfGravityDepthStandardError
##                            #del EffectiveAreaOccupied, CoreHabitatArea
##                            del OffsetLatitude, OffsetLongitude, OffsetDepth
##                            #del Species, CommonName, CoreSpecies
##
##                        del medianBiomass
##                        del first_year
##                        del first_year_offset_latitude, first_year_offset_longitude, first_year_offset_depth
##                    else:
##                        pass # Passng for the moment to limit print output
##                        #msg = "###--->>> Species: {0} does not have a folder, Common Name: {1}".format(Species, CommonName)
##                        #logFile(log_file, msg)
##                        #del msg
##
##                    del Species, CommonName, CoreSpecies
##
##                msg = ">-----> Inserting records into the table"
##                print(msg)
##                del msg
##
##                for row_value in row_values:
##                    #print(row_value)
##                    print("Region: {0}".format(row_value[0]))
##                    print("DisMapRegionCode: {0}".format(row_value[1]))
##                    print("DisMapSeasonCode: {0}".format(row_value[2]))
##                    print("Species: {0}".format(row_value[3]))
##                    print("CommonName: {0}".format(row_value[4]))
##                    print("CoreSpecies: {0}".format(row_value[5]))
##                    print("Year: {0}".format(row_value[6]))
##                    print("\tCenterOfGravityLatitude: {0}".format(row_value[7]))
##                    print("\tMinimumLatitude: {0}".format(row_value[8]))
##                    print("\tMaximumLatitude: {0}".format(row_value[9]))
##                    print("\tOffsetLatitude: {0}".format(row_value[10]))
##                    print("\tCenterOfGravityLatitudeStandardError: {0}".format(row_value[11]))
##                    print("\tCenterOfGravityLongitude: {0}".format(row_value[12]))
##                    print("\tMinimumLongitude: {0}".format(row_value[13]))
##                    print("\tMaximumLongitude: {0}".format(row_value[14]))
##                    print("\tOffsetLongitude: {0}".format(row_value[15]))
##                    print("\tCenterOfGravityLongitudeStandardError: {0}".format(row_value[16]))
##                    print("\tCenterOfGravityDepth: {0}".format(row_value[17]))
##                    print("\tMinimumDepth: {0}".format(row_value[18]))
##                    print("\tMaximumDepth: {0}".format(row_value[19]))
##                    print("\tOffsetDepth: {0}".format(row_value[20]))
##                    print("\tCenterOfGravityDepthStandardError: {0}".format(row_value[21]))
##                    #print("\tEffectiveAreaOccupied: {0}".format(row_value[22]))
##                    #print("\tCoreHabitatArea: {0}".format(row_value[23]))
##                if row_value: del row_value
##
##                # This gets a list of fields in the table
##                fields = [f.name for f in arcpy.ListFields(layercode_indicators) if f.name != 'OBJECTID']
##                #print(fields)
##
##                # Open an InsertCursor
##                cursor = arcpy.da.InsertCursor(layercode_indicators, fields)
##
##                # Insert new rows into the table
##                for row in row_values:
##                    try:
##                        row = [None if x != x else x for x in row]
##                        cursor.insertRow(row)
##                        del row
##                    except:
##                        #print(fields)
##                        print("Row: {0}".format(row))
##
##                #print(row_values)
##                # Delete cursor object
##                del cursor
##                del row_values
##
##                # Remove Identical Records
##                arcpy.management.DeleteIdentical(in_dataset=layercode_indicators, fields=fields, xy_tolerance="", z_tolerance="0")
##                msg = arcpy.GetMessages()
##                msg = ">-> {0}\n".format(msg.replace('\n', '\n>-> '))
##                logFile(log_file, msg); del msg
##
##                del fields
##
##                # Make XY Event  Layer
##                my_events = arcpy.management.MakeXYEventLayer(layercode_indicators, "CenterOfGravityLongitude", "CenterOfGravityLatitude", "my_events","#","#")
##
##                # Make it a Dataset and output it to the local hard disk drive (for usage and debugging purposes)
##                arcpy.FeatureClassToFeatureClass_conversion(in_features=my_events, out_path=ProjectGDB, out_name= "{0}_Indicators_COG".format(layercode),
##                                                            where_clause='',
##                                                            field_mapping='',
##                                                            #field_mapping="""Field1 "Field1" true true false 50 Text 0 0 ,First,#,my_events,Field1,-1,-1;region "region" true true false 50 Text 0 0 ,First,#,my_events,region,-1,-1;haulid "haulid" true true false 255 Text 0 0 ,First,#,my_events,haulid,-1,-1;year "year" true true false 4 Long 0 0 ,First,#,my_events,year,-1,-1;spp "spp" true true false 50 Text 0 0 ,First,#,my_events,spp,-1,-1;wtcpue "wtcpue" true true false 8 Double 10 20 ,First,#,my_events,wtcpue,-1,-1;common "common" true true false 50 Text 0 0 ,First,#,my_events,common,-1,-1;lat "lat" true true false 8 Double 10 20 ,First,#,my_events,lat,-1,-1;stratum "stratum" true true false 50 Text 0 0 ,First,#,my_events,stratum,-1,-1;stratumare "stratumare" true true false 50 Text 0 0 ,First,#,my_events,stratumarea,-1,-1;lon "lon" true true false 8 Double 10 20 ,First,#,my_events,lon,-1,-1;depth "depth" true true false 50 Text 0 0 ,First,#,my_events,depth,-1,-1""",
##                                                            config_keyword="")
##                #arcpy.conversion.FeatureClassToFeatureClass("neusf_csv_XYTableToPoint", r"C:\Users\jfken\Documents\GitHub\DisMap\Default.gdb", "neusf_csv_XY", '', 'csv_id "csv_id" true true false 4 Long 0 0,First,#,neusf_csv_XYTableToPoint,csv_id,-1,-1;region "region" true true false 34 Text 0 0,First,#,neusf_csv_XYTableToPoint,region,0,34;haulid "haulid" true true false 30 Text 0 0,First,#,neusf_csv_XYTableToPoint,haulid,0,30;year "year" true true false 4 Long 0 0,First,#,neusf_csv_XYTableToPoint,year,-1,-1;spp "spp" true true false 64 Text 0 0,First,#,neusf_csv_XYTableToPoint,spp,0,64;wtcpue "wtcpue" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,wtcpue,-1,-1;wtc_cube "wtc_cube" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,wtc_cube,-1,-1;common "common" true true false 64 Text 0 0,First,#,neusf_csv_XYTableToPoint,common,0,64;stratum "stratum" true true false 4 Long 0 0,First,#,neusf_csv_XYTableToPoint,stratum,-1,-1;stratumarea "stratumarea" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,stratumarea,-1,-1;lat "lat" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,lat,-1,-1;lon "lon" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,lon,-1,-1;depth "depth" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,depth,-1,-1', '')
##
##                # Clear the XY Event Layer from memory.
##                arcpy.management.Delete("my_events")
##                del my_events
##
##                # Append Region Indicators to Indicators Table
##                arcpy.management.Append(inputs=layercode_indicators, target=indicators, schema_type="TEST", field_mapping="", subtype="")
##
##                # Add some metadata
##                years_md = unique_years(layercode_indicators)
##
##                layercode_indicators_md = md.Metadata(layercode_indicators)
##                layercode_indicators_md.synchronize('ACCESSED', 1)
##                layercode_indicators_md.title = "{0} Indicators {1}".format(region.replace('-',' to '), DateCode)
##                layercode_indicators_md.tags = "{0}, {1} to {2}".format(geographic_regions[layercode], min(years_md), max(years_md))
##                layercode_indicators_md.save()
##                del layercode_indicators_md, years_md
##
##                del input_folder, biomassRasters, species_folder
##
##            else:
##                print("Region {0} Indicator Table exists is set to False".format(layercode))
##
##            # Clean up
##            del csv_file, layercode_name
##            del layercode_folder, layercode_sr, layercode
##            del OARegion #, Species, CommonName, CoreSpecies
##            del DisMapRegionCode, DisMapSeasonCode
##            del layercode_indicators, layercode_bathymetry, layercode_latitude
##            del layercode_longitude, layercode_raster_mask, species_folders
##            del species_common_name_dict
##            #del medianBiomass
##
##            #Final benchmark for the region.
##            msg = "ENDING REGION {} COMPLETED ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
##            logFile(log_file, msg)
##            del msg
##            del region
##
##        # This gets a list of fields in the table
##        fields = [f.name for f in arcpy.ListFields(indicators) if f.name != 'OBJECTID']
##
##        # Remove Identical Records
##        arcpy.management.DeleteIdentical(in_dataset=indicators, fields=fields, xy_tolerance="", z_tolerance="0")
##        msg = arcpy.GetMessages()
##        msg = ">-> {0}\n".format(msg.replace('\n', '\n>-> '))
##        logFile(log_file, msg); del msg
##
##
##        msg = '>-> Adding field index in the Indicators Table'
##        logFile(log_file, msg)
##
##        try:
##            arcpy.RemoveIndex_management(indicators, ["IndicatorsTableSpeciesIndex"])
##        except:
##            pass
##
##        # Add Attribute Index
##        arcpy.management.AddIndex(indicators, ['Species', 'CommonName', 'SpeciesCommonName', 'Year'], "IndicatorsTableSpeciesIndex", "NON_UNIQUE", "NON_ASCENDING")
##        msg = f">-----> {arcpy.GetMessages()}"
##        logFile(log_file, msg); del msg
##
##
##
##        #geographic_regions[layercode]
##        indicators_md = md.Metadata(indicators)
##        indicators_md.synchronize('ACCESSED', 1)
##        indicators_md.title = "Indicators {0}".format(DateCode)
##        #indicators_md.tags = "{0}, {1} to {2}".format(geographic_regions[layercode], min(years), max(years))
##        indicators_md.save()
##        del indicators_md
##
##        del indicators, indicators_template, layercode_snap_raster
##        del DisMapSeasonCodeDict, fields
##
##        arcpy.env.workspace = temp_workspace
##        del temp_workspace
##
##        # Elapsed time
##        end_time = time()
##        elapse_time =  end_time - start_time
##        msg = u"Elapsed Time {0} (H:M:S)\n".format(strftime("%H:%M:%S", gmtime(elapse_time)))
##        logFile(log_file, msg)
##        del msg, start_time, end_time, elapse_time, log_file
##
##        localKeys =  [key for key in locals().keys()]
##
##        if localKeys:
##            msg = "Local Keys in createIndicatorsTable(): {0}".format(u", ".join(localKeys))
##            print(msg)
##            del msg
##        del localKeys
##
##    except:
##        import sys, traceback
##        # Get the traceback object
##        tb = sys.exc_info()[2]
##        tbinfo = traceback.format_tb(tb)[0]
##        # Concatenate information together concerning the error into a message string
##        pymsg = f"PYTHON ERRORS:{chr(10)}Traceback info:{chr(10)}{tbinfo}{chr(10)}Error Info:{chr(10)}{str(sys.exc_info()[1])}"
##        print(pymsg)
##        del pymsg, tb, tbinfo
##
##def createLayerCodeBathymetry():
##    try: # The code with the exception that you want to catch. If an exception
##         # is raised, control flow leaves this block immediately and goes to
##         # the except block
##
##        # Uses the inspect module and a lamda to find name of this function
##        function = function_name()
##        # arcpy.AddMessage(function)
##
##        # Set a start time so that we can see how log things take
##        start_time = time()
##
##        # For benchmarking.
##        #timestr = strftime("%Y%m%d-%H%M%S")
##        timestr = strftime('%a %b %d %I %M %S %p', localtime())
##        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
##        del timestr
##
##        # Write a message to the log file
##        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##        # Set the workspace to the workspace
##        arcpy.env.workspace = ProjectGDB
##
##        # Set the scratch workspace to the ScratchGDB
##        arcpy.env.scratchWorkspace = ScratchGDB
##
##        # Set the overwriteOutput to True
##        arcpy.env.overwriteOutput = True
##
##        # Use all of the cores on the machine.
##        arcpy.env.parallelProcessingFactor = "100%"
##
##        # Set Log Metadata to False in order to not record all geoprocessing
##        # steps in metadata
##        arcpy.SetLogMetadata(False)
##
##        # Start looping over the datasets array as we go region by region.
##        for dataset in datasets:
##            # Assigning variables from items in the chosen table list
##            layercode = dataset[0]
##            region = dataset[1]
##            #layercode_csv_table = dataset[2]
##            #layercode_shape = dataset[3]
##            #layercode_boundary = dataset[4]
##            layercode_georef = dataset[5]
##            #layercode_contours = dataset[6]
##            cellsize = dataset[7]
##            del dataset
##
##            layercode_start_time = time()
##
##            # Write a message to the log file
##            msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg
##
##            # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
##            msg = f'> Generating {region} Fishnet Dataset'
##            logFile(log_file, msg); del msg
##
##            # Get the reference system defined for the region in datasets
##            #layercode_sr = dataset_srs[layercode_georef]
##            layercode_sr = arcpy.SpatialReference(layercode_georef)
##            arcpy.env.outputCoordinateSystem = layercode_sr
##            arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
##            # Delete after last use
##            del layercode_georef, layercode_sr
##
##            # Set cell size
##            arcpy.env.cellSize = cellsize
##
##            # Region datasets
##            layercode_survey_area = f"{layercode}_Survey_Area"
##            #layercode_boundary_line = f"{layercode}_Boundary_Line"
##            layercode_fish_net = f"{layercode}_Fish_Net"
##            #layercode_fish_net_label = layercode+"_Fish_Net_Label"
##            #layercode_fish_net_points = layercode+"_Fish_Net_Points"
##            layercode_raster_mask = f"{layercode}_Raster_Mask"
##            layercode_lat_long = f"{layercode}_Lat_Long"
##            layercode_latitude = f"{layercode}_Latitude"
##            layercode_longitude = f"{layercode}_Longitude"
##
##            bathymetry = os.path.join(BASE_DIRECTORY, r"{0}\{1}_Bathymetry".format(BathymetryGDB, layercode))
##            layercode_bathymetry = layercode+"_Bathymetry"
##
##            msg = f"> Feature to Raster Conversion to create Raster Mask"
##            logFile(log_file, msg); del msg
##            # Change mask to the region shape to create the raster mask
##            arcpy.env.mask = layercode_survey_area
##            arcpy.FeatureToRaster_conversion(layercode_survey_area, "ID", layercode_raster_mask, cellsize)
##
##            addMetadata(layercode_raster_mask, log_file)
##
##            # Resets a specific environment setting to its default
##            arcpy.ClearEnvironment("mask")
##
##            msg = f"> Point to Raster Conversion using {layercode_lat_long} to create {layercode_longitude}"
##            logFile(log_file, msg); del msg
##            # Process: Point to Raster Longitude
##            arcpy.env.cellSize = cellsize
##            arcpy.env.extent = arcpy.Describe(layercode_raster_mask).extent
##            arcpy.env.mask = layercode_raster_mask
##            arcpy.env.snapRaster = layercode_raster_mask
##
##            arcpy.PointToRaster_conversion(layercode_lat_long, "Longitude", layercode_longitude+"_tmp", "MOST_FREQUENT", "NONE", cellsize)
##
##            msg = f"> Extract by Mask to create {layercode_longitude}"
##            logFile(log_file, msg); del msg
##            # Execute ExtractByMask
##            outExtractByMask = arcpy.sa.ExtractByMask(layercode_longitude+"_tmp", layercode_raster_mask, "INSIDE", layercode_longitude+"_tmp")
##
##            # Save the output
##            outExtractByMask.save(layercode_longitude)
##            del outExtractByMask
##
##            arcpy.management.Delete(layercode_longitude+"_tmp")
##
##            addMetadata(layercode_longitude, log_file)
##
##            msg = f"> Point to Raster Conversion using {layercode_lat_long} to create {layercode_latitude}"
##            logFile(log_file, msg); del msg
##            # Process: Point to Raster Latitude
##            arcpy.PointToRaster_conversion(layercode_lat_long, "Latitude", layercode_latitude+"_tmp", "MOST_FREQUENT", "NONE", cellsize)
##
##            msg = f"> Extract by Mask to create {layercode_latitude}"
##            logFile(log_file, msg); del msg
##            # Execute ExtractByMask
##            outExtractByMask = arcpy.sa.ExtractByMask(layercode_latitude+"_tmp", layercode_raster_mask, "INSIDE", layercode_latitude+"_tmp")
##
##            # Save the output
##            outExtractByMask.save(layercode_latitude)
##            del outExtractByMask
##
##            arcpy.management.Delete(layercode_latitude+"_tmp")
##
##            addMetadata(layercode_latitude, log_file)
##
##            msg = f"> Zonal Statistics using {layercode_fish_net} and {os.path.basename(bathymetry)} to create {layercode_bathymetry}"
##            logFile(log_file, msg); del msg
##            # Execute ZonalStatistics
##            outZonalStatistics = arcpy.sa.ZonalStatistics(layercode_fish_net, "OID", bathymetry, "MEDIAN", "NODATA")
##
##            # Save the output
##            outZonalStatistics.save(layercode_bathymetry)
##
##            del outZonalStatistics
##
##            # Resets a specific environment setting to its default
##            arcpy.ClearEnvironment("cellSize")
##            arcpy.ClearEnvironment("extent")
##            arcpy.ClearEnvironment("mask")
##            arcpy.ClearEnvironment("snapRaster")
##
##            # Delete after last use
##            del layercode_survey_area, layercode_sr
##            del layercode, cellsize
##            del layercode_fish_net
##            del layercode_lat_long
##            del layercode_raster_mask, layercode_latitude, layercode_longitude
##            del layercode_bathymetry
##            del bathymetry
##
##            #Final benchmark for the region.
##            msg = f"ENDING REGION {region} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg, region
##
##            # Elapsed time
##            end_time = time()
##            elapse_time =  end_time - layercode_start_time
##            msg = f"Elapsed Time for {region}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)\n"
##            logFile(log_file, msg); del msg, end_time, elapse_time, layercode_start_time
##
##         #Final benchmark for the region.
##        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Elapsed time
##        end_time = time()
##        elapse_time =  end_time - start_time
##        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
##        logFile(log_file, msg); del msg
##
##        del start_time, end_time, elapse_time
##
##    except: # This code is executed only if an exception was raised in the
##            # try block. Code executed in this block is just like normal code:
##            # if there is an exception, it will not be automatically caught
##            # (and probably stop the program).
##        import sys, traceback
##        # Get the traceback object
##        tb = sys.exc_info()[2]
##        tbinfo = traceback.format_tb(tb)[0]
##        # Concatenate information together concerning the error into a message string
##        py_msg = f"PYTHON ERRORS:{chr(10)}Traceback info:{chr(10)}{tbinfo}{chr(10)}Error Info:{chr(10)}{str(sys.exc_info()[1])}"
##        arcpy_msg = f"Arcpy Errors: {chr(10)}{arcpy.GetMessages(2)}{chr(10)}"
##        #arcpy.AddError(py_msg)
##        #arcpy.AddError(arcpy_msg)
##        logFile(log_file.replace(".log", " ERROR.log"), py_msg)
##        logFile(log_file.replace(".log", " ERROR.log"), arcpy_msg)
##        del tb, tbinfo, py_msg, arcpy_msg, sys, traceback
##
##    else: # This code is executed only if no exceptions were raised in the try
##          # block. Code executed in this block is just like normal code: if
##          # there is an exception, it will not be automatically caught
##          # (and probably stop the program). Notice that if the else block is
##          # executed, then the except block is not, and vice versa. This block
##          # is optional.
##        # Use pass to skip this code block
##        # pass
##
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##    finally: # This code always executes after the other blocks, even if there
##             # was an uncaught exception (that didn’t cause a crash, obviously)
##             # or a return statement in one of the other blocks. Code executed
##             # in this block is just like normal code: if there is an exception,
##             # it will not be automatically caught (and probably stop the
##             # program). This block is also optional.
##
##        # Get list of local keys that may need to be deleted.
##        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]
##
##        # If there is a list of local keys, print the list, and then delete
##        # variables
##        if localKeys:
##            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
##            logFile(log_file, msg); del msg
##
##        del localKeys, function

##def createRegionFishNets():
##    try: # The code with the exception that you want to catch. If an exception
##         # is raised, control flow leaves this block immediately and goes to
##         # the except block
##
##        # Uses the inspect module and a lamda to find name of this function
##        function = function_name()
##        # arcpy.AddMessage(function)
##
##        # Set a start time so that we can see how log things take
##        start_time = time()
##
##        # For benchmarking.
##        #timestr = strftime("%Y%m%d-%H%M%S")
##        timestr = strftime('%a %b %d %I %M %S %p', localtime())
##        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
##        del timestr
##
##        # Write a message to the log file
##        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##        # Set the workspace to the workspace
##        arcpy.env.workspace = ProjectGDB
##
##        # Set the scratch workspace to the ScratchGDB
##        arcpy.env.scratchWorkspace = ScratchGDB
##
##        # Set the overwriteOutput to True
##        arcpy.env.overwriteOutput = True
##
##        # Use all of the cores on the machine.
##        arcpy.env.parallelProcessingFactor = "100%"
##
##        # Set Log Metadata to False in order to not record all geoprocessing
##        # steps in metadata
##        arcpy.SetLogMetadata(False)
##
##        # Start looping over the datasets array as we go region by region.
##        for dataset in datasets:
##            # Assigning variables from items in the chosen table list
##            layercode = dataset[0]
##            region = dataset[1]
##            #layercode_csv_table = dataset[2]
##            #layercode_shape = dataset[3]
##            #layercode_boundary = dataset[4]
##            layercode_georef = dataset[5]
##            #layercode_contours = dataset[6]
##            cellsize = dataset[7]
##            del dataset
##
##            layercode_start_time = time()
##
##            # Write a message to the log file
##            msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg
##
##            # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
##            msg = f'> Generating {region} Fishnet Dataset'
##            logFile(log_file, msg); del msg
##
##            # Get the reference system defined for the region in datasets
##            #layercode_sr = dataset_srs[layercode_georef]
##            layercode_sr = arcpy.SpatialReference(layercode_georef)
##
##            # Delete after last use
##            del layercode_georef
##
##            # Set the output coordinate system to what is needed for the
##            # DisMAP project
##            arcpy.env.outputCoordinateSystem = layercode_sr
##            arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
##            arcpy.env.cellSize = cellsize
##
##            layercode_survey_area = f"{layercode}_Survey_Area"
##            #layercode_boundary_line = f"{layercode}_Boundary_Line"
##            layercode_fish_net = f"{layercode}_Fish_Net"
### #           layercode_raster_mask = f"{layercode}_Raster_Mask"
##            layercode_lat_long = f"{layercode}_Lat_Long"
### #           layercode_latitude = f"{layercode}_Latitude"
### #           layercode_longitude = f"{layercode}_Longitude"
##
### #           bathymetry = os.path.join(BASE_DIRECTORY, r"{0}\{1}_Bathymetry".format(BathymetryGDB, layercode))
### #           layercode_bathymetry = layercode+"_Bathymetry"
##
### #           msg = f"> Feature to Raster Conversion to create aRaster Mask"
### #           logFile(log_file, msg); del msg
### #           # Change mask to the region shape to create the raster mask
### #           arcpy.env.mask = layercode_survey_area
### #           arcpy.FeatureToRaster_conversion(layercode_survey_area, "ID", layercode_raster_mask, cellsize)
##
### #           addMetadata(layercode_raster_mask, log_file)
##
##            # Resets a specific environment setting to its default
##            arcpy.ClearEnvironment("mask")
##
##            # Get Extent
##            extent = arcpy.Describe(layercode_survey_area).extent
##            X_Min, Y_Min, X_Max, Y_Max = extent.XMin, extent.YMin, extent.XMax, extent.YMax
##            del extent
##            # print("X_Min: {0}, Y_Min: {1}, X_Max: {2}, Y_Max: {3}\n".format(X_Min, Y_Min, X_Max, Y_Max))
##
##            msg = f"X_Min: {X_Min}\n"
##            msg = msg + f"Y_Min: {Y_Min}\n"
##            msg = msg + f"X_Max: {X_Max}\n"
##            msg = msg + f"Y_Max: {Y_Max}\n"
##            logFile(log_file, msg); del msg
##
##            # A list of coordinate pairs
##            pointList = [[X_Min, Y_Min], [X_Min, Y_Max], [X_Max, Y_Max]]
##
##            # Create an empty Point object
##            point = arcpy.Point()
##
##            # A list to hold the PointGeometry objects
##            pointGeometryList = []
##
##            # For each coordinate pair, populate the Point object and create a new
##            # PointGeometry object
##            for pt in pointList:
##                point.X = pt[0]
##                point.Y = pt[1]
##
##                pointGeometry = arcpy.PointGeometry(point, layercode_sr)
##                pointGeometryList.append(pointGeometry)
##                del pt, pointGeometry
##
##            # Delete after last use
##            del pointList, point
##
##            # Create a copy of the PointGeometry objects, by using pointGeometryList as
##            # input to the CopyFeatures tool.
##            layercode_points_tmp = f"{layercode}_Points_Temp"
##            arcpy.management.CopyFeatures(pointGeometryList, layercode_points_tmp)
##            del pointGeometryList
##
##            Coordinate_System = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
##            msg = f"> Add Geometry Attributes"
##            logFile(log_file, msg); del msg
##            # Process: Add Geometry Attributes
##            arcpy.management.AddGeometryAttributes(layercode_points_tmp, "POINT_X_Y_Z_M", "", "", Coordinate_System)
##            del Coordinate_System
##
##            msg = f"> Alter Field POINT_X to Longitude for {layercode_points_tmp}"
##            logFile(log_file, msg); del msg
##            #
##            arcpy.management.AlterField(layercode_points_tmp, "POINT_X", "Longitude", "Longitude")
##
##            msg = f"> Alter Field POINT_Y to Latitude for {layercode_points_tmp}"
##            logFile(log_file, msg); del msg
##            #
##            arcpy.management.AlterField(layercode_points_tmp, "POINT_Y", "Latitude", "Latitude")
##
##            layercode_points = f"{layercode}_Points"
##            msg = f"> Convert Coordinate Notation to add fields for DMS to create {os.path.basename(layercode_points)}"
##            logFile(log_file, msg); del msg
##
##            arcpy.ConvertCoordinateNotation_management(layercode_points_tmp,
##                                                       layercode_points,
##                                                       "Longitude",
##                                                       "Latitude",
##                                                       "DD_2",
##                                                       "DMS_2",
##                                                       None,
##                                                       layercode_sr,
##                                                       None,
##                                                       "INCLUDE_INVALID",
##                                                       )
##            # Delete after last use
##            del layercode_sr
##
##            arcpy.management.Delete(layercode_points_tmp)
##            del layercode_points_tmp
##
##            fields = ['DMSLat', 'DMSLon',]
##
##            # Create update cursor for Dataset
##            with arcpy.da.UpdateCursor(layercode_points, fields) as cursor:
##                for row in cursor:
##                    row[0] = row[0][:][:-7] + row[0][:][-1:]
##                    row[1] = row[1][:][:-7] + row[1][:][-1:]
##                    cursor.updateRow(row)
##                    del row
##            del fields, cursor
##
##            msg = f"> Delete Field ORIG_FID from {os.path.basename(layercode_points)}"
##            logFile(log_file, msg); del msg
##            # Execute DeleteField
##            arcpy.management.DeleteField(layercode_points, ['ORIG_OID'])
##
##            # Add metadata
##            addMetadata(layercode_points, log_file)
##
##            # Clearup after last use
##            del layercode_points
##
##            # CreateFishnet(out_feature_class, origin_coord, y_axis_coord, cell_width, cell_height, number_rows, number_columns, {corner_coord}, {labels}, {template}, {geometry_type})
##            #outFeatureClass = layercode_fish_net
##            # Set the origin of the fishnet
##            originCoordinate = f'{X_Min} {Y_Min}'
##            # Set the orientation
##            yAxisCoordinate = f'{X_Min} {Y_Max}'
##            # Enter 0 for width and height - these values will be calcualted by the tool
##            cellSizeWidth = f'{cellsize}'
##            cellSizeHeight = f'{cellsize}'
##            # Number of rows and columns together with origin and opposite corner
##            # determine the size of each cell
##            numRows =  ''
##            numColumns = ''
##            oppositeCoorner = f'{X_Max} {Y_Max}'
##            # Create a point label Dataset
##            labels = 'NO_LABELS'
##            # Extent is set by origin and opposite corner - no need to use a template fc
##            templateExtent = f"{X_Min} {Y_Min} {X_Max} {Y_Max}"
##            # Each output cell will be a polygon
##            geometryType = 'POLYGON'
##            #Coordinate_System = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
##            msg = f"> Create Fishnet with {cellSizeWidth} by {cellSizeHeight} cells"
##            logFile(log_file, msg); del msg
##            arcpy.CreateFishnet_management(layercode_fish_net, originCoordinate, yAxisCoordinate, cellSizeWidth, cellSizeHeight, numRows, numColumns, oppositeCoorner, labels, templateExtent, geometryType)
##
##            del X_Min, Y_Min, X_Max, Y_Max
##            del originCoordinate, yAxisCoordinate, cellSizeWidth
##            del cellSizeHeight, numRows, numColumns, oppositeCoorner, labels
##            del templateExtent, geometryType
##
### ###--->>> Select by location and trim
##            msg = f"> Make Feature Layer for {'{0}_Fish_Net_Layer'.format(layercode)}"
##            logFile(log_file, msg); del msg
##            layercode_fish_net_layer = arcpy.management.MakeFeatureLayer(layercode_fish_net, "{0}_Fish_Net_Layer".format(layercode))
##
##            msg = f"> Select Layer by Location"
##            logFile(log_file, msg); del msg
##            #arcpy.management.SelectLayerByLocation(layercode_fish_net_layer, "HAVE_THEIR_CENTER_IN", layercode_survey_area, 0, "NEW_SELECTION", "INVERT") # WITHIN_A_DISTANCE, CONTAINS, INTERSECT, WITHIN, WITHIN_CLEMENTINI, HAVE_THEIR_CENTER_IN
##            arcpy.management.SelectLayerByLocation(layercode_fish_net_layer, "WITHIN_A_DISTANCE", layercode_survey_area, 25000, "NEW_SELECTION", "INVERT")
##
##            msg = f"> Delete Features from {'{0}_Fish_Net_Layer'.format(layercode)}"
##            logFile(log_file, msg); del msg
##            arcpy.DeleteFeatures_management(layercode_fish_net_layer)
##
##            addMetadata(layercode_fish_net, log_file)
##
##            msg = f"> Deleting {'{0}_Fish_Net_Layer'.format(layercode)}"
##            logFile(log_file, msg); del msg
##            arcpy.management.Delete("{0}_Fish_Net_Layer".format(layercode))
##            #arcpy.management.Delete("{0}_Fish_Net_Label_Layer".format(layercode))
##            del layercode_fish_net_layer #, layercode_fish_net_label_layer
##
### #           msg = f"> Calculate Field GRID_ID"
### #           logFile(log_file, msg); del msg
### #           arcpy.management.CalculateField(in_table=layercode_fish_net, field="GRID_ID", expression='!OID!', expression_type="PYTHON", code_block="")
##
##            msg = f"> Feature to Point using {os.path.basename(layercode_fish_net)} to create {os.path.basename(layercode_lat_long)}"
##            logFile(log_file, msg); del msg
##            #
##            arcpy.FeatureToPoint_management(layercode_fish_net, layercode_lat_long, "CENTROID")
##
##            msg = f"> Delete Field ORIG_FID from {os.path.basename(layercode_lat_long)}"
##            logFile(log_file, msg); del msg
##            # Execute DeleteField
##            arcpy.management.DeleteField(layercode_lat_long, ['ORIG_FID'])
##
##            Coordinate_System = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
##            msg = f"> Add Geometry Attributes to {os.path.basename(layercode_lat_long)}"
##            logFile(log_file, msg); del msg
##            # Process: Add Geometry Attributes
##            arcpy.management.AddGeometryAttributes(layercode_lat_long, "POINT_X_Y_Z_M", "", "", Coordinate_System)
##            del Coordinate_System
##
##            msg = f"> Alter Field POINT_X to Longitude for {os.path.basename(layercode_lat_long)}"
##            logFile(log_file, msg); del msg
##            #
##            arcpy.management.AlterField(layercode_lat_long, "POINT_X", "Longitude", "Longitude")
##
##            msg = f"> Alter Field POINT_Y to Latitude for {os.path.basename(layercode_lat_long)}"
##            logFile(log_file, msg); del msg
##            #
##            arcpy.management.AlterField(layercode_lat_long, "POINT_Y", "Latitude", "Latitude")
##
### #           msg = f"> PointToRaster_conversion"
### #           logFile(log_file, msg); del msg
### #           # Process: Point to Raster Longitude
### #           arcpy.env.cellSize = cellsize
### #           arcpy.env.extent = arcpy.Describe(layercode_raster_mask).extent
### #           arcpy.env.mask = layercode_raster_mask
### #           arcpy.env.snapRaster = layercode_raster_mask
##
### #           arcpy.PointToRaster_conversion(layercode_lat_long, "Longitude", layercode_longitude, "MOST_FREQUENT", "NONE", cellsize)
##
### #           addMetadata(layercode_longitude, log_file)
##
### #           msg = f"> Point to Raster Conversion"
### #           logFile(log_file, msg); del msg
### #           # Process: Point to Raster Latitude
### #           arcpy.PointToRaster_conversion(layercode_lat_long, "Latitude", layercode_latitude, "MOST_FREQUENT", "NONE", cellsize)
##
### #           addMetadata(layercode_latitude, log_file)
##
### #           # Execute ZonalStatistics
### #           outZonalStatistics = arcpy.sa.ZonalStatistics(layercode_fish_net, "GRID_ID", bathymetry, "MEDIAN", "NODATA")
##
### #           # Save the output
### #           outZonalStatistics.save(layercode_bathymetry)
##
### #           del outZonalStatistics
##
##            # Resets a specific environment setting to its default
##            arcpy.ClearEnvironment("cellSize")
##            arcpy.ClearEnvironment("extent")
##            arcpy.ClearEnvironment("mask")
##            arcpy.ClearEnvironment("snapRaster")
##
##            # Delete after last use
##            del layercode_survey_area
##            del layercode, cellsize
##            del layercode_fish_net #, layercode_fish_net_label
##            del layercode_lat_long
##
##            #Final benchmark for the region.
##            msg = f"ENDING REGION {region} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg, region
##
##            # Elapsed time
##            end_time = time()
##            elapse_time =  end_time - layercode_start_time
##            msg = f"Elapsed Time for {region}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)\n"
##            logFile(log_file, msg); del msg, end_time, elapse_time, layercode_start_time
##
##         #Final benchmark for the region.
##        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Elapsed time
##        end_time = time()
##        elapse_time =  end_time - start_time
##        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
##        logFile(log_file, msg); del msg
##
##        del start_time, end_time, elapse_time
##
##    except: # This code is executed only if an exception was raised in the
##            # try block. Code executed in this block is just like normal code:
##            # if there is an exception, it will not be automatically caught
##            # (and probably stop the program).
##        import sys, traceback
##        # Get the traceback object
##        tb = sys.exc_info()[2]
##        tbinfo = traceback.format_tb(tb)[0]
##        # Concatenate information together concerning the error into a message string
##        py_msg = f"PYTHON ERRORS:{chr(10)}Traceback info:{chr(10)}{tbinfo}{chr(10)}Error Info:{chr(10)}{str(sys.exc_info()[1])}"
##        arcpy_msg = f"Arcpy Errors: {chr(10)}{arcpy.GetMessages(2)}{chr(10)}"
##        logFile(log_file.replace(".log", " ERROR.log"), py_msg)
##        logFile(log_file.replace(".log", " ERROR.log"), arcpy_msg)
##        del tb, tbinfo, py_msg, arcpy_msg, sys, traceback
##
##    else: # This code is executed only if no exceptions were raised in the try
##          # block. Code executed in this block is just like normal code: if
##          # there is an exception, it will not be automatically caught
##          # (and probably stop the program). Notice that if the else block is
##          # executed, then the except block is not, and vice versa. This block
##          # is optional.
##        # Use pass to skip this code block
##        # pass
##
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##    finally: # This code always executes after the other blocks, even if there
##             # was an uncaught exception (that didn’t cause a crash, obviously)
##             # or a return statement in one of the other blocks. Code executed
##             # in this block is just like normal code: if there is an exception,
##             # it will not be automatically caught (and probably stop the
##             # program). This block is also optional.
##
##        # Get list of local keys that may need to be deleted.
##        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]
##
##        # If there is a list of local keys, print the list, and then delete
##        # variables
##        if localKeys:
##            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
##            logFile(log_file, msg); del msg
##
##        del localKeys, function

def createCoreSpeciesRichnessRasters(args):
    """Create Table"""
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        # Set a start time so that we can see how log things take
        start_time = time()

        CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = ScratchGDB
        arcpy.env.rasterStatistics = u'STATISTICS 1 1'
        arcpy.env.buildStatsAndRATForTempRaster = True

        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            #layercode_shape = table_name[0]
            #layercode_boundary = table_name[1]
            layercode = table_name[2]
            region = table_name[3]
            csv_file = table_name[4]
            layercode_georef = table_name[5]
            #layercode_contours = table_name[6]
            cell_size = table_name[7]

            # Set the output coordinate system to what is available for us.
            layercode_sr = srs[layercode_georef]
            arcpy.env.outputCoordinateSystem = layercode_sr

            #layercode_shape = os.path.join(ProjectGDB, layercode+"_Shape")
            layercode_snap_raster = os.path.join(ProjectGDB, layercode+"_Snap_Raster")
            layercode_raster_mask = os.path.join(ProjectGDB, layercode+"_Raster_Mask")

            arcpy.env.snapRaster = layercode_snap_raster
            # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
            arcpy.env.extent = arcpy.Describe(layercode_snap_raster).extent
            arcpy.env.mask = layercode_raster_mask

            # These are used later to set the rows and columns for a zero numpy array
            rowCount = int(arcpy.management.GetRasterProperties(layercode_snap_raster, "ROWCOUNT" ).getOutput(0))
            columnCount = int(arcpy.management.GetRasterProperties(layercode_snap_raster, "COLUMNCOUNT" ).getOutput(0))

            msg = ">-> Region (abb): {0}\n\t Region:  {1}".format(layercode, region)
            logFile(log_file, msg)

            # Region richness raster
            # Set layercode_year_richness_path
            layercode_year_richness_path = os.path.join(ANALYSIS_DIRECTORY, layercode, "Core Species Richness")

            if not os.path.isdir(layercode_year_richness_path):
                os.makedirs(layercode_year_richness_path)

            if ReplaceRegionYearRichness:
                tmp_workspace = arcpy.env.workspace
                arcpy.env.workspace = layercode_year_richness_path
                rs = arcpy.ListRasters("*Core_Species_Richness*")
                for r in rs: arcpy.management.Delete(r); del r
                del rs
                arcpy.env.workspace = tmp_workspace
                del tmp_workspace

            # Define layercode_mosaic
            layercode_mosaic = os.path.join(ProjectGDB, layercode)
            # Make layercode_mosaic_layer
            layercode_mosaic_layer = arcpy.management.MakeMosaicLayer(layercode_mosaic, "layercode_mosaic_layer")

            # Get a unique list of years from the layercode_mosaic_layer
            years = unique_years(layercode_mosaic_layer)
            #years = unique_years(layercode_mosaic)

            if arcpy.Exists("layercode_mosaic_layer"): arcpy.management.Delete("layercode_mosaic_layer")
            del layercode_mosaic_layer

            # Test if we are filtering on years. If so, a new year list is
            # created with the selected years remaining in the list
            #if FilterYears:
            #    # Get a shorter list
            #    years = [y for y in years if y in selected_years]
            #else:
            #    pass

            for year in years:

                layercode_year_base_name = "{0}_{1}_".format(layercode, year)

                layercode_year_richness = os.path.join(layercode_year_richness_path, "{0}Core_Species_Richness.tif".format(layercode_year_base_name))

                if not os.path.isfile(layercode_year_richness) or ReplaceRegionYearRichness:

                    msg = ">->-> Year: {0}".format(year)
                    logFile(log_file, msg)

                    # Set workspace
                    arcpy.env.workspace = ScratchFolder

                    msg = ">->->-> arcpy.management.ExportMosaicDatasetItems"
                    logFile(log_file, msg)

                    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
                    # The following inputs are layers or table views: "layercode_mosaic_layer"

                    arcpy.management.ExportMosaicDatasetItems(#in_mosaic_dataset = "layercode_mosaic_layer",
                                                              in_mosaic_dataset = layercode_mosaic,
                                                              out_folder = ScratchFolder,
                                                              out_base_name = layercode_year_base_name,
                                                              where_clause = "Year = {0} AND CoreSpecies = 'Yes' AND Variable NOT IN ('Species Richness', 'Core Species Richness')".format(year),
                                                              format = "TIFF",
                                                              nodata_value = "-3.40282346639e+38", #-3.402823e+38
                                                              clip_type = "NONE",
                                                              template_dataset = "DEFAULT",
                                                              cell_size = "{0} {0}".format(cell_size))

                    msg = arcpy.GetMessages()
                    msg = ">->->-> {0}\n".format(msg.replace('\n', '\n>->->-> '))
                    logFile(log_file, msg)

                    # Get a list of rasters that are exported from the arcpy.management.ExportMosaicDatasetItems tool
                    # These, for some reason, have TIF as an extension
                    rasters = [r for r in arcpy.ListRasters("{0}*.TIF".format(layercode_year_base_name)) if "Richness" not in r]
                    for raster in rasters: arcpy.management.CalculateStatistics(raster)
                    del raster
                    #print(rasters)

                    #richnessArray = np.zeros((rowCount, columnCount), dtype=int, order='C')
                    #richnessArray = np.zeros((rowCount, columnCount), dtype=float, order='C')
                    #richnessArray = np.zeros((rowCount, columnCount), dtype=np.int32, order='C')
                    richnessArray = np.zeros((rowCount, columnCount), dtype='float32', order='C')

                    msg = ">->->-> Processing rasters"
                    logFile(log_file, msg)
                    # For each raster exported, create the Con mask
                    for raster in rasters:
                        #arcpy.management.CalculateStatistics(raster)
                        msg = ">->->->-> Processing {0} raster".format(raster)
                        logFile(log_file, msg)

                        # Get Raster Maximum to test of zero rasters
                        #rasterMaximum = float(arcpy.management.GetRasterProperties(raster,"MAXIMUM").getOutput(0))

                        # If Raster Maximum greater than zero, then proceed
                        #if rasterMaximum > 0.0:

                        rasterArray = arcpy.RasterToNumPyArray(raster, nodata_to_value=np.nan)
                        #rasterArray = rasterArray.astype('float32')
                        rasterArray[rasterArray < 0.0] = np.nan

    ##                    maximumRasterArray = np.nanmax(rasterArray)
    ##                    minimumRasterArray = np.nanmin(rasterArray)
    ##
    ##                    msg = ">->->->-> Maximum Biomass Array:         {0}".format(maximumRasterArray)
    ##                    print(msg)
    ##                    del msg
    ##
    ##                    msg = ">->->->-> Minimum Biomass Array:         {0}".format(minimumRasterArray)
    ##                    print(msg)
    ##                    del msg

                        rasterArray[rasterArray > 0.0] = 1.0

    ##                    maximumRasterArray = np.nanmax(rasterArray)
    ##                    minimumRasterArray = np.nanmin(rasterArray)
    ##
    ##                    msg = ">->->->-> Maximum Biomass Array:         {0}".format(maximumRasterArray)
    ##                    print(msg)
    ##                    del msg
    ##
    ##                    msg = ">->->->-> Minimum Biomass Array:         {0}".format(minimumRasterArray)
    ##                    print(msg)
    ##                    del msg

                        #add rasterArray to richnessArray
                        richnessArray = np.add(richnessArray, rasterArray)
                        # Can also use: richnessArray + rasterArray
                        del rasterArray
                    # cleanup
                    # del rasterMaximum

                    #richnessArray[richnessArray <= 0] = np.nan

                    msg = ">->->-> Creating Richness Raster"
                    logFile(log_file, msg)

                    # Create Raster from Array
                    snapRaster = arcpy.Raster(layercode_snap_raster)
                    lowerLeft = arcpy.Point(snapRaster.extent.XMin, snapRaster.extent.YMin)
                    del snapRaster

                    # Cast array as float32
                    richnessArray = richnessArray.astype('float32')

                    # Convert Array to Raster
                    richnessArrayRaster = arcpy.NumPyArrayToRaster(richnessArray, lowerLeft, cell_size, cell_size, -3.40282346639e+38) #-3.40282346639e+38
                    richnessArrayRaster.save(layercode_year_richness)
                    del richnessArray, richnessArrayRaster, lowerLeft
                    del rasters

                    arcpy.management.CalculateStatistics(layercode_year_richness)

                    # Add metadata
                    layercode_year_richness_md = md.Metadata(layercode_year_richness)
                    layercode_year_richness_md.synchronize('ACCESSED', 1)
                    layercode_year_richness_md.title = "{0} {1}".format(region.replace('-',' to '), DateCode)
                    layercode_year_richness_md.tags = "{0}, {1}, Core Species Richness".format(geographic_regions[layercode], year)
                    layercode_year_richness_md.save()
                    del layercode_year_richness_md

                    # ###--->>>

                    tmp_workspace = arcpy.env.workspace
                    arcpy.env.workspace = ScratchFolder
                    msg = ">->->-> arcpy.management.Delete in ScratchFolder"
                    logFile(log_file, msg)
                    # This removes the saved rasters in the ScratchFolder
                    #for raster in [r for r in arcpy.ListRasters("*") if "Richness" not in r]: arcpy.management.Delete(raster)
                    for raster in arcpy.ListRasters("*"): arcpy.management.Delete(raster)
                    del raster
                    arcpy.env.workspace = tmp_workspace
                    del tmp_workspace

            # ###--->>>

            # Loading images into the Mosaic.
            msg = '>->->-> Loading the {} Mosaic. This may take a while... Please wait...'.format(region)
            logFile(log_file, msg)

            arcpy.management.AddRastersToMosaicDataset(in_mosaic_dataset = layercode_mosaic,
                                                       raster_type = "Raster Dataset",
                                                       input_path = layercode_year_richness_path,
                                                       #input_path = layercode_year_richness,
                                                       update_cellsize_ranges = "UPDATE_CELL_SIZES",
                                                       #update_cellsize_ranges = "NO_CELL_SIZES",
                                                       update_boundary = "UPDATE_BOUNDARY",
                                                       #update_boundary = "NO_BOUNDARY",
                                                       update_overviews = "NO_OVERVIEWS",
                                                       maximum_pyramid_levels = "",
                                                       maximum_cell_size = "0",
                                                       minimum_dimension = "1500",
                                                       spatial_reference = layercode_sr,
                                                       #filter = "*Richness.tif",
                                                       filter = "*Core_Species_Richness.tif",
                                                       sub_folder = "NO_SUBFOLDERS",
                                                       #duplicate_items_action = "OVERWRITE_DUPLICATES",
                                                       duplicate_items_action = "EXCLUDE_DUPLICATES",
                                                       build_pyramids = "NO_PYRAMIDS",
                                                       calculate_statistics = "CALCULATE_STATISTICS",
                                                       #calculate_statistics = "NO_STATISTICS",
                                                       build_thumbnails = "BUILD_THUMBNAILS",
                                                       #build_thumbnails = "NO_THUMBNAILS",
                                                       operation_description = "",
                                                       #force_spatial_reference = "NO_FORCE_SPATIAL_REFERENCE",
                                                       force_spatial_reference = "FORCE_SPATIAL_REFERENCE",
                                                       estimate_statistics = "ESTIMATE_STATISTICS",
                                                       #estimate_statistics = "NO_STATISTICS",
                                                       )

            del layercode_year_richness, layercode_year_richness_path

            msg = ">->->-> Calculating new values for the new fields in the regional Mosaic Dataset"
            logFile(log_file, msg)

            msg = ">->->-> arcpy.management.MakeTableView Variable_View"
            logFile(log_file, msg)
            # For Multidimensional data (https://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/wkfl-create-a-multidimensional-mosaic-dataset-from-a-set-of-time-series-images.htm)
            # Make table view for calculations
            #arcpy.management.MakeTableView(in_table=layercode_richness_mosaic, out_view="Variable_View", where_clause="Variable IS NULL", workspace="", )
            arcpy.management.MakeTableView(in_table=layercode_mosaic, out_view="Variable_View", where_clause="Variable IS NULL OR Variable = 'Core Species Richness'", workspace="", )

            msg = ">->->-> arcpy.management.CalculateField Region"
            logFile(log_file, msg)
            # Process: Calculate Region Field
            arcpy.management.CalculateField("Variable_View", "OARegion", "'{0}'".format(region.replace("'","''")), "PYTHON", "")

            msg = ">->->-> arcpy.management.CalculateField CoreSpecies"
            logFile(log_file, msg)
            # Process: Calculate Region Field
            arcpy.management.CalculateField("Variable_View", "CoreSpecies", "'Yes'", "PYTHON", "")

            msg = ">->->-> arcpy.management.CalculateField Year"
            logFile(log_file, msg)
            # Process: Calculate Year Field
            arcpy.management.CalculateField("Variable_View", "Year", expression="MakeInt( !Name!)", expression_type="PYTHON", code_block="def MakeInt(name):   return int(name[-21:-17]) if 'Core' not in name else int(name[-26:-22])")

            msg = ">->->-> arcpy.management.CalculateField Variable"
            logFile(log_file, msg)
            # Process: Calculate Species Field
            arcpy.management.CalculateField("Variable_View", "Variable", "'Core Species Richness'", "PYTHON", "")

            codeBlock = """def getDate(region, year):
                              from datetime import datetime
                              import pytz
                              regionDateDict = {# Region : Month, Day, Time Zone
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

            msg = ">->->-> arcpy.management.CalculateField StdTime"
            logFile(log_file, msg)
            arcpy.management.CalculateField("Variable_View", "StdTime", expression="getDate( !OARegion!, !Year! )", expression_type="PYTHON", code_block=codeBlock)
            del codeBlock

            msg = ">->->-> arcpy.management.CalculateField Dimensions"
            logFile(log_file, msg); del msg

            arcpy.management.CalculateField(in_table="Variable_View", field="Dimensions", expression="'StdTime'", expression_type="PYTHON", code_block="")

            arcpy.management.Delete("Variable_View")

            # Cleanup
            del layercode_mosaic, layercode
            del layercode_georef, year, years
            del table_name, csv_file, layercode_year_base_name
            del region, layercode_sr
            del rowCount, columnCount
            del layercode_snap_raster, layercode_raster_mask, cell_size

        # Cleanup
        del log_file

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"#-> Elapsed Time for {0} {1} (H:M:S)\n".format(function, strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

def createDatasetTable(args):
    """Create Dataset Table"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        import pandas as pd
        import numpy as np
        import warnings

        start_time = time()

        CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr, log_file_folder

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB; del ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        datasets = "Datasets"
        input_datasets_csv_table = os.path.join(CSV_DIRECTORY, f"{datasets}.csv")
        del CSV_DIRECTORY

        #
        msg = f'> Generating Datasets CSV Table: {os.path.basename(input_datasets_csv_table)}'
        logFile(log_file, msg); del msg

        # https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/09_timeseries.html?highlight=datetime
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        #df = pd.read_csv('my_file.tsv', sep='\t', header=0)  ## not setting the index_col
        #df.set_index(['0'], inplace=True)

        # C:\. . .\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\lib\site-packages\numpy\lib\arraysetops.py:583:
        # FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
        # mask |= (ar1 == a)
        # A fix: https://www.youtube.com/watch?v=TTeElATMpoI
        # TLDR: pandas are Jedi; numpy are the hutts; and python is the galatic empire
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            # DataFrame
            df = pd.read_csv(input_datasets_csv_table,
                             index_col = 0,
                             encoding="utf-8",
                             #encoding = "ISO-8859-1",
                             #engine='python',
                             delimiter = ',',
                             #dtype = None,
                             dtype = {
                                      "OARegionCode"            : str,
                                      "OARegion"                : str,
                                      "DisMapRegionCode"        : str,
                                      "DisMapSeasonCode"        : str,
                                      "LayerCode"               : str,
                                      "LayerName"               : str,
                                      "DateCode"                : 'uint16',
                                      "DistributionProjectName" : str,
                                      "DistributionProjectCode" : str,
                                      "Region"                  : str,
                                      "SeasonCode"              : str,
                                      "SummaryProduct"          : str,
                                      "CSVFile"                 : str,
                                      "GeographicArea"          : str,
                                      "CoordinateSystem"        : str,
                                      "CellSize"                : 'uint16',
                                      "TransformUnit"           : str,
                                      "TimeZone"                : str,
                                      },
                             )
        del input_datasets_csv_table

        msg = f'>-> Defining the column names.'
        logFile(log_file, msg); del msg

        # The original column names from the CSV files are not very
        # reader friendly, so we are making some changes here
        #df.columns = [u'Region', u'HUALID', u'Year', u'Species', u'WTCPUE', u'CommonName', u'Stratum', u'StratumArea', u'Latitude', u'Longitude', u'Depth']
        df.columns = ["OARegionCode", "OARegion", "DisMapRegionCode", "DisMapSeasonCode", "LayerCode", "LayerName", "DateCode", "DistributionProjectName", "DistributionProjectCode", "Region", "Season", "SummaryProduct", "CSVFile", "GeographicArea", "CoordinateSystem", "CellSize", "TransformUnit", "TimeZone"]

        # Replace NaN with an empty string. When pandas reads a cell
        # with missing data, it asigns that cell with a Null or nan
        # value. So, we are changing that value to an empty string of ''.

        df.fillna('', inplace=True)

        msg = f'>-> Creating the {datasets} Geodatabase Table'
        logFile(log_file, msg); del msg

        # ###--->>> Numpy Datatypes
        # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm

        #print('DataFrame\n----------\n', df.head(10))
        #print('\nDataFrame datatypes :\n', df.dtypes)
        #columns = [str(c) for c in df.dtypes.index.tolist()]
        column_names = list(df.columns)
        #print(column_names)
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        column_formats = ['S10', 'S30', 'S40', 'S10', 'S20', 'S40', 'u4', 'S60', 'S5', 'S40', 'S10', 'S5', 'S20', 'S20', 'S30', 'u4', 'S30', 'S20']
        # # OARegionCode            = 9 (10)
        # # OARegion                = 30 (30)
        # # DisMapRegionCode        = 33 (40)
        # # DisMapSeasonCode        = 9 (10)
        # # LayerCode               = 12 (20)
        # # LayerName               = 35 (40)
        # # DateCode                = 8 (10)
        # # DistributionProjectName = 52 (60)
        # # DistributionProjectCode = 5 (5)
        # # Region                  = 31 (40)
        # # SeasonCode              = 9 (10)
        # # SummaryProduct          = 3 (5)
        # # CSVFile                 = 16 (20)
        # # GeographicArea          = 18 (20)
        # # CoordinateSystem        = 26 (30)
        # # CellSize                = 18 (20)
        # # TransformUnit           = 26 (30)
        # # TimeZone                = 20

        dtypes = list(zip(column_names, column_formats))
        del column_names, column_formats

        #print(df)
        try:
            array = np.array(np.rec.fromrecords(df.values), dtype = dtypes)
        except Exception as e:
            import sys
            # Capture all other errors
            #print(sys.exc_info()[2].tb_lineno)
            msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
            if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
            else: print(msg); del msg, sys

        del df, dtypes

        # Temporary table
        tmp_table = f'memory\{datasets.lower()}_tmp'

        try:
            arcpy.da.NumPyArrayToTable(array, tmp_table)
            del array
        except arcpy.ExecuteError:
            import sys
            # Geoprocessor threw an error
            #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
            msg = arcpy.GetMessages(2).replace('\n', '\n\t')
            msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
            if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
            else: print(msg); del msg, sys

        msg = f'>-> Copying the Datasets Table from memory to the GDB'
        logFile(log_file, msg); del msg

        datasets_table = os.path.join(ProjectGDB, datasets)

        template_datasets = "_Template_Datasets"
        template_datasets_path = os.path.join(ProjectGDB, template_datasets)

        createTemplateTables({k: v for k, v in template_table_dictionary.items() if k.startswith(template_datasets)})

        # Execute CreateTable
        arcpy.management.CreateTable(ProjectGDB, datasets, template_datasets_path, "", "")

        del ProjectGDB, template_datasets_path, template_datasets

        arcpy.CopyRows_management(tmp_table, datasets_table, "")

        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        msg = f'>-> Updating the field aliases for the {os.path.basename(datasets_table)} Table'
        logFile(log_file, msg); del msg

        # Field Alias Dictionary
        field_alias = {
                       "OARegionCode"            : "OA Region Code",
                       "OARegion"                : "OA Region",
                       "DisMapRegionCode"        : "DisMAP Region Code",
                       "DisMapSeasonCode"        : "DisMAP Season Code",
                       "LayerCode"               : "Layer Code",
                       "LayerName"               : "Layer Name",
                       "DateCode"                : "Date Code",
                       "DistributionProjectName" : "Distribution Project Name",
                       "DistributionProjectCode" : "Distribution Project Code",
                       "Region"                  : "Region",
                       "Season"                  : "Season",
                       "SummaryProduct"          : "Summary Product",
                       "CSVFile"                 : "CSVFile",
                       "GeographicArea"          : "Geographic Area",
                       "CoordinateSystem"        : "Coordinate System",
                       "CellSize"                : "CellSize",
                       "TransformUnit"           : "Transform Unit",
                       "TimeZone"                : "Time Zone",
                      }

        # Alter Field Alias
        alterFieldAlias(datasets_table, field_alias, log_file)
        #
        del field_alias

        msg = f'>-> Adding metadata to the {datasets} Table'
        logFile(log_file, msg); del msg

        # Add Metadata
        addMetadata(datasets_table, log_file)

        # Cleanup
        del datasets, datasets_table

        del pd, np, warnings

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def createFolders(basefolder):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        print(f"Basefolder: {os.path.basename(basefolder)}")
        os.chdir(basefolder)
        args = [CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder]
        datasets = generateDatasets(args)
        #print(len(datasets))
        for i in range(len(datasets)):
            layercode = datasets[i][4]
            del i
            try:
                print(f"\tCreating folder: {layercode}")
                os.makedirs(layercode)
            except FileExistsError:
                pass

        del basefolder, args, datasets, layercode

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg, sys
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def createMasterSpeciesInformationTable(args):
    """Create Master Species Information Table"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        import pandas as pd
        import numpy as np
        import warnings

        start_time = time()

        CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr, log_file_folder

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB; del ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        masterspeciestnformation = "MasterSpeciesInformation"
        masterspeciestnformation_csv_table = os.path.join(CSV_DIRECTORY, f"{masterspeciestnformation}.csv")
        del CSV_DIRECTORY

        #
        msg = f'> Generating {masterspeciestnformation} CSV Table: {os.path.basename(masterspeciestnformation_csv_table)}'
        logFile(log_file, msg); del msg

        # https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/09_timeseries.html?highlight=datetime
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        #df = pd.read_csv('my_file.tsv', sep='\t', header=0)  ## not setting the index_col
        #df.set_index(['0'], inplace=True)

        # C:\. . .\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\lib\site-packages\numpy\lib\arraysetops.py:583:
        # FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
        # mask |= (ar1 == a)
        # A fix: https://www.youtube.com/watch?v=TTeElATMpoI
        # TLDR: pandas are Jedi; numpy are the hutts; and python is the galatic empire
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            # DataFrame
            df = pd.read_csv(masterspeciestnformation_csv_table,
                             index_col = 0,
                             encoding="utf-8",
                             #encoding = "ISO-8859-1",
                             #engine='python',
                             delimiter = ',',
                             #dtype = None,
                             dtype = {
                                      "Species"           : str,
                                      "CommonName"        : str,
                                      "SpeciesCommonName" : str,
                                      "CommonNameSpecies" : str,
                                      "TaxonomicGroup"    : str,
                                      },
                             )
        del masterspeciestnformation_csv_table

        #print(df)

        msg = f'>-> Defining the column names.'
        logFile(log_file, msg); del msg

        # The original column names from the CSV files are not very
        # reader friendly, so we are making some changes here
        #df.columns = [u'Region', u'HUALID', u'Year', u'Species', u'WTCPUE', u'CommonName', u'Stratum', u'StratumArea', u'Latitude', u'Longitude', u'Depth']
        df.columns = ["Species", "CommonName", "SpeciesCommonName", "CommonNameSpecies", "TaxonomicGroup"]

        # Replace NaN with an empty string. When pandas reads a cell
        # with missing data, it asigns that cell with a Null or nan
        # value. So, we are changing that value to an empty string of ''.

        df.fillna('', inplace=True)

        msg = f'>-> Creating the {masterspeciestnformation} Geodatabase Table'
        logFile(log_file, msg); del msg

        # ###--->>> Numpy Datatypes
        # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm

        #print('DataFrame\n----------\n', df.head(10))
        #print('\nDataFrame datatypes :\n', df.dtypes)
        #columns = [str(c) for c in df.dtypes.index.tolist()]
        column_names = list(df.columns)
        #print(column_names)
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        column_formats = ['S50', 'U50', 'U100', 'U100', 'S50', ]
        # # "Species" 50
        # # "CommonName" 50
        # # "SpeciesCommonName" 100
        # # "CommonNameSpecies" 100
        # # "TaxonomicGroup" 50

        dtypes = list(zip(column_names, column_formats))
        del column_names, column_formats
        #print(dtypes)

        #print(df)
        try:
            array = np.array(np.rec.fromrecords(df.values), dtype = dtypes)
        except Exception as e:
            import sys
            # Capture all other errors
            #print(sys.exc_info()[2].tb_lineno)
            msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
            if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
            else: print(msg); del msg, sys

        del df, dtypes

        # Temporary table
        tmp_table = f'memory\{masterspeciestnformation.lower()}_tmp'

        try:
            arcpy.da.NumPyArrayToTable(array, tmp_table)
            del array
        except arcpy.ExecuteError:
            import sys
            # Geoprocessor threw an error
            #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
            msg = arcpy.GetMessages(2).replace('\n', '\n\t')
            msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
            if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
            else: print(msg); del msg, sys

        msg = f'>-> Copying the masterspeciestnformation Table from memory to the GDB'
        logFile(log_file, msg); del msg

        masterspeciestnformation_table = os.path.join(ProjectGDB, masterspeciestnformation)

        # Template MasterSpeciesInformation Table
        template = "_Template_MasterSpeciesInformation"
        template_path = os.path.join(ProjectGDB, template)

        CreateTemplateTable = True
        if CreateTemplateTable:
            createTemplateTables({k: v for k, v in template_table_dictionary.items() if template in k})
        del CreateTemplateTable, template

        # Execute CreateTable
        arcpy.management.CreateTable(ProjectGDB, masterspeciestnformation, template_path, "", "")

        del ProjectGDB, template_path

        arcpy.CopyRows_management(tmp_table, masterspeciestnformation_table, "")

        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        msg = f'>-> Updating the field aliases for the {os.path.basename(masterspeciestnformation_table)} Table'
        logFile(log_file, msg); del msg

        # Field Alias Dictionary
        field_alias = {
                       'Species'           : 'Species',
                       'CommonName'        : 'Common Name',
                       'SpeciesCommonName' : 'Species (Common Name)',
                       'CommonNameSpecies' : 'Common Name (Species)',
                       'TaxonomicGroup'    : 'Taxonomic Group',
                      }

        # Alter Field Alias
        alterFieldAlias(masterspeciestnformation_table, field_alias, log_file)
        #
        del field_alias

        msg = f'>-> Adding metadata to the {masterspeciestnformation} Table'
        logFile(log_file, msg); del msg

        # Add Metadata
        addMetadata(masterspeciestnformation_table, log_file)

        # Cleanup
        del masterspeciestnformation, masterspeciestnformation_table

        del pd, np, warnings

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def createRegionSpeciesYearImageName(args):
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        # Set a start time so that we can see how log things take
        start_time = time()

        CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Generate Datasets
        args = [CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder]
        datasets = generateDatasets(args); del args, log_file_folder

        # ###--->>> Create Template Tables Start
        # Template RegionSpeciesYearImageName Table
        template = "_Template_RegionSpeciesYearImageName"

        CreateTemplateTable = True
        if CreateTemplateTable:
            createTemplateTables({k: v for k, v in template_table_dictionary.items() if template in k})
        del CreateTemplateTable, template

        # ###--->>> Create Template Tables End

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB; del ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Region Species Year Image Name Table
        regionspeciesyearimagename = "RegionSpeciesYearImageName"

        msg = f"Creatnig the RegionSpeciesYearImageName Table"
        logFile(log_file, msg); del msg

        arcpy.management.CreateTable(ProjectGDB, regionspeciesyearimagename, "_Template_RegionSpeciesYearImageName")

        # Get datasets that have a table
        datasets = [[r for r in group] for group in datasets if group[4] in arcpy.ListTables("*")]

        # Start looping over the datasets array as we go region by region.
        for i in range(len(datasets)):
            layercode = datasets[i][4]
            del i

# #            oaregioncode            = datasets[i][0]
# #            oaregion                = datasets[i][1]
# #            dismapregioncode        = datasets[i][2]
# #            dismapseasoncode        = datasets[i][3]
# #            layercode               = datasets[i][4]
# #            layername               = datasets[i][5]
# #            datecode                = datasets[i][6]
# #            distributionprojectname = datasets[i][7]
# #            distributionprojectcode = datasets[i][8]
# #            region                  = datasets[i][9]
# #            seasoncode              = datasets[i][10]
# #            summaryproduct          = datasets[i][11]
# #            csvfile                 = datasets[i][12]
# #            geographicarea          = datasets[i][13]
# #            coordinatesystem        = datasets[i][14]
# #            cellsize                = datasets[i][15]
# #            transformunit           = datasets[i][16]
# #            timezone                = datasets[i][17]

            layercode_start_time = time()

            # Write a message to the log file
            msg = f"STARTING REGION {layercode} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
            logFile(log_file, msg); del msg

            # Get a record count to see if data is present
            # num = 12345
            # print(f"{num:,d}") >>> 12,345
            # print('{:,.2f}'.format(num)) >>> 12,345.00
            getcount = int(arcpy.management.GetCount(layercode)[0])
            msg = f'\t> {layercode} has {getcount:,d} records'
            logFile(log_file, msg); del msg, getcount

            # Execute Statistics to get unique set of records
            layercode_tmp = layercode+"_tmp"
            statsFields = [["Species", "COUNT"]]

            fields = [f.name for f in arcpy.ListFields(layercode)]

            if "CoreSpecies" in fields:
                caseFields = ["LayerCode", "Region", "Species", "CommonName", "SpeciesCommonName", "CommonNameSpecies", "CoreSpecies", "Year", "StdTime"]
            if "CoreSpecies" not in fields:
                caseFields = ["LayerCode", "Region", "Species", "CommonName", "SpeciesCommonName", "CommonNameSpecies", "Year", "StdTime"]
            del fields

            msg = f"\t> Statistics Analysis of {layercode} Table"
            logFile(log_file, msg); del msg

            stat_tb = arcpy.analysis.Statistics(layercode, layercode_tmp, statsFields, caseFields)
            del statsFields, caseFields

            # Get a record count to see if data is present; we don't want to add data
            getcount = int(arcpy.management.GetCount(stat_tb)[0])
            msg = f'\t\t> {layercode_tmp} has {getcount:,d} records'
            logFile(log_file, msg); del msg, getcount

            msg = f'\t\t> Add Variable, Dimensions, and ImageName Fields to {layercode_tmp} {regionspeciesyearimagename} table'
            logFile(log_file, msg); del msg

            arcpy.management.AddFields(layercode_tmp,
                                       [["Variable", "TEXT", "Variable", "50", "", ""], ["Dimensions", "TEXT", "Dimensions", "10", "", ""], ["ImageName", "TEXT", "Image Name", "100", "", ""]]
                                       )

            msg = f'\t\t> Calculate Variable Field to {layercode_tmp} {regionspeciesyearimagename} table'
            logFile(log_file, msg); del msg

            arcpy.management.CalculateField(in_table=layercode_tmp, field="Variable", expression='!Species!', expression_type="PYTHON", code_block="")

            msg = f'\t\t> Calculate Dimensions Field to {layercode_tmp} {regionspeciesyearimagename} table'
            logFile(log_file, msg); del msg

            arcpy.management.CalculateField(in_table=layercode_tmp, field="Dimensions", expression="'StdTime'", expression_type="PYTHON", code_block="")

            msg = f'\t\t> Calculate ImageName Field to {layercode_tmp} {regionspeciesyearimagename} table'
            logFile(log_file, msg); del msg

            # The following calculates the time stamp for the Dataset
            # Use Update Cursor instead of Calculate Field
            with arcpy.da.UpdateCursor(layercode_tmp, ["ImageName", "Species", "Year"]) as cursor:
                for row in cursor:
                    row[0] = "{0}_{1}_{2}".format(layercode, row[1].replace("(","").replace(")",""), str(row[2]))
                    cursor.updateRow(row)
                    del row
            del cursor

            msg = f'\t\t> Append {layercode_tmp} to {regionspeciesyearimagename} table'
            logFile(log_file, msg); del msg

            #
            arcpy.management.Append(inputs = layercode_tmp, target = regionspeciesyearimagename, schema_type="NO_TEST", field_mapping="", subtype="")
            #msg = arcpy.GetMessages().replace('\n', '\n\t\t ')
            #logFile(log_file, msg); del msg

            # Remove temporary table
            arcpy.management.Delete(stat_tb)
            #msg = arcpy.GetMessages().replace('\n', '\n\t\t ')
            #logFile(log_file, msg); del msg

            del layercode_tmp, stat_tb

            #Final benchmark for the region.
            msg = f"ENDING REGION {layercode} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
            logFile(log_file, msg); del msg

            # Elapsed time
            end_time = time()
            elapse_time =  end_time - layercode_start_time
            msg = f"Elapsed Time for {layercode}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)\n"
            logFile(log_file, msg); del msg, end_time, elapse_time, layercode_start_time

            del layercode

        del datasets, ProjectGDB

        # Field Alias Dictionary
        field_alias = {
                       'LayerCode'         : 'Layer Code',
                       'Region'            : 'Region',
                       'FilterRegion'      : 'Filter Region',
                       'FilterSubRegion'   : 'Filter Sub-Region',
                       'Species'           : 'Species',
                       'CommonName'        : 'Common Name',
                       'SpeciesCommonName' : 'Species (Common Name)',
                       'CommonNameSpecies' : 'Common Name (Species)',
                       'TaxonomicGroup'    : 'Taxonomic Group',
                       'ManagementBody'    : 'Management Body',
                       'ManagementPlan'    : 'Management Plan',
                       'CoreSpecies'       : 'Core Species',
                       'Year'              : 'Year',
                       'StdTime'           : 'StdTime',
                       'Variable'          : 'Variable',
                       'Dimensions'        : 'Dimensions',
                       'ImageName'         : 'Image Name',
                      }

        # Alter Field Alias
        alterFieldAlias(regionspeciesyearimagename, field_alias, log_file)
        #
        del field_alias

        # Add Metadata
        addMetadata(regionspeciesyearimagename, log_file)

        CalculateSummaryTables = True
        if CalculateSummaryTables:
            #
            msg = f'\t> Statistics Analysis: {regionspeciesyearimagename} table for Master Species Information'
            logFile(log_file, msg); del msg

            arcpy.analysis.Statistics(in_table=regionspeciesyearimagename, out_table="_MasterSpeciesInformation", statistics_fields="Species COUNT", case_field="Species;CommonName;SpeciesCommonName;CommonNameSpecies;TaxonomicGroup;ManagementBody;ManagementPlan")

            arcpy.management.DeleteField(in_table="_MasterSpeciesInformation", drop_field="FREQUENCY;COUNT_Species")

            msg = f'\t\t> Table to Table to create _MasterSpeciesInformation{SoftwareEnvironmentLevel}.csv Table'
            logFile(log_file, msg); del msg
            # Create CSV file
            arcpy.conversion.TableToTable(in_rows="_MasterSpeciesInformation", out_path=CSV_DIRECTORY, out_name=f"_MasterSpeciesInformation{SoftwareEnvironmentLevel}.csv", where_clause="", field_mapping='', config_keyword="")
            ReplaceTable = False
            if ReplaceTable:
                arcpy.conversion.TableToTable(in_rows="_MasterSpeciesInformation", out_path=CSV_DIRECTORY, out_name=f"MasterSpeciesInformation.csv", where_clause="", field_mapping='', config_keyword="")
            del ReplaceTable
            #
            msg = f'\t> Statistics Analysis: {regionspeciesyearimagename} table for Species Filter'
            logFile(log_file, msg); del msg

            arcpy.analysis.Statistics(in_table=regionspeciesyearimagename, out_table="_SpeciesFilter", statistics_fields="Species COUNT", case_field="Species;CommonName;SpeciesCommonName;TaxonomicGroup;FilterRegion;FilterSubRegion")

            arcpy.management.DeleteField(in_table="_SpeciesFilter", drop_field="FREQUENCY;COUNT_Species")

            msg = f'\t\t> Table to Table to create _SpeciesFilter{SoftwareEnvironmentLevel}.csv Table'
            logFile(log_file, msg); del msg
            # Create CSV file
            arcpy.conversion.TableToTable(in_rows="_SpeciesFilter", out_path=CSV_DIRECTORY, out_name=f"_SpeciesFilter{SoftwareEnvironmentLevel}.csv", where_clause="", field_mapping='', config_keyword="")
            ReplaceTable = False
            if ReplaceTable:
                arcpy.conversion.TableToTable(in_rows="_SpeciesFilter", out_path=CSV_DIRECTORY, out_name=f"SpeciesFilter.csv", where_clause="", field_mapping='', config_keyword="")
            del ReplaceTable

            #
            msg = f'\t> Statistics Analysis: {regionspeciesyearimagename} table for Core Species'
            logFile(log_file, msg); del msg

            arcpy.analysis.Statistics(in_table=regionspeciesyearimagename, out_table="_CoreSpecies", statistics_fields="Species COUNT", case_field="LayerCode;Region;Species;CoreSpecies")

            arcpy.management.DeleteField(in_table="_CoreSpecies", drop_field="FREQUENCY;COUNT_Species")

            msg = f'\t\t> Table to Table to create _Species{SoftwareEnvironmentLevel}.csv Table'
            logFile(log_file, msg); del msg
            # Create CSV file
            arcpy.conversion.TableToTable(in_rows="_CoreSpecies", out_path=CSV_DIRECTORY, out_name=f"_CoreSpecies{SoftwareEnvironmentLevel}.csv", where_clause="", field_mapping='', config_keyword="")

        del CalculateSummaryTables

        del regionspeciesyearimagename, CSV_DIRECTORY

        #Final benchmark for the function.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, end_time, elapse_time, start_time


    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def createSpeciesFilterTable(args):
    """Create Species Filter Table"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        import pandas as pd
        import numpy as np
        import warnings

        start_time = time()

        CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr, log_file_folder

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB; del ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        speciesfiltertable = "SpeciesFilter"
        speciesfiltertable_csv_table = os.path.join(CSV_DIRECTORY, f"{speciesfiltertable}.csv")
        del CSV_DIRECTORY

        #
        msg = f'> Generating {speciesfiltertable} CSV Table: {os.path.basename(speciesfiltertable_csv_table)}'
        logFile(log_file, msg); del msg

        # https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/09_timeseries.html?highlight=datetime
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        #df = pd.read_csv('my_file.tsv', sep='\t', header=0)  ## not setting the index_col
        #df.set_index(['0'], inplace=True)

        # C:\. . .\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\lib\site-packages\numpy\lib\arraysetops.py:583:
        # FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
        # mask |= (ar1 == a)
        # A fix: https://www.youtube.com/watch?v=TTeElATMpoI
        # TLDR: pandas are Jedi; numpy are the hutts; and python is the galatic empire
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            # DataFrame
            df = pd.read_csv(speciesfiltertable_csv_table,
                             index_col = 0,
                             encoding="utf-8",
                             #encoding = "ISO-8859-1",
                             #engine='python',
                             delimiter = ',',
                             #dtype = None,
                             dtype = {
                                      "Species"         : str,
                                      "CommonName"      : str,
                                      "FilterRegion"    : str,
                                      "FilterSubRegion" : str,
                                      "TaxonomicGroup"  : str,
                                      "ManagementBody"  : str,
                                      "ManagementPlan"  : str,
                                      },
                             )
        del speciesfiltertable_csv_table

        msg = f'>-> Defining the column names.'
        logFile(log_file, msg); del msg

        # The original column names from the CSV files are not very
        # reader friendly, so we are making some changes here
        #df.columns = [u'Region', u'HUALID', u'Year', u'Species', u'WTCPUE', u'CommonName', u'Stratum', u'StratumArea', u'Latitude', u'Longitude', u'Depth']
        df.columns = ["Species", "CommonName", "FilterRegion", "FilterSubRegion", "TaxonomicGroup", "ManagementBody", "ManagementPlan"]

        # Replace NaN with an empty string. When pandas reads a cell
        # with missing data, it asigns that cell with a Null or nan
        # value. So, we are changing that value to an empty string of ''.

        df.fillna('', inplace=True)

        msg = f'>-> Creating the {speciesfiltertable} Geodatabase Table'
        logFile(log_file, msg); del msg

        # ###--->>> Numpy Datatypes
        # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm

        #print('DataFrame\n----------\n', df.head(10))
        #print('\nDataFrame datatypes :\n', df.dtypes)
        #columns = [str(c) for c in df.dtypes.index.tolist()]
        column_names = list(df.columns)
        #print(column_names)
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        column_formats = ['S50', 'U50', 'S40', 'S40', 'S50', 'S50', 'S50',]
        # # "Species" 50
        # # "CommonName" 50
        # # "FilterRegion" 40
        # # "FilterSubRegion" 40
        # # "TaxonomicGroup" 50
        # # "ManagementBody" 50
        # # "ManagementPlan" 50

        dtypes = list(zip(column_names, column_formats))
        del column_names, column_formats

        #print(df)
        try:
            array = np.array(np.rec.fromrecords(df.values), dtype = dtypes)
        except Exception as e:
            import sys
            # Capture all other errors
            #print(sys.exc_info()[2].tb_lineno)
            msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
            if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
            else: print(msg); del msg, sys

        del df, dtypes

        # Temporary table
        tmp_table = f'memory\{speciesfiltertable.lower()}_tmp'

        try:
            arcpy.da.NumPyArrayToTable(array, tmp_table)
            del array
        except arcpy.ExecuteError:
            import sys
            # Geoprocessor threw an error
            #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
            msg = arcpy.GetMessages(2).replace('\n', '\n\t')
            msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
            if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
            else: print(msg); del msg, sys

        msg = f'>-> Copying the {speciesfiltertable} Table from memory to the GDB'
        logFile(log_file, msg); del msg

        speciesfiltertable_table = os.path.join(ProjectGDB, speciesfiltertable)

        # Template MasterSpeciesInformation Table
        template = "_Template_SpeciesFilter"
        template_path = os.path.join(ProjectGDB, template)

        CreateTemplateTable = True
        if CreateTemplateTable:
            createTemplateTables({k: v for k, v in template_table_dictionary.items() if template in k})
        del CreateTemplateTable, template

        # Execute CreateTable
        arcpy.management.CreateTable(ProjectGDB, speciesfiltertable, template_path, "", "")

        del ProjectGDB, template_path

        arcpy.CopyRows_management(tmp_table, speciesfiltertable_table, "")

        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        msg = f'>-> Updating the field aliases for the {os.path.basename(speciesfiltertable_table)} Table'
        logFile(log_file, msg); del msg

        # Field Alias Dictionary
        field_alias = {
                       'Species'           : 'Species',
                       'CommonName'        : 'Common Name',
                       'FilterRegion'      : 'Species (Common Name)',
                       'FilterSubRegion'   : 'Species (Common Name)',
                       'TaxonomicGroup'    : 'Taxonomic Group',
                       'ManagementBody'    : 'Management Body',
                       'ManagementPlan'    : 'Management Plan',
                      }

        # Alter Field Alias
        alterFieldAlias(speciesfiltertable_table, field_alias, log_file)
        #
        del field_alias

        msg = f'>-> Adding metadata to the {speciesfiltertable} Table'
        logFile(log_file, msg); del msg

        # Add Metadata
        addMetadata(speciesfiltertable_table, log_file)

        # Cleanup
        del speciesfiltertable, speciesfiltertable_table

        del pd, np, warnings

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')

def createSpeciesRichnessRasters():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        arcpy.env.overwriteOutput = True

        arcpy.env.rasterStatistics = u'STATISTICS 1 1'
        arcpy.env.buildStatsAndRATForTempRaster = True

        # Clean Scatch workspace -- Start
        tmp_workspace = arcpy.env.workspace
        arcpy.env.workspace = ScratchGDB
        # This removes the saved rasters in the ScratchGDB
        for raster in arcpy.ListRasters("*"): arcpy.management.Delete(raster)
        arcpy.management.Compact(ScratchGDB)
        #del raster
        arcpy.env.workspace = ScratchFolder
        # This removes the saved rasters in the ScratchGDB
        for raster in [r for r in arcpy.ListRasters("*")]: arcpy.management.Delete(raster)
        #del raster

        arcpy.env.workspace = tmp_workspace
        del tmp_workspace
        # Clean Scatch workspace -- End

##        # Set the workspace to the ProjectGDB
##        tmp_workspace = arcpy.env.workspace
##        arcpy.env.workspace = ProjectGDB
##
##        # Set the scratch workspace to the ScratchGDB
##        tmp_scratchWorkspace = arcpy.env.scratchWorkspace
##        arcpy.env.scratchWorkspace = ScratchGDB


        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            #layercode_shape = table_name[0]
            #layercode_boundary = table_name[1]
            layercode = table_name[2]
            region = table_name[3]
            csv_file = table_name[4]
            layercode_georef = table_name[5]
            #layercode_contours = table_name[6]
            cell_size = table_name[7]

            # Set the output coordinate system to what is available for us.
            layercode_sr = srs[layercode_georef]
            arcpy.env.outputCoordinateSystem = layercode_sr

            #layercode_shape = os.path.join(ProjectGDB, layercode+"_Shape")
            layercode_snap_raster = os.path.join(ProjectGDB, layercode+"_Snap_Raster")
            layercode_raster_mask = os.path.join(ProjectGDB, layercode+"_Raster_Mask")

            arcpy.env.snapRaster = layercode_snap_raster
            # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
            arcpy.env.extent = arcpy.Describe(layercode_snap_raster).extent
            arcpy.env.mask = layercode_raster_mask

            # These are used later to set the rows and columns for a zero numpy array
            rowCount = int(arcpy.management.GetRasterProperties(layercode_snap_raster, "ROWCOUNT" ).getOutput(0))
            columnCount = int(arcpy.management.GetRasterProperties(layercode_snap_raster, "COLUMNCOUNT" ).getOutput(0))

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")
            # Start with removing the log file if it exists
            #if os.path.isfile(log_file):
            #    os.remove(log_file)

            # Write a message to the log file
            msg = "#-> STARTING {0} ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)
            del msg

            msg = ">-> Region (abb): {0}\n\t Region:  {1}".format(layercode, region)
            logFile(log_file, msg)

            layercode_year_richness_path = os.path.join(ANALYSIS_DIRECTORY, layercode)

            if ReplaceRegionYearRichness:
                tmp_workspace = arcpy.env.workspace
                arcpy.env.workspace = layercode_year_richness_path
                rs = arcpy.ListRasters("*Richness*")
                for r in rs: arcpy.management.Delete(r); del r
                del rs
                arcpy.env.workspace = tmp_workspace
                del tmp_workspace

            # Region richness raster
            # Set layercode_year_richness_path
            layercode_year_richness_path = os.path.join(ANALYSIS_DIRECTORY, layercode, "Species Richness")

            if not os.path.isdir(layercode_year_richness_path):
                os.makedirs(layercode_year_richness_path)

            if ReplaceRegionYearRichness:
                tmp_workspace = arcpy.env.workspace
                arcpy.env.workspace = layercode_year_richness_path
                rs = arcpy.ListRasters("*Richness*")
                for r in rs: arcpy.management.Delete(r); del r
                del rs
                arcpy.env.workspace = tmp_workspace
                del tmp_workspace

            # Define layercode_mosaic
            layercode_mosaic = os.path.join(ProjectGDB, layercode)
            # Make layercode_mosaic_layer
            layercode_mosaic_layer = arcpy.management.MakeMosaicLayer(layercode_mosaic, "layercode_mosaic_layer")

            # Get a unique list of years from the layercode_mosaic_layer
            years = unique_years(layercode_mosaic_layer)
            #years = unique_years(layercode_mosaic)

            if arcpy.Exists("layercode_mosaic_layer"): arcpy.management.Delete("layercode_mosaic_layer")
            del layercode_mosaic_layer

            # Test if we are filtering on years. If so, a new year list is
            # created with the selected years remaining in the list
            #if FilterYears:
            #    # Get a shorter list
            #    years = [y for y in years if y in selected_years]
            #else:
            #    pass

            for year in years:

                layercode_year_base_name = "{0}_{1}_".format(layercode, year)

                layercode_year_richness = os.path.join(layercode_year_richness_path, "{0}Species_Richness.tif".format(layercode_year_base_name))

                if not os.path.isfile(layercode_year_richness) or ReplaceRegionYearRichness:

                    msg = ">->-> Year: {0}".format(year)
                    logFile(log_file, msg)

                    # Set workspace
                    arcpy.env.workspace = ScratchFolder

                    msg = ">->->-> arcpy.management.ExportMosaicDatasetItems"
                    logFile(log_file, msg)

                    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
                    # The following inputs are layers or table views: "layercode_mosaic_layer"

                    arcpy.management.ExportMosaicDatasetItems(#in_mosaic_dataset = "layercode_mosaic_layer",
                                                              in_mosaic_dataset = layercode_mosaic,
                                                              out_folder = ScratchFolder,
                                                              out_base_name = layercode_year_base_name,
                                                              where_clause = "Year = {0} AND Variable NOT IN ('Species Richness', 'Core Species Richness')".format(year),
                                                              format = "TIFF",
                                                              nodata_value = "-3.40282346639e+38", #-3.402823e+38
                                                              clip_type = "NONE",
                                                              template_dataset = "DEFAULT",
                                                              cell_size = "{0} {0}".format(cell_size))

                    msg = arcpy.GetMessages()
                    msg = ">->->-> {0}\n".format(msg.replace('\n', '\n>->->-> '))
                    logFile(log_file, msg)

                    # Get a list of rasters that are exported from the arcpy.management.ExportMosaicDatasetItems tool
                    # These, for some reason, have TIF as an extension
                    rasters = [r for r in arcpy.ListRasters("{0}*.TIF".format(layercode_year_base_name)) if "Richness" not in r]
                    for raster in rasters: arcpy.management.CalculateStatistics(raster)
                    del raster
                    #print(rasters)

                    #richnessArray = np.zeros((rowCount, columnCount), dtype=int, order='C')
                    #richnessArray = np.zeros((rowCount, columnCount), dtype=float, order='C')
                    #richnessArray = np.zeros((rowCount, columnCount), dtype=np.int32, order='C')
                    richnessArray = np.zeros((rowCount, columnCount), dtype='float32', order='C')

                    msg = ">->->-> Processing rasters"
                    logFile(log_file, msg)
                    # For each raster exported, create the Con mask
                    for raster in rasters:
                        #arcpy.management.CalculateStatistics(raster)
                        msg = ">->->->-> Processing {0} raster".format(raster)
                        logFile(log_file, msg)

                        # Get Raster Maximum to test of zero rasters
                        #rasterMaximum = float(arcpy.management.GetRasterProperties(raster,"MAXIMUM").getOutput(0))

                        # If Raster Maximum greater than zero, then proceed
                        #if rasterMaximum > 0.0:

                        rasterArray = arcpy.RasterToNumPyArray(raster, nodata_to_value=np.nan)
                        #rasterArray = rasterArray.astype('float32')
                        rasterArray[rasterArray < 0.0] = np.nan

    ##                    maximumRasterArray = np.nanmax(rasterArray)
    ##                    minimumRasterArray = np.nanmin(rasterArray)
    ##
    ##                    msg = ">->->->-> Maximum Biomass Array:         {0}".format(maximumRasterArray)
    ##                    print(msg)
    ##                    del msg
    ##
    ##                    msg = ">->->->-> Minimum Biomass Array:         {0}".format(minimumRasterArray)
    ##                    print(msg)
    ##                    del msg

                        rasterArray[rasterArray > 0.0] = 1.0

    ##                    maximumRasterArray = np.nanmax(rasterArray)
    ##                    minimumRasterArray = np.nanmin(rasterArray)
    ##
    ##                    msg = ">->->->-> Maximum Biomass Array:         {0}".format(maximumRasterArray)
    ##                    print(msg)
    ##                    del msg
    ##
    ##                    msg = ">->->->-> Minimum Biomass Array:         {0}".format(minimumRasterArray)
    ##                    print(msg)
    ##                    del msg

                        #add rasterArray to richnessArray
                        richnessArray = np.add(richnessArray, rasterArray)
                        # Can also use: richnessArray + rasterArray
                        del rasterArray
                    # cleanup
                    # del rasterMaximum

                    #richnessArray[richnessArray <= 0] = np.nan

                    msg = ">->->-> Creating Richness Raster"
                    logFile(log_file, msg)

                    # Create Raster from Array
                    snapRaster = arcpy.Raster(layercode_snap_raster)
                    lowerLeft = arcpy.Point(snapRaster.extent.XMin, snapRaster.extent.YMin)
                    del snapRaster

                    # Cast array as float32
                    richnessArray = richnessArray.astype('float32')

                    # Convert Array to Raster
                    richnessArrayRaster = arcpy.NumPyArrayToRaster(richnessArray, lowerLeft, cell_size, cell_size, -3.40282346639e+38) #-3.40282346639e+38
                    richnessArrayRaster.save(layercode_year_richness)
                    del richnessArray, richnessArrayRaster, lowerLeft
                    del rasters

                    arcpy.management.CalculateStatistics(layercode_year_richness)

                    # Add metadata
                    layercode_year_richness_md = md.Metadata(layercode_year_richness)
                    layercode_year_richness_md.synchronize('ACCESSED', 1)
                    layercode_year_richness_md.title = "{0} {1}".format(region.replace('-',' to '), DateCode)
                    layercode_year_richness_md.tags = "{0}, {1}, Species Richness".format(geographic_regions[layercode], year)
                    layercode_year_richness_md.save()
                    del layercode_year_richness_md

                    # ###--->>>

                    tmp_workspace = arcpy.env.workspace
                    arcpy.env.workspace = ScratchFolder
                    msg = ">->->-> arcpy.management.Delete in ScratchFolder"
                    logFile(log_file, msg)
                    # This removes the saved rasters in the ScratchFolder
                    #for raster in [r for r in arcpy.ListRasters("*") if "Richness" not in r]: arcpy.management.Delete(raster)
                    for raster in arcpy.ListRasters("*"): arcpy.management.Delete(raster)
                    del raster
                    arcpy.env.workspace = tmp_workspace
                    del tmp_workspace

            # ###--->>>

            # Loading images into the Mosaic.
            msg = '>->->-> Loading the {} Mosaic. This may take a while... Please wait...'.format(region)
            logFile(log_file, msg)

            arcpy.management.AddRastersToMosaicDataset(in_mosaic_dataset = layercode_mosaic,
                                                       raster_type = "Raster Dataset",
                                                       input_path = layercode_year_richness_path,
                                                       update_cellsize_ranges = "UPDATE_CELL_SIZES",
                                                       #update_cellsize_ranges = "NO_CELL_SIZES",
                                                       update_boundary = "UPDATE_BOUNDARY",
                                                       #update_boundary = "NO_BOUNDARY",
                                                       update_overviews = "NO_OVERVIEWS",
                                                       maximum_pyramid_levels = "",
                                                       maximum_cell_size = "0",
                                                       minimum_dimension = "1500",
                                                       spatial_reference = layercode_sr,
                                                       #filter = "*Richness.tif",
                                                       filter = "*Richness.tif",
                                                       sub_folder = "NO_SUBFOLDERS",
                                                       #duplicate_items_action = "OVERWRITE_DUPLICATES",
                                                       duplicate_items_action = "EXCLUDE_DUPLICATES",
                                                       build_pyramids = "NO_PYRAMIDS",
                                                       calculate_statistics = "CALCULATE_STATISTICS",
                                                       #calculate_statistics = "NO_STATISTICS",
                                                       build_thumbnails = "BUILD_THUMBNAILS",
                                                       #build_thumbnails = "NO_THUMBNAILS",
                                                       operation_description = "",
                                                       #force_spatial_reference = "NO_FORCE_SPATIAL_REFERENCE",
                                                       force_spatial_reference = "FORCE_SPATIAL_REFERENCE",
                                                       estimate_statistics = "ESTIMATE_STATISTICS",
                                                       #estimate_statistics = "NO_STATISTICS",
                                                       )

            del layercode_year_richness, layercode_year_richness_path

            msg = ">->->-> Calculating new values for the new fields in the regional Mosaic Dataset"
            logFile(log_file, msg)

            msg = ">->->-> arcpy.management.MakeTableView Variable_View"
            logFile(log_file, msg)
            # For Multidimensional data (https://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/wkfl-create-a-multidimensional-mosaic-dataset-from-a-set-of-time-series-images.htm)
            # Make table view for calculations
            #arcpy.management.MakeTableView(in_table=layercode_richness_mosaic, out_view="Variable_View", where_clause="Variable IS NULL", workspace="", )
            arcpy.management.MakeTableView(in_table=layercode_mosaic, out_view="Variable_View", where_clause="Variable IS NULL OR Variable = 'Species Richness'", workspace="", )

            msg = ">->->-> arcpy.management.CalculateField Region"
            logFile(log_file, msg)
            # Process: Calculate Region Field
            arcpy.management.CalculateField("Variable_View", "OARegion", "'{0}'".format(region.replace("'","''")), "PYTHON", "")

            msg = ">->->-> arcpy.management.CalculateField CoreSpecies"
            logFile(log_file, msg)
            # Process: Calculate Region Field
            arcpy.management.CalculateField("Variable_View", "CoreSpecies", "'No'", "PYTHON", "")

            msg = ">->->-> arcpy.management.CalculateField Year"
            logFile(log_file, msg)
            # Process: Calculate Year Field
            arcpy.management.CalculateField("Variable_View", "Year", expression="MakeInt( !Name!)", expression_type="PYTHON", code_block="def MakeInt(name):   return int(name[-21:-17]) if 'Core' not in name else int(name[-26:-22])")

            msg = ">->->-> arcpy.management.CalculateField Variable"
            logFile(log_file, msg)
            # Process: Calculate Species Field
            arcpy.management.CalculateField("Variable_View", "Variable", "'Species Richness'", "PYTHON", "")

            codeBlock = """def getDate(region, year):
                              from datetime import datetime
                              import pytz
                              regionDateDict = {# Region : Month, Day, Time Zone
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

            msg = ">->->-> arcpy.management.CalculateField StdTime"
            logFile(log_file, msg)

            arcpy.management.CalculateField("Variable_View", "StdTime", expression="getDate( !OARegion!, !Year! )", expression_type="PYTHON", code_block=codeBlock)
            del codeBlock

            msg = ">->->-> arcpy.management.CalculateField Dimensions"
            logFile(log_file, msg); del msg

            arcpy.management.CalculateField(in_table="Variable_View", field="Dimensions", expression="'StdTime'", expression_type="PYTHON", code_block="")

            arcpy.management.Delete("Variable_View")

            # Cleanup
            del layercode_mosaic, layercode
            del layercode_georef, year, years
            del table_name, csv_file, layercode_year_base_name
            del region, layercode_sr
            del rowCount, columnCount
            del layercode_snap_raster, layercode_raster_mask, cell_size

        # Cleanup
        del log_file

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"#-> Elapsed Time for {0} {1} (H:M:S)\n".format(function, strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys



##def createSampleLocationPoints():
##    try: # The code with the exception that you want to catch. If an exception
##         # is raised, control flow leaves this block immediately and goes to
##         # the except block
##
##        # Uses the inspect module and a lamda to find name of this function
##        function = function_name()
##        # arcpy.AddMessage(function)
##
##        # Set a start time so that we can see how log things take
##        start_time = time()
##
##        # For benchmarking.
##        #timestr = strftime("%Y%m%d-%H%M%S")
##        timestr = strftime('%a %b %d %I %M %S %p', localtime())
##        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
##        del timestr
##
##        # Write a message to the log file
##        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##        # Set the workspace to the workspace
##        arcpy.env.workspace = ProjectGDB
##
##        # Set the scratch workspace to the ScratchGDB
##        arcpy.env.scratchWorkspace = ScratchGDB
##
##        # Set the overwriteOutput to True
##        arcpy.env.overwriteOutput = True
##
##        # Use all of the cores on the machine.
##        arcpy.env.parallelProcessingFactor = "100%"
##
##        # Set Log Metadata to False in order to not record all geoprocessing
##        # steps in metadata
##        arcpy.SetLogMetadata(False)
##
##        # Start looping over the datasets array as we go region by region.
##        for dataset in datasets:
##            # Assigning variables from items in the chosen table list
##            layercode = dataset[0]
##            region = dataset[1]
##            layercode_csv_table = dataset[2]
##            #layercode_shape = dataset[3]
##            #layercode_boundary = dataset[4]
##            layercode_georef = dataset[5]
##            #layercode_contours = dataset[6]
##            #cellsize = dataset[7]
##            del dataset
##
##            # Make Geodatabase friendly name
##            #layercode_name = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "")
##            #layercode_name = arcpy.ValidateTableName(region)
##
##            layercode_start_time = time()
##
##            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")
##
##            RegionGDB = os.path.join(BASE_DIRECTORY, f"{layercode} {SoftwareEnvironmentLevel}.gdb")
##
##            if not os.path.exists(RegionScratchGDB):
##                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch")
##
##            if not os.path.exists(RegionGDB):
##                arcpy.management.CreateFileGDB(BASE_DIRECTORY, f"{layercode} {SoftwareEnvironmentLevel}")
##
##            # Set the workspace to the workspace
##            arcpy.env.workspace = RegionGDB
##
##            # Set the scratch workspace to the ScratchGDB
##            arcpy.env.scratchWorkspace = RegionScratchGDB
##
##            # Write a message to the log file
##            msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg
##
##            # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
##            msg = f'> Generating {layercode} Dataset'
##            logFile(log_file, msg); del msg
##
##            # Set the output coordinate system to a reference system used for
##            # the NOAA GP / Fisheries GP (Albers, UTM, etc.)
##            #layercode_sr = dataset_srs[layercode_georef]
##            layercode_sr = arcpy.SpatialReference(layercode_georef)
##
##            # Delete after last use
##            del layercode_georef
##
##            arcpy.env.outputCoordinateSystem = layercode_sr
##            arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
##            del layercode_sr
##
##            msg = f'>-> Creating the {layercode} Sample Locations Dataset'
##            logFile(log_file, msg); del msg
##
##            # Make XY Event  Layer
##            my_events = arcpy.management.MakeXYEventLayer(layercode_csv_table, "Longitude", "Latitude", "my_events", "#", "#")
##            del layercode_csv_table
##
##            # Make it a Dataset and output it to the local hard disk drive (for usage and debugging purposes)
##            arcpy.FeatureClassToFeatureClass_conversion(in_features = my_events,
##                                                        out_path = ProjectGDB,
##                                                        out_name = f"{layercode}_Sample_Locations",
##                                                        where_clause = "",
##                                                        field_mapping = "",
##                                                        config_keyword = "")
##
##            # Clear the XY Event Layer from memory.
##            arcpy.management.Delete(my_events)
##            del my_events
##
##            msg = f'>-> Adding field index in the {region} Dataset'
##            logFile(log_file, msg); del msg
##
##            # Input Dataset
##            layercode_sample_locations = os.path.join(RegionGDB, f"{layercode}_Sample_Locations")
##
##            # Add Attribute Index
##            arcpy.AddIndex_management(layercode_sample_locations, ['Species', 'CommonName', 'SpeciesCommonName', 'Year'], f"{layercode}_SampleLocationsSpeciesIndex", "NON_UNIQUE", "NON_ASCENDING")
##
##            result = arcpy.management.GetCount(layercode_sample_locations)
##            msg = f">-> '{layercode}_Sample_Locations' has {result[0]} records"
##            logFile(log_file, msg); del msg
##            del result
##
##            # Delete after last use
##            del layercode
##
##            # Add Metadata
##            addMetadata(layercode_sample_locations, log_file)
##
##            # Field Alias Dictionary
##            field_alias = {
##                           'Region' : 'Region',
##                           'SampleID' : 'Sample ID',
##                           'Species' : 'Species',
##                           'CommonName' : 'Common Name',
##                           'SpeciesCommonName' : 'Species (Common Name)',
##                           'CommonNameSpecies' : 'Common Name (Species)',
##                           'CoreSpecies' : 'Core Species',
##                           'Year' : 'Year',
##                           'WTCPUE' : 'WTCPUE',
##                           'WTCPUECubeRoot' : 'WTCPUE Cube Root',
##                           'Stratum' : '',
##                           'StratumArea' : 'Stratum Area',
##                           'Latitude' : 'Latitude',
##                           'Longitude' : 'Longitude',
##                           'Depth' : 'Depth',
##                           'StdTime' : 'StdTime',
##                          }
##
##            # Alter Field Alias
##            alterFieldAlias(layercode_sample_locations, field_alias, log_file)
##
##            #
##            del field_alias, layercode_sample_locations
##
##            msg = f"> Generating {layercode} Dataset completed ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg
##
##            #Final benchmark for the region.
##            msg = f"ENDING REGION {region} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##            logFile(log_file, msg); del msg
##
##            # Elapsed time
##            end_time = time()
##            elapse_time =  end_time - layercode_start_time
##            msg = f"Elapsed Time for {region}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)\n"
##            logFile(log_file, msg); del msg, end_time, elapse_time, layercode_start_time
##
##            del region
##
##        #Final benchmark for the function.
##        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Elapsed time
##        end_time = time()
##        elapse_time =  end_time - start_time
##        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
##        logFile(log_file, msg); del msg, end_time, elapse_time
##
##        del log_file, start_time
##
##    # This code is executed only if an exception was raised in the try block.
##    # Code executed in this block is just like normal code: if there is an
##    # exception, it will not be automatically caught (and probably stop the
##    # program).
##    except arcpy.ExecuteError:
##        # Geoprocessor threw an error
##        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
##        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
##        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
##        logFile(log_file.replace(".log", " ERROR.log"), msg); del msg
##    except Exception as e:
##        # Capture all other errors
##        #print(sys.exc_info()[2].tb_lineno)
##        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
##        logFile(log_file.replace(".log", " ERROR.log"), msg); del msg
##
##    # This code is executed only if no exceptions were raised in the try block.
##    # Code executed in this block is just like normal code: if there is an
##    # exception, it will not be automatically caught (and probably stop the
##    # program). Notice that if the else block is executed, then the except block
##    # is not, and vice versa. This block is optional.
##    else:
##        # Reset Environments to start fresh
##        arcpy.ResetEnvironments()
##
##    # This code always executes after the other blocks, even if there was an
##    # uncaught exception (that didn’t cause a crash, obviously) or a return
##    # statement in one of the other blocks. Code executed in this block is just
##    # like normal code: if there is an exception, it will not be automatically
##    # caught (and probably stop the program). This block is also optional.
##    finally:
##        # Get list of local keys that may need to be deleted.
##        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]
##
##        # If there is a list of local keys, print the list, and then delete
##        # variables
##        if localKeys:
##            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
##            logFile(log_file, msg); del msg
##        del localKeys, function

def createTableAndFieldReport(workspace, wildcard, datatype, type):
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
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
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
                        'CenterX', 'Name', 'CenterY', 'Raster',
                        'UriHash', 'MinPS', 'ServiceName', 'TypeID', 'OBJECTID',
                        'MaxPS', 'Uri', 'LowPS', 'Shape_Area', 'Thumbnail',
                        'ItemTS', 'GroupName', 'Category',] # 'ProductName',

        dataSets = []

        walk = arcpy.da.Walk(workspace, topdown=True, datatype=datatype, type=type)

        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                if wildcard.lower() in filename.lower():
                    #dataSets.append(os.path.join(dirpath, filename))
                    dataSets.append(filename)

        dataset_dictionary = {}
        FieldListReport = False
        #print(dataSets.sort())
        for dataSet in sorted(dataSets):
            # Describe dataset
            desc = arcpy.Describe(dataSet)
            # Print selected dataset and describe object properties
            msg = "Data Set: {0} Data Type: {1}".format(desc.name, desc.dataType)
            logFile(log_file, msg); del msg
            del desc

            # Get list of fields in the table
            # fields_list = lambda feature_class: [field.name for field in arcpy.ListFields(feature_class) if field.type != 'Geometry' and field.type != 'OID']
            #fields = arcpy.ListFields(dataSet)

            if FieldListReport:
                fieldlist = []
                fields = [f for f in arcpy.ListFields(dataSet) if not f.required]
                # Loop through fields
                for field in fields:
                    fieldlist.append([field.name, field.type.upper(), field.aliasName, field.length, '', '',])
                    del field
                dataset_dictionary[dataSet] = fieldlist

            DetailedFieldReport = True
            if DetailedFieldReport:
                fields = [f for f in arcpy.ListFields(dataSet) if not f.required]
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

                    state = "is a Esri Field" if field.name in arcGISfields else "is a DisMAP Field"

                    msg = f"{fieldName}"
                    msg = f"\t Field:       {fieldName} ({state})\n"
                    msg = msg + f"\t Alias:       {fieldAliasName}\n"
                    msg = msg + f"\t Type:        {fieldType}\n"
                    msg = msg + f"\t Length:      {fieldLength}\n"
                    msg = msg + f"\t Editable:    {fieldEditable}\n"
                    msg = msg + f"\t Required:    {fieldRequired}\n"
                    msg = msg + f"\t Scale:       {fieldScale}\n"
                    msg = msg + f"\t Precision:   {fieldPrecision}\n"
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
            del DetailedFieldReport

            del dataSet, fields

##template_table_dictionary = {"_Template_Datasets" : [["OARegionCode",     "TEXT",     "OA Region Code",     50,           "",            ""],
##                                                     ["OARegion",         "TEXT",     "OA Region",          50,           "",            ""],
##                                                     ["DisMapRegionCode", "TEXT",     "DisMAP Region Code", 50,           "",            ""],
##                                                     ["",     "TEXT",     "",      50,           "",            ""],
##
        if FieldListReport:
            for key in dataset_dictionary:
                print(f'{{"{key}" : [')
                for i in range(len(dataset_dictionary[key])):
                    print(f"\t{dataset_dictionary[key][i]}")
                #print(key, dataset_dictionary[key])

        del dataset_dictionary
        del FieldListReport

        del workspace, wildcard, fieldNames, arcGISfields, dataSets
        del walk, dirpath, dirnames, filenames, filename, datatype, type

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys


def createTemplateTables(template_table_dictionary):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

##        # Set a start time so that we can see how log things take
##        start_time = time()
##
##        # For benchmarking.
##        #timestr = strftime("%Y%m%d-%H%M%S")
##        timestr = strftime('%a %b %d %I %M %S %p', localtime())
##        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
##        del timestr
##
##        # Write a message to the log file
##        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg

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

        for tb in template_table_dictionary:
            msg = "###--->>> Creating Template: {0} <<<---###".format(tb)
            logFile(log_file, msg); del msg
            arcpy.management.CreateTable(ProjectGDB, tb)
            arcpy.management.AddFields(tb, template_table_dictionary[tb])

            # Add Metadata
            addMetadata(tb, log_file)
            del tb
        #
        del template_table_dictionary

        # Compact GDB
        #compactGDB(ProjectGDB, log_file)

##        #Final benchmark for the region.
##        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
##        logFile(log_file, msg); del msg
##
##        # Elapsed time
##        end_time = time()
##        elapse_time =  end_time - start_time
##        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
##        logFile(log_file, msg); del msg
##
##        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def generateDatasets(args):
    try:
        CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder = args

        dataset_table = os.path.join(ProjectGDB, "Datasets")

        CreateDatasetTable = False
        if CreateDatasetTable:
            createDatasetTable(args)

        del args, CreateDatasetTable

        fields = [f.name for f in arcpy.ListFields(dataset_table) if not f.required]

        datasets = []
        with arcpy.da.SearchCursor(dataset_table, fields) as cursor:
            for row in cursor:
                oaregioncode            = row[0]
                oaregion                = row[1]
                dismapregioncode        = row[2]
                dismapseasoncode        = row[3]
                layercode               = row[4]
                layername               = row[5]
                datecode                = row[6]
                distributionprojectname = row[7]
                distributionprojectcode = row[8]
                region                  = row[9]
                seasoncode              = row[10]
                summaryproduct          = row[11]
                csvfile                 = row[12]
                geographicarea          = row[13]
                coordinatesystem        = row[14]
                cellsize                = row[15]
                transformunit           = row[16]
                timezone                = row[17]

                datasets.append([oaregioncode, oaregion, dismapregioncode,
                                 dismapseasoncode, layercode, layername,
                                 datecode, distributionprojectname,
                                 distributionprojectcode, region, seasoncode,
                                 summaryproduct, csvfile, geographicarea,
                                 coordinatesystem, cellsize, transformunit,
                                 timezone]
                                )

                del oaregioncode, oaregion, dismapregioncode, dismapseasoncode
                del layercode, layername, datecode
                del distributionprojectname, distributionprojectcode, region
                del seasoncode, summaryproduct, csvfile, geographicarea
                del coordinatesystem, cellsize, transformunit, timezone

        # Test if True
        if FilterDatasets:
            # New datasets list of lists #-> https://stackoverflow.com/questions/21507319/python-list-comprehension-list-of-lists
            datasets = [[r for r in group] for group in datasets if group[4] in selected_datasets]

        return datasets

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

def generateMasterSpeciesInformation(args):
    try:
        CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder = args

        masterspeciesinformation_table = os.path.join(ProjectGDB, "MasterSpeciesInformation")

        CreateMasterSpeciesInformationTable = False
        if CreateMasterSpeciesInformationTable:
            createMasterSpeciesInformationTable(args)
        del CreateMasterSpeciesInformationTable, args

        fields = [f.name for f in arcpy.ListFields(masterspeciesinformation_table) if not f.required]

        masterspeciesinformation = []
        with arcpy.da.SearchCursor(masterspeciesinformation_table, fields) as cursor:
            for row in cursor:
                masterspeciesinformation.append([row[0],row[1],row[2],row[3],row[4]])
                del row
        del cursor, masterspeciesinformation_table, fields
        del CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder

        return masterspeciesinformation

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

def generateSpeciesFilter(args):
    try:
        CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder = args

        speciesfilter_table = os.path.join(ProjectGDB, "SpeciesFilter")

        CreateSpeciesFilterTable = False
        if CreateSpeciesFilterTable:
            createSpeciesFilterTable(args)
        del CreateSpeciesFilterTable, args

        fields = [f.name for f in arcpy.ListFields(speciesfilter_table) if not f.required]

        speciesfilter = []
        with arcpy.da.SearchCursor(speciesfilter_table, fields) as cursor:
            for row in cursor:
                speciesfilter.append([row[0],row[1],row[2],row[3],row[4],row[5],row[6]])
                del row
        del cursor, speciesfilter_table, fields
        del CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder

        return speciesfilter

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

def getDMSPointsForGebco():
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
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
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

        # Start looping over the datasets array as we go region by region.
        for dataset in datasets:
            # Assigning variables from items in the chosen table list
            layercode = dataset[0]
            region = dataset[1]
            del dataset

            # Region DMS Points
            layercode_dms_points = layercode+"_Points"

            fields = ['DMSLat', 'DMSLon',]

            import math
            # For each row, print the WELL_ID and WELL_TYPE fields, and
            # the feature's x,y coordinates
            with arcpy.da.SearchCursor(layercode_dms_points, fields) as cursor:
                ns = []; ew = []
                for row in cursor:
                    ns.append( round(int(row[0][:2]) + (float(row[0][3:5]) / 60 ), 3) )
                    ew.append( round(int(row[1][:3]) + (float(row[1][4:6]) / 60 ), 3) )
                    del row

                n = math.ceil(max(ns) * 5.0) / 5.0
                w = math.floor(max(ew) * 5.0) / 5.0
                e = math.ceil(min(ew) * 5.0)/5.0
                s = math.floor(min(ns) * 5.0)/5.0

                msg = f"\t\t# {region} ({layercode}) = N {n} W -{w} E -{e} S {s}"
                logFile(log_file, msg); del msg
                # gebco_2022_n35.4_s28.6_w-81.4_e-75.6.asc
                msg = f"\t\t#\t 'gebco_2022_n{n}_s{s}_w-{w}_e-{e}.asc'"
                logFile(log_file, msg); del msg

                del ns, ew, n, w, e, s

            del fields, cursor, math

            # Delete after last use
            del layercode_dms_points, layercode, region

         #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

def importEPU():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
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

        epu_shape_path = os.path.join(MAP_DIRECTORY, 'EPU_shape', 'EPU_NOESTUARIES')

        arcpy.management.CopyFeatures(epu_shape_path, 'EPU_NOESTUARIES')

        #arcpy.management.DeleteField('EPU_NOESTUARIES', )

        # Cleanup
        del epu_shape_path

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"#-> Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)\n"
        logFile(log_file, msg); del msg
        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

class LicenseError(Exception):
    pass

def listEnvironments():
    try:
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
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg

def listFolder(folder):
    try:
        # List folder contents
        filenames = os.listdir(folder)
        return True if filenames else False
        del filenames
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg

def logFile(log_file, msg):
    try:
        arcpy.AddMessage(msg)
        my_log = open(log_file, "a+")
        my_log.write(msg + '\n')
        my_log.close
        del my_log

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg

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

        # For example: 'http://www.arcgis.com/'
        arcpy.SignInToPortal("https://noaa.maps.arcgis.com/")

        print(f"Signed into Portal: {arcpy.GetActivePortalURL()}")

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

        # Table Field dictionary
        # geomTypes: "Polygon", "PolyLine", "Point", "Table"
        global template_table_dictionary
        template_table_dictionary = {"_Template_Datasets" : [
                                                             ['OARegionCode',            'TEXT',   'OA Region Code',            10, '', ''],
                                                             ['OARegion',                'TEXT',   'OA Region',                 50, '', ''],
                                                             ['DisMapRegionCode',        'TEXT',   'DisMAP Region Code',        40, '', ''],
                                                             ['DisMapSeasonCode',        'TEXT',   'DisMAP Season Code',        10, '', ''],
                                                             ['LayerCode',               'TEXT',   'Layer Code',                20, '', ''],
                                                             ['LayerName',               'TEXT',   'Layer Name',                40, '', ''],
                                                             ['DateCode',                'TEXT',   'DisMap Date Code',          10, '', ''],
                                                             ['DistributionProjectName', 'TEXT',   'Distribution Project Name', 60, '', ''],
                                                             ['DistributionProjectCode', 'TEXT',   'Distribution Project Code', 20, '', ''],
                                                             ['Region',                  'TEXT',   'Region',                    40, '', ''],
                                                             ['Season',                  'TEXT',   'Season',                    10, '', ''],
                                                             ['SummaryProduct',          'TEXT',   'Summary Product',            5, '', ''],
                                                             ['CSVFile',                 'TEXT',   'CSV File',                  20, '', ''],
                                                             ['GeographicArea',          'TEXT',   'Geographic Area',           20, '', ''],
                                                             ['CoordinateSystem',        'TEXT',   'Coordinate System',         30, '', ''],
                                                             ['CellSize',                'SHORT',  'Cell Size',                  4, '', ''],
                                                             ['TransformUnit',           'TEXT',   'Transform Unit',            30, '', ''],
                                                             ['TimeZone',                'TEXT',   'Time Zone',                 20, '', ''],
                                                            ],
                                     "_Template_DisMAP_Regions" : [
                                                                   ['OARegionCode', 'TEXT', 'OA Region Code', 10, '', ''],
                                                                   ['OARegion',     'TEXT', 'OA Region',      50, '', ''],
                                                                   ['LayerCode',    'TEXT', 'Layer Code',     20, '', ''],
                                                                   ['Region',       'TEXT', 'Region',         40, '', ''],
                                                                  ],
                                     "_Template_GLMME_Data" : [
                                                               ['LayerCode',         'TEXT',   'Layer Code',            20, '', ''],
                                                               ['Region',            'TEXT',   'Region',                40, '', ''],
                                                               ['Year',              'SHORT',  'Year',                   4, '', ''],
                                                               ['Easting',           'DOUBLE', 'Easting (UTM)',          8, '', ''],
                                                               ['Northing',          'DOUBLE', 'Northing (UTM)',         8, '', ''],
                                                               ['Latitude',          'DOUBLE', 'Latitude (DD)',          8, '', ''],
                                                               ['Longitude',         'DOUBLE', 'Longitude (DD)',         8, '', ''],
                                                               ['Depth',             'DOUBLE', 'Depth',                  8, '', ''],
                                                               ['MedianEstimate',    'DOUBLE', 'Median Estimate',        8, '', ''],
                                                               ['AnalysisValue',     'DOUBLE', 'Analysis Value',         8, '', ''],
                                                               ['TransformUnit',     'TEXT',   'Transform Unit',         10, '', ''],
                                                               ['MeanEstimate',      'DOUBLE', 'Mean Estimate',          8, '', ''],
                                                               ['Estimate5Percent',  'DOUBLE', 'Estimate 5 Percent',     8, '', ''],
                                                               ['Estimate95Percent', 'DOUBLE', 'Estimate 95 Percent',    8, '', ''],
                                                               ['Species',           'TEXT',   'Species',                50, '', ''],
                                                               ['CommonName',        'TEXT',   'Common Name',            50, '', ''],
                                                               ['SpeciesCommonName', 'TEXT',   'Species (Common Name)', 100, '', ''],
                                                               ['CommonNameSpecies', 'TEXT',   'Common Name (Species)', 100, '', ''],
                                                              ],
                                     "_Template_IDW_Data" : [
                                                             ['OARegionCode',      'TEXT',   'OA Region Code',         10, '', ''],
                                                             ['OARegion',          'TEXT',   'OA Region',              50, '', ''],
                                                             ['LayerCode',         'TEXT',   'Layer Code',             20, '', ''],
                                                             ['Region',            'TEXT',   'Region',                 40, '', ''],
                                                             ['SampleID',          'TEXT',   'Sample ID',              20, '', ''],
                                                             ['Year',              'SHORT',  'Year',                    4, '', ''],
                                                             ['Species',           'TEXT',   'Species',                50, '', ''],
                                                             ['WTCPUE',            'DOUBLE', 'WTCPUE',                  8, '', ''],
                                                             ['AnalysisValue',     'DOUBLE', 'Analysis Value',          8, '', ''],
                                                             ['TransformUnit',     'TEXT',   'Transform Unit',         10, '', ''],
                                                             ['CommonName',        'TEXT',   'Common Name',            50, '', ''],
                                                             ['SpeciesCommonName', 'TEXT',   'Species (Common Name)', 100, '', ''],
                                                             ['CommonNameSpecies', 'TEXT',   'Common Name (Species)', 100, '', ''],
                                                             ['CoreSpecies',       'TEXT',   'Core Species',            5, '', ''],
                                                             ['Stratum',           'TEXT',   'Stratum',                25, '', ''],
                                                             ['StratumArea',       'DOUBLE', 'Stratum Area',            8, '', ''],
                                                             ['Latitude',          'DOUBLE', 'Latitude (DD)',           8, '', ''],
                                                             ['Longitude',         'DOUBLE', 'Longitude (DD)',          8, '', ''],
                                                             ['Depth',             'DOUBLE', 'Depth',                   8, '', ''],
                                                             ['StdTime',           'DATE',   'StdTime',                 8, '', ''],
                                                            ],
                                     "_Template_Indicators" : [
                                                               ['OARegionCode',               'TEXT',   'OA Region Code',                             10, '', ''],
                                                               ['OARegion',                   'TEXT',   'OA Region',                                  50, '', ''],
                                                               ['DisMapRegionCode',           'TEXT',   'DisMAP Region Code',                         40, '', ''],
                                                               ['DisMapSeasonCode',           'TEXT',   'DisMAP Season Code',                         10, '', ''],
                                                               ['LayerCode',                  'TEXT',   'Layer Code',                                 20, '', ''],
                                                               ['Region',                     'TEXT',   'Model Region',                               40, '', ''],
                                                               ['Species',                    'TEXT',   'Species',                                    50, '', ''],
                                                               ['CommonName',                 'TEXT',   'Common Name',                                50, '', ''],
                                                               ['CoreSpecies',                'TEXT',   'Core Species',                                5, '', ''],
                                                               ['Year',                       'SHORT',  'Year',                                        4, '', ''],
                                                               # product name (only IDW Interpolation for now)
                                                               ['DistributionProjectName',    'TEXT',   'Distribution Project Name',                  50, '', ''],
                                                               # Note: DistributionProjectCode is a short code for
                                                               #       DistributionProjectName, for example,
                                                               #       DistributionProjectCode: IDW,
                                                               #       DistributionProjectName: NMFS/Rutgers IDW Interpolation
                                                               ['DistributionProjectCode',    'TEXT',   'Distribution Project Code',                   8, '', ''],
                                                               #  NOTE: SummaryProduct will be Yes if there is a regional
                                                               #        summary (e.g. species richness) or No if not
                                                               #        (some GLMME models may not have enough species to
                                                               #        warrant a species richness raster).
                                                               ['SummaryProduct',             'TEXT',   'Summary Product',                             5, '', ''],
                                                               ['CenterOfGravityLatitude',    'DOUBLE', 'Center of Gravity Latitude',                  8, '', ''],
                                                               ['MinimumLatitude',            'DOUBLE', 'Minimum Latitude',                            8, '', ''],
                                                               ['MaximumLatitude',            'DOUBLE', 'Maximum Latitude',                            8, '', ''],
                                                               ['OffsetLatitude',             'DOUBLE', 'Offset Latitude',                             8, '', ''],
                                                               ['CenterOfGravityLatitudeSE',  'DOUBLE', 'Center of Gravity Latitude Standard Error',   8, '', ''],
                                                               ['CenterOfGravityLongitude',   'DOUBLE', 'Center of Gravity Longitude',                 8, '', ''],
                                                               ['MinimumLongitude',           'DOUBLE', 'Minimum Longitude',                           8, '', ''],
                                                               ['MaximumLongitude',           'DOUBLE', 'Maximum Longitude',                           8, '', ''],
                                                               ['OffsetLongitude',            'DOUBLE', 'Offset Longitude',                            8, '', ''],
                                                               ['CenterOfGravityLongitudeSE', 'DOUBLE', 'Center of Gravity Longitude Standard Error',  8, '', ''],
                                                               ['CenterOfGravityDepth',       'DOUBLE', 'Center of Gravity Depth',                     8, '', ''],
                                                               ['MinimumDepth',               'DOUBLE', 'Minimum Depth',                               8, '', ''],
                                                               ['MaximumDepth',               'DOUBLE', 'Maximum Depth',                               8, '', ''],
                                                               ['OffsetDepth',                'DOUBLE', 'Offset Depth',                                8, '', ''],
                                                               ['CenterOfGravityDepthSE',     'DOUBLE', 'Center of Gravity Depth Standard Error',      8, '', ''],
                                                              ],
                                     "_Template_MasterSpeciesInformation" : [
                                                                             ['Species',                  'TEXT', 'Species',                     50, '', ''],
                                                                             ['CommonName',               'TEXT', 'Common Name',                 50, '', ''],
                                                                             ['SpeciesCommonName',        'TEXT', 'Species (Common Name)',      100, '', ''],
                                                                             ['CommonNameSpecies',        'TEXT', 'Common Name (Species)',      100, '', ''],
                                                                             ['TaxonomicGroup',           'TEXT', 'Taxonomic Group',             50, '', ''],
                                                                            ],
                                     "_Template_RegionSpeciesYearImageName" : [
                                                                               ['LayerCode',                'TEXT',  'Layer Code',                  20, '', ''],
                                                                               ['Region',                   'TEXT',  'Region',                      40, '', ''],
                                                                               ['FilterRegion',             'TEXT',  'Filter Region',               40, '', ''],
                                                                               ['FilterSubRegion',          'TEXT',  'Filter Sub-Region',           40, '', ''],
                                                                               ['Species',                  'TEXT',  'Species',                     50, '', ''],
                                                                               ['CommonName',               'TEXT',  'Common Name',                 50, '', ''],
                                                                               ['SpeciesCommonName',        'TEXT',  'Species (Common Name)',      100, '', ''],
                                                                               ['CommonNameSpecies',        'TEXT',  'Common Name (Species)',      100, '', ''],
                                                                               ['TaxonomicGroup',           'TEXT',  'Taxonomic Group',             50, '', ''],
                                                                               ['ManagementBody',           'TEXT',  'Management Body',             50, '', ''],
                                                                               ['ManagementPlan',           'TEXT',  'Management Plan',             50, '', ''],
                                                                               ['CoreSpecies',              'TEXT',  'Core Species',                 5, '', ''],
                                                                               ['Year',                     'SHORT', 'Year',                         4, '', ''],
                                                                               ['StdTime',                  'DATE',  'StdTime',                      8, '', ''],
                                                                               ['Variable',                 'TEXT',  'Variable',                    50, '', ''],
                                                                               ['Dimensions',               'TEXT',  'Dimensions',                  10, '', ''],
                                                                               ['ImageName',                'TEXT',  'Image Name',                 200, '', ''],
                                                                              ],
                                     "_Template_SpeciesFilter" : [
                                                                  ['Species',         'TEXT', 'Species',           50, '', ''],
                                                                  ['CommonName',      'TEXT', 'Common Name',       50, '', ''],
                                                                  ['FilterRegion',    'TEXT', 'Filter Region',     40, '', ''],
                                                                  ['FilterSubRegion', 'TEXT', 'Filter Sub-Region', 40, '', ''],
                                                                  ['TaxonomicGroup',  'TEXT', 'Taxonomic Group',   50, '', ''],
                                                                  ['ManagementBody',  'TEXT', 'Management Body',   50, '', ''],
                                                                  ['ManagementPlan',  'TEXT', 'Management Plan',   50, '', ''],
                                                                ],
                                    }

        # ###--->>> Declaring Dataset Names
        # The datasets variable includes the following information:
        #        datasets[0]: The abbreviation of the region (for file/folder structure)
        #        datasets[1]: The actual name of the region
        #        datasets[2]: The CSV file that contains this region's data
        #        datasets[3]: The region shape that gets used for the mask and extent of the environment variable, and the output coordinate system
        #        datasets[4]: The boundary shape file ( a single Polyline ) that gets used by arcpy.gp.Idw_sa
        #        datasets[5]: ??? The PRJ datum used by the region shapefile (datasets[0]). These are included within the ArcGIS installation. Please see
        #                            https://desktop.arcgis.com/en/arcmap/10.5/map/projections/pdf/projected_coordinate_systems.pdf
        #                            for valid Projection Names or inside arcgis itself.
        #                            The variable itself does not appear to be used, it's just there for my reference.
        #        datasets[6]: A shapefile containing contour lines for outputting pictures.
        #        datasets[7]: Raster cell size
        # In order to automate generating raster files and pictures for the Ocean Adapt website, This array of information was used to allow controlled and regulated so all regions are treated the exact same way.
        global datasets

##            # Assigning variables from items in the chosen table list
##            #layercode_shape = table_name[0]
##            #layercode_boundary = table_name[1]
##            layercode = table_name[2]
##            region = table_name[3]
##            csv_file = table_name[4]
##            layercode_georef = table_name[5]
##            #layercode_contours = table_name[6]
##            cell_size = table_name[7]
##
##            # Assigning variables from items in the chosen table list
##            #layercode_shape = table_name[0]
##            #layercode_boundary = table_name[1]
##            layercode_abb = table_name[2]
##            region = table_name[3]
##            csv_file = table_name[4]
##            layercode_georef = table_name[5]
##            #layercode_contours = table_name[6]
##            cell_size = table_name[7]

##        table_names = [
##                       [ 'AI_Shape', 'AI_Boundary','AI', 'Aleutian Islands', 'ai_csv', 'NAD_1983_2011_UTM_Zone_1N', 'contour_ai', 2000],
##                       [ 'EBS_Shape', 'EBS_Boundary','EBS', 'Eastern Bering Sea', 'ebs_csv', 'NAD_1983_2011_UTM_Zone_3N', 'contour_ebs', 2000],
##                       [ 'GOA_Shape', 'GOA_Boundary','GOA', 'Gulf of Alaska', 'goa_csv', 'NAD_1983_2011_UTM_Zone_5N', 'contour_goa', 2000],
##
##                       [ 'GOM_Shape', 'GOM_Boundary','GOM', 'Gulf of Mexico', 'gmex_csv', 'NAD_1983_2011_UTM_Zone_15N', 'contour_gom', 2000],
##
##                       #[ 'HI_Shape', 'HI_Boundary','HI', 'Hawaii Islands', 'hi_csv', 'WGS_1984_UTM_Zone_4N', 'contour_hi', 500],
##                       [ 'HI_Shape', 'HI_Boundary','HI', "Hawai'i Islands", 'hi_csv', 'WGS_1984_UTM_Zone_4N', 'contour_hi', 500],
##
##                       [ 'NEUS_Fall_Shape', 'NEUS_Fall_Boundary','NEUS_F', 'Northeast US Fall', 'neusf_csv', 'NAD_1983_2011_UTM_Zone_18N', 'contour_neus', 2000],
##                       [ 'NEUS_Spring_Shape', 'NEUS_Spring_Boundary','NEUS_S', 'Northeast US Spring', 'neus_csv', 'NAD_1983_2011_UTM_Zone_18N', 'contour_neus', 2000],
##
##                       [ 'SEUS_Shape', 'SEUS_Boundary','SEUS_SPR', 'Southeast US Spring', 'seus_spr_csv', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],
##                       [ 'SEUS_Shape', 'SEUS_Boundary','SEUS_SUM', 'Southeast US Summer', 'seus_sum_csv', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],
##                       [ 'SEUS_Shape', 'SEUS_Boundary','SEUS_FALL', 'Southeast US Fall', 'seus_fal_csv', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],
##
##                       [ 'WC_Ann_Shape', 'WC_Ann_Boundary','WC_ANN', 'West Coast Annual 2003-Present', 'wcann_csv', 'NAD_1983_2011_UTM_Zone_10N', 'contour_wc', 2000],
##                       [ 'WC_Tri_Shape', 'WC_Tri_Boundary','WC_TRI', 'West Coast Triennial 1977-2004', 'wctri_csv', 'NAD_1983_2011_UTM_Zone_10N', 'contour_wc', 2000]
##                      ]

##        datasets = [
##                    [ 'AI', 'Aleutian Islands', 'ai_csv', 'AI_Shape', 'AI_Boundary', 'NAD_1983_2011_UTM_Zone_1N', 'contour_ai', 2000],
##                    [ 'EBS', 'Eastern Bering Sea', 'ebs_csv', 'EBS_Shape', 'EBS_Boundary', 'NAD_1983_2011_UTM_Zone_3N', 'contour_ebs', 2000],
##                    [ 'GOA', 'Gulf of Alaska', 'goa_csv','GOA_Shape', 'GOA_Boundary', 'NAD_1983_2011_UTM_Zone_5N', 'contour_goa', 2000],
##
##                    [ 'GMEX', 'Gulf of Mexico', 'gmex_csv', 'GMEX_Shape', 'GMEX_Boundary', 'NAD_1983_2011_UTM_Zone_15N', 'contour_gmex', 2000],
##
##                    # [ 'HI', 'Hawaii Islands', 'hi_csv','HI_Shape', 'HI_Boundary', 'WGS_1984_UTM_Zone_4N', 'contour_hi', 500],
##                    [ 'HI', "Hawai'i Islands", 'hi_csv','HI_Shape', 'HI_Boundary', 'WGS_1984_UTM_Zone_4N', 'contour_hi', 500],
##
##                    [ 'NEUS_F', 'Northeast US Fall', 'neusf_csv', 'NEUS_Fall_Shape', 'NEUS_Fall_Boundary', 'NAD_1983_2011_UTM_Zone_18N', 'contour_neus', 2000],
##                    [ 'NEUS_S', 'Northeast US Spring', 'neus_csv', 'NEUS_Spring_Shape', 'NEUS_Spring_Boundary', 'NAD_1983_2011_UTM_Zone_18N', 'contour_neus', 2000],
##
##                    [ 'SEUS_SPR', 'Southeast US Spring', 'seus_spr_csv', 'SEUS_Shape', 'SEUS_Boundary', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],
##                    [ 'SEUS_SUM', 'Southeast US Summer', 'seus_sum_csv', 'SEUS_Shape', 'SEUS_Boundary', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],
##                    [ 'SEUS_FALL', 'Southeast US Fall', 'seus_fal_csv', 'SEUS_Shape', 'SEUS_Boundary', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],
##
##                    # [ 'WC_ANN', 'West Coast Annual 2003-Present', 'wcann_csv', 'WC_Ann_Shape', 'WC_Ann_Boundary', 'NAD_1983_2011_UTM_Zone_10N', 'contour_wc', 2000],
##                    #  'WC_TRI', 'West Coast Triennial 1977-2004', 'wctri_csv', 'WC_Tri_Shape', 'WC_Tri_Boundary', 'NAD_1983_2011_UTM_Zone_10N', 'contour_wc', 2000],
##                    [ 'WC_ANN', 'West Coast Annual', 'wcann_csv', 'WC_Ann_Shape', 'WC_Ann_Boundary', 'NAD_1983_2011_UTM_Zone_10N', 'contour_wc', 2000],
##                    [ 'WC_TRI', 'West Coast Triennial', 'wctri_csv', 'WC_Tri_Shape', 'WC_Tri_Boundary', 'NAD_1983_2011_UTM_Zone_10N', 'contour_wc', 2000],
##                    ]
#"RegionAbbr", "OARegion", "DisMapRegionCode", "DisMapSeasonCode", "LayerCode", "LayerName", "Version", "DateCode", "DistributionProjectName", "DistributionProjectCode", "Region", "SeasonCode", "SummaryProduct", "CSVFile", "GeographicArea", "CoordinateSystem", "CellSize", "TransformUnit"

        datasets = [#"OARegionCode", "OARegion",                       "DisMapRegionCode",                  "DisMapSeasonCode", "LayerCode",    "LayerName",                           "Version",       "DateCode", "DistributionProjectName",                              "DistributionProjectCode", "Region",                          "SeasonCode", "SummaryProduct", "CSVFile",          "GeographicArea",     "CoordinateSystem",          "CellSize", "TransformUnit", "TimeZone"
                    ["AI",           "Aleutian Islands",               "aleutian_islands",                  "",                 "AI_IDW",       "Aleutian Islands IDW",                "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Aleutian Islands",                "",           "Yes",            "AI_IDW.csv",       "AI_IDW_Shape",       "NAD_1983_2011_UTM_Zone_1N",  2000,       "cuberoot",     "US/Alaska", ],
                    ["EBS",          "Eastern Bering Sea",             "eastern_bering_sea",                "",                 "EBS_IDW",      "Eastern Bering Sea IDW",              "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Eastern Bering Sea",              "",           "Yes",            "EBS_IDW.csv",      "EBS_IDW_Shape",      "NAD_1983_2011_UTM_Zone_3N",  2000,       "cuberoot",     "US/Alaska", ],
                    ["",             "",                               "",                                  "",                 "NBS_IDW",      "Northern Bering Sea IDW",             "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Northern Bering Sea",             "",           "Yes",            "NBS_IDW.csv",      "NBS_IDW_Shape",      "NAD_1983_2011_UTM_Zone_3N",  2000,       "cuberoot",     "US/Alaska", ],
                    ["GOA",          "Gulf of Alaska",                 "gulf_of_alaska",                    "",                 "GOA_IDW",      "Gulf of Alaska IDW",                  "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Gulf of Alaska",                  "",           "Yes",            "GOA_IDW.csv",      "GOA_IDW_Shape",      "NAD_1983_2011_UTM_Zone_5N",  2000,       "cuberoot",     "US/Alaska", ],
                    ["",             "",                               "",                                  "",                 "ENBS_IDW",     "Eastern and Northern Bering Sea IDW", "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Eastern and Northern Bering Sea", "",           "Yes",            "ENBS_IDW.csv",     "ENBS_IDW_Shape",     "",                           0,           "",            "US/Alaska", ],
                    ["",             "",                               "",                                  "",                 "BSS_IDW",      "Bering Sea Slope IDW",                "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Bering Sea Slope",                "",           "Yes",            "BSS_IDW.csv",      "BSS_IDW_Shape",      "",                           0,           "",            "US/Alaska", ],
                    ["GMEX",         "Gulf of Mexico",                 "gulf_of_mexico",                    "",                 "GMEX_IDW",     "Gulf of Mexico IDW",                  "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Gulf of Mexico",                  "",           "Yes",            "GMEX_IDW.csv",     "GMEX_IDW_Shape",     "NAD_1983_2011_UTM_Zone_15N", 2000,       "cuberoot",     "US/Central",],
                    ["HI",           "Hawai'i Islands",                "hawaii_islands",                    "",                 "HI_IDW",       "Hawai'i Islands IDW",                 "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Hawai'i Islands",                 "",           "Yes",            "HI_IDW.csv",       "HI_IDW_Shape",       "WGS_1984_UTM_Zone_4N",       500,        "cuberoot",     "US/Hawaii", ],
                    ["NEUS_F",       "Northeast US Fall",              "northeast_us_fall",                 "Fall",             "NEUS_FAL_IDW", "Northeast US Fall IDW",               "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Northeast US",                    "Fall",       "Yes",            "NEUS_FAL_IDW.csv", "NEUS_FAL_IDW_Shape", "NAD_1983_2011_UTM_Zone_18N", 2000,       "cuberoot",     "US/Eastern",],
                    ["NEUS_S",       "Northeast US Spring",            "northeast_us_spring",               "Spring",           "NEUS_SPR_IDW", "Northeast US Spring IDW",             "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Northeast US",                    "Spring",     "Yes",            "NEUS_SPR_IDW.csv", "NEUS_SPR_IDW_Shape", "NAD_1983_2011_UTM_Zone_18N", 2000,       "cuberoot",     "US/Eastern",],
                    ["SEUS_FALL",    "Southeast US Fall",              "southeast_us_fall",                 "Fall",             "SEUS_FAL_IDW", "Southeast US Fall IDW",               "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Southeast US",                    "Fall",       "Yes",            "SEUS_FAL_IDW.csv", "SEUS_SPR_IDW_Shape", "NAD_1983_2011_UTM_Zone_17N", 2000,       "cuberoot",     "US/Eastern",],
                    ["SEUS_SPR",     "Southeast US Spring",            "southeast_us_spring",               "Spring",           "SEUS_SPR_IDW", "Southeast US Spring IDW",             "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Southeast US",                    "Spring",     "Yes",            "SEUS_SPR_IDW.csv", "SEUS_SUM_IDW_Shape", "NAD_1983_2011_UTM_Zone_17N", 2000,       "cuberoot",     "US/Eastern",],
                    ["SEUS_SUM",     "Southeast US Summer",            "southeast_us_summer",               "Summer",           "SEUS_SUM_IDW", "Southeast US Summer IDW",             "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "Southeast US",                    "Summer",     "Yes",            "SEUS_SUM_IDW.csv", "SEUS_FAL_IDW_Shape", "NAD_1983_2011_UTM_Zone_17N", 2000,       "cuberoot",     "US/Eastern",],
                    ["",             "",                               "",                                  "",                 "WC_GLMME",     "West Coast GLMME",                    "January 1 2023", 20230101,  "West Coast Generallized Lineral Mixed Model Ensemble", "GLMME",                   "West Coast",                      "",           "No",             "WC_GLMME.csv",     "WC_GLMME_Shape",     "NAD_1983_2011_UTM_Zone_10N", 10000,      "log10",        "US/Pacific",],
                    ["WC_ANN",       "West Coast Annual 2003-Present", "west_coast_annual_2003_to_present", "Annual",           "WC_ANN_IDW",   "West Coast Annual IDW",               "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "West Coast",                      "Annual",     "Yes",            "WC_ANN_IDW.csv",   "WC_ANN_IDW_Shape",   "NAD_1983_2011_UTM_Zone_10N", 2000,       "cuberoot",     "US/Pacific",],
                    ["WC_TRI",       "West Coast Triennial 1977-2004", "west_coast_triennial_1977_to_2004", "Triennial",        "WC_TRI_IDW",   "West Coast Triennial IDW",            "January 1 2023", 20230101,  "NMFS/Rutgers IDW Interpolation",                       "IDW",                     "West Coast",                      "Triennial",  "Yes",            "WC_TRI_IDW.csv",   "WC_TRI_IDW_Shape",   "NAD_1983_2011_UTM_Zone_10N", 2000,       "cuberoot",     "US/Pacific",],
                   ]

        # Test if True
        if FilterDatasets:
            # selected_regions = ['AI', 'EBS', 'GOA', 'GMEX', 'HI', 'NEUS_F', 'NEUS_S', 'SEUS_FALL', 'SEUS_SPR', 'SEUS_SUM', 'WC_ANN', 'WC_TRI',]
            # Below are lists used to test different regions
            #selected_datasets = ['HI',]
            # New datasets list of lists #-> https://stackoverflow.com/questions/21507319/python-list-comprehension-list-of-lists
            datasets = [[r for r in group] for group in datasets if group[0] in selected_datasets]
            #del selected_datasets
        #else:
        #    datasets = [[r for r in group] for group in datasets if group[0] in selected_datasets]

##        # Spatial Reference Dictionary
##        global dataset_srs
##        dataset_srs = {
##                       'NAD_1983_2011_UTM_Zone_1N'  : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Aleutian Islands
##                       'NAD_1983_2011_UTM_Zone_3N'  : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Eastern Bering Sea
##                       'NAD_1983_2011_UTM_Zone_5N'  : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Gulf of Alaska
##                       'NAD_1983_2011_UTM_Zone_10N' : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # West Coast
##                       'WGS_1984_UTM_Zone_4N'       : "PROJCS['WGS_1984_UTM_Zone_4N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-159.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-5120900 -9998100 450445547.391054;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision", # Hawaii
##                       'WGS_1984_UTM_Zone_10N'      : 'PROJCS["unknown",GEOGCS["GCS_unknown",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-123.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["kilometre",1000.0]];-5120.9 -9998.1 450445547391.054;-100000 10000;-100000 10000;0.000001;0.001;0.001;IsHighPrecision', # West Coast GLMME
##                       'NAD_1983_2011_UTM_Zone_15N' : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Gulf of Mexico
##                       'NAD_1983_2011_UTM_Zone_17N' : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Southeast US
##                       'NAD_1983_2011_UTM_Zone_18N' : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Northeast US
##                      }

        # Geographic Regions Dictionary
        global geographic_regions
        geographic_regions = {
                              'AI'        : 'Aleutian Islands',
                              'EBS'       : 'Eastern Bering Sea',
                              'GOA'       : 'Gulf of Alaska',
                              'GMEX'      : 'Gulf of Mexico',
                              #'HI'        : 'Hawaii Islands',
                              'HI'        : "Hawai'i Islands",
                              'NEUS_F'    : 'Northeast US',
                              'NEUSF'     : 'Northeast US, East Coast',
                              'NEUS_S'    : 'Northeast US',
                              'NEUS'      : 'Northeast US, East Coast',
                              'SEUS_SPR'  : 'Southeast US',
                              'SEUS_SUM'  : 'Southeast US',
                              'SEUS_FALL' : 'Southeast US',
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

        #global timezone_dict
        #timezone_dict = {# LayerCode : Time Zone
        #                 'AI_IDW'       : 'US/Alaska' ,
        #                 'BSS_IDW'      : 'US/Alaska' ,
        #                 'EBS_IDW'      : 'US/Alaska' ,
        #                 'NEBS_IDW'     : 'US/Alaska' ,
        #                 'NBS_IDW'      : 'US/Alaska' ,
        #                 'GOA_IDW'      : 'US/Alaska' ,
        #                 'GMEX_IDW'     : 'US/Central',
        #                 'HI_IDW'       : 'US/Hawaii' ,
        #                 'NEUS_FAL_IDW' : 'US/Eastern',
        #                 'NEUS_SPR_IDW' : 'US/Eastern',
        #                 'SEUS_FAL_IDW' : 'US/Eastern',
        #                 'SEUS_SPR_IDW' : 'US/Eastern',
        #                 'SEUS_SUM_IDW' : 'US/Eastern',
        #                 'WC_ANN_IDW'   : 'US/Pacific',
        #                 'WC_GLMME'     : 'US/Pacific',
        #                 'WC_TRI_IDW'   : 'US/Pacific',
        #                }


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
                                    # 'WC_GLMME'
                                    'Microstomus pacificus' : 'Dover sole',
                                    # 'GMEX', 'Gulf of Mexico'
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
                                    # 'WC_GLMME'
                                    'Microstomus pacificus' : 'Dover sole',
                                    'Sebastolobus altivelis' : 'Longspine thornyhead',
                                    # 'GMEX', 'Gulf of Mexico'
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
        #global selected_years
        #if FilterYears:
        #    year_min = 1983; year_max = 1987
        #    selected_years = [yr for yr in range(year_min, year_max+1)]
        #    del year_min, year_max
        #else:
        #    selected_years = []

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpCreateDisMapRegions(args):
    """mp Create Region Bathymetry"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        start_time = time()

        dataset, REGION_SHAPEFILE_DIRECTORY, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr, log_file_folder

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        oaregioncode     = dataset[0]
        oaregion         = dataset[1]
        layercode        = dataset[4]
        region           = dataset[9]
        #csvfile          = dataset[12][:-4].upper()
        geographicarea   = dataset[13]
        #coordinatesystem = dataset[14]
        #transformunit    = dataset[16]
# #      oaregioncode            = dataset[0]
# #      oaregion                = dataset[1]
# #      dismapregioncode        = dataset[2]
# #      dismapseasoncode        = dataset[3]
# #      layercode               = dataset[4]
# #      layername               = dataset[5]
# #      datecode                = dataset[6]
# #      distributionprojectname = dataset[7]
# #      distributionprojectcode = dataset[8]
# #      region                  = dataset[9]
# #      seasoncode              = dataset[10]
# #      summaryproduct          = dataset[11]
# #      csvfile                 = dataset[12]
# #      geographicarea          = dataset[13]
# #      coordinatesystem        = dataset[14]
# #      cellsize                = dataset[15]
# #      transformunit           = dataset[16]
# #      timezone                = dataset[17]
        del dataset

        RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

        del SoftwareEnvironmentLevel, ScratchFolder

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = RegionGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = RegionScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Set the output coordinate system to what is needed for the
        # DisMAP project
        geographicarea_sr = os.path.join(REGION_SHAPEFILE_DIRECTORY, layercode, f"{geographicarea}.prj")
        #print(geographicarea_sr)

        sr = arcpy.SpatialReference(geographicarea_sr)
        del geographicarea_sr

        arcpy.env.outputCoordinateSystem = sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        del sr

        # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
        msg = f'> Generating {layercode} Surevy Areas'
        logFile(log_file, msg); del msg

        layercode_survey_area = os.path.join(RegionGDB, f"{layercode}_Survey_Area")

        # The shapefile used to create the extent and mask for the environment variable
        layercode_shape_file = os.path.join(REGION_SHAPEFILE_DIRECTORY, layercode, geographicarea + ".shp")
        layercode_shape_scratch = os.path.join(RegionScratchGDB, geographicarea)

        # Delete after last use
        del REGION_SHAPEFILE_DIRECTORY, geographicarea

        msg = f'>-> Copy {layercode} Shape File to a Dataset.'
        logFile(log_file, msg); del msg

        with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
            arcpy.conversion.ExportFeatures(in_features = layercode_shape_file,
                                            out_features = layercode_shape_scratch,
                                            where_clause = "",
                                            use_field_alias_as_name = "",
                                            field_mapping = "",
                                            sort_field = "")
        # Delete after use
        del layercode_shape_file

        # Get a list of non-required fields
        fields = [f.name for f in arcpy.ListFields(layercode_shape_scratch) if not f.required]

        msg = f'>-> Delete non-required fields from {layercode} Dataset.'
        logFile(log_file, msg); del msg
        arcpy.management.DeleteField(layercode_shape_scratch, fields)

        # Delete after last use
        del fields

        msg = f'>-> Adding the "OARegionCode" field to the {layercode} Dataset'
        logFile(log_file, msg); del msg

        # Process: Add Region Field
        arcpy.management.AddField(layercode_shape_scratch, "OARegionCode", "TEXT", "", "", "10", "OA Region Code", "NULLABLE", "NON_REQUIRED", "")

        msg = f">-> Calculating the 'OARegionCode' field in the {layercode} Dataset"
        logFile(log_file, msg); del msg
        # Process: Calculate Region Field
        arcpy.management.CalculateField(layercode_shape_scratch, "OARegionCode", f'"{oaregioncode}"', "PYTHON", "")
        del oaregioncode

        msg = f'>-> Adding the "OARegion" field to the {layercode} Dataset'
        logFile(log_file, msg); del msg

        # Process: Add Region Field
        arcpy.management.AddField(layercode_shape_scratch, "OARegion", "TEXT", "", "", "50", "OA Region", "NULLABLE", "NON_REQUIRED", "")

        msg = f">-> Calculating the 'OARegion' field in the {layercode} Dataset"
        logFile(log_file, msg); del msg
        # Process: Calculate Region Field
        arcpy.management.CalculateField(layercode_shape_scratch, "OARegion", f'"{oaregion}"', "PYTHON", "")
        del oaregion

        msg = f'>-> Adding the "LayerCode" field to the {layercode} Dataset'
        logFile(log_file, msg); del msg

        # Process: Add Region Field
        arcpy.management.AddField(layercode_shape_scratch, "LayerCode", "TEXT", "", "", "20", "Layer Code", "NULLABLE", "NON_REQUIRED", "")

        msg = f">-> Calculating the 'LayerCode' field in the {layercode} Dataset"
        logFile(log_file, msg); del msg
        # Process: Calculate Region Field
        arcpy.management.CalculateField(layercode_shape_scratch, "LayerCode", f'"{layercode}"', "PYTHON", "")

        msg = f'>-> Adding the "Region" field to the {layercode} Dataset'
        logFile(log_file, msg); del msg

        # Process: Add Region Field
        arcpy.management.AddField(layercode_shape_scratch, "Region", "TEXT", "", "", "40", "Region", "NULLABLE", "NON_REQUIRED", "")

        msg = f">-> Calculating the 'Region' field in the {layercode} Dataset"
        logFile(log_file, msg); del msg
        # Process: Calculate Region Field
        arcpy.management.CalculateField(layercode_shape_scratch, "Region", f'"{region}"', "PYTHON", "")

        msg = f">-> Adding the 'ID' field in the {layercode} Dataset"
        logFile(log_file, msg); del msg
        arcpy.management.AddField(layercode_shape_scratch, "ID", "LONG","","","","ID","NULLABLE","NON_REQUIRED")

        msg = f">-> Calculating the 'ID' field in the {layercode} Dataset"
        logFile(log_file, msg); del msg
        # Set ID field value
        arcpy.management.CalculateField(layercode_shape_scratch, "ID", 1, "PYTHON")

        layercode_survey_area = f"{layercode}_Survey_Area"
        layercode_boundary_line = f"{layercode}_Boundary_Line"

        msg = f">-> Export Features from scratch to region gdb for the {layercode} Dataset"
        logFile(log_file, msg); del msg

        with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
            arcpy.conversion.ExportFeatures(in_features = layercode_shape_scratch,
                                            out_features = layercode_survey_area,
                                            where_clause = "",
                                            use_field_alias_as_name = "",
                                            field_mapping = "",
                                            sort_field = "")
        # Delete after use
        arcpy.management.Delete(layercode_shape_scratch)
        del layercode_shape_scratch, RegionScratchGDB, RegionGDB

        msg = f">-> Converting the {layercode} Dataset from Polygon to Polyline"
        logFile(log_file, msg); del msg
        # Process: Feature To Line
        arcpy.management.FeatureToLine(in_features = layercode_survey_area, out_feature_class = layercode_boundary_line, cluster_tolerance="", attributes="ATTRIBUTES")

        # Delete after last use
        del layercode_survey_area, layercode_boundary_line

        # Resets a specific environment setting to its default
        arcpy.ClearEnvironment("cellSize")
        arcpy.ClearEnvironment("extent")
        arcpy.ClearEnvironment("mask")
        arcpy.ClearEnvironment("snapRaster")

        #Final benchmark for the region.
        msg = f"ENDING REGION {layercode} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {layercode}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)\n"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time, region

        del layercode

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpCreateGLMMETables(args):
    """mp Create CSV Tables"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        import pandas as pd
        import numpy as np
        import warnings

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        start_time = time()

        dataset, CSV_DIRECTORY, FilterSpecies, selected_species, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr, log_file_folder

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        RegionGDB = os.path.join(ScratchFolder, f"{dataset[4]} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset[4]} {SoftwareEnvironmentLevel} Scratch.gdb")

        del SoftwareEnvironmentLevel, ScratchFolder

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = RegionGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = RegionScratchGDB; del RegionScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Assigning variables from items in the chosen table list
        layercode     = dataset[4]
        region        = dataset[9]
        csvfile       = dataset[12][:-4].upper()
        transformunit = dataset[16]
        timezone      = dataset[17]
##        oaregioncode            = dataset[0]
##        oaregion                = dataset[1]
##        dismapregioncode        = dataset[2]
##        dismapseasoncode        = dataset[3]
##        layercode               = dataset[4]
##        layername               = dataset[5]
##        datecode                = dataset[6]
##        distributionprojectname = dataset[7]
##        distributionprojectcode = dataset[8]
##        region                  = dataset[9]
##        seasoncode              = dataset[9]
##        summaryproduct          = dataset[11]
##        csvfile                 = dataset[12][:-4].upper()
##        geographicarea          = dataset[13]
##        coordinatesystem        = dataset[14]
##        cellsize                = dataset[15]
##        transformunit           = dataset[16]
##        timezone                = dataset[17]
        del dataset

        start_time = time()

        # Write a message to the log file
        msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        input_csvfile = os.path.join(CSV_DIRECTORY, csvfile + ".csv")
        del CSV_DIRECTORY

        #
        msg = f'> Generating CSV Table: {os.path.basename(input_csvfile)}'
        logFile(log_file, msg); del msg

        # https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/09_timeseries.html?highlight=datetime
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        #df = pd.read_csv('my_file.tsv', sep='\t', header=0)  ## not setting the index_col
        #df.set_index(['0'], inplace=True)

        # C:\. . .\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\lib\site-packages\numpy\lib\arraysetops.py:583:
        # FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
        # mask |= (ar1 == a)
        # A fix: https://www.youtube.com/watch?v=TTeElATMpoI
        # TLDR: pandas are Jedi; numpy are the hutts; and python is the galatic empire
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            # DataFrame
            df = pd.read_csv(input_csvfile,
                             index_col = False,
                             encoding="utf-8",
                             #encoding = "ISO-8859-1",
                             #engine='python',
                             delimiter = ',',
                             #dtype = None,
                             dtype = {
                                      "year"       : 'uint16',
                                      "lon_UTM"    : float,
                                      "lat_UTM"    : float,
                                      "lat"        : float,
                                      "lon"        : float,
                                      "depth_m"    : float,
                                      "median_est" : float,
                                      "mean_est"   : float,
                                      "est5"       : float,
                                      "est95"      : float,
                                      "spp_sci"    : str,
                                      "spp_common" : str,
                                      },
                             )
        del input_csvfile

        msg = f'>-> Defining the column names.'
        logFile(log_file, msg); del msg

        # The original column names from the CSV files are not very
        # reader friendly, so we are making some changes here
        #df.columns = [u'Region', u'HUALID', u'Year', u'Species', u'WTCPUE', u'CommonName', u'Stratum', u'StratumArea', u'Latitude', u'Longitude', u'Depth']
        df.columns = ['Year', 'Easting', 'Northing', 'Latitude', 'Longitude', 'Depth', 'MedianEstimate', 'MeanEstimate', 'Estimate5Percent', 'Estimate95Percent', 'Species', 'CommonName',]

        # Test if we are filtering on species. If so, a new species list is
        # created with the selected species remaining in the list
        if FilterSpecies:
            msg = '>->-> Filtering table on selected species for {0} Table'.format(region)
            logFile(log_file, msg); del msg
            # Filter data frame
            df = df.loc[df['Species'].isin(selected_species.keys())]
        else:
            msg = '>->-> No species filtering of selected species for {0} Table'.format(region)
            logFile(log_file, msg); del msg

        del FilterSpecies, selected_species

        #-->> Species and CommonName
        msg = f'#--->  Setting Nulls in Species and CommonName to empty strings.'
        logFile(log_file, msg); del msg
        # Replace NaN with an empty string. When pandas reads a cell
        # with missing data, it asigns that cell with a Null or nan
        # value. So, we are changing that value to an empty string of ''.
        # Seems to be realivent for Species and CommonName only
        df.Species    = df.Species.fillna('')
        df.CommonName = df.CommonName.fillna('')
        df.Species    = df.Species.replace('Na', '')
        df.CommonName = df.CommonName.replace('Na', '')

        # Example of how to drop rows in a Data Frame
        # msg = f'#--->  Droping row where Species have an empty string.'
        # logFile(log_file, msg); del msg
        # Drop rows based on a condition. Rows without a species name are not of use
        # df = df[df.Species != '']

        #-->> Layer Code
        msg = f'#--->  Adding Layer Code.'
        logFile(log_file, msg); del msg
        # Insert column
        df.insert(df.columns.get_loc('Year'), 'LayerCode', f"{layercode}")

        #-->> Region
        msg = f'#--->  Adding Region.'
        logFile(log_file, msg); del msg
        # Insert column
        df.insert(df.columns.get_loc('Year'), 'Region', f"{region}")

        #-->> Region
        msg = f'#--->  Adding StdTime.'
        logFile(log_file, msg); del msg
        # Insert column
        #df['date'] = pd.to_datetime(df['Year'], format="%Y").dt.tz_localize(timezone).dt.tz_convert('UTC')
        df.insert(df.columns.get_loc('Year')+1, 'StdTime', pd.to_datetime(df['Year'], format="%Y").dt.tz_localize(timezone).dt.tz_convert('UTC'))
        del timezone

        #-->> SpeciesCommonName
        msg = f'#--->  Adding SpeciesCommonName and setting it to "Species (CommonName)".'
        logFile(log_file, msg); del msg
        # Insert column
        df.insert(df.columns.get_loc('CommonName')+1, 'SpeciesCommonName', df['Species'] + ' (' + df['CommonName'] + ')')

        #-->> CommonNameSpecies
        msg = f'#--->  Adding CommonNameSpecies and setting it to "CommonName (Species)".'
        logFile(log_file, msg); del msg
        # Insert column
        df.insert(df.columns.get_loc('SpeciesCommonName')+1, 'CommonNameSpecies', df['CommonName'] + ' (' + df['Species'] + ')')

        #-->> AnalysisValue
        msg = f'#--->  Adding the AnalysisValue column and calculating values.'
        logFile(log_file, msg); del msg
        # Insert a column to the right of a column and then do a calculation
        df.insert(df.columns.get_loc('MedianEstimate')+1, 'AnalysisValue', 10 ** df['MedianEstimate'])

        #-->> TransformUnit
        msg = f'#--->  Adding the TransformUnit column and calculating values.'
        logFile(log_file, msg); del msg
        # Insert a column to the right of a column and then do a calculation
        df.insert(df.columns.get_loc('AnalysisValue')+1, 'TransformUnit', transformunit)
        del transformunit

        msg = f'>-> Creating the {region} Geodatabase Table'
        logFile(log_file, msg); del msg

        # ###--->>> Numpy Datatypes
        # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm

        #print('DataFrame\n----------\n', df.head(10))
        #print('\nDataFrame datatypes :\n', df.dtypes)
        #columns = [str(c) for c in df.dtypes.index.tolist()]
        column_names = list(df.columns)
        #print(column_names)
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        #[                'LayerCode', 'Region', 'Year', 'StdTime', 'Easting', 'Northing', 'Latitude', 'Longitude', 'Depth', 'MedianEstimate', 'AnalysisValue', 'TransformUnit', 'MeanEstimate', 'Estimate5Percent', 'Estimate95Percent', 'Species', 'CommonName', 'SpeciesCommonName', 'CommonNameSpecies',]
        column_formats = [ 'S20', 'S40', 'u4', 'M8[us]', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'S10', 'd', 'd', 'd', 'S40', 'U30', 'U60', 'U60', ]

        dtypes = list(zip(column_names, column_formats))
        del column_names, column_formats

        # Cast text as Unicode in the CommonName field
        df['CommonName'] = df['CommonName'].astype('unicode')

        #print(df)
        try:
            array = np.array(np.rec.fromrecords(df.values), dtype = dtypes)
        except Exception as e:
            import sys
            msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
            print(msg); del msg, sys

        del df, dtypes

        # Temporary table
        tmp_table = f'memory\{csvfile}_tmp'
        #print(layercode_csv_table)
        #tmp_table = os.path.join(RegionScratchGDB, f'{layercode_csv_table}_tmp'); del RegionScratchGDB

        if arcpy.Exists(tmp_table):
            arcpy.management.Delete(tmp_table)

        try:
            arcpy.da.NumPyArrayToTable(array, tmp_table)
            del array
        except arcpy.ExecuteError:
            import sys
            msg = arcpy.GetMessages(2).replace('\n', '\n\t')
            msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
            #print(msg); del msg
            logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys

        msg = f'>-> Adding the StdTime column to the {region} Table and calculating the datetime value'
        logFile(log_file, msg); del msg

        del layercode

        msg = f'>-> Copying the {region} Table from memory to the GDB'
        logFile(log_file, msg); del msg

        out_table = os.path.join(RegionGDB, csvfile)

        # Execute CreateTable
        arcpy.management.CreateTable(RegionGDB, csvfile, os.path.join(RegionGDB, "_Template_GLMME_Data"), "", "")

        del RegionGDB, csvfile

        arcpy.CopyRows_management(tmp_table, out_table, "")

        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        msg = f'>-> Updating the field aliases for the {region} Table'
        logFile(log_file, msg); del msg

        # Field Alias Dictionary
        field_alias = {
                        "LayerCode"         : "Layer Code",
                        "Region"            : "Region",
                        "Year"              : "Year",
                        "StdTime"           : "StdTime",
                        "Easting"           : "Easting (UTM)",
                        "Northing"          : "Northing (UTM)",
                        "Latitude"          : "Latitude (DD)",
                        "Longitude"         : "Longitude (DD)",
                        "Depth"             : "Depth",
                        "MedianEstimate"    : "Median Estimate",
                        "AnalysisValue"     : "Analysis Value",
                        "TransformUnit"     : "Transform Unit",
                        "MeanEstimate"      : "Mean Estimate",
                        "Estimate5Percent"  : "Estimate 5 Percent",
                        "Estimate95Percent" : "Estimate 95 Percent",
                        "Species"           : "Species",
                        "CommonName"        : "Common Name",
                        "SpeciesCommonName" : "Species (Common Name)",
                        "CommonNameSpecies" : "Common Name (Species)",
                      }

        # Alter Field Alias
        alterFieldAlias(out_table, field_alias, log_file)
        #
        del field_alias

        msg = f'>-> Adding metadata to the {region} Table'
        logFile(log_file, msg); del msg

        # Add Metadata
        addMetadata(out_table, log_file)

        # Cleanup
        del out_table, region

        del pd, np, warnings

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

# ## Reads from the queue and does work
def mpCreateIDWRasters(args):
    """mp Create Biomass Rasters"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        start_time = time()

        dataset, SoftwareEnvironmentLevel, ScratchFolder, \
        log_file_folder, IMAGE_DIRECTORY = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        RegionGDB = os.path.join(ScratchFolder, f"{dataset[0]} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset[0]} {SoftwareEnvironmentLevel} Scratch.gdb")

        del SoftwareEnvironmentLevel

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = RegionGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = RegionScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Set the compression environment to LZ77
        arcpy.env.compression = "LZ77"

        # Assigning variables from items in the chosen table list
        layercode = dataset[0]
        region = dataset[1]
        #layercode_csv_table = dataset[2]
        #layercode_shape = dataset[3]
        #layercode_boundary = dataset[4]
        layercode_georef = dataset[5]
        #layercode_contours = dataset[6]
        cellsize = dataset[7]
        del dataset

        # Write a message to the log file
        msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        msg = f'> Generating {region} Biomass Rasters'
        logFile(log_file, msg); del msg

        # Get the reference system defined for the region in datasets
        layercode_sr = arcpy.SpatialReference(layercode_georef)
        arcpy.env.outputCoordinateSystem = layercode_sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

        # Delete after last use
        del layercode_georef, layercode_sr

        arcpy.env.cellSize = cellsize

        layercode_raster_mask = os.path.join(RegionGDB, f"{layercode}_Raster_Mask")

        # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
        arcpy.env.extent = arcpy.Describe(layercode_raster_mask).extent
        arcpy.env.mask = layercode_raster_mask
        arcpy.env.snapRaster = layercode_raster_mask
        del layercode_raster_mask

        msg = f">-> Make Feature Layer for {layercode}_Sample_Locations"
        logFile(log_file, msg); del msg

        # Prepare the points layer
        layercode_sample_locations = os.path.join(RegionGDB, f"{layercode}_Sample_Locations")
        layercode_sample_locations_layer = arcpy.management.MakeFeatureLayer(layercode_sample_locations, "Region Sample Locations Layer")
        del layercode_sample_locations

        # Add the YearWeights feild
        fields =  [f.name for f in arcpy.ListFields(layercode_sample_locations_layer)]
        if "YearWeights" not in fields:
            # Add the YearWeights field to the Dataset. This is used for the IDW modeling later
            arcpy.management.AddField(layercode_sample_locations_layer, "YearWeights", "SHORT", field_alias = "Year Weights")
        del fields

        result = arcpy.management.GetCount(layercode_sample_locations_layer)
        msg = f'>-> {layercode}_Sample_Locations has {result[0]:,d} records'
        logFile(log_file, msg); del msg, result

        layercode_unique_species = unique_species( layercode_sample_locations_layer )
        # print(f"{', '.join(layercode_unique_species)}\n")

        # Finally we will start looping of the uniquely identified fish in this csv.
        for layercode_unique_specie in layercode_unique_species:
            # We prepare a place so that we can place fish data relevant to the fish species we're looking at.
            #print(layercode_unique_specie)

            layercode_unique_specie_dir = layercode_unique_specie.replace('(','').replace(')','')

            msg = f"#---> Creating Raster Files for {layercode_unique_specie} in directory: {layercode_unique_specie_dir}"
            logFile(log_file, msg); del msg

            # Create a special folder for them
            layercode_unique_specie_dir_path = os.path.join(IMAGE_DIRECTORY, layercode, layercode_unique_specie_dir)
            if not os.path.exists( layercode_unique_specie_dir_path  ) and not os.path.isdir( layercode_unique_specie_dir_path ):
                os.makedirs( layercode_unique_specie_dir_path )
            #print(f"\n#-> {layercode_unique_specie_dir_path}")
            #print(f"###--->>> {arcpy.ValidateTableName(layercode_unique_specie_dir, layercode_unique_specie_dir_path)}\n")
            del layercode_unique_specie_dir_path

            msg = f"#---> Select from {layercode}_Sample_Locations all records for {layercode_unique_specie}"
            logFile(log_file, msg); del msg

            # We are pretty much going to set min to 0, max to STD(OVER YEARS)*2+AVG(OVER YEARS), and the other two shouldn't matter, but we'll set those anyways.
            select_by_specie_no_years(layercode_sample_locations_layer, layercode_unique_specie, log_file)

            msg = f"#---> Get a list of years for the selected species {layercode_unique_specie}"
            logFile(log_file, msg); del msg

            # Get all of the unique years
            specie_unique_years = unique_year(layercode_sample_locations_layer, layercode_unique_specie)

            # Note: in the previous script there was an attemp to find the
            # earliest year of data, but that doesn't make since as the
            # unique year list is sorted (ordered).
            # set the year to the future, where no data should exist.
            # We will update this variable as we loop over the uniquely
            # identified years for later.
            # year_smallest = date.today().year + 100
            # Since the goal is to get the first (or smallest) year in the list
            # year_smallest = min(specie_unique_years)

            #print(f"Year smallest in the future: {year_smallest}"
            for specie_unique_year in specie_unique_years:
                msg =  f"#-----> Processing {layercode}_Sample_Locations for {layercode_unique_specie} and year: {specie_unique_year}"
                logFile(log_file, msg); del msg

                msg =  f"#-------> Select from {layercode}_Sample_Locations all records for {layercode_unique_specie} and year {specie_unique_year}"
                logFile(log_file, msg); del msg

                # select the fish species data by the year provided.
                #select_by_specie(layercode_sample_locations_layer, layercode_unique_specie, str(specie_unique_year), log_file)
                select_by_specie(layercode_sample_locations_layer, layercode_unique_specie, specie_unique_year, log_file)

                # Calculate YearWeights=3-(abs(Tc-Ti))
                arcpy.management.CalculateField(in_table=layercode_sample_locations_layer, field="YearWeights", expression=f"3 - (abs({int(specie_unique_year)} - !Year!))", expression_type="PYTHON", code_block="")

                # Get the count of records for selected species
                result = arcpy.management.GetCount(layercode_sample_locations_layer)
                msg = f"#-------> {layercode}_Sample_Locations has {result[0]:,d} records for {layercode_unique_specie} and year {specie_unique_year}"
                logFile(log_file, msg); del msg, result

                # Set variables for search neighborhood
                #majSemiaxis = 200000
                #minSemiaxis = 200000
                majSemiaxis = cellsize * 1000
                minSemiaxis = cellsize * 1000
                angle = 0
                maxNeighbors = 15
                minNeighbors = 10
                sectorType = "ONE_SECTOR"
                searchNeighbourhood = arcpy.SearchNeighborhoodStandard(majSemiaxis, minSemiaxis,
                                                                       angle, maxNeighbors,
                                                                       minNeighbors, sectorType)

                del majSemiaxis, minSemiaxis, angle
                del maxNeighbors, minNeighbors, sectorType

                # Check out the ArcGIS Geostatistical Analyst extension license
                arcpy.CheckOutExtension("GeoStats")

                # Generate the interpolated Raster file and store it on the local hard drive. Can now be used in other ArcGIS Documents
                # No special character used, replace spaces, '(', ')' '.', '-' with '_' (underscores)
                specie_unique_year_raster = f"{layercode}_{layercode_unique_specie_dir.replace(' ','_')}_{specie_unique_year}"
                del specie_unique_year

                #tmp_raster = os.path.join(RegionScratchGDB, f"{specie_unique_year_raster.replace('_','')}")
                tmp_raster = os.path.join(ScratchFolder, f"{specie_unique_year_raster.replace('_','')}.tif")

                # Execute IDW using the selected selected species, years, and WTCPUECubeRoot
                arcpy.IDW_ga(in_features = layercode_sample_locations_layer,
                             z_field = 'WTCPUECubeRoot',
                             out_ga_layer = '',
                             out_raster = tmp_raster,
                             cell_size = '',
                             power = 2,
                             search_neighborhood = searchNeighbourhood,
                             weight_field = "YearWeights")

                del searchNeighbourhood

                # Check In GeoStats Extension
                arcpy.CheckInExtension("GeoStats")

                msg =  f"#-------> Creating Raster File {specie_unique_year_raster}.tif for {layercode_unique_specie}"
                logFile(log_file, msg); del msg

                specie_unique_year_raster_path = os.path.join(IMAGE_DIRECTORY, layercode, layercode_unique_specie_dir, specie_unique_year_raster+".tif")
                del specie_unique_year_raster
                #print()
                #print(f"\n#-> {specie_unique_year_raster_path}")
                #print(f"###--->>> {arcpy.ValidateTableName(specie_unique_year_raster, specie_unique_year_raster_path)}\n")
                #print()

                # Execute Power to convert the raster back to WTCPUE from WTCPUECubeRoot
                out_cube = arcpy.sa.Power(tmp_raster, 3)
                #out_cube.save(tmp_raster_power)
                out_cube.save(specie_unique_year_raster_path)
                #arcpy.management.Delete(out_cube)
                del out_cube

                arcpy.management.Delete(tmp_raster)
                del tmp_raster

                # Add Metadata
                addMetadata(specie_unique_year_raster_path, log_file)

                del specie_unique_year_raster_path

                # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
                # The following inputs are layers or table views: "Aleutian_Islands"
                arcpy.management.CalculateField(in_table=layercode_sample_locations_layer, field="YearWeights", expression="None", expression_type="PYTHON", code_block="")

            del specie_unique_years, layercode_unique_specie, layercode_unique_specie_dir

            # Delete after last use

        msg = f'>-> Delete non-required fields from {layercode}_Sample_Locations.'
        logFile(log_file, msg); del msg
        arcpy.management.DeleteField(layercode_sample_locations_layer, ["YearWeights"])

        # Delete layercode_sample_locations_layer
        arcpy.management.Delete(layercode_sample_locations_layer)
        del layercode_sample_locations_layer

        # Clean up
        del RegionScratchGDB, ScratchFolder
        del log_file_folder, IMAGE_DIRECTORY, RegionGDB
        del layercode, cellsize, layercode_unique_species,

        #Final benchmark for the region.
        msg = f"ENDING REGION {region} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {region}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, region

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpCreateIDWTables(args):
    """mp Create CSV Tables"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        import pandas as pd
        import numpy as np
        import warnings

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        dataset, CSV_DIRECTORY, FilterSpecies, selected_species, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr, log_file_folder

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # layercode = datasets[i][4]
        RegionGDB = os.path.join(ScratchFolder, f"{dataset[4]} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset[4]} {SoftwareEnvironmentLevel} Scratch.gdb")

        del SoftwareEnvironmentLevel, ScratchFolder

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = RegionGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = RegionScratchGDB; del RegionScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Assigning variables from items in the chosen table list
        oaregioncode  = dataset[0]
        oaregion      = dataset[1]
        layercode     = dataset[4]
        region        = dataset[9]
        csvfile       = dataset[12][:-4].upper()
        transformunit = dataset[16]
        timezone      = dataset[17]
##        oaregioncode            = dataset[0]
##        oaregion                = dataset[1]
##        dismapregioncode        = dataset[2]
##        dismapseasoncode        = dataset[3]
##        layercode               = dataset[4]
##        layername               = dataset[5]
##        datecode                = dataset[6]
##        distributionprojectname = dataset[7]
##        distributionprojectcode = dataset[8]
##        region                  = dataset[9]
##        seasoncode              = dataset[10]
##        summaryproduct          = dataset[11]
##        csvfile                 = dataset[12][:-4].upper()
##        geographicarea          = dataset[13]
##        coordinatesystem        = dataset[14]
##        cellsize                = dataset[15]
##        transformunit           = dataset[16]
##        timezone                = dataset[17]
        del dataset


        # Write a message to the log file
        msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        input_csvfile = os.path.join(CSV_DIRECTORY, csvfile + ".csv")
        del CSV_DIRECTORY

        #
        msg = f'> Generating CSV Table: {os.path.basename(input_csvfile)}'
        logFile(log_file, msg); del msg

        # https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/09_timeseries.html?highlight=datetime
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        #df = pd.read_csv('my_file.tsv', sep='\t', header=0)  ## not setting the index_col
        #df.set_index(['0'], inplace=True)

        # C:\. . .\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\lib\site-packages\numpy\lib\arraysetops.py:583:
        # FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
        # mask |= (ar1 == a)
        # A fix: https://www.youtube.com/watch?v=TTeElATMpoI
        # TLDR: pandas are Jedi; numpy are the hutts; and python is the galatic empire
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            # DataFrame
            df = pd.read_csv(input_csvfile,
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
        del input_csvfile

        msg = f'>-> Defining the column names.'
        logFile(log_file, msg); del msg

        # The original column names from the CSV files are not very
        # reader friendly, so we are making some changes here
        df.columns = ['Region', 'SampleID', 'Year', 'Species', 'WTCPUE', 'CommonName', 'Stratum', 'StratumArea', 'Latitude', 'Longitude', 'Depth']

        # Test if we are filtering on species. If so, a new species list is
        # created with the selected species remaining in the list
        if FilterSpecies:
            msg = f'>->-> Filtering table on selected species for {region} Table'
            logFile(log_file, msg); del msg
            # Filter data frame
            df = df.loc[df['Species'].isin(selected_species.keys())]
        else:
            msg = f'>->-> No species filtering of selected species for {region} Table'
            logFile(log_file, msg); del msg

        del FilterSpecies, selected_species

        #-->> Species and CommonName
        msg = f'#--->  Setting Nulls in Species and CommonName to empty strings.'
        logFile(log_file, msg); del msg
        # Replace NaN with an empty string. When pandas reads a cell
        # with missing data, it asigns that cell with a Null or nan
        # value. So, we are changing that value to an empty string of ''.
        # Seems to be realivent for Species and CommonName only
        df.Species    = df.Species.fillna('')
        df.CommonName = df.CommonName.fillna('')
        df.Species    = df.Species.replace('Na', '')
        df.CommonName = df.CommonName.replace('Na', '')

        # Cast text as Unicode in the CommonName field
        df['CommonName'] = df['CommonName'].astype('unicode')

        # Example of how to drop rows in a Data Frame
        # msg = f'#--->  Droping row where Species have an empty string.'
        # logFile(log_file, msg); del msg
        # Drop rows based on a condition. Rows without a species name are not of use
        # df = df[df.Species != '']

        #-->> Region Abbr
        msg = f'#--->  Adding OA Region Code.'
        logFile(log_file, msg); del msg
        # Insert column
        df.insert(df.columns.get_loc('Region'), 'OARegionCode', f"{oaregioncode}")
        del oaregioncode

        #-->> OA Region
        msg = f'#--->  Adding OA Region.'
        logFile(log_file, msg); del msg
        # Insert column
        df.insert(df.columns.get_loc('OARegionCode')+1, 'OARegion', f"{oaregion}")
        del oaregion

        #-->> Layer Code
        msg = f'#--->  Adding Layer Code.'
        logFile(log_file, msg); del msg
        # Insert column
        df.insert(df.columns.get_loc('OARegion')+1, 'LayerCode', f"{layercode}")
        #del layercode

        #-->> SpeciesCommonName
        msg = f'#--->  Adding SpeciesCommonName and setting it to "Species (CommonName)".'
        logFile(log_file, msg); del msg
        # Insert column
        df.insert(df.columns.get_loc('CommonName')+1, 'SpeciesCommonName', df['Species'] + ' (' + df['CommonName'] + ')')

        #-->> CommonNameSpecies
        msg = f'#--->  Adding CommonNameSpecies and setting it to "CommonName (Species)".'
        logFile(log_file, msg); del msg
        # Insert column
        df.insert(df.columns.get_loc('SpeciesCommonName')+1, 'CommonNameSpecies', df['CommonName'] + ' (' + df['Species'] + ')')

        #-->> CoreSpecies
        msg = f'#--->  Adding CoreSpecies and setting it to "No".'
        logFile(log_file, msg); del msg
        # Insert column
        df.insert(df.columns.get_loc('CommonNameSpecies')+1, 'CoreSpecies', "No")

        #-->> WTCPUE
        msg = f'#--->  Replacing Infinity values with Nulls.'
        logFile(log_file, msg); del msg
        # Replace Inf with Nulls
        # For some cell values in the 'WTCPUE' column, there is an Inf
        # value representing an infinit
        df.replace([np.inf, -np.inf], np.nan, inplace=True)

        #-->> AnalysisValue
        msg = f'#--->  Adding the AnalysisValue column and calculating values.'
        logFile(log_file, msg); del msg
        # Insert a column to the right of a column and then do a calculation
        df.insert(df.columns.get_loc('WTCPUE')+1, 'AnalysisValue', df['WTCPUE'].pow((1.0/3.0)))

        #-->> TransformUnit
        msg = f'#--->  Adding the TransformUnit column and calculating values.'
        logFile(log_file, msg); del msg
        # Insert a column to the right of a column and then do a calculation
        df.insert(df.columns.get_loc('AnalysisValue')+1, 'TransformUnit', transformunit)
        del transformunit

        #-->> Region
        msg = f'#--->  Adding StdTime.'
        logFile(log_file, msg); del msg
        # Insert column
        df.insert(df.columns.get_loc('Year')+1, 'StdTime', pd.to_datetime(df['Year'], format="%Y").dt.tz_localize(timezone).dt.tz_convert('UTC'))
        del timezone

        msg = f'>-> Creating the {region} Geodatabase Table'
        logFile(log_file, msg); del msg

        # ###--->>> Numpy Datatypes
        # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm

    # # OARegionCode            = 9 (10)
    # # OARegion                = 30 (30)
    # # DisMapRegionCode        = 33 (40)
    # # DisMapSeasonCode        = 9 (10)
    # # LayerCode               = 12 (20)
    # # LayerName               = 35 (40)
    # # DateCode                = 8 (10)
    # # DistributionProjectName = 52 (60)
    # # DistributionProjectCode = 5 (5)
    # # Region                  = 31 (40)
    # # SeasonCode              = 9 (10)
    # # SummaryProduct          = 3 (5)
    # # CSVFile                 = 16 (20)
    # # GeographicArea          = 18 (20)
    # # CoordinateSystem        = 26 (30)
    # # CellSize                = 18 (20)
    # # TransformUnit           = 26 (30)

        # Get max length of all columns in the dataframe
        # max_length_all_cols = {col: df.loc[:, col].astype(str).apply(len).max() for col in df.columns}
        # print(max_length_all_cols); del max_length_all_cols

    # # OARegionCode       =  9 (10)
    # # OARegion           = 30 (30)
    # # LayerCode          = 12 (20)
    # # Region             = 20 (20)
    # # SampleID           = 18 (20)
    # # Year               =  4 (5)
    # # Species            = 31 (40)
    # # WTCPUE             = 18 (20)
    # # WTCPUECubeRoot     = 19 (20)
    # # CommonName         = 23 (30)
    # # SpeciesCommonName  = 57 (60)
    # # CommonNameSpecies  = 57 (60)
    # # CoreSpecies        =  2 (5)
    # # Stratum            = 14 (20)
    # # StratumArea        = 16 (20)
    # # Latitude           = 16 (20)
    # # Longitude          = 17 (20)
    # # Depth              =  9 (10)

        # print('DataFrame\n----------\n', df.head(10))
        # print('\nDataFrame datatypes :\n', df.dtypes)
        #columns = [str(c) for c in df.dtypes.index.tolist()]
        column_names = list(df.columns)
        #print(column_names)
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        #[                 'OARegionCode', 'OARegion', 'LayerCode', 'Region', 'SampleID', 'Year', 'StdTime',  'Species', 'WTCPUE', 'AnalysisValue', 'TransformUnit', 'CommonName', 'SpeciesCommonName', 'CommonNameSpecies', 'CoreSpecies', 'Stratum', 'StratumArea', 'Latitude', 'Longitude', 'Depth'      ]
        column_formats = ['S10',          'S30',      'S20',       'S40',    'S20',      'u4',   'M8[us]',   'S40',     'd',     'd',             'S10',           'U30',        'U60',               'U60',               'S5',          'S20',     'd',          'd',       'd',       'd']
        # 'M' can be used for date fields

        dtypes = list(zip(column_names, column_formats))
        del column_names, column_formats

        try:
            array = np.array(np.rec.fromrecords(df.values), dtype = dtypes)
        except Exception as e:
            import sys
            # Capture all other errors
            #print(sys.exc_info()[2].tb_lineno)
            msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
            print(msg); del msg

        del df, dtypes

        # Temporary table
        tmp_table = f'memory\{csvfile}_tmp'

        if arcpy.Exists(tmp_table):
            arcpy.management.Delete(tmp_table)

        try:
            arcpy.da.NumPyArrayToTable(array, tmp_table)
            del array
        except arcpy.ExecuteError:
            import sys
            # Geoprocessor threw an error
            #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
            msg = arcpy.GetMessages(2).replace('\n', '\n\t')
            msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
            if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
            else: print(msg); del msg, sys

        msg = f'>-> Adding the StdTime column to the {region} Table and calculating the datetime value'
        logFile(log_file, msg); del msg

        del layercode

        msg = f'>-> Calculate Core Species for the {region} Table'
        logFile(log_file, msg); del msg

        # Calculate Core Species
        calculateCoreSpecies(tmp_table, log_file)

        msg = f'>-> Copying the {region} Table from memory to the GDB'
        logFile(log_file, msg); del msg

        out_table = os.path.join(RegionGDB, csvfile)

        # Execute CreateTable
        arcpy.management.CreateTable(RegionGDB, csvfile, os.path.join(RegionGDB, "_Template_IDW_Data"), "", "")

        del RegionGDB, csvfile

        arcpy.CopyRows_management(tmp_table, out_table, "")

        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        msg = f'>-> Updating the field aliases for the {region} Table'
        logFile(log_file, msg); del msg

        # Field Alias Dictionary
        field_alias = {
                       'OARegionCode' : 'OA Region Code',
                       'OARegion' : 'OA Region',
                       'LayerCode' : 'Layer Code',
                       'Region' : 'Region',
                       'SampleID' : 'Sample ID',
                       'Species' : 'Species',
                       'CommonName' : 'Common Name',
                       'SpeciesCommonName' : 'Species (Common Name)',
                       'CommonNameSpecies' : 'Common Name (Species)',
                       'CoreSpecies' : 'Core Species',
                       'Year' : 'Year',
                       'WTCPUE' : 'WTCPUE',
                       'AnalysisValue' : 'Analysis Value',
                       'TransformUnit' : 'Transform Unit',
                       'Stratum' : 'Stratum',
                       'StratumArea' : 'Stratum Area',
                       'Latitude' : 'Latitude (DD)',
                       'Longitude' : 'Longitude (DD)',
                       'Depth' : 'Depth',
                       'StdTime' : 'StdTime',
                      }

        # Alter Field Alias
        alterFieldAlias(out_table, field_alias, log_file)
        #
        del field_alias

        msg = f'>-> Adding metadata to the {region} Table'
        logFile(log_file, msg); del msg

        # Add Metadata
        addMetadata(out_table, log_file)

        # Cleanup
        del out_table

        del pd, np, warnings

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time, region

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpCreateIndicatorsTable(args):
    import numpy as np
    import math
    np.seterr(divide='ignore', invalid='ignore')
    """mp Create Indicators Table"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        start_time = time()

        dataset, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder, \
        IMAGE_DIRECTORY = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr, log_file_folder

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        RegionGDB = os.path.join(ScratchFolder, f"{dataset[0]} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset[0]} {SoftwareEnvironmentLevel} Scratch.gdb")

        del ScratchFolder, SoftwareEnvironmentLevel

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = RegionGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = RegionScratchGDB; del RegionScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Assigning variables from items in the chosen table list
        layercode = dataset[0]
        region = dataset[1]
        layercode_csv_table = dataset[2].upper()
        #layercode_shape = dataset[3]
        #layercode_boundary = dataset[4]
        layercode_georef = dataset[5]
        #layercode_contours = dataset[6]
        cellsize = dataset[7]
        del dataset

        # Write a message to the log file
        msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        msg = f'> Generating {region} Indicators Table'
        logFile(log_file, msg); del msg

        # This is s dictionary that maps 'season' codes used as part of the CSV
        # file names. An R script, created by OceanAdap (ref?), parses a data-
        # table to create a set of CSV files that indivdually  contains data
        # for a region/season
        DisMapSeasonCodeDict = {"F" : "Fall",
                                "S" : "Spring",
                                "SPR" : "Spring",
                                "SUM" : "Summer",
                                "FALL" : "Fall",
                                "ANN" : "Annual",
                                "TRI" : "Triennial",
                                "Spring" : "Spring",
                                "Summer" : "Summer",
                                "Fall" : "Fall",
                                "Winter" : "Winter",
                                "Annual" : "Annual",
                                "Triennial" : "Triennial",
                                None : None,
                                '' : ''}

        # List of varaibles for the table
        # OARegionCode = layercode
        #OARegion = region[:region.find("(")].strip() if "(" in region else region
        RegionCode = layercode
        Region = region
        ModelRegion = ''
        #CommonName = ''
        DisMapRegionCode = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "").lower()
        #RegionText = region
        SeasonCode = layercode[layercode.find('_')+1:] if '_' in layercode else None
        DisMapSeasonCode = DisMapSeasonCodeDict[SeasonCode]
        ProductName = "IDW Interpolation"
        ProductCode = "IDW"
        SummaryProduct = ""
        # Clean up
        del SeasonCode, DisMapSeasonCodeDict

# #  0   RegionCode
# #  1   Region
# #  2   ModelRegion
# #  3   DisMapRegionCode
# #  4   DisMapSeasonCode
# #  5   Species
# #  6   CommonName
# #  7   CoreSpecies
# #  8   Year
# #  9   ProductName
# # 10   ProductCode
# # 11   SummaryProduct
# # 12   CenterOfGravityLatitude
# # 13   MinimumLatitude
# # 14   MaximumLatitude
# # 15   OffsetLatitude
# # 16   CenterOfGravityLatitudeSE
# # 17   CenterOfGravityLongitude
# # 18   MinimumLongitude
# # 19   MaximumLongitude
# # 20   OffsetLongitude
# # 21   CenterOfGravityLongitudeSE
# # 22   CenterOfGravityDepth
# # 23   MinimumDepth
# # 24   MaximumDepth
# # 25   OffsetDepth
# # 26   CenterOfGravityDepthSE

        # Get the reference system defined for the region in datasets
        #layercode_sr = dataset_srs[layercode_georef]
        layercode_sr = arcpy.SpatialReference(layercode_georef)
        arcpy.env.outputCoordinateSystem = layercode_sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        # Delete after last use
        del layercode_georef, layercode_sr

        arcpy.env.cellSize = cellsize; del cellsize

        # Region Raster Mask
        layercode_raster_mask = os.path.join(RegionGDB, f"{layercode}_Raster_Mask")

        # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
        arcpy.env.extent = arcpy.Describe(layercode_raster_mask).extent
        arcpy.env.mask = layercode_raster_mask
        arcpy.env.snapRaster = layercode_raster_mask
        del layercode_raster_mask

        # region abbreviated path
        layercode_folder = os.path.join(IMAGE_DIRECTORY, layercode); del IMAGE_DIRECTORY

        # Template Indicators Table
        template_indicators = os.path.join(RegionGDB, f"_Template_Indicators")

        # Region Indicators
        layercode_indicators = os.path.join(RegionGDB, f"{layercode}_Indicators")

        # Region Bathymetry
        layercode_bathymetry = os.path.join(RegionGDB, f"{layercode}_Bathymetry")

        # Region Latitude
        layercode_latitude = os.path.join(RegionGDB, f"{layercode}_Latitude")

        # Region Longitude
        layercode_longitude = os.path.join(RegionGDB, f"{layercode}_Longitude")

        # Region CVS Table
        layercode_csv_table = os.path.join(RegionGDB, layercode_csv_table)

        # Execute CreateTable
        arcpy.management.CreateTable(RegionGDB, f"{layercode}_Indicators", template_indicators, "")
        msg = arcpy.GetMessages()
        msg = ">---> {0}".format(msg.replace('\n', '\n>-----> '))
        logFile(log_file, msg); del msg

        del template_indicators, layercode

        # Get a disctionary of species and common names from the
        # Dictionary of species and common names that are in the tables
        layercode_unique_species_common_name_dict = unique_fish_dict(layercode_csv_table)
        del layercode_csv_table

        #print( layercode_unique_species_common_name_dict )
        #print("Is the")

        # Start with empty row_values list of list
        row_values = []

        # Loop through dictionary
        for layercode_unique_specie in layercode_unique_species_common_name_dict:
            # Speices folders do not include the '.' that can be a part
            # of the name, so remove
            layercode_unique_specie_dir = layercode_unique_specie.replace('(','').replace(')','')
            # Species
            Species = layercode_unique_specie[:]
            # The common name is the value in the dictionary
            CommonName = layercode_unique_species_common_name_dict[layercode_unique_specie][0]
            #print(CommonName)
            CoreSpecies = layercode_unique_species_common_name_dict[layercode_unique_specie][1]
            #print(CoreSpecies)

            msg = ">---> Species: {0}, Common Name: {1}".format(Species, CommonName)
            logFile(log_file, msg); del msg

            layercode_unique_specie_dir = os.path.join(layercode_folder, layercode_unique_specie_dir)

            msg = ">---> Processing Biomass Rasters"
            logFile(log_file, msg); del msg

            arcpy.env.workspace = layercode_unique_specie_dir; del layercode_unique_specie_dir

            biomassRasters = arcpy.ListRasters("*.tif")

            # ###--->>> This is to get a median biomass value for all years
            biomassBigArray = np.array([])
            for biomassRaster in sorted(biomassRasters):
                # Get maximumBiomass value to filter out "zero" rasters
                maximumBiomass = float(arcpy.management.GetRasterProperties(biomassRaster,"MAXIMUM").getOutput(0))
                # If maximumBiomass greater than zero, then process raster
                if maximumBiomass > 0.0:
                    # Use Raster To NumPy Array
                    biomassArray = arcpy.RasterToNumPyArray(biomassRaster, nodata_to_value=np.nan)
                    # Set zero and smaller values to NaN
                    biomassArray[biomassArray <= 0.0] = np.nan
                    # make the biomass arrays one dimensional
                    flatBiomassArray = biomassArray.flatten(); del biomassArray
                    # Remove NaN values from flatten (1-D) array
                    flatBiomassArray = flatBiomassArray[~np.isnan(flatBiomassArray)]
                    # Append Yearly Flatten Biomass Array to the big array (for all years)
                    biomassBigArray = np.append(biomassBigArray, flatBiomassArray)

                del biomassRaster, maximumBiomass
            # After processing all years, get the median value
            medianBiomass  = np.median(flatBiomassArray); del flatBiomassArray
            del biomassBigArray

            # ###--->>> This is to get a median biomass value for all years

            first_year = 9999
            # Process rasters
            for biomassRaster in sorted(biomassRasters):
                # Get year from raster name
                Year = int(biomassRaster[-8:-4])

                msg = ">-----> Processing {0} Biomass Raster".format(biomassRaster)
                logFile(log_file, msg); del msg

                # Get maximumBiomass value to filter out "zero" rasters
                maximumBiomass = float(arcpy.management.GetRasterProperties(biomassRaster,"MAXIMUM").getOutput(0))

                msg = ">-------> Biomass Raster Maximum: {0}".format(maximumBiomass)
                logFile(log_file, msg); del msg


                # If maximumBiomass greater than zero, then process raster
                if maximumBiomass > 0.0:
                    msg = ">-------> Calculating indicators"
                    logFile(log_file, msg); del msg

                    # Test is for first year
                    if Year < first_year:
                        first_year = Year

                # ###--->>> Biomass Start

                    #biomassArray = arcpy.RasterToNumPyArray(masked_biomass_raster, nodata_to_value=np.nan)
                    biomassArray = arcpy.RasterToNumPyArray(biomassRaster, nodata_to_value=np.nan)
                    biomassArray[biomassArray <= 0.0] = np.nan

                    #arcpy.management.Delete(masked_biomass_raster)
                    #del masked_biomass_raster

                    #sumWtCpue = sum of all wtcpue values (get this from biomassRaster stats??)
                    sumBiomassArray = np.nansum(biomassArray)

                    #msg = ">-------> sumBiomassArray: {0}".format(sumBiomassArray)
                    #logFile(log_file, msg); del msg


                    #msg = ">-------> biomassArray non-nan count: {0}".format(np.count_nonzero(~np.isnan(biomassArray)))
                    #logFile(log_file, msg); del msg

                # ###--->>> Biomass End

                # ###--->>> Latitude Start
                    #latitudeArray = arcpy.RasterToNumPyArray(masked_latitude_raster, nodata_to_value = np.nan)
                    #arcpy.management.Delete(masked_latitude_raster)
                    #del masked_latitude_raster

                    # Latitude
                    latitudeArray = arcpy.RasterToNumPyArray(layercode_latitude, nodata_to_value=np.nan)
                    #print(latitudeArray.shape)
                    latitudeArray[np.isnan(biomassArray)] = np.nan
                    #print(latitudeArray.shape)

                    msg = ">-------> latitudeArray non-nan count: {0:,d}".format(np.count_nonzero(~np.isnan(latitudeArray)))
                    logFile(log_file, msg); del msg


                    msg = ">-------> Latitude Min: {0}".format(np.nanmin(latitudeArray))
                    logFile(log_file, msg); del msg

                    msg = ">-------> Latitude Max: {0}".format(np.nanmax(latitudeArray))
                    logFile(log_file, msg); del msg


                    # make the biomass and latitude arrays one dimensional

                    flatBiomassArray = biomassArray.flatten()

                    flatLatitudeArray = latitudeArray.flatten()

                    # latsInds is an array of indexes representing the sort

                    latsInds = flatLatitudeArray.argsort()

                    # sort biomass and latitude arrays by lat sorted index

                    sortedBiomassArray = flatBiomassArray[latsInds]
                    sortedLatitudeArray = flatLatitudeArray[latsInds]

                    # calculate the cumulative sum of the sorted biomass values

                    sortedBiomassArrayCumSum = np.nancumsum(sortedBiomassArray)

                    # quantile is cumulative sum value divided by total biomass

                    sortedBiomassArrayQuantile = sortedBiomassArrayCumSum / np.nansum(flatBiomassArray)

                    # find the difference between 0.95 and each cumulative sum value ... asbolute value gives the closest distance

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.95)

                    # find the index of the smallest difference

                    minIndex = diffArray.argmin()

                    # get the lat at that index

                    #maxLat = sortedLatitudeArray[minIndex]
                    MaximumLatitude = sortedLatitudeArray[minIndex]

                    # do the same for 0.05

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.05)

                    minIndex = diffArray.argmin()

                    #minLat = sortedLatitudeArray[minIndex]
                    MinimumLatitude = sortedLatitudeArray[minIndex]

                    del sortedBiomassArrayCumSum, sortedBiomassArrayQuantile, diffArray, minIndex
                    del sortedLatitudeArray, sortedBiomassArray, flatBiomassArray
                    del latsInds, flatLatitudeArray

                    weightedLatitudeArray = np.multiply(biomassArray, latitudeArray)

                    sumWeightedLatitudeArray = np.nansum(weightedLatitudeArray)

                    #msg = ">-------> Sum Weighted Latitude: {0}".format(sumWeightedLatitudeArray)
                    #logFile(log_file, msg); del msg


                    CenterOfGravityLatitude = sumWeightedLatitudeArray / sumBiomassArray

                    if Year == first_year:
                        first_year_offset_latitude = CenterOfGravityLatitude

                    OffsetLatitude = CenterOfGravityLatitude - first_year_offset_latitude

                    weightedLatitudeArrayVariance = np.nanvar(weightedLatitudeArray)
                    weightedLatitudeArrayCount = np.count_nonzero(~np.isnan(weightedLatitudeArray))

                    CenterOfGravityLatitudeSE = math.sqrt(weightedLatitudeArrayVariance) / math.sqrt(weightedLatitudeArrayCount)

                    del weightedLatitudeArrayVariance, weightedLatitudeArrayCount

                    #msg = ">-------> Center of Gravity Latitude: {0}".format(round(CenterOfGravityLatitude,6))
                    msg = ">-------> Center of Gravity Latitude: {0}".format(CenterOfGravityLatitude)
                    logFile(log_file, msg); del msg


                    msg = ">-------> Minimum Latitude (5th Percentile): {0}".format(MinimumLatitude)
                    logFile(log_file, msg); del msg


                    msg = ">-------> Maximum Latitude (95th Percentile): {0}".format(MaximumLatitude)
                    logFile(log_file, msg); del msg


                    msg = ">-------> Offset Latitude: {0}".format(OffsetLatitude)
                    logFile(log_file, msg); del msg


                    msg = ">-------> Center of Gravity Latitude Standard Error: {0}".format(CenterOfGravityLatitudeSE)
                    logFile(log_file, msg); del msg


                    del latitudeArray, weightedLatitudeArray, sumWeightedLatitudeArray

                # ###--->>> Latitude End

                # ###--->>> Longitude Start
                    #longitudeArray = arcpy.RasterToNumPyArray(masked_longitude_raster, nodata_to_value = np.nan)
                    #arcpy.management.Delete(masked_longitude_raster)
                    #del masked_longitude_raster

                    # Longitude
                    # Doesn't work for International Date Line
                    #longitudeArray = arcpy.RasterToNumPyArray(layercode_longitude, nodata_to_value=np.nan)
                    #longitudeArray[np.isnan(biomassArray)] = np.nan

                    # For issue of international date line
                    # Added/Modified by JFK June 15, 2022
                    longitudeArray = arcpy.RasterToNumPyArray(layercode_longitude, nodata_to_value=np.nan)

                    longitudeArray = np.mod(longitudeArray, 360.0)

                    longitudeArray[np.isnan(biomassArray)] = np.nan

                    # make the biomass and latitude arrays one dimensional

                    flatBiomassArray = biomassArray.flatten()

                    flatLongitudeArray = longitudeArray.flatten()

                    # longsInds is an array of indexes representing the sort

                    longsInds = flatLongitudeArray.argsort()

                    # sort biomass and latitude arrays by long sorted index

                    sortedBiomassArray = flatBiomassArray[longsInds]
                    sortedLongitudeArray = flatLongitudeArray[longsInds]

                    # calculate the cumulative sum of the sorted biomass values

                    sortedBiomassArrayCumSum = np.nancumsum(sortedBiomassArray)

                    # quantile is cumulative sum value divided by total biomass

                    sortedBiomassArrayQuantile = sortedBiomassArrayCumSum / np.nansum(flatBiomassArray)

                    # find the difference between 0.95 and each cumulative sum value ... asbolute value gives the closest distance

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.95)

                    # find the index of the smallest difference

                    minIndex = diffArray.argmin()

                    # get the lat at that index

                    MaximumLongitude = sortedLongitudeArray[minIndex]

                    # do the same for 0.05

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.05)

                    minIndex = diffArray.argmin()

                    MinimumLongitude = sortedLongitudeArray[minIndex]

                    del sortedBiomassArrayCumSum, sortedBiomassArrayQuantile, diffArray, minIndex
                    del sortedLongitudeArray, sortedBiomassArray, flatBiomassArray
                    del longsInds, flatLongitudeArray

                    weightedLongitudeArray = np.multiply(biomassArray, longitudeArray)

                    sumWeightedLongitudeArray = np.nansum(weightedLongitudeArray)

                    CenterOfGravityLongitude = sumWeightedLongitudeArray / sumBiomassArray

                    if Year == first_year:
                        first_year_offset_longitude = CenterOfGravityLongitude

                    OffsetLongitude = CenterOfGravityLongitude - first_year_offset_longitude

                    weightedLongitudeArrayVariance = np.nanvar(weightedLongitudeArray)
                    weightedLongitudeArrayCount = np.count_nonzero(~np.isnan(weightedLongitudeArray))

                    CenterOfGravityLongitudeSE = math.sqrt(weightedLongitudeArrayVariance) / math.sqrt(weightedLongitudeArrayCount)

                    del weightedLongitudeArrayVariance, weightedLongitudeArrayCount

                    # Convert 360 back to 180
                    # Added/Modified by JFK June 15, 2022
                    CenterOfGravityLongitude = np.mod(CenterOfGravityLongitude - 180.0, 360.0) - 180.0
                    MinimumLongitude = np.mod(MinimumLongitude - 180.0, 360.0) - 180.0
                    MaximumLongitude = np.mod(MaximumLongitude - 180.0, 360.0) - 180.0

                    #msg = ">-------> Sum Weighted Longitude: {0}".format(sumWeightedLongitudeArray)
                    #logFile(log_file, msg); del msg


                    #msg = ">-------> Center of Gravity Longitude: {0}".format(round(CenterOfGravityLongitude,6))
                    msg = ">-------> Center of Gravity Longitude: {0}".format(CenterOfGravityLongitude)
                    logFile(log_file, msg); del msg


                    #msg = ">-------> Center of Gravity Longitude: {0}".format(np.mod(CenterOfGravityLongitude - 180.0, 360.0) -180.0)
                    #logFile(log_file, msg); del msg


                    msg = ">-------> Minimum Longitude (5th Percentile): {0}".format(MinimumLongitude)
                    logFile(log_file, msg); del msg


                    msg = ">-------> Maximum Longitude (95th Percentile): {0}".format(MaximumLongitude)
                    logFile(log_file, msg); del msg


                    msg = ">-------> Offset Longitude: {0}".format(OffsetLongitude)
                    logFile(log_file, msg); del msg


                    msg = ">-------> Center of Gravity Longitude Standard Error: {0}".format(CenterOfGravityLongitudeSE)
                    logFile(log_file, msg); del msg


                    del longitudeArray, weightedLongitudeArray, sumWeightedLongitudeArray

                # ###--->>> Center of Gravity Depth Start
                    # ###--->>> Bathymetry (Depth)

                    # Bathymetry
                    bathymetryArray = arcpy.RasterToNumPyArray(layercode_bathymetry, nodata_to_value=np.nan)
                    # If biomass cells are Null, make bathymetry cells Null as well
                    bathymetryArray[np.isnan(biomassArray)] = np.nan
                    # For bathymetry values zero are larger, make zero
                    bathymetryArray[bathymetryArray >= 0.0] = 0.0

                    #msg = ">-------> bathymetryArray non-nan count: {0}".format(np.count_nonzero(~np.isnan(bathymetryArray)))
                    #logFile(log_file, msg); del msg

                    #msg = ">-------> Bathymetry Min: {0}".format(np.nanmin(bathymetryArray))
                    #logFile(log_file, msg); del msg

                    #msg = ">-------> Bathymetry Max: {0}".format(np.nanmax(bathymetryArray))
                    #logFile(log_file, msg); del msg

                    # make the biomass and latitude arrays one dimensional

                    flatBiomassArray = biomassArray.flatten()

                    flatBathymetryArray = bathymetryArray.flatten()

                    # bathyInds is an array of indexes representing the sort

                    bathyInds = flatBathymetryArray.argsort()

                    # sort biomass and latitude arrays by lat sorted index

                    sortedBiomassArray = flatBiomassArray[bathyInds]
                    sortedBathymetryArray = flatBathymetryArray[bathyInds]

                    # calculate the cumulative sum of the sorted biomass values

                    sortedBiomassArrayCumSum = np.nancumsum(sortedBiomassArray)

                    # quantile is cumulative sum value divided by total biomass

                    sortedBiomassArrayQuantile = sortedBiomassArrayCumSum/np.nansum(flatBiomassArray)

                    # find the difference between 0.95 and each cumulative sum
                    # value ... asbolute value gives the closest distance

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.95)

                    # find the index of the smallest difference

                    minIndex = diffArray.argmin()

                    # get the lat at that index

                    #maxLat = sortedBathymetryArray[minIndex]
                    MaximumDepth = sortedBathymetryArray[minIndex]

                    # do the same for 0.05

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.05)

                    minIndex = diffArray.argmin()

                    #minLat = sortedBathymetryArray[minIndex]
                    MinimumDepth = sortedBathymetryArray[minIndex]

                    del sortedBiomassArrayCumSum, sortedBiomassArrayQuantile, diffArray, minIndex
                    del sortedBathymetryArray, sortedBiomassArray, flatBiomassArray
                    del bathyInds, flatBathymetryArray

                    weightedBathymetryArray = np.multiply(biomassArray, bathymetryArray)

                    sumWeightedBathymetryArray = np.nansum(weightedBathymetryArray)

                    msg = ">-------> Sum Weighted Bathymetry: {0}".format(sumWeightedBathymetryArray)
                    logFile(log_file, msg); del msg

                    #
                    CenterOfGravityDepth = sumWeightedBathymetryArray / sumBiomassArray

                    if Year == first_year:
                        first_year_offset_depth = CenterOfGravityDepth

                    OffsetDepth = CenterOfGravityDepth - first_year_offset_depth

                    weightedBathymetryArrayVariance = np.nanvar(weightedBathymetryArray)
                    weightedBathymetryArrayCount = np.count_nonzero(~np.isnan(weightedBathymetryArray))

                    CenterOfGravityDepthSE = math.sqrt(weightedBathymetryArrayVariance) / math.sqrt(weightedBathymetryArrayCount)

                    del weightedBathymetryArrayVariance, weightedBathymetryArrayCount

                    msg = ">-------> Center of Gravity Depth: {0}".format(CenterOfGravityDepth)
                    logFile(log_file, msg); del msg


                    msg = ">-------> Minimum Depth (5th Percentile): {0}".format(MinimumDepth)
                    logFile(log_file, msg); del msg


                    msg = ">-------> Maximum Depth (95th Percentile): {0}".format(MaximumDepth)
                    logFile(log_file, msg); del msg


                    msg = ">-------> Offset Depth: {0}".format(OffsetDepth)
                    logFile(log_file, msg); del msg


                    msg = ">-------> Center of Gravity Depth Standard Error: {0}".format(CenterOfGravityDepthSE)
                    logFile(log_file, msg); del msg


                    del bathymetryArray, weightedBathymetryArray
                    del sumWeightedBathymetryArray, biomassRaster
                    del biomassArray, sumBiomassArray

                # ###--->>> Center of Gravity Depth End

                elif maximumBiomass == 0.0:
                    CenterOfGravityLatitude = None
                    MinimumLatitude = None
                    MaximumLatitude = None
                    OffsetLatitude = None
                    CenterOfGravityLatitudeSE = None
                    CenterOfGravityLongitude = None
                    MinimumLongitude = None
                    MaximumLongitude = None
                    OffsetLongitude = None
                    CenterOfGravityLongitudeSE = None
                    CenterOfGravityDepth = None
                    MinimumDepth = None
                    MaximumDepth = None
                    OffsetDepth = None
                    CenterOfGravityDepthSE = None
                else:
                    msg = 'Something wrong with biomass raster'
                    logFile(log_file, msg); del msg

                row = [RegionCode,
                       Region,
                       ModelRegion,
                       DisMapRegionCode,
                       DisMapSeasonCode,
                       Species,
                       CommonName,
                       CoreSpecies,
                       Year,
                       ProductName,
                       ProductCode,
                       SummaryProduct,
                       CenterOfGravityLatitude,
                       MinimumLatitude,
                       MaximumLatitude,
                       OffsetLatitude,
                       CenterOfGravityLatitudeSE,
                       CenterOfGravityLongitude,
                       MinimumLongitude,
                       MaximumLongitude,
                       OffsetLongitude,
                       CenterOfGravityLongitudeSE,
                       CenterOfGravityDepth,
                       MinimumDepth,
                       MaximumDepth,
                       OffsetDepth,
                       CenterOfGravityDepthSE,
                       ]
                # Append to list
                row_values.append(row)
                del row

                # Clean-up
                del maximumBiomass

                del Year
                del CenterOfGravityLatitude, MinimumLatitude, MaximumLatitude
                del OffsetLatitude, CenterOfGravityLatitudeSE
                del CenterOfGravityLongitude, MinimumLongitude, MaximumLongitude
                del OffsetLongitude, CenterOfGravityLongitudeSE
                del CenterOfGravityDepth, MinimumDepth, MaximumDepth
                del OffsetDepth, CenterOfGravityDepthSE

            del biomassRasters, medianBiomass, layercode_unique_specie
            del first_year
            del first_year_offset_latitude, first_year_offset_longitude, first_year_offset_depth

        del Species, CommonName, CoreSpecies, layercode_folder
        del RegionCode, Region, ModelRegion, DisMapRegionCode, DisMapSeasonCode
        del ProductName, ProductCode, SummaryProduct
        del layercode_bathymetry, layercode_unique_species_common_name_dict, np, math
        del layercode_latitude, layercode_longitude

        msg = ">-----> Inserting records into the table"
        logFile(log_file, msg); del msg

        PrintRowContent = False
        if PrintRowContent:
            for row_value in row_values:
                #print(row_value)
                # LayerCode
                msg =  f"OARegionCode: {row_value[0]}" + "\n"
                msg += f"OARegion: {row_value[1]}" + "\n"
                msg += f"ModelRegion: {row_value[2]}" + "\n"
                msg += f"DisMapRegionCode: {row_value[3]}" + "\n"
                msg += f"DisMapSeasonCode: {row_value[4]}" + "\n"
                msg += f"Species: {row_value[5]}" + "\n"
                msg += f"CommonName: {row_value[6]}" + "\n"
                msg += f"CoreSpecies: {row_value[7]}" + "\n"
                msg += f"Year: {row_value[8]}" + "\n"
                msg += f"ProductName: {row_value[9]}" + "\n"
                msg += f"ProductCode: {row_value[10]}" + "\n"
                msg += f"SummaryProduct: {row_value[11]}" + "\n"
                msg += f"CenterOfGravityLatitude: {row_value[12]}" + "\n"
                msg += f"MinimumLatitude: {row_value[13]}" + "\n"
                msg += f"MaximumLatitude: {row_value[14]}" + "\n"
                msg += f"OffsetLatitude: {row_value[15]}" + "\n"
                msg += f"CenterOfGravityLatitudeSE: {row_value[16]}" + "\n"
                msg += f"CenterOfGravityLongitude: {row_value[17]}" + "\n"
                msg += f"MinimumLongitude: {row_value[18]}" + "\n"
                msg += f"MaximumLongitude: {row_value[19]}" + "\n"
                msg += f"OffsetLongitude: {row_value[20]}" + "\n"
                msg += f"CenterOfGravityLongitudeSE: {row_value[21]}" + "\n"
                msg += f"CenterOfGravityDepth: {row_value[22]}" + "\n"
                msg += f"MinimumDepth: {row_value[23]}" + "\n"
                msg += f"MaximumDepth: {row_value[24]}" + "\n"
                msg += f"OffsetDepth: {row_value[25]}" + "\n"
                msg += f"enterOfGravityDepthSE: {row_value[26]}" + "\n"
                logFile(log_file, msg); del msg
                if row_value: del row_value
        del PrintRowContent

        # This gets a list of fields in the table
        fields = [f.name for f in arcpy.ListFields(layercode_indicators) if f.name != 'OBJECTID']
        #print(fields)

        # Open an InsertCursor
        cursor = arcpy.da.InsertCursor(layercode_indicators, fields)

        # Insert new rows into the table
        for row in row_values:
            try:
                row = [None if x != x else x for x in row]
                cursor.insertRow(row)
                del row
            except Exception as e:
                import sys
                # Capture all other errors
                #print(sys.exc_info()[2].tb_lineno)
                msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
                logFile(log_file.replace(".log", " ERROR.log"), msg); del msg

        #print(row_values)
        # Delete cursor object
        del cursor, row_values, fields

# #    # Add some metadata
# #    years_md = unique_years(layercode_indicators)
# #
# #    layercode_indicators_md = md.Metadata(layercode_indicators)
# #    layercode_indicators_md.synchronize('ACCESSED', 1)
# #    layercode_indicators_md.title = "{0} Indicators {1}".format(region.replace('-',' to '), DateCode)
# #    layercode_indicators_md.tags = "{0}, {1} to {2}".format(geographic_regions[layercode], min(years_md), max(years_md))
# #    layercode_indicators_md.save()
# #    del layercode_indicators_md, years_md
# #    del layercode, layercode_indicators, DateCode

        del RegionGDB

        #Final benchmark for the region.
        msg = f"ENDING REGION {region} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        #Final benchmark
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {region}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, region

        del start_time, end_time, elapse_time

        # return layercode_indicators
        del layercode_indicators

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpCreateLayerCodeBathymetry(args):
    """mp Create Region Bathymetry"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        start_time = time()

        dataset, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        print(msg)
        logFile(log_file, msg); del msg

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset[0]} {SoftwareEnvironmentLevel} Scratch.gdb")

        RegionGDB = os.path.join(ScratchFolder, f"{dataset[0]} {SoftwareEnvironmentLevel}.gdb")
        del SoftwareEnvironmentLevel
        del ScratchFolder

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = RegionGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = RegionScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Set the compression environment to LZ77
        arcpy.env.compression = "LZ77"

        # Assigning variables from items in the chosen table list
        layercode = dataset[0]
        region = dataset[1]
        #layercode_csv_table = dataset[2]
        #layercode_shape = dataset[3]
        #layercode_boundary = dataset[4]
        layercode_georef = dataset[5]
        #layercode_contours = dataset[6]
        cellsize = dataset[7]
        del dataset

        # Write a message to the log file
        msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        msg = f'> Generating {region} Bathymetry Rasters'
        logFile(log_file, msg); del msg

        # Get the reference system defined for the region in datasets
        #layercode_sr = dataset_srs[layercode_georef]
        layercode_sr = arcpy.SpatialReference(layercode_georef)
        arcpy.env.outputCoordinateSystem = layercode_sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        # Delete after last use
        del layercode_georef, layercode_sr

        # Set cell size
        arcpy.env.cellSize = cellsize

        # Region datasets
        layercode_survey_area = f"{layercode}_Survey_Area"
        layercode_fish_net = f"{layercode}_Fish_Net"
        layercode_raster_mask = f"{layercode}_Raster_Mask"
        layercode_lat_long = f"{layercode}_Lat_Long"
        layercode_latitude = f"{layercode}_Latitude"
        layercode_longitude = f"{layercode}_Longitude"

        #BathymetryGDB = os.path.join(BASE_DIRECTORY, "Bathymetry.gdb")
        layercode_bathymetry = f"{layercode}_Bathymetry"
        bathymetry = os.path.join(RegionScratchGDB, f"{layercode_bathymetry}")
        #del BASE_DIRECTORY, BathymetryGDB

        msg = f"#-> Feature to Raster Conversion using {layercode_survey_area} to create Raster Mask {layercode_raster_mask}"
        logFile(log_file, msg); del msg
        # Change mask to the region shape to create the raster mask
        arcpy.env.mask = layercode_survey_area
        arcpy.FeatureToRaster_conversion(layercode_survey_area, "ID", layercode_raster_mask, cellsize)

        addMetadata(layercode_raster_mask, log_file)

      # Resets a specific environment setting to its default
        arcpy.ClearEnvironment("mask")

        msg = f"#-> Point to Raster Conversion using {layercode_lat_long} to create {layercode_longitude}"
        logFile(log_file, msg); del msg
        # Process: Point to Raster Longitude
        arcpy.env.cellSize = cellsize
        arcpy.env.extent = arcpy.Describe(layercode_raster_mask).extent
        arcpy.env.mask = layercode_raster_mask
        arcpy.env.snapRaster = layercode_raster_mask

        layercode_longitude_tmp = os.path.join(RegionScratchGDB, f"{layercode_longitude}_tmp")

        arcpy.conversion.PointToRaster(layercode_lat_long, "Longitude", layercode_longitude_tmp, "MOST_FREQUENT", "NONE", cellsize)

        if arcpy.CheckExtension("Spatial") == "Available":
                arcpy.CheckOutExtension("Spatial")
        else:
            # raise a custom exception
            raise LicenseError

        msg = f"#-> Extract by Mask to create {layercode_longitude}"
        logFile(log_file, msg); del msg
        # Execute ExtractByMask
        outExtractByMask = arcpy.sa.ExtractByMask(layercode_longitude_tmp, layercode_raster_mask, "INSIDE", layercode_longitude_tmp)

        arcpy.CheckInExtension("Spatial")

        # Save the output
        outExtractByMask.save(layercode_longitude)
        del outExtractByMask

        arcpy.management.Delete(layercode_longitude_tmp)
        del layercode_longitude_tmp

        addMetadata(layercode_longitude, log_file)

        layercode_latitude_tmp = os.path.join(RegionScratchGDB, f"{layercode_latitude}_tmp")

        msg = f"#-> Point to Raster Conversion using {layercode_lat_long} to create {layercode_latitude}"
        logFile(log_file, msg); del msg
        # Process: Point to Raster Latitude
        arcpy.conversion.PointToRaster(layercode_lat_long, "Latitude", layercode_latitude_tmp, "MOST_FREQUENT", "NONE", cellsize)

        msg = f"#-> Extract by Mask to create {layercode_latitude}"
        logFile(log_file, msg); del msg
        # Execute ExtractByMask
        outExtractByMask = arcpy.sa.ExtractByMask(layercode_latitude_tmp, layercode_raster_mask, "INSIDE", layercode_latitude_tmp)

        # Save the output
        outExtractByMask.save(layercode_latitude)
        del outExtractByMask

        arcpy.management.Delete(layercode_latitude_tmp)
        del layercode_latitude_tmp

        addMetadata(layercode_latitude, log_file)

        msg = f"#-> Zonal Statistics using {layercode_fish_net} and {os.path.basename(bathymetry)} to create {layercode_bathymetry}"
        logFile(log_file, msg); del msg
        # Execute ZonalStatistics
        outZonalStatistics = arcpy.sa.ZonalStatistics(layercode_fish_net, "OID", bathymetry, "MEDIAN", "NODATA")

        # Save the output
        outZonalStatistics.save(layercode_bathymetry)

        del outZonalStatistics

        # Resets a specific environment setting to its default
        arcpy.ClearEnvironment("cellSize")
        arcpy.ClearEnvironment("extent")
        arcpy.ClearEnvironment("mask")
        arcpy.ClearEnvironment("snapRaster")

        del RegionScratchGDB
        del log_file_folder, RegionGDB
        del layercode, cellsize
        del layercode_survey_area, layercode_fish_net, layercode_raster_mask
        del layercode_lat_long, layercode_latitude, layercode_longitude, bathymetry
        del layercode_bathymetry

        #Final benchmark for the region.
        msg = f"ENDING REGION {region} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {region}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, region

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except LicenseError:
        import sys
        msg = f"Spatial Analyst license is not available"
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file.replace(".log", " ERROR.log"), msg); del msg
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpCreateLayerCodeFishnets(args):
    """mp Create Region Bathymetry"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        start_time = time()

        dataset, REGION_SHAPEFILE_DIRECTORY, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr, log_file_folder

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        #oaregioncode     = dataset[0]
        #oaregion         = dataset[1]
        layercode        = dataset[4]
        #region           = dataset[9]
        #csvfile          = dataset[12][:-4].upper()
        geographicarea   = dataset[13]
        cellsize         = dataset[15]
        #coordinatesystem = dataset[14]
        #transformunit    = dataset[16]
# #      oaregioncode            = dataset[0]
# #      oaregion                = dataset[1]
# #      dismapregioncode        = dataset[2]
# #      dismapseasoncode        = dataset[3]
# #      layercode               = dataset[4]
# #      layername               = dataset[5]
# #      datecode                = dataset[6]
# #      distributionprojectname = dataset[7]
# #      distributionprojectcode = dataset[8]
# #      region                  = dataset[9]
# #      seasoncode              = dataset[10]
# #      summaryproduct          = dataset[11]
# #      csvfile                 = dataset[12]
# #      geographicarea          = dataset[13]
# #      coordinatesystem        = dataset[14]
# #      cellsize                = dataset[15]
# #      transformunit           = dataset[16]
# #      timezone                = dataset[17]
        del dataset

        RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

        RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")
        del SoftwareEnvironmentLevel, ScratchFolder

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = RegionGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = RegionScratchGDB; del RegionScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
        msg = f'> Generating {layercode} Fishnet Dataset'
        logFile(log_file, msg); del msg

        # Set the output coordinate system to what is needed for the
        # DisMAP project
        geographicarea_sr = os.path.join(REGION_SHAPEFILE_DIRECTORY, layercode, f"{geographicarea}.prj")
        #print(geographicarea_sr)
        del geographicarea, REGION_SHAPEFILE_DIRECTORY

        layercode_sr = arcpy.SpatialReference(geographicarea_sr)
        del geographicarea_sr

        arcpy.env.outputCoordinateSystem = layercode_sr

        arcpy.env.cellSize = cellsize

        layercode_survey_area = os.path.join(RegionGDB, f"{layercode}_Survey_Area")
        layercode_fish_net = os.path.join(RegionGDB, f"{layercode}_Fish_Net")
        layercode_lat_long = os.path.join(RegionGDB, f"{layercode}_Lat_Long")

        # Get Extent
        extent = arcpy.Describe(layercode_survey_area).extent
        X_Min, Y_Min, X_Max, Y_Max = extent.XMin, extent.YMin, extent.XMax, extent.YMax
        del extent
        # print("X_Min: {0}, Y_Min: {1}, X_Max: {2}, Y_Max: {3}\n".format(X_Min, Y_Min, X_Max, Y_Max))

        msg = f"X_Min: {X_Min}\n"
        msg = msg + f"Y_Min: {Y_Min}\n"
        msg = msg + f"X_Max: {X_Max}\n"
        msg = msg + f"Y_Max: {Y_Max}\n"
        logFile(log_file, msg); del msg

        # A list of coordinate pairs
        pointList = [[X_Min, Y_Min], [X_Min, Y_Max], [X_Max, Y_Max]]

        # Create an empty Point object
        point = arcpy.Point()

        # A list to hold the PointGeometry objects
        pointGeometryList = []

        # For each coordinate pair, populate the Point object and create a new
        # PointGeometry object
        for pt in pointList:
            point.X = pt[0]
            point.Y = pt[1]

            pointGeometry = arcpy.PointGeometry(point, layercode_sr)
            pointGeometryList.append(pointGeometry)
            del pt, pointGeometry

        #print(pointList)
        # Delete after last use
        del pointList, point, layercode_sr

        # Create a copy of the PointGeometry objects, by using pointGeometryList as
        # input to the CopyFeatures tool.
        layercode_points = os.path.join(RegionGDB, f"{layercode}_Points")
        arcpy.management.CopyFeatures(pointGeometryList, layercode_points)
        del pointGeometryList, RegionGDB

        # Add metadata
        addMetadata(layercode_points, log_file)

        # Clearup after last use
        del layercode_points

        # CreateFishnet(out_feature_class, origin_coord, y_axis_coord, cell_width, cell_height, number_rows, number_columns, {corner_coord}, {labels}, {template}, {geometry_type})
        # Set the origin of the fishnet
        originCoordinate = f'{X_Min} {Y_Min}'
        # Set the orientation
        yAxisCoordinate = f'{X_Min} {Y_Max}'
        # Enter 0 for width and height - these values will be calcualted by the tool
        cellSizeWidth = f'{cellsize}'
        cellSizeHeight = f'{cellsize}'
        # Number of rows and columns together with origin and opposite corner
        # determine the size of each cell
        numRows =  ''
        numColumns = ''
        oppositeCoorner = f'{X_Max} {Y_Max}'
        # Create a point label Dataset
        labels = 'NO_LABELS'
        # Extent is set by origin and opposite corner - no need to use a template fc
        templateExtent = f"{X_Min} {Y_Min} {X_Max} {Y_Max}"
        # Each output cell will be a polygon
        geometryType = 'POLYGON'
        #Coordinate_System = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        msg = f"> Create Fishnet with {cellSizeWidth} by {cellSizeHeight} cells"
        logFile(log_file, msg); del msg
        arcpy.management.CreateFishnet(layercode_fish_net, originCoordinate, yAxisCoordinate, cellSizeWidth, cellSizeHeight, numRows, numColumns, oppositeCoorner, labels, templateExtent, geometryType)

        del X_Min, Y_Min, X_Max, Y_Max
        del originCoordinate, yAxisCoordinate, cellSizeWidth
        del cellSizeHeight, numRows, numColumns, oppositeCoorner, labels
        del templateExtent, geometryType

# ###--->>> Select by location and trim
        msg = f"> Make Feature Layer for {layercode}_Fish_Net_Layer"
        logFile(log_file, msg); del msg
        layercode_fish_net_layer = arcpy.management.MakeFeatureLayer(layercode_fish_net, "{0}_Fish_Net_Layer".format(layercode))

        msg = f"> Select Layer by Location"
        logFile(log_file, msg); del msg
        #arcpy.management.SelectLayerByLocation(layercode_fish_net_layer, "HAVE_THEIR_CENTER_IN", layercode_survey_area, 0, "NEW_SELECTION", "INVERT") # WITHIN_A_DISTANCE, CONTAINS, INTERSECT, WITHIN, WITHIN_CLEMENTINI, HAVE_THEIR_CENTER_IN
        arcpy.management.SelectLayerByLocation(layercode_fish_net_layer, "WITHIN_A_DISTANCE", layercode_survey_area, 2 * cellsize, "NEW_SELECTION", "INVERT")

        msg = f"> Delete Features from {layercode}_Fish_Net_Layer"
        logFile(log_file, msg); del msg
        arcpy.management.DeleteFeatures(layercode_fish_net_layer)

        addMetadata(layercode_fish_net, log_file)

        msg = f"> Deleting {layercode}_Fish_Net_Layer"
        logFile(log_file, msg); del msg
        arcpy.management.Delete("{0}_Fish_Net_Layer".format(layercode))
        del layercode_fish_net_layer #, layercode_fish_net_label_layer

        msg = f"> Feature to Point using {os.path.basename(layercode_fish_net)} to create {os.path.basename(layercode_lat_long)}"
        logFile(log_file, msg); del msg
        #
        arcpy.management.FeatureToPoint(layercode_fish_net, layercode_lat_long, "CENTROID")

        msg = f"> Delete Field ORIG_FID from {os.path.basename(layercode_lat_long)}"
        logFile(log_file, msg); del msg
        # Execute DeleteField
        arcpy.management.DeleteField(layercode_lat_long, ['ORIG_FID'])

        # Resets a specific environment setting to its default
        arcpy.ClearEnvironment("cellSize")
        arcpy.ClearEnvironment("extent")
        arcpy.ClearEnvironment("mask")
        arcpy.ClearEnvironment("snapRaster")

        # Delete after last use
        del layercode_survey_area
        del layercode, cellsize
        del layercode_fish_net
        del layercode_lat_long

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpCreateSampleLocationPoints(args):
    """mp Create Region Sample LocationP oints"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        start_time = time()

        dataset, REGION_SHAPEFILE_DIRECTORY, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr, log_file_folder

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        #oaregioncode     = dataset[0]
        #oaregion         = dataset[1]
        layercode        = dataset[4]
        region           = dataset[9]
        #csvfile          = dataset[12][:-4].upper()
        geographicarea   = dataset[13]
        #coordinatesystem = dataset[14]
        #transformunit    = dataset[16]
# #      oaregioncode            = dataset[0]
# #      oaregion                = dataset[1]
# #      dismapregioncode        = dataset[2]
# #      dismapseasoncode        = dataset[3]
# #      layercode               = dataset[4]
# #      layername               = dataset[5]
# #      datecode                = dataset[6]
# #      distributionprojectname = dataset[7]
# #      distributionprojectcode = dataset[8]
# #      region                  = dataset[9]
# #      seasoncode              = dataset[10]
# #      summaryproduct          = dataset[11]
# #      csvfile                 = dataset[12]
# #      geographicarea          = dataset[13]
# #      coordinatesystem        = dataset[14]
# #      cellsize                = dataset[15]
# #      transformunit           = dataset[16]
# #      timezone                = dataset[17]
        del dataset

        RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

        del SoftwareEnvironmentLevel, ScratchFolder

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = RegionGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = RegionScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Set the output coordinate system to what is needed for the
        # DisMAP project
        geographicarea_sr = os.path.join(REGION_SHAPEFILE_DIRECTORY, layercode, f"{geographicarea}.prj")
        #print(geographicarea_sr)
        del REGION_SHAPEFILE_DIRECTORY, geographicarea

        sr = arcpy.SpatialReference(geographicarea_sr)
        #del geographicarea_sr

        arcpy.env.outputCoordinateSystem = sr
        #del sr

        msg = f'>-> Creating the {layercode} Sample Locations Dataset'
        logFile(log_file, msg); del msg

        layercodepath = os.path.join(RegionGDB, layercode)

        fields = [f.name for f in arcpy.ListFields(layercodepath) if f.name in ['Easting', 'Northing']]
        #for field in fields:
        #    print(field)
        if fields:
            x_coord, y_coord = 'Easting', 'Northing'
        else:
            x_coord, y_coord = 'Longitude', 'Latitude'
        del fields

        # Make XY Event  Layer
        my_events = arcpy.management.MakeXYEventLayer(layercodepath, x_coord, y_coord, "my_events", geographicarea_sr, "#")

        del x_coord, y_coord, sr, layercodepath, geographicarea_sr

        # Input Dataset
        sample_locations = os.path.join(RegionGDB, f"{layercode}_Sample_Locations")

        with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
            arcpy.conversion.ExportFeatures(in_features = my_events,
                                            out_features = sample_locations,
                                            where_clause = "",
                                            use_field_alias_as_name = "",
                                            field_mapping = "",
                                            sort_field = "")
        del RegionGDB, RegionScratchGDB
        # Clear the XY Event Layer from memory.
        arcpy.management.Delete(my_events)
        del my_events

        msg = f'>-> Adding field index in the {layercode}_Sample_Locations Dataset'
        logFile(log_file, msg); del msg

        # Add Attribute Index
        arcpy.AddIndex_management(sample_locations, ['Species', 'CommonName', 'SpeciesCommonName', 'Year'], f"{layercode}_SampleLocationsSpeciesIndex", "NON_UNIQUE", "NON_ASCENDING")

        result = arcpy.management.GetCount(sample_locations)
        msg = f">-> {layercode}_Sample_Locations has {result[0]:,d} records"
        logFile(log_file, msg); del msg
        del result

        # Add Metadata
        addMetadata(sample_locations, log_file)

        # Field Alias Dictionary
        field_alias = {
                       "OARegionCode"      : "OA Region Code",
                       "OARegion"          : "OA Region",
                       "LayerCode"         : "Layer Code",
                       "Region"            : "Region",
                       "SampleID"          : "Sample ID",
                       "Species"           : "Species",
                       "CommonName"        : "Common Name",
                       "SpeciesCommonName" : "Species (Common Name)",
                       "CommonNameSpecies" : "Common Name (Species)",
                       "CoreSpecies"       : "Core Species",
                       "Year"              : "Year",
                       "WTCPUE"            : "WTCPUE",
                       "MedianEstimate"    : "Median Estimate",
                       "AnalysisValue"     : "Analysis Value",
                       "TransformUnit"     : "Transform Unit",
                       "MeanEstimate"      : "Mean Estimate",
                       "Estimate5Percent"  : "Estimate 5 Percent",
                       "Estimate95Percent" : "Estimate 95 Percent",
                       "Stratum"           : "Stratum",
                       "StratumArea"       : "Stratum Area",
                       "Easting"           : "Easting (UTM)",
                       "Northing"          : "Northing (UTM)",
                       "Latitude"          : "Latitude (DD)",
                       "Longitude"         : "Longitude (DD)",
                       "Depth"             : "Depth",
                       "StdTime"           : "StdTime",
                      }

        # Alter Field Alias
        alterFieldAlias(sample_locations, field_alias, log_file)

        #
        del field_alias, sample_locations

        #Final benchmark for the region.
        msg = f"ENDING REGION {layercode} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {layercode}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)\n"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time, region

        del layercode

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

# ## Reads from the queue and does work
def mpCreateSpeciesRichnessRasters(args):
    """mp Create Core Species Richness Rasters"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        start_time = time()

        dataset, SoftwareEnvironmentLevel, ScratchFolder, \
        log_file_folder, IMAGE_DIRECTORY = args
        del args

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        RegionGDB = os.path.join(ScratchFolder, f"{dataset[0]} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset[0]} {SoftwareEnvironmentLevel} Scratch.gdb")

        del SoftwareEnvironmentLevel

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = RegionGDB

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = RegionScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        # Set the compression environment to LZ77
        arcpy.env.compression = "LZ77"

        # Assigning variables from items in the chosen table list
        layercode = dataset[0]
        region = dataset[1]
        #layercode_csv_table = dataset[2]
        #layercode_shape = dataset[3]
        #layercode_boundary = dataset[4]
        layercode_georef = dataset[5]
        #layercode_contours = dataset[6]
        cellsize = dataset[7]
        del dataset

        # Write a message to the log file
        msg = f"STARTING REGION {region} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        msg = f'> Generating {region} Biomass Rasters'
        logFile(log_file, msg); del msg

        # Get the reference system defined for the region in datasets
        layercode_sr = arcpy.SpatialReference(layercode_georef)
        arcpy.env.outputCoordinateSystem = layercode_sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

        # Delete after last use
        del layercode_georef, layercode_sr

        arcpy.env.cellSize = cellsize

        layercode_raster_mask = os.path.join(RegionGDB, f"{layercode}_Raster_Mask")

        # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
        arcpy.env.extent = arcpy.Describe(layercode_raster_mask).extent
        arcpy.env.mask = layercode_raster_mask
        arcpy.env.snapRaster = layercode_raster_mask
        del layercode_raster_mask











        #Final benchmark for the region.
        msg = f"ENDING REGION {region} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {region}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, region

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpHandlerCreateDisMapRegions(CreateRegionDisMapRegionsSequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        #start the clock
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        args = [CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder]
        datasets = generateDatasets(args)

        with arcpy.EnvManager(scratchWorkspace = ScratchFolder, workspace = ProjectGDB):
            wc = "_Sample_Locations"
            fcs = arcpy.ListFeatureClasses(f"*{wc}")
            datasets = [[r for r in group] for group in datasets if f"{group[4]}{wc}" in fcs]
            del wc, fcs

        for i in range(len(datasets)):
# #            oaregioncode            = datasets[i][0]
# #            oaregion                = datasets[i][1]
# #            dismapregioncode        = datasets[i][2]
# #            dismapseasoncode        = datasets[i][3]
            layercode               = datasets[i][4]
# #            layername               = datasets[i][5]
# #            datecode                = datasets[i][6]
# #            distributionprojectname = datasets[i][7]
# #            distributionprojectcode = datasets[i][8]
# #            region                  = datasets[i][9]
# #            seasoncode              = datasets[i][10]
# #            summaryproduct          = datasets[i][11]
# #            csvfile                 = datasets[i][12]
# #            geographicarea          = datasets[i][13]
# #            coordinatesystem        = datasets[i][14]
# #            cellsize                = datasets[i][15]
# #            transformunit           = datasets[i][16]
# #            timezone                = datasets[i][17]
            del i

            msg = f"> Checking if there is a File GDB for region: {layercode} and if there is data"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch")

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}")

            del RegionGDB, RegionScratchGDB, layercode

    # ###--->>> Multiprocessing Start

        if not CreateRegionDisMapRegionsSequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            cpu_num = multiprocessing.cpu_count() - 2
            #cpu_num = cpu_count()
            with multiprocessing.Pool(cpu_num) as pool:
            #with multiprocessing.Pool(len(datasets)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append([datasets[i], REGION_SHAPEFILE_DIRECTORY, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder])
                    del i
                # use the map function of pool to call the function worker()
                pool.map(mpCreateDisMapRegions, args)
                # Close and join pools
                pool.close()
                pool.join()

                del pool, args
            del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if CreateRegionDisMapRegionsSequential:
            for i in range(len(datasets)):
                args = [datasets[i], REGION_SHAPEFILE_DIRECTORY, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder]
                mpCreateDisMapRegions(args)
                del i, args

        del CreateRegionDisMapRegionsSequential

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        arcpy.env.overwriteOutput = True

        arcpy.env.workspace = ProjectGDB

        # Creating the DisMAP Regions Dataset
        msg = f'> Generating DisMAP Region Dataset.'
        logFile(log_file, msg); del msg

        dismap_regions = os.path.join(ProjectGDB, u"DisMAP_Regions")
        #sp_ref = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]];-20037700 -30241100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
        sp_ref = arcpy.SpatialReference('WGS_1984_Web_Mercator_Auxiliary_Sphere')

        # Template DisMAP Regions
        template = "_Template_DisMAP_Regions"
        #template_csv_data_path = os.path.join(ProjectGDB, template)

        #if not arcpy.Exists(template_csv_data_path):
        #    createTemplateTables({k: v for k, v in template_table_dictionary.items() if template in k})
        #del template_csv_data_path

        createTemplateTables({k: v for k, v in template_table_dictionary.items() if template in k})
        del template

        arcpy.management.CreateFeatureclass(out_path = ProjectGDB,
                                            out_name = "DisMAP_Regions",
                                            geometry_type = "POLYLINE",
                                            template = "_Template_DisMAP_Regions",
                                            has_m="DISABLED",
                                            has_z="DISABLED",
                                            spatial_reference=sp_ref,
                                            config_keyword="",
                                            spatial_grid_1="0",
                                            spatial_grid_2="0",
                                            spatial_grid_3="0")
        del sp_ref

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End
        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            layercode = datasets[i][4]
            del i

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            layercode_survey_area = f"{layercode}_Survey_Area"
            layercode_boundary_line = f"{layercode}_Boundary_Line"

            arcpy.env.workspace = RegionGDB

            msg = f"#-> Copying the {layercode_survey_area} and {layercode_boundary_line} Datasetes"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(layercode_survey_area, os.path.join(ProjectGDB, layercode_survey_area))

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(layercode_boundary_line, os.path.join(ProjectGDB, layercode_boundary_line))

            del layercode_survey_area

            msg = f">-> Appending the {layercode} Dataset to the DisMAP Regions Dataset"
            logFile(log_file, msg); del msg
            # Process: Append
            arcpy.management.Append(inputs = layercode_boundary_line,
                                    target = dismap_regions,
                                    schema_type="NO_TEST",
                                    field_mapping="",
                                    subtype="")

            # Delete after last use
            del RegionGDB, RegionScratchGDB
            del layercode_boundary_line, layercode

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # ##-->> Delete Identical features in DisMAP Regions Start

        msg = f"> Delete Identical features in DisMAP Regions"
        logFile(log_file, msg); del msg
        # Process: arcpy.management.DeleteIdentical
        arcpy.DeleteIdentical_management(in_dataset = dismap_regions,
                                         fields = "Shape;Shape_Length;LayerCode;Region",
                                         xy_tolerance="",
                                         z_tolerance="0")

        # Add Metadata
        addMetadata(dismap_regions, log_file)

        # Delete after last use
        del dismap_regions

        # Compacting the ProjectGDB
        compactGDB(ProjectGDB, log_file)

        # ##-->> Delete Identical features in DisMAP Regions End

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            layercode = datasets[i][4]
            del i

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {layercode} Region GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {layercode} Region Scratch GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del layercode
        # ##-->> Deleting Scratch and Temporary GDB End

        del datasets

    # ###--->>> Postprocessing End

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpHandlerCreateGLMMETables(CreateGLMMETablesSequential, distributionprojectcode):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        #start the clock
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        args = [CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder]

        datasets = generateDatasets(args)
        datasets = [[r for r in group] for group in datasets if group[8] == distributionprojectcode]

        with arcpy.EnvManager(scratchWorkspace = ScratchFolder, workspace = CSV_DIRECTORY):
            csv_files = arcpy.ListFiles(f"*{distributionprojectcode}*.csv")
            datasets = [[r for r in group] for group in datasets if group[12].lower() in csv_files]
            del csv_files
        del distributionprojectcode

        # Template CSV Table
        template = "_Template_GLMME_Data"
        #template_csv_data_path = os.path.join(ProjectGDB, template)

        #if not arcpy.Exists(template_csv_data_path):
        #    createTemplateTables({k: v for k, v in template_table_dictionary.items() if template in k})
        #del template_csv_data_path

        createTemplateTables({k: v for k, v in template_table_dictionary.items() if template in k})

        for i in range(len(datasets)):
##            oaregioncode            = datasets[i][0]
##            oaregion                = datasets[i][1]
##            dismapregioncode        = datasets[i][2]
##            dismapseasoncode        = datasets[i][3]
            layercode               = datasets[i][4]
##            layername               = datasets[i][5]
##            datecode                = datasets[i][6]
##            distributionprojectname = datasets[i][7]
##            distributionprojectcode = datasets[i][8]
##            region                  = datasets[i][9]
##            seasoncode              = datasets[i][10]
##            summaryproduct          = datasets[i][11]
##            csvfile                 = datasets[i][12]
##            geographicarea          = datasets[i][13]
##            coordinatesystem        = datasets[i][14]
##            cellsize                = datasets[i][15]
##            transformunit           = datasets[i][16]
##            timezone                = datasets[i][17]
            del i

            msg = f"> Checking if there is a File GDB for region: {layercode} and if there is data"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch")

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}")

            if not arcpy.Exists(os.path.join(RegionGDB, template)):
                msg = f"\t> Copying the {template}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, template), os.path.join(RegionGDB, template))

            del RegionGDB, RegionScratchGDB
        del template

    # ###--->>> Multiprocessing Start

        if not CreateGLMMETablesSequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            cpu_num = multiprocessing.cpu_count() - 2
            #cpu_num = cpu_count()
            with multiprocessing.Pool(cpu_num) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append([datasets[i], CSV_DIRECTORY, FilterSpecies, selected_species, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder])
                    del i
                # use the map function of pool to call the function worker()
                pool.map(mpCreateGLMMETables, args)
                # Close and join pools
                pool.close()
                pool.join()

                del pool, args
            del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if CreateGLMMETablesSequential:
            for i in range(len(datasets)):
                args = [datasets[i], CSV_DIRECTORY, FilterSpecies, selected_species, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder]
                mpCreateGLMMETables(args)
                del i, args

        del CreateGLMMETablesSequential

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End
        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            layercode = datasets[i][4]
            csvfile = datasets[i][12][:-4].upper()

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Copying the {csvfile} Dataset"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(csvfile, os.path.join(ProjectGDB, csvfile))

            del RegionGDB, RegionScratchGDB
            del layercode, csvfile, i

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # Compacting the ProjectGDB
        compactGDB(ProjectGDB, log_file)

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            layercode = datasets[i][4]

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            msg = f"#-> Deleting the {layercode} Region GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {layercode} Region Scratch GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del layercode, i
        # ##-->> Deleting Scratch and Temporary GDB End

        del datasets
    # ###--->>> Postprocessing End

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpHandlerCreateIDWRasters(CreateIDWRastersSequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        #start the clock
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        for i in range(len(datasets)):
            layercode = datasets[i][0]
            #layercode_csv_table = datasets[i][2]

            msg = f"> Checking if there is a File GDB for region: {layercode} and if there is data"
            logFile(log_file, msg); del msg
            del i

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            # Region Sample Locations
            layercode_sample_locations = f"{layercode}_Sample_Locations"

            # Region Raster Mask
            layercode_raster_mask = f"{layercode}_Raster_Mask"

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch")

            del layercode

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_sample_locations)):
                msg = f"\t> Copying the {layercode_sample_locations}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_sample_locations), os.path.join(RegionGDB, layercode_sample_locations))

            del layercode_sample_locations

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_raster_mask)):
                msg = f"\t> Copying the {layercode_raster_mask}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_raster_mask), os.path.join(RegionGDB, layercode_raster_mask))

            del layercode_raster_mask

            del RegionGDB, RegionScratchGDB

    # ###--->>> Preprocessing Setup End

    # ###--->>> Multiprocessing Start

        if not CreateIDWRastersSequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            cpu_num = multiprocessing.cpu_count() - 2
            #cpu_num = cpu_count()
            with multiprocessing.Pool(cpu_num) as pool:
            #with multiprocessing.Pool(len(datasets)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append([datasets[i], SoftwareEnvironmentLevel, ScratchFolder, log_file_folder, IMAGE_DIRECTORY])
                    del i
                # use the map function of pool to call the function worker()
                pool.map(mpCreateIDWRasters, args)
                # Close and join pools
                pool.close()
                pool.join()

                del pool, args
            del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start
        if CreateIDWRastersSequential:
            for i in range(len(datasets)):
                args = [datasets[i], SoftwareEnvironmentLevel, ScratchFolder, log_file_folder, IMAGE_DIRECTORY]
                mpCreateIDWRasters(args)
                del i, args

        del CreateIDWRastersSequential

    # ###--->>> Sequentialprocessing End

        # ##-->> Copying Output Start

        compactGDB(ProjectGDB, log_file)

        # ##-->> Copying Output End

    # ###--->>> Postprocessing Start

        # ##-->> Deleting Scratch and Temporary GDB Start
        for dataset in datasets:
            layercode = dataset[0]

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            msg = f"#-> Deleting the {layercode} Region GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {layercode} Region Scratch GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del layercode, dataset
        # ##-->> Deleting Scratch and Temporary GDB End

    # ###--->>> Postprocessing End

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpHandlerCreateIDWTables(CreateIDWTablesSequential, distributionprojectcode):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        #start the clock
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        args = [CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder]
        datasets = generateDatasets(args)
        datasets = [[r for r in group] for group in datasets if group[8] == distributionprojectcode]

        with arcpy.EnvManager(scratchWorkspace = ScratchFolder, workspace = CSV_DIRECTORY):
            csv_files = arcpy.ListFiles(f"*{distributionprojectcode}*.csv")
            datasets = [[r for r in group] for group in datasets if group[12].lower() in csv_files]
            del csv_files
        del distributionprojectcode

        # Template CSV Table
        template = "_Template_IDW_Data"
        #template_csv_data_path = os.path.join(ProjectGDB, template)

        #if not arcpy.Exists(template_csv_data_path):
        #    createTemplateTables({k: v for k, v in template_table_dictionary.items() if template in k})
        #del template_csv_data_path

        createTemplateTables({k: v for k, v in template_table_dictionary.items() if template in k})

        for i in range(len(datasets)):
##            oaregioncode            = datasets[i][0]
##            oaregion                = datasets[i][1]
##            dismapregioncode        = datasets[i][2]
##            dismapseasoncode        = datasets[i][3]
            layercode               = datasets[i][4]
##            layername               = datasets[i][5]
##            datecode                = datasets[i][6]
##            distributionprojectname = datasets[i][7]
##            distributionprojectcode = datasets[i][8]
##            region                  = datasets[i][9]
##            seasoncode              = datasets[i][10]
##            summaryproduct          = datasets[i][11]
##            csvfile                 = datasets[i][12]
##            geographicarea          = datasets[i][13]
##            coordinatesystem        = datasets[i][14]
##            cellsize                = datasets[i][15]
##            transformunit           = datasets[i][16]
##            timezone                = datasets[i][17]
            del i

            msg = f"> Checking if there is a File GDB for region: {layercode} and if there is data"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch")

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}")

            if not arcpy.Exists(os.path.join(RegionGDB, template)):
                msg = f"\t> Copying the {template}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, template), os.path.join(RegionGDB, template))

            del RegionGDB, RegionScratchGDB

        del template

    # ###--->>> Multiprocessing Start

        if not CreateIDWTablesSequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            cpu_num = multiprocessing.cpu_count() - 2
            #cpu_num = cpu_count()
            with multiprocessing.Pool(cpu_num) as pool:
            #with multiprocessing.Pool(len(datasets)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append([datasets[i], CSV_DIRECTORY, FilterSpecies, selected_species, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder])
                    del i
                # use the map function of pool to call the function worker()
                pool.map(mpCreateIDWTables, args)
                # Close and join pools
                pool.close()
                pool.join()

                del pool, args
            del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if CreateIDWTablesSequential:
            for i in range(len(datasets)):
                args = [datasets[i], CSV_DIRECTORY, FilterSpecies, selected_species, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder]
                mpCreateIDWTables(args)
                del i, args

        del CreateIDWTablesSequential

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End
        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            layercode = datasets[i][4]
            csvfile = datasets[i][12][:-4].upper()

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Copying the {csvfile} Dataset"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(csvfile, os.path.join(ProjectGDB, csvfile))

            del RegionGDB, RegionScratchGDB
            del layercode, csvfile, i

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # Compacting the ProjectGDB
        compactGDB(ProjectGDB, log_file)

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            layercode = datasets[i][4]

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            msg = f"#-> Deleting the {layercode} Region GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {layercode} Region Scratch GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del layercode, i
        # ##-->> Deleting Scratch and Temporary GDB End

        del datasets

    # ###--->>> Postprocessing End

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpHandlerCreateIndicatorsTable(CreateIndicatorsTableSequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        #start the clock
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Template CSV Table
        template = "_Template_Indicators"
        #template_csv_data_path = os.path.join(ProjectGDB, template)

        #if not arcpy.Exists(template_csv_data_path):
        #    createTemplateTables({k: v for k, v in template_table_dictionary.items() if template in k})
        #del template_csv_data_path

        createTemplateTables({k: v for k, v in template_table_dictionary.items() if template in k})

    # ###--->>> Preprocessing Setup Start
        for i in range(len(datasets)):
            layercode = datasets[i][0]
            layercode_csv_table = datasets[i][2].upper()
            del i

            msg = f"> Checking if there is a File GDB for region: {layercode} and if there is data"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            # Region Raster Mask
            layercode_raster_mask = f"{layercode}_Raster_Mask"

            # Region Bathymetry
            layercode_bathymetry = f"{layercode}_Bathymetry"

            # Region Latitude
            layercode_latitude   = f"{layercode}_Latitude"

            # Region Longitude
            layercode_longitude  = f"{layercode}_Longitude"

            # Template Indicators Table
            template_indicators = "_Template_Indicators"

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch")
                arcpy.management.Copy(os.path.join(BathymetryGDB, f"{layercode}_Bathymetry"), os.path.join(RegionScratchGDB, f"{layercode}_Bathymetry"))

            del layercode

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_csv_table)):
                msg = f"\t> Copying the {layercode_csv_table}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_csv_table), os.path.join(RegionGDB, layercode_csv_table))

            del layercode_csv_table

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_raster_mask)):
                msg = f"\t> Copying the {layercode_raster_mask}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_raster_mask), os.path.join(RegionGDB, layercode_raster_mask))

            del layercode_raster_mask

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_bathymetry)):
                msg = f"\t> Copying the {layercode_bathymetry}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_bathymetry), os.path.join(RegionGDB, layercode_bathymetry))

            del layercode_bathymetry

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_latitude)):
                msg = f"\t> Copying the {layercode_latitude}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_latitude), os.path.join(RegionGDB, layercode_latitude))

            del layercode_latitude

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_longitude)):
                msg = f"\t> Copying the {layercode_longitude}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_longitude), os.path.join(RegionGDB, layercode_longitude))

            del layercode_longitude

            if not arcpy.Exists(os.path.join(RegionGDB, template)):
                msg = f"\t> Copying the {template}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, template), os.path.join(RegionGDB, template))

            del RegionGDB, RegionScratchGDB

        del template

    # ###--->>> Preprocessing Setup End

    # ###--->>> Multiprocessing Start

        if not CreateIndicatorsTableSequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            cpu_num = multiprocessing.cpu_count() - 2
            #cpu_num = cpu_count()
            with multiprocessing.Pool(cpu_num) as pool:
            #with multiprocessing.Pool(len(datasets)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append([datasets[i], SoftwareEnvironmentLevel, ScratchFolder, log_file_folder, IMAGE_DIRECTORY])
                    del i
                # use the map function of pool to call the function worker()
                pool.map(mpCreateIndicatorsTable, args)
                # Close and join pools
                pool.close()
                pool.join()

                del pool, args
            del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start
        if CreateIndicatorsTableSequential:
            for i in range(len(datasets)):
                args = [datasets[i], SoftwareEnvironmentLevel, ScratchFolder, log_file_folder, IMAGE_DIRECTORY]
                mpCreateIndicatorsTable(args)
                del i, args

        del CreateIndicatorsTableSequential

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        arcpy.env.overwriteOutput = True

        # ##-->> Copying Output Start
        indicators_template = os.path.join(ProjectGDB, u"_Template_Indicators")
        indicators = os.path.join(ProjectGDB, u"Indicators")

        #arcpy.management.Delete(indicators)
        arcpy.management.CreateTable(ProjectGDB, u"Indicators", indicators_template, "" ,"")
        msg = f"#-> {arcpy.GetMessages().replace(chr(10), f'{chr(10)}#-> ')}{chr(10)}"
        logFile(log_file, msg); del msg

        del indicators_template

        for dataset in datasets:
            layercode = dataset[0]

            msg = f"#-> Copying the {layercode} Indicators Table"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            layercode_indicators = os.path.join(RegionGDB, f"{layercode}_Indicators")
            arcpy.management.Copy(layercode_indicators, os.path.join(ProjectGDB, f"{layercode}_Indicators"))
            # Append Region Indicators to Indicators Table
            arcpy.management.Append(inputs=layercode_indicators, target=indicators, schema_type="TEST", field_mapping="", subtype="")
            del layercode_indicators

            del RegionGDB
            del dataset, layercode

        del indicators

        compactGDB(ProjectGDB, log_file)

        # ##-->> Copying Output End

        # ##-->> Deleting Scratch and Temporary GDB Start
        for dataset in datasets:
            layercode = dataset[0]

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {layercode} Region GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {layercode} Region Scratch GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del layercode, dataset
        # ##-->> Deleting Scratch and Temporary GDB End

    # ###--->>> Postprocessing End

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpHandlerCreateLayerCodeBathymetry(CreateLayerCodeBathymetrySequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        #start the clock
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        PurgeGDB = False
        if PurgeGDB:
            # ##-->> Deleting Scratch and Temporary GDB Start
            for dataset in datasets:
                layercode = dataset[0]

                RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

                RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

                msg = f"#-> Deleting the {layercode} Region GDB"
                logFile(log_file, msg); del msg

                purgeGDB(RegionGDB)
                arcpy.management.Delete(RegionGDB)

                msg = f"#-> Deleting the {layercode} Region Scratch GDB"
                logFile(log_file, msg); del msg

                purgeGDB(RegionScratchGDB)
                arcpy.management.Delete(RegionScratchGDB)

                del RegionGDB, RegionScratchGDB
                del layercode, dataset
            # ##-->> Deleting Scratch and Temporary GDB End
        del PurgeGDB

        for i in range(len(datasets)):
            layercode = datasets[i][0].upper()
            del i

            msg = f"> Checking if there is a File GDB for region: {layercode} and if there is data"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            # Region Survey Area
            layercode_survey_area = f"{layercode}_Survey_Area"

            # Region Fishnet
            layercode_fish_net = f"{layercode}_Fish_Net"

            # Region Bathymetry
            layercode_bathymetry = f"{layercode}_Bathymetry"

            # Region Latitude & Longitude
            layercode_lat_long = f"{layercode}_Lat_Long"

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch")

            del layercode

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_survey_area)):
                msg = f"\t> Copying the {layercode_survey_area}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_survey_area), os.path.join(RegionGDB, layercode_survey_area))

            del layercode_survey_area

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_fish_net)):
                msg = f"\t> Copying the {layercode_fish_net}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_fish_net), os.path.join(RegionGDB, layercode_fish_net))

            del layercode_fish_net

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_lat_long)):
                msg = f"\t> Copying the {layercode_lat_long}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_lat_long), os.path.join(RegionGDB, layercode_lat_long))

            del layercode_lat_long

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_bathymetry)):
                msg = f"\t> Copying the {layercode_bathymetry}"
                logFile(log_file, msg); del msg
                arcpy.management.Copy(os.path.join(BathymetryGDB, layercode_bathymetry), os.path.join(RegionScratchGDB, layercode_bathymetry))

            del layercode_bathymetry

            del RegionGDB, RegionScratchGDB

    # ###--->>> Multiprocessing Start

        if not CreateLayerCodeBathymetrySequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            cpu_num = multiprocessing.cpu_count() - 2
            #cpu_num = cpu_count()
            with multiprocessing.Pool(cpu_num) as pool:
            #with multiprocessing.Pool(len(datasets)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append([datasets[i], SoftwareEnvironmentLevel, ScratchFolder, log_file_folder])
                    del i
                # use the map function of pool to call the function worker()
                pool.map(mpCreateLayerCodeBathymetry, args)
                # Close and join pools
                pool.close()
                pool.join()

                del pool, args
            del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if CreateLayerCodeBathymetrySequential:
            for i in range(len(datasets)):
                args = [datasets[i], SoftwareEnvironmentLevel, ScratchFolder, log_file_folder]
                mpCreateLayerCodeBathymetry(args)
                del i, args

        del CreateLayerCodeBathymetrySequential

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB Start
        arcpy.env.overwriteOutput = True

        for dataset in datasets:
            layercode = dataset[0]

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            layercode_bathymetry = f"{layercode}_Bathymetry"

            msg = f"#-> Copying the {layercode_bathymetry}"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(layercode_bathymetry, os.path.join(ProjectGDB, layercode_bathymetry))

            del layercode_bathymetry

            layercode_raster_mask = f"{layercode}_Raster_Mask"

            msg = f"#-> Copying the {layercode_raster_mask}"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(layercode_raster_mask, os.path.join(ProjectGDB, layercode_raster_mask))

            del layercode_raster_mask

            layercode_latitude = f"{layercode}_Latitude"

            msg = f"#-> Copying the {layercode_latitude}"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(layercode_latitude, os.path.join(ProjectGDB, layercode_latitude))

            del layercode_latitude

            layercode_longitude = f"{layercode}_Longitude"

            msg = f"#-> Copying the {layercode_longitude}"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(layercode_longitude, os.path.join(ProjectGDB, layercode_longitude))

            del layercode_longitude

            del RegionGDB, RegionScratchGDB
            del dataset, layercode

        compactGDB(ProjectGDB, log_file)

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # ##-->> Deleting Scratch and Temporary GDB Start
        for dataset in datasets:
            layercode = dataset[0]

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {layercode} Region GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {layercode} Region Scratch GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del layercode, dataset
        # ##-->> Deleting Scratch and Temporary GDB End

    # ###--->>> Postprocessing End

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpHandlerCreateLayerCodeFishnets(CreateLayerCodeFishnetsSequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        #start the clock
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        args = [CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder]
        datasets = generateDatasets(args)

        with arcpy.EnvManager(scratchWorkspace = ScratchFolder, workspace = ProjectGDB):
            wc = "_Survey_Area"
            fcs = arcpy.ListFeatureClasses(f"*{wc}")
            datasets = [[r for r in group] for group in datasets if f"{group[4]}{wc}" in fcs]
            del wc, fcs

        for i in range(len(datasets)):
            layercode = datasets[i][4]
            #layercode_csv_table = datasets[i][2]
            del i

            msg = f"> Checking if there is a File GDB for region: {layercode} and if there is data"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            # Region Survey Area
            layercode_survey_area = f"{layercode}_Survey_Area"

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch")

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}")

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_survey_area)):
                msg = f"\t> Copying the {layercode_survey_area}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_survey_area), os.path.join(RegionGDB, layercode_survey_area))

            del layercode_survey_area, layercode

            del RegionGDB, RegionScratchGDB

    # ###--->>> Multiprocessing Start

        if not CreateLayerCodeFishnetsSequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            cpu_num = multiprocessing.cpu_count() - 2
            #cpu_num = cpu_count()
            with multiprocessing.Pool(cpu_num) as pool:
            #with multiprocessing.Pool(len(datasets)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append([datasets[i], REGION_SHAPEFILE_DIRECTORY, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder])
                    del i
                # use the map function of pool to call the function worker()
                pool.map(mpCreateLayerCodeFishnets, args)
                # Close and join pools
                pool.close()
                pool.join()

                del pool, args
            del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if CreateLayerCodeFishnetsSequential:
            for i in range(len(datasets)):
                args = [datasets[i], REGION_SHAPEFILE_DIRECTORY, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder]
                mpCreateLayerCodeFishnets(args)
                del i, args

        del CreateLayerCodeFishnetsSequential

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        # ##-->> Adding geometry attributes Start
        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            layercode = datasets[i][4]
            del i

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Adding geometry attributes"
            logFile(log_file, msg); del msg

            sr = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"

            layercode_points = f"{layercode}_Points"

            msg = f"\n\tAdding Latitude and Longitude values to {layercode_points}"
            logFile(log_file, msg); del msg
            # Add DD to points
            # File GDB Workspace
            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.CalculateGeometryAttributes(layercode_points, "Longitude POINT_X;Latitude POINT_Y", '', '', sr, "DD")
                #print(arcpy.GetMessages())

            msg = f"\n\tAdding DMS values to {layercode}_Points"
            logFile(log_file, msg); del msg
            # Add DMS to points
            # File GDB Workspace
            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.CalculateGeometryAttributes(layercode_points, "DMSLong POINT_X;DMSLat POINT_Y", '', '', sr, "DMS_DIR_LAST")
                #print(arcpy.GetMessages())

            fields = ['DMSLat', 'DMSLong',]

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                # Create update cursor for Dataset
                with arcpy.da.UpdateCursor(layercode_points, fields) as cursor:
                    for row in cursor:
                        #print(f"\n{row[0]}, {row[1]}\n")
                        #print(f"Lat: {row[0][:-14]}")
                        #print(f"Lat: {str(round(float(row[0][-14:-7]),1))}")
                        #print(f"Lat: {row[0][-3:]}")
                        #print(f"Long: {row[1][:-14]}")
                        #print(f"Long: {str(round(float(row[1][-14:-7]),1))}")
                        #print(f"Long: {row[1][-3:]}")
                        row[0] = row[0][:][:-14] + str(round(float(row[0][-14:-7]),1)) + row[0][-3:]
                        row[1] = row[1][:][:-14] + str(round(float(row[1][-14:-7]),1)) + row[1][-3:]
                        #print(f"\n{row[0]}, {row[1]}\n")
                        cursor.updateRow(row)
                        del row
                del fields, cursor

            layercode_lat_long = f"{layercode}_Lat_Long"

            print(f"\n\tAdding Latitude and Longitude values to {layercode_lat_long}")
            # Add DD to points
            # File GDB Workspace
            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.CalculateGeometryAttributes(layercode_lat_long, "Longitude POINT_X;Latitude POINT_Y", '', '', sr, "DD")
                #print(arcpy.GetMessages())

            del RegionGDB, RegionScratchGDB
            del layercode, layercode_points, layercode_lat_long, sr

        # ##-->> Adding geometry attributes End

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB Start

        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            layercode = datasets[i][4]
            del i

            msg = f"#-> Copying the {layercode}_Points, {layercode}_Lat_Long, and {layercode}_Fish_Net Datasetes"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            layercode_points = f"{layercode}_Points"

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(layercode_points, os.path.join(ProjectGDB, layercode_points))

            layercode_lat_long = f"{layercode}_Lat_Long"

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(layercode_lat_long, os.path.join(ProjectGDB, layercode_lat_long))

            layercode_fishnet = f"{layercode}_Fish_Net"

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(layercode_fishnet, os.path.join(ProjectGDB, layercode_fishnet))

            del RegionGDB, RegionScratchGDB
            del layercode, layercode_points, layercode_lat_long, layercode_fishnet

        # Compacting the ProjectGDB
        compactGDB(ProjectGDB, log_file)

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            layercode = datasets[i][4]
            del i

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {layercode} Region GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {layercode} Region Scratch GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del layercode
        # ##-->> Deleting Scratch and Temporary GDB End

        del datasets
    # ###--->>> Postprocessing End

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpHandlerCreateSampleLocationPoints(CreateSampleLocationPointsSequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        #start the clock
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        args = [CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder]
        datasets = generateDatasets(args)

        with arcpy.EnvManager(scratchWorkspace = ScratchFolder, workspace = ProjectGDB):
            tbs = arcpy.ListTables(f"*")
            datasets = [[r for r in group] for group in datasets if group[4] in tbs]
            del tbs

        for i in range(len(datasets)):
# #            oaregioncode            = datasets[i][0]
# #            oaregion                = datasets[i][1]
# #            dismapregioncode        = datasets[i][2]
# #            dismapseasoncode        = datasets[i][3]
            layercode               = datasets[i][4]
# #            layername               = datasets[i][5]
# #            datecode                = datasets[i][6]
# #            distributionprojectname = datasets[i][7]
# #            distributionprojectcode = datasets[i][8]
# #            region                  = datasets[i][9]
# #            seasoncode              = datasets[i][10]
# #            summaryproduct          = datasets[i][11]
# #            csvfile                 = datasets[i][12]
# #            geographicarea          = datasets[i][13]
# #            coordinatesystem        = datasets[i][14]
# #            cellsize                = datasets[i][15]
# #            transformunit           = datasets[i][16]
# #            timezone                = datasets[i][17]
            del i


            msg = f"> Checking if there is a File GDB for region: {layercode} and if there is data"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch")

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}")

            if not arcpy.Exists(os.path.join(RegionGDB, layercode)):
                msg = f"\t> Copying the {layercode}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode), os.path.join(RegionGDB, layercode))

            del RegionGDB, RegionScratchGDB, layercode

    # ###--->>> Multiprocessing Start

        if not CreateSampleLocationPointsSequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            cpu_num = multiprocessing.cpu_count() - 2
            #cpu_num = cpu_count()
            with multiprocessing.Pool(cpu_num) as pool:
            #with multiprocessing.Pool(len(datasets)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append([datasets[i], REGION_SHAPEFILE_DIRECTORY, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder])
                    del i
                # use the map function of pool to call the function worker()
                pool.map(mpCreateSampleLocationPoints, args)
                # Close and join pools
                pool.close()
                pool.join()

                del pool, args
            del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if CreateSampleLocationPointsSequential:
            for i in range(len(datasets)):
                args = [datasets[i], REGION_SHAPEFILE_DIRECTORY, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder]
                mpCreateSampleLocationPoints(args)
                del i, args

        del CreateSampleLocationPointsSequential

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End
        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            layercode = datasets[i][4]

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            sample_locations = f"{layercode}_Sample_Locations"

            msg = f"#-> Copying the {sample_locations} Dataset"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(sample_locations, os.path.join(ProjectGDB, sample_locations))

            del RegionGDB, RegionScratchGDB
            del i, layercode, sample_locations

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # Compacting the ProjectGDB
        compactGDB(ProjectGDB, log_file)

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            layercode = datasets[i][4]

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {layercode} Region GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {layercode} Region Scratch GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del layercode, i
        # ##-->> Deleting Scratch and Temporary GDB End

        del datasets
    # ###--->>> Postprocessing End

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def mpHandlerCreateSpeciesRichnessRasters(CreateSpeciesRichnessRastersSequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        #start the clock
        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        for i in range(len(datasets)):
            layercode = datasets[i][0]
            #layercode_csv_table = datasets[i][2]
            del i

            msg = f"> Checking if there is a File GDB for region: {layercode} and if there is data"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            # Region Raster Mask
            layercode_raster_mask = f"{layercode}_Raster_Mask"

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch")
                #arcpy.management.Copy(os.path.join(BathymetryGDB, f"{layercode}_Bathymetry"), os.path.join(RegionScratchGDB, f"{layercode}_Bathymetry"))

            del layercode

            if not arcpy.Exists(os.path.join(RegionGDB, layercode_raster_mask)):
                msg = f"\t> Copying the {layercode_raster_mask}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, layercode_raster_mask), os.path.join(RegionGDB, layercode_raster_mask))

            del layercode_raster_mask

            del RegionGDB, RegionScratchGDB

    # ###--->>> Preprocessing Setup End

    # ###--->>> Multiprocessing Start

        if not CreateSpeciesRichnessRastersSequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            cpu_num = multiprocessing.cpu_count() - 2
            #cpu_num = cpu_count()
            with multiprocessing.Pool(cpu_num) as pool:
            #with multiprocessing.Pool(len(datasets)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append([datasets[i], SoftwareEnvironmentLevel, ScratchFolder, log_file_folder, IMAGE_DIRECTORY])
                    del i
                # use the map function of pool to call the function worker()
                pool.map(mpCreateSpeciesRichnessRasters, args)
                # Close and join pools
                pool.close()
                pool.join()

                del pool, args
            del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start
        if CreateSpeciesRichnessRastersSequential:
            for i in range(len(datasets)):
                args = [datasets[i], SoftwareEnvironmentLevel, ScratchFolder, log_file_folder, IMAGE_DIRECTORY]
                mpCreateCoreSpeciesRichnessRasters(args)
                del i, args

        del CreateIDWRastersSequential

    # ###--->>> Sequentialprocessing End

        # ##-->> Copying Output Start

        compactGDB(ProjectGDB, log_file)

        # ##-->> Copying Output End

    # ###--->>> Postprocessing Start

        # ##-->> Deleting Scratch and Temporary GDB Start
        for dataset in datasets:
            layercode = dataset[0]

            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {layercode} Region GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {layercode} Region Scratch GDB"
            logFile(log_file, msg); del msg

            purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del layercode, dataset
        # ##-->> Deleting Scratch and Temporary GDB End

    # ###--->>> Postprocessing End

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        del start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            logFile(log_file, msg); del msg
        del localKeys, function

def purgeGDB(target_gdb=arcpy.env.scratchGDB):
    try:
        # use walk to get all the objects in the scratch geodatabase
        for parent, grp_objs, objs in arcpy.da.Walk(target_gdb):

            # iterate a combined list of all top level objects
            for item in grp_objs + objs:

                # create a full path to the current item
                item_path = os.path.join(parent, item)

                # delete the item
                arcpy.management.Delete(item_path)

            # break out of the loop after the first iteration
            break

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg

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
        Usage:
        new_field_order = ["field2", "field3", "field1"]
        reorder_fields(in_fc, out_fc, new_field_order)
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
        arcpy.Merge_management(table, out_table, new_mapping)
        return out_table

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg

# #
# Function: select_by_specie
#       Selects the rows of fish species data in a 5 year span for use by the
#       Inverse Distance Weighted (IDW) function.
# @param string table: The name of the layer that contains the fish information
# @param string which_fish: The scientific name (Species) of the fish species to look at
# @param string base_year: The origin year (as a string) to get a five year range
#       (-2 to +2) of data for this fish.
# @return integer 1: returns 1 on complete
# #
def select_by_specie(table, unique_specie, base_year, log_file):
    # This clears the selection just incase it is not empty, even though
    # "NEW_SELECTION" should theroetically take care of this
    # base_year should already be converted to string using str()
    #msg = f"\n>-> Selecing from table: '{table}'"
    #msg += f"\n>-> With Statement: \"Species\"='{unique_specie}' AND \"Year\" >= ({base_year-2}) AND \"Year\" <= ({base_year+2})"
    #logFile(log_file, msg); del msg

    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", f"\"Species\"='{unique_specie}' AND \"Year\" >= ({base_year-2}) AND \"Year\" <= ({base_year+2})" )
    return 1

##
# Function: select_by_specie_no_years
#       Does same thing as @function select_by_specie, just all of the years worth of data.
# @param string table: The name of the layer that contains the fish information
# @param string which_fish: The scientific name (Species) of the fish species to look at
# @return boolean True: returns True on complete.
##
def select_by_specie_no_years(table, unique_specie, log_file):
    #
    #msg = f"\n>-> Selecing from table: '{table}'"
    #msg += f"\n>-> With Statement: \"Species\"= '{unique_specie}'"
    #logFile(log_file, msg); del msg

    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", f"\"Species\"='{unique_specie}'" )
    return 1

# #
# Function: unique_field
#       Generic function to return all the unique values within a specified field
# @param string table: The name of the layer that contains the field to be searched
# @param string field: which field to look
# @return array: a sorted array of unique values.
# #
def unique_field(table, field):
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
# Function: unique_species
#       Gets the unique fish species within a dataset
# @param string table: The name of the layer that contains the fish information
# @return array: a sorted array of unique fish species.
# #
def unique_species(table):
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    with arcpy.da.SearchCursor(table, ["Species"]) as cursor:
        return sorted({row[0] for row in cursor})

# #
# Function: unique_species_dict
#       Gets the unique fish species and common name within a dataset
# @param string table: The name of the layer that contains the fish information
# @return array: a sorted array of unique fish species and common name.
# #
def unique_species_dict(table):
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
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", "Year IS NOT NULL")
    with arcpy.da.SearchCursor(table, ["Year"]) as cursor:
        return sorted({row[0] for row in cursor})

def unique_values(table, field):
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor}) # Uses list comprehension

if __name__ == '__main__':
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        # Set Current Working Directory to the path of this Python script
        global cwd
        cwd = os.path.dirname(__file__)
        # Change the path to the Current Working Directory
        os.chdir(cwd)

        # Specify the Log File Folder (directory)
        global log_file_folder
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
        timestr = strftime('%a %b %d %I %M %S %p', localtime())

        # The log file is For benchmarking, capturing general messages and
        # errors.
        global log_file
        log_file = os.path.join(log_file_folder, f"{script_file} {timestr}.log")
        # Clean-up
        del timestr

        # Write a message to the log file
        msg = "STARTING {0} ON {1}".format(script_file, strftime('%a %b %d %I:%M:%S %p', localtime()))
        logFile(log_file, msg); del msg

# ###--->>>

        # Version and Date Code
        # December 1 2022
        # Version = "December 1 2022"
        # DateCode = "20221201"

        # December 15 2022
        #Version = "December 15 2022"
        #DateCode = "20221215"

        # December 15 2022
        Version = "January 1 2023"
        DateCode = "20230101"

        # Software Environment Level
        SoftwareEnvironmentLevel = "Dev" # For use on Local laptop
        #SoftwareEnvironmentLevel = "Test" # For use on Local laptop and Windows Instance
        #SoftwareEnvironmentLevel = "Prod" # For use on Windows Instance

        # Set to True if we want to filter on certian one or more regions, else
        # False to process all regions
        FilterDatasets = False # True False
        # selected_datasets = selected_regions = 'AI_IDW','BSS_IDW','EBS_IDW','NEBS_IDW','NBS_IDW','GOA_IDW','GMEX_IDW','HI_IDW','NEUS_FAL_IDW','NEUS_SPR_IDW','SEUS_FAL_IDW','SEUS_SPR_IDW','SEUS_SUM_IDW','WC_ANN_IDW','WC_GLMME','WC_TRI_IDW',
        # Below are lists used to test different regions
        #selected_datasets = ['AI_IDW', 'EBS_IDW', 'HI_IDW',]
        #selected_datasets = ['HI_IDW',]
        #selected_datasets = ['WC_GLMME', 'HI_IDW',]
        #selected_datasets = ['WC_GLMME', 'HI_IDW', 'SEUS_FAL_IDW',]
        selected_datasets = ['WC_GLMME',]

        # Set to True if we want to filter on certian years, else False to
        # process all years
        #FilterYears = False

        # The main() is for testing and project setup
        main()

    # ###--->>> Step #0
    # ###--->>> Create Tables Start
        # Create Template Tables: True or False
        CreateTemplateTables = False
        # Create empty tables, if CreateTemplateTables is set to True
        if CreateTemplateTables:
            #print(template_table_dictionary["_Template_Datasets"])
            #createTemplateTables({k: v for k, v in template_table_dictionary.items() if k.startswith('_Template_Datasets')})
            createTemplateTables(template_table_dictionary)
        del CreateTemplateTables
    # ###--->>> Create Tables End

    # ###--->>> Step #1
    # ###--->>> Create Dataset Table Start
        # Create Template Tables: True or False
        CreateDatasetTable = False
        if CreateDatasetTable:
            args = [CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder]
            createDatasetTable(args); del args
        del CreateDatasetTable
    # ###--->>> Create Daaset Table End

    # ###--->>> Step #2
    # ###--->>> Import IDW CSV Tables Start

        # Create IDW CSV Tables True or False
        CreateIDWTables = False
        CreateIDWTablesSequential = False
        distributionprojectcode = "IDW"
        # Generate Tables -- Needs to run next so that Datasetes can be
        # created in the following step.
        if CreateIDWTables:
            mpHandlerCreateIDWTables(CreateIDWTablesSequential, distributionprojectcode)
        del CreateIDWTables, CreateIDWTablesSequential
        del mpCreateIDWTables, mpHandlerCreateIDWTables, distributionprojectcode

    # ###--->>> Import IDW CSV Tables End

    # ###--->>> Step #3
    # ###--->>> Import GLMME CSV Tables Start

        # Create GLMME CSV Tables True or False
        CreateGLMMETables = False
        CreateGLMMETablesSequential = False
        distributionprojectcode = "GLMME"
        # Generate Tables -- Needs to run next so that Datasetes can be
        # created in the following step.
        if CreateGLMMETables:
            mpHandlerCreateGLMMETables(CreateGLMMETablesSequential, distributionprojectcode)
        del CreateGLMMETables, CreateGLMMETablesSequential
        del mpCreateGLMMETables, mpHandlerCreateGLMMETables, distributionprojectcode

    # ###--->>> Import GLMME CSV Tables End

    # ###--->>> Step #4
    # ###--->>> Create Master Species Information Table Start

        CreateMasterSpeciesInformationTable = False
        if CreateMasterSpeciesInformationTable:
            args = CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder
            createMasterSpeciesInformationTable(args); del args
        del CreateMasterSpeciesInformationTable
        del createMasterSpeciesInformationTable

        #args = CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder
        #print(generateMasterSpeciesInformation(args)); del args

    # ###--->>> Create Master Species Information Table End

    # ###--->>> Step #5
    # ###--->>> Create Species Filter Table Start

        CreateSpeciesFilterTable = False
        if CreateSpeciesFilterTable:
            args = CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder
            createSpeciesFilterTable(args); del args
        del CreateSpeciesFilterTable, createSpeciesFilterTable

        #args = CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder
        #print(generateSpeciesFilter(args)); del args

    # ###--->>> Create Species Filter Table End

    # ###--->>> Step #6
    # ###--->>> Populate Region Species Year Image Name Table Start

        # Create Region-Species-Year-Image-Name Table True or False
        CreateRegionSpeciesYearImageName = False
        if CreateRegionSpeciesYearImageName:
            args = CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder
            createRegionSpeciesYearImageName(args); del args
        del CreateRegionSpeciesYearImageName
        del createRegionSpeciesYearImageName

    # ###--->>> Populate Region Species Year Image Name Table End

    # ###--->>> Step #7
    # ###--->>> Create Sample Location Points Datasetes Start

        # Create Folders in a Base Folder
        #createFolders(REGION_SHAPEFILE_DIRECTORY)

        # Generate Point Datasetes True or False
        CreateSampleLocationPoints = False
        CreateSampleLocationPointsSequential = True
        if CreateSampleLocationPoints:
            mpHandlerCreateSampleLocationPoints(CreateSampleLocationPointsSequential)
        del CreateSampleLocationPoints, CreateSampleLocationPointsSequential
        del mpCreateSampleLocationPoints, mpHandlerCreateSampleLocationPoints

    # ###--->>>  Create Survey Location Points Datasetes End

    # ###--->>> Step #8
    # ###--->>> Create DisMAP Regions Start

        # Create DisMAP Regions True or False
        CreateDisMapRegions = False
        CreateDisMapRegionsSequential = False
        if CreateDisMapRegions:
            mpHandlerCreateDisMapRegions(CreateDisMapRegionsSequential)
        del CreateDisMapRegions, CreateDisMapRegionsSequential
        del mpCreateDisMapRegions, mpHandlerCreateDisMapRegions

    # ###--->>> Create DisMAP Regions End

    # ###--->>> Step #9
    # ###--->>> Create Regions Fishnets Start

##        args = [CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder]
##        datasets = generateDatasets(args)
##
##        layercodes = [group[4] for group in datasets]
##        #print(layercodes)
##
##        with arcpy.EnvManager(scratchWorkspace = ScratchFolder, workspace = ProjectGDB):
##            wc = "_Survey_Area"
##            fcs = arcpy.ListFeatureClasses(f"*{wc}")
##            datasets = [[r for r in group] for group in datasets if f"{group[4]}{wc}" in fcs]
##            del wc, fcs
##
##        #datasets = [[r for r in group] for group in datasets if group[12].lower() in csv_files]
##        for dataset in datasets:
##            layercode = dataset[4]
##            #print(layercode)
##            RegionGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}.gdb")
##            RegionScratchGDB = os.path.join(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch.gdb")
##            if not os.path.exists(RegionScratchGDB):
##                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
##                logFile(log_file, msg); del msg
##                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel} Scratch")
##            if not os.path.exists(RegionGDB):
##                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
##                logFile(log_file, msg); del msg
##                arcpy.management.CreateFileGDB(ScratchFolder, f"{layercode} {SoftwareEnvironmentLevel}")
##            del RegionGDB, RegionScratchGDB, layercode
##
##            args = [dataset, SoftwareEnvironmentLevel, ScratchFolder, log_file_folder]
##            mpCreateLayerCodeFishnets(args)
##        del args

        # Generate Region Bathymetry True or False
        CreateLayerCodeFishnets = False
        CreateLayerCodeFishnetsSequential = False
        if CreateLayerCodeFishnets:
            mpHandlerCreateLayerCodeFishnets(CreateLayerCodeFishnetsSequential)
        del CreateLayerCodeFishnets, mpHandlerCreateLayerCodeFishnets
        del mpCreateLayerCodeFishnets, CreateLayerCodeFishnetsSequential

    # ###--->>> Create Regions Fishnets End

    # ###--->>> Step #10
    # ###--->>> Get DMS Points for GEBCO Regions Start

        # This function creates a report of coordinate values by region
        # to be used to extract GEBCO data
        # Get DMS for points that create fishnet True or False
        GetDMSPointsForGebco = False
        if GetDMSPointsForGebco:
            getDMSPointsForGebco()
        del GetDMSPointsForGebco, getDMSPointsForGebco

    # ###--->>> Get DMS Points for GEBCO Regions End

    # ###--->>> Step #11
    # ###--->>> Create Regions Bathymetry Start
        # Create Region Bathymetry True or False
        CreateLayerCodeBathymetry = False
        CreateLayerCodeBathymetrySequential = False
        if CreateLayerCodeBathymetry:
            mpHandlerCreateLayerCodeBathymetry(CreateLayerCodeBathymetrySequential)
        del CreateLayerCodeBathymetry, mpHandlerCreateLayerCodeBathymetry
        del CreateLayerCodeBathymetrySequential, mpCreateLayerCodeBathymetry

    # ###--->>> Create Regions Bathymetry End

    # ###--->>> Step #12
    # ###--->>> Create Biomass Rasters Start

        # Generate Rasters True or False
        CreateIDWRasters = False
        CreateIDWRastersSequential = False
        if CreateIDWRasters:
            mpHandlerCreateIDWRasters(CreateIDWRastersSequential)
        del CreateIDWRasters, mpHandlerCreateIDWRasters
        del CreateIDWRastersSequential, mpCreateIDWRasters

    # ###--->>> Step #13
    # ###--->>> Indicators Table Start

        # Populate Indicators Table True or False
        CreateIndicatorsTable = False
        CreateIndicatorsTableSequential = False
        if CreateIndicatorsTable:
            mpHandlerCreateIndicatorsTable(CreateIndicatorsTableSequential)
        del CreateIndicatorsTable, mpHandlerCreateIndicatorsTable
        del CreateIndicatorsTableSequential, mpCreateIndicatorsTable

    # ###--->>> Indicators Table End

    # ###--->>> Step #14
    # ###--->>> Species Richness Rasters Start

        # Create Species Richness Rasters = True or False
        CreateSpeciesRichnessRasters = False
        CreateSpeciesRichnessRastersSequential = False
        if CreateSpeciesRichnessRasters:
            mpHandlerCreateSpeciesRichnessRasters(CreateSpeciesRichnessRastersSequential)
        del CreateSpeciesRichnessRasters, CreateSpeciesRichnessRastersSequential
        del mpHandlerCreateSpeciesRichnessRasters, mpCreateSpeciesRichnessRasters

        del createCoreSpeciesRichnessRasters, createSpeciesRichnessRasters

    # ###--->>> Species Richness Rasters End


    # ###--->>> Step #
    # ###--->>> Table and Field Report Start
        # Table and Field Report: True or False
        CreateTableAndFieldReport = False
        # Workspace: ws
        ws = ProjectGDB
        # Wildcard: wc
        #   Usage: wc = "", wc = "HI_CSV", wc = "_Template", wc = "_csv"
        # Data Type: dt
        #   Usage: dt = ["Any",], dt = ["Table", "FeatureClass"], dt = ["Table"]
        # Feature Type: t
        #   Usage: t = ["Any",], t = ["Polygon",]

        # Report on Template Datasets
        #wc = "_Template_Indicators"; dt = ["Any",];  t = ["Any",]
        wc = "_Template"; dt = ["Any",];  t = ["Any",]

        if CreateTableAndFieldReport: createTableAndFieldReport(ws, wc, dt, t)
        del CreateTableAndFieldReport, createTableAndFieldReport, ws, wc, dt, t
    # ###--->>> Table and Field Report End

        # Clean-Up
        del Version, DateCode, SoftwareEnvironmentLevel
        del FilterDatasets
        # del FilterYears

# ###--->>>

        # Final benchmark
        msg = f"ENDING {script_file} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {script_file}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg

        # Clean up
        del cwd, script_file, start_time, end_time, elapse_time

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        if log_file: logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys
        else: print(msg); del msg, sys

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        #pass
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

    # This code always executes after the other blocks, even if there was an
    # uncaught exception (that didn’t cause a crash, obviously) or a return
    # statement in one of the other blocks. Code executed in this block is just
    # like normal code: if there is an exception, it will not be automatically
    # caught (and probably stop the program). This block is also optional.
    finally:
        # Remove imported modules
        del time, datetime, math, numpy, sys
        del os, inspect, function_name, function
        del localtime, strftime, gmtime
        del multiprocessing

        #del logging

        # Remove defined functions
        del compactGDB, listEnvironments, clearFolder, addMetadata
        del reorder_fields, select_by_specie, select_by_specie_no_years
        del unique_field, unique_species, unique_species_dict, unique_year
        del unique_years, unique_values, FilterSpecies
        del alterFieldAlias, calculateCoreSpecies, importEPU, purgeGDB
        del unique_fish, unique_fish_dict, LicenseError, createTemplateTables
        del generateDatasets, createDatasetTable, createFolders
        del generateSpeciesFilter, generateMasterSpeciesInformation

        # Remove declared globals
        del BASE_DIRECTORY, IMAGE_DIRECTORY, CSV_DIRECTORY, REGION_SHAPEFILE_DIRECTORY
        del MOSAIC_DIRECTORY, ProjectGIS, ProjectToolBox, ProjectGDB, ProjectName
        del BathymetryGDB, ScratchGDB, ScratchFolder, EXPORT_METADATA_DIRECTORY
        del ARCGIS_METADATA_DIRECTORY, INPORT_METADATA_DIRECTORY, LOG_DIRECTORY
        del datasets, geographic_regions, selected_species
        del selected_datasets, listFolder, template_table_dictionary
        #del logger, formatter, ch, selected_years

        # This is a list of local and global variables that are exclude from
        # lists of variables
        exclude_keys = ["main", "exclude_keys", "arcpy", "logFile",
                        "log_file_folder", "log_file" ]

        globalKeys = [key for key in globals().keys() if not key.startswith('__') and key not in exclude_keys]

        if globalKeys:
            msg = f"\n###--->>> Global Keys: {', '.join(globalKeys)} <<<---###\n"
            #msg = "Global Keys: {0}".format(u', '.join('"{0}"'.format(gk) for gk in globalKeys))
            logFile(log_file, msg); del msg
        del globalKeys, exclude_keys, logFile, log_file, log_file_folder, arcpy

        import gc; gc.collect(); del gc