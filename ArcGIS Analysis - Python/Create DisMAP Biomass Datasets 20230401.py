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
# ### ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # #
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
# ### ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # ### # #

import os
import arcpy
import multiprocessing
from time import time, localtime, strftime, gmtime, sleep

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

def addFields(tb, fields, field_definitions):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        if fields:
            field_list = []
            for field in fields:
                msg = f'>-> Adding field {field} to the "{os.path.basename(tb)}" Table'
                print(msg); del msg
                if field in field_definitions.keys():
                    field_definition = field_definitions[field]
                    field_list.append(field_definition)
                    del field_definition
                else:
                    msg = f'>-> Field {field} not in field_definitions'
                    print(msg); del msg
                del field
            #print(fields)

            arcpy.management.AddFields(in_table=tb, field_description=field_list, template="")

            del field_list

        else:
            msg = f'>-> Fields are already in the {os.path.basename(tb)} Table'
            print(msg); del msg

        del tb, field_definitions, fields

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
        print(msg); del msg #logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg #logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function#, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def alterFields(tb):
    try:
         # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        msg = f'> Updating the field aliases in the Table'
        print(msg); del msg

        fields = [f for f in arcpy.ListFields(tb) if not f.required]

        missing_fields = []
        for field in fields:
            field_name = field.name; field
            msg = f'>-> Updating the {field_name} alias'
            print(msg); del msg

            if field_name in field_definitions.keys():
                field_definition = field_definitions[field_name]

                msg = f">--> Altering Field: {field_name}"
                print(msg); del msg

                if field_definition:
                    try:
                        # arcpy.management.AlterField(in_table, field, {new_field_name}, {new_field_alias}, {field_type}, {field_length}, {field_is_nullable}, {clear_field_alias})
                        arcpy.management.AlterField(
                                                    in_table = tb,
                                                    field             = field_definition[0],
                                                    new_field_name    = field_definition[0],
                                                    new_field_alias   = field_definition[2],
                                                    field_length      = field_definition[3],
                                                    field_is_nullable = "NULLABLE",
                                                    clear_field_alias = "DO_NOT_CLEAR",
                                                    )

                    except arcpy.ExecuteError:
                        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
                        print(msg); del msg

                else:
                    msg = f"###---> Add field: {field_name} to field_definitions dictionary<---###"
                    print(msg); del msg

                del field_definition

            else:
                msg = f'>-> Field not found in field_definitions'
                print(msg); del msg
                missing_fields.append(field_name)

            del field, field_name

        for missing_field in missing_fields:
            msg = f"Missing field: {missing_field} in field_definitions dictionary"
            print(msg); del msg
            print(f"\t{field_definitions[missing_field]}")
            del missing_field

        if missing_fields:
            raise Exception

        del tb, fields, missing_fields

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
        print(msg); del msg #logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg #logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function#, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def addMapsToProjectGIS():
    try:
        function = function_name()

        datasets = generateDatasets()

        with arcpy.EnvManager(scratchWorkspace = ScratchFolder, workspace = ProjectGDB):
            tbs = arcpy.ListTables(f"*")
            datasets = [[r for r in group] for group in datasets if group[3] in tbs]
            del tbs

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        if not datasets:
            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

        dataset_maps = [group[6] for group in datasets]
        #print(dataset_maps)

        base_name = os.path.basename(ProjectGIS)
        msg = f"\n###--->>> GIS Project: {base_name} <<<---###"
        print(msg); del msg, base_name

        aprx = arcpy.mp.ArcGISProject(ProjectGIS)
        current_maps = aprx.listMaps()
        current_map_names = [cm.name for cm in current_maps]
        #print(current_map_names)
        add_maps = [am for am in dataset_maps if am not in current_map_names]
        #print(add_maps)
        del dataset_maps, current_map_names, current_maps

        for add_map in add_maps:
            #Create a copy of an existing map
            msg = f"\n###--->>> Adding {add_map} to GIS Project <<<---###"
            print(msg); del msg
            aprx.createMap(f"{add_map}", "Map")
            aprx.save()
            del add_map

        del aprx, datasets, add_maps

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def addMetadata(item):
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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

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
        #msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        #logFile(log_file, msg); del msg

        #msg = f"Table: {os.path.basename(csv_table)}"
        #logFile(log_file, msg); del msg

        # Get  unique list of years from the table
        all_years = unique_values(csv_table, "Year")

        PrintListOfYears = False
        if PrintListOfYears:
            # Print list of years
            msg = f"--> Years: {', '.join([str(y) for y in all_years])}"
            logFile(log_file, msg); del msg

            # Get minimum year (first year) and maximum year (last year)
            min_year, max_year = min(all_years), max(all_years)

            # Print min year
            msg = f"--> Min Year: {min_year} and Max Year: {max_year}"
            logFile(log_file, msg); del msg
            del min_year, max_year
        del PrintListOfYears

        # msg = f"\t Creating {os.path.basename(csv_table)} Table View"
        # logFile(log_file, msg); del msg

        species_table_view = arcpy.management.MakeTableView(csv_table, f'{os.path.basename(csv_table)} Table View')

        unique_species = unique_values(species_table_view, "Species")

        for unique_specie in unique_species:
            # msg = f"\t\t Unique Species: {unique_specie}"
            # logFile(log_file, msg); del msg

            # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
            # The following inputs are layers or table views: "ai_csv"
            arcpy.management.SelectLayerByAttribute(in_layer_or_view=species_table_view, selection_type="NEW_SELECTION", where_clause=f"Species = '{unique_specie}' AND WTCPUE > 0.0")

            all_specie_years = unique_values(species_table_view, "Year")

            #msg = f"\t\t\t Years: {', '.join([str(y) for y in all_specie_years])}"
            #logFile(log_file, msg); del msg

            #msg = f"\t\t Select Species ({unique_specie}) by attribute"
            #logFile(log_file, msg); del msg

            arcpy.management.SelectLayerByAttribute(in_layer_or_view=species_table_view, selection_type="NEW_SELECTION", where_clause=f"Species = '{unique_specie}'")

            #msg = f"\t Set CoreSpecies to Yes or No"
            #logFile(log_file, msg); del msg

            if all_years == all_specie_years:
                # msg = f"\t\t {unique_specie} is a Core Species"
                # logFile(log_file, msg); del msg
                arcpy.management.CalculateField(in_table=species_table_view, field="CoreSpecies", expression="'Yes'", expression_type="PYTHON", code_block="")
            else:
                # msg = f"\t\t @@@@ {unique_specie} is not a Core Species @@@@"
                # logFile(log_file, msg); del msg
                arcpy.management.CalculateField(in_table=species_table_view, field="CoreSpecies", expression="'No'", expression_type="PYTHON", code_block="")

            arcpy.management.SelectLayerByAttribute(species_table_view, "CLEAR_SELECTION")
            del unique_specie, all_specie_years

        #msg = f"\t Deleteing {os.path.basename(csv_table)} Table View"
        #logFile(log_file, msg); del msg

        arcpy.management.Delete(f'{csv_table} Table View')
        del species_table_view, unique_species, all_years
        del csv_table, log_file

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
        print(msg); del msg #logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg #logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function #, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

def compactGDB(gdb):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        base_name = os.path.basename(gdb) #.strip('.gdb')
        msg = f"\n###--->>> Compacting GDB: {base_name} <<<---###"
        print(msg); del msg
        arcpy.Compact_management(gdb)
        msg = arcpy.GetMessages().replace('chr(10)', f'chr(10)#---> Compact {base_name} ')
        msg = f"#---> {msg}\n"
        print(msg); del msg

        del gdb, base_name

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
        print(msg); del msg #logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg #logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function#, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def createAlasakaBathymetry():
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

        # Set Cell Size
        arcpy.env.cellSize = 1000

        # Set Output Coordinate System
        arcpy.env.outputCoordinateSystem = None

        # Set Build Pyramids
        arcpy.env.pyramid ="PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP"

        # Set Build Statistics
        arcpy.env.rasterStatistics = "STATISTICS 1 1"

        # Set Resampling Method
        arcpy.env.resamplingMethod = "NEAREST"

        # Set BATHYMETRY_DIRECTORY
        BATHYMETRY_DIRECTORY = os.path.join(cwd, "Alaska Bathymetry")

        # Set AlaskaGDB
        AlaskaGDB = os.path.join(BASE_DIRECTORY, "Alaska.gdb")

        if not arcpy.Exists(AlaskaGDB): arcpy.CreateFileGDB_management(BASE_DIRECTORY, "Alaska")

# #        arcpy.env.cellSize = "MAXOF"
# #        arcpy.env.cellSizeProjectionMethod = "PRESERVE_RESOLUTION"
# #        arcpy.env.coincidentPoints = "INCLUDE_ALL"
# #        arcpy.env.geographicTransformations = None
# #        arcpy.env.mask = None
# #        arcpy.env.outputCoordinateSystem = None #'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]'
# #        arcpy.env.overwriteOutput = True
# #        arcpy.env.parallelProcessingFactor ="100%"
# #        #arcpy.env.projectCompare = "FULL"
# #        arcpy.env.pyramid ="PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP"
# #        arcpy.env.rasterStatistics = "STATISTICS 1 1"
# #        arcpy.env.resamplingMethod = "NEAREST"
# #        arcpy.env.scratchWorkspace = ScratchGDB
# #        arcpy.env.snapRaster = None
# #        arcpy.env.workspace = AlaskaGDB  ENBS NBS

        ai_bathy         = os.path.join(BATHYMETRY_DIRECTORY, 'AI_IDW_Bathy.grd')
        ebs_bathy        = os.path.join(BATHYMETRY_DIRECTORY, 'EBS_IDW_Bathy.grd')
        goa_bathy        = os.path.join(BATHYMETRY_DIRECTORY, 'GOA_IDW_Bathy.grd')

        ai_bathy_grid    = os.path.join(AlaskaGDB, 'AI_IDW_Bathy_Grid')
        ebs_bathy_grid   = os.path.join(AlaskaGDB, 'EBS_IDW_Bathy_Grid')
        goa_bathy_grid   = os.path.join(AlaskaGDB, 'GOA_IDW_Bathy_Grid')

        ai_bathy_raster  = os.path.join(AlaskaGDB, 'AI_IDW_Bathy_Raster')
        ebs_bathy_raster = os.path.join(AlaskaGDB, 'EBS_IDW_Bathy_Raster')
        goa_bathy_raster = os.path.join(AlaskaGDB, 'GOA_IDW_Bathy_Raster')

        ai_bathymetry    = os.path.join(BathymetryGDB, 'AI_IDW_Bathymetry')
        ebs_bathymetry   = os.path.join(BathymetryGDB, 'EBS_IDW_Bathymetry')
        goa_bathymetry   = os.path.join(BathymetryGDB, 'GOA_IDW_Bathymetry')
        ENBS_bathymetry  = os.path.join(BathymetryGDB, 'ENBS_IDW_Bathymetry')
        NBS_bathymetry   = os.path.join(BathymetryGDB, 'NBS_IDW_Bathymetry')

        msg = f"> Processing Esri Raster Grids"
        logFile(log_file, msg); del msg

        spatial_ref = arcpy.Describe(ai_bathy).spatialReference.name
        msg = f"Spatial Reference for {ai_bathy}: {spatial_ref}"
        logFile(log_file, msg); del msg

        spatial_ref = arcpy.Describe(ai_bathy).spatialReference
        # Set Output Coordinate System
        arcpy.env.outputCoordinateSystem = spatial_ref
        del spatial_ref

        msg = f"> Copy AI_IDW_Bathy.grd to AI_IDW_Bathy_Grid"
        logFile(log_file, msg); del msg

        arcpy.management.CopyRaster(ai_bathy, ai_bathy_grid)
        del ai_bathy

        msg = f"> Copy EBS_IDW_Bathy.grd to EBS_IDW_Bathy_Grid"
        logFile(log_file, msg); del msg

        arcpy.management.CopyRaster(ebs_bathy, ebs_bathy_grid)
        del ebs_bathy

        msg = f"> Copy GOA_IDW_Bathy.grd to GOA_IDW_Bathy_Grid"
        logFile(log_file, msg); del msg

        arcpy.management.CopyRaster(goa_bathy, goa_bathy_grid)
        del goa_bathy

        msg = f"> Converting AI_IDW_Bathy_Grid from positive values to negative"
        logFile(log_file, msg); del msg

        tmp_grid = arcpy.sa.Times(ai_bathy_grid, -1)
        tmp_grid.save(ai_bathy_raster)
        del tmp_grid

        msg = f"> Converting EBS_IDW_Bathy_Grid from positive values to negative"
        logFile(log_file, msg); del msg

        tmp_grid = arcpy.sa.Times(ebs_bathy_grid, -1)
        tmp_grid.save(ebs_bathy_raster)
        del tmp_grid

        msg = f"> Setting values equal to and less than 0 in the GOA_IDW_Bathy_Grid Null values"
        logFile(log_file, msg); del msg

        tmp_grid = arcpy.sa.SetNull(goa_bathy_grid, goa_bathy_grid, "Value <= 0.0")
        tmp_grid.save(goa_bathy_raster+'_SetNull')
        del tmp_grid

        msg = f"> Converting the GOA_IDW_Bathy_Grid from positive values to negative"
        logFile(log_file, msg); del msg

        #arcpy.gp.Times_sa(goa_bathy_raster+'_SetNull', "-1", goa_bathy_raster)
        tmp_grid = arcpy.sa.Times(goa_bathy_raster+'_SetNull', -1)
        tmp_grid.save(goa_bathy_raster)
        del tmp_grid

        msg = f"> Deleteing the GOA_IDW_Bathy Null grid"
        logFile(log_file, msg); del msg

        arcpy.management.Delete(goa_bathy_raster+'_SetNull')

        msg = f"> Appending the AI raster to the GOA grid to ensure complete coverage"
        logFile(log_file, msg); del msg

        extent = arcpy.Describe(goa_bathy_raster).extent
        X_Min, Y_Min, X_Max, Y_Max = extent.XMin-(1000 * 366), extent.YMin-(1000 * 80), extent.XMax, extent.YMax
        extent = f"{X_Min} {Y_Min} {X_Max} {Y_Max}"
        arcpy.env.extent = extent

        arcpy.management.Append(inputs = ai_bathy_raster, target = goa_bathy_raster, schema_type="TEST", field_mapping="", subtype="")

        msg = f"> Cliping GOA Raster"
        logFile(log_file, msg); del msg

        arcpy.management.Clip(goa_bathy_raster, extent, goa_bathy_raster+"_Clip")
        del extent

        msg = f"> Copying GOA Raster"
        logFile(log_file, msg); del msg
        arcpy.management.CopyRaster(goa_bathy_raster+"_Clip", goa_bathy_raster)

        arcpy.management.Delete(goa_bathy_raster+"_Clip")

        msg = f"> Appending the EBS raster to the AI grid to ensure complete coverage"
        logFile(log_file, msg); del msg

        extent = arcpy.Describe(ai_bathy_raster).extent
        X_Min, Y_Min, X_Max, Y_Max = extent.XMin, extent.YMin, extent.XMax, extent.YMax
        extent = f"{X_Min} {Y_Min} {X_Max} {Y_Max}"
        arcpy.env.extent = extent
        del X_Min, Y_Min, X_Max, Y_Max

        arcpy.management.Append(inputs = ebs_bathy_raster, target = ai_bathy_raster, schema_type="TEST", field_mapping="", subtype="")

        msg = f"> Cliping AI Raster"
        logFile(log_file, msg); del msg

        arcpy.management.Clip(ai_bathy_raster, extent, ai_bathy_raster+"_Clip")
        del extent

        msg = f"> Copying AI Raster"
        logFile(log_file, msg); del msg
        arcpy.management.CopyRaster(ai_bathy_raster+"_Clip", ai_bathy_raster)

        arcpy.management.Delete(ai_bathy_raster+"_Clip")

        arcpy.ClearEnvironment("extent")

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        dataset_product_code = "AI_IDW"
        geographicarea = f"{dataset_product_code}_Shape"
        geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
        #print(geographicarea_sr)

        datasetcode_sr = arcpy.SpatialReference(geographicarea_sr)
        del geographicarea_sr, dataset_product_code, geographicarea

        arcpy.env.outputCoordinateSystem = datasetcode_sr; del datasetcode_sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

        msg = f"> Copy AI_IDW_Bathymetry_Raster to AI_IDW_Bathymetry"
        logFile(log_file, msg); del msg

        arcpy.management.CopyRaster(ai_bathy_raster, ai_bathymetry)

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        dataset_product_code = "EBS_IDW"
        geographicarea = f"{dataset_product_code}_Shape"
        geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
        #print(geographicarea_sr)

        datasetcode_sr = arcpy.SpatialReference(geographicarea_sr)
        del geographicarea_sr, dataset_product_code, geographicarea

        arcpy.env.outputCoordinateSystem = datasetcode_sr; del datasetcode_sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

        msg = f"> Copy EBS_IDW_Bathymetry_Raster to EBS_IDW_Bathymetry"
        logFile(log_file, msg); del msg

        arcpy.management.CopyRaster(ebs_bathy_raster, ebs_bathymetry)

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        dataset_product_code = "ENBS_IDW"
        geographicarea = f"{dataset_product_code}_Shape"
        geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
        #print(geographicarea_sr)

        datasetcode_sr = arcpy.SpatialReference(geographicarea_sr)
        del geographicarea_sr, dataset_product_code, geographicarea

        arcpy.env.outputCoordinateSystem = datasetcode_sr; del datasetcode_sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

        msg = f"> Copy EBS_IDW_Bathymetry_Raster to ENBS_IDW_Bathymetry"
        logFile(log_file, msg); del msg

        arcpy.management.CopyRaster(ebs_bathy_raster, ENBS_bathymetry)

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        dataset_product_code = "NBS_IDW"
        geographicarea = f"{dataset_product_code}_Shape"
        geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
        #print(geographicarea_sr)

        datasetcode_sr = arcpy.SpatialReference(geographicarea_sr)
        del geographicarea_sr, dataset_product_code, geographicarea

        arcpy.env.outputCoordinateSystem = datasetcode_sr; del datasetcode_sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

        msg = f"> Copy EBS_IDW_Bathymetry_Raster to NBS_IDW_Bathymetry"
        logFile(log_file, msg); del msg

        arcpy.management.CopyRaster(ebs_bathy_raster, NBS_bathymetry)

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        dataset_product_code = "GOA_IDW"
        geographicarea = f"{dataset_product_code}_Shape"
        geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
        #print(geographicarea_sr)

        datasetcode_sr = arcpy.SpatialReference(geographicarea_sr)
        del geographicarea_sr, dataset_product_code, geographicarea

        arcpy.env.outputCoordinateSystem = datasetcode_sr; del datasetcode_sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

        msg = f"> Copy GOA_IDW_Bathymetry_Raster to GOA_IDW_Bathymetry"
        logFile(log_file, msg); del msg

        arcpy.management.CopyRaster(goa_bathy_raster, goa_bathymetry)

        del BATHYMETRY_DIRECTORY, AlaskaGDB, ai_bathy_grid, ebs_bathy_grid
        del goa_bathy_grid, ai_bathy_raster, ebs_bathy_raster, goa_bathy_raster
        del ai_bathymetry, ebs_bathymetry, goa_bathymetry
        del ENBS_bathymetry, NBS_bathymetry

         #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def createEmptyTempMetadataXML():
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        from arcpy import metadata as md

##        # Set a start time so that we can see how log things take
##        start_time = time()
##
##        # For benchmarking.
##        #timestr = strftime("%Y%m%d-%H%M%S")
##        timestr = strftime("%a %b %d %I %M %S %p", localtime())
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

        empty_xml = os.path.join(ARCGIS_METADATA_DIRECTORY, "empty.xml")
        temp_xml = os.path.join(ARCGIS_METADATA_DIRECTORY, "temp.xml")

        # Create a new Metadata object and add some content to it
        new_md = md.Metadata()
        # Empty XML Files
        new_md.saveAsXML(empty_xml)

        # Temp XML File
        new_md.title = 'My Title'
        new_md.tags = 'Tag1, Tag2'
        new_md.summary = 'My Summary'
        new_md.description = 'My Description'
        new_md.credits = 'My Credits'
        new_md.accessConstraints = 'My Access Constraints'
        new_md.saveAsXML(temp_xml)

        prettyXML(empty_xml)
        prettyXML(temp_xml)

        del empty_xml, temp_xml, new_md, md

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def createDatasetTableMetadata():
    """Create Dataset Table"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        from arcpy import metadata as md

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        arcpy.SetLogHistory(False)

        datasets = "Datasets"
        datasets_table = os.path.join(ProjectGDB, datasets)

        msg = f'> Creating Metadata for: {os.path.basename(datasets_table)}'
        logFile(log_file, msg); del msg

        datasets_md = md.Metadata(datasets_table)

        empty_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"empty.xml")

        #datasets_md.importMetadata(empty_metadata, 'ARCGIS_METADATA')
        datasets_md.importMetadata(empty_metadata, 'DEFAULT')
        #datasets_md.synchronize("SELECTIVE")
        #datasets_md.synchronize("ACCESSED", 0)
        #datasets_md.synchronize("NOT_CREATED", 0)
        #datasets_md.synchronize("CREATED", 0)
        #datasets_md.synchronize("ALWAYS")
        #datasets_md.synchronize("OVERWRITE")
        datasets_md.save()
        datasets_md.reload()
        del empty_metadata, datasets_md

##        datasets_md = md.Metadata(datasets_table)
##
##        template_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, "Indicators Template")
##
##        #datasets_md.importMetadata(template_metadata, 'ARCGIS_METADATA')
##        datasets_md.importMetadata(template_metadata, 'DEFAULT')
##        datasets_md.save()
##        datasets_md.reload()
##        #datasets_md.synchronize("SELECTIVE")
##        #datasets_md.synchronize("ACCESSED", 0)
##        #datasets_md.synchronize("NOT_CREATED", 0)
##        #datasets_md.synchronize("CREATED", 0)
##        #datasets_md.synchronize("ALWAYS")
##        #datasets_md.synchronize("OVERWRITE")
##        datasets_md.save()
##        datasets_md.reload()
##        del template_metadata, datasets_md

        datasets_md = md.Metadata(datasets_table)

        msg = "\t\t Title: {0}".format(datasets_md.title)
        print(msg); del msg

        msg = "\t\t Tags: {0}".format(datasets_md.tags)
        print(msg); del msg

        msg = "\t\t Summary: {0}".format(datasets_md.summary)
        print(msg); del msg

        msg = "\t\t Description: {0}".format(datasets_md.description)
        print(msg); del msg

        msg = "\t\t Credits: {0}".format(datasets_md.credits)
        print(msg); del msg

        msg = "\t\t Access Constraints: {0}".format(datasets_md.accessConstraints)
        print(msg); del msg

        # Delete all geoprocessing history and any enclosed files from the item's metadata
##        if not datasets_md.isReadOnly:
##            datasets_md.deleteContent('GPHISTORY')
##            datasets_md.deleteContent('ENCLOSED_FILES')
##            datasets_md.deleteContent('THUMBNAIL')
##            datasets_md.save()
##            datasets_md.reload()

        export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{datasets}.xml")

        datasets_md.saveAsXML(export_metadata.replace(".xml", " EXACT_COPY.xml"), 'EXACT_COPY') # Default
        datasets_md.saveAsXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO.xml"), 'REMOVE_ALL_SENSITIVE_INFO')
        #datasets_md.saveAsXML(export_metadata.replace(".xml", " REMOVE_MACHINE_NAMES.xml"), 'REMOVE_MACHINE_NAMES')
        datasets_md.saveAsXML(export_metadata.replace(".xml", " TEMPLATE.xml"), 'TEMPLATE')
        #prettyXML(export_metadata.replace(".xml", " EXACT_COPY.xml"))
        #prettyXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO.xml"))
        #prettyXML(export_metadata.replace(".xml", " TEMPLATE.xml"))

##        datasets_md.synchronize("ACCESSED", 0)
##        datasets_md.save()
##        datasets_md.reload()
##
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " EXACT_COPY ACCESSED.xml"), 'EXACT_COPY')
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO ACCESSED.xml"), 'REMOVE_ALL_SENSITIVE_INFO')
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " TEMPLATE ACCESSED.xml"), 'TEMPLATE')
##
##        prettyXML(export_metadata.replace(".xml", " EXACT_COPY ACCESSED.xml"))
##        prettyXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO ACCESSED.xml"))
##        prettyXML(export_metadata.replace(".xml", " TEMPLATE ACCESSED.xml"))
##
##        datasets_md.synchronize("ALWAYS")
##        datasets_md.save()
##        datasets_md.reload()
##
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " EXACT_COPY ALWAYS.xml"), 'EXACT_COPY')
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO ALWAYS.xml"), 'REMOVE_ALL_SENSITIVE_INFO')
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " TEMPLATE ALWAYS.xml"), 'TEMPLATE')
##
##        prettyXML(export_metadata.replace(".xml", " EXACT_COPY ALWAYS.xml"))
##        prettyXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO ALWAYS.xml"))
##        prettyXML(export_metadata.replace(".xml", " TEMPLATE ALWAYS.xml"))

##        datasets_md.synchronize("CREATED", 0)
##        datasets_md.save()
##        datasets_md.reload()
##
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " EXACT_COPY CREATED.xml"), 'EXACT_COPY')
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO CREATED.xml"), 'REMOVE_ALL_SENSITIVE_INFO')
##        #datasets_md.saveAsXML(export_metadata.replace(".xml", " TEMPLATE CREATED.xml"), 'TEMPLATE')
##
##        prettyXML(export_metadata.replace(".xml", " EXACT_COPY CREATED.xml"))
##        prettyXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO CREATED.xml"))
##        #prettyXML(export_metadata.replace(".xml", " TEMPLATE CREATED.xml"))

##        datasets_md.synchronize("NOT_CREATED", 0)
##        datasets_md.save()
##        datasets_md.reload()
##
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " EXACT_COPY NOT_CREATED.xml"), 'EXACT_COPY')
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO NOT_CREATED.xml"), 'REMOVE_ALL_SENSITIVE_INFO')
##        #datasets_md.saveAsXML(export_metadata.replace(".xml", " TEMPLATE NOT_CREATED.xml"), 'TEMPLATE')
##
##        prettyXML(export_metadata.replace(".xml", " EXACT_COPY NOT_CREATED.xml"))
##        prettyXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO NOT_CREATED.xml"))
##        #prettyXML(export_metadata.replace(".xml", " TEMPLATE NOT_CREATED.xml"))

##        datasets_md.synchronize("OVERWRITE")
##        datasets_md.save()
##        datasets_md.reload()
##
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " EXACT_COPY OVERWRITE.xml"), 'EXACT_COPY')
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO OVERWRITE.xml"), 'REMOVE_ALL_SENSITIVE_INFO')
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " TEMPLATE OVERWRITE.xml"), 'TEMPLATE')
##
##        prettyXML(export_metadata.replace(".xml", " EXACT_COPY OVERWRITE.xml"))
##        prettyXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO OVERWRITE.xml"))
##        prettyXML(export_metadata.replace(".xml", " TEMPLATE OVERWRITE.xml"))
##
##        datasets_md.synchronize("SELECTIVE")
##        datasets_md.save()
##        datasets_md.reload()
##
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " EXACT_COPY SELECTIVE.xml"), 'EXACT_COPY')
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO SELECTIVE.xml"), 'REMOVE_ALL_SENSITIVE_INFO')
##        datasets_md.saveAsXML(export_metadata.replace(".xml", " TEMPLATE SELECTIVE.xml"), 'TEMPLATE')
##
##        prettyXML(export_metadata.replace(".xml", " EXACT_COPY SELECTIVE.xml"))
##        prettyXML(export_metadata.replace(".xml", " REMOVE_ALL_SENSITIVE_INFO SELECTIVE.xml"))
##        prettyXML(export_metadata.replace(".xml", " TEMPLATE SELECTIVE.xml"))


        # Save the modified ArcGIS metadata output back to the source item
        #tgt_item_md = md.Metadata(target_file_path)
        #src_item_md.copy(tgt_item_md)
        #src_item_md.save()


        del datasets_md
        del datasets, datasets_table, export_metadata
        del md

        compactGDB(ProjectGDB)

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

    # This code is executed only if no exceptions were raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program). Notice that if the else block is executed, then the except block
    # is not, and vice versa. This block is optional.
    else:
        # Use pass to skip this code block
        pass

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def createDatasetTable():
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

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        datasets = "Datasets"
        input_datasets_csv_table = os.path.join(CSV_DIRECTORY, f"{datasets}.csv")
        datasets_table = os.path.join(ProjectGDB, datasets)

        # Execute CreateTable
        #arcpy.management.CreateTable(ProjectGDB, datasets, template_datasets_path, "", "")
        arcpy.management.CreateTable(ProjectGDB, datasets, "", "", "")

        tb_fields = [f.name for f in arcpy.ListFields(datasets_table) if f.type not in ['Geometry', 'OID']]
        tb_definition_fields = table_definitions[datasets]
        fields = [f for f in tb_definition_fields if f not in tb_fields]

        addFields(datasets_table, fields, field_definitions)
        del tb_fields, tb_definition_fields, fields

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
                             dtype = {# DatasetCode    CSVFile    TransformUnit    TableName    GeographicArea  CellSize    PointFeatureType    FeatureClassName
                                      # Region    Season    DateCode    Status    DistributionProjectCode    DistributionProjectName    SummaryProduct    FilterRegion    FilterSubRegion
                                      # FeatureServiceName    FeatureServiceTitle    MosaicName    MosaicTitle    ImageServiceName    ImageServiceTitle
                                      "DatasetCode"             : str,
                                      "CSVFile"                 : str,
                                      "TransformUnit"           : str,
                                      "TableName"               : str,
                                      "GeographicArea"          : str,
                                      "CellSize"                : 'uint16',
                                      "PointFeatureType"        : str,
                                      "FeatureClassName"        : str,
                                      "Region"                  : str,
                                      "Season"                  : str,
                                      "DateCode"                : str,
                                      "Status"                  : str,
                                      "DistributionProjectCode" : str,
                                      "DistributionProjectName" : str,
                                      "SummaryProduct"          : str,
                                      "FilterRegion"            : str,
                                      "FilterSubRegion"         : str,
                                      "FeatureServiceName"      : str,
                                      "FeatureServiceTitle"     : str,
                                      "MosaicName"              : str,
                                      "MosaicTitle"             : str,
                                      "ImageServiceName"        : str,
                                      "ImageServiceTitle"       : str,

                                     },
                             )
        del input_datasets_csv_table

        msg = f'>-> Defining the column names.'
        logFile(log_file, msg); del msg

        # The original column names from the CSV files are not very
        # reader friendly, so we are making some changes here
        #
        df.columns = ["DatasetCode", "CSVFile", "TransformUnit", "TableName", "GeographicArea", "CellSize", "PointFeatureType", "FeatureClassName", "Region", "Season", "DateCode", "Status", "DistributionProjectCode", "DistributionProjectName", "SummaryProduct", "FilterRegion", "FilterSubRegion", "FeatureServiceName", "FeatureServiceTitle", "MosaicName", "MosaicTitle", "ImageServiceName", "ImageServiceTitle",]

        # Replace NaN with an empty string. When pandas reads a cell
        # with missing data, it asigns that cell with a Null or nan
        # value. So, we are changing that value to an empty string of ''.

        df.fillna('', inplace=True)

        msg = f'>-> Creating the {datasets} Geodatabase Table'
        logFile(log_file, msg); del msg

        # ###--->>> Numpy Datatypes
        # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm

        # Get max length of all columns in the dataframe
        # max_length_all_cols = {col: df.loc[:, col].astype(str).apply(len).max() for col in df.columns}
        # type_dict = {'TEXT' : "S", 'SHORT' : "u4", 'DOUBLE' : 'd', 'DATE' : 'M8[us]' }

        # print([f'S{max_length_all_cols[v]}' for v in max_length_all_cols])
        # print([f'{v} : {max_length_all_cols[v]},' for v in max_length_all_cols])
        # print([f'S{field_definitions[v][3]}' for v in max_length_all_cols])
        # print([f'{v} S{field_definitions[v][3]}' for v in max_length_all_cols])
        # print([f'{field_definitions[v][1]} {field_definitions[v][3]}' for v in max_length_all_cols])

        # small = 10
        # big   = 20
        # multiplier = lambda x: big if x > small else small
        # nearest = lambda x: multiplier(x) * math.ceil(x / multiplier(x))

        # for key in max_length_all_cols:
        #     print(f"\t# # {key:23} = {max_length_all_cols[key]:3} ({nearest(max_length_all_cols[key]):2})")
        #    max_length_all_cols[key] = nearest(max_length_all_cols[key])

        # print([f'{v} : {max_length_all_cols[v]},' for v in max_length_all_cols])
        # print([f'S{max_length_all_cols[v]}' for v in max_length_all_cols])
        # del max_length_all_cols


        #print('DataFrame\n----------\n', df.head(10))
        #print('\nDataFrame datatypes :\n', df.dtypes)
        #columns = [str(c) for c in df.dtypes.index.tolist()]
        column_names = list(df.columns)
        #print(column_names)
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
                          # DatasetCode    CSVFile    TransformUnit    TableName    GeographicArea    CellSize    PointFeatureType    FeatureClassName
                                      # Region    Season    DateCode    Status    DistributionProjectCode    DistributionProjectName    SummaryProduct    FilterRegion    FilterSubRegion
                                      # FeatureServiceName    FeatureServiceTitle    MosaicName    MosaicTitle    ImageServiceName    ImageServiceTitle
                       #  DatasetCode    CSVFile   TransformUnit  TableName    GeographicArea    CellSize    PointFeatureType    FeatureClassName Region    Season    DateCode    Status    DistributionProjectCode    DistributionProjectName    SummaryProduct    FilterRegion    FilterSubRegion  FeatureServiceName    FeatureServiceTitle    MosaicName    MosaicTitle    ImageServiceName    ImageServiceTitle
        column_formats = ['S20',        'S20',     'S10',         'S20',      'S20',             'u4',        'S20',              'S40',           'S40',     'S10',   'S10',      'S10',    'S10',                    'S60',                      'S10',           'S25',          'S40',           'S40',                'S60',                  'S20',        'S60',         'S40',              'S60']
           #            ['S20',         'S20',     'S10',         'S20',      'S20',             'S10',       'S20',              'S40',           'S40',     'S10',   'S10',      'S10',    'S10',                    'S60',                      'S10',           'S20',          'S40',           'S40',                'S60',                  'S20',        'S60',         'S40',              'S60']

        # Get max length of all columns in the dataframe
        # max_length_all_cols = {col: df.loc[:, col].astype(str).apply(len).max() for col in df.columns}
        # type_dict = {'TEXT' : "S", 'SHORT' : "u4", 'DOUBLE' : 'd', 'DATE' : 'M8[us]' }

        # print([f'S{max_length_all_cols[v]}' for v in max_length_all_cols])
        # print([f'{v} : {max_length_all_cols[v]},' for v in max_length_all_cols])
        # print([f'S{field_definitions[v][3]}' for v in max_length_all_cols])
        # print([f'{v} S{field_definitions[v][3]}' for v in max_length_all_cols])
        # print([f'{field_definitions[v][1]} {field_definitions[v][3]}' for v in max_length_all_cols])

        # small = 10
        # big   = 20
        # multiplier = lambda x: big if x > small else small
        # nearest = lambda x: multiplier(x) * math.ceil(x / multiplier(x))

        # for key in max_length_all_cols:
        #     print(f"\t# # {key:23} = {max_length_all_cols[key]:3} ({nearest(max_length_all_cols[key]):2})")
        #    max_length_all_cols[key] = nearest(max_length_all_cols[key])

        # print([f'{v} : {max_length_all_cols[v]},' for v in max_length_all_cols])
        # print([f'S{max_length_all_cols[v]}' for v in max_length_all_cols])
        # del max_length_all_cols

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
            logFile(log_file, msg); del msg

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
            logFile(log_file, msg); del msg

        msg = f'>-> Copying the Datasets Table from memory to the GDB'
        logFile(log_file, msg); del msg

        arcpy.management.CopyRows(tmp_table, datasets_table, "")

        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        msg = f'>-> Updating the field aliases for the {os.path.basename(datasets_table)} Table'
        logFile(log_file, msg); del msg

        # Alter Field Aliases
        alterFields(datasets_table)

        #msg = f'>-> Adding metadata to the {datasets} Table'
        #logFile(log_file, msg); del msg

        # Add Metadata
        #addMetadata(datasets_table)

        compactGDB(ProjectGDB)

        ExportDatasetsTable = False
        if ExportDatasetsTable:
            # Create TAB file
            arcpy.conversion.ExportTable(in_table=datasets_table, out_table= os.path.join(CSV_DIRECTORY, f"{datasets}.cav"), where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")
        else:
            arcpy.conversion.ExportTable(in_table=datasets_table, out_table= os.path.join(CSV_DIRECTORY, f"_{datasets}.cav"), where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")
        del ExportDatasetsTable

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
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        print(msg); del msg #logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg #logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function#, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def createFolders(basefolder):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        print(f"Basefolder: {os.path.basename(basefolder)}")
        os.chdir(basefolder); del basefolder

        datasets = generateDatasets()

        #print(len(datasets))
        for i in range(len(datasets)):
            datasetcode = datasets[i][1]
            del i
            try:
                print(f"\tCreating folder: {datasetcode}")
                os.makedirs(datasetcode)
            except FileExistsError:
                pass
            del datasetcode

        del datasets

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def createGebcoBathymetry():
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

        # Set Cell Size
        arcpy.env.cellSize = 1000

        # Set Output Coordinate System
        arcpy.env.outputCoordinateSystem = None

        # Set Build Pyramids
        arcpy.env.pyramid ="PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP"

        # Set Build Statistics
        arcpy.env.rasterStatistics = "STATISTICS 1 1"

        # Set Resampling Method
        arcpy.env.resamplingMethod = "NEAREST"

        # Set BATHYMETRY_DIRECTORY
        BATHYMETRY_DIRECTORY = os.path.join(cwd, "GEBCO Bathymetry")

        # Set GebcoGDB
        GebcoGDB = os.path.join(BASE_DIRECTORY, "GEBCO.gdb")

        if not arcpy.Exists(GebcoGDB): arcpy.CreateFileGDB_management(BASE_DIRECTORY, "GEBCO")

##        arcpy.env.cellSize = "MAXOF"
##        arcpy.env.cellSizeProjectionMethod = "PRESERVE_RESOLUTION"
##        arcpy.env.coincidentPoints = "INCLUDE_ALL"
##        arcpy.env.geographicTransformations = None
##        arcpy.env.mask = None
##        arcpy.env.outputCoordinateSystem = None #'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]'
##        arcpy.env.overwriteOutput = True
##        arcpy.env.parallelProcessingFactor ="100%"
##        #arcpy.env.projectCompare = "FULL"
##        arcpy.env.pyramid ="PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP"
##        arcpy.env.rasterStatistics = "STATISTICS 1 1"
##        arcpy.env.resamplingMethod = "NEAREST"
##        arcpy.env.scratchWorkspace = ScratchGDB
##        arcpy.env.snapRaster = None
##        arcpy.env.workspace = AlaskaGDB

        msg = f"> Processing GEBCO Raster Grids"
        logFile(log_file, msg); del msg

        # Aleutian Islands (AI) = N 54.6 W -171.2 E -165.2 S 50.4
        #     'gebco_2022_n54.6_s50.4_w-171.2_e-165.2.asc'
        # Eastern Bering Sea (EBS) = N 61.4 W -179.2 E -157.2 S 53.8
        #     'gebco_2022_n61.4_s53.8_w-179.2_e-157.2.asc'
        # Gulf of Alaska (GOA) = N 59.2 W -173.2 E -130.2 S 52.2
        #     'gebco_2022_n59.2_s52.2_w-173.2_e-130.2.asc'
        # Gulf of Mexico (GMEX) = N 30.6 W -97.4 E -81.6 S 25.8
        #     'gebco_2022_n30.6_s25.8_w-97.4_e-81.6.asc'
        # Hawai'i Islands (HI) = N 22.4 W -160.2 E -154.8 S 18.8
        #     'gebco_2022_n22.4_s18.8_w-160.2_e-154.8.asc'
        # Northeast US Fall (NEUS_F) = N 44.8 W -75.8 E -65.4 S 35.0
        #     'gebco_2022_n44.8_s35.0_w-75.8_e-65.4.asc'
        # Northeast US Spring (NEUS_S) = N 44.8 W -75.8 E -65.4 S 35.0
        #     'gebco_2022_n44.8_s35.0_w-75.8_e-65.4.asc'
        # Southeast US Spring (SEUS_SPR) = N 35.4 W -81.4 E -75.6 S 28.6
        #     'gebco_2022_n35.4_s28.6_w-81.4_e-75.6.asc'
        # Southeast US Summer (SEUS_SUM) = N 35.4 W -81.4 E -75.6 S 28.6
        #     'gebco_2022_n35.4_s28.6_w-81.4_e-75.6.asc'
        # Southeast US Fall (SEUS_FALL) = N 35.4 W -81.4 E -75.6 S 28.6
        #     'gebco_2022_n35.4_s28.6_w-81.4_e-75.6.asc'
        # West Coast Annual (WC_ANN) = N 48.6 W -126.0 E -115.8 S 32.0
        #     'gebco_2022_n48.6_s32.0_w-126.0_e-115.8.asc'
        # West Coast Triennial (WC_TRI) = N 49.2 W -126.6 E -121.6 S 36.0
        #     'gebco_2022_n49.2_s36.0_w-126.6_e-121.6.asc'

        gebco_dict = {
                       'GMEX'     : 'gebco_2022_n30.6_s25.8_w-97.4_e-81.6.asc',
                       'NEUS_FAL' : 'gebco_2022_n44.8_s35.0_w-75.8_e-65.4.asc',
                       'NEUS_SPR' : 'gebco_2022_n44.8_s35.0_w-75.8_e-65.4.asc',
                       'SEUS_FAL' : 'gebco_2022_n35.4_s28.6_w-81.4_e-75.6.asc',
                       'SEUS_SPR' : 'gebco_2022_n35.4_s28.6_w-81.4_e-75.6.asc',
                       'SEUS_SUM' : 'gebco_2022_n35.4_s28.6_w-81.4_e-75.6.asc',
                       'WC'       : 'gebco_2022_n48.6_s32.0_w-126.0_e-115.8.asc',
                       'WC_ANN'   : 'gebco_2022_n48.6_s32.0_w-126.0_e-115.8.asc',
                       'WC_TRI'   : 'gebco_2022_n49.2_s36.0_w-126.6_e-121.6.asc',
                      }

        datasets = generateDatasets()

        datasets = [[r for r in group] for group in datasets if group[0] in gebco_dict.keys()]


        # Start looping over the datasets array as we go region by region.
        for i in range(len(datasets)):
            # Assigning variables from items in the chosen table list
            datasetcode             = datasets[i][0]
            geographicarea          = datasets[i][4]
            region                  = datasets[i][8]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"
            del distributionprojectcode

            gebco_grid = os.path.join(BATHYMETRY_DIRECTORY, f'{gebco_dict[datasetcode]}')

            bathy_grid = os.path.join(GebcoGDB, f'{dataset_product_code}_Bathy_Grid')

            bathy_raster = os.path.join(GebcoGDB, f'{dataset_product_code}_Bathy_Raster')

            bathymetry = os.path.join(GebcoGDB, f'{dataset_product_code}_Bathymetry')

            msg = f'Creating the {region} GEBCO Dataset'
            logFile(log_file, msg); del msg

            del region

            msg = f"> Copy {gebco_dict[datasetcode]} to {os.path.basename(bathy_grid)}"
            logFile(log_file, msg); del msg

            # Set Build Pyramids
            arcpy.env.pyramid ="PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP"

            # Set Build Statistics
            arcpy.env.rasterStatistics = "STATISTICS 1 1"

            # Set Resampling Method
            arcpy.env.resamplingMethod = "NEAREST"

            # Execute ASCIIToRaster
            arcpy.conversion.ASCIIToRaster(gebco_grid, bathy_grid, "FLOAT")

            msg = f"> Define projection for {os.path.basename(bathy_grid)}"
            logFile(log_file, msg); del msg

            arcpy.management.DefineProjection(bathy_grid, gebco_grid.replace('.asc', '.prj'))

            # Cleanup after last use
            del gebco_grid

            msg = f"> Project Raster to create: {os.path.basename(bathy_raster)}"
            logFile(log_file, msg); del msg

            # Get the reference system defined for the region in datasets
            # Set the output coordinate system to what is needed for the
            # DisMAP project
            geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
            #print(geographicarea_sr)
            del geographicarea

            datasetcode_sr = arcpy.SpatialReference(geographicarea_sr)
            del geographicarea_sr

            if datasetcode_sr.linearUnitName == "Kilometer":
                arcpy.env.cellSize = 1
            elif datasetcode_sr.linearUnitName == "Meter":
                arcpy.env.cellSize = 1000

            arcpy.env.outputCoordinateSystem = datasetcode_sr #; del datasetcode_sr
            arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

            # Project Raster management
            arcpy.ProjectRaster_management(in_raster = bathy_grid, out_raster = bathy_raster, out_coor_system = datasetcode_sr)

            # Cleanup after last use
            del datasetcode_sr, bathy_grid

            msg = f"> Set Null for positive elevation values to create: {os.path.basename(bathymetry)}"
            logFile(log_file, msg); del msg

            tmp_grid = arcpy.sa.SetNull(bathy_raster, bathy_raster, "Value >= 0.0")
            tmp_grid.save(bathymetry)
            # Cleanup after last use
            del tmp_grid, bathy_raster

            msg = f"> Copying: {os.path.basename(bathymetry)} to Bathymetry GDB"
            logFile(log_file, msg); del msg

            # Set Build Pyramids
            arcpy.env.pyramid ="PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP"

            # Set Build Statistics
            arcpy.env.rasterStatistics = "STATISTICS 1 1"

            arcpy.management.CopyRaster(bathymetry, os.path.join(BathymetryGDB, f"{dataset_product_code}_Bathymetry"))

            # Cleadup after last use
            del datasetcode, bathymetry, dataset_product_code

        del datasets, BATHYMETRY_DIRECTORY, GebcoGDB, gebco_dict

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def createHawaiiBathymetry():
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

        # Set Cell Size
        arcpy.env.cellSize = 500

        # Set Output Coordinate System
        arcpy.env.outputCoordinateSystem = None

        # Set Build Pyramids
        arcpy.env.pyramid ="PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP"

        # Set Build Statistics
        arcpy.env.rasterStatistics = "STATISTICS 1 1"

        # Set Resampling Method
        arcpy.env.resamplingMethod = "NEAREST"

        # Set BATHYMETRY_DIRECTORY
        BATHYMETRY_DIRECTORY = os.path.join(cwd, "Hawaii Bathymetry")

        HawaiiGDB = os.path.join(BASE_DIRECTORY, "HAWAII_500m.gdb")

        if not arcpy.Exists(HawaiiGDB): arcpy.CreateFileGDB_management(BASE_DIRECTORY, "HAWAII_500m")

        hi_bathy_grid  = os.path.join(BATHYMETRY_DIRECTORY, 'BFISH_PSU.shp')

        hi_bathy_raster  = os.path.join(HawaiiGDB, 'HI_IDW_Bathy_Raster')

        hi_bathymetry    = os.path.join(HawaiiGDB, 'HI_IDW_Bathymetry')

##        arcpy.env.cellSize = "MAXOF"
##        arcpy.env.cellSizeProjectionMethod = "PRESERVE_RESOLUTION"
##        arcpy.env.coincidentPoints = "INCLUDE_ALL"
##        arcpy.env.geographicTransformations = None
##        arcpy.env.mask = None
##        arcpy.env.outputCoordinateSystem = None #'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]'
##        arcpy.env.overwriteOutput = True
##        arcpy.env.parallelProcessingFactor ="100%"
##        #arcpy.env.projectCompare = "FULL"
##        arcpy.env.pyramid ="PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP"
##        arcpy.env.rasterStatistics = "STATISTICS 1 1"
##        arcpy.env.resamplingMethod = "NEAREST"
##        arcpy.env.scratchWorkspace = ScratchGDB
##        arcpy.env.snapRaster = None
##        arcpy.env.workspace = AlaskaGDB

        msg = f"Processing Hawaii Grids"
        logFile(log_file, msg); del msg

        msg = f"> Converting Hawaii Polygon Grid to a Raster"
        logFile(log_file, msg); del msg

        arcpy.PolygonToRaster_conversion(in_features = hi_bathy_grid, value_field = "Depth_MEDI", out_rasterdataset = hi_bathy_raster, cell_assignment="CELL_CENTER", priority_field="NONE", cellsize="500")
        #
        tmp_grid = arcpy.sa.Times(hi_bathy_raster, -1.0)
        tmp_grid.save(hi_bathymetry)
        del tmp_grid

        msg = f"> Copy Hawaii Raster to the Bathymetry GDB"
        logFile(log_file, msg); del msg

        arcpy.management.CopyRaster(hi_bathymetry, os.path.join(BathymetryGDB, "HI_IDW_Bathymetry"))

        del  BATHYMETRY_DIRECTORY, HawaiiGDB, hi_bathy_grid, hi_bathy_raster, hi_bathymetry

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def createMapLayers():
    """Create Map Layers"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

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

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

    # ###--->>> Preprocessing Setup Start
        arcpy.env.overwriteOutput = True

        aprx = arcpy.mp.ArcGISProject(ProjectGIS)

        CreateMaps = True
        if CreateMaps:
            msg = f"> Createing Maps."
            logFile(log_file, msg); del msg

            datasets = generateDatasets()

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                fcs = arcpy.ListFeatureClasses("*_Sample_Locations")
                datasets = [[r for r in group] for group in datasets if group[7] in fcs]
                del fcs

            if FilterDatasets:
                datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

            if not datasets:
                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            # ###---> Remving all Maps
            current_maps = [cm for cm in aprx.listMaps()]
            if current_maps:
                for current_map in current_maps:
                    print(f"Removing: {current_map.name}")
                    aprx.deleteItem(current_map)
                    del current_map
            else:
                print(f"No maps to remove")
            aprx.save()
            del current_maps

            # ###---> Create DisMAP Regions Map
            maptitle = "DisMAP Regions"

            msg = f" > Creating Map: {maptitle}"
            logFile(log_file, msg); del msg

            #aprx = arcpy.mp.ArcGISProject(ProjectGIS)
            aprx.createMap(f"{maptitle}", "Map")
            aprx.save()

            # ###---> Create other Maps

            for i in range(len(datasets)):
                datasetcode             = datasets[i][0]
                featureclassname        = datasets[i][7]
                region                  = datasets[i][8]
                season                  = datasets[i][9]
                datecode                = datasets[i][10]
                distributionprojectcode = datasets[i][12]
                featureservicetitle     = datasets[i][18]
                del i

                maptitle = f"{region} {season} {distributionprojectcode}".replace('  ', ' ')

                msg = f" > Creating Map: {maptitle}"
                logFile(log_file, msg); del msg

                aprx.createMap(f"{maptitle}", "Map")
                aprx.save()
            aprx.save()

            del datasets, datasetcode, region, season, distributionprojectcode
            del datecode, featureclassname, featureservicetitle, maptitle
        del CreateMaps

        CreateLayerFiles = True
        if CreateLayerFiles:
            msg = f"> Createing Layer Files."
            logFile(log_file, msg); del msg

            datasets = generateDatasets()

            #with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            #    layer_list = ["DisMAP_Regions", "Indicators", "Datasets", "Species_Filter",]
            #    datasets = [[r for r in group] for group in datasets if group[0] in layer_list]
            #    del layer_list

            #if FilterDatasets:
            #    datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

            #if not datasets:
            #    print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            #aprx = arcpy.mp.ArcGISProject(ProjectGIS)

            # ###---> Create DisMAP Regions Layer File
            with arcpy.EnvManager(scratchWorkspace=ScratchGDB, workspace=ProjectGDB):

                maptitle = "DisMAP Regions"

                # ###--->>> DisMAP_Regions
                ds = [[r for r in group] for group in datasets if group[7] == "DisMAP_Regions"][0]

                regionslayername, regionslayertitle = ds[7], ds[18]
                del ds

                # ###--->>> "Indicators"
                ds = [[r for r in group] for group in datasets if group[3] == "Indicators"][0]

                indicatorslayername, indicatorslayertitle = ds[3], ds[18]
                del ds

                # ###--->>> "Datasets"

                ds = [[r for r in group] for group in datasets if group[3] == "Datasets"][0]

                datasetslayername, datasetslayertitle,  = ds[3], ds[18]
                del ds

                # ###--->>> "Species_Filter"
                ds = [[r for r in group] for group in datasets if group[3] == "Species_Filter"][0]

                species_filterlayername, species_filterlayertitle = ds[3], ds[18]
                del ds

                fields = [f.name for f in arcpy.ListFields(regionslayername) if f.type not in ['Geometry', 'OID']]
                field_info = ";".join([f"{f} {f} VISABLE NONE" for f in fields])
                del fields

                dismap_regions_layer = arcpy.management.MakeFeatureLayer(
                                                                         in_features  = f"{regionslayername}",
                                                                         out_layer    = f"{regionslayertitle}",
                                                                         where_clause = "",
                                                                         workspace    = ProjectGDB,
                                                                         field_info    = field_info
                                                                        )
                del field_info

                msg = f"   > Saving {regionslayertitle} Layer File."
                logFile(log_file, msg); del msg

                dismap_regions_layer_path = os.path.join(LAYER_DIRECTORY, f"{regionslayertitle}.lyrx")

                arcpy.management.SaveToLayerFile(
                                                 in_layer         = dismap_regions_layer,
                                                 out_layer        = dismap_regions_layer_path,
                                                 is_relative_path = None,
                                                 version          = "CURRENT"
                                                )
                arcpy.management.Delete(f"{regionslayertitle} Layer")
                arcpy.management.Delete(dismap_regions_layer)
                del dismap_regions_layer, dismap_regions_layer_path

                msg = f"      > Adding {regionslayertitle} layer to map"
                logFile(log_file, msg); del msg

                dismap_regions_layer_path = os.path.join(LAYER_DIRECTORY, f"{regionslayertitle}.lyrx")

                # Get information from a layer in a layer file
                lyrFile = arcpy.mp.LayerFile(dismap_regions_layer_path)
                #aprx = arcpy.mp.ArcGISProject(ProjectGIS)
                m = aprx.listMaps(f"{maptitle}")[0]
                rm_lyrs = [l for l in m.listLayers(f"{regionslayertitle}")]
                for rm_lyr in rm_lyrs: m.removeLayer(rm_lyr); del rm_lyr
                del rm_lyrs
                lyrs = m.listLayers()
                if len(lyrs) > 0:
                    reference_layer = lyrs[len(lyrs)-1]
                    m.insertLayer(reference_layer, lyrFile, "BEFORE")
                    del reference_layer
                else:
                    m.addLayer(lyrFile, 'TOP')
                lyrFile.save()
                aprx.save()
                del lyrFile

                msg = f"   > Adding {indicatorslayertitle} Table."
                logFile(log_file, msg); del msg

                indicatorsTable = arcpy.mp.Table(os.path.join(ProjectGDB, indicatorslayername))

                # Remove all tables
                tbs = [t for t in m.listTables("*")]
                for tb in tbs: m.removeTable(tb); del tb
                del tbs#, indicatorsTable
                aprx.save()

                tbs = [t for t in m.listTables(indicatorslayername)]
                for tb in tbs: m.removeTable(tb); del tb
                del tbs
                tbs = m.listTables()
                if f"{indicatorslayername}" not in tbs:
                    m.addTable(indicatorsTable)
                del tbs
                aprx.save()

                msg = f"   > Adding {datasetslayertitle} Table."
                logFile(log_file, msg); del msg

                datasetsTable = arcpy.mp.Table(os.path.join(ProjectGDB, datasetslayername))

                tbs = [t for t in m.listTables(datasetslayername)]
                for tb in tbs: m.removeTable(tb); del tb
                tbs = m.listTables()
                if f"{datasetslayername}" not in tbs:
                    m.addTable(datasetsTable)
                del tbs, datasetsTable
                aprx.save()

                msg = f"   > Adding {species_filterlayertitle} Table."
                logFile(log_file, msg); del msg

                species_filterTable = arcpy.mp.Table(os.path.join(ProjectGDB, species_filterlayername))

                tbs = [t for t in m.listTables(species_filterlayername)]
                for tb in tbs: m.removeTable(tb); del tb
                tbs = m.listTables()
                if f"{species_filterlayername}" not in tbs:
                    m.addTable(species_filterTable)
                del tbs, species_filterTable
                aprx.save()
                del m, lyrs

                del dismap_regions_layer_path, maptitle
                del indicatorslayername, indicatorslayertitle
                del datasetslayername, datasetslayertitle
                del species_filterlayername, species_filterlayertitle
                del regionslayername, regionslayertitle

            datasets = generateDatasets()

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                fcs = arcpy.ListFeatureClasses("*_Sample_Locations")
                datasets = [[r for r in group] for group in datasets if group[7] in fcs]
                del fcs

            if FilterDatasets:
                datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

            if not datasets:
                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            for i in range(len(datasets)):
                datasetcode             = datasets[i][0]
                featureclassname        = datasets[i][7]
                region                  = datasets[i][8]
                season                  = datasets[i][9]
                datecode                = datasets[i][10]
                distributionprojectcode = datasets[i][12]
                featureservicetitle     = datasets[i][18]
                mosaicname              = datasets[i][19]
                mosaictitle             = datasets[i][20]
                del i

                maptitle = f"{region} {season} {distributionprojectcode}".replace('  ', ' ')

                msg = f" > Creating Layer File: {maptitle}"
                logFile(log_file, msg); del msg

                #msg = f" > Processing Sample Location Layer Files for: {region} {season} {distributionprojectcode}"
                #logFile(log_file, msg); del msg

                msg = f"  > Processing: {featureservicetitle}"
                logFile(log_file, msg); del msg

                with arcpy.EnvManager(scratchWorkspace=ScratchGDB, workspace=ProjectGDB):
                    #msg = f"      > Checking of layer file for {featureservicetitle} exists"
                    #print(msg); del msg
                    #msg = f"      > Layer file for {featureservicetitle} does not exist"
                    #print(msg); del msg

                    msg = f"   > Creating {featureservicetitle} Layer File."
                    logFile(log_file, msg); del msg

                    fields = [f.name for f in arcpy.ListFields(featureclassname) if f.type not in ['Geometry', 'OID']]
                    field_info = ";".join([f"{f} {f} VISABLE NONE" for f in fields])
                    del fields

                    layertitle_layer = arcpy.management.MakeFeatureLayer(
                                                                          in_features=f"{featureclassname}",
                                                                          out_layer=f"{featureservicetitle}",
                                                                          where_clause="",
                                                                          workspace=ProjectGDB,
                                                                          field_info=field_info
                                                                         )
                    del field_info

                    msg = f"   > Saving {featureservicetitle} Layer File."
                    logFile(log_file, msg); del msg

                    featureservicetitle_path = os.path.join(LAYER_DIRECTORY, f"{featureservicetitle}.lyrx")

                    arcpy.management.SaveToLayerFile(
                                                     in_layer=layertitle_layer,
                                                     out_layer=featureservicetitle_path,
                                                     is_relative_path=None,
                                                     version="CURRENT"
                                                    )
                    arcpy.management.Delete(f"{featureservicetitle}")
                    arcpy.management.Delete(layertitle_layer)
                    del layertitle_layer

                    # Get time information from a layer in a layer file
                    lyrFile = arcpy.mp.LayerFile(featureservicetitle_path)
                    lyr = lyrFile.listLayers()[0]
                    lyr.enableTime("StdTime", "StdTime", True)
                    lyrFile.save()
                    del lyr

                    for lyr in lyrFile.listLayers():
                        if lyr.supports('TIME'):
                            if lyr.isTimeEnabled:
                                lyrTime = lyr.time
                                startTime = lyrTime.startTime
                                endTime = lyrTime.endTime
                                timeDelta = endTime - startTime
                                startTimeField = lyrTime.startTimeField
                                endTimeField = lyrTime.endTimeField
                                print(f"Layer: {lyr.name}")
                                print(f"  Start Time Field: {startTimeField}")
                                print(f"  End Time Field: {endTimeField}")
                                print(f"  Start Time: {str(startTime.strftime('%m-%d-%Y'))}")
                                print(f"  End Time:   {str(endTime.strftime('%m-%d-%Y'))}")
                                print(f"  Time Extent: {str(timeDelta.days)} days")
                                del  lyrTime, startTime, endTime, timeDelta
                                del startTimeField, endTimeField
                            else:
                                print("No time properties have been set on the layer")
                        else:
                            print("Time is not supported on this layer")
                        del lyr
                    del lyrFile, featureservicetitle_path

                    featureservicetitle_path = os.path.join(LAYER_DIRECTORY, f"{featureservicetitle}.lyrx")

                    msg = f"      > Adding {featureservicetitle} layer to map"
                    logFile(log_file, msg); del msg

                    # Get information from a layer in a layer file
                    lyrFile = arcpy.mp.LayerFile(featureservicetitle_path)
                    #aprx = arcpy.mp.ArcGISProject(ProjectGIS)
                    m = aprx.listMaps(f"{maptitle}")[0]
                    rm_lyrs = [l for l in m.listLayers(f"{featureservicetitle}")]
                    for rm_lyr in rm_lyrs: m.removeLayer(rm_lyr); del rm_lyr
                    del rm_lyrs
                    lyrs = m.listLayers()
                    if len(lyrs) > 0:
                        reference_layer = lyrs[len(lyrs)-1]
                        m.insertLayer(reference_layer, lyrFile, "BEFORE")
                        del reference_layer
                    else:
                        m.addLayer(lyrFile, 'TOP')
                    lyrFile.save()
                    aprx.save()
                    del lyrFile

                    del featureclassname, featureservicetitle, featureservicetitle_path

                #msg = f"   > Creating {mosaictitle} Layer."
                #logFile(log_file, msg); del msg

                with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                    if arcpy.Exists(mosaicname):

                        msg = f"  > Processing: {mosaictitle}"
                        logFile(log_file, msg); del msg

                        extent = arcpy.Describe(mosaicname).extent

                        variables = []
                        time_iterations = []
                        with arcpy.da.SearchCursor(mosaicname, ["StdTime", "Variable",]) as cursor:
                            for row in cursor:
                                #print(row)
                                time_iterations.append(row[0])
                                variables.append(row[1])
                                del row
                        del cursor

                        start_of_first_iteration = f'{str(min(time_iterations)).replace(" ", "T")}'

                        end_of_first_iteration   = f'{str(max(time_iterations)).replace(" ", "T")}'

                        del time_iterations

                        variables = "';'".join(sorted(list(set(variables))))
                        variables = f"'{variables}'"

                        mosaicname_layer = arcpy.md.MakeMultidimensionalRasterLayer(
                                                                                  in_multidimensional_raster=mosaicname,
                                                                                  out_multidimensional_raster_layer=f"{mosaictitle}",
                                                                                  variables=variables,
                                                                                  dimension_def="BY_ITERATION",
                                                                                  dimension_ranges=None,
                                                                                  dimension_values=None,
                                                                                  dimension="StdTime",
                                                                                  start_of_first_iteration=start_of_first_iteration,
                                                                                  end_of_first_iteration=end_of_first_iteration,
                                                                                  iteration_step=1,
                                                                                  iteration_unit="YEARS",
                                                                                  template=extent,
                                                                                  dimensionless="DIMENSIONS",
                                                                                  spatial_reference=None
                                                                                 )

                        del start_of_first_iteration, end_of_first_iteration
                        del variables, extent
                        msg = f"   > Saving {mosaictitle} Layer File."
                        logFile(log_file, msg); del msg

                        mosaictitle_path = os.path.join(LAYER_DIRECTORY, f"{mosaictitle}.lyrx")

                        arcpy.management.SaveToLayerFile(
                                                         in_layer=mosaicname_layer,
                                                         out_layer=mosaictitle_path ,
                                                         is_relative_path=None,
                                                         version="CURRENT"
                                                        )

                        arcpy.management.Delete(f"{mosaictitle}")
                        arcpy.management.Delete(mosaicname_layer)
                        del mosaicname_layer

                        mosaictitle_path = os.path.join(LAYER_DIRECTORY, f"{mosaictitle}.lyrx")

                        msg = f"      > Adding {mosaictitle} layer to map"
                        logFile(log_file, msg); del msg

                        # Get information from a layer in a layer file
                        lyrFile = arcpy.mp.LayerFile(mosaictitle_path)
                        m = aprx.listMaps(f"{maptitle}")[0]
                        rm_lyrs = [l for l in m.listLayers(f"{mosaictitle}")]
                        for rm_lyr in rm_lyrs: m.removeLayer(rm_lyr); del rm_lyr
                        del rm_lyrs
                        lyrs = m.listLayers()
                        if len(lyrs) > 0:
                            reference_layer = lyrs[len(lyrs)-1]
                            m.insertLayer(reference_layer, lyrFile, "BEFORE")
                            del reference_layer
                        else:
                            m.addLayer(lyrFile, 'TOP')
                        del m, lyrs
                        lyrFile.save()
                        aprx.save()
                        del lyrFile
                        del mosaictitle_path, mosaictitle

                    with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):

                        msg = f"   > Working on {datasetcode} {distributionprojectcode} Layer."
                        logFile(log_file, msg); del msg

                        crftitle_path = os.path.join(LAYER_DIRECTORY, f"{datasetcode} {distributionprojectcode} CRF.lyrx")
                        #msg = f"      > Checking layer file for {datasetcode} exists"
                        #print(msg); del msg

                        #msg = f"      > Layer file for {datasetcode} does not exist"
                        #print(msg); del msg

                        crf = f"{datasetcode}_{distributionprojectcode}.crf"

                        if arcpy.Exists(crf):

                            extent = arcpy.Describe().extent

                            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                                fields = [f.name for f in arcpy.ListFields(mosaicname) if f.name in ["StdTime", "Variable",] and f.type not in ['Geometry', 'OID']]
                                variables = []
                                time_iterations = []
                                with arcpy.da.SearchCursor(mosaicname, fields) as cursor:
                                    for row in cursor:
                                        #print(row)
                                        time_iterations.append(row[0])
                                        variables.append(row[1])
                                        del row
                                del cursor

                                start_of_first_iteration = f'{str(min(time_iterations)).replace(" ", "T")}'

                                end_of_first_iteration   = f'{str(max(time_iterations)).replace(" ", "T")}'

                                del time_iterations

                                variables = "';'".join(sorted(list(set(variables))))
                                variables = f"'{variables}'"

                                del fields

                            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):

                                mosaictitle_layer = arcpy.md.MakeMultidimensionalRasterLayer(
                                                                                              in_multidimensional_raster=f"{datasetcode}_{distributionprojectcode}.crf",
                                                                                              out_multidimensional_raster_layer=f"{datasetcode}_{distributionprojectcode} CRF",
                                                                                              #variables="'Anoplopoma fimbria';'Core Species Richness';'Gadus chalcogrammus';'Limanda aspera';'Microstomus pacificus';'Species Richness'",
                                                                                              variables=variables,
                                                                                              dimension_def="BY_ITERATION",
                                                                                              dimension_ranges=None,
                                                                                              dimension_values=None,
                                                                                              dimension="StdTime",
                                                                                              start_of_first_iteration=start_of_first_iteration,
                                                                                              end_of_first_iteration=end_of_first_iteration,
                                                                                              iteration_step=1,
                                                                                              iteration_unit="YEARS",
                                                                                              template=extent,
                                                                                              dimensionless="DIMENSIONS",
                                                                                              spatial_reference=None
                                                                                            )

                                del variables, start_of_first_iteration, end_of_first_iteration, extent

                            crftitle_path = os.path.join(LAYER_DIRECTORY, f"{datasetcode}_{distributionprojectcode} CRF.lyrx")

                            msg = f"   > Saving {datasetcode}_{distributionprojectcode} Layer File."
                            logFile(log_file, msg); del msg

                            arcpy.management.SaveToLayerFile(
                                                             in_layer=mosaictitle_layer,
                                                             out_layer=crftitle_path,
                                                             is_relative_path=None,
                                                             version="CURRENT"
                                                            )

                            arcpy.management.Delete(f"{datasetcode}_{distributionprojectcode} CRF")
                            arcpy.management.Delete(mosaictitle_layer)
                            del mosaictitle_layer

                            crftitle_path = os.path.join(LAYER_DIRECTORY, f"{datasetcode}_{distributionprojectcode} CRF.lyrx")

                            msg = f"      > Adding {datasetcode}_{distributionprojectcode} layer to map"
                            logFile(log_file, msg); del msg

                            # Get information from a layer in a layer file
                            lyrFile = arcpy.mp.LayerFile(crftitle_path)
                            #aprx = arcpy.mp.ArcGISProject(ProjectGIS)
                            m = aprx.listMaps(f"{maptitle}")[0]
                            rm_lyrs = [l for l in m.listLayers(f"{datasetcode}_{distributionprojectcode} CRF")]
                            for rm_lyr in rm_lyrs: m.removeLayer(rm_lyr); del rm_lyr
                            del rm_lyrs
                            lyrs = m.listLayers()
                            if len(lyrs) > 0:
                                reference_layer = lyrs[len(lyrs)-1]
                                m.insertLayer(reference_layer, lyrFile, "BEFORE")
                                del reference_layer
                            else:
                                m.addLayer(lyrFile, 'TOP')
                            del m, lyrs
                            lyrFile.save()
                            aprx.save()
                            del lyrFile
                            del crftitle_path

                del datasetcode, region, season, distributionprojectcode
                del mosaictitle, datecode
                del maptitle
            aprx.save()
            #del aprx
            del datasets
        del CreateLayerFiles

        CreateMapThumbnails = True
        if CreateMapThumbnails:
            msg = f"> Create Thumbnails for Maps"
            logFile(log_file, msg); del msg

            msg = f" > But first we need to check for browken datasource in each map"
            logFile(log_file, msg); del msg

            mps = aprx.listMaps()

            for mp in mps:
                msg = f" > Checking Map: {mp.name}"
                logFile(log_file, msg); del msg
                lyrs = mp.listLayers()
                last = lyrs.pop(); del last
                for lyr in lyrs:
                    if lyr.isBroken:
                        msg = f"\t###---> Layer: {lyr.name} is broken, but we'll fix it!!"
                        print(msg); del msg
                        conectionproperties = lyr.connectionProperties
                        database, dataset = os.path.split(lyr.dataSource)
                        conectionproperties['dataset'] = dataset
                        conectionproperties['connection_info'] = {'database' : f'{database}'}
                        if "CRF" in lyr.name:
                            conectionproperties['workspace_factory'] = 'Raster'
                        else:
                            conectionproperties['workspace_factory'] = 'File Geodatabase'
                        lyr.updateConnectionProperties(lyr.connectionProperties, conectionproperties)
                        lyrFiles = arcpy.mp.LayerFile(os.path.join(LAYER_DIRECTORY, f"{lyr.name}.lyrx"))
                        for lyrFile in lyrFiles.listLayers():
                            lyrFile.updateConnectionProperties(lyrFile.connectionProperties, conectionproperties)
                            del lyrFile
                        lyrFiles.save(); del lyrFiles
                        aprx.save()
                        del conectionproperties, database, dataset
                    del lyr
                del mp, lyrs
            del mps

            msg = f" > Now on to the thumbnails"
            logFile(log_file, msg); del msg

            mps = aprx.listMaps()

            for mp in mps:
                msg = f" > Working on Map: {mp.name}"
                logFile(log_file, msg); del msg
                lyrs = mp.listLayers()
                last = lyrs.pop(); del last
                # Turn off all layers first
                for lyr in lyrs: lyr.visible = False; del lyr
                # Now process each layer
                for lyr in lyrs:
                    msg = f"  > Working on Layer: {lyr.name}"
                    logFile(log_file, msg); del msg
                    lyr.visible = True
                    cmv = mp.defaultView
                    # This will ensure a unique output name
                    database, dataset = os.path.split(lyr.dataSource)
                    thumbnail = f"{dataset}.png"
                    thumbnail_path = os.path.join(LAYER_DIRECTORY, thumbnail)
                    del database, dataset
                    # Export the web map
                    cmv.exportToPNG(thumbnail_path, width=200, height=133, resolution = 96, color_mode="24-BIT_TRUE_COLOR", embed_color_profile=True)
                    lyr.visible = False
                    # Clean up
                    del lyr, cmv, thumbnail, thumbnail_path
                for lyr in lyrs: lyr.visible = True; del lyr
                del mp, lyrs
            del mps
            aprx.save()
        del CreateMapThumbnails

        UpdateMetadataWithThumbnails = False
        if UpdateMetadataWithThumbnails:
            arcpy.env.workspace = LAYER_DIRECTORY
            pngs = arcpy.ListFiles("*.png")
            if not pngs:
                print("No PNG files present. Need to run the thumbnail generator above!!")
            else:
                print("PNG files present.")

                from arcpy import metadata as md

                msg = f"> Update Metadata with Thumbnails."
                logFile(log_file, msg); del msg

                datasets = generateDatasets()

                with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                    fcs = arcpy.ListFeatureClasses("*")
                    datasets = [[r for r in group] for group in datasets if group[7] in fcs]
                    del fcs

                if FilterDatasets:
                    datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

                if not datasets:
                    print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

                msg = f"> Processing Feature Classes and Mosaics"
                logFile(log_file, msg); del msg

                for i in range(len(datasets)):
                    datasetcode             = datasets[i][0]
                    featureclassname        = datasets[i][7]
                    distributionprojectcode = datasets[i][12]
                    featureservicetitle     = datasets[i][18]
                    mosaicname              = datasets[i][19]
                    mosaictitle             = datasets[i][20]
                    del i

                    with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                        msg = f" > Processing: {featureservicetitle}"
                        logFile(log_file, msg); del msg

                        thumbnail = f"{featureclassname}.png"
                        thumbnail_path = os.path.join(LAYER_DIRECTORY, thumbnail)
                        if arcpy.Exists(thumbnail_path):
                            layername_md = md.Metadata(featureclassname)
                            layername_md.synchronize('SELECTIVE')
                            layername_md.thumbnailUri = thumbnail_path
                            layername_md.save()
                            del layername_md
                        else:
                            msg = f"\t\t###--> Thumbnail {thumbnail_path} is missing.<---###"
                            logFile(log_file, msg); del msg
                        del featureclassname, featureservicetitle, thumbnail, thumbnail_path

                        if mosaicname:
                            msg = f" > Processing: {mosaictitle}"
                            logFile(log_file, msg); del msg

                            thumbnail = f"{mosaicname}.png"
                            thumbnail_path = os.path.join(LAYER_DIRECTORY, thumbnail)
                            if arcpy.Exists(thumbnail_path):
                                layername_md = md.Metadata(mosaicname)
                                layername_md.synchronize('SELECTIVE')
                                layername_md.thumbnailUri = thumbnail_path
                                layername_md.save()
                                del layername_md
                            else:
                                msg = f"\t\t###--> Thumbnail {thumbnail_path} is missing.<---###"
                                logFile(log_file, msg); del msg
                            del thumbnail, thumbnail_path

                            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):
                                crf = f"{datasetcode}_{distributionprojectcode}.crf"
                                msg = f" > Processing: {crf}"
                                logFile(log_file, msg); del msg

                                thumbnail = f"{crf}.png"
                                thumbnail_path = os.path.join(LAYER_DIRECTORY, thumbnail)
                                if arcpy.Exists(thumbnail_path):
                                    layername_md = md.Metadata(crf)
                                    layername_md.synchronize('SELECTIVE')
                                    layername_md.thumbnailUri = thumbnail_path
                                    layername_md.save()
                                    del layername_md
                                else:
                                    msg = f"\t\t###--> Thumbnail {thumbnail_path} is missing.<---###"
                                    logFile(log_file, msg); del msg
                                del crf, thumbnail, thumbnail_path
                        del datasetcode, distributionprojectcode, mosaicname, mosaictitle
                del md, datasets
            del pngs
        del UpdateMetadataWithThumbnails

        aprx.save()
        del aprx

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
    except:
        import sys
        msg = sys.exc_info()[0]
        print(f"Unexpected error: {msg}" )
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def createSpeciesFilterTable():
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

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        speciesfilter = "Species_Filter"
        speciesfiltertable_csv_table = os.path.join(CSV_DIRECTORY, f"{speciesfilter}.csv")
        speciesfilter_table = os.path.join(ProjectGDB, speciesfilter)

        # Execute CreateTable
        arcpy.management.CreateTable(ProjectGDB, speciesfilter, "", "", "")

        tb_fields = [f.name for f in arcpy.ListFields(speciesfilter_table) if f.type not in ['Geometry', 'OID']]
        tb_definition_fields = table_definitions[speciesfilter]
        fields = [f for f in tb_definition_fields if f not in tb_fields]

        addFields(speciesfilter_table, fields, field_definitions)
        del tb_fields, tb_definition_fields, fields

        msg = f'> Generating {speciesfilter} CSV Table: {os.path.basename(speciesfiltertable_csv_table)}'
        #msg = f'> Generating {speciesfilter} CSV Table: {os.path.basename(speciesfiltertable_txt_table)}'
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
            #df = pd.read_csv(speciesfiltertable_txt_table,
                             #index_col = 0,
                             index_col = False,
                             encoding="utf-8",
                             #encoding="ISO-8859-1",
                             #encoding = "ISO-8859-1",
                             #engine='python',
                             delimiter = ',',
                             #delimiter = ';',
                             #delimiter = '\t',
                             #lineterminator='\n',
                             #dtype = None,
                             dtype = {
                                      "Species"         : str,
                                      "CommonName"      : str,
                                      "TaxonomicGroup"  : str,
                                      "FilterRegion"    : str,
                                      "FilterSubRegion" : str,
                                      "ManagementBody"  : str,
                                      "ManagementPlan"  : str,
                                      },
                             )
        #del speciesfiltertable_txt_table
        del speciesfiltertable_csv_table

        msg = f'>-> Defining the column names.'
        logFile(log_file, msg); del msg

        # The original column names from the CSV files are not very
        # reader friendly, so we are making some changes here
        #df.columns = [u'Region', u'HUALID', u'Year', u'Species', u'WTCPUE', u'CommonName', u'Stratum', u'StratumArea', u'Latitude', u'Longitude', u'Depth']
        df.columns = ["Species", "CommonName", "TaxonomicGroup", "FilterRegion", "FilterSubRegion", "ManagementBody", "ManagementPlan"]

        # Replace NaN with an empty string. When pandas reads a cell
        # with missing data, it asigns that cell with a Null or nan
        # value. So, we are changing that value to an empty string of ''.

        df.fillna("", inplace=True)

        msg = f'>-> Creating the {speciesfilter} Geodatabase Table'
        logFile(log_file, msg); del msg

        # ###--->>> Numpy Datatypes
        # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm

        # Get max length of all columns in the dataframe
        # max_length_all_cols = {col: df.loc[:, col].astype(str).apply(len).max() for col in df.columns}
        # type_dict = {'TEXT' : "S", 'SHORT' : "u4", 'DOUBLE' : 'd', 'DATE' : 'M8[us]' }

        # print([f'S{max_length_all_cols[v]}' for v in max_length_all_cols])
        # print([f'{v} : {max_length_all_cols[v]},' for v in max_length_all_cols])
        # print([f'S{field_definitions[v][3]}' for v in max_length_all_cols])
        # print([f'{v} S{field_definitions[v][3]}' for v in max_length_all_cols])
        # print([f'{field_definitions[v][1]} {field_definitions[v][3]}' for v in max_length_all_cols])

        # small = 10
        # big   = 20
        # multiplier = lambda x: big if x > small else small
        # nearest = lambda x: multiplier(x) * math.ceil(x / multiplier(x))

        # for key in max_length_all_cols:
        #     print(f"\t# # {key:23} = {max_length_all_cols[key]:3} ({nearest(max_length_all_cols[key]):2})")
        #     max_length_all_cols[key] = nearest(max_length_all_cols[key])

        # print([f'{v} : {max_length_all_cols[v]},' for v in max_length_all_cols])
        # print([f'S{max_length_all_cols[v]}' for v in max_length_all_cols])
        # del max_length_all_cols

        #pd.set_option("display.max_rows", 30)
        #pd.set_option("display.max_columns", 7)
        # print(pd.get_option("display.max_rows"))
        # print(pd.get_option("display.max_columns"))
        #pd.set_option('expand_frame_repr', False)
        #pd.set_option('precision', 7)
        #pd.set_option('colheader_justify', 'left')

        #print('DataFrame\n----------\n', df.head(30))
        #print('\nDataFrame datatypes :\n', df.dtypes)
        column_names = list(df.columns)
        #print(column_names)
        #columns = [str(c) for c in df.dtypes.index.tolist()]

        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        #                ['Species : 60,', 'CommonName : 40,', 'TaxonomicGroup : 80,', 'FilterRegion : 20,', 'FilterSubRegion : 20,', 'ManagementBody : 20,', 'ManagementPlan : 80,']
        column_formats = ['S50',           'S40',              'S80',                  'S25',                'S25',                   'S20',                   'S90']
        #            ['S60', 'S40', 'S80', 'S20', 'S20', 'S20', 'S80']

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
            logFile(log_file, msg); del msg

        del df, dtypes

        # Temporary table
        tmp_table = f'memory\{speciesfilter}_tmp'

        try:
            arcpy.da.NumPyArrayToTable(array, tmp_table)
            del array
        except arcpy.ExecuteError:
            import sys
            # Geoprocessor threw an error
            #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
            msg = arcpy.GetMessages(2).replace('\n', '\n\t')
            msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
            logFile(log_file, msg); del msg

        msg = f'>-> Copying the {speciesfilter} Table from memory to the GDB'
        logFile(log_file, msg); del msg

        arcpy.management.CopyRows(tmp_table, speciesfilter_table, "")

        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        msg = f'>-> Updating the field aliases for the {os.path.basename(speciesfilter_table)} Table'
        logFile(log_file, msg); del msg

        alterFields(speciesfilter_table)

        #msg = f'>-> Adding metadata to the {os.path.basename(speciesfilter_table)} Table'
        #logFile(log_file, msg); del msg

        # Add Metadata
        #addMetadata(speciesfilter_table)

        # Cleanup
        del speciesfilter_table, speciesfilter

        del pd, np, warnings

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        print(msg); del msg #logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg #logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function#, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

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

        del walk, dirpath, dirnames, filenames, filename, datatype, type

        dataset_dictionary = {}
        FieldListReport = True
        #print(dataSets.sort())
        for dataSet in sorted(dataSets):
            # Describe dataset
            desc = arcpy.Describe(dataSet)
            # Print selected dataset and describe object properties
            msg = f"Data Set: {desc.name} Data Type: {desc.dataType}"
            logFile(log_file, msg); del msg
            del desc

            # Get list of fields in the table
            # fields_list = lambda feature_class: [field.name for field in arcpy.ListFields(feature_class) if field.type not in ['Geometry', 'OID']
            #fields = arcpy.ListFields(dataSet)

            if FieldListReport:
                fieldlist = []
                fields = [f for f in arcpy.ListFields(dataSet) if f.type not in ['Geometry', 'OID']]
                # Loop through fields
                for field in fields:
                    fieldlist.append([field.name, field.type.upper(), field.aliasName, field.length, '', '',])
                    del field
                dataset_dictionary[dataSet] = fieldlist

            DetailedFieldReport = False
            if DetailedFieldReport:
                fields = [f for f in arcpy.ListFields(dataSet) if f.type not in ['Geometry', 'OID']]
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
                    # msg = msg + '\t\t\t\t<attrlabl Sync="TRUE">{fieldName}</attrlabl>\n'
                    # msg = msg + '\t\t\t\t<attalias Sync="TRUE">{fieldAliasName}</attalias>\n'
                    # msg = msg + '\t\t\t\t<attrtype Sync="TRUE">{fieldType}</attrtype>\n'
                    # msg = msg + '\t\t\t\t<attwidth Sync="TRUE">{fieldLength}</attwidth>\n'
                    # msg = msg + '\t\t\t\t<atprecis Sync="TRUE">{fieldPrecision}</atprecis>\n'
                    # msg = msg + '\t\t\t\t<attscale Sync="TRUE">0</attscale>\n')
                    # msg = msg + '\t\t\t\t<attrdef>{fieldAliasName}</attrdef>\n'
                    # msg = msg + '\t\t\t\t<attrdefs>{state}</attrdefs>\n'
                    # logFile(log_file, msg); del msg

                    del field, fieldName, fieldAliasName, fieldType
                    del fieldLength, fieldEditable, fieldRequired, fieldScale
                    del fieldPrecision, state
            del DetailedFieldReport

            del dataSet, fields

        if FieldListReport:
            for key in dataset_dictionary:
                print(f'{{"{key}" : [')
                for i in range(len(dataset_dictionary[key])):
                    print(f"\t{dataset_dictionary[key][i]}")
                #print(key, dataset_dictionary[key])

        del dataset_dictionary
        del FieldListReport

        del workspace, wildcard, fieldNames, arcGISfields, dataSets

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

def exportArcGisMetadata():
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

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

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        arcpy.env.overwriteOutput = True

        from arcpy import metadata as md

##        aprx = arcpy.mp.ArcGISProject(ProjectGIS)

        msg = f"> Exporting Metadata"
        logFile(log_file, msg); del msg

        datasets = []
        #with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            #tb_list = [os.path.join(ProjectGDB, tb) for tb in arcpy.ListTables("*") if tb in ['Indicators', 'Datasets', 'Species_Filter']]
            #fc_list = [os.path.join(ProjectGDB, fc) for fc in arcpy.ListFeatureClasses("*Sample_Locations")] #
            #fc_list = [os.path.join(ProjectGDB, fc) for fc in arcpy.ListFeatureClasses("*") if "Sample_Locations" in fc or "DisMAP_Regions" in fc] #
            #ms_list = [os.path.join(ProjectGDB, ms) for ms in arcpy.ListDatasets(feature_type='Mosaic')] # if ms in ['AI_IDW_Mosaic']]
            #rs_list = [rs for rs in arcpy.ListDatasets(feature_type='Raster') if rs in ['AI_IDW_Mask']]
        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):
            #crf_list = [os.path.join(MOSAIC_DIRECTORY, crf) for crf in arcpy.ListFiles(f"*.crf") if crf in ['AI_IDW.crf','WC_GLMME.crf']]
            crf_list = [os.path.join(MOSAIC_DIRECTORY, crf) for crf in arcpy.ListFiles(f"*.crf")]

        #datasets.extend(tb_list); del tb_list
        #datasets.extend(fc_list); del fc_list
        #datasets.extend(ms_list); del ms_list
        #datasets.extend(rs_list); del rs_list
        datasets.extend(crf_list); del crf_list

##        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
##            tb_list = [os.path.join(ProjectGDB, tb) for tb in arcpy.ListTables("*")]
##            fc_list = [os.path.join(ProjectGDB, fc) for fc in arcpy.ListFeatureClasses("*")]
##            ms_list = [os.path.join(ProjectGDB, ms) for ms in arcpy.ListDatasets(feature_type='Mosaic')]
##            rs_list = [os.path.join(ProjectGDB, rs) for rs in arcpy.ListDatasets(feature_type='Raster')]
##        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):
##            crf_list = [os.path.join(MOSAIC_DIRECTORY, crf) for crf in arcpy.ListFiles(f"*.crf")]
##
##        datasets.extend(tb_list)
##        datasets.extend(fc_list)
##        datasets.extend(ms_list)
##        datasets.extend(rs_list)
##        datasets.extend(crf_list)
##
##        del tb_list, fc_list, ms_list, rs_list, crf_list

        #print(EXPORT_METADATA_DIRECTORY)
        #Loop through all datasets in the database that are specified in the workspace
        for dataset in sorted(datasets):
            print(f"Dataset: {os.path.basename(dataset)}")
            #print(f"\tPath: {dataset}")

            if '.crf' in dataset:
                out_metadata = f"{os.path.basename(dataset).replace('.crf','_CRF')}.xml"
            else:
                out_metadata = f"{os.path.basename(dataset)}.xml"

            #empty_xml_file = os.path.join(ARCGIS_METADATA_DIRECTORY, f"empty.xml")
            #prettyXML(empty_xml_file)
            #entity_xml = os.path.join(ARCGIS_METADATA_DIRECTORY, f"EntityMetadata.xml")
            dataset_xml_file = os.path.join(ARCGIS_METADATA_DIRECTORY, out_metadata)
            dataset_xml_file_template = os.path.join(ARCGIS_METADATA_DIRECTORY, out_metadata.replace('.xml', ' TEMPLATE.xml'))
            del out_metadata

            # Process: Export Metadata
            print(f"> Creating dataset Metadata Object for {os.path.basename(dataset)}")
            #print(dataset)
            dataset_md = md.Metadata(dataset)

            if "Sample_Locations" in os.path.basename(dataset):
                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset)}.xml")
            elif "DisMAP_Regions" in os.path.basename(dataset):
                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset)}.xml")
            elif "Indicators" in os.path.basename(dataset):
                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset)}.xml")
            elif "GRID_Points" in os.path.basename(dataset):
                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset)}.xml")
            elif "Mosaic" in os.path.basename(dataset):
                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset)}.xml")
            elif ".crf" in os.path.basename(dataset):
                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset.replace('.crf','_Mosaic'))}.xml")
            else:
                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"EntityMetadata.xml")
            #if ".crf" in dataset:
            #    dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset.replace('.crf','_Mosaic'))}.xml")

            if arcpy.Exists(dataset_template):
                prettyXML(dataset_template)

            ImportDatasetMetadata = False
            print(f" > Importing: {dataset_template}")
            if ImportDatasetMetadata:
                # #dataset_md.synchronize("ALWAYS")
                dataset_md.synchronize("SELECTIVE")
                dataset_md.importMetadata(dataset_template, "DEFAULT")
                dataset_md.save()
                dataset_md.reload()
                dataset_md.synchronize("ACCESSED")
                dataset_md.save()
                dataset_md.reload()
            del dataset_template, ImportDatasetMetadata

            #dataset_md.synchronize("ACCESSED", 0)
            #dataset_md.synchronize("ALWAYS")
            #dataset_md.synchronize("CREATED", 0)
            #dataset_md.synchronize("NOT_CREATED", 0)
            #dataset_md.synchronize("OVERWRITE")
            #dataset_md.synchronize("SELECTIVE")

            #dataset_md.synchronize("OVERWRITE")
            #dataset_md.importMetadata(empty_xml_file, "DEFAULT")
            #dataset_md.save()
            #dataset_md.reload()
            #del empty_xml_file

            if not dataset_md.isReadOnly:
                dataset_md.deleteContent('GPHISTORY')
                dataset_md.deleteContent('ENCLOSED_FILES')
                dataset_md.deleteContent('THUMBNAIL')
                dataset_md.save()
                dataset_md.reload()

            ExportDatasetMetadata = True
            if ExportDatasetMetadata:
                print(f" > Saving dataset metadata as an 'EXACT_COPY' file: {os.path.basename(dataset_xml_file)}")
                dataset_md.saveAsXML(dataset_xml_file, 'EXACT_COPY')

                #print(f" > Saving dataset metadata as 'REMOVE_ALL_SENSITIVE_INFO' file: {os.path.basename(dataset_xml_file_template)}")
                #dataset_md.saveAsXML(dataset_xml_file_template, 'REMOVE_ALL_SENSITIVE_INFO')

                print(f" > Saving dataset as an 'TEMPLATE' file: {os.path.basename(dataset_xml_file_template)}")
                #dataset_md.saveAsXML(dataset_xml_file_template, 'TEMPLATE')
                #dataset_md.exportMetadata(dataset_xml_file_template.replace('TEMPLATE', 'FGDC_CSDGM'), 'FGDC_CSDGM', 'REMOVE_ALL_SENSITIVE_INFO')

                prettyXML(dataset_xml_file)
                #prettyXML(dataset_xml_file_template)
                #prettyXML(dataset_xml_file_template.replace('TEMPLATE', 'FGDC_CSDGM'))
            del ExportDatasetMetadata

            del dataset_md, dataset, dataset_xml_file, dataset_xml_file_template
        del md, datasets

        PrettyAllXML = False
        if PrettyAllXML:
            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ARCGIS_METADATA_DIRECTORY):
                xml_list = [os.path.join(ARCGIS_METADATA_DIRECTORY, xml) for xml in arcpy.ListFiles(f"*.xml")]
                for xml in xml_list:
                    prettyXML(xml)
                    del xml
                del xml_list
        del PrettyAllXML


##            xml_file = os.path.join(EXPORT_METADATA_DIRECTORY, f"{os.path.basename(dataset).replace('.crf','')}_xml.xml")
##            xml_file_template = os.path.join(EXPORT_METADATA_DIRECTORY, f"{os.path.basename(dataset).replace('.crf','')}_TEMPLATE.xml")
##            empty_xml_file = os.path.join(EXPORT_METADATA_DIRECTORY, f"empty.xml")
##
##            xml_file_exact_copy = xml_file.replace('_xml.xml', '_xml EXACT_COPY.xml')
##            xml_file_exact_copy_fgdc = xml_file_exact_copy.replace('_xml EXACT_COPY.xml', '_xml EXACT_COPY FGDC.xml')
##            xml_file_exact_copy_updated = xml_file_exact_copy.replace('_xml EXACT_COPY.xml', '_xml EXACT_COPY Updated.xml')
##            xml_file_template_updated = xml_file_template.replace('_TEMPLATE.xml', '_TEMPLATE Updated.xml')
##
##            #dataset = os.path.join(ProjectGDB, dataset)
##            # Process: Export Metadata
##            print(f"> Creating dataset Metadata Object")
##            dataset_md = md.Metadata(dataset)
##            # Synchronize the item's metadata now
##            dataset_md.synchronize('ALWAYS')
##            #dataset_md.synchronize("OVERWRITE")
##            dataset_md.save()
##            dataset_md.reload()
##            print(f"> Saving dataset as an 'EXACT_COPY' file: {os.path.basename(xml_file)}")
##            dataset_md.saveAsXML(xml_file, 'EXACT_COPY')
##            dataset_md.saveAsXML(xml_file_exact_copy, 'EXACT_COPY')
##            print(f"> Exporting dataset as an 'FGDC_CSDGM' file: {os.path.basename(xml_file)}")
##            dataset_md.exportMetadata(xml_file.replace('.xml',' FGDC.xml'), 'FGDC_CSDGM', 'REMOVE_ALL_SENSITIVE_INFO')
##            dataset_md.synchronize('OVERWRITE')
##            dataset_md.importMetadata(xml_file.replace('.xml',' FGDC.xml'), 'FGDC_CSDGM')
##            dataset_md.save()
##            dataset_md.reload()
##            print(f"> Saving dataset as an 'EXACT_COPY' file: {os.path.basename(xml_file)}")
##            dataset_md.saveAsXML(xml_file, 'EXACT_COPY')
##            print(f"> Saving dataset as a 'TEMPLATE' file: {os.path.basename(xml_file_template)}")
##            dataset_md.saveAsXML(xml_file_template, 'TEMPLATE')
##            #dataset_md.synchronize("ALWAYS")
##            #dataset_md.importMetadata(empty_xml_file, "DEFAULT")
##            #dataset_md.synchronize("OVERWRITE")
##
##            del dataset_md
##
##            #prettyXML(xml_file)
##            #prettyXML(xml_file_template)
##
##            dataset_md = md.Metadata(xml_file_exact_copy)
##            if not dataset_md.isReadOnly:
##                dataset_md.deleteContent('GPHISTORY')
##                dataset_md.deleteContent('ENCLOSED_FILES')
##                dataset_md.deleteContent('THUMBNAIL')
##                dataset_md.save()
##                dataset_md.reload()
##
##            #dataset_md.synchronize("ACCESSED", 0)
##            #dataset_md.synchronize("ALWAYS")
##            #dataset_md.synchronize("CREATED", 0)
##            #dataset_md.synchronize("NOT_CREATED", 0)
##            #dataset_md.synchronize("OVERWRITE")
##            dataset_md.synchronize("SELECTIVE")
##            dataset_md.save()
##            dataset_md.reload()
##
##            if "Indicators" in os.path.basename(dataset):
##                dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Indicators Template.xml"))
##            elif "DisMAP_Regions" in os.path.basename(dataset):
##                dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "DisMAP Regions Template.xml"))
##            elif "_Sample_Locations" in os.path.basename(dataset):
##                dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Sample Locations Template.xml"))
##            elif "_Mosaic" in os.path.basename(dataset):
##                dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Biomass Rasters Template.xml"))
##            elif ".crf" in os.path.basename(dataset):
##                dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Biomass Rasters Template.xml"))
##
##
##            if "Indicators" in os.path.basename(dataset):
##                if not dataset_md.isReadOnly:
##                    dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Indicators Template.xml"))
##            elif "DisMAP_Regions" in os.path.basename(dataset):
##                if not dataset_md.isReadOnly:
##                    dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "DisMAP Regions Template.xml"))
##            elif "_Sample_Locations" in os.path.basename(dataset):
##                if not dataset_md.isReadOnly:
##                    dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Sample Locations Template.xml"))
##            elif "_Mosaic" in os.path.basename(dataset):
##                if not dataset_md.isReadOnly:
##                    dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Biomass Rasters Template.xml"))
##            elif ".crf" in os.path.basename(dataset):
##                if not dataset_md.isReadOnly:
##                    dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Biomass Rasters Template.xml"))
##
##            dataset_md.save()
##            dataset_md.reload()
##
##            print(f"> Exporting dataset as an 'FGDC_CSDGM' file: {os.path.basename(xml_file)}")
##            dataset_md.exportMetadata(xml_file_exact_copy_fgdc, 'FGDC_CSDGM', 'REMOVE_ALL_SENSITIVE_INFO')
##            dataset_md.synchronize('OVERWRITE')
##            dataset_md.importMetadata(xml_file_exact_copy_fgdc, 'FGDC_CSDGM')
##            dataset_md.save()
##            dataset_md.reload()
##            print(f"> Saving dataset as an 'EXACT_COPY' file: {os.path.basename(xml_file)}")
##            dataset_md.saveAsXML(xml_file_exact_copy_updated, 'EXACT_COPY')
##            print(f"> Saving dataset as a 'TEMPLATE' file: {os.path.basename(xml_file_template)}")
##            dataset_md.saveAsXML(xml_file_template_updated, 'TEMPLATE')
##
##            #print(f"> Saving dataset as an 'EXACT_COPY' file: {os.path.basename(xml_file)}")
##            #dataset_md.saveAsXML(xml_file.replace('.xml', ' Update.xml'), 'EXACT_COPY')
##            #print(f"> Saving dataset as a 'TEMPLATE' file: {os.path.basename(xml_file_template)}")
##            #dataset_md.saveAsXML(xml_file_template.replace('.xml', ' Update.xml'), 'TEMPLATE')
##
##            del dataset_md
##
##            #dataset_md.save()
##            #dataset_md.reload()
##            #dataset_md.deleteContent('GPHISTORY')
##            #dataset_md.deleteContent('ENCLOSED_FILES')
##            #dataset_md.deleteContent('THUMBNAIL')
##            #dataset_md.synchronize("OVERWRITE")
##            #dataset_md.save()
##            #dataset_md.reload()
##            #dataset_md.saveAsXML(xml_file, 'REMOVE_ALL_SENSITIVE_INFO')
##            #dataset_md.saveAsXML(xml_file_template, 'TEMPLATE')
##
##            prettyXML(xml_file)
##            prettyXML(xml_file_template)
##            prettyXML(xml_file_exact_copy)
##            prettyXML(xml_file_exact_copy_fgdc)
##            prettyXML(xml_file_template_updated)
##            prettyXML(xml_file_exact_copy_updated)
##
##            del xml_file_template, empty_xml_file
##            del xml_file_exact_copy, xml_file_exact_copy_fgdc, xml_file_exact_copy_updated, xml_file_template_updated
##
##            del dataset, xml_file
##        del md, datasets, tb_list, fc_list, ms_list, crf_list
##
##        datasets = generateDatasets()
##
##        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
##            fcs = arcpy.ListFeatureClasses("*")
##            datasets = [[r for r in group] for group in datasets if group[7] in fcs]
##            del fcs
##
##        if FilterDatasets:
##            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]
##
##        if not datasets:
##            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")
##
##        msg = f"> Processing Tables, Feature Classes, and Mosaics"
##        logFile(log_file, msg); del msg
##
##        for i in range(len(datasets)):
##            datasetcode             = datasets[i][0]
##            tablename               = datasets[i][3]
##            pointfeaturetype        = datasets[i][6]
##            featureclassname        = datasets[i][7]
##            region                  = datasets[i][8]
##            season                  = datasets[i][9]
##            datecode                = datasets[i][10]
##            distributionprojectcode = datasets[i][12]
##            featureservicename      = datasets[i][11]
##            featureservicetitle     = datasets[i][18]
##            mosaicname              = datasets[i][19]
##            mosaictitle             = datasets[i][20]
##            imageservicename        = datasets[i][21]
##            imageservicetitle       = datasets[i][22]
##            del i
##
##            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"
##
##            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
##                #msg = f" > Processing: {dataset_product_code}"
##                #logFile(log_file, msg); del msg
##
##                if tablename:
##                    msg = f" > Processing Table: {tablename}"
##                    logFile(log_file, msg); del msg
##
##                    tablename_md = md.Metadata(tablename)
##
##                    template_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{tablename} Template.xml")
##                    if arcpy.Exists(template_metadata):
##                        tablename_md.importMetadata(template_metadata, 'DEFAULT')
##                        #tablename_md.synchronize("SELECTIVE")
##                        #tablename_md.synchronize("ACCESSED", 0)
##                        #tablename_md.synchronize("NOT_CREATED", 0)
##                        #tablename_md.synchronize("CREATED", 0)
##                        #tablename_md.synchronize("ALWAYS")
##                        #tablename_md.synchronize("OVERWRITE")
##                    del template_metadata
##
##                    #tablename_md.synchronize('ACCESSED')
##                    tablename_md.title = tablename
##                    tablename_md.save()
##                    tablename_md.reload()
##
##                    # Delete all geoprocessing history and any enclosed files from the item's metadata
##                    if not tablename_md.isReadOnly:
##                        tablename_md.deleteContent('GPHISTORY')
##                        #tablename_md.deleteContent('ENCLOSED_FILES')
##                        #tablename_md.deleteContent('THUMBNAIL')
##                        #tablename_md.save()
##                        tablename_md.reload()
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{tablename}.xml")
##                    #tablename_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
##                    tablename_md.saveAsXML(export_metadata, 'EXACT_COPY')
##                    prettyXML(export_metadata); del export_metadata
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{tablename} Template.xml")
##                    tablename_md.saveAsXML(export_metadata, 'TEMPLATE')
##                    prettyXML(export_metadata); del export_metadata
##
##                    del tablename_md
##
##                if featureclassname:
##                    msg = f" > Processing Feature Class: {featureclassname}"
##                    logFile(log_file, msg); del msg
##
##                    featureclassname_md = md.Metadata(featureclassname)
##
##                    template_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureclassname} Template.xml")
##                    if arcpy.Exists(template_metadata):
##                        featureclassname_md.importMetadata(template_metadata, 'DEFAULT')
##                        #featureclassname_md.synchronize("SELECTIVE")
##                        #featureclassname_md.synchronize("ACCESSED", 0)
##                        #featureclassname_md.synchronize("NOT_CREATED", 0)
##                        #featureclassname_md.synchronize("CREATED", 0)
##                        #featureclassname_md.synchronize("ALWAYS")
##                        #featureclassname_md.synchronize("OVERWRITE")
##                    del template_metadata
##
##                    #featureclassname_md.synchronize('ACCESSED')
##                    featureclassname_md.title = featureservicetitle
##                    featureclassname_md.save()
##                    featureclassname_md.reload()
##
##                    # Delete all geoprocessing history and any enclosed files from the item's metadata
##                    if not featureclassname_md.isReadOnly:
##                        featureclassname_md.deleteContent('GPHISTORY')
##                        #featureclassname_md.deleteContent('ENCLOSED_FILES')
##                        #featureclassname_md.deleteContent('THUMBNAIL')
##                        featureclassname_md.save()
##                        featureclassname_md.reload()
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureclassname}.xml")
##                    #featureclassname_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
##                    featureclassname_md.saveAsXML(export_metadata, 'EXACT_COPY')
##                    prettyXML(export_metadata); del export_metadata
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureclassname} Template.xml")
##                    featureclassname_md.saveAsXML(export_metadata, 'TEMPLATE')
##                    prettyXML(export_metadata); del export_metadata
##
##                    del featureclassname_md
##
##                if mosaicname:
##                    msg = f" > Processing Mosaic: {mosaicname}"
##                    logFile(log_file, msg); del msg
##
##                    mosaicname_md = md.Metadata(mosaicname)
##
##                    template_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname} Template.xml")
##                    if arcpy.Exists(template_metadata):
##                        mosaicname_md.importMetadata(template_metadata, 'DEFAULT')
##                        #mosaicname_md.synchronize("SELECTIVE")
##                        #mosaicname_md.synchronize("ACCESSED", 0)
##                        #mosaicname_md.synchronize("NOT_CREATED", 0)
##                        #mosaicname_md.synchronize("CREATED", 0)
##                        #mosaicname_md.synchronize("ALWAYS")
##                        #mosaicname_md.synchronize("OVERWRITE")
##                    del template_metadata
##
##                    #mosaicname_md.synchronize('ACCESSED')
##                    mosaicname_md.title = mosaictitle
##                    mosaicname_md.save()
##                    mosaicname_md.reload()
##
##                    # Delete all geoprocessing history and any enclosed files from the item's metadata
##                    if not mosaicname_md.isReadOnly:
##                        mosaicname_md.deleteContent('GPHISTORY')
##                        #mosaicname_md.deleteContent('ENCLOSED_FILES')
##                        #mosaicname_md.deleteContent('THUMBNAIL')
##                        mosaicname_md.save()
##                        mosaicname_md.reload()
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname}.xml")
##                    #mosaicname_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
##                    mosaicname_md.saveAsXML(export_metadata, 'EXACT_COPY')
##                    prettyXML(export_metadata); del export_metadata
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname} Template.xml")
##                    mosaicname_md.saveAsXML(export_metadata, 'TEMPLATE')
##                    prettyXML(export_metadata); del export_metadata
##
##                    del mosaicname_md
##
##                    msg = f" > Processing CRF: {dataset_product_code}"
##                    logFile(log_file, msg); del msg
##
##                    with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):
##                        crf = f"{dataset_product_code}.crf"
##                        #msg = f" > Processing: {crf}"
##                        #logFile(log_file, msg); del msg
##
##                        crf_md = md.Metadata(crf)
##
##                        template_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname} CRF Template.xml")
##                        if arcpy.Exists(template_metadata):
##                            crf_md.importMetadata(template_metadata, 'DEFAULT')
##                            #crf_md.synchronize("SELECTIVE")
##                            #crf_md.synchronize("ACCESSED", 0)
##                            #crf_md.synchronize("NOT_CREATED", 0)
##                            #crf_md.synchronize("CREATED", 0)
##                            #crf_md.synchronize("ALWAYS")
##                            #crf_md.synchronize("OVERWRITE")
##                        del template_metadata
##
##                        #crf_md.synchronize('ACCESSED')
##                        crf_md.title = mosaictitle
##                        crf_md.save()
##                        crf_md.reload()
##
##                        # Delete all geoprocessing history and any enclosed files from the item's metadata
##                        if not crf_md.isReadOnly:
##                            crf_md.deleteContent('GPHISTORY')
##                            #crf_md.deleteContent('ENCLOSED_FILES')
##                            #crf_md.deleteContent('THUMBNAIL')
##                            crf_md.save()
##                            crf_md.reload()
##
##                        export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname} CRF.xml")
##                        crf_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
##                        prettyXML(export_metadata); del export_metadata
##
##                        export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname} CRF Template.xml")
##                        crf_md.saveAsXML(export_metadata, 'TEMPLATE')
##                        prettyXML(export_metadata); del export_metadata
##
##                        del crf_md, crf,
##
##            del datasetcode, tablename, pointfeaturetype, featureclassname
##            del region, season, datecode, distributionprojectcode
##            del featureservicename, featureservicetitle, mosaicname, mosaictitle
##            del imageservicename, imageservicetitle, dataset_product_code
##
##        del md
##        del datasets
##
##        aprx.save()
##        del aprx

        compactGDB(ProjectGDB)

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
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
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def generateDatasets():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        dataset_table = os.path.join(ProjectGDB, "Datasets")

        CreateDatasetTable = False
        if not arcpy.Exists(dataset_table) or CreateDatasetTable:
            createDatasetTable()
        del CreateDatasetTable

        fields = [f.name for f in arcpy.ListFields(dataset_table) if f.type not in ['Geometry', 'OID']]

        PrettyPrintFields = False
        if PrettyPrintFields:
            # Pretty prints column names and row reference for the search cursor
            for field in fields:
                print(f"\t\t\t\t{field.lower().ljust(23, ' ')} = row[{fields.index(field)}]"); del field
            for field in fields:
                print(f"# # {field.lower().ljust(23, ' ')} = dataset[{fields.index(field)}]"); del field
            for field in fields:
                print(f"# # {field.lower().ljust(23, ' ')} = datasets[i][{fields.index(field)}]"); del field
            print(", ".join(fields).lower())
        del PrettyPrintFields

        datasets = []
        with arcpy.da.SearchCursor(dataset_table, fields) as cursor:
            for row in cursor:
                datasetcode             = row[0]
                csvfile                 = row[1]
                transformunit           = row[2]
                tablename               = row[3]
                geographicarea          = row[4]
                cellsize                = row[5]
                pointfeaturetype        = row[6]
                featureclassname        = row[7]
                region                  = row[8]
                season                  = row[9]
                datecode                = row[10]
                status                  = row[11]
                distributionprojectcode = row[12]
                distributionprojectname = row[13]
                summaryproduct          = row[14]
                filterregion            = row[15]
                filtersubregion         = row[16]
                featureservicename      = row[17]
                featureservicetitle     = row[18]
                mosaicname              = row[19]
                mosaictitle             = row[20]
                imageservicename        = row[21]
                imageservicetitle       = row[22]

                datasets.append(
                                [
                                datasetcode, csvfile, transformunit,
                                tablename, geographicarea,
                                cellsize, pointfeaturetype, featureclassname,
                                region, season, datecode, status,
                                distributionprojectcode, distributionprojectname,
                                summaryproduct, filterregion, filtersubregion,
                                featureservicename, featureservicetitle,
                                mosaicname, mosaictitle, imageservicename,
                                imageservicetitle,
                                ]
                               )

                del row
                del datasetcode, csvfile, transformunit,
                del tablename, geographicarea
                del cellsize, pointfeaturetype, featureclassname,
                del region, season, datecode, status,
                del distributionprojectcode, distributionprojectname,
                del summaryproduct, filterregion, filtersubregion,
                del featureservicename, featureservicetitle,
                del mosaicname, mosaictitle, imageservicename,
                del imageservicetitle
        del cursor
        del dataset_table, fields
        return datasets



    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg #logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg #logFile(log_file, msg); del msg

    finally:
        del datasets

        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            print(msg); del msg
        del localKeys, function#, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def generateFieldDefinitions(workspace, wildcard, datatype, type):
    try:
        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        # Set the workspace to the workspace
        arcpy.env.workspace = workspace

        # Set the scratch workspace to the ScratchGDB
        #arcpy.env.scratchWorkspace = ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        dataSets = []

        walk = arcpy.da.Walk(workspace, topdown=True, datatype=datatype, type=type)

        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                if wildcard.lower() in filename.lower():
                    dataSets.append(filename)
                #dirpath, dirnames, filenames

        dataset_dictionary = {}

        FieldListReport = True

        for dataSet in sorted(dataSets):
            if FieldListReport:
                fieldlist = []
                fields = [f for f in arcpy.ListFields(dataSet) if f.type not in ['Geometry', 'OID', 'ID', 'FID'] or not f.required]
                # Loop through fields
                for field in fields:
                    #if 'FID' not in field.name:
                    if field.name not in ["CenterX", "CenterY", "Count", 'FID', "ID", "ItemTS", "LowPS", "MaxPS", "MinPS", "Shape_Area", "Shape_Length", "Uri", "UriHash", "ZOrder" ]:
                        fieldlist.append([field.name, field.type.upper(), field.aliasName, field.length, '', '',])
                    del field
                dataset_dictionary[dataSet] = fieldlist
                del fields

            del dataSet

        FieldDictionaryListReport = True
        field_definitions = {}
        if FieldDictionaryListReport:
            for key in dataset_dictionary:
                #print(f'{key}')
                for i in range(len(dataset_dictionary[key])):
                    field  = dataset_dictionary[key][i][0]
                    values = dataset_dictionary[key][i]
                    #print(field, values)
                    if field not in field_definitions.keys():
                        field_definitions[field] = values


        small = 5
        big   = 10
        multiplier = lambda x: big if x > small else small
        nearest = lambda x: multiplier(x) * math.ceil(x / multiplier(x))

        for key in sorted(field_definitions):
            field_name, field_type, field_alias, field_length, default_value, dmomain = field_definitions[key]
            if 'STRING' in field_type:
                field_type = 'TEXT'
            if 'INTEGER' in field_type:
                field_type = 'SHORT'
            if field_type in ['DATE', 'SHORT', 'DOUBLE']:
                field_length = None

            if field_type == 'TEXT':
                field_length = nearest(field_length)

            field_name, field_type, field_alias, field_length, default_value, dmomain = f'"{field_name}",', f'"{field_type}",', f'"{field_alias}",', f'{field_length},', f'"",', f'""'
            key = f'"{key}"'
            print(f'{key:<29} : [{field_name:<29} {field_type:<9} {field_alias:<45} {field_length:>5} {default_value:>3} {dmomain:<1}],')
            del key, field_name, field_type, field_alias, field_length, default_value, dmomain
        del dataset_dictionary
        del FieldListReport

        del workspace, wildcard, dataSets
    except:
        import traceback
        traceback.print_exc()
        del traceback

def generateLayerSpeciesYearImageName():
    try:
        layerspeciesyearimagename = os.path.join(ProjectGDB, "LayerSpeciesYearImageName")

        if not arcpy.Exists(layerspeciesyearimagename) or CreateLayerSpeciesYearImageName:
            Sequential = False
            mpHandlerCreateLayerSpeciesYearImageName(Sequential)
            del Sequential

        #del args
##        CreateLayerSpeciesYearImageName, CSV_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder = args
##
##        layerspeciesyearimagename = os.path.join(ProjectGDB, "LayerSpeciesYearImageName")
##
##        if not arcpy.Exists(layerspeciesyearimagename):
##            raise Exception
##
##        del args

        fields = [f.name for f in arcpy.ListFields(layerspeciesyearimagename) if f.type not in ['Geometry', 'OID']]

        #print(len(fields))

        layerSpeciesYearImageNameFilter = []
        with arcpy.da.SearchCursor(layerspeciesyearimagename, fields) as cursor:
            for row in cursor:
                layerSpeciesYearImageNameFilter.append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19]])
                del row
        del cursor, layerspeciesyearimagename, fields

        return layerSpeciesYearImageNameFilter

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

def generateMasterSpeciesInformation():
    try:
        masterspeciesinformation_table = os.path.join(ProjectGDB, "MasterSpeciesInformation")

        CreateMasterSpeciesInformationTable = False
        if not arcpy.Exists(masterspeciesinformation_table) or CreateMasterSpeciesInformationTable:
            createMasterSpeciesInformationTable(args)
        del CreateMasterSpeciesInformationTable, args

        fields = [f.name for f in arcpy.ListFields(masterspeciesinformation_table) if f.type not in ['Geometry', 'OID']]

        masterspeciesinformation = []
        with arcpy.da.SearchCursor(masterspeciesinformation_table, fields) as cursor:
            for row in cursor:
                masterspeciesinformation.append([row[0],row[1],row[2],row[3],row[4]])
                del row
        del cursor, masterspeciesinformation_table, fields

        return masterspeciesinformation

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def generateSpeciesFilter():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        speciesfilter_table = os.path.join(ProjectGDB, "Species_Filter")

        if not arcpy.Exists(speciesfilter_table):
            createSpeciesFilterTable()

        fields = [f.name for f in arcpy.ListFields(speciesfilter_table) if f.type not in ['Geometry', 'OID']]

        # Pretty prints column names and row reference for the search cursor
        #for field in fields:
        #    print(f"\t\t\t\t{field.lower().ljust(15, ' ')} = row[{fields.index(field)}]")
        #for field in fields:
        #    print(f"# # {field.lower().ljust(15, ' ')} = speciesfilter[{fields.index(field)}]")
        #print(", ".join(fields).lower())

        speciesfilter = []
        with arcpy.da.SearchCursor(speciesfilter_table, fields) as cursor:
            for row in cursor:
                species         = row[0]
                commonname      = row[1]
                taxonomicgroup  = row[2]
                filterregion    = row[3]
                filtersubregion = row[4]
                managementbody  = row[5]
                managementplan  = row[6]
                speciesfilter.append([
                                      species, commonname, taxonomicgroup,
                                      filterregion, filtersubregion,
                                      managementbody, managementplan
                                     ])
                del row
                del species, commonname, taxonomicgroup, filterregion
                del filtersubregion, managementbody, managementplan

        del cursor, speciesfilter_table, fields

# # species         = speciesfilter[0]
# # commonname      = speciesfilter[1]
# # taxonomicgroup  = speciesfilter[2]
# # filterregion    = speciesfilter[3]
# # filtersubregion = speciesfilter[4]
# # managementbody  = speciesfilter[5]
# # managementplan  = speciesfilter[6]

        return speciesfilter

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
        del speciesfilter
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

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

        datasets = generateDatasets()

        with arcpy.EnvManager(scratchWorkspace = ScratchFolder, workspace = ProjectGDB):
            wc = f"_Points"
            fcs = arcpy.ListFeatureClasses(f"*{wc}")
            datasets = [[r for r in group] for group in datasets if f"{group[3]}{wc}" in fcs]
            del fcs, wc

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        # Start looping over the datasets array as we go region by region.
        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            region                  = datasets[i][8]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            # Region DMS Points
            datasetcode_dms_points = f"{dataset_product_code}_Points"

            fields = ['DMSLat', 'DMSLong',]

            import math
            # For each row, print the DMSLat and DMSLong fields, and
            # the feature's x,y coordinates
            with arcpy.da.SearchCursor(datasetcode_dms_points, fields) as cursor:
                ns = []; ew = []
                for row in cursor:
                    ns.append( round(int(row[0][:2]) + (float(row[0][3:5]) / 60 ), 3) )
                    ew.append( round(int(row[1][:3]) + (float(row[1][4:6]) / 60 ), 3) )
                    del row

                n = math.ceil(max(ns) * 5.0) / 5.0
                w = math.floor(max(ew) * 5.0) / 5.0
                e = math.ceil(min(ew) * 5.0)/5.0
                s = math.floor(min(ns) * 5.0)/5.0

                msg = f"\t\t# {region} ({datasetcode}) = N {n} W -{w} E -{e} S {s}"
                logFile(log_file, msg); del msg
                # gebco_2022_n35.4_s28.6_w-81.4_e-75.6.asc
                msg = f"\t\t#\t 'gebco_2022_n{n}_s{s}_w-{w}_e-{e}.asc'"
                logFile(log_file, msg); del msg

                del ns, ew, n, w, e, s

            del fields, cursor, math

            # Delete after last use
            del datasetcode_dms_points, datasetcode, region, dataset_product_code
            del distributionprojectcode

        del datasets

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def importEPU():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

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

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def importArcGisMetadata():
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        from arcpy import metadata as md

        ProcessDisMAPRegionsAndTables = True
        if ProcessDisMAPRegionsAndTables:
            msg = f"> Processing DisMAP_Region, Indicators, Datasets, Species_Filter Layers."
            logFile(log_file, msg); del msg

            datasets = generateDatasets()

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                layer_list = ["DisMAP_Regions", "Indicators", "Datasets", "Species_Filter",]
                #layer_list = ["DisMAP_Regions"]
                datasets = [[r for r in group] for group in datasets if group[0] in layer_list]
                del layer_list

            #if FilterDatasets:
            #    datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

            if not datasets:
                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            for i in range(len(datasets)):
                datasetcode         = datasets[i][0]
                tablename           = datasets[i][3]
                featureclassname    = datasets[i][7]
                region              = datasets[i][8]
                season              = datasets[i][9]
                datecode            = datasets[i][10]
                featureservicetitle = datasets[i][18]
                del i

                msg = f"  > Processing {featureservicetitle} Layer."
                logFile(log_file, msg); del msg

                if featureclassname == "DisMAP_Regions":
                    with arcpy.EnvManager(scratchWorkspace=ScratchGDB, workspace=ProjectGDB):
                        #prettyXML(template_metadata)
                        # Export Metadata File
                        #export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{layername}.xml")
                        #layertitle_md = md.Metadata(layername)
                        #layertitle_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
                        #prettyXML(export_metadata)
                        #del export_metadata
                        #empty_xml = os.path.join(ARCGIS_METADATA_DIRECTORY, "empty.xml")
                        #layertitle_md.importMetadata(empty_xml, 'ARCGIS_METADATA')
                        #layertitle_md.importMetadata(empty_xml)
                        #layertitle_md.synchronize('OVERWRITE')
                        #layertitle_md.save()
                        #layertitle_md.reload()
                        #del empty_xml

                        template_metadata = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{featureservicetitle}.xml")

                        layertitle_md = md.Metadata(featureclassname)

                        thumbnail = os.path.join(LAYER_DIRECTORY, f"{featureservicetitle}.png")
                        layertitle_md.deleteContent('GPHISTORY')
                        layertitle_md.synchronize('SELECTIVE')
                        layertitle_md.importMetadata(template_metadata, 'ARCGIS_METADATA')
                        layertitle_md.title = f"{featureservicetitle}"
                        layertitle_md.save()
                        layertitle_md.reload()
                        if arcpy.Exists(thumbnail):
                            layertitle_md.thumbnailUri = thumbnail
                            layertitle_md.save()
                        del thumbnail
                        layertitle_md.reload()

                        regions = unique_values(featureclassname, "Region")
                        tags = "; ".join(regions)
                        #print(tags)

                        layertitle_md.tags = tags + ', ' + layertitle_md.tags
                        layertitle_md.save()
                        layertitle_md.reload()
                        del tags

                        msg = f"\t\t Title: {layertitle_md.title}"
                        print(msg); del msg

    # #                    msg = f"\t\t Tags: {layertitle_md.tags}"
    # #                    print(msg); del msg
    # #
    # #                    msg = f"\t\t Summary: {layertitle_md.summary}"
    # #                    print(msg); del msg
    # #
    # #                    msg = f"\t\t Description: {layertitle_md.description}"
    # #                    print(msg); del msg
    # #
    # #                    msg = f"\t\t Credits: {layertitle_md.credits}"
    # #                    print(msg); del msg

                        export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureservicetitle}.xml")

                        layertitle_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
                        del layertitle_md

                        prettyXML(export_metadata)

                        del template_metadata, export_metadata
                        del datecode, region, season, regions

                elif tablename in ["Indicators", "Datasets", "Species_Filter",]:
                    with arcpy.EnvManager(scratchWorkspace=ScratchGDB, workspace=ProjectGDB):

                        template_metadata = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{featureservicetitle}.xml")

                        #prettyXML(template_metadata)

                        # Export Metadata File
                        #export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{layername}.xml")

                        layertitle_md = md.Metadata(tablename)
                        layertitle_md.deleteContent('GPHISTORY')
                        layertitle_md.synchronize('SELECTIVE')
                        layertitle_md.importMetadata(template_metadata, 'ARCGIS_METADATA')
                        layertitle_md.title = f"{featureservicetitle}"
                        layertitle_md.save()
                        layertitle_md.reload()

                        #layertitle_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
                        #prettyXML(export_metadata)

                        msg = "\t\t Title: {0}".format(layertitle_md.title)
                        print(msg); del msg

    # #                    msg = "\t\t Tags: {0}".format(layertitle_md.tags)
    # #                    print(msg); del msg
    # #
    # #                    msg = "\t\t Summary: {0}".format(layertitle_md.summary)
    # #                    print(msg); del msg
    # #
    # #                    msg = "\t\t Description: {0}".format(layertitle_md.description)
    # #                    print(msg); del msg
    # #
    # #                    msg = "\t\t Credits: {0}".format(layertitle_md.credits)
    # #                    print(msg); del msg

                        export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureservicetitle}.xml")

                        layertitle_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
                        del layertitle_md

                        prettyXML(export_metadata)

                        del template_metadata, export_metadata
                        del datecode, region, season

                del datasetcode, tablename, featureclassname, featureservicetitle
            del datasets
        del ProcessDisMAPRegionsAndTables

        ProcessingSampleLocationLayers = True
        if ProcessingSampleLocationLayers:
            msg = f"> Processing Sample Location Layers."
            logFile(log_file, msg); del msg

            datasets = generateDatasets()

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                wc = "_Sample_Locations"
                fcs = arcpy.ListFeatureClasses(f"*{wc}")
                datasets = [[r for r in group] for group in datasets if group[7] in fcs]
                del wc, fcs

            if FilterDatasets:
                datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

            if not datasets:
                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            for i in range(len(datasets)):
                datasetcode         = datasets[i][0]
                #tablename           = datasets[i][3]
                featureclassname    = datasets[i][7]
                region              = datasets[i][8]
                season              = datasets[i][9]
                datecode            = datasets[i][10]
                featureservicetitle = datasets[i][18]
                del i

                msg = f"  > Processing {featureservicetitle} Layer."
                logFile(log_file, msg); del msg

                with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                    # Export Metadata File
                    #export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureclassname}.xml")
                    #layertitle_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
                    #prettyXML(export_metadata)
                    #del export_metadata
                    #empty_xml = os.path.join(ARCGIS_METADATA_DIRECTORY, "empty.xml")
                    #layertitle_md.importMetadata(empty_xml, 'ARCGIS_METADATA')
                    #layertitle_md.importMetadata(empty_xml)
                    #layertitle_md.synchronize('OVERWRITE')
                    #layertitle_md.save()
                    #layertitle_md.reload()
                    #del empty_xml

                    #layertitle_md = md.Metadata(featureclassname)
                    #empty_xml = os.path.join(ARCGIS_METADATA_DIRECTORY, "empty.xml")
                    #layertitle_md.importMetadata(empty_xml, 'ARCGIS_METADATA')
                    #layertitle_md.importMetadata(empty_xml)
                    #layertitle_md.synchronize('OVERWRITE')
                    #layertitle_md.save()
                    #layertitle_md.reload()
                    #del empty_xml, layertitle_md

                    template_metadata = os.path.join(ARCGIS_METADATA_DIRECTORY, f"Survey catch-per-unit-effort {datecode}.xml")

                    #print(template_metadata)
                    #template_md = md.Metadata(template_metadata)
                    #msg = "\t\t Title: {0}".format(template_md.title)
                    #print(msg); del msg
                    #msg = "\t\t Tags: {0}".format(template_md.tags)
                    #print(msg); del msg
                    #msg = "\t\t Summary: {0}".format(template_md.summary)
                    #print(msg); del msg
                    #msg = "\t\t Description: {0}".format(template_md.description)
                    #print(msg); del msg
                    #msg = "\t\t Credits: {0}".format(template_md.credits)
                    #print(msg); del msg
                    #del template_md

                    layertitle_md = md.Metadata(featureclassname)

                    #layertitle_md.synchronize('ACCESSED', 1)
                    #layertitle_md.synchronize('ALWAYS', 1)
                    #layertitle_md.synchronize('CREATED', 1)
                    #layertitle_md.synchronize('NOT_CREATED', 1)
                    #layertitle_md.synchronize('OVERWRITE')
                    #layertitle_md.synchronize('SELECTIVE')
                    thumbnail = os.path.join(LAYER_DIRECTORY, f"{featureservicetitle}.png")
                    layertitle_md.deleteContent('GPHISTORY')
                    layertitle_md.synchronize('SELECTIVE')
                    #layertitle_md.save()
                    #layertitle_md.reload()
                    #layertitle_md.synchronize('ALWAYS')
                    #layertitle_md.copy(template_md)
                    #layertitle_md.save()
                    #layertitle_md.reload()
                    layertitle_md.importMetadata(template_metadata, 'ARCGIS_METADATA')
                    layertitle_md.title = f"{featureservicetitle}"
                    layertitle_md.save()
                    layertitle_md.reload()
                    if arcpy.Exists(thumbnail):
                        layertitle_md.thumbnailUri = thumbnail
                        layertitle_md.save()
                    del thumbnail
                    layertitle_md.reload()

                    del template_metadata

                    #msg = "\t\t Title: {0}".format(layertitle_md.title)
                    #print(msg); del msg
                    #msg = "\t\t Tags: {0}".format(layertitle_md.tags)
                    #print(msg); del msg
                    #msg = "\t\t Summary: {0}".format(layertitle_md.summary)
                    #print(msg); del msg
                    #msg = "\t\t Description: {0}".format(layertitle_md.description)
                    #print(msg); del msg
                    #msg = "\t\t Credits: {0}".format(layertitle_md.credits)
                    #print(msg); del msg

                    #if not layertitle_md.isReadOnly:
                    #layertitle_md.synchronize('ALWAYS')
                    fields = [f.name for f in arcpy.ListFields(featureclassname)  if f.type not in ['Geometry', 'OID']]

                    if 'Year' in fields:
                        years_md = unique_years(featureclassname)
                        if years_md:
                            tags = f"{region}, {min(years_md)} to {max(years_md)}"
                        else:
                            tags = f"{region}"
                        del years_md
                    else:
                        tags = f"{region}"

                    del fields

                    layertitle_md.tags = tags + ', ' + layertitle_md.tags
                    layertitle_md.save()
                    layertitle_md.reload()
                    del tags

                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureservicetitle}.xml")

                    layertitle_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')

                    prettyXML(export_metadata)
                    del export_metadata
                    del layertitle_md

                del datasetcode, region, season, datecode, featureclassname, featureservicetitle
            del datasets
        del ProcessingSampleLocationLayers

        ProcessingMosaicLayers = True
        if ProcessingMosaicLayers:
            msg = f" > Processing Mosaic Layers."
            logFile(log_file, msg); del msg

            datasets = generateDatasets()

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                wc = ""
                mss = arcpy.ListDatasets(f"*{wc}")
                datasets = [[r for r in group] for group in datasets if group[19] in mss]
                del wc, mss

            if FilterDatasets:
                datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

            if not datasets:
                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            for i in range(len(datasets)):
                region      = datasets[i][8]
                season      = datasets[i][9]
                datecode    = datasets[i][10]
                mosaicname  = datasets[i][19]
                mosaictitle = datasets[i][20]
                del i

                msg = f"  > Processing {mosaictitle} Layer."
                logFile(log_file, msg); del msg

                with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                    # Export Metadata File
                    #export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname}.xml")
                    #mosaicname_md = md.Metadata(mosaicname)
                    #mosaicname_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
                    #prettyXML(export_metadata)
                    #del export_metadata
                    #empty_xml = os.path.join(ARCGIS_METADATA_DIRECTORY, "empty.xml")
                    #mosaicname_md.importMetadata(empty_xml, 'ARCGIS_METADATA')
                    #mosaicname_md.importMetadata(empty_xml)
                    #mosaicname_md.synchronize('OVERWRITE')
                    #mosaicname_md.save()
                    #mosaicname_md.reload()
                    #del empty_xml

                    template_metadata = os.path.join(ARCGIS_METADATA_DIRECTORY, f"Fish and Invertebrate Interpolated Biomass Distribution Surfaces {datecode}.xml")

                    mosaicname_md = md.Metadata(mosaicname)

                    thumbnail = os.path.join(LAYER_DIRECTORY, f"{mosaictitle}.png")
                    mosaicname_md.deleteContent('GPHISTORY')
                    mosaicname_md.synchronize('SELECTIVE')
                    mosaicname_md.importMetadata(template_metadata, 'ARCGIS_METADATA')
                    mosaicname_md.title = f"{mosaictitle}"
                    mosaicname_md.save()
                    if arcpy.Exists(thumbnail):
                        mosaicname_md.thumbnailUri = thumbnail
                        mosaicname_md.save()
                    del thumbnail
                    mosaicname_md.reload()

                    msg = "\t\t Title: {0}".format(mosaicname_md.title)
                    print(msg); del msg

# #                    msg = "\t\t Tags: {0}".format(mosaicname_md.tags)
# #                    print(msg); del msg
# #
# #                    msg = "\t\t Summary: {0}".format(mosaicname_md.summary)
# #                    print(msg); del msg
# #
# #                    msg = "\t\t Description: {0}".format(mosaicname_md.description)
# #                    print(msg); del msg
# #
# #                    msg = "\t\t Credits: {0}".format(mosaicname_md.credits)
# #                    print(msg); del msg

                    if not mosaicname_md.isReadOnly:
                        mosaicname_md.synchronize('OVERWRITE')
                        fields = [f.name for f in arcpy.ListFields(mosaicname) if f.type not in ['Geometry', 'OID']]

                        if 'Year' in fields:
                            years_md = unique_years(mosaicname)
                            if years_md:
                                tags = f"{region}, {min(years_md)} to {max(years_md)}"
                            else:
                                tags = f"{region}"
                            del years_md
                        else:
                            tags = f"{region}"

                        del fields

                        mosaicname_md.tags = tags + ', ' + mosaicname_md.tags
                        mosaicname_md.save()
                        mosaicname_md.reload()
                        del tags

                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaictitle}.xml")

                    mosaicname_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
                    del mosaicname_md

                    prettyXML(export_metadata)

                    del template_metadata, export_metadata
                del mosaicname, mosaictitle, datecode, region, season
            del datasets
        del ProcessingMosaicLayers

        ProcessingCRFLayers = True
        if ProcessingCRFLayers:
            msg = f" > Processing CRF Layers."
            logFile(log_file, msg); del msg

            datasets = generateDatasets()

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):
                wc = ""
                crfs = [crf[:-4] for crf in arcpy.ListFiles(f"*{wc}*")]
                datasets = [[r for r in group] for group in datasets if group[3] in crfs]
                del wc, crfs

            if FilterDatasets:
                datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

            if not datasets:
                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            for i in range(len(datasets)):
                #tablename   = datasets[i][3]
                crfname      = datasets[i][3]
                region       = datasets[i][8]
                season       = datasets[i][9]
                datecode     = datasets[i][10]
                #mosaicname  = datasets[i][19]
                #mosaictitle = datasets[i][20]
                crftitle     = datasets[i][20]
                del i

                msg = f"  > Processing {crftitle} Layer."
                logFile(log_file, msg); del msg

                with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):
                    template_metadata = os.path.join(ARCGIS_METADATA_DIRECTORY, f"Fish and Invertebrate Interpolated Biomass Distribution Surfaces {datecode}.xml")

                    mosaicname_md = md.Metadata(f"{crfname}.crf")

                    thumbnail = os.path.join(LAYER_DIRECTORY, f"{crftitle}.png")
                    mosaicname_md.deleteContent('GPHISTORY')
                    mosaicname_md.synchronize('OVERWRITE')
                    mosaicname_md.importMetadata(template_metadata, 'ARCGIS_METADATA')
                    mosaicname_md.title = f"{crftitle}"
                    mosaicname_md.save()
                    if arcpy.Exists(thumbnail):
                        mosaicname_md.thumbnailUri = thumbnail
                        mosaicname_md.save()
                    del thumbnail
                    mosaicname_md.reload()

                    msg = "\t\t Title: {0}".format(mosaicname_md.title)
                    print(msg); del msg

    # #                    msg = "\t\t Tags: {0}".format(crfname_metadata_md.tags)
    # #                    print(msg); del msg
    # #
    # #                    msg = "\t\t Summary: {0}".format(crfname_metadata_md.summary)
    # #                    print(msg); del msg
    # #
    # #                    msg = "\t\t Description: {0}".format(crfname_metadata_md.description)
    # #                    print(msg); del msg
    # #
    # #                    msg = "\t\t Credits: {0}".format(crfname_metadata_md.credits)
    # #                    print(msg); del msg

                    if not mosaicname_md.isReadOnly:
                        mosaicname_md.synchronize('OVERWRITE')
                        fields = [f.name for f in arcpy.ListFields(f"{crfname}.crf") if f.type not in ['Geometry', 'OID']]

                        if 'Year' in fields:
                            years_md = unique_years(f"{crfname}.crf")
                            if years_md:
                                tags = f"{region}, {min(years_md)} to {max(years_md)}"
                            else:
                                tags = f"{region}"
                            del years_md
                        else:
                            tags = f"{region}"

                        del fields

                        mosaicname_md.tags = tags + ', ' + mosaicname_md.tags
                        mosaicname_md.save()
                        mosaicname_md.reload()
                        del tags

                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{crftitle} CRF.xml")

                    mosaicname_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
                    del mosaicname_md

                    prettyXML(export_metadata)

                    del template_metadata, export_metadata
                del crfname, crftitle, region, season, datecode
            del datasets
        del ProcessingCRFLayers

        del md

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
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
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            logFile(log_file, msg); del msg

        del localKeys, function, log_file

def importMetadata():
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

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

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

        arcpy.env.overwriteOutput = True

        from arcpy import metadata as md

        msg = f"> Importing Metadata"
        logFile(log_file, msg); del msg

        datasets = []
##        #with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
##            tb_list = [os.path.join(ProjectGDB, tb) for tb in arcpy.ListTables("*") if tb in ['Indicators', 'Datasets', 'Species_Filter']]
##            # # fc_list = [os.path.join(ProjectGDB, fc) for fc in arcpy.ListFeatureClasses("*Sample_Locations")] #
##            fc_list = [os.path.join(ProjectGDB, fc) for fc in arcpy.ListFeatureClasses("*") if "Sample_Locations" in fc or "DisMAP_Regions" in fc] #
##            ms_list = [os.path.join(ProjectGDB, ms) for ms in arcpy.ListDatasets(feature_type='Mosaic')] # if ms in ['AI_IDW_Mosaic']]
##            rs_list = [rs for rs in arcpy.ListDatasets(feature_type='Raster') if rs in ['AI_IDW_Mask']]
##        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):
##            #crf_list = [os.path.join(MOSAIC_DIRECTORY, crf) for crf in arcpy.ListFiles(f"*.crf") if crf in ['AI_IDW.crf','WC_GLMME.crf']]
##            crf_list = [os.path.join(MOSAIC_DIRECTORY, crf) for crf in arcpy.ListFiles(f"*.crf")]
##
##        datasets.extend(tb_list);  del tb_list
##        datasets.extend(fc_list);  del fc_list
##        datasets.extend(ms_list);  del ms_list
##        datasets.extend(rs_list);  del rs_list
##        datasets.extend(crf_list); del crf_list

        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            tb_list = [os.path.join(ProjectGDB, tb) for tb in arcpy.ListTables("*")]
            fc_list = [os.path.join(ProjectGDB, fc) for fc in arcpy.ListFeatureClasses("*")]
            ms_list = [os.path.join(ProjectGDB, ms) for ms in arcpy.ListDatasets(feature_type='Mosaic')]
            rs_list = [os.path.join(ProjectGDB, rs) for rs in arcpy.ListDatasets(feature_type='Raster')]
        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):
            crf_list = [os.path.join(MOSAIC_DIRECTORY, crf) for crf in arcpy.ListFiles(f"*.crf")]

        datasets.extend(tb_list);  del tb_list
        datasets.extend(fc_list);  del fc_list
        datasets.extend(ms_list);  del ms_list
        datasets.extend(rs_list);  del rs_list
        datasets.extend(crf_list); del crf_list

        #print(EXPORT_METADATA_DIRECTORY)
        #Loop through all datasets in the database that are specified in the workspace
        for dataset in sorted(datasets):
            print(f"Dataset: {os.path.basename(dataset)}")
            #print(f"\tPath: {dataset}")

            if '.crf' in dataset:
                dataset_metadata = f"{os.path.basename(dataset).replace('.crf','_CRF')}.xml"
            else:
                dataset_metadata = f"{os.path.basename(dataset)}.xml"

            #empty_xml_file = os.path.join(ARCGIS_METADATA_DIRECTORY, f"empty.xml")
            #prettyXML(empty_xml_file)
            #entity_xml = os.path.join(ARCGIS_METADATA_DIRECTORY, f"EntityMetadata.xml")
            dataset_xml_file = os.path.join(ARCGIS_METADATA_DIRECTORY, dataset_metadata)
            #dataset_xml_file_template = os.path.join(ARCGIS_METADATA_DIRECTORY, dataset_metadata.replace('.xml', ' TEMPLATE.xml'))
            del dataset_metadata

            if arcpy.Exists(dataset_xml_file):

                # Process: Export Metadata
                print(f"> Creating dataset Metadata Object for {os.path.basename(dataset)}")
                #print(dataset)
                dataset_md = md.Metadata(dataset)

                print(f" > Importing: {os.path.basename(dataset_xml_file)}")

                # #dataset_md.synchronize("ALWAYS")
                dataset_md.synchronize("SELECTIVE")
                dataset_md.importMetadata(dataset_xml_file, "DEFAULT")
                dataset_md.save()
                dataset_md.reload()
                dataset_md.synchronize("ACCESSED")
                dataset_md.save()
                dataset_md.reload()

                if not dataset_md.isReadOnly:
                    dataset_md.deleteContent('GPHISTORY')
                    dataset_md.deleteContent('ENCLOSED_FILES')
                    #dataset_md.deleteContent('THUMBNAIL')
                    dataset_md.save()
                    dataset_md.reload()

                del dataset_md

            else:

                # Process: Export Metadata
                print(f"> Creating dataset Metadata Object for {os.path.basename(dataset)}")
                #print(dataset)
                dataset_md = md.Metadata(dataset)

                print(f" > Creating basic metadata")

                dataset_md.synchronize("ACCESSED")
                dataset_md.save()
                dataset_md.reload()

                dataset_md.title             = f'{os.path.basename(dataset)}'
                dataset_md.tags              = f'{os.path.basename(dataset)}'
                dataset_md.summary           = f'{os.path.basename(dataset)}, Summary'
                dataset_md.description       = f'{os.path.basename(dataset)}, Description'
                dataset_md.credits           = f'{os.path.basename(dataset)}, Credits'
                dataset_md.accessConstraints = f'{os.path.basename(dataset)}, Access Constraints'

                if not dataset_md.isReadOnly:
                    dataset_md.deleteContent('GPHISTORY')
                    dataset_md.deleteContent('ENCLOSED_FILES')
                    #dataset_md.deleteContent('THUMBNAIL')
                    dataset_md.save()
                    dataset_md.reload()

                del dataset_md

            del dataset, dataset_xml_file

        del md, datasets

        PrettyAllXML = False
        if PrettyAllXML:
            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ARCGIS_METADATA_DIRECTORY):
                xml_list = [os.path.join(ARCGIS_METADATA_DIRECTORY, xml) for xml in arcpy.ListFiles(f"*.xml")]
                for xml in xml_list:
                    prettyXML(xml)
                    del xml
                del xml_list
        del PrettyAllXML


##            if "Sample_Locations" in os.path.basename(dataset):
##                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset)}.xml")
##            elif "DisMAP_Regions" in os.path.basename(dataset):
##                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset)}.xml")
##            elif "Indicators" in os.path.basename(dataset):
##                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset)}.xml")
##            elif "GRID_Points" in os.path.basename(dataset):
##                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset)}.xml")
##            elif "Mosaic" in os.path.basename(dataset):
##                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset)}.xml")
##            elif ".crf" in os.path.basename(dataset):
##                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{os.path.basename(dataset.replace('.crf','_Mosaic'))}.xml")
##            else:
##                dataset_template = os.path.join(ARCGIS_METADATA_DIRECTORY, f"EntityMetadata.xml")
##
##            if arcpy.Exists(dataset_template):
##                prettyXML(dataset_template)
##
##            ImportDatasetMetadata = False
##            print(f" > Importing: {dataset_template}")
##            if ImportDatasetMetadata:
##                # #dataset_md.synchronize("ALWAYS")
##                dataset_md.synchronize("SELECTIVE")
##                dataset_md.importMetadata(dataset_template, "DEFAULT")
##                dataset_md.save()
##                dataset_md.reload()
##                dataset_md.synchronize("ACCESSED")
##                dataset_md.save()
##                dataset_md.reload()
##            del dataset_template, ImportDatasetMetadata
##
##            #dataset_md.synchronize("ACCESSED", 0)
##            #dataset_md.synchronize("ALWAYS")
##            #dataset_md.synchronize("CREATED", 0)
##            #dataset_md.synchronize("NOT_CREATED", 0)
##            #dataset_md.synchronize("OVERWRITE")
##            #dataset_md.synchronize("SELECTIVE")
##
##            #dataset_md.synchronize("OVERWRITE")
##            #dataset_md.importMetadata(empty_xml_file, "DEFAULT")
##            #dataset_md.save()
##            #dataset_md.reload()
##            #del empty_xml_file
##
##            if not dataset_md.isReadOnly:
##                dataset_md.deleteContent('GPHISTORY')
##                dataset_md.deleteContent('ENCLOSED_FILES')
##                dataset_md.deleteContent('THUMBNAIL')
##                dataset_md.save()
##                dataset_md.reload()
##
##            ExportDatasetMetadata = True
##            if ExportDatasetMetadata:
##                print(f" > Saving dataset metadata as an 'EXACT_COPY' file: {os.path.basename(dataset_xml_file)}")
##                dataset_md.saveAsXML(dataset_xml_file, 'EXACT_COPY')
##
##                #print(f" > Saving dataset metadata as 'REMOVE_ALL_SENSITIVE_INFO' file: {os.path.basename(dataset_xml_file_template)}")
##                #dataset_md.saveAsXML(dataset_xml_file_template, 'REMOVE_ALL_SENSITIVE_INFO')
##
##                print(f" > Saving dataset as an 'TEMPLATE' file: {os.path.basename(dataset_xml_file_template)}")
##                #dataset_md.saveAsXML(dataset_xml_file_template, 'TEMPLATE')
##                #dataset_md.exportMetadata(dataset_xml_file_template.replace('TEMPLATE', 'FGDC_CSDGM'), 'FGDC_CSDGM', 'REMOVE_ALL_SENSITIVE_INFO')
##
##                prettyXML(dataset_xml_file)
##                #prettyXML(dataset_xml_file_template)
##                #prettyXML(dataset_xml_file_template.replace('TEMPLATE', 'FGDC_CSDGM'))
##            del ExportDatasetMetadata
##
##            del dataset_md, dataset_xml_file, dataset_xml_file_template


# # # Delete???
##            xml_file = os.path.join(EXPORT_METADATA_DIRECTORY, f"{os.path.basename(dataset).replace('.crf','')}_xml.xml")
##            xml_file_template = os.path.join(EXPORT_METADATA_DIRECTORY, f"{os.path.basename(dataset).replace('.crf','')}_TEMPLATE.xml")
##            empty_xml_file = os.path.join(EXPORT_METADATA_DIRECTORY, f"empty.xml")
##
##            xml_file_exact_copy = xml_file.replace('_xml.xml', '_xml EXACT_COPY.xml')
##            xml_file_exact_copy_fgdc = xml_file_exact_copy.replace('_xml EXACT_COPY.xml', '_xml EXACT_COPY FGDC.xml')
##            xml_file_exact_copy_updated = xml_file_exact_copy.replace('_xml EXACT_COPY.xml', '_xml EXACT_COPY Updated.xml')
##            xml_file_template_updated = xml_file_template.replace('_TEMPLATE.xml', '_TEMPLATE Updated.xml')
##
##            #dataset = os.path.join(ProjectGDB, dataset)
##            # Process: Export Metadata
##            print(f"> Creating dataset Metadata Object")
##            dataset_md = md.Metadata(dataset)
##            # Synchronize the item's metadata now
##            dataset_md.synchronize('ALWAYS')
##            #dataset_md.synchronize("OVERWRITE")
##            dataset_md.save()
##            dataset_md.reload()
##            print(f"> Saving dataset as an 'EXACT_COPY' file: {os.path.basename(xml_file)}")
##            dataset_md.saveAsXML(xml_file, 'EXACT_COPY')
##            dataset_md.saveAsXML(xml_file_exact_copy, 'EXACT_COPY')
##            print(f"> Exporting dataset as an 'FGDC_CSDGM' file: {os.path.basename(xml_file)}")
##            dataset_md.exportMetadata(xml_file.replace('.xml',' FGDC.xml'), 'FGDC_CSDGM', 'REMOVE_ALL_SENSITIVE_INFO')
##            dataset_md.synchronize('OVERWRITE')
##            dataset_md.importMetadata(xml_file.replace('.xml',' FGDC.xml'), 'FGDC_CSDGM')
##            dataset_md.save()
##            dataset_md.reload()
##            print(f"> Saving dataset as an 'EXACT_COPY' file: {os.path.basename(xml_file)}")
##            dataset_md.saveAsXML(xml_file, 'EXACT_COPY')
##            print(f"> Saving dataset as a 'TEMPLATE' file: {os.path.basename(xml_file_template)}")
##            dataset_md.saveAsXML(xml_file_template, 'TEMPLATE')
##            #dataset_md.synchronize("ALWAYS")
##            #dataset_md.importMetadata(empty_xml_file, "DEFAULT")
##            #dataset_md.synchronize("OVERWRITE")
##
##            del dataset_md
##
##            #prettyXML(xml_file)
##            #prettyXML(xml_file_template)
##
##            dataset_md = md.Metadata(xml_file_exact_copy)
##            if not dataset_md.isReadOnly:
##                dataset_md.deleteContent('GPHISTORY')
##                dataset_md.deleteContent('ENCLOSED_FILES')
##                dataset_md.deleteContent('THUMBNAIL')
##                dataset_md.save()
##                dataset_md.reload()
##
##            #dataset_md.synchronize("ACCESSED", 0)
##            #dataset_md.synchronize("ALWAYS")
##            #dataset_md.synchronize("CREATED", 0)
##            #dataset_md.synchronize("NOT_CREATED", 0)
##            #dataset_md.synchronize("OVERWRITE")
##            dataset_md.synchronize("SELECTIVE")
##            dataset_md.save()
##            dataset_md.reload()
##
##            if "Indicators" in os.path.basename(dataset):
##                dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Indicators Template.xml"))
##            elif "DisMAP_Regions" in os.path.basename(dataset):
##                dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "DisMAP Regions Template.xml"))
##            elif "_Sample_Locations" in os.path.basename(dataset):
##                dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Sample Locations Template.xml"))
##            elif "_Mosaic" in os.path.basename(dataset):
##                dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Biomass Rasters Template.xml"))
##            elif ".crf" in os.path.basename(dataset):
##                dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Biomass Rasters Template.xml"))
##
##
##            if "Indicators" in os.path.basename(dataset):
##                if not dataset_md.isReadOnly:
##                    dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Indicators Template.xml"))
##            elif "DisMAP_Regions" in os.path.basename(dataset):
##                if not dataset_md.isReadOnly:
##                    dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "DisMAP Regions Template.xml"))
##            elif "_Sample_Locations" in os.path.basename(dataset):
##                if not dataset_md.isReadOnly:
##                    dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Sample Locations Template.xml"))
##            elif "_Mosaic" in os.path.basename(dataset):
##                if not dataset_md.isReadOnly:
##                    dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Biomass Rasters Template.xml"))
##            elif ".crf" in os.path.basename(dataset):
##                if not dataset_md.isReadOnly:
##                    dataset_md.importMetadata(os.path.join(EXPORT_METADATA_DIRECTORY, "Biomass Rasters Template.xml"))
##
##            dataset_md.save()
##            dataset_md.reload()
##
##            print(f"> Exporting dataset as an 'FGDC_CSDGM' file: {os.path.basename(xml_file)}")
##            dataset_md.exportMetadata(xml_file_exact_copy_fgdc, 'FGDC_CSDGM', 'REMOVE_ALL_SENSITIVE_INFO')
##            dataset_md.synchronize('OVERWRITE')
##            dataset_md.importMetadata(xml_file_exact_copy_fgdc, 'FGDC_CSDGM')
##            dataset_md.save()
##            dataset_md.reload()
##            print(f"> Saving dataset as an 'EXACT_COPY' file: {os.path.basename(xml_file)}")
##            dataset_md.saveAsXML(xml_file_exact_copy_updated, 'EXACT_COPY')
##            print(f"> Saving dataset as a 'TEMPLATE' file: {os.path.basename(xml_file_template)}")
##            dataset_md.saveAsXML(xml_file_template_updated, 'TEMPLATE')
##
##            #print(f"> Saving dataset as an 'EXACT_COPY' file: {os.path.basename(xml_file)}")
##            #dataset_md.saveAsXML(xml_file.replace('.xml', ' Update.xml'), 'EXACT_COPY')
##            #print(f"> Saving dataset as a 'TEMPLATE' file: {os.path.basename(xml_file_template)}")
##            #dataset_md.saveAsXML(xml_file_template.replace('.xml', ' Update.xml'), 'TEMPLATE')
##
##            del dataset_md
##
##            #dataset_md.save()
##            #dataset_md.reload()
##            #dataset_md.deleteContent('GPHISTORY')
##            #dataset_md.deleteContent('ENCLOSED_FILES')
##            #dataset_md.deleteContent('THUMBNAIL')
##            #dataset_md.synchronize("OVERWRITE")
##            #dataset_md.save()
##            #dataset_md.reload()
##            #dataset_md.saveAsXML(xml_file, 'REMOVE_ALL_SENSITIVE_INFO')
##            #dataset_md.saveAsXML(xml_file_template, 'TEMPLATE')
##
##            prettyXML(xml_file)
##            prettyXML(xml_file_template)
##            prettyXML(xml_file_exact_copy)
##            prettyXML(xml_file_exact_copy_fgdc)
##            prettyXML(xml_file_template_updated)
##            prettyXML(xml_file_exact_copy_updated)
##
##            del xml_file_template, empty_xml_file
##            del xml_file_exact_copy, xml_file_exact_copy_fgdc, xml_file_exact_copy_updated, xml_file_template_updated
##
##            del dataset, xml_file
##        del md, datasets, tb_list, fc_list, ms_list, crf_list
##
##        datasets = generateDatasets()
##
##        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
##            fcs = arcpy.ListFeatureClasses("*")
##            datasets = [[r for r in group] for group in datasets if group[7] in fcs]
##            del fcs
##
##        if FilterDatasets:
##            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]
##
##        if not datasets:
##            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")
##
##        msg = f"> Processing Tables, Feature Classes, and Mosaics"
##        logFile(log_file, msg); del msg
##
##        for i in range(len(datasets)):
##            datasetcode             = datasets[i][0]
##            tablename               = datasets[i][3]
##            pointfeaturetype        = datasets[i][6]
##            featureclassname        = datasets[i][7]
##            region                  = datasets[i][8]
##            season                  = datasets[i][9]
##            datecode                = datasets[i][10]
##            distributionprojectcode = datasets[i][12]
##            featureservicename      = datasets[i][11]
##            featureservicetitle     = datasets[i][18]
##            mosaicname              = datasets[i][19]
##            mosaictitle             = datasets[i][20]
##            imageservicename        = datasets[i][21]
##            imageservicetitle       = datasets[i][22]
##            del i
##
##            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"
##
##            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
##                #msg = f" > Processing: {dataset_product_code}"
##                #logFile(log_file, msg); del msg
##
##                if tablename:
##                    msg = f" > Processing Table: {tablename}"
##                    logFile(log_file, msg); del msg
##
##                    tablename_md = md.Metadata(tablename)
##
##                    template_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{tablename} Template.xml")
##                    if arcpy.Exists(template_metadata):
##                        tablename_md.importMetadata(template_metadata, 'DEFAULT')
##                        #tablename_md.synchronize("SELECTIVE")
##                        #tablename_md.synchronize("ACCESSED", 0)
##                        #tablename_md.synchronize("NOT_CREATED", 0)
##                        #tablename_md.synchronize("CREATED", 0)
##                        #tablename_md.synchronize("ALWAYS")
##                        #tablename_md.synchronize("OVERWRITE")
##                    del template_metadata
##
##                    #tablename_md.synchronize('ACCESSED')
##                    tablename_md.title = tablename
##                    tablename_md.save()
##                    tablename_md.reload()
##
##                    # Delete all geoprocessing history and any enclosed files from the item's metadata
##                    if not tablename_md.isReadOnly:
##                        tablename_md.deleteContent('GPHISTORY')
##                        #tablename_md.deleteContent('ENCLOSED_FILES')
##                        #tablename_md.deleteContent('THUMBNAIL')
##                        #tablename_md.save()
##                        tablename_md.reload()
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{tablename}.xml")
##                    #tablename_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
##                    tablename_md.saveAsXML(export_metadata, 'EXACT_COPY')
##                    prettyXML(export_metadata); del export_metadata
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{tablename} Template.xml")
##                    tablename_md.saveAsXML(export_metadata, 'TEMPLATE')
##                    prettyXML(export_metadata); del export_metadata
##
##                    del tablename_md
##
##                if featureclassname:
##                    msg = f" > Processing Feature Class: {featureclassname}"
##                    logFile(log_file, msg); del msg
##
##                    featureclassname_md = md.Metadata(featureclassname)
##
##                    template_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureclassname} Template.xml")
##                    if arcpy.Exists(template_metadata):
##                        featureclassname_md.importMetadata(template_metadata, 'DEFAULT')
##                        #featureclassname_md.synchronize("SELECTIVE")
##                        #featureclassname_md.synchronize("ACCESSED", 0)
##                        #featureclassname_md.synchronize("NOT_CREATED", 0)
##                        #featureclassname_md.synchronize("CREATED", 0)
##                        #featureclassname_md.synchronize("ALWAYS")
##                        #featureclassname_md.synchronize("OVERWRITE")
##                    del template_metadata
##
##                    #featureclassname_md.synchronize('ACCESSED')
##                    featureclassname_md.title = featureservicetitle
##                    featureclassname_md.save()
##                    featureclassname_md.reload()
##
##                    # Delete all geoprocessing history and any enclosed files from the item's metadata
##                    if not featureclassname_md.isReadOnly:
##                        featureclassname_md.deleteContent('GPHISTORY')
##                        #featureclassname_md.deleteContent('ENCLOSED_FILES')
##                        #featureclassname_md.deleteContent('THUMBNAIL')
##                        featureclassname_md.save()
##                        featureclassname_md.reload()
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureclassname}.xml")
##                    #featureclassname_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
##                    featureclassname_md.saveAsXML(export_metadata, 'EXACT_COPY')
##                    prettyXML(export_metadata); del export_metadata
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureclassname} Template.xml")
##                    featureclassname_md.saveAsXML(export_metadata, 'TEMPLATE')
##                    prettyXML(export_metadata); del export_metadata
##
##                    del featureclassname_md
##
##                if mosaicname:
##                    msg = f" > Processing Mosaic: {mosaicname}"
##                    logFile(log_file, msg); del msg
##
##                    mosaicname_md = md.Metadata(mosaicname)
##
##                    template_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname} Template.xml")
##                    if arcpy.Exists(template_metadata):
##                        mosaicname_md.importMetadata(template_metadata, 'DEFAULT')
##                        #mosaicname_md.synchronize("SELECTIVE")
##                        #mosaicname_md.synchronize("ACCESSED", 0)
##                        #mosaicname_md.synchronize("NOT_CREATED", 0)
##                        #mosaicname_md.synchronize("CREATED", 0)
##                        #mosaicname_md.synchronize("ALWAYS")
##                        #mosaicname_md.synchronize("OVERWRITE")
##                    del template_metadata
##
##                    #mosaicname_md.synchronize('ACCESSED')
##                    mosaicname_md.title = mosaictitle
##                    mosaicname_md.save()
##                    mosaicname_md.reload()
##
##                    # Delete all geoprocessing history and any enclosed files from the item's metadata
##                    if not mosaicname_md.isReadOnly:
##                        mosaicname_md.deleteContent('GPHISTORY')
##                        #mosaicname_md.deleteContent('ENCLOSED_FILES')
##                        #mosaicname_md.deleteContent('THUMBNAIL')
##                        mosaicname_md.save()
##                        mosaicname_md.reload()
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname}.xml")
##                    #mosaicname_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
##                    mosaicname_md.saveAsXML(export_metadata, 'EXACT_COPY')
##                    prettyXML(export_metadata); del export_metadata
##
##                    export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname} Template.xml")
##                    mosaicname_md.saveAsXML(export_metadata, 'TEMPLATE')
##                    prettyXML(export_metadata); del export_metadata
##
##                    del mosaicname_md
##
##                    msg = f" > Processing CRF: {dataset_product_code}"
##                    logFile(log_file, msg); del msg
##
##                    with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):
##                        crf = f"{dataset_product_code}.crf"
##                        #msg = f" > Processing: {crf}"
##                        #logFile(log_file, msg); del msg
##
##                        crf_md = md.Metadata(crf)
##
##                        template_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname} CRF Template.xml")
##                        if arcpy.Exists(template_metadata):
##                            crf_md.importMetadata(template_metadata, 'DEFAULT')
##                            #crf_md.synchronize("SELECTIVE")
##                            #crf_md.synchronize("ACCESSED", 0)
##                            #crf_md.synchronize("NOT_CREATED", 0)
##                            #crf_md.synchronize("CREATED", 0)
##                            #crf_md.synchronize("ALWAYS")
##                            #crf_md.synchronize("OVERWRITE")
##                        del template_metadata
##
##                        #crf_md.synchronize('ACCESSED')
##                        crf_md.title = mosaictitle
##                        crf_md.save()
##                        crf_md.reload()
##
##                        # Delete all geoprocessing history and any enclosed files from the item's metadata
##                        if not crf_md.isReadOnly:
##                            crf_md.deleteContent('GPHISTORY')
##                            #crf_md.deleteContent('ENCLOSED_FILES')
##                            #crf_md.deleteContent('THUMBNAIL')
##                            crf_md.save()
##                            crf_md.reload()
##
##                        export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname} CRF.xml")
##                        crf_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
##                        prettyXML(export_metadata); del export_metadata
##
##                        export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{mosaicname} CRF Template.xml")
##                        crf_md.saveAsXML(export_metadata, 'TEMPLATE')
##                        prettyXML(export_metadata); del export_metadata
##
##                        del crf_md, crf,
##
##            del datasetcode, tablename, pointfeaturetype, featureclassname
##            del region, season, datecode, distributionprojectcode
##            del featureservicename, featureservicetitle, mosaicname, mosaictitle
##            del imageservicename, imageservicetitle, dataset_product_code
##
##        del md
##        del datasets
##
##        aprx.save()
##        del aprx

        compactGDB(ProjectGDB)

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
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
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def init_processes(arcgismetadatadirectory, basedirectory, csvdirectory,
                   datasetshapefiledirectory, exportmetadatadirectory,
                   filterdatasets, imagedirectory, inportmetadatadirectory,
                   layerdirectory, logdirectory, logfilefolder, mosaicdirectory,
                   publishdirectory, scratchfolder, softwareenvironmentlevel,
                   fielddefinitions, tabledefinitions, selectedspecies,
                   filterspecies, timeZones):

    global ARCGIS_METADATA_DIRECTORY
    global BASE_DIRECTORY
    global CSV_DIRECTORY
    global DATASET_SHAPEFILE_DIRECTORY
    global EXPORT_METADATA_DIRECTORY
    global FilterDatasets
    global IMAGE_DIRECTORY
    global INPORT_METADATA_DIRECTORY
    global LAYER_DIRECTORY
    global LOG_DIRECTORY
    global log_file_folder
    global MOSAIC_DIRECTORY
    global PUBLISH_DIRECTORY
    global ScratchFolder
    global SoftwareEnvironmentLevel
    global field_definitions
    global table_definitions
    global selected_species
    global FilterSpecies
    global timezones

    ARCGIS_METADATA_DIRECTORY   = arcgismetadatadirectory
    BASE_DIRECTORY              = basedirectory
    CSV_DIRECTORY               = csvdirectory
    DATASET_SHAPEFILE_DIRECTORY = datasetshapefiledirectory
    EXPORT_METADATA_DIRECTORY   = exportmetadatadirectory
    FilterDatasets              = filterdatasets
    IMAGE_DIRECTORY             = imagedirectory
    INPORT_METADATA_DIRECTORY   = inportmetadatadirectory
    LAYER_DIRECTORY             = layerdirectory
    LOG_DIRECTORY               = logdirectory
    log_file_folder             = logfilefolder
    MOSAIC_DIRECTORY            = mosaicdirectory
    PUBLISH_DIRECTORY           = publishdirectory
    ScratchFolder               = scratchfolder
    SoftwareEnvironmentLevel    = softwareenvironmentlevel
    field_definitions           = fielddefinitions
    table_definitions           = tabledefinitions
    selected_species            = selectedspecies
    FilterSpecies               = filterspecies
    timezones                   = timeZones

    del arcgismetadatadirectory, basedirectory, csvdirectory
    del datasetshapefiledirectory
    del exportmetadatadirectory, filterdatasets, imagedirectory
    del inportmetadatadirectory, layerdirectory, logdirectory
    del mosaicdirectory, publishdirectory, scratchfolder
    del softwareenvironmentlevel, fielddefinitions, tabledefinitions
    del selectedspecies, filterspecies, timeZones

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg


def listMapsInProjectGIS():
    try:
        function = function_name()

        base_name = os.path.basename(ProjectGIS)
        msg = f"\n###--->>> GIS Project: {base_name} <<<---###"
        print(msg); del msg, base_name

        aprx = arcpy.mp.ArcGISProject(ProjectGIS)
        maps = aprx.listMaps()
        if maps:
            for m in maps:
                print(f"Map: {m.name}")
                for lyr in m.listLayers():
                    print(f" Layer: {lyr.name}")
                    del lyr
                del m
        del maps
        lyts = aprx.listLayouts()
        if lyts:
            print("Layouts:")
            for lyt in lyts:
                print(f"  {lyt.name} ({lyt.pageHeight} x {lyt.pageWidth} {lyt.pageUnits})")
                del lyt
        del aprx, lyts

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            print(msg); del msg
        del localKeys, function, log_file

def logFile(log_file, msg):
    try:
        arcpy.AddMessage(msg)
        #print(log_file)
        my_log = open(log_file, "a+")
        my_log.write(msg + '\n')
        my_log.close
        del my_log

    # This code is executed only if an exception was raised in the try block.
    # Code executed in this block is just like normal code: if there is an
    # exception, it will not be automatically caught (and probably stop the
    # program).
##    except arcpy.ExecuteError:
##        import sys
##        # Geoprocessor threw an error
##        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
##        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
##        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
##        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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

        LogInAGOL = True
        if LogInAGOL:
            # For example: 'http://www.arcgis.com/'
            arcpy.SignInToPortal("https://noaa.maps.arcgis.com/")

            print(f"Signed into Portal: {arcpy.GetActivePortalURL()}")
        del LogInAGOL

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
        CSV_DIRECTORY = os.path.join(BASE_DIRECTORY, "CSV Data Folder")
        # If the Fish Data is missing, create the folder
        if not os.path.exists( CSV_DIRECTORY ) and not os.path.isdir( CSV_DIRECTORY ):
            os.makedirs( CSV_DIRECTORY )
        else:
            if not listFolder(CSV_DIRECTORY):
                print(f"###--->>> {os.path.basename(CSV_DIRECTORY)} is empty")

        # The Map Folder contains source data needed for this script. The source
        # data was provided by Ocean Adapt in the original download file.
        # Updates shape files replace the oroginal data as needed.
        global DATASET_SHAPEFILE_DIRECTORY
        DATASET_SHAPEFILE_DIRECTORY = os.path.join(BASE_DIRECTORY, "Dataset Shapefile Folder")
        # If the Map_Shapefiles is missing, create the folder
        if not os.path.exists( DATASET_SHAPEFILE_DIRECTORY ) and not os.path.isdir( DATASET_SHAPEFILE_DIRECTORY ):
            os.makedirs( DATASET_SHAPEFILE_DIRECTORY )
        else:
            if not listFolder( DATASET_SHAPEFILE_DIRECTORY ):
                print(f"###--->>> {os.path.basename(DATASET_SHAPEFILE_DIRECTORY)} is empty")

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
                print(f"###--->>> {os.path.basename(ARCGIS_METADATA_DIRECTORY)} is empty")

        # The INPORT_METADATA_DIRECTORY Folder is the output location for InPort
        # metadata
        global INPORT_METADATA_DIRECTORY
        INPORT_METADATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "InPort Metadata")
        # If INPORT_METADATA_DIRECTORY is missing, create the folder
        if not os.path.exists( INPORT_METADATA_DIRECTORY ) and not os.path.isdir( INPORT_METADATA_DIRECTORY ):
            os.makedirs( INPORT_METADATA_DIRECTORY )

        # The LAYER_DIRECTORY Folder is the output location for InPort
        # metadata
        global LAYER_DIRECTORY
        LAYER_DIRECTORY = os.path.join(BASE_DIRECTORY, "Layers Folder")
        # If LAYER_DIRECTORY is missing, create the folder
        if not os.path.exists( LAYER_DIRECTORY ) and not os.path.isdir( LAYER_DIRECTORY ):
            os.makedirs( LAYER_DIRECTORY )

        # The PUBLISH_DIRECTORY Folder is the output location for InPort
        # metadata
        global PUBLISH_DIRECTORY
        PUBLISH_DIRECTORY = os.path.join(BASE_DIRECTORY, "Publish Folder")
        # If PUBLISH_DIRECTORY is missing, create the folder
        if not os.path.exists( PUBLISH_DIRECTORY ) and not os.path.isdir( PUBLISH_DIRECTORY ):
            os.makedirs( PUBLISH_DIRECTORY )

        # Project Name
        global ProjectName
        #ProjectName = "DisMAP"
        ProjectName = f"DisMAP {Version}"

        # The name of the ArcGIS Pro Project
        global ProjectGIS
        ProjectGIS = os.path.join(BASE_DIRECTORY, f"{ProjectName} {SoftwareEnvironmentLevel}.aprx")

        # The name of the ArcGIS Pro Project Toolbox
        global ProjectToolBox
        ProjectToolBox = os.path.join(BASE_DIRECTORY, f"{ProjectName} {SoftwareEnvironmentLevel}.tbx")
        #DefaultGDB = os.path.join(BASE_DIRECTORY, "Default.gdb")

        # The ProjectGDB is the output location for data
        global ProjectGDB
        #ProjectGDB = os.path.join(BASE_DIRECTORY, "{0}.gdb".format(ProjectName + " " + SoftwareEnvironmentLevel))
        ProjectGDB = os.path.join(BASE_DIRECTORY, f"{ProjectName} {SoftwareEnvironmentLevel}.gdb")
        # If the ProjectGDB is missing, create the folder
        if not os.path.exists(ProjectGDB):
            arcpy.management.CreateFileGDB(BASE_DIRECTORY, ProjectName + " " + SoftwareEnvironmentLevel)

        # Template ArcGIS Pro Project
        template_project = os.path.join(os.path.dirname(BASE_DIRECTORY), "DisMAP Project Template", "DisMAP Project Template.aprx")
        aprx = arcpy.mp.ArcGISProject(template_project); del template_project

        # print( aprx.defaultGeodatabase )
        # print( aprx.defaultToolbox )
        # print( aprx.homeFolder )

        if not os.path.exists( ProjectGIS ):
            aprx.defaultGeodatabase = ProjectGDB
            aprx.homeFolder = BASE_DIRECTORY
            aprx.updateFolderConnections([{'alias': '', 'connectionString': f'{BASE_DIRECTORY}', 'isHomeFolder': True}], True)
            aprx.updateConnectionProperties(None, ProjectGDB, True)
            #aprx.defaultToolbox = ProjectToolBox
            aprx.saveACopy(ProjectGIS)
            aprx = arcpy.mp.ArcGISProject(ProjectGIS)

            #Create a copy of an existing map
            #existingMap = aprx.listMaps("Map")[0]
            #aprx.copyItem(existingMap, new_name="DisMAP Regions")
            #del existingMap
            aprx.save()

        del aprx

        # The BathymetryGDB is the output location for data
        global BathymetryGDB
        BathymetryGDB = os.path.join(BASE_DIRECTORY, "Bathymetry.gdb")
        # If the BathymetryGDB is missing, create the folder
        #if not os.path.exists(BathymetryGDB):
        #    print(os.path.exists(BathymetryGDB))
        #    arcpy.management.CreateFileGDB(BASE_DIRECTORY, "Bathymetry")

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

        global field_definitions
        field_definitions = {
                                "CSVFile"                     : ["CSVFile",                    "TEXT",   "CSV File",                                     20, "", ""],
                                "Category"                    : ["Category",                   "SHORT",  "Category",                                   None, "", ""],
                                "CellSize"                    : ["CellSize",                   "SHORT",  "Cell Size",                                  None, "", ""],
                                "CenterOfGravityDepth"        : ["CenterOfGravityDepth",       "DOUBLE", "Center of Gravity Depth",                    None, "", ""],
                                "CenterOfGravityDepthSE"      : ["CenterOfGravityDepthSE",     "DOUBLE", "Center of Gravity Depth Standard Error",     None, "", ""],
                                "CenterOfGravityLatitude"     : ["CenterOfGravityLatitude",    "DOUBLE", "Center of Gravity Latitude",                 None, "", ""],
                                "CenterOfGravityLatitudeSE"   : ["CenterOfGravityLatitudeSE",  "DOUBLE", "Center of Gravity Latitude Standard Error",  None, "", ""],
                                "CenterOfGravityLongitude"    : ["CenterOfGravityLongitude",   "DOUBLE", "Center of Gravity Longitude",                None, "", ""],
                                "CenterOfGravityLongitudeSE"  : ["CenterOfGravityLongitudeSE", "DOUBLE", "Center of Gravity Longitude Standard Error", None, "", ""],
                                #"CenterX"                     : ["CenterX",                    "DOUBLE", "CenterX",                                    None, "", ""],
                                #"CenterY"                     : ["CenterY",                    "DOUBLE", "CenterY",                                    None, "", ""],
                                "CommonName"                  : ["CommonName",                 "TEXT",   "Common Name",                                  40, "", ""],
                                "CommonNameSpecies"           : ["CommonNameSpecies",          "TEXT",   "Common Name (Species)",                        90, "", ""],
                                "CoreSpecies"                 : ["CoreSpecies",                "TEXT",   "Core Species",                                  5, "", ""],
                                #"Count"                       : ["Count",                      "DOUBLE", "Count",                                      None, "", ""],
                                "DMSLat"                      : ["DMSLat",                     "TEXT",   "DMS Latitude",                                260, "", ""],
                                "DMSLong"                     : ["DMSLong",                    "TEXT",   "DMS Longitude",                               260, "", ""],
                                "DatasetCode"                 : ["DatasetCode",                "TEXT",   "Dataset Code",                                 20, "", ""],
                                "DateCode"                    : ["DateCode",                   "TEXT",   "Date Code",                                    10, "", ""],
                                "Depth"                       : ["Depth",                      "DOUBLE", "Depth",                                      None, "", ""],
                                "Dimensions"                  : ["Dimensions",                 "TEXT",   "Dimensions",                                   10, "", ""],
                                "DistributionProjectCode"     : ["DistributionProjectCode",    "TEXT",   "Distribution Project Code",                    10, "", ""],
                                "DistributionProjectName"     : ["DistributionProjectName",    "TEXT",   "Distribution Project Name",                    60, "", ""],
                                "Easting"                     : ["Easting",                    "DOUBLE", "Easting",                                    None, "", ""],
                                "FeatureClassName"            : ["FeatureClassName",           "TEXT",   "Feature Class Name",                           40, "", ""],
                                "FeatureServiceName"          : ["FeatureServiceName",         "TEXT",   "Feature Service Name",                         40, "", ""],
                                "FeatureServiceTitle"         : ["FeatureServiceTitle",        "TEXT",   "Feature Service Title",                        60, "", ""],
                                "FilterRegion"                : ["FilterRegion",               "TEXT",   "Filter Region",                                25, "", ""],
                                "FilterSubRegion"             : ["FilterSubRegion",            "TEXT",   "Filter Sub-Region",                            40, "", ""],
                                "GeographicArea"              : ["GeographicArea",             "TEXT",   "Geographic Area",                              20, "", ""],
                                "GroupName"                   : ["GroupName",                  "TEXT",   "GroupName",                                   100, "", ""],
                                "HighPS"                      : ["HighPS",                     "DOUBLE", "HighPS",                                     None, "", ""],
                                #"ID"                          : ["ID",                         "SHORT",  "ID",                                         None, "", ""],
                                "ImageName"                   : ["ImageName",                  "TEXT",   "Image Name",                                  100, "", ""],
                                "ImageServiceName"            : ["ImageServiceName",           "TEXT",   "Image Service Name",                           40, "", ""],
                                "ImageServiceTitle"           : ["ImageServiceTitle",          "TEXT",   "Image Service Title",                          60, "", ""],
                                #"ItemTS"                      : ["ItemTS",                     "DOUBLE", "ItemTS",                                     None, "", ""],
                                "Latitude"                    : ["Latitude",                   "DOUBLE", "Latitude",                                   None, "", ""],
                                "LayerName"                   : ["LayerName",                  "TEXT",   "Layer Name",                                   40, "", ""],
                                "LayerTitle"                  : ["LayerTitle",                 "TEXT",   "Layer Title",                                  70, "", ""],
                                "Longitude"                   : ["Longitude",                  "DOUBLE", "Longitude",                                  None, "", ""],
                                #"LowPS"                       : ["LowPS",                      "DOUBLE", "LowPS",                                      None, "", ""],
                                "ManagementBody"              : ["ManagementBody",             "TEXT",   "Management Body",                              20, "", ""],
                                "ManagementPlan"              : ["ManagementPlan",             "TEXT",   "Management Plan",                              90, "", ""],
                                "MapValue"                    : ["MapValue",                   "DOUBLE", "MapValue",                                   None, "", ""],
                                #"MaxPS"                       : ["MaxPS",                      "DOUBLE", "MaxPS",                                      None, "", ""],
                                "MaximumDepth"                : ["MaximumDepth",               "DOUBLE", "Maximum Depth",                              None, "", ""],
                                "MaximumLatitude"             : ["MaximumLatitude",            "DOUBLE", "Maximum Latitude",                           None, "", ""],
                                "MaximumLongitude"            : ["MaximumLongitude",           "DOUBLE", "Maximum Longitude",                          None, "", ""],
                                "MedianEstimate"              : ["MedianEstimate",             "DOUBLE", "Median Estimate",                            None, "", ""],
                                #"MinPS"                       : ["MinPS",                      "DOUBLE", "MinPS",                                      None, "", ""],
                                "MinimumDepth"                : ["MinimumDepth",               "DOUBLE", "Minimum Depth",                              None, "", ""],
                                "MinimumLatitude"             : ["MinimumLatitude",            "DOUBLE", "Minimum Latitude",                           None, "", ""],
                                "MinimumLongitude"            : ["MinimumLongitude",           "DOUBLE", "Minimum Longitude",                          None, "", ""],
                                "MosaicName"                  : ["MosaicName",                 "TEXT",   "Mosaic Name",                                  20, "", ""],
                                "MosaicTitle"                 : ["MosaicTitle",                "TEXT",   "Mosaic Title",                                 60, "", ""],
                                "Name"                        : ["Name",                       "TEXT",   "Name",                                        200, "", ""],
                                "Northing"                    : ["Northing",                   "DOUBLE", "Northing",                                   None, "", ""],
                                "OffsetDepth"                 : ["OffsetDepth",                "DOUBLE", "Offset Depth",                               None, "", ""],
                                "OffsetLatitude"              : ["OffsetLatitude",             "DOUBLE", "Offset Latitude",                            None, "", ""],
                                "OffsetLongitude"             : ["OffsetLongitude",            "DOUBLE", "Offset Longitude",                           None, "", ""],
                                "PointFeatureType"            : ["PointFeatureType",           "TEXT",   "Point Feature Type",                           20, "", ""],
                                "ProductName"                 : ["ProductName",                "TEXT",   "Product Name",                                100, "", ""],
                                "Raster"                      : ["Raster",                     "RASTER", "Raster",                                        0, "", ""],
                                "Region"                      : ["Region",                     "TEXT",   "Region",                                       40, "", ""],
                                "SampleID"                    : ["SampleID",                   "TEXT",   "SampleID",                                     20, "", ""],
                                "Season"                      : ["Season",                     "TEXT",   "Season",                                       10, "", ""],
                                #"Shape_Area"                  : ["Shape_Area",                 "DOUBLE", "Shape_Area",                                 None, "", ""],
                                #"Shape_Length"                : ["Shape_Length",               "DOUBLE", "Shape_Length",                               None, "", ""],
                                "Species"                     : ["Species",                    "TEXT",   "Species",                                      50, "", ""],
                                "SpeciesCommonName"           : ["SpeciesCommonName",          "TEXT",   "Species (Common Name)",                        90, "", ""],
                                "Status"                      : ["Status",                     "TEXT",   "Status",                                       10, "", ""],
                                "StdTime"                     : ["StdTime",                    "DATE",   "StdTime",                                    None, "", ""],
                                "Stratum"                     : ["Stratum",                    "TEXT",   "Stratum",                                      20, "", ""],
                                "StratumArea"                 : ["StratumArea",                "DOUBLE", "Stratum Area",                               None, "", ""],
                                "SummaryProduct"              : ["SummaryProduct",             "TEXT",   "Summary Product",                              10, "", ""],
                                "TableName"                   : ["TableName",                  "TEXT",   "Table Name",                                   20, "", ""],
                                "Tag"                         : ["Tag",                        "TEXT",   "Tag",                                         100, "", ""],
                                "TaxonomicGroup"              : ["TaxonomicGroup",             "TEXT",   "Taxonomic Group",                              80, "", ""],
                                "Thumbnail"                   : ["Thumbnail",                  "BLOB",   "Thumbnail",                                     0, "", ""],
                                "TransformUnit"               : ["TransformUnit",              "TEXT",   "Transform Unit",                               20, "", ""],
                                "TypeID"                      : ["TypeID",                     "SHORT",  "Raster Type ID",                             None, "", ""],
                                #"Uri"                         : ["Uri",                        "BLOB",   "Uri",                                           0, "", ""],
                                #"UriHash"                     : ["UriHash",                    "TEXT",   "UriHash",                                      50, "", ""],
                                "Value"                       : ["Value",                      "TEXT",   "Value",                                        50, "", ""],
                                "Variable"                    : ["Variable",                   "TEXT",   "Variable",                                     50, "", ""],
                                "WTCPUE"                      : ["WTCPUE",                     "DOUBLE", "WTCPUE",                                     None, "", ""],
                                "Year"                        : ["Year",                       "SHORT",  "Year",                                       None, "", ""],
                                #"ZOrder"                      : ["ZOrder",                     "SHORT",  "ZOrder",                                     None, "", ""],
                          }

        global table_definitions
        table_definitions = {"Datasets" : ['DatasetCode', 'CSVFile', 'TransformUnit', 'TableName',
                                           'GeographicArea', 'CellSize', 'PointFeatureType',
                                           'FeatureClassName', 'Region', 'Season', 'DateCode',
                                           'Status', 'DistributionProjectCode', 'DistributionProjectName',
                                           'SummaryProduct', 'FilterRegion', 'FilterSubRegion',
                                           'FeatureServiceName', 'FeatureServiceTitle', 'MosaicName',
                                           'MosaicTitle', 'ImageServiceName', 'ImageServiceTitle',],
                            "DisMAP_Regions" : ['DatasetCode', 'Region', 'Season', 'DistributionProjectCode'],
                            "GLMME_Data" : ['DatasetCode', 'Region', 'SummaryProduct', 'Year', 'StdTime',
                                            'Species', 'WTCPUE', 'MapValue', 'TransformUnit', 'CommonName',
                                            'SpeciesCommonName', 'CommonNameSpecies', 'Easting',
                                            'Northing', 'Latitude', 'Longitude', 'MedianEstimate',
                                            'Depth'],
                            "IDW_Data" : ['DatasetCode', 'Region', 'Season',
                                          'SummaryProduct', 'SampleID', 'Year', 'StdTime',
                                          'Species', 'WTCPUE', 'MapValue', 'TransformUnit',
                                          'CommonName', 'SpeciesCommonName', 'CommonNameSpecies',
                                          'CoreSpecies', 'Stratum', 'StratumArea', 'Latitude',
                                          'Longitude', 'Depth'],
                            "Indicators" : ['DatasetCode', 'Region', 'Season',
                                            'DateCode', 'Species', 'CommonName', 'CoreSpecies',
                                            'Year', 'DistributionProjectName', 'DistributionProjectCode',
                                            'SummaryProduct', 'CenterOfGravityLatitude', 'MinimumLatitude',
                                            'MaximumLatitude', 'OffsetLatitude', 'CenterOfGravityLatitudeSE',
                                            'CenterOfGravityLongitude', 'MinimumLongitude', 'MaximumLongitude',
                                            'OffsetLongitude', 'CenterOfGravityLongitudeSE',
                                            'CenterOfGravityDepth', 'MinimumDepth', 'MaximumDepth',
                                            'OffsetDepth', 'CenterOfGravityDepthSE'],
                            "MasterSpeciesInformation" : ['Species', 'CommonName', 'SpeciesCommonName',
                                                          'CommonNameSpecies', 'TaxonomicGroup'],
                            "LayerSpeciesYearImageName" : ['DatasetCode', 'Region',
                                                           'Season', 'SummaryProduct', 'FilterRegion',
                                                           'FilterSubRegion', 'Species', 'CommonName',
                                                           'SpeciesCommonName', 'CommonNameSpecies',
                                                           'TaxonomicGroup', 'ManagementBody',
                                                           'ManagementPlan', 'CoreSpecies', 'Year',
                                                           'StdTime', 'Variable', 'Value', 'Dimensions',
                                                           'ImageName'],
                            "Species_Filter" : ['Species', 'CommonName', 'TaxonomicGroup', 'FilterRegion',
                                                'FilterSubRegion', 'ManagementBody', 'ManagementPlan'],
                            }

# #        for table in table_definitions:
# #            #print(f'"{table}" : {table_definitions[table]}')
# #            print(f'{table}')
# #            fields = table_definitions[table]
# #            #print(f'"{table}" : {fields},')
# #            #print(fields)
# #            for field in fields:
# #                #print(f"\t{field} : {field_definitions[field]}")
# #                field_atr = field_definitions[field]
# #                if field not in field_atr:
# #                    field_atr.insert(0, field)
# #                    print(f"\t{field_atr}")
# #                    del field_atr

        # #    Timezones
        # #    US/Alaska
        # #    US/Aleutian
        # #    US/Arizona
        # #    US/Central
        # #    US/East-Indiana
        # #    US/Eastern
        # #    US/Hawaii
        # #    US/Indiana-Starke
        # #    US/Michigan
        # #    US/Mountain
        # #    US/Pacific
        # #    US/Samoa

        global timezones
        timezones = {"AI"       : "US/Aleutian",
                     "EBS"      : "US/Alaska",
                     "NBS"      : "US/Alaska",
                     "GOA"      : "US/Alaska",
                     "ENBS"     : "US/Alaska",
                     "GMEX"     : "US/Central",
                     "HI"       : "US/Hawaii",
                     "NEUS_FAL" : "US/Eastern",
                     "NEUS_SPR" : "US/Eastern",
                     "SEUS_FAL" : "US/Eastern",
                     "SEUS_SPR" : "US/Eastern",
                     "SEUS_SUM" : "US/Eastern",
                     "WC"       : "US/Pacific",
                     "WC_ANN"   : "US/Pacific",
                     "WC_TRI"   : "US/Pacific",
                    }

##        timezones = {"Aleutian Islands"                : "US/Aleutian",
##                     "Eastern Bering Sea"              : "US/Alaska",
##                     "Northern Bering Sea"             : "US/Alaska",
##                     "Gulf of Alaska"                  : "US/Alaska",
##                     "Eastern and Northern Bering Sea" : "US/Alaska",
##                     "Gulf of Mexico"                  : "US/Central",
##                     "Hawai'i Islands"                 : "US/Hawaii",
##                     "Hawaii Islands"                  : "US/Hawaii",
##                     "Northeast US"                    : "US/Eastern",
##                     "Southeast US"                    : "US/Eastern",
##                     "West Coast"                      : "US/Pacific",
##                    }

        # Geographic Regions Dictionary
        global geographic_regions
        geographic_regions = {
                              'AI'        : 'Aleutian Islands',
                              'EBS'       : 'Eastern Bering Sea',
                              'GOA'       : 'Gulf of Alaska',
                              'GMEX_IDW'      : 'Gulf of Mexico',
                              #'HI'        : 'Hawaii Islands',
                              'HI'        : "Hawai'i Islands",
                              'NEUS_FAL_IDW'    : 'Northeast US',
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

# #        Atheresthes stomias and A. evermanni    Aleutian Islands
# #        Atheresthes stomias and A. evermanni    Eastern Bering Sea
# #        Bathyraja spp.    Aleutian Islands
# #        Bathyraja spp.    Eastern Bering Sea
# #        Bathyraja spp.    Northern Bering Sea
# #        Bathyraja spp.    Gulf of Alaska
# #        Bathyraja spp.    West Coast
# #        Eucinostomus spp.    Southeast
# #        Hippoglossoides elassodon and H. robustus    Eastern Bering Sea
# #        Hippoglossoides elassodon and H. robustus    Northern Bering Sea
# #        Lepidopsetta sp.    Aleutian Islands
# #        Lepidopsetta sp.    Eastern Bering Sea
# #        Lepidopsetta sp.    Northern Bering Sea
# #        Lepidopsetta sp.    Gulf of Alaska
# #        Lepidopsetta sp.    West Coast
# #        Loligo spp.    Southeast
# #        Sebastes melanostictus and S. aleutianus    West Coast
# #        Sebastes variabilis and S. ciliatus    Aleutian Islands
# #        Sebastes variabilis and S. ciliatus    Gulf of Alaska

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
                                    'Acesta sphoni'                   : 'Limid clam sp.',
                                    'Anthopleura xanthogrammica'      : 'Giant green anemone',
                                    'Bathymaster signatus'            : 'Searcher',
                                    'Bathyraja spp.'                  : 'Skate complex',
                                    'Citharichthys sordidus'          : 'Pacific sanddab',
                                    'Doryteuthis (Loligo) opalescens' : 'California market squid',
                                    'Gadus chalcogrammus'             : 'Walleye Pollock', # in EBS,
                                    'Gadus macrocephalus'             : 'Pacific Cod',
                                    'Limanda aspera'                  : 'yellowfin sole', # in EBS,
                                    # 'WC_GLMME'
                                    'Anoplopoma fimbria'              : 'Sablefish',
                                    'Microstomus pacificus'           : 'Dover sole', # also in EBS
                                    # 'GMEX_IDW', 'Gulf of Mexico'
                                    'Lutjanus campechanus'            : 'red snapper',
                                    'Ancylopsetta dilecta'            : 'three-eye flounder',
                                    # 'HI', 'Hawaii'
                                    'Etelis coruscans'                : 'Onaga',
                                    'Hyporthodus quernus'             : 'HapuÊ»upuÊ»u',
                                    # NEUS_FAL_IDW, 'Northeast US Fall'
                                    # 'NEUS_S', 'Northeast US Spring'
                                    # 'SEUS_SPR', 'Southeast US Spring'
                                    # 'SEUS_SUM', 'Southeast US Summer'
                                    # 'SEUS_FALL', 'Southeast US Fall'
                                    'Centropristis striata'            : 'black sea bass',
                                    'Geryon (Chaceon) quinquedens'     : 'Red Deep Sea Crab',
                                    'Loligo spp.'                      : 'Loligo squid',
                                    'Rachycentron canadum'             : 'Cobia',
                                   }
            if SoftwareEnvironmentLevel == "Test":
                # TODO: Consider using sets instead
                selected_species = {
                                    # 'AI', 'Aleutian Islands'
                                    # 'EBS', 'Eastern Bering Sea'
                                    # 'GOA', 'Gulf of Alaska'
                                    # 'WC_ANN', 'West Coast Annual (2003-present)'
                                    # 'WC_TRI', 'West Coast Triennial (1977-2004)',
                                    'Acesta sphoni'                       : 'Limid clam sp.',
                                    'Anthopleura xanthogrammica'          : 'Giant green anemone',
                                    'Bathyraja spp.'                      : 'Skate complex',
                                    'Calinaticina oldroydii'              : "Oldroyd's Fragile Moon Snail",
                                    'Citharichthys sordidus'              : 'Pacific sanddab',
                                    'Doryteuthis (Loligo) opalescens'     : 'California market squid',
                                    'Gadus chalcogrammus'                 : 'Walleye Pollock',
                                    'Gadus macrocephalus'                 : 'Pacific Cod',
                                    'Hippoglossus stenolepis'             : 'Pacific Halibut',
                                    'Limanda aspera'                      : 'yellowfin sole',
                                    'Sebastes variabilis and S. ciliatus' : 'Dusky and dark rockfish',
                                    # 'WC_GLMME'
                                    'Anoplopoma fimbria'                  : 'Sablefish',
                                    'Microstomus pacificus'               : 'Dover sole',
                                    'Sebastolobus alascanus'              : 'Shortspine thornyhead',
                                    'Sebastolobus altivelis'              : 'Longspine thornyhead',
                                    # 'GMEX_IDW', 'Gulf of Mexico'
                                    'Ancylopsetta dilecta'                : 'three-eye flounder',
                                    'Ancylopsetta ommata'                 : 'ocellated flounder',
                                    'Chicoreus florifer-dilectus'         : 'Flowery lace murex',
                                    'Lutjanus campechanus'                : 'red snapper',
                                    'Scomberomorus maculatus'             : 'Spanish Mackerel',
                                    # 'HI', 'Hawaii'
                                    'Aphareus rutilans'                   : 'Lehi',
                                    'Etelis carbunculus'                  : 'Ehu',
                                    'Etelis coruscans'                    : 'Onaga',
                                    'Hyporthodus quernus'                 : 'HapuÊ»upuÊ»u',
                                    'Pristipomoides filamentosus'         : 'Opakapaka',
                                    'Pristipomoides sieboldii'            : 'Kalekale',
                                    'Pristipomoides zonatus'              : 'Gindai',
                                    # NEUS_FAL_IDW, 'Northeast US Fall'
                                    # 'NEUS_S', 'Northeast US Spring'
                                    'Centropristis striata'               : 'black sea bass',
                                    'Geryon (Chaceon) quinquedens'        : 'Red Deep Sea Crab',
                                    'Homarus americanus'                  : 'American Lobster',
                                    # 'SEUS_SPR', 'Southeast US Spring'
                                    # 'SEUS_SUM', 'Southeast US Summer'
                                    # 'SEUS_FALL', 'Southeast US Fall'
                                    'Brevoortia tyrannus'                 : 'Atlantic menhaden',
                                    'Loligo spp.'                         : 'Loligo squid',
                                    'Micropogonias undulatus'             : 'Atlantic croaker',
                                    'Rachycentron canadum'                : 'Cobia',
                                   }
        else:
            FilterSpecies = False
            selected_species = {}

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
        print(msg); del msg #logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        print(msg); del msg #logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function#, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def metadataUpdate():
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        from arcpy import metadata as md

        ProcessDisMAPRegionsAndTables = False
        if ProcessDisMAPRegionsAndTables:
            msg = f"> Processing DisMAP_Region, Indicators, Datasets, Species_Filter Layers."
            logFile(log_file, msg); del msg

            datasets = generateDatasets()

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                layer_list = ["DisMAP_Regions", "Indicators", "Datasets", "Species_Filter",]
                #layer_list = ["DisMAP_Regions"]
                datasets = [[r for r in group] for group in datasets if group[0] in layer_list]
                del layer_list

            if FilterDatasets:
                datasets = [[r for r in group] for group in datasets if f"{group[4]}_{group[7]}" in selected_datasets]

            if not datasets:
                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            for i in range(len(datasets)):
                datasetcode         = datasets[i][0]
                featureclassname    = datasets[i][7]
                region              = datasets[i][8]
                season              = datasets[i][9]
                datecode            = datasets[i][10]
                featureservicetitle = datasets[i][18]
                #layername        = datasets[i][14]
                #layertitle       = datasets[i][15]
                del i


##                datasetcode             = row[0]
##                csvfile                 = row[1]
##                transformunit           = row[2]
##                tablename               = row[3]
##                geographicarea          = row[4]
##                cellsize                = row[5]
##                pointfeaturetype        = row[6]
##                featureclassname        = row[7]
##                region                  = row[8]
##                season                  = row[9]
##                datecode                = row[10]
##                status                  = row[11]
##                distributionprojectcode = row[12]
##                distributionprojectname = row[13]
##                summaryproduct          = row[14]
##                filterregion            = row[15]
##                filtersubregion         = row[16]
##                featureservicename      = row[17]
##                featureservicetitle     = row[18]
##                mosaicname              = row[19]
##                mosaictitle             = row[20]
##                imageservicename        = row[21]
##                imageservicetitle       = row[22]

                msg = f"  > Processing {layertitle} Layer."
                logFile(log_file, msg); del msg

                if layername == "DisMAP_Regions":
                    with arcpy.EnvManager(scratchWorkspace=ScratchGDB, workspace=ProjectGDB):

                        #template_metadata = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{layertitle}.xml")

                        layertitle_md = md.Metadata(layername)

                        msg = "\t\t Title: {0}".format(layertitle_md.title)
                        print(msg); del msg

                        msg = "\t\t Tags: {0}".format(layertitle_md.tags)
                        print(msg); del msg

                        msg = "\t\t Summary: {0}".format(layertitle_md.summary)
                        print(msg); del msg

                        msg = "\t\t Description: {0}".format(layertitle_md.description)
                        print(msg); del msg

                        msg = "\t\t Credits: {0}".format(layertitle_md.credits)
                        print(msg); del msg

                        #export_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{layertitle}.xml")

                        #layertitle_md.saveAsXML(export_metadata, 'REMOVE_ALL_SENSITIVE_INFO')
                        #del layertitle_md

                        #prettyXML(export_metadata)

                        #del template_metadata, export_metadata
                        del datecode, region, season, regions

                elif layername in ["Indicators", "Datasets", "Species_Filter",]:
                    with arcpy.EnvManager(scratchWorkspace=ScratchGDB, workspace=ProjectGDB):

                        #template_metadata = os.path.join(ARCGIS_METADATA_DIRECTORY, f"{layertitle}.xml")

                        #prettyXML(template_metadata)

                        msg = "\t\t Title: {0}".format(layertitle_md.title)
                        print(msg); del msg

                        msg = "\t\t Tags: {0}".format(layertitle_md.tags)
                        print(msg); del msg

                        msg = "\t\t Summary: {0}".format(layertitle_md.summary)
                        print(msg); del msg

                        msg = "\t\t Description: {0}".format(layertitle_md.description)
                        print(msg); del msg

                        msg = "\t\t Credits: {0}".format(layertitle_md.credits)
                        print(msg); del msg

                        #del template_metadata, export_metadata
                        del datecode, region, season

                del datasetcode, layername, layertitle
            del datasets
        del ProcessDisMAPRegionsAndTables

        ProcessingSampleLocationLayers = False
        if ProcessingSampleLocationLayers:
            msg = f"> Processing Sample Location Layers."
            logFile(log_file, msg); del msg

            datasets = generateDatasets()

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                wc = "_Sample_Locations"
                fcs = arcpy.ListFeatureClasses(f"*{wc}")
                datasets = [[r for r in group] for group in datasets if group[7] in fcs]
                del wc, fcs

            if FilterDatasets:
                datasets = [[r for r in group] for group in datasets if f"{group[0]}_{group[12]}" in selected_datasets]

            if not datasets:
                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            for i in range(len(datasets)):
                datasetcode         = datasets[i][0]
                featureclassname    = datasets[i][7]
                region              = datasets[i][8]
                season              = datasets[i][9]
                datecode            = datasets[i][10]
                featureservicetitle = datasets[i][18]
                #layername        = datasets[i][14]
                #layertitle       = datasets[i][15]
                del i

##                datasetcode             = row[0]
##                csvfile                 = row[1]
##                transformunit           = row[2]
##                tablename               = row[3]
##                geographicarea          = row[4]
##                cellsize                = row[5]
##                pointfeaturetype        = row[6]
##                featureclassname        = row[7]
##                region                  = row[8]
##                season                  = row[9]
##                datecode                = row[10]
##                status                  = row[11]
##                distributionprojectcode = row[12]
##                distributionprojectname = row[13]
##                summaryproduct          = row[14]
##                filterregion            = row[15]
##                filtersubregion         = row[16]
##                featureservicename      = row[17]
##                featureservicetitle     = row[18]
##                mosaicname              = row[19]
##                mosaictitle             = row[20]
##                imageservicename        = row[21]
##                imageservicetitle       = row[22]

                msg = f"  > Processing {layertitle} Layer."
                logFile(log_file, msg); del msg

                with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                    #template_metadata = os.path.join(ARCGIS_METADATA_DIRECTORY, f"Survey catch-per-unit-effort {datecode}.xml")

                    layertitle_md = md.Metadata(layername)

                    msg = "\t\t Title: {0}".format(layertitle_md.title)
                    print(msg); del msg

                    msg = "\t\t Tags: {0}".format(layertitle_md.tags)
                    print(msg); del msg

                    msg = "\t\t Summary: {0}".format(layertitle_md.summary)
                    print(msg); del msg

                    msg = "\t\t Description: {0}".format(layertitle_md.description)
                    print(msg); del msg

                    msg = "\t\t Credits: {0}".format(layertitle_md.credits)
                    print(msg); del msg

                    #prettyXML(export_metadata)

                    #del template_metadata, export_metadata
                del layername, layertitle, datecode, region, season,  datasetcode
            del datasets
        del ProcessingSampleLocationLayers

        ProcessingMosaicLayers = False
        if ProcessingMosaicLayers:
            msg = f" > Processing Mosaic Layers."
            logFile(log_file, msg); del msg

            datasets = generateDatasets()

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                wc = ""
                mss = arcpy.ListDatasets(f"*{wc}")
                datasets = [[r for r in group] for group in datasets if group[19] in mss]
                del wc, mss

            if FilterDatasets:
                datasets = [[r for r in group] for group in datasets if f"{group[0]}_{group[12]}" in selected_datasets]

            if not datasets:
                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            for i in range(len(datasets)):
                region      = datasets[i][8]
                season      = datasets[i][9]
                datecode    = datasets[i][10]
                mosaicname  = datasets[i][19]
                mosaictitle = datasets[i][20]
                del i

##                datasetcode         = datasets[i][0]
##                featureclassname    = datasets[i][7]
##                region              = datasets[i][8]
##                season              = datasets[i][9]
##                datecode            = datasets[i][10]
##                featureservicetitle = datasets[i][18]
##                #layername        = datasets[i][14]
##                #layertitle       = datasets[i][15]
##                del i
##
##                datasetcode             = row[0]
##                csvfile                 = row[1]
##                transformunit           = row[2]
##                tablename               = row[3]
##                geographicarea          = row[4]
##                cellsize                = row[5]
##                pointfeaturetype        = row[6]
##                featureclassname        = row[7]
##                region                  = row[8]
##                season                  = row[9]
##                datecode                = row[10]
##                status                  = row[11]
##                distributionprojectcode = row[12]
##                distributionprojectname = row[13]
##                summaryproduct          = row[14]
##                filterregion            = row[15]
##                filtersubregion         = row[16]
##                featureservicename      = row[17]
##                featureservicetitle     = row[18]
##                mosaicname              = row[19]
##                mosaictitle             = row[20]
##                imageservicename        = row[21]
##                imageservicetitle       = row[22]


                msg = f"  > Processing {mosaictitle} Layer."
                logFile(log_file, msg); del msg

                with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                    #del empty_xml

                    #template_metadata = os.path.join(ARCGIS_METADATA_DIRECTORY, f"Survey catch-per-unit-effort {datecode}.xml")

                    mosaicname_md = md.Metadata(mosaicname)

                    msg = "\t\t Title: {0}".format(layertitle_md.title)
                    print(msg); del msg

                    msg = "\t\t Tags: {0}".format(layertitle_md.tags)
                    print(msg); del msg

                    msg = "\t\t Summary: {0}".format(layertitle_md.summary)
                    print(msg); del msg

                    msg = "\t\t Description: {0}".format(layertitle_md.description)
                    print(msg); del msg

                    msg = "\t\t Credits: {0}".format(layertitle_md.credits)
                    print(msg); del msg

                    del mosaicname_md

                    #prettyXML(export_metadata)

                    #del template_metadata, export_metadata
                del mosaicname, mosaictitle, datecode, region, season
            del datasets
        del ProcessingMosaicLayers

        ProcessingCRFLayers = True
        if ProcessingCRFLayers:
            msg = f" > Processing CRF Layers."
            logFile(log_file, msg); del msg

            datasets = generateDatasets()

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):
                wc = ""
                crfs = [crf[:-4] for crf in arcpy.ListFiles(f"*{wc}*")]
                datasets = [[r for r in group] for group in datasets if f"{group[0]}_{group[12]}" in crfs]
                del wc, crfs

            if FilterDatasets:
                datasets = [[r for r in group] for group in datasets if f"{group[0]}_{group[12]}" in selected_datasets]

            if not datasets:
                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            for i in range(len(datasets)):
                region      = datasets[i][8]
                season      = datasets[i][9]
                datecode    = datasets[i][10]
                mosaicname  = datasets[i][19].replace('_Mosaic', '')
                mosaictitle = f"{mosaicname}_{datecode}"
                del i

##                datasetcode         = datasets[i][0]
##                featureclassname    = datasets[i][7]
##                region              = datasets[i][8]
##                season              = datasets[i][9]
##                datecode            = datasets[i][10]
##                featureservicetitle = datasets[i][18]
##                #layername        = datasets[i][14]
##                #layertitle       = datasets[i][15]
##                del i
##
##                datasetcode             = row[0]
##                csvfile                 = row[1]
##                transformunit           = row[2]
##                tablename               = row[3]
##                geographicarea          = row[4]
##                cellsize                = row[5]
##                pointfeaturetype        = row[6]
##                featureclassname        = row[7]
##                region                  = row[8]
##                season                  = row[9]
##                datecode                = row[10]
##                status                  = row[11]
##                distributionprojectcode = row[12]
##                distributionprojectname = row[13]
##                summaryproduct          = row[14]
##                filterregion            = row[15]
##                filtersubregion         = row[16]
##                featureservicename      = row[17]
##                featureservicetitle     = row[18]
##                mosaicname              = row[19]
##                mosaictitle             = row[20]
##                imageservicename        = row[21]
##                imageservicetitle       = row[22]


                msg = f" > CRF: {mosaicname}.crf"
                print(msg); del msg

                crf_path = os.path.join(MOSAIC_DIRECTORY, f"{mosaicname}.crf")

                msg = f" > CRF path: {crf_path}"
                print(msg); del msg

                mosaicname_md = md.Metadata(crf_path)
                mosaicname_md.title = mosaictitle
                mosaicname_md.save()
                mosaicname_md.reload()

                msg = "\t\t Title: {0}".format(mosaicname_md.title)
                print(msg); del msg

                msg = "\t\t Tags: {0}".format(mosaicname_md.tags)
                print(msg); del msg

                msg = "\t\t Summary: {0}".format(mosaicname_md.summary)
                print(msg); del msg

                msg = "\t\t Description: {0}".format(mosaicname_md.description)
                print(msg); del msg

                msg = "\t\t Credits: {0}".format(mosaicname_md.credits)
                print(msg); del msg


                del mosaicname_md, crf_path

                    #prettyXML(export_metadata)

                    #del template_metadata, export_metadata
                del mosaicname, mosaictitle, region, season, datecode
            del datasets
        del ProcessingCRFLayers

        del md

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
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
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            logFile(log_file, msg); del msg

        del localKeys, function, log_file

def mpCreateDisMapRegions(dataset):
    """mp Create Region Bathymetry"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        datasetcode             = dataset[0]
        geographicarea          = dataset[4]
        cellsize                = dataset[5]
        region                  = dataset[8]
        season                  = dataset[9]
        distributionprojectcode = dataset[12]
        del dataset

        dataset_product_code = f"{datasetcode}_{distributionprojectcode}"
        #del distributionprojectcode

        RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

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

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
        #print(geographicarea_sr)

        datasetcode_sr = arcpy.SpatialReference(geographicarea_sr)
        del geographicarea_sr

        arcpy.env.outputCoordinateSystem = datasetcode_sr; del datasetcode_sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

        # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
        msg = f'> Generating {dataset_product_code} Surevy Areas'
        logFile(log_file, msg); del msg

        datasetcode_survey_area   = f"{dataset_product_code}_Survey_Area"
        datasetcode_boundary_line = f"{dataset_product_code}_Boundary_Line"
        datasetcode_raster_mask   = f"{dataset_product_code}_Raster_Mask"

        # The shapefile used to create the extent and mask for the environment variable
        datasetcode_shape_file = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.shp")
        datasetcode_shape_scratch = os.path.join(RegionScratchGDB, geographicarea)

        # Delete after last use
        del geographicarea

        msg = f'>-> Copy {dataset_product_code} Shape File to a Dataset.'
        logFile(log_file, msg); del msg

        with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
            arcpy.conversion.ExportFeatures(in_features = datasetcode_shape_file,
                                            out_features = datasetcode_shape_scratch,
                                            where_clause = "",
                                            use_field_alias_as_name = "",
                                            field_mapping = "",
                                            sort_field = "")
        # Delete after use
        del datasetcode_shape_file

        # Get a list of non-required fields

        delete_fields = [f.name for f in arcpy.ListFields(datasetcode_shape_scratch) if not f.required]

        msg = f'>-> Delete non-required fields from {dataset_product_code} Dataset.'
        logFile(log_file, msg); del msg
        arcpy.management.DeleteField(datasetcode_shape_scratch, delete_fields)

        # Delete after last use
        del delete_fields

        # DisMAP Regions
        dismap_regions = "DisMAP_Regions"

        tb_fields = [f.name for f in arcpy.ListFields(datasetcode_shape_scratch) if f.type not in ['Geometry', 'OID']]
        tb_definition_fields = table_definitions[dismap_regions]
        fields = [f for f in tb_definition_fields if f not in tb_fields]

        del dismap_regions, tb_fields

        addFields(datasetcode_shape_scratch, fields, field_definitions)
        del tb_definition_fields, fields

        msg = f">-> Calculating the 'DatasetCode' field in the {dataset_product_code} Dataset"
        logFile(log_file, msg); del msg
        # Process: Calculate Region Field
        arcpy.management.CalculateField(datasetcode_shape_scratch, "DatasetCode", f'"{datasetcode}"', "PYTHON", "")

        msg = f">-> Calculating the 'Region' field in the {dataset_product_code} Dataset"
        logFile(log_file, msg); del msg
        # Process: Calculate Region Field
        arcpy.management.CalculateField(datasetcode_shape_scratch, "Region", f'"{region}"', "PYTHON", "")

        msg = f">-> Calculating the 'Season' field in the {dataset_product_code} Dataset"
        logFile(log_file, msg); del msg
        # Process: Calculate Region Field
        arcpy.management.CalculateField(datasetcode_shape_scratch, "Season", f'"{season}"', "PYTHON", "")
        del season

        msg = f">-> Calculating the 'DistributionProjectCode' field in the {dataset_product_code} Dataset"
        logFile(log_file, msg); del msg
        # Process: Calculate Region Field
        arcpy.management.CalculateField(datasetcode_shape_scratch, "DistributionProjectCode", f'"{distributionprojectcode}"', "PYTHON", "")
        del distributionprojectcode

        msg = f">-> Adding the 'ID' field in the {dataset_product_code} Dataset"
        logFile(log_file, msg); del msg
        arcpy.management.AddField(datasetcode_shape_scratch, "ID", "LONG","","","","ID","NULLABLE","NON_REQUIRED")

        msg = f">-> Calculating the 'ID' field in the {datasetcode} Dataset"
        logFile(log_file, msg); del msg
        # Set ID field value
        arcpy.management.CalculateField(datasetcode_shape_scratch, "ID", 1, "PYTHON")

        msg = f">-> Export Features from scratch to region gdb for the {dataset_product_code} Dataset"
        logFile(log_file, msg); del msg

        with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
            arcpy.conversion.ExportFeatures(in_features = datasetcode_shape_scratch,
                                            out_features = datasetcode_survey_area,
                                            where_clause = "",
                                            use_field_alias_as_name = "",
                                            field_mapping = "",
                                            sort_field = "")
            # Delete after use
            arcpy.management.Delete(datasetcode_shape_scratch)

        del datasetcode_shape_scratch

        msg = f">-> Converting the {datasetcode} Dataset from Polygon to Polyline"
        logFile(log_file, msg); del msg
        # Process: Feature To Line
        with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
            arcpy.management.FeatureToLine(in_features = datasetcode_survey_area, out_feature_class = datasetcode_boundary_line, cluster_tolerance="", attributes="ATTRIBUTES")

            #addMetadata(datasetcode_boundary_line)

            # Delete after last use
            del datasetcode_boundary_line

        msg = f">-> Feature to Raster Conversion using {datasetcode_survey_area} to create Raster Mask {datasetcode_raster_mask}"
        logFile(log_file, msg); del msg

        with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
            # Change mask to the region shape to create the raster mask
            arcpy.env.extent   = arcpy.Describe(datasetcode_survey_area).extent
            arcpy.env.mask     = datasetcode_survey_area
            arcpy.env.cellSize = cellsize
            arcpy.conversion.FeatureToRaster(datasetcode_survey_area, "ID", datasetcode_raster_mask, cellsize)

            #addMetadata(datasetcode_raster_mask)

            del datasetcode_survey_area, datasetcode_raster_mask, RegionScratchGDB, RegionGDB, cellsize

        del datasetcode, dataset_product_code, region

        # Resets a specific environment setting to its default
        arcpy.ClearEnvironment("cellSize")
        arcpy.ClearEnvironment("extent")
        arcpy.ClearEnvironment("mask")
        arcpy.ClearEnvironment("snapRaster")

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
        return False
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
        return False
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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

        return True # everything went well so we return True

def mpCreateIndicatorsTable(dataset):

    """mp Create Indicators Table"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        import numpy as np
        import math
        np.seterr(divide='ignore', invalid='ignore')

        global log_file_folder
        global ScratchFolder
        global SoftwareEnvironmentLevel

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        datasetcode             = dataset[0]
        geographicarea          = dataset[4]
        cellsize                = dataset[5]
        region                  = dataset[8]
        season                  = dataset[9]
        datecode                = dataset[10]
        distributionprojectcode = dataset[12]
        distributionprojectname = dataset[13]
        summaryproduct          = dataset[14]

        del dataset

        dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

        RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

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

        msg = f'> Generating {dataset_product_code} Indicators Table'
        logFile(log_file, msg); del msg

        # Get the reference system defined for the region in datasets
        datasetcodepath = os.path.join(RegionGDB, f"{dataset_product_code}")
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
        psr = arcpy.SpatialReference(geographicarea_sr)
        arcpy.env.outputCoordinateSystem = psr

        del geographicarea, geographicarea_sr, psr

        arcpy.env.cellSize = cellsize; del cellsize

# #  4   DatasetCode,
# #  5   Region,
# #  6   Season
# #  7   Species
# #  8   CommonName
# #  9   CoreSpecies
# # 10   Year
# # 11   DistributionProjectName
# # 12   DistributionProjectCode
# # 13   SummaryProduct
# # 14   CenterOfGravityLatitude
# # 15   MinimumLatitude
# # 16   MaximumLatitude
# # 17   OffsetLatitude
# # 18   CenterOfGravityLatitudeSE
# # 19   CenterOfGravityLongitude
# # 20   MinimumLongitude
# # 21   MaximumLongitude
# # 21   OffsetLongitude
# # 22   CenterOfGravityLongitudeSE
# # 23   CenterOfGravityDepth
# # 24   MinimumDepth
# # 25   MaximumDepth
# # 26   OffsetDepth
# # 27   CenterOfGravityDepthSE

        # Region Raster Mask
        datasetcode_raster_mask = os.path.join(RegionGDB, f"{dataset_product_code}_Raster_Mask")

        # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
        arcpy.env.extent = arcpy.Describe(datasetcode_raster_mask).extent
        arcpy.env.mask = datasetcode_raster_mask
        arcpy.env.snapRaster = datasetcode_raster_mask
        del datasetcode_raster_mask

        # region abbreviated path
        datasetcode_folder = os.path.join(IMAGE_DIRECTORY, dataset_product_code)

        # Template Indicators Table
        #template_indicators = os.path.join(RegionGDB, f"Indicators")

        # Region Indicators
        datasetcode_indicators = os.path.join(RegionGDB, f"{dataset_product_code}_Indicators")

        # Region Bathymetry
        datasetcode_bathymetry = os.path.join(RegionGDB, f"{dataset_product_code}_Bathymetry")

        # Region Latitude
        datasetcode_latitude = os.path.join(RegionGDB, f"{dataset_product_code}_Latitude")

        # Region Longitude
        datasetcode_longitude = os.path.join(RegionGDB, f"{dataset_product_code}_Longitude")

        # Region CVS Table
        datasetcode_path = os.path.join(RegionGDB, dataset_product_code)
        #print(datasetcode_path)
        fields = [f.name for f in arcpy.ListFields(datasetcode_path) if f.type not in ['Geometry', 'OID']]

        if "CoreSpecies" not in fields:
            arcpy.management.AddField(datasetcode_path, "CoreSpecies", "TEXT", "", "", 10, "Core Species")
            arcpy.management.CalculateField(datasetcode_path, "CoreSpecies", "None")
        del fields

##        # Execute CreateTable
##        arcpy.management.CreateTable(RegionGDB, f"{datasetcode}_Indicators", template_indicators, "")
##        msg = arcpy.GetMessages()
##        msg = ">---> {0}".format(msg.replace('\n', '\n>-----> '))
##        logFile(log_file, msg); del msg
##
##        del template_indicators

        # Get a disctionary of species and common names from the
        # Dictionary of species and common names that are in the tables
        datasetcode_unique_species_common_name_dict = unique_fish_dict(datasetcode_path)
        del datasetcode_path

        #print( datasetcode_unique_species_common_name_dict )
        #print("Is the")

        # Start with empty row_values list of list
        row_values = []

        # Loop through dictionary
        for datasetcode_unique_specie in datasetcode_unique_species_common_name_dict:
            # Speices folders do not include the '.' that can be a part
            # of the name, so remove
            datasetcode_unique_specie_dir = datasetcode_unique_specie.replace('(','').replace(')','')
            # Species
            Species = datasetcode_unique_specie[:]
            #print(Species)
            # The common name is the value in the dictionary
            CommonName = datasetcode_unique_species_common_name_dict[datasetcode_unique_specie][0]
            #print(CommonName)
            CoreSpecies = datasetcode_unique_species_common_name_dict[datasetcode_unique_specie][1]
            del datasetcode_unique_specie
            #print(CoreSpecies)

            msg = f">---> Species: {Species}, Common Name: {CommonName}"
            logFile(log_file, msg); del msg

            datasetcode_unique_specie_dir = os.path.join(datasetcode_folder, datasetcode_unique_specie_dir)

            msg = f">---> Processing Biomass Rasters in {os.path.basename(datasetcode_unique_specie_dir)}"
            logFile(log_file, msg); del msg

            arcpy.env.workspace = datasetcode_unique_specie_dir; del datasetcode_unique_specie_dir

            biomassRasters = arcpy.ListRasters("*.tif")

            # ###--->>> This is to get a median biomass value for all years

            first_year = 9999
            # Process rasters
            for biomassRaster in sorted(biomassRasters):
                # Get year from raster name
                br_year = int(biomassRaster[-8:-4])

                msg = f">-----> Processing {biomassRaster} Biomass Raster"
                logFile(log_file, msg); del msg

                # Get maximumBiomass value to filter out "zero" rasters
                maximumBiomass = float(arcpy.management.GetRasterProperties(biomassRaster,"MAXIMUM").getOutput(0))

                msg = f">-------> Biomass Raster Maximum: {maximumBiomass}"
                logFile(log_file, msg); del msg

                # If maximumBiomass greater than zero, then process raster
                if maximumBiomass > 0.0:
                    msg = f">-------> Calculating indicators"
                    logFile(log_file, msg); del msg

                    # Test is for first year
                    if br_year < first_year:
                        first_year = br_year

                # ###--->>> Biomass Start

                    biomassArray = arcpy.RasterToNumPyArray(biomassRaster, nodata_to_value=np.nan)
                    biomassArray[biomassArray <= 0.0] = np.nan

                    #sumWtCpue = sum of all wtcpue values (get this from biomassRaster stats??)
                    sumBiomassArray = np.nansum(biomassArray)

                    msg = f">-------> sumBiomassArray: {sumBiomassArray}"
                    logFile(log_file, msg); del msg

                    msg = f">-------> biomassArray non-nan count: {np.count_nonzero(~np.isnan(biomassArray))}"
                    logFile(log_file, msg); del msg

                # ###--->>> Biomass End

                # ###--->>> Latitude Start

                    # Latitude
                    latitudeArray = arcpy.RasterToNumPyArray(datasetcode_latitude, nodata_to_value=np.nan)
                    #print(latitudeArray.shape)
                    latitudeArray[np.isnan(biomassArray)] = np.nan
                    #print(latitudeArray.shape)

                    #msg = f">-------> latitudeArray non-nan count: {np.count_nonzero(~np.isnan(latitudeArray)):,d}"
                    #logFile(log_file, msg); del msg

                    #msg = f">-------> Latitude Min: {np.nanmin(latitudeArray)}"
                    #logFile(log_file, msg); del msg

                    #msg = f">-------> Latitude Max: {np.nanmax(latitudeArray)}"
                    #logFile(log_file, msg); del msg

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

                    #msg = ">-------> Sum Weighted Latitude: {sumWeightedLatitudeArray}"
                    #logFile(log_file, msg); del msg

                    CenterOfGravityLatitude = sumWeightedLatitudeArray / sumBiomassArray

                    if br_year == first_year:
                        first_year_offset_latitude = CenterOfGravityLatitude

                    OffsetLatitude = CenterOfGravityLatitude - first_year_offset_latitude

                    weightedLatitudeArrayVariance = np.nanvar(weightedLatitudeArray)
                    weightedLatitudeArrayCount = np.count_nonzero(~np.isnan(weightedLatitudeArray))

                    CenterOfGravityLatitudeSE = math.sqrt(weightedLatitudeArrayVariance) / math.sqrt(weightedLatitudeArrayCount)

                    del weightedLatitudeArrayVariance, weightedLatitudeArrayCount

                    #msg = f">-------> Center of Gravity Latitude: {round(CenterOfGravityLatitude,6)}"
                    msg = f">-------> Center of Gravity Latitude: {CenterOfGravityLatitude}"
                    logFile(log_file, msg); del msg

                    msg = f">-------> Minimum Latitude (5th Percentile): {MinimumLatitude}"
                    logFile(log_file, msg); del msg

                    msg = f">-------> Maximum Latitude (95th Percentile): {MaximumLatitude}"
                    logFile(log_file, msg); del msg

                    msg = f">-------> Offset Latitude: {OffsetLatitude}"
                    logFile(log_file, msg); del msg

                    msg = f">-------> Center of Gravity Latitude Standard Error: {CenterOfGravityLatitudeSE}"
                    logFile(log_file, msg); del msg

                    del latitudeArray, weightedLatitudeArray, sumWeightedLatitudeArray

                # ###--->>> Latitude End

                # ###--->>> Longitude Start
                    #longitudeArray = arcpy.RasterToNumPyArray(masked_longitude_raster, nodata_to_value = np.nan)
                    #arcpy.management.Delete(masked_longitude_raster)
                    #del masked_longitude_raster

                    # Longitude
                    # Doesn't work for International Date Line
                    #longitudeArray = arcpy.RasterToNumPyArray(datasetcode_longitude, nodata_to_value=np.nan)
                    #longitudeArray[np.isnan(biomassArray)] = np.nan

                    # For issue of international date line
                    # Added/Modified by JFK June 15, 2022
                    longitudeArray = arcpy.RasterToNumPyArray(datasetcode_longitude, nodata_to_value=np.nan)

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

                    if br_year == first_year:
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

                    #msg = f">-------> Sum Weighted Longitude: {0}".format(sumWeightedLongitudeArray)
                    #logFile(log_file, msg); del msg

                    #msg = f">-------> Center of Gravity Longitude: {round(CenterOfGravityLongitude,6)}"
                    msg = f">-------> Center of Gravity Longitude: {CenterOfGravityLongitude}"
                    logFile(log_file, msg); del msg


                    #msg = F">-------> Center of Gravity Longitude: {np.mod(CenterOfGravityLongitude - 180.0, 360.0) -180.0}"
                    #logFile(log_file, msg); del msg

                    msg = f">-------> Minimum Longitude (5th Percentile): {MinimumLongitude}"
                    logFile(log_file, msg); del msg

                    msg = f">-------> Maximum Longitude (95th Percentile): {MaximumLongitude}"
                    logFile(log_file, msg); del msg

                    msg = f">-------> Offset Longitude: {OffsetLongitude}"
                    logFile(log_file, msg); del msg

                    msg = f">-------> Center of Gravity Longitude Standard Error: {CenterOfGravityLongitudeSE}"
                    logFile(log_file, msg); del msg

                    del longitudeArray, weightedLongitudeArray, sumWeightedLongitudeArray

                # ###--->>> Center of Gravity Depth Start
                    # ###--->>> Bathymetry (Depth)

                    # Bathymetry
                    bathymetryArray = arcpy.RasterToNumPyArray(datasetcode_bathymetry, nodata_to_value=np.nan)
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

                    msg = f">-------> Sum Weighted Bathymetry: {sumWeightedBathymetryArray}"
                    logFile(log_file, msg); del msg

                    #
                    CenterOfGravityDepth = sumWeightedBathymetryArray / sumBiomassArray

                    if br_year == first_year:
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
                    CenterOfGravityLatitude    = None
                    MinimumLatitude            = None
                    MaximumLatitude            = None
                    OffsetLatitude             = None
                    CenterOfGravityLatitudeSE  = None
                    CenterOfGravityLongitude   = None
                    MinimumLongitude           = None
                    MaximumLongitude           = None
                    OffsetLongitude            = None
                    CenterOfGravityLongitudeSE = None
                    CenterOfGravityDepth       = None
                    MinimumDepth               = None
                    MaximumDepth               = None
                    OffsetDepth                = None
                    CenterOfGravityDepthSE     = None
                else:
                    msg = 'Something wrong with biomass raster'
                    logFile(log_file, msg); del msg

                # Clean-up
                del maximumBiomass

                # Standard for all records
                DatasetCode             = datasetcode
                Region                  = region
                Season                  = season
                DateCode                = datecode
                # Species,CommonName,
                # CoreSpecies,
                Year                    = br_year
                DistributionProjectName = distributionprojectname
                DistributionProjectCode = distributionprojectcode
                SummaryProduct          = summaryproduct
                #
                row = [
                       DatasetCode,
                       Region,
                       Season,
                       DateCode,
                       Species,
                       CommonName,
                       CoreSpecies,
                       Year,
                       DistributionProjectName,
                       DistributionProjectCode,
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

                del br_year
                del Year, DistributionProjectName, DistributionProjectCode
                del SummaryProduct, CenterOfGravityLatitude, MinimumLatitude
                del MaximumLatitude, OffsetLatitude, CenterOfGravityLatitudeSE
                del CenterOfGravityLongitude, MinimumLongitude, MaximumLongitude
                del OffsetLongitude, CenterOfGravityLongitudeSE, CenterOfGravityDepth
                del MinimumDepth, MaximumDepth, OffsetDepth, CenterOfGravityDepthSE
                del DateCode, DatasetCode, Region, Season

            del biomassRasters
            del first_year
            del Species, CommonName, CoreSpecies
            del first_year_offset_latitude
            del first_year_offset_longitude, first_year_offset_depth

        del datasetcode, region, season, datecode, distributionprojectcode
        del distributionprojectname, summaryproduct
        del dataset_product_code, RegionGDB, datasetcodepath ,
        del datasetcode_folder, datasetcode_bathymetry, datasetcode_latitude
        del datasetcode_longitude, datasetcode_unique_species_common_name_dict
        del np, math,

        msg = ">-----> Inserting records into the table"
        logFile(log_file, msg); del msg

        PrintRowContent = False
        if PrintRowContent:
            for row_value in row_values:
                #print(row_value)
                # DatasetCode
                msg =  f"DatasetCode:                {row_value[4]}\n"
                msg += f"Region:                     {row_value[5]}\n"
                msg += f"Season:                     {row_value[6]}\n"
                msg += f"DateCode:                   {row_value[7]}\n"
                msg += f"Species:                    {row_value[8]}\n"
                msg += f"CommonName:                 {row_value[9]}\n"
                msg += f"CoreSpecies:                {row_value[10]}\n"
                msg += f"Year:                       {row_value[11]}\n"
                msg += f"DistributionProjectName:    {row_value[12]}\n"
                msg += f"DistributionProjectCode:    {row_value[13]}\n"
                msg += f"SummaryProduct:             {row_value[14]}\n"
                msg += f"CenterOfGravityLatitude:    {row_value[15]}\n"
                msg += f"MinimumLatitude:            {row_value[16]}\n"
                msg += f"MaximumLatitude:            {row_value[17]}\n"
                msg += f"OffsetLatitude:             {row_value[18]}\n"
                msg += f"CenterOfGravityLatitudeSE:  {row_value[19]}\n"
                msg += f"CenterOfGravityLongitude:   {row_value[20]}\n"
                msg += f"MinimumLongitude:           {row_value[21]}\n"
                msg += f"MaximumLongitude:           {row_value[22]}\n"
                msg += f"OffsetLongitude:            {row_value[23]}\n"
                msg += f"CenterOfGravityLongitudeSE: {row_value[24]}\n"
                msg += f"CenterOfGravityDepth:       {row_value[25]}\n"
                msg += f"MinimumDepth:               {row_value[26]}\n"
                msg += f"MaximumDepth:               {row_value[27]}\n"
                msg += f"OffsetDepth:                {row_value[28]}\n"
                msg += f"enterOfGravityDepthSE:      {row_value[29]}\n"
                logFile(log_file, msg); del msg
                if row_value: del row_value
        del PrintRowContent

        # This gets a list of fields in the table
        fields = [f.name for f in arcpy.ListFields(datasetcode_indicators) if f.type not in ['Geometry', 'OID']]

        # Open an InsertCursor
        cursor = arcpy.da.InsertCursor(datasetcode_indicators, fields)
        del datasetcode_indicators

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
                logFile(log_file.replace(".log", " ERROR.log"), msg); del msg, sys

        #print(row_values)
        # Delete cursor object
        del cursor, row_values, fields

# #    # Add some metadata
# #    years_md = unique_years(datasetcode_indicators)
# #
# #    datasetcode_indicators_md = md.Metadata(datasetcode_indicators)
# #    datasetcode_indicators_md.synchronize('ACCESSED', 1)
# #    datasetcode_indicators_md.title = "{0} Indicators {1}".format(region.replace('-',' to '), DateCode)
# #    datasetcode_indicators_md.tags = "{0}, {1} to {2}".format(geographic_regions[datasetcode], min(years_md), max(years_md))
# #    datasetcode_indicators_md.save()
# #    del datasetcode_indicators_md, years_md
# #    del layercode, datasetcode_indicators, DateCode

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
        return False
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
        return False

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

        return True # everything went well so we return True

# ## Reads from the queue and does work
def mpCreateLatitudeLongitudeRasters(dataset):
    """mp Create Biomass Rasters"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        datasetcode             = dataset[0]
        cellsize                = dataset[5]
        distributionprojectcode = dataset[12]
        del dataset

        dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

        RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

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

        msg = f'> Generating {dataset_product_code} Latitude and Longitude Rasters'
        logFile(log_file, msg); del msg

        datasetcode_lat_long    = f"{dataset_product_code}_Lat_Long"
        datasetcode_latitude     = f"{dataset_product_code}_Latitude"
        datasetcode_longitude    = f"{dataset_product_code}_Longitude"
        datasetcode_raster_mask = f"{dataset_product_code}_Raster_Mask"

        arcpy.env.cellSize   = cellsize
        arcpy.env.extent     = arcpy.Describe(datasetcode_raster_mask).extent
        arcpy.env.mask       = datasetcode_raster_mask
        arcpy.env.snapRaster = datasetcode_raster_mask

        msg = f"#-> Point to Raster Conversion using {datasetcode_lat_long} to create {datasetcode_longitude}"
        logFile(log_file, msg); del msg
        # Process: Point to Raster Longitude

        datasetcode_longitude_tmp = os.path.join(RegionScratchGDB, f"{datasetcode_longitude}_tmp")

        arcpy.conversion.PointToRaster(datasetcode_lat_long, "Longitude", datasetcode_longitude_tmp, "MOST_FREQUENT", "NONE", cellsize)

        if arcpy.CheckExtension("Spatial") == "Available":
                arcpy.CheckOutExtension("Spatial")
        else:
            # raise a custom exception
            raise LicenseError

        msg = f"#-> Extract by Mask to create {datasetcode_longitude}"
        logFile(log_file, msg); del msg
        # Execute ExtractByMask
        outExtractByMask = arcpy.sa.ExtractByMask(datasetcode_longitude_tmp, datasetcode_raster_mask, "INSIDE", datasetcode_longitude_tmp)

        arcpy.CheckInExtension("Spatial")

        # Save the output
        outExtractByMask.save(datasetcode_longitude)
        del outExtractByMask

        arcpy.management.Delete(datasetcode_longitude_tmp)
        del datasetcode_longitude_tmp

        #addMetadata(datasetcode_longitude)

        datasetcode_latitude_tmp = os.path.join(RegionScratchGDB, f"{datasetcode_latitude}_tmp")

        msg = f"#-> Point to Raster Conversion using {datasetcode_lat_long} to create {datasetcode_latitude}"
        logFile(log_file, msg); del msg
        # Process: Point to Raster Latitude
        arcpy.conversion.PointToRaster(datasetcode_lat_long, "Latitude", datasetcode_latitude_tmp, "MOST_FREQUENT", "NONE", cellsize)

        msg = f"#-> Extract by Mask to create {datasetcode_latitude}"
        logFile(log_file, msg); del msg
        # Execute ExtractByMask
        outExtractByMask = arcpy.sa.ExtractByMask(datasetcode_latitude_tmp, datasetcode_raster_mask, "INSIDE", datasetcode_latitude_tmp)

        # Save the output
        outExtractByMask.save(datasetcode_latitude)
        del outExtractByMask

        arcpy.management.Delete(datasetcode_latitude_tmp)
        del datasetcode_latitude_tmp

        #addMetadata(datasetcode_latitude)

        del datasetcode, cellsize
        del RegionGDB, RegionScratchGDB, datasetcode_lat_long
        del datasetcode_latitude, datasetcode_longitude, datasetcode_raster_mask
        del distributionprojectcode, dataset_product_code

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
        return False
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
        return False

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

        return True # everything went well so we return True

def mpCreateLayerBathymetry(dataset):
    """mp Create Region Bathymetry"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        print(msg)
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        datasetcode             = dataset[0]
        geographicarea          = dataset[4]
        cellsize                = dataset[5]
        distributionprojectcode = dataset[12]
        del dataset

        dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

        RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

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

        # Write a message to the log file
        msg = f"STARTING REGION {dataset_product_code} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        msg = f'> Generating {dataset_product_code} Bathymetry Rasters'
        logFile(log_file, msg); del msg

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
        #print(geographicarea_sr)
        del geographicarea

        datasetcode_sr = arcpy.SpatialReference(geographicarea_sr)
        del geographicarea_sr

        arcpy.env.outputCoordinateSystem = datasetcode_sr; del datasetcode_sr
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

         # Set cell size
        arcpy.env.cellSize = cellsize

        # Region datasets

        datasetcode_fishnet     = f"{dataset_product_code}_Fishnet"
        datasetcode_raster_mask = f"{dataset_product_code}_Raster_Mask"

        datasetcode_bathymetry = f"{dataset_product_code}_Bathymetry"
        bathymetry = os.path.join(RegionScratchGDB, f"{datasetcode_bathymetry}")

        # Process: Point to Raster Longitude
        arcpy.env.cellSize   = cellsize
        arcpy.env.extent     = arcpy.Describe(datasetcode_raster_mask).extent
        arcpy.env.mask       = datasetcode_raster_mask
        arcpy.env.snapRaster = datasetcode_raster_mask

        msg = f"#-> Zonal Statistics using {datasetcode_fishnet} and {os.path.basename(bathymetry)} to create {datasetcode_bathymetry}"
        logFile(log_file, msg); del msg
        # Execute ZonalStatistics
        outZonalStatistics = arcpy.sa.ZonalStatistics(datasetcode_fishnet, "OID", bathymetry, "MEDIAN", "NODATA")

        # Save the output
        outZonalStatistics.save(datasetcode_bathymetry)

        del outZonalStatistics

        # Resets a specific environment setting to its default
        arcpy.ClearEnvironment("cellSize")
        arcpy.ClearEnvironment("extent")
        arcpy.ClearEnvironment("mask")
        arcpy.ClearEnvironment("snapRaster")

        del RegionScratchGDB
        del RegionGDB
        del datasetcode, cellsize
        del datasetcode_fishnet, datasetcode_raster_mask
        del bathymetry, datasetcode_bathymetry, dataset_product_code
        del distributionprojectcode

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
        return False
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
        return False

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

        return True # everything went well so we return True

def mpCreateLayerFishnets(dataset):
    """mp Create Region Bathymetry"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        datasetcode             = dataset[0]
        geographicarea          = dataset[4]
        cellsize                = dataset[5]
        distributionprojectcode = dataset[12]
        del dataset

        dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

        RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

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
        msg = f'> Generating {datasetcode} Fishnet Dataset'
        logFile(log_file, msg); del msg

        # Set the output coordinate system to what is needed for the
        # DisMAP project
        geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
        #print(geographicarea_sr)
        del geographicarea

        datasetcode_sr = arcpy.SpatialReference(geographicarea_sr)
        del geographicarea_sr

        arcpy.env.outputCoordinateSystem = datasetcode_sr

        arcpy.env.cellSize = cellsize

        datasetcode_survey_area = os.path.join(RegionGDB, f"{dataset_product_code}_Survey_Area")
        datasetcode_raster_mask = os.path.join(RegionGDB, f"{dataset_product_code}_Raster_Mask")
        datasetcode_points      = os.path.join(RegionGDB, f"{dataset_product_code}_Points")
        datasetcode_fishnet     = os.path.join(RegionGDB, f"{dataset_product_code}_Fishnet")
        datasetcode_lat_long    = os.path.join(RegionGDB, f"{dataset_product_code}_Lat_Long")

        # Get Extent
        extent = arcpy.Describe(datasetcode_survey_area).extent
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

            pointGeometry = arcpy.PointGeometry(point, datasetcode_sr)
            pointGeometryList.append(pointGeometry)
            del pt, pointGeometry

        #print(pointList)
        # Delete after last use
        del pointList, point

        # Create a copy of the PointGeometry objects, by using pointGeometryList as
        # input to the CopyFeatures tool.
        arcpy.management.CopyFeatures(pointGeometryList, datasetcode_points)
        del pointGeometryList, RegionGDB

        # Add metadata
        #addMetadata(datasetcode_points)

        # Clearup after last use
        del datasetcode_points

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

        arcpy.env.outputCoordinateSystem = datasetcode_sr

        msg = f"> Create Fishnet with {cellSizeWidth} by {cellSizeHeight} cells"
        logFile(log_file, msg); del msg
        arcpy.management.CreateFishnet(datasetcode_fishnet, originCoordinate, yAxisCoordinate, cellSizeWidth, cellSizeHeight, numRows, numColumns, oppositeCoorner, labels, templateExtent, geometryType)

        del X_Min, Y_Min, X_Max, Y_Max
        del originCoordinate, yAxisCoordinate, cellSizeWidth
        del cellSizeHeight, numRows, numColumns, oppositeCoorner, labels
        del templateExtent, geometryType

# ###--->>> Select by location and trim
        msg = f"> Make Feature Layer for {dataset_product_code}_Fishnet_Layer"
        logFile(log_file, msg); del msg
        datasetcode_fishnet_layer = arcpy.management.MakeFeatureLayer(datasetcode_fishnet, "{0}_Fishnet_Layer".format(dataset_product_code))

        msg = f"> Select Layer by Location"
        logFile(log_file, msg); del msg

        arcpy.env.outputCoordinateSystem = datasetcode_sr

        arcpy.management.SelectLayerByLocation(datasetcode_fishnet_layer, "WITHIN_A_DISTANCE", datasetcode_survey_area, 2 * cellsize, "NEW_SELECTION", "INVERT")

        msg = f"> Delete Features from {dataset_product_code}_Fishnet_Layer"
        logFile(log_file, msg); del msg
        arcpy.management.DeleteFeatures(datasetcode_fishnet_layer)

        #addMetadata(datasetcode_fishnet)

        msg = f"> Deleting {dataset_product_code}_Fishnet_Layer"
        logFile(log_file, msg); del msg
        arcpy.management.Delete("{0}_Fishnet_Layer".format(dataset_product_code))
        del datasetcode_fishnet_layer #, datasetcode_fishnet_label_layer

        msg = f"> Feature to Point using {os.path.basename(datasetcode_fishnet)} to create {os.path.basename(datasetcode_lat_long)}"
        logFile(log_file, msg); del msg

        arcpy.env.outputCoordinateSystem = datasetcode_sr
        #
        arcpy.management.FeatureToPoint(datasetcode_fishnet, datasetcode_lat_long, "CENTROID")

        msg = f"> Delete Field ORIG_FID from {os.path.basename(datasetcode_lat_long)}"
        logFile(log_file, msg); del msg
        # Execute DeleteField
        arcpy.management.DeleteField(datasetcode_lat_long, ['ORIG_FID'])

        # Delete after last use
        del datasetcode_survey_area
        del datasetcode, cellsize
        del datasetcode_fishnet
        del datasetcode_lat_long
        del datasetcode_raster_mask
        del distributionprojectcode, dataset_product_code
        del datasetcode_sr

        # Resets a specific environment setting to its default
        arcpy.ClearEnvironment("cellSize")
        arcpy.ClearEnvironment("extent")
        arcpy.ClearEnvironment("mask")
        arcpy.ClearEnvironment("snapRaster")

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
        return False
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
        return False

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

        return True # everything went well so we return True

def mpCreateLayerSpeciesYearImageName(dataset):
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

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

        datasetcode             = dataset[0]
        tablename               = dataset[3]
        distributionprojectcode = dataset[12]
        filterregion            = dataset[15]
        filtersubregion         = dataset[16]
        del dataset

        dataset_product_code = f"{datasetcode}_{distributionprojectcode}"
        del distributionprojectcode

        RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")
        #del dataset_product_code

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

        #species_filter_table = os.path.join(RegionGDB, "Species_Filter")
        speciesfilter_table = "Species_Filter"
        fields = [f.name for f in arcpy.ListFields(speciesfilter_table) if f.type not in ['Geometry', 'OID']]

        # species         = row[0]
        # commonname      = row[1]
        # taxonomicgroup  = row[2]
        # filterregion    = row[3]
        # filtersubregion = row[4]
        # managementbody  = row[5]
        # managementplan  = row[6]

        speciesfilter = {}
        with arcpy.da.SearchCursor(speciesfilter_table, fields) as cursor:
            for row in cursor:
                speciesfilter[row[0]] = [row[1],row[2],row[3],row[4],row[5],row[6]]
                del row
        del cursor, speciesfilter_table, fields

        layerspeciesyearimagename = "LayerSpeciesYearImageName"

        # Get a record count to see if data is present
        # num = 12345
        # print(f"{num:,d}") >>> 12,345
        # print('{:,.2f}'.format(num)) >>> 12,345.00
        getcount = int(arcpy.management.GetCount(tablename)[0])
        msg = f'\t> {tablename} has {getcount:,d} records'
        logFile(log_file, msg); del msg, getcount

        layerspeciesyearimagenamefields  = [f.name for f in arcpy.ListFields(layerspeciesyearimagename) if f.type not in ['Geometry', 'OID']]
        datasetcodefields                 = [f.name for f in arcpy.ListFields(tablename) if f.type not in ['Geometry', 'OID']]

        casefields = [f for f in layerspeciesyearimagenamefields if f in datasetcodefields]
        #fds = '", "'.join(casefields)
        #print(f'Case Fields: "{fds}"'); del fds

        del layerspeciesyearimagenamefields, datasetcodefields

        # Execute Statistics to get unique set of records
        datasetcode_tmp = tablename+"_tmp"
        statsfields = [[f"{f}", "COUNT"] for f in casefields]

        msg = f"\t> Statistics Analysis of {tablename} Table"
        logFile(log_file, msg); del msg

        arcpy.analysis.Statistics(tablename, datasetcode_tmp, statsfields, casefields)
        del statsfields, casefields

        fields = [f.name for f in arcpy.ListFields(datasetcode_tmp) if f.type not in ['Geometry', 'OID']]
        #fds = '", "'.join(fields)
        #print(f'Delete Fields: "{fds}"'); del fds
        dropfields = ";".join([f for f in fields if "FREQUENCY" in f or "COUNT" in f])
        del fields
        #print(f'Delete Fields: {dropfields}')

        arcpy.management.DeleteField(in_table=datasetcode_tmp, drop_field=dropfields)
        del dropfields

        # Get a record count to see if data is present; we don't want to add data
        getcount = int(arcpy.management.GetCount(datasetcode_tmp)[0])
        msg = f'\t\t> {datasetcode_tmp} has {getcount:,d} records'
        logFile(log_file, msg); del msg, getcount

        msg = f'\t\t> Add Variable, Dimensions, and ImageName \n\t\t> Fields to {datasetcode_tmp} table'
        logFile(log_file, msg); del msg

        datasetcode_tmp_new_fields = ['FilterRegion', 'FilterSubRegion', 'TaxonomicGroup',
                                      'ManagementBody', 'ManagementPlan', 'Variable',
                                      'Value', 'Dimensions', 'ImageName',
                                     ]
        tb_fields = [f.name for f in arcpy.ListFields(datasetcode_tmp) if f.type not in ['Geometry', 'OID']]
        #fds = '", "'.join(tb_fields)
        #print(f'["{fds}"]'); del fds

        datasetcode_tmp_new_fields = [f for f in datasetcode_tmp_new_fields if f not in tb_fields]

        addFields(datasetcode_tmp, datasetcode_tmp_new_fields, field_definitions)
        del datasetcode_tmp_new_fields, tb_fields

        fields = [f.name for f in arcpy.ListFields(datasetcode_tmp) if f.type not in ['Geometry', 'OID']]
        #fds = '", "'.join(fields)
        #print(f'["{fds}"]'); del fields, fds

        # The following calculates the time stamp for the Dataset
        # Use Update Cursor instead of Calculate Field
        fields = ["DatasetCode", "Region", "Species", "Year", "FilterRegion", "FilterSubRegion", "TaxonomicGroup", "ManagementBody", "ManagementPlan",
                  "Variable", "Value", "Dimensions", "ImageName"]

        # species is key
        # commonname      = row[0]
        # taxonomicgroup  = row[1]
        # filterregion    = row[2]
        # filtersubregion = row[3]
        # managementbody  = row[4]
        # managementplan  = row[5]

        with arcpy.da.UpdateCursor(datasetcode_tmp, fields) as cursor:
            for row in cursor:
                #print(row)
                variable   = row[2].replace("(","").replace(")","").replace(".","")
                value      = "Species"
                dimensions = "StdTime"
                imagename  = f"{dataset_product_code}_{variable.replace(' ','_')}_{str(row[3])}"
                if row[2] in speciesfilter:
                    row[4]  = filterregion
                    row[5]  = filtersubregion
                    row[6]  = speciesfilter[row[2]][1] # TaxonomicGroup
                    row[7]  = speciesfilter[row[2]][4] # ManagementBody
                    row[8]  = speciesfilter[row[2]][5] # ManagementPlan
                else:
##                    row[4]  = filterregion
##                    row[5]  = filtersubregion
##                    row[6]  = "TaxonomicGroup"
##                    row[7]  = "ManagementBody"
##                    row[8]  = "ManagementPlan"
                    row[4]  = ""
                    row[5]  = ""
                    row[6]  = ""
                    row[7]  = ""
                    row[8]  = ""
                row[9]      = variable
                row[10]     = value
                row[11]     = dimensions
                row[12]     = imagename
                cursor.updateRow(row)
                del row, variable, value, dimensions, imagename
            del cursor
        del fields

        arcpy.management.Append(inputs = datasetcode_tmp, target = layerspeciesyearimagename, schema_type="NO_TEST", field_mapping="", subtype="")

        datasetcode_tmp_fields = [f.name for f in arcpy.ListFields(datasetcode_tmp) if f.type not in ['Geometry', 'OID']]
        #fds = '", "'.join(fields)
        #print(f'"{fds}"')

        if "CoreSpecies" in datasetcode_tmp_fields:

            fields = [f.name for f in arcpy.ListFields(datasetcode_tmp) if f.type not in ['Geometry', 'OID']]
            #print(fields)

            leaveoutfields = ["CoreSpecies", "Species", "CommonName", "SpeciesCommonName", "CommonNameSpecies", "TaxonomicGroup", "ManagementBody", "ManagementPlan", "Variable", "Value", "Dimensions", "ImageName"]

            casefields = [f for f in fields if f not in leaveoutfields]
            #fds = '", "'.join(casefields)
            #print(f'Case Fields: "{fds}"'); del fds
            del fields, leaveoutfields

            # Execute Statistics to get unique set of records
            datasetcode_tmp_stat = datasetcode_tmp+"stat"

            statsfields = [[f"{f}", "COUNT"] for f in casefields]

            msg = f"\t> Statistics Analysis of {os.path.basename(datasetcode_tmp)} Table"
            logFile(log_file, msg); del msg
            #print(msg); del msg

            arcpy.analysis.Statistics(datasetcode_tmp, datasetcode_tmp_stat, statsfields, casefields)
            del statsfields, casefields

            fields = [f.name for f in arcpy.ListFields(datasetcode_tmp_stat) if f.type not in ['Geometry', 'OID']]
            #for field in fields: print(field)
            #del field, fields
            #fds = '", "'.join(fields)
            #print(f'Delete Fields: "{fds}"'); del fds
            dropfields = ";".join([f for f in fields if "FREQUENCY" in f or "COUNT" in f])
            del fields
            #print(f'Delete Fields: {dropfields}')

            arcpy.management.DeleteField(in_table=datasetcode_tmp_stat, drop_field=dropfields)
            del dropfields

            # Get a record count to see if data is present; we don't want to add data
            getcount = int(arcpy.management.GetCount(datasetcode_tmp_stat)[0])
            msg = f'\t\t> {os.path.basename(datasetcode_tmp_stat)} has {getcount:,d} records'
            logFile(log_file, msg); del msg, getcount

            msg = f'\t\t> Add Variable, Dimensions, and ImageName \n\t\t> Fields to {os.path.basename(datasetcode_tmp_stat)} table'
            logFile(log_file, msg); del msg

            datasetcode_tmp_new_fields = ['CoreSpecies', 'Variable', 'Value',
                                          'Dimensions', 'ImageName',
                                         ]

            tb_fields = [f.name for f in arcpy.ListFields(datasetcode_tmp_stat) if f.type not in ['Geometry', 'OID']]
            #fds = '", "'.join(tb_fields)
            #print(f'["{fds}"]'); del fds

            datasetcode_tmp_new_fields = [f for f in datasetcode_tmp_new_fields if f not in tb_fields]

            addFields(datasetcode_tmp_stat, datasetcode_tmp_new_fields, field_definitions)
            del datasetcode_tmp_new_fields, tb_fields

            fields = [f.name for f in arcpy.ListFields(datasetcode_tmp_stat) if f.type not in ['Geometry', 'OID']]
            #fds = '", "'.join(fields)
            #print(f'["{fds}"]'); del fds
            #["DatasetCode", "Region", "Season", "SummaryProduct", "Year", "StdTime", "FilterRegion", "FilterSubRegion", "CoreSpecies", "Variable", "Value", "Dimensions", "ImageName"]

            with arcpy.da.UpdateCursor(datasetcode_tmp_stat, fields) as cursor:
                for row in cursor:
                    variable   = "Core Species Richness"
                    value      = "Core Species Richness"
                    dimensions = "StdTime"
                    imagename  = f"{dataset_product_code}_{variable.replace(' ','_')}_{str(row[4])}"
                    row[6]     = filterregion
                    row[7]     = filtersubregion
                    row[8]     = "Yes"
                    row[9]     = variable
                    row[10]    = value
                    row[11]    = dimensions
                    row[12]    = imagename
                    cursor.updateRow(row)
                    del row, variable, value, dimensions, imagename
            del cursor

            arcpy.management.Append(inputs = datasetcode_tmp_stat, target = layerspeciesyearimagename, schema_type="NO_TEST", field_mapping="", subtype="")

            # The following calculates the time stamp for the Dataset
            # Use Update Cursor instead of Calculate Field

            with arcpy.da.UpdateCursor(datasetcode_tmp_stat, fields) as cursor:
                for row in cursor:
                    # #variable   = "Core Species Richness" if row[8] == "Yes" else "Species Richness"
                    variable   = "Species Richness"
                    value      = "Species Richness"
                    dimensions = "StdTime"
                    imagename  = f"{dataset_product_code}_{variable.replace(' ','_')}_{str(row[4])}"
                    row[6]     = filterregion
                    row[7]     = filtersubregion
                    row[8]     = "No"
                    row[9]     = variable
                    row[10]    = value
                    row[11]    = dimensions
                    row[12]    = imagename
                    #print(row)
                    cursor.updateRow(row)
                    del row, variable, value, dimensions, imagename
            del fields, cursor

            arcpy.management.Append(inputs = datasetcode_tmp_stat, target = layerspeciesyearimagename, schema_type="NO_TEST", field_mapping="", subtype="")

            #arcpy.management.Delete(datasetcode_tmp_stat)
            del datasetcode_tmp_stat


        del datasetcode_tmp_fields
        # Remove temporary table
        #arcpy.management.Delete(datasetcode_tmp)
        del datasetcode_tmp
        #msg = arcpy.GetMessages().replace('\n', '\n\t\t ')
        #logFile(log_file, msg); del msg

        del RegionGDB, datasetcode, layerspeciesyearimagename
        del speciesfilter, tablename, filterregion, filtersubregion
        del dataset_product_code

        #Final benchmark for the function.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, end_time, elapse_time, start_time#, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def mpCreateLayerTables(dataset):
    """mp Create CSV Tables"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        import pandas as pd
        import numpy as np
        import warnings

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        datasetcode             = dataset[0]
        csvfile                 = dataset[1]
        transformunit           = dataset[2]
        region                  = dataset[8]
        season                  = dataset[9]
        distributionprojectcode = dataset[12]
        summaryproduct          = dataset[14]
        del dataset

        dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

        RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

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

        start_time = time()

        # Write a message to the log file
        msg = f"STARTING REGION {datasetcode} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        input_csvfile = os.path.join(CSV_DIRECTORY, csvfile)

        #
        msg = f'> Generating CSV Table: {os.path.basename(input_csvfile)}'
        logFile(log_file, msg); del msg

        if summaryproduct == "No":
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
                #parse_dates = ['year']
                df = pd.read_csv(input_csvfile,
                                 #index_col = False,
                                 index_col = 0,
                                 encoding="utf-8",
                                 #encoding = "ISO-8859-1",
                                 #engine='python',
                                 delimiter = ',',
                                 #dtype = None, #year,lon_UTM,lat_UTM,lat,lon,depth_m,median_est,spp_sci,spp_common,median_est_kgha
                                 #parse_dates=parse_dates,
                                 dtype = {
                                          "year"              : 'uint16',
                                          "lon_UTM"           : float,
                                          "lat_UTM"           : float,
                                          "lat"               : float,
                                          "lon"               : float,
                                          "depth_m"           : float,
                                          "median_est"        : float,
                                          "spp_sci"           : str,
                                          "spp_common"        : str,
                                          "wtcpue"            : float,
                                          "transformed_value" : float,
                                          "transform_unit"    : str,
                                          },
                                 )
            del input_csvfile
            #parse_dates

            msg = f'>-> Defining the column names.'
            logFile(log_file, msg); del msg

            # The original column names from the CSV files are not very
            # reader friendly, so we are making some changes here
            df.columns  = ['Year', 'Easting', 'Northing', 'Latitude', 'Longitude', 'Depth', 'MedianEstimate', 'Species', 'CommonName', 'WTCPUE', 'MapValue', 'TransformUnit',]
            new_columns = ['Year', 'Species', 'WTCPUE', 'MapValue', 'TransformUnit', 'CommonName', 'Easting', 'Northing', 'Latitude', 'Longitude', 'MedianEstimate', 'Depth',]
            df = df[new_columns]; del new_columns

            # Test if we are filtering on species. If so, a new species list is
            # created with the selected species remaining in the list
            if FilterSpecies:
                msg = f'>->-> Filtering table on selected species for {datasetcode} Table'
                logFile(log_file, msg); del msg
                # Filter data frame
                df = df.loc[df['Species'].isin(selected_species.keys())]
            else:
                msg = f'>->-> No species filtering of selected species for {datasetcode} Table'
                logFile(log_file, msg); del msg

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
            #df.insert(df.columns.get_loc('Year'), 'DatasetCode', f"{datasetcode}")
            #print(df.columns.get_loc('Year'))
            df.insert(0, 'DatasetCode', f"{datasetcode}")

            #-->> Region
            msg = f'#--->  Adding Region.'
            logFile(log_file, msg); del msg
            # Insert column
            #df.insert(df.columns.get_loc('Year'), 'Region', f"{region}")
            df.insert(1, 'Region', f"{region}")

            #-->> SummaryProduct
            msg = f'#--->  Adding SummaryProduct.'
            logFile(log_file, msg); del msg
            # Insert column
            #df.insert(df.columns.get_loc('StdTime') + 1, 'SummaryProduct', f"{summaryproduct}")
            df.insert(2, 'SummaryProduct', f"{summaryproduct}")

            #-->> StdTime
            msg = f'#--->  Adding StdTime.'
            logFile(log_file, msg); del msg
            # Insert column
            #df.insert(df.columns.get_loc('Year')+1, 'StdTime', pd.to_datetime(df['Year'], format="%Y").dt.tz_localize(timezones[datasetcode]))
            df.insert(4, 'StdTime', pd.to_datetime(df['Year'], format="%Y").dt.tz_localize(timezones[datasetcode]).dt.tz_convert('UTC'))

            #df['Year'] = df['Year'].dt.strftime('%Y')

            #-->> SpeciesCommonName
            msg = f'#--->  Adding SpeciesCommonName and setting it to "Species (CommonName)".'
            logFile(log_file, msg); del msg
            # Insert column
            #df.insert(df.columns.get_loc('CommonName')+1, 'SpeciesCommonName', df['Species'] + ' (' + df['CommonName'] + ')')
            df.insert(10, 'SpeciesCommonName', df['Species'] + ' (' + df['CommonName'] + ')')

            #-->> CommonNameSpecies
            msg = f'#--->  Adding CommonNameSpecies and setting it to "CommonName (Species)".'
            logFile(log_file, msg); del msg
            # Insert column
            #df.insert(df.columns.get_loc('SpeciesCommonName')+1, 'CommonNameSpecies', df['CommonName'] + ' (' + df['Species'] + ')')
            df.insert(11, 'CommonNameSpecies', df['CommonName'] + ' (' + df['Species'] + ')')

            #df.drop(['wtcpue', 'transformed_value', 'transform_unit'], axis=1)
            #df.drop(columns=['wtcpue', 'transformed_value', 'transform_unit'], inplace=True)

            msg = f'>-> Creating the {datasetcode} Geodatabase Table'
            logFile(log_file, msg); del msg

            # ###--->>> Numpy Datatypes
            # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm

            # Get max length of all columns in the dataframe
            # max_length_all_cols = {col: df.loc[:, col].astype(str).apply(len).max() for col in df.columns}
            # type_dict = {'TEXT' : "S", 'SHORT' : "u4", 'DOUBLE' : 'd', 'DATE' : 'M8[us]' }

            # print([f'S{max_length_all_cols[v]}' for v in max_length_all_cols])
            # print([f'{v} : {max_length_all_cols[v]},' for v in max_length_all_cols])
            # print([f'S{field_definitions[v][3]}' for v in max_length_all_cols])
            # print([f'{v} S{field_definitions[v][3]}' for v in max_length_all_cols])
            # print([f'{field_definitions[v][1]} {field_definitions[v][3]}' for v in max_length_all_cols])

            # small = 10
            # big   = 20
            # multiplier = lambda x: big if x > small else small
            # nearest = lambda x: multiplier(x) * math.ceil(x / multiplier(x))

            # for key in max_length_all_cols:
            #     print(f"\t# # {key:23} = {max_length_all_cols[key]:3} ({nearest(max_length_all_cols[key]):2})")
            #    max_length_all_cols[key] = nearest(max_length_all_cols[key])

            # print([f'{v} : {max_length_all_cols[v]},' for v in max_length_all_cols])
            # print([f'S{max_length_all_cols[v]}' for v in max_length_all_cols])
            # del max_length_all_cols

            #print('DataFrame\n----------\n', df.head(10))
            #print('DataFrame datatypes:\n', df.dtypes)
            #columns = [str(c) for c in df.dtypes.index.tolist()]
            column_names = list(df.columns)
            #print(column_names); del columns

            # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
            #[                'DatasetCode', 'Region', 'SummaryProduct', 'Year',   'StdTime', 'Species', 'WTCPUE', 'MapValue', 'TransformUnit', 'CommonName', 'SpeciesCommonName', 'CommonNameSpecies', 'Easting', 'Northing', 'Latitude', 'Longitude', 'MedianEstimate', 'Depth',]
            column_formats = [ 'S20',        'S40',    'S5',             'u4',     'M8[us]',  'S50',     'd',      'd',        'S30',           'U40',        'U90',               'U90',               'd',       'd',        'd',        'd',         'd',              'd', ]
            #column_formats = [ 'S20',       'S40',    'S5',             'M8[us]', 'M8[us]',  'S40',     'd',      'd',        'S30',           'U30',        'U60',               'U60',               'd',       'd',        'd',        'd',         'd',              'd',  ]

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
                logFile(log_file, msg); del msg

            del df, dtypes

            # Temporary table
            tmp_table = f'memory\{csvfile.replace(".csv", "")}_tmp'
            #print(csvfile)
            #tmp_table = os.path.join(RegionScratchGDB, f'{csvfile}_tmp'); del RegionScratchGDB

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

            msg = f'>-> Copying the {datasetcode} Table from memory to the GDB'
            logFile(log_file, msg); del msg

            out_table = os.path.join(RegionGDB, csvfile.replace(".csv", ""))

            # Execute CreateTable
            #arcpy.management.CreateTable(RegionGDB, csvfile, os.path.join(RegionGDB, "GLMME_Data"), "", "")

            del RegionGDB

            arcpy.management.CopyRows(tmp_table, out_table, "")

            # Remove the temporary table
            arcpy.management.Delete(tmp_table)
            del tmp_table

            # Cleanup
            del out_table

        if summaryproduct == "Yes":
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
                #parse_dates = ['year']
                df = pd.read_csv(input_csvfile,
                                 index_col = 0,
                                 encoding="utf-8",
                                 #encoding = "ISO-8859-1",
                                 #engine='python',
                                 delimiter = ',',
                                 #dtype = None,
                                 #parse_dates=parse_dates,
                                 dtype = {
                                          "region"      : str,
                                          "sampleid"    : str,
                                          "year"        : 'uint16',
                                          # 'TrawlDate' : 'uint16',
                                          # 'SurfaceTemperature' : float,
                                          # 'BottomTemperature' : float,
                                          "spp"         : str,
                                          "wtcpue"      : float,
                                          "common"      : str,
                                          "stratum"     : str,
                                          "stratumarea" : float,
                                          "lat"         : float,
                                          "lon"         : float,
                                          "depth"       : float,
                                          },
                                 )
            del input_csvfile
            # del parse_dates

            msg = f'>-> Defining the column names.'
            logFile(log_file, msg); del msg

            # The original column names from the CSV files are not very
            # reader friendly, so we are making some changes here
            df.columns = ['Region', 'SampleID', 'Year', 'Species', 'WTCPUE', 'CommonName', 'Stratum', 'StratumArea', 'Latitude', 'Longitude', 'Depth']

            # Test if we are filtering on species. If so, a new species list is
            # created with the selected species remaining in the list
            if FilterSpecies:
                msg = f'>->-> Filtering table on selected species for {datasetcode} Table'
                logFile(log_file, msg); del msg
                # Filter data frame
                df = df.loc[df['Species'].isin(selected_species.keys())]
            else:
                msg = f'>->-> No species filtering of selected species for {datasetcode} Table'
                logFile(log_file, msg); del msg

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

            #-->> Dataset Code
            msg = f'#--->  Adding Dataset Code.'
            logFile(log_file, msg); del msg
            # Insert column
            df.insert(df.columns.get_loc('Region'), 'DatasetCode', f"{datasetcode}")

            #-->> Season
            msg = f'#--->  Adding Season.'
            logFile(log_file, msg); del msg
            # Insert column
            df.insert(df.columns.get_loc('Region')+1, 'Season', f"{season}")

            #-->> SummaryProduct
            msg = f'#--->  Adding SummaryProduct.'
            logFile(log_file, msg); del msg
            # Insert column
            df.insert(df.columns.get_loc('Season'), 'SummaryProduct', f"{summaryproduct}")

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

            #-->> MapValue
            msg = f'#--->  Adding the MapValue column and calculating values.'
            logFile(log_file, msg); del msg
            # Insert a column to the right of a column and then do a calculation
            df.insert(df.columns.get_loc('WTCPUE')+1, 'MapValue', df['WTCPUE'].pow((1.0/3.0)))

            #-->> TransformUnit
            msg = f'#--->  Adding the TransformUnit column and calculating values.'
            logFile(log_file, msg); del msg
            # Insert a column to the right of a column and then do a calculation
            df.insert(df.columns.get_loc('MapValue')+1, 'TransformUnit', transformunit)

            #-->> StdTime
            msg = f'#--->  Adding StdTime.'
            logFile(log_file, msg); del msg
            # Insert column
            #df.insert(df.columns.get_loc('Year')+1, 'StdTime', pd.to_datetime(df['Year'], format="%Y").dt.tz_localize(timezones[datasetcode])
            df.insert(df.columns.get_loc('Year')+1, 'StdTime', pd.to_datetime(df['Year'], format="%Y").dt.tz_localize(timezones[datasetcode]).dt.tz_convert('UTC'))

            #df['Year'] = df['Year'].dt.strftime('%Y')

            msg = f'>-> Creating the {datasetcode} Geodatabase Table'
            logFile(log_file, msg); del msg

            # ###--->>> Numpy Datatypes
            # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm

            # Get max length of all columns in the dataframe
            # max_length_all_cols = {col: df.loc[:, col].astype(str).apply(len).max() for col in df.columns}
            # type_dict = {'TEXT' : "S", 'SHORT' : "u4", 'DOUBLE' : 'd', 'DATE' : 'M8[us]' }

            # print([f'S{max_length_all_cols[v]}' for v in max_length_all_cols])
            # print([f'{v} : {max_length_all_cols[v]},' for v in max_length_all_cols])
            # print([f'S{field_definitions[v][3]}' for v in max_length_all_cols])
            # print([f'{v} S{field_definitions[v][3]}' for v in max_length_all_cols])
            # print([f'{field_definitions[v][1]} {field_definitions[v][3]}' for v in max_length_all_cols])

            # small = 10
            # big   = 20
            # multiplier = lambda x: big if x > small else small
            # nearest = lambda x: multiplier(x) * math.ceil(x / multiplier(x))

            # for key in max_length_all_cols:
            #     print(f"\t# # {key:23} = {max_length_all_cols[key]:3} ({nearest(max_length_all_cols[key]):2})")
            #    max_length_all_cols[key] = nearest(max_length_all_cols[key])

            # print([f'{v} : {max_length_all_cols[v]},' for v in max_length_all_cols])
            # print([f'S{max_length_all_cols[v]}' for v in max_length_all_cols])
            # del max_length_all_cols

            #print('DataFrame\n----------\n', df.head(10))
            #print('\nDataFrame datatypes :\n', df.dtypes)
            #columns = [str(c) for c in df.dtypes.index.tolist()]
            column_names = list(df.columns)
            #print(column_names)
            # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
            #[                'DatasetCode', 'Region', 'Season', 'SummaryProduct', 'SampleID', 'Year', 'StdTime',  'Species', 'WTCPUE', 'MapValue', 'TransformUnit', 'CommonName', 'SpeciesCommonName', 'CommonNameSpecies', 'CoreSpecies', 'Stratum', 'StratumArea', 'Latitude', 'Longitude', 'Depth']
            column_formats = [ 'S20',        'S40',    'S10',    'S5',             'S20',       'u4',   'M8[us]',   'S50',     'd',      'd',        'S30',           'U40',        'U90',               'U90',               'S5',          'S20',     'd',           'd',        'd',        'd']
            #column_formats = ['S20',       'S40',    'S10',    'S5',             'S20',      'M8[us]',   'M8[us]',   'S40',     'd',      'd',        'S30',           'U30',        'U60',               'U60',               'S5',          'S20',     'd',           'd',        'd',        'd']
            # 'M8[us]' can be used for date fields

            dtypes = list(zip(column_names, column_formats))
            del column_names, column_formats

            try:
                array = np.array(np.rec.fromrecords(df.values), dtype = dtypes)
            except Exception as e:
                import sys
                # Capture all other errors
                #print(sys.exc_info()[2].tb_lineno)
                msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
                logFile(log_file, msg); del msg

            del df, dtypes

            # Temporary table
            tmp_table = f'memory\{csvfile.replace(".csv", "")}_tmp'

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
                logFile(log_file, msg); del msg

            msg = f'>-> Calculate Core Species for the {datasetcode} Table'
            logFile(log_file, msg); del msg

            # Calculate Core Species
            calculateCoreSpecies(tmp_table, log_file)

            msg = f'>-> Copying the {datasetcode} Table from memory to the GDB'
            logFile(log_file, msg); del msg

            out_table = os.path.join(RegionGDB, csvfile.replace(".csv", ""))

            # Execute CreateTable
            #arcpy.management.CreateTable(RegionGDB, csvfile, os.path.join(RegionGDB, "IDW_Data"), "", "")

            del RegionGDB

            arcpy.management.CopyRows(tmp_table, out_table, "")

            # Remove the temporary table
            arcpy.management.Delete(tmp_table)
            del tmp_table

            # Cleanup
            del out_table

        del datasetcode, region, csvfile, transformunit
        del season, summaryproduct, distributionprojectcode, dataset_product_code

        del pd, np, warnings

         #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

# ## Reads from the queue and does work
def mpCreateMosaics(dataset):
    """mp Create Core Species Richness Rasters"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        import numpy as np

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        datasetcode             = dataset[0]
        geographicarea          = dataset[4]
        cellsize                = dataset[5]
        distributionprojectcode = dataset[12]
        mosaicname              = dataset[19]
        mosaictitle             = dataset[20]
        del dataset

        dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

        RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        arcpy.env.rasterStatistics = u'STATISTICS 1 1'
        arcpy.env.buildStatsAndRATForTempRaster = True

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

        mosaicname_path = os.path.join(RegionGDB, mosaicname)

        # Loading images into the Mosaic.
        msg = f'> Loading the {dataset_product_code} Mosaic. This may take a while... Please wait...'
        logFile(log_file, msg)

        with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
            msg = f'\t> Creating the {dataset_product_code} Mosaic'
            logFile(log_file, msg)

            geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
            # Set the output coordinate system to what is needed for the
            # DisMAP project
            psr = arcpy.SpatialReference(geographicarea_sr)
            del geographicarea_sr, geographicarea

            arcpy.management.CreateMosaicDataset(in_workspace = RegionGDB,
                                                 in_mosaicdataset_name = mosaicname,
                                                 coordinate_system = psr,
                                                 num_bands = "1",
                                                 pixel_type = "32_BIT_FLOAT",
                                                 product_definition = "",
                                                 product_band_definitions="")

            msg = arcpy.GetMessages()
            msg = ">->-> {0}\n".format(msg.replace('\n', '\n>->-> '))
            logFile(log_file, msg); del msg

        layerspeciesyearimagename_table = os.path.join(RegionGDB, "LayerSpeciesYearImageName")

        input_raster_paths = []
        input_rasters_path = os.path.join(IMAGE_DIRECTORY, dataset_product_code)

        msg = f"\t> Walking the {os.path.basename(input_rasters_path)} directory searching for species rasters."
        logFile(log_file, msg); del msg

        # Get a list of input_rasters
        walk = arcpy.da.Walk(input_rasters_path, topdown=True, datatype="RasterDataset")
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                if os.path.basename(dirpath) not in ["_Core Species Richness", "_Species Richness",]:
                    if dirpath not in input_raster_paths:
                        input_raster_paths.append(dirpath)
                del filename
        del walk, dirpath, dirnames, filenames

        msg = f"\t> Loading Species Rasters into the {os.path.basename(mosaicname_path)}."
        logFile(log_file, msg); del msg

        for input_raster_path in input_raster_paths:
            msg = f"\t\t> Layer Code: {dataset_product_code} Species: {os.path.basename(input_raster_path)}."
            logFile(log_file, msg); del msg

            arcpy.management.AddRastersToMosaicDataset(in_mosaic_dataset = mosaicname_path,
                                                       raster_type = "Raster Dataset",
                                                       input_path = input_raster_path,
                                                       update_cellsize_ranges = "UPDATE_CELL_SIZES",
                                                       #update_cellsize_ranges = "NO_CELL_SIZES",
                                                       update_boundary = "UPDATE_BOUNDARY",
                                                       #update_boundary = "NO_BOUNDARY",
                                                       update_overviews = "NO_OVERVIEWS",
                                                       maximum_pyramid_levels = "",
                                                       maximum_cell_size = "0",
                                                       minimum_dimension = "1500",
                                                       spatial_reference = psr,
                                                       #filter = "*Richness.tif",
                                                       #filter = "*Richness.tif",
                                                       filter = "",
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
            del input_raster_path
        del input_raster_paths

        input_raster_paths = []
        input_rasters_path = os.path.join(IMAGE_DIRECTORY, dataset_product_code)

        msg = f"\t> Walking the {os.path.basename(input_rasters_path)} directory searching for species richness rasters."
        logFile(log_file, msg); del msg

        # Get a list of input_rasters
        walk = arcpy.da.Walk(input_rasters_path, topdown=True, datatype="RasterDataset")
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                if os.path.basename(dirpath) in ["_Core Species Richness", "_Species Richness",]:
                    if dirpath not in input_raster_paths:
                        input_raster_paths.append(dirpath)
                del filename
        del walk, dirpath, dirnames, filenames

        msg = f"\t> Loading Species Richness Rasters into the {os.path.basename(mosaicname_path)}."
        logFile(log_file, msg); del msg

        for input_raster_path in input_raster_paths:
            msg = f"\t\t> Layer Code: {dataset_product_code} Species: {os.path.basename(input_raster_path)}."
            logFile(log_file, msg); del msg

            arcpy.management.AddRastersToMosaicDataset(in_mosaic_dataset = mosaicname_path,
                                                       raster_type = "Raster Dataset",
                                                       input_path = input_raster_path,
                                                       update_cellsize_ranges = "UPDATE_CELL_SIZES",
                                                       #update_cellsize_ranges = "NO_CELL_SIZES",
                                                       update_boundary = "UPDATE_BOUNDARY",
                                                       #update_boundary = "NO_BOUNDARY",
                                                       update_overviews = "NO_OVERVIEWS",
                                                       maximum_pyramid_levels = "",
                                                       maximum_cell_size = "0",
                                                       minimum_dimension = "1500",
                                                       spatial_reference = psr,
                                                       #filter = "*Richness.tif",
                                                       #filter = "*Richness.tif",
                                                       filter = "",
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

            del input_raster_path
        del input_raster_paths, psr

        del input_rasters_path

        msg = f">-> Joining {os.path.basename(mosaicname_path)} with {os.path.basename(layerspeciesyearimagename_table)}"
        logFile(log_file, msg); del msg

        fields = [f.name for f in arcpy.ListFields(layerspeciesyearimagename_table) if not f.required]
        #print(";".join(fields))
        arcpy.management.JoinField(in_data = mosaicname_path, in_field="Name", join_table = layerspeciesyearimagename_table, join_field="ImageName", fields="DatasetCode;Region;Season;Species;CommonName;SpeciesCommonName;CoreSpecies;Year;StdTime;Variable;Value;Dimensions")

        del layerspeciesyearimagename_table

        msg = f'>-> Removing field index for {os.path.basename(mosaicname_path)}'
        logFile(log_file, msg); del msg

        try:
            arcpy.RemoveIndex_management(datasetcode_mosaic, [f"{dataset_product_code}_MosaicSpeciesIndex",])
        except:
            pass

        msg = f'>-> Adding field index for {os.path.basename(mosaicname_path)}'
        logFile(log_file, msg); del msg

        # Add Attribute Index
        arcpy.management.AddIndex(mosaicname_path, ['Species', 'CommonName', 'SpeciesCommonName', 'Year'], f"{dataset_product_code}_MosaicSpeciesIndex", "NON_UNIQUE", "NON_ASCENDING")

        msg = arcpy.GetMessages()
        msg = ">->->-> {0}".format(msg.replace('\n', '\n>->->-> '))
        logFile(log_file, msg); del msg

        #--->>> SetMosaicDatasetProperties
        msg = ">-> Set Mosaic Dataset Properties"
        logFile(log_file, msg)

        #fields = [f.name for f in arcpy.ListFields(mosaicname_path) if f.type not in ['Geometry', 'OID'] and f.name not in ["Shape", "Raster", "Category", "TypeID", "ItemTS", "UriHash", "Uri",]]
        fields = [f.name for f in arcpy.ListFields(mosaicname_path)]

        fields = ";".join(fields)
        #fds = '", "'.join(fields)
        #print(f'["{fds}"]'); del fds

        processing_templates        = os.path.join(BASE_DIRECTORY, "RasterFunctionTemplates/Project1/Statistics and Histogram.rft.xml")
        default_processing_template = os.path.join(BASE_DIRECTORY, "RasterFunctionTemplates/Project1/Statistics and Histogram.rft.xml")

        arcpy.management.SetMosaicDatasetProperties(
                                                    in_mosaic_dataset=mosaicname_path,
                                                    rows_maximum_imagesize=4100,
                                                    columns_maximum_imagesize=15000,
                                                    allowed_compressions="None;JPEG;LZ77;LERC",
                                                    default_compression_type="LZ77",
                                                    JPEG_quality=75,
                                                    LERC_Tolerance=0.01,
                                                    resampling_type="BILINEAR",
                                                    clip_to_footprints="NOT_CLIP",
                                                    footprints_may_contain_nodata="FOOTPRINTS_MAY_CONTAIN_NODATA",
                                                    clip_to_boundary="CLIP",
                                                    color_correction="NOT_APPLY",
                                                    allowed_mensuration_capabilities="Basic",
                                                    default_mensuration_capabilities="Basic",
                                                    allowed_mosaic_methods="NorthWest;Center;LockRaster;ByAttribute;Nadir;Viewpoint;Seamline;None",
                                                    default_mosaic_method="NorthWest",
                                                    order_field="",
                                                    order_base="",
                                                    sorting_order="ASCENDING",
                                                    mosaic_operator="FIRST",
                                                    blend_width=10,
                                                    view_point_x=600,
                                                    view_point_y=300,
                                                    max_num_per_mosaic=20,
                                                    cell_size_tolerance=0.8,
                                                    cell_size=f"{cellsize} {cellsize}",
                                                    metadata_level="FULL",
                                                    transmission_fields=fields,
                                                    use_time="ENABLED",
                                                    start_time_field="StdTime",
                                                    end_time_field="StdTime",
                                                    time_format="YYYYMMDD",
                                                    geographic_transform=None,
                                                    max_num_of_download_items=20,
                                                    max_num_of_records_returned=1000,
                                                    data_source_type="GENERIC",
                                                    minimum_pixel_contribution=1,
                                                    #processing_templates = "None",
                                                    processing_templates = processing_templates,
                                                    #processing_templates="None;'Anoplopoma fimbria';'Core Species Richness';'Gadus chalcogrammus';'Limanda aspera';'Microstomus pacificus';'Species Richness'",
                                                    #default_processing_template="None",
                                                    default_processing_template = default_processing_template,
                                                    time_interval=1,
                                                    time_interval_units="Years",
                                                    product_definition="NONE",
                                                    product_band_definitions=None
                                                   )
        del fields, processing_templates, default_processing_template

        msg = f">-> Adding Multidimensional Information to {os.path.basename(mosaicname_path)} Dataset"
        logFile(log_file, msg); del msg

        with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
            arcpy.md.BuildMultidimensionalInfo(
                                                in_mosaic_dataset=mosaicname_path,
                                                variable_field="Variable",
                                                dimension_fields="StdTime Year Year",
                                                variable_desc_units=None,
                                                delete_multidimensional_info="NO_DELETE_MULTIDIMENSIONAL_INFO"
                                               )

        msg = arcpy.GetMessages()
        msg = ">->-> {0}".format(msg.replace('\n', '\n>->-> '))
        logFile(log_file, msg); del msg

        msg = f">-> arcpy.management.AnalyzeMosaicDataset for {mosaicname}"
        logFile(log_file, msg); del msg

        arcpy.management.AnalyzeMosaicDataset(
                                              in_mosaic_dataset=mosaicname_path,
                                              where_clause="",
                                              checker_keywords="FOOTPRINT;FUNCTION;RASTER;PATHS;SOURCE_VALIDITY;STALE;PYRAMIDS;STATISTICS;PERFORMANCE;INFORMATION"
                                             )
        msg = arcpy.GetMessages()
        msg = ">->-> {0}".format(msg.replace('\n', '\n>->-> '))
        logFile(log_file, msg); del msg

        # Copy Raster to CRF
        crf = os.path.join( ScratchFolder, f"{mosaicname.replace('_Mosaic', '')}.crf")#print(crf)
        #print(os.path.basename(mosaicname_path))
        arcpy.management.CopyRaster(
                                    in_raster=mosaicname_path,
                                    out_rasterdataset=crf,
                                    config_keyword="",
                                    background_value=None,
                                    nodata_value="",
                                    onebit_to_eightbit="NONE",
                                    colormap_to_RGB="NONE",
                                    pixel_type="",
                                    scale_pixel_value="NONE",
                                    RGB_to_Colormap="NONE",
                                    format="CRF",
                                    transform=None,
                                    process_as_multidimensional="ALL_SLICES",
                                    build_multidimensional_transpose="NO_TRANSPOSE"
                                   )
        del mosaicname_path

        msg = arcpy.GetMessages()
        msg = ">->-> {0}".format(msg.replace('\n', '\n>->-> '))
        logFile(log_file, msg); del msg

        msg = f">->-> Calculate Statistics on {os.path.basename(crf)}"
        logFile(log_file, msg); del msg

        arcpy.management.CalculateStatistics(crf, 1, 1, [], "OVERWRITE")
        del crf

        msg = arcpy.GetMessages()
        msg = ">->-> {0}".format(msg.replace('\n', '\n>->-> '))
        logFile(log_file, msg); del msg

        del np
        del mosaicname, mosaictitle, RegionGDB, RegionScratchGDB
        del dataset_product_code, datasetcode, cellsize, distributionprojectcode

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
        return False
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
        return False

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

        return True # everything went well so we return True

# ## Reads from the queue and does work
def mpCreateRasters(dataset):
    """mp Create Biomass Rasters"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        datasetcode             = dataset[0]
        tablename               = dataset[3]
        geographicarea          = dataset[4]
        cellsize                = dataset[5]
        season                  = dataset[9]
        distributionprojectcode = dataset[12]
        summaryproduct          = dataset[14]
        del dataset

        dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

        RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

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

        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

        arcpy.env.cellSize = cellsize

        datasetcode_raster_mask = os.path.join(RegionGDB, f"{tablename}_Raster_Mask")

        # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
        arcpy.env.extent     = arcpy.Describe(datasetcode_raster_mask).extent
        arcpy.env.mask       = datasetcode_raster_mask
        arcpy.env.snapRaster = datasetcode_raster_mask
        del datasetcode_raster_mask

        msg = f'> Generating {tablename} Biomass Rasters'
        logFile(log_file, msg); del msg

        msg = f">-> Make Feature Layer for {datasetcode}_Sample_Locations"
        logFile(log_file, msg); del msg

        # Prepare the points layer
        datasetcode_sample_locations = os.path.join(RegionGDB, f"{datasetcode}_Sample_Locations")
        datasetcode_sample_locations_layer = arcpy.management.MakeFeatureLayer(datasetcode_sample_locations, "Region Sample Locations Layer")
        del datasetcode_sample_locations

        # Add the YearWeights feild
        fields =  [f.name for f in arcpy.ListFields(datasetcode_sample_locations_layer) if f.type not in ['Geometry', 'OID']]
        if "YearWeights" not in fields:
            # Add the YearWeights field to the Dataset. This is used for the IDW modeling later
            arcpy.management.AddField(datasetcode_sample_locations_layer, "YearWeights", "SHORT", field_alias = "Year Weights")
        del fields

        getcount = int(arcpy.management.GetCount(datasetcode_sample_locations_layer)[0])
        msg = f'\t> {datasetcode}_Sample_Locations has {getcount:,d} records'
        logFile(log_file, msg); del msg, getcount

        datasetcode_unique_species = unique_species( datasetcode_sample_locations_layer )
        # print(f"{', '.join(datasetcode_unique_species)}\n")

        # Finally we will start looping of the uniquely identified fish in this csv.
        for datasetcode_unique_specie in datasetcode_unique_species:
            # We prepare a place so that we can place fish data relevant to the fish species we're looking at.
            #print(datasetcode_unique_specie)

            datasetcode_unique_specie_dir = datasetcode_unique_specie.replace('(','').replace(')','').replace('.','')

            msg = f"#---> Creating Raster Files for {datasetcode_unique_specie} in directory: {datasetcode_unique_specie_dir}"
            logFile(log_file, msg); del msg

            # Create a special folder for them
            datasetcode_unique_specie_dir_path = os.path.join(IMAGE_DIRECTORY, dataset_product_code, datasetcode_unique_specie_dir)
            if not os.path.exists( datasetcode_unique_specie_dir_path  ) and not os.path.isdir( datasetcode_unique_specie_dir_path ):
                os.makedirs( datasetcode_unique_specie_dir_path )
            #print(f"\n#-> {datasetcode_unique_specie_dir_path}")
            #print(f"###--->>> {arcpy.ValidateTableName(datasetcode_unique_specie_dir, datasetcode_unique_specie_dir_path)}\n")
            del datasetcode_unique_specie_dir_path

            msg = f"#---> Select from {datasetcode}_Sample_Locations all records for {datasetcode_unique_specie}"
            logFile(log_file, msg); del msg

            # We are pretty much going to set min to 0, max to STD(OVER YEARS)*2+AVG(OVER YEARS), and the other two shouldn't matter, but we'll set those anyways.
            select_by_specie_no_years(datasetcode_sample_locations_layer, datasetcode_unique_specie, log_file)

            msg = f"#---> Get a list of years for the selected species {datasetcode_unique_specie}"
            logFile(log_file, msg); del msg

            # Get all of the unique years
            specie_unique_years = unique_year(datasetcode_sample_locations_layer, datasetcode_unique_specie)

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
                msg =  f"#-----> Processing {datasetcode}_Sample_Locations for {datasetcode_unique_specie} and year: {specie_unique_year}"
                logFile(log_file, msg); del msg

                msg =  f"#-------> Select from {datasetcode}_Sample_Locations all records for {datasetcode_unique_specie} and year {specie_unique_year}"
                logFile(log_file, msg); del msg

                # select the fish species data by the year provided.
                #select_by_specie(datasetcode_sample_locations_layer, datasetcode_unique_specie, str(specie_unique_year), log_file)
                select_by_specie(datasetcode_sample_locations_layer, datasetcode_unique_specie, specie_unique_year, log_file)

                # Calculate YearWeights=3-(abs(Tc-Ti))
                arcpy.management.CalculateField(in_table=datasetcode_sample_locations_layer, field="YearWeights", expression=f"3 - (abs({int(specie_unique_year)} - !Year!))", expression_type="PYTHON", code_block="")

                # Get the count of records for selected species
                getcount = int(arcpy.management.GetCount(datasetcode_sample_locations_layer)[0])
                msg = f"#-------> {datasetcode}_Sample_Locations has {getcount:,d} records for {datasetcode_unique_specie} and year {specie_unique_year}"
                logFile(log_file, msg); del msg, getcount


                # Generate the interpolated Raster file and store it on the local hard drive. Can now be used in other ArcGIS Documents
                # No special character used, replace spaces, '(', ')' '.', '-' with '_' (underscores)
                specie_unique_year_raster = f"{dataset_product_code}_{datasetcode_unique_specie_dir.replace(' ','_')}_{specie_unique_year}"
                #del specie_unique_year

                #tmp_raster = os.path.join(RegionScratchGDB, f"{specie_unique_year_raster.replace('_','')}")
                tmp_raster = os.path.join(ScratchFolder, f"{specie_unique_year_raster.replace('_','')}.tif")

                specie_unique_year_raster_path = os.path.join(IMAGE_DIRECTORY, dataset_product_code, datasetcode_unique_specie_dir, specie_unique_year_raster+".tif")

                if not arcpy.Exists(specie_unique_year_raster_path):

                    msg =  f"#-------> Creating Raster File {specie_unique_year_raster}.tif for {datasetcode_unique_specie}"
                    logFile(log_file, msg); del msg

                    geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
                    # Set the output coordinate system to what is needed for the
                    # DisMAP project
                    psr = arcpy.SpatialReference(geographicarea_sr)
                    arcpy.env.outputCoordinateSystem = psr; del psr
                    del geographicarea_sr

                    if summaryproduct == "Yes":
                        msg =  f"#-------> Image: {specie_unique_year_raster}.tif for {datasetcode_unique_specie}"
                        logFile(log_file, msg); del msg
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

                        # Execute IDW using the selected selected species, years, and MapValue
                        arcpy.IDW_ga(in_features = datasetcode_sample_locations_layer,
                                     z_field = 'MapValue',
                                     out_ga_layer = '',
                                     out_raster = tmp_raster,
                                     cell_size = '',
                                     power = 2,
                                     search_neighborhood = searchNeighbourhood,
                                     weight_field = "YearWeights")

                        del searchNeighbourhood

                        # Check In GeoStats Extension
                        arcpy.CheckInExtension("GeoStats")

                        # Execute Power to convert the raster back to WTCPUE from WTCPUECubeRoot
                        out_cube = arcpy.sa.Power(tmp_raster, 3)
                        #out_cube.save(tmp_raster_power)
                        out_cube.save(specie_unique_year_raster_path)
                        #arcpy.management.Delete(out_cube)
                        del out_cube

                    if summaryproduct == "No":
                        msg =  f"#-------> Image: {specie_unique_year_raster}.tif for {datasetcode_unique_specie}"
                        logFile(log_file, msg); del msg
                        #gsr = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
                        #arcpy.env.outputCoordinateSystem = gsr
                        #del gsr

                        # Set local variables
                        inFeatures     = datasetcode_sample_locations_layer
                        valField       = 'MapValue'
                        #outRaster      = tmp_raster
                        outRaster      = specie_unique_year_raster_path
                        assignmentType = "MEAN"
                        priorityField  = ""
                        cellSize       = cellsize

                        # Run PointToRaster
                        arcpy.conversion.PointToRaster(inFeatures, valField, outRaster,
                                                       assignmentType, priorityField, cellSize)

                        del inFeatures, valField, outRaster, assignmentType, priorityField, cellSize

                del specie_unique_year_raster

                arcpy.management.Delete(tmp_raster)
                del tmp_raster

                del specie_unique_year

                del specie_unique_year_raster_path
                # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
                # The following inputs are layers or table views: "Aleutian_Islands"
                arcpy.management.CalculateField(in_table=datasetcode_sample_locations_layer, field="YearWeights", expression="None", expression_type="PYTHON", code_block="")

            del specie_unique_years, datasetcode_unique_specie, datasetcode_unique_specie_dir

            # Delete after last use

        msg = f'>-> Delete non-required fields from {datasetcode}_Sample_Locations.'
        logFile(log_file, msg); del msg
        arcpy.management.DeleteField(datasetcode_sample_locations_layer, ["YearWeights"])

        # Delete datasetcode_sample_locations_layer
        arcpy.management.Delete(datasetcode_sample_locations_layer)
        del datasetcode_sample_locations_layer

        # Clean up
        del RegionScratchGDB, RegionGDB, tablename, distributionprojectcode
        del datasetcode, cellsize, datasetcode_unique_species
        del geographicarea, season, summaryproduct, dataset_product_code

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
        return False
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
        return False

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

        return True # everything went well so we return True

def mpCreateSampleLocationPoints(dataset):
    """mp Create Region Sample LocationP oints"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        datasetcode             = dataset[0]
        tablename               = dataset[3]
        geographicarea          = dataset[4]
        distributionprojectcode = dataset[12]
        summaryproduct          = dataset[14]
        del dataset

        dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

        RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

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

        msg = f'>-> Creating the {tablename} Sample Locations Dataset'
        logFile(log_file, msg); del msg

        tablename_path = os.path.join(RegionGDB, f"{tablename}")

        # Set the output coordinate system to what is needed for the
        # DisMAP project
        geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
        psr = arcpy.SpatialReference(geographicarea_sr)
        arcpy.env.outputCoordinateSystem = psr

        del geographicarea_sr

        if summaryproduct == "Yes":
            # Set the output coordinate system to what is needed for the
            # DisMAP project
            gsr = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
            x_coord, y_coord = 'Longitude', 'Latitude'
            my_events = arcpy.management.MakeXYEventLayer(tablename_path, x_coord, y_coord, "my_events", gsr, "#")
            del gsr

        elif summaryproduct == "No":
            x_coord, y_coord = 'Easting', 'Northing'
            my_events = arcpy.management.MakeXYEventLayer(tablename_path, x_coord, y_coord, "my_events", psr, "#")

        del x_coord, y_coord, geographicarea
        del tablename_path, psr

        # Input Dataset
        sample_locations = os.path.join(RegionGDB, f"{datasetcode}_Sample_Locations")

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

        msg = f'>-> Adding field index in the {datasetcode}_Sample_Locations Dataset'
        logFile(log_file, msg); del msg

        # Add Attribute Index
        arcpy.management.AddIndex(sample_locations, ['Species', 'CommonName', 'SpeciesCommonName', 'Year'], f"{datasetcode}_SampleLocationsSpeciesIndex", "NON_UNIQUE", "NON_ASCENDING")

        # Get the count of records for selected species
        getcount = int(arcpy.management.GetCount(sample_locations)[0])
        msg = f">-> {datasetcode}_Sample_Locations has {getcount:,d} records"
        logFile(log_file, msg); del msg, getcount

        # Add Metadata
        #addMetadata(sample_locations)

        del sample_locations, dataset_product_code
        del datasetcode, tablename, distributionprojectcode, summaryproduct

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
        return False
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
        return False

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

        return True # everything went well so we return True

# ## Reads from the queue and does work
def mpCreateSpeciesRichnessRasters(dataset):
    """mp Create Core Species Richness Rasters"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        start_time = time()

        import numpy as np

        # For benchmarking.
        #timestr = strftime("%Y%m%d-%H%M%S")
        timestr = strftime('%a %b %d %I %M %S %p', localtime())
        log_file = os.path.join(log_file_folder, f"{function} {timestr}.log")
        del timestr

        # Write a message to the log file
        msg = f"STARTING {function} ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Assigning variables from items in the chosen table list
        datasetcode             = dataset[0]
        geographicarea          = dataset[4]
        cellsize                = dataset[5]
        distributionprojectcode = dataset[12]
        del dataset

        dataset_product_code = f"{datasetcode}_{distributionprojectcode}"
        del datasetcode, distributionprojectcode

        RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

        RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

        # Reset Environments to start fresh
        arcpy.ResetEnvironments()

        arcpy.env.rasterStatistics = u'STATISTICS 1 1'
        arcpy.env.buildStatsAndRATForTempRaster = True

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

        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"

        arcpy.env.cellSize = cellsize

        datasetcode_raster_mask = os.path.join(RegionGDB, f"{dataset_product_code}_Raster_Mask")

        # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
        arcpy.env.extent     = arcpy.Describe(datasetcode_raster_mask).extent
        arcpy.env.mask       = datasetcode_raster_mask
        arcpy.env.snapRaster = datasetcode_raster_mask
        #del datasetcode_raster_mask

        # These are used later to set the rows and columns for a zero numpy array
        rowCount = int(arcpy.management.GetRasterProperties(datasetcode_raster_mask, "ROWCOUNT" ).getOutput(0))
        columnCount = int(arcpy.management.GetRasterProperties(datasetcode_raster_mask, "COLUMNCOUNT" ).getOutput(0))

        # Create Raster from Array
        rasterMask = arcpy.Raster(datasetcode_raster_mask)
        lowerLeft = arcpy.Point(rasterMask.extent.XMin, rasterMask.extent.YMin)
        del rasterMask

        geographicarea_sr = os.path.join(DATASET_SHAPEFILE_DIRECTORY, dataset_product_code, f"{geographicarea}.prj")
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        psr = arcpy.SpatialReference(geographicarea_sr)
        arcpy.env.outputCoordinateSystem = psr; del psr
        del geographicarea_sr, geographicarea

        msg = f'>-> Creating {dataset_product_code} Species Richness Rasters'
        logFile(log_file, msg); del msg

        layerspeciesyearimagename = os.path.join(RegionGDB, "LayerSpeciesYearImageName")

        fields = [f.name for f in arcpy.ListFields(layerspeciesyearimagename) if f.type not in ['Geometry', 'OID']]

        datasetcode_rasters = {}
        with arcpy.da.SearchCursor(layerspeciesyearimagename, fields) as cursor:
            for row in cursor:
                datasetcode             = row[0]
                distributionprojectcode = row[12]
                corespecies             = row[13]
                year                    = row[14]
                image                   = row[19]
                datasetcode_rasters[f"{image}.tif"] = [f"{datasetcode}_{distributionprojectcode}", corespecies, year]
                del row, datasetcode, distributionprojectcode, corespecies, year, image
        del cursor, layerspeciesyearimagename, fields

##        for i in range(len(layerspeciesyearimagename)):
##            datasetcode             = layerspeciesyearimagename[i][0]
##            distributionprojectcode = layerspeciesyearimagename[i][12]
##            corespecies             = layerspeciesyearimagename[i][13]
##            year                    = layerspeciesyearimagename[i][14]
##            image                   = layerspeciesyearimagename[i][19]
##            datasetcode_rasters[f"{image}.tif"] = [f"{datasetcode}_{distributionprojectcode}", corespecies, year]
##            #print(layer, corespecies, year, image)
##            del i, datasetcode, distributionprojectcode, corespecies, year, image

        input_rasters = {}
        input_rasters_path = os.path.join(IMAGE_DIRECTORY, dataset_product_code)

        # Get a list of input_rasters
        walk = arcpy.da.Walk(input_rasters_path, topdown=True, datatype="RasterDataset")
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                if os.path.basename(dirpath) not in ["_Core Species Richness", "_Species Richness",]:
                    imagelist = datasetcode_rasters[filename]
                    imagepath = os.path.join(dirpath, filename)
                    imagelist.append(imagepath)
                    input_rasters[filename] = imagelist
                    del imagelist, imagepath
                del filename
        del walk, dirpath, dirnames, filenames
        del datasetcode_rasters, input_rasters_path

        # Set layercode_species_richness_path
        species_richness = "_Species Richness"
        layercode_species_richness_path = os.path.join(IMAGE_DIRECTORY, dataset_product_code, species_richness)
        layercode_species_richness_scratch_path = os.path.join(ScratchFolder, dataset_product_code, species_richness)
        del species_richness

        arcpy.env.workspace        = layercode_species_richness_path
        arcpy.env.scratchWorkspace = layercode_species_richness_scratch_path
        del layercode_species_richness_scratch_path

        years = sorted(list(set([input_rasters[input_raster][2] for input_raster in input_rasters])))

        msg = f">-> Processing all species"
        logFile(log_file, msg); del msg

        for year in years:

            layercode_year_richness = os.path.join(layercode_species_richness_path, f"{dataset_product_code}_Species_Richness_{year}.tif")

            msg = f">->-> Year: {year}"
            logFile(log_file, msg); del msg

            richnessArray = np.zeros((rowCount, columnCount), dtype='float32', order='C')

            rasters = [r for r in input_rasters if input_rasters[r][2] == year]

            msg = ">->->-> Processing rasters"
            logFile(log_file, msg)
            # For each raster exported, create the Con mask
            for raster in rasters:
                msg = f">->->->-> Processing {raster} raster"
                logFile(log_file, msg); del msg

                in_raster = input_rasters[raster][3]

                rasterArray = arcpy.RasterToNumPyArray(in_raster, nodata_to_value=np.nan)
                rasterArray[rasterArray < 0.0] = np.nan

                rasterArray[rasterArray > 0.0] = 1.0

                #add rasterArray to richnessArray
                richnessArray = np.add(richnessArray, rasterArray) # Can also use: richnessArray + rasterArray
                del rasterArray, in_raster, raster

            msg = ">->->-> Creating Species Richness Raster"
            logFile(log_file, msg)

            # Cast array as float32
            richnessArray = richnessArray.astype('float32')

            # Convert Array to Raster
            richnessArrayRaster = arcpy.NumPyArrayToRaster(richnessArray, lowerLeft, cellsize, cellsize, -3.40282346639e+38) #-3.40282346639e+38
            richnessArrayRaster.save(layercode_year_richness)
            del richnessArrayRaster
            # Add metadata
            arcpy.management.CalculateStatistics(layercode_year_richness)

            del year, layercode_year_richness
            del richnessArray, rasters

        del years, layercode_species_richness_path

            # ###--->>>

        msg = f'>-> Creating {dataset_product_code} Core Species Richness Rasters'
        logFile(log_file, msg); del msg

        # Set layercode_core_species_richness_path
        core_species_richness = "_Core Species Richness"
        layercode_core_species_richness_path = os.path.join(IMAGE_DIRECTORY, dataset_product_code, core_species_richness)
        layercode_core_species_richness_scratch_path = os.path.join(ScratchFolder, dataset_product_code, core_species_richness)
        del core_species_richness

        arcpy.env.workspace        = layercode_core_species_richness_path
        arcpy.env.scratchWorkspace = layercode_core_species_richness_scratch_path
        del layercode_core_species_richness_scratch_path

        years = sorted(list(set([input_rasters[input_raster][2] for input_raster in input_rasters if input_rasters[input_raster][1] == "Yes"])))

        # ###--->>>
        msg = f">-> Processing Core Species"
        logFile(log_file, msg); del msg

        for year in years:

            layercode_year_richness = os.path.join(layercode_core_species_richness_path, f"{dataset_product_code}_Core_Species_Richness_{year}.tif")

            msg = f">->-> Year: {year}"
            logFile(log_file, msg); del msg

            richnessArray = np.zeros((rowCount, columnCount), dtype='float32', order='C')

            rasters = [r for r in input_rasters if input_rasters[r][2] == year and input_rasters[r][1] == "Yes"]

            msg = ">->->-> Processing rasters"
            logFile(log_file, msg)
            # For each raster exported, create the Con mask
            for raster in rasters:
                msg = f">->->->-> Processing {raster} raster"
                logFile(log_file, msg); del msg

                in_raster = input_rasters[raster][3]

                rasterArray = arcpy.RasterToNumPyArray(in_raster, nodata_to_value=np.nan)
                rasterArray[rasterArray < 0.0] = np.nan

                rasterArray[rasterArray > 0.0] = 1.0

                #add rasterArray to richnessArray
                richnessArray = np.add(richnessArray, rasterArray)
                # Can also use: richnessArray + rasterArray
                del rasterArray, in_raster, raster

            msg = ">->->-> Creating Core Species Richness Raster"
            logFile(log_file, msg)

            # Cast array as float32
            richnessArray = richnessArray.astype('float32')

            # Convert Array to Raster
            richnessArrayRaster = arcpy.NumPyArrayToRaster(richnessArray, lowerLeft, cellsize, cellsize, -3.40282346639e+38) #-3.40282346639e+38
            richnessArrayRaster.save(layercode_year_richness)
            del richnessArrayRaster
           # Add metadata
            arcpy.management.CalculateStatistics(layercode_year_richness)

            del year, layercode_year_richness
            del richnessArray, rasters

        del years, layercode_core_species_richness_path

            # Add metadata layerspeciesyearimagename

        del RegionGDB, RegionScratchGDB
        del columnCount, rowCount, lowerLeft
        del datasetcode_raster_mask, input_rasters, np, cellsize
        del dataset_product_code

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
        return False
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
        return False

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

        return True # everything went well so we return True

def mpHandlerCreateDisMapRegions(Sequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        arcpy.SetLogHistory(False)

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

        datasets = generateDatasets()

        fcs = []
        wc = "_Shape.shp"

        for dirpath, dirnames, filenames in arcpy.da.Walk(DATASET_SHAPEFILE_DIRECTORY, datatype="FeatureClass", type="Polygon"):
            for filename in filenames:
                if wc in filename:
                    fcs.append(filename)
                del filename
            del dirpath, dirnames, filenames

        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            datasets = [[r for r in group] for group in datasets if f"{group[3]}{wc}" in fcs]
            del wc, fcs

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        if not datasets:
            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

        arcpy.env.overwriteOutput = True

    # ###--->>> Preprocessing Setup Start

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            msg = f"> Checking if there is a File GDB for region: {datasetcode} and if there is data"
            logFile(log_file, msg); del msg

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch")

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}")

            del RegionGDB, RegionScratchGDB, datasetcode, distributionprojectcode

    # ###--->>> Multiprocessing Start

        if not Sequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            #cpu_num = multiprocessing.cpu_count() - 2
            with multiprocessing.Pool(processes=cpu_num, initializer=init_processes, initargs=(ARCGIS_METADATA_DIRECTORY, BASE_DIRECTORY, CSV_DIRECTORY,
                                                                                               DATASET_SHAPEFILE_DIRECTORY, EXPORT_METADATA_DIRECTORY,
                                                                                               FilterDatasets, IMAGE_DIRECTORY, INPORT_METADATA_DIRECTORY,
                                                                                               LAYER_DIRECTORY, LOG_DIRECTORY, log_file_folder, MOSAIC_DIRECTORY,
                                                                                               PUBLISH_DIRECTORY, ScratchFolder, SoftwareEnvironmentLevel,
                                                                                               field_definitions, table_definitions, selected_species,
                                                                                               FilterSpecies, timezones)) as pool:
            #with multiprocessing.Pool(processes=cpu_num,) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append(datasets[i])
                    del i
                # use the map function of pool to call the function worker()
                res = pool.map(mpCreateDisMapRegions, args)
                # Close and join pools
                pool.close()
                pool.join()

                # If an error has occurred report it 
                failed = res.count(False) # count how many times False appears in the list with the return values
                if failed > 0:
                    print(f"{failed} workers failed!")
                print("Finished multiprocessing!")
                del res, failed
                del pool, args
            #del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if Sequential:
            for i in range(len(datasets)):
                mpCreateDisMapRegions(datasets[i])
                del i

    # ###--->>> Sequentialprocessing End

        del Sequential

    # ###--->>> Postprocessing Start

        arcpy.env.overwriteOutput = True

        arcpy.env.workspace = ProjectGDB

        # Creating the DisMAP Regions Dataset
        msg = f'> Generating DisMAP Region Dataset.'
        logFile(log_file, msg); del msg

        # DisMAP Regions
        dismap_regions = "DisMAP_Regions"

        dismap_regions_path = os.path.join(ProjectGDB, "DisMAP_Regions")
        sp_ref = arcpy.SpatialReference('WGS_1984_Web_Mercator_Auxiliary_Sphere')

        # Execute Create Feature Class
        arcpy.management.CreateFeatureclass(out_path          = ProjectGDB,
                                            out_name          = dismap_regions,
                                            geometry_type     = "POLYLINE",
                                            template          = "",
                                            has_m             = "DISABLED",
                                            has_z             = "DISABLED",
                                            spatial_reference = sp_ref,
                                            config_keyword    = "",
                                            spatial_grid_1    = "0",
                                            spatial_grid_2    = "0",
                                            spatial_grid_3    = "0")
        del sp_ref

        #if not arcpy.Exists(dismap_regions_path):
        tb_fields = [f.name for f in arcpy.ListFields(dismap_regions_path) if f.type not in ['Geometry', 'OID']]
        tb_definition_fields = table_definitions[dismap_regions]
        fields = [f for f in tb_definition_fields if f not in tb_fields]

        addFields(dismap_regions_path, fields, field_definitions)
        del tb_fields, tb_definition_fields, fields

        msg = f'>-> Updating the field aliases for the {os.path.basename(dismap_regions_path)} Feature Class'
        logFile(log_file, msg); del msg

        alterFields(dismap_regions_path)

        del dismap_regions, dismap_regions_path

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End
        arcpy.env.overwriteOutput = True

        # DisMAP Regions
        dismap_regions = "DisMAP_Regions"

        dismap_regions_path = os.path.join(ProjectGDB, "DisMAP_Regions")

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            datasetcode_survey_area   = f"{dataset_product_code}_Survey_Area"
            datasetcode_boundary_line = f"{dataset_product_code}_Boundary_Line"
            datasetcode_raster_mask   = f"{dataset_product_code}_Raster_Mask"

            arcpy.env.workspace = RegionGDB

            msg = f"#-> Copying the {datasetcode_survey_area} and {datasetcode_boundary_line} Datasetes"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(datasetcode_survey_area, os.path.join(ProjectGDB, datasetcode_survey_area))

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(datasetcode_boundary_line, os.path.join(ProjectGDB, datasetcode_boundary_line))

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(datasetcode_raster_mask, os.path.join(ProjectGDB, datasetcode_raster_mask))

            del datasetcode_survey_area, datasetcode_raster_mask

            msg = f">-> Appending the {datasetcode} Dataset to the DisMAP Regions Dataset"
            logFile(log_file, msg); del msg
            # Process: Append
            arcpy.management.Append(inputs = datasetcode_boundary_line,
                                    target = dismap_regions_path,
                                    schema_type="NO_TEST",
                                    field_mapping="",
                                    subtype="")

            # Delete after last use
            del RegionGDB, RegionScratchGDB
            del datasetcode_boundary_line, distributionprojectcode
            del datasetcode, dataset_product_code

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # ##-->> Delete Identical features in DisMAP Regions Start

        msg = f"> Delete Identical features in DisMAP Regions"
        logFile(log_file, msg); del msg
        # Process: arcpy.management.DeleteIdentical
        arcpy.management.DeleteIdentical(in_dataset = dismap_regions_path,
                                         fields = "Shape;Shape_Length;DatasetCode;Region",
                                         xy_tolerance="",
                                         z_tolerance="0")

        # Add Metadata
        #addMetadata(dismap_regions_path)

        # Delete after last use
        del dismap_regions, dismap_regions_path

        # Compacting the ProjectGDB
        compactGDB(ProjectGDB)

        # ##-->> Delete Identical features in DisMAP Regions End

##        # ##-->> Deleting Scratch and Temporary GDB Start
##        for i in range(len(datasets)):
##            datasetcode = datasets[i][0]
##            distributionprojectcode = datasets[i][12]
##            del i
##
##            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"
##
##            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")
##
##            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")
##
##            RegionScratchFolder = os.path.join(ScratchFolder, f"{datasetcode}")
##
##            msg = f"#-> Deleting the {datasetcode} Region GDB"
##            logFile(log_file, msg); del msg
##
##            #purgeGDB(RegionGDB)
##            arcpy.management.Delete(RegionGDB)
##            #shutil.rmtree(RegionGDB)
##
##            msg = f"#-> Deleting the {dataset_product_code} Region Scratch GDB"
##            logFile(log_file, msg); del msg
##
##            #purgeGDB(RegionScratchGDB)
##            arcpy.management.Delete(RegionScratchGDB)
##            #shutil.rmtree(RegionScratchGDB)
##
##            msg = f"#-> Deleting the {dataset_product_code} Region Scratch Folder"
##            logFile(log_file, msg); del msg
##
##            #purgeGDB(RegionScratchGDB)
##            arcpy.management.Delete(RegionScratchFolder)
##            #shutil.rmtree(RegionScratchGDB)
##
##            del RegionGDB, RegionScratchGDB, RegionScratchFolder
##            del datasetcode, dataset_product_code, distributionprojectcode
##        # ##-->> Deleting Scratch and Temporary GDB End

    # ###--->>> Postprocessing End

        del datasets

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def mpHandlerCreateIndicatorsTable(Sequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        arcpy.SetLogHistory(False)

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

        datasets = generateDatasets()

        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            tbs = arcpy.ListTables(f"*")
            datasets = [[r for r in group] for group in datasets if group[3] in tbs and group[3] not in ['', 'Datasets', 'Indicators', 'Species_Filter']]
            del tbs

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        if not datasets:
            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

     # ###--->>> Preprocessing Setup Start
        arcpy.env.overwriteOutput = True

        indicators = "Indicators"
        indicators_table = os.path.join(ProjectGDB, indicators)

        msg = f"Creating the {indicators} Table"
        logFile(log_file, msg); del msg

        arcpy.management.Delete(indicators_table)

        if not arcpy.Exists(indicators_table):
            # Execute CreateTable
            arcpy.management.CreateTable(ProjectGDB, indicators, "", "", "")

            tb_fields = [f.name for f in arcpy.ListFields(indicators_table) if f.type not in ['Geometry', 'OID']]
            tb_definition_fields = table_definitions[indicators]
            fields = [f for f in tb_definition_fields if f not in tb_fields]

            addFields(indicators_table, fields, field_definitions)
            del tb_fields, tb_definition_fields, fields

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            msg = f"> Checking if there is a File GDB for region: {datasetcode} and if there is data"
            logFile(log_file, msg); del msg

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            # Region Raster Mask
            datasetcode_raster_mask = f"{dataset_product_code}_Raster_Mask"

            # Region Bathymetry
            datasetcode_bathymetry = f"{dataset_product_code}_Bathymetry"

            # Region Latitude
            datasetcode_latitude   = f"{dataset_product_code}_Latitude"

            # Region Longitude
            datasetcode_longitude  = f"{dataset_product_code}_Longitude"

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch")
                #arcpy.management.Copy(os.path.join(BathymetryGDB, datasetcode_bathymetry), os.path.join(RegionScratchGDB, datasetcode_bathymetry))

            if not arcpy.Exists(os.path.join(RegionGDB, dataset_product_code)):
                msg = f"\t> Copying the {dataset_product_code}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, dataset_product_code), os.path.join(RegionGDB, dataset_product_code))

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_raster_mask)):
                msg = f"\t> Copying the {datasetcode_raster_mask}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, datasetcode_raster_mask), os.path.join(RegionGDB, datasetcode_raster_mask))

            del datasetcode_raster_mask

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_bathymetry)):
                msg = f"\t> Copying the {datasetcode_bathymetry}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, datasetcode_bathymetry), os.path.join(RegionGDB, datasetcode_bathymetry))

            del datasetcode_bathymetry

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_latitude)):
                msg = f"\t> Copying the {datasetcode_latitude}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, datasetcode_latitude), os.path.join(RegionGDB, datasetcode_latitude))

            del datasetcode_latitude

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_longitude)):
                msg = f"\t> Copying the {datasetcode_longitude}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, datasetcode_longitude), os.path.join(RegionGDB, datasetcode_longitude))

            del datasetcode_longitude

            if not arcpy.Exists(os.path.join(RegionGDB, f"{dataset_product_code}_{indicators}")):
                msg = f"\t> Creating the {dataset_product_code}_{indicators} table"
                logFile(log_file, msg); del msg

                arcpy.management.CreateTable(RegionGDB, f"{dataset_product_code}_{indicators}", os.path.join(ProjectGDB, indicators), "", "")

                #arcpy.management.Copy(os.path.join(ProjectGDB, indicators), os.path.join(RegionGDB, f"{dataset_product_code}_{indicators}"), "", "")

            del RegionGDB, RegionScratchGDB, dataset_product_code, datasetcode
            del distributionprojectcode

        del indicators, indicators_table

    # ###--->>> Preprocessing Setup End

    # ###--->>> Multiprocessing Start

        if not Sequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            #cpu_num = multiprocessing.cpu_count() - 2
            with multiprocessing.Pool(processes=cpu_num, initializer=init_processes, initargs=(ARCGIS_METADATA_DIRECTORY, BASE_DIRECTORY, CSV_DIRECTORY,
                                                                                               DATASET_SHAPEFILE_DIRECTORY, EXPORT_METADATA_DIRECTORY,
                                                                                               FilterDatasets, IMAGE_DIRECTORY, INPORT_METADATA_DIRECTORY,
                                                                                               LAYER_DIRECTORY, LOG_DIRECTORY, log_file_folder, MOSAIC_DIRECTORY,
                                                                                               PUBLISH_DIRECTORY, ScratchFolder, SoftwareEnvironmentLevel,
                                                                                               field_definitions, table_definitions, selected_species,
                                                                                               FilterSpecies, timezones)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append(datasets[i])
                    del i
                # use the map function of pool to call the function worker()
                res = pool.map(mpCreateIndicatorsTable, args)
                # Close and join pools
                pool.close()
                pool.join()

                # If an error has occurred report it 
                failed = res.count(False) # count how many times False appears in the list with the return values
                if failed > 0:
                    print(f"{failed} workers failed!")
                print("Finished multiprocessing!")
                del res, failed
                del pool, args
            #del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if Sequential:
            for i in range(len(datasets)):
                mpCreateIndicatorsTable(datasets[i])
                del i

    # ###--->>> Sequentialprocessing End

        del Sequential

    # ###--->>> Postprocessing Start

        arcpy.env.overwriteOutput = True

        indicators = "Indicators"
        indicators_table = os.path.join(ProjectGDB, indicators)

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            msg = f"#-> Copying the {datasetcode} Indicators Table"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            datasetcode_indicators = os.path.join(RegionGDB, f"{dataset_product_code}_Indicators")
            arcpy.management.Copy(datasetcode_indicators, os.path.join(ProjectGDB, f"{dataset_product_code}_Indicators"))
            # Append Region Indicators to Indicators Table
            arcpy.management.Append(inputs=datasetcode_indicators, target=indicators_table, schema_type="TEST", field_mapping="", subtype="")
            del datasetcode_indicators

            del RegionGDB, dataset_product_code, datasetcode, distributionprojectcode

        # This gets a list of fields in the table
        fields = [f.name for f in arcpy.ListFields(indicators_table) if f.type not in ['Geometry', 'OID']]

        # Remove Identical Records
        arcpy.management.DeleteIdentical(in_dataset=indicators_table, fields=fields, xy_tolerance="", z_tolerance="0")
        msg = arcpy.GetMessages()
        msg = ">-> {0}\n".format(msg.replace('\n', '\n>-> '))
        logFile(log_file, msg); del msg
        del fields

        del indicators, indicators_table

        compactGDB(ProjectGDB)

        # ##-->> Copying Output End

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {dataset_product_code} Region GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {dataset_product_code} Region Scratch GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del datasetcode, dataset_product_code, distributionprojectcode

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
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def mpHandlerCreateLayerBathymetry(Sequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        arcpy.SetLogHistory(False)

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

        datasets = generateDatasets()

        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            wc = f"_Fishnet"
            fcs = arcpy.ListFeatureClasses(f"*{wc}")
            datasets = [[r for r in group] for group in datasets if f"{group[3]}{wc}" in fcs]
            del fcs, wc

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        if not datasets:
            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

        arcpy.env.overwriteOutput = True

    # ###--->>> Preprocessing Setup Start

        for i in range(len(datasets)):
            datasetcode = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            msg = f"> Checking if there is a File GDB for region: {datasetcode} and if there is data"
            logFile(log_file, msg); del msg

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            # Layr Raster Mask
            datasetcode_raster_mask = f"{dataset_product_code}_Raster_Mask"

            # Region Fishnet
            datasetcode_fishnet = f"{dataset_product_code}_Fishnet"

            # Region Bathymetry
            datasetcode_bathymetry = f"{dataset_product_code}_Bathymetry"

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch")

            del dataset_product_code

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_raster_mask)):
                msg = f"\t> Copying the {datasetcode_raster_mask}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, datasetcode_raster_mask), os.path.join(RegionGDB, datasetcode_raster_mask))

            del datasetcode_raster_mask

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_fishnet)):
                msg = f"\t> Copying the {datasetcode_fishnet}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, datasetcode_fishnet), os.path.join(RegionGDB, datasetcode_fishnet))

            del datasetcode_fishnet

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_bathymetry)):
                msg = f"\t> Copying the {datasetcode_bathymetry}"
                logFile(log_file, msg); del msg
                arcpy.management.Copy(os.path.join(BathymetryGDB, datasetcode_bathymetry), os.path.join(RegionScratchGDB, datasetcode_bathymetry))

            del datasetcode_bathymetry

            del RegionGDB, RegionScratchGDB

    # ###--->>> Multiprocessing Start

        if not Sequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            #cpu_num = multiprocessing.cpu_count() - 2
            with multiprocessing.Pool(processes=cpu_num, initializer=init_processes, initargs=(ARCGIS_METADATA_DIRECTORY, BASE_DIRECTORY, CSV_DIRECTORY,
                                                                                               DATASET_SHAPEFILE_DIRECTORY, EXPORT_METADATA_DIRECTORY,
                                                                                               FilterDatasets, IMAGE_DIRECTORY, INPORT_METADATA_DIRECTORY,
                                                                                               LAYER_DIRECTORY, LOG_DIRECTORY, log_file_folder, MOSAIC_DIRECTORY,
                                                                                               PUBLISH_DIRECTORY, ScratchFolder, SoftwareEnvironmentLevel,
                                                                                               field_definitions, table_definitions, selected_species,
                                                                                               FilterSpecies, timezones)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append(datasets[i])
                    del i
                # use the map function of pool to call the function worker()
                #pool.map(mpCreateLayerBathymetry, args)
                res = pool.map(mpCreateLayerBathymetry, args)
                # Close and join pools
                pool.close()
                pool.join()

                # If an error has occurred report it 
                failed = res.count(False) # count how many times False appears in the list with the return values
                if failed > 0:
                    print(f"{failed} workers failed!")
                print("Finished multiprocessing!")
                del res, failed
                del pool, args
            #del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if Sequential:
            for i in range(len(datasets)):
                mpCreateLayerBathymetry(datasets[i])
                del i

        del Sequential

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB Start
        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            datasetcode = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            datasetcode_bathymetry = f"{dataset_product_code}_Bathymetry"

            msg = f"#-> Copying the {dataset_product_code}"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(datasetcode_bathymetry, os.path.join(ProjectGDB, datasetcode_bathymetry))

            del datasetcode_bathymetry, dataset_product_code, distributionprojectcode

            del RegionGDB, RegionScratchGDB
            del datasetcode

        compactGDB(ProjectGDB)

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            datasetcode = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {dataset_product_code} Region GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {dataset_product_code} Region Scratch GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del dataset_product_code, datasetcode, distributionprojectcode
        # ##-->> Deleting Scratch and Temporary GDB End

    # ###--->>> Postprocessing End

        del datasets

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def mpHandlerCreateLayerFishnets(Sequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        arcpy.SetLogHistory(False)

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

        datasets = generateDatasets()

        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            wc = "_Survey_Area"
            fcs = arcpy.ListFeatureClasses(f"*{wc}")
            datasets = [[r for r in group] for group in datasets if f"{group[3]}{wc}" in fcs]
            del wc, fcs

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        if not datasets:
            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

        arcpy.env.overwriteOutput = True

    # ###--->>> Preprocessing Setup Start

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            msg = f"> Checking if there is a File GDB for region: {datasetcode} and if there is data"
            logFile(log_file, msg); del msg

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            # Region Survey Area
            datasetcode_survey_area = f"{dataset_product_code}_Survey_Area"
            datasetcode_raster_mask = f"{dataset_product_code}_Raster_Mask"

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch")

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}")

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_survey_area)):
                msg = f"\t> Copying the {datasetcode_survey_area}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, datasetcode_survey_area), os.path.join(RegionGDB, datasetcode_survey_area))

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_raster_mask)):
                msg = f"\t> Copying the {datasetcode_raster_mask}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, datasetcode_raster_mask), os.path.join(RegionGDB, datasetcode_raster_mask))

            del datasetcode_survey_area, datasetcode_raster_mask

            del RegionGDB, RegionScratchGDB

    # ###--->>> Multiprocessing Start

        if not Sequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            #cpu_num = multiprocessing.cpu_count() - 2
            with multiprocessing.Pool(processes=cpu_num, initializer=init_processes, initargs=(ARCGIS_METADATA_DIRECTORY, BASE_DIRECTORY, CSV_DIRECTORY,
                                                                                               DATASET_SHAPEFILE_DIRECTORY, EXPORT_METADATA_DIRECTORY,
                                                                                               FilterDatasets, IMAGE_DIRECTORY, INPORT_METADATA_DIRECTORY,
                                                                                               LAYER_DIRECTORY, LOG_DIRECTORY, log_file_folder, MOSAIC_DIRECTORY,
                                                                                               PUBLISH_DIRECTORY, ScratchFolder, SoftwareEnvironmentLevel,
                                                                                               field_definitions, table_definitions, selected_species,
                                                                                               FilterSpecies, timezones)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append(datasets[i])
                    del i
                # use the map function of pool to call the function worker()
                res = pool.map(mpCreateLayerFishnets, args)
                # Close and join pools
                pool.close()
                pool.join()
                #res = pool.starmap(mpCreateLayerFishnets, args) # run jobs in job list; res is a list with return values of the worker function
                # If an error has occurred report it 
                failed = res.count(False) # count how many times False appears in the list with the return values
                if failed > 0:
                    print(f"{failed} workers failed!")
                print("Finished multiprocessing!")
                del res, failed
                del pool, args
            #del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if Sequential:
            for i in range(len(datasets)):
                mpCreateLayerFishnets(datasets[i])
                del i

        #del Sequential

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        # ##-->> Adding geometry attributes Start
        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            cellsize                = datasets[i][5]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            datasetcode_lat_long    = f"{dataset_product_code}_Lat_Long"
            datasetcode_points      = f"{dataset_product_code}_Points"
            datasetcode_raster_mask = f"{dataset_product_code}_Raster_Mask"

            arcpy.env.workspace        = RegionGDB
            arcpy.env.scratchWorkspace = RegionScratchGDB
            arcpy.env.cellSize         = cellsize
            arcpy.env.extent           = arcpy.Describe(datasetcode_raster_mask).extent
            arcpy.env.mask             = datasetcode_raster_mask
            arcpy.env.snapRaster       = datasetcode_raster_mask
            del cellsize, datasetcode_raster_mask

            msg = f"#-> Adding geometry attributes"
            logFile(log_file, msg); del msg

            gsr = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"

            msg = f"\tAdding Latitude and Longitude values to {datasetcode_points}"
            logFile(log_file, msg); del msg
            # Add DD to points
            # File GDB Workspace
            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.CalculateGeometryAttributes(datasetcode_points, "Longitude POINT_X;Latitude POINT_Y", '', '', gsr, "DD")
                #print(arcpy.GetMessages())

            msg = f"\tAdding DMS values to {dataset_product_code}_Points"
            logFile(log_file, msg); del msg
            # Add DMS to points
            # File GDB Workspace
            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.CalculateGeometryAttributes(datasetcode_points, "DMSLong POINT_X;DMSLat POINT_Y", '', '', gsr, "DMS_DIR_LAST")
                #print(arcpy.GetMessages())

            fields = ['DMSLat', 'DMSLong',]

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                # Create update cursor for Dataset
                with arcpy.da.UpdateCursor(datasetcode_points, fields) as cursor:
                    for row in cursor:
                        row[0] = row[0][:][:-14] + str(round(float(row[0][-14:-7]),1)) + row[0][-3:]
                        row[1] = row[1][:][:-14] + str(round(float(row[1][-14:-7]),1)) + row[1][-3:]
                        cursor.updateRow(row)
                        del row
                del fields, cursor

            msg = f"\tAdding Latitude and Longitude values to {datasetcode_lat_long}"
            logFile(log_file, msg); del msg
            # Add DD to points
            # File GDB Workspace
            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.CalculateGeometryAttributes(datasetcode_lat_long, "Longitude POINT_X;Latitude POINT_Y", '', '', gsr, "DD")
                #print(arcpy.GetMessages())

            del RegionGDB, RegionScratchGDB
            del dataset_product_code, datasetcode_points, datasetcode_lat_long, gsr
            del datasetcode, distributionprojectcode

        # ##-->> Adding geometry attributes End

    # ###--->>> Multiprocessing Start

        if not Sequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            #cpu_num = multiprocessing.cpu_count() - 2
            with multiprocessing.Pool(processes=cpu_num, initializer=init_processes, initargs=(ARCGIS_METADATA_DIRECTORY, BASE_DIRECTORY, CSV_DIRECTORY,
                                                                                   DATASET_SHAPEFILE_DIRECTORY, EXPORT_METADATA_DIRECTORY,
                                                                                   FilterDatasets, IMAGE_DIRECTORY, INPORT_METADATA_DIRECTORY,
                                                                                   LAYER_DIRECTORY, LOG_DIRECTORY, log_file_folder, MOSAIC_DIRECTORY,
                                                                                   PUBLISH_DIRECTORY, ScratchFolder, SoftwareEnvironmentLevel,
                                                                                   field_definitions, table_definitions, selected_species,
                                                                                   FilterSpecies, timezones)) as pool:
            #cpu_num = cpu_count()
            #with multiprocessing.Pool(processes=cpu_num, ) as pool:
            #with multiprocessing.Pool(len(datasets)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append(datasets[i])
                    del i
                # use the map function of pool to call the function worker()
                res = pool.map(mpCreateLatitudeLongitudeRasters, args)
                # Close and join pools
                pool.close()
                pool.join()
                #res = pool.starmap(mpCreateLayerFishnets, args) # run jobs in job list; res is a list with return values of the worker function
                # If an error has occurred report it 
                failed = res.count(False) # count how many times False appears in the list with the return values
                if failed > 0:
                    print(f"{failed} workers failed!")
                print("Finished multiprocessing!")
                del res, failed
                del pool, args
            #del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if Sequential:
            for i in range(len(datasets)):
                mpCreateLatitudeLongitudeRasters(datasets[i])
                del i

        del Sequential

    # ###--->>> Sequentialprocessing End

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB Start

        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            msg = f"#-> Copying the {dataset_product_code}_Points, {dataset_product_code}_Lat_Long, and {dataset_product_code}_Fishnet Datasetes"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            datasetcode_fishnet     = f"{dataset_product_code}_Fishnet"
            datasetcode_lat_long    = f"{dataset_product_code}_Lat_Long"
            datasetcode_latitude    = f"{dataset_product_code}_Latitude"
            datasetcode_longitude   = f"{dataset_product_code}_Longitude"
            datasetcode_points      = f"{dataset_product_code}_Points"

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(datasetcode_fishnet, os.path.join(ProjectGDB, datasetcode_fishnet))

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(datasetcode_lat_long, os.path.join(ProjectGDB, datasetcode_lat_long))

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(datasetcode_latitude, os.path.join(ProjectGDB, datasetcode_latitude))

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(datasetcode_longitude, os.path.join(ProjectGDB, datasetcode_longitude))

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(datasetcode_points, os.path.join(ProjectGDB, datasetcode_points))

            del RegionGDB, RegionScratchGDB
            del datasetcode_fishnet, datasetcode_lat_long
            del datasetcode_latitude, datasetcode_longitude, datasetcode_points
            del datasetcode, distributionprojectcode

        # Compacting the ProjectGDB
        compactGDB(ProjectGDB)

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            datasetcode = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {dataset_product_code} Region GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {dataset_product_code} Region Scratch GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del dataset_product_code, datasetcode, distributionprojectcode
        # ##-->> Deleting Scratch and Temporary GDB End

    # ###--->>> Postprocessing End

        del datasets

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def mpHandlerCreateLayerSpeciesYearImageName(Sequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        arcpy.SetLogHistory(False)

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

        datasets = generateDatasets()

        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            tbs = arcpy.ListTables(f"*")
            datasets = [[r for r in group] for group in datasets if group[3] in tbs and group[3] not in ['Datasets', 'DisMAP_Regions', 'Indicators', 'Species_Filter']]
            del tbs

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        if not datasets:
            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

    # ###--->>> Preprocessing Setup Start

        arcpy.env.overwriteOutput = True

        # Region Species Year Image Name Table
        layerspeciesyearimagename = "LayerSpeciesYearImageName"

        msg = f"Creating the {layerspeciesyearimagename} Table"
        logFile(log_file, msg); del msg

        layerspeciesyearimagename_table = os.path.join(ProjectGDB, layerspeciesyearimagename)

        ReplaceLayerSpeciesYearImageName = True
        if not arcpy.Exists(layerspeciesyearimagename_table) or ReplaceLayerSpeciesYearImageName:

            # Execute CreateTable
            arcpy.management.CreateTable(ProjectGDB, layerspeciesyearimagename, "", "", "")

            tb_fields = [f.name for f in arcpy.ListFields(layerspeciesyearimagename_table) if f.type not in ['Geometry', 'OID']]
            tb_definition_fields = table_definitions[layerspeciesyearimagename]
            fields = [f for f in tb_definition_fields if f not in tb_fields]

            addFields(layerspeciesyearimagename_table, fields, field_definitions)
            del tb_fields, tb_definition_fields, fields

            msg = f'>-> Updating the field aliases for the {os.path.basename(layerspeciesyearimagename_table)} Table'
            logFile(log_file, msg); del msg

        del ReplaceLayerSpeciesYearImageName

        xml_file = os.path.join(BASE_DIRECTORY, f"{layerspeciesyearimagename}.xml")

        #arcpy.management.ExportXMLWorkspaceDocument(in_data, out_file, {export_type}, {storage_type}, {export_metadata})
        arcpy.management.ExportXMLWorkspaceDocument(in_data=layerspeciesyearimagename_table,
                                                    out_file=xml_file,
                                                    export_type= "SCHEMA_ONLY",
                                                    storage_type="NORMALIZED",
                                                    export_metadata="NO_METADATA")
        del layerspeciesyearimagename_table

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            tablename               = datasets[i][3]
            distributionprojectcode = datasets[i][12]
            filtersubregion         = datasets[i][16]
            del i

            layerspeciesyearimagename = "LayerSpeciesYearImageName"

            msg = f"> Checking if there is a File GDB for region: {tablename} and if there is data"
            logFile(log_file, msg); del msg

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch")

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}")

            msg = f"\t> Copying the {tablename}"
            logFile(log_file, msg); del msg

            arcpy.management.Copy(os.path.join(ProjectGDB, tablename), os.path.join(RegionGDB, tablename))

            msg = f"\t> Importing XML schema for {layerspeciesyearimagename}"
            logFile(log_file, msg); del msg

            #arcpy.management.ImportXMLWorkspaceDocument(target_geodatabase, in_file, {import_type}, {config_keyword})
            arcpy.management.ImportXMLWorkspaceDocument(target_geodatabase=RegionGDB,
                                                        in_file=xml_file,
                                                        import_type="SCHEMA_ONLY",
                                                        config_keyword="DEFAULTS",
                                                       )
            species_filter_table = os.path.join(ProjectGDB, "Species_Filter")
            msg = f"\t> Creating Table View: {os.path.basename(species_filter_table)}"
            logFile(log_file, msg); del msg
            tableview = arcpy.management.MakeTableView(species_filter_table, "table view", f"FilterSubRegion = '{filtersubregion}'", RegionGDB)
            arcpy.management.CopyRows(tableview, os.path.join(RegionGDB, "Species_Filter"))
            arcpy.management.Delete(tableview)
            del tableview, species_filter_table, filtersubregion

            del RegionGDB, RegionScratchGDB, tablename
            del dataset_product_code, datasetcode, distributionprojectcode
            del layerspeciesyearimagename

        arcpy.management.Delete(xml_file)

        del xml_file

    # ###--->>> Multiprocessing Start

        if not Sequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            #cpu_num = multiprocessing.cpu_count() - 2
            with multiprocessing.Pool(processes=cpu_num, initializer=init_processes, initargs=(ARCGIS_METADATA_DIRECTORY, BASE_DIRECTORY, CSV_DIRECTORY,
                                                                                               DATASET_SHAPEFILE_DIRECTORY, EXPORT_METADATA_DIRECTORY,
                                                                                               FilterDatasets, IMAGE_DIRECTORY, INPORT_METADATA_DIRECTORY,
                                                                                               LAYER_DIRECTORY, LOG_DIRECTORY, log_file_folder, MOSAIC_DIRECTORY,
                                                                                               PUBLISH_DIRECTORY, ScratchFolder, SoftwareEnvironmentLevel,
                                                                                               field_definitions, table_definitions, selected_species,
                                                                                               FilterSpecies, timezones)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append(datasets[i])
                    del i
                # use the map function of pool to call the function worker()
                res = pool.map(mpCreateLayerSpeciesYearImageName, args)
                # Close and join pools
                pool.close()
                pool.join()

                # If an error has occurred report it 
                failed = res.count(False) # count how many times False appears in the list with the return values
                if failed > 0:
                    print(f"{failed} workers failed!")
                print("Finished multiprocessing!")
                del res, failed
                del pool, args
            #del cpu_num
    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if Sequential:
            for i in range(len(datasets)):
                mpCreateLayerSpeciesYearImageName(datasets[i])
                del i

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End
        arcpy.env.overwriteOutput = True

        # Region Species Year Image Name Table
        layerspeciesyearimagename = "LayerSpeciesYearImageName"
        layerspeciesyearimagename_table = os.path.join(ProjectGDB, layerspeciesyearimagename)

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            tablename               = datasets[i][3]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f'\t\t> Append {datasetcode}: {layerspeciesyearimagename} to {layerspeciesyearimagename} table'
            logFile(log_file, msg); del msg

            arcpy.management.Append(inputs = os.path.join(RegionGDB, layerspeciesyearimagename), target = layerspeciesyearimagename_table, schema_type="NO_TEST", field_mapping="", subtype="")
            #msg = arcpy.GetMessages().replace('\n', '\n\t\t ')
            #logFile(log_file, msg); del msg

            del RegionGDB, RegionScratchGDB, tablename
            del dataset_product_code, datasetcode, distributionprojectcode

        msg = f"> Delete Identical records in {os.path.basename(layerspeciesyearimagename_table)}"
        logFile(log_file, msg); del msg
        # Process: arcpy.management.DeleteIdentical
        arcpy.management.DeleteIdentical(in_dataset = layerspeciesyearimagename_table,
                                         fields = ";".join([f.name for f in arcpy.ListFields(layerspeciesyearimagename_table) if f.type not in ['Geometry', 'OID']]),
                                         xy_tolerance="",
                                         z_tolerance="0")

        # Alter Field Alias
        alterFields(layerspeciesyearimagename_table)

        # Add Metadata
        #addMetadata(layerspeciesyearimagename_table)

        CalculateSummaryTables = True
        if CalculateSummaryTables:
            arcpy.env.overwriteOutput = True

            #  Master Species Information
            msg = f'\t> Statistics Analysis: {os.path.basename(layerspeciesyearimagename_table)} table for Master Species Information'
            logFile(log_file, msg); del msg

            arcpy.env.scratchWorkspace = ScratchGDB
            arcpy.env.workspace = ProjectGDB

            arcpy.analysis.Statistics(in_table=layerspeciesyearimagename_table, out_table="_MasterSpeciesInformation", statistics_fields="Species COUNT", case_field="Species;CommonName;SpeciesCommonName;CommonNameSpecies;TaxonomicGroup")

            arcpy.management.DeleteField(in_table="_MasterSpeciesInformation", drop_field="FREQUENCY;COUNT_Species")

            fields = [f.name for f in arcpy.ListFields("_MasterSpeciesInformation") if f.type not in ['Geometry', 'OID']]
            #print(fields)
            # UpdateCursor (in_table, field_names, {where_clause}, {spatial_reference}, {explode_to_points}, {sql_clause}, {datum_transformation}, {explicit})
            with arcpy.da.UpdateCursor(in_table="_MasterSpeciesInformation", field_names=fields, where_clause="Species IS NULL") as cursor:
                for row in cursor:
                    cursor.deleteRow()
                    del row
            del cursor, fields

            msg = f'\t\t> Export Table to create _MasterSpeciesInformation{SoftwareEnvironmentLevel}.csv Table'
            logFile(log_file, msg); del msg
            # Create Tab delimited file
            # Run ExportTable
            #arcpy.conversion.ExportTable(in_table, in_table, {where_clause}, use_field_alias_as_name, {field_mapping}, {sort_field})
            arcpy.conversion.ExportTable(in_table="_MasterSpeciesInformation", out_table= os.path.join(CSV_DIRECTORY, f"_MasterSpeciesInformation{SoftwareEnvironmentLevel}.csv"), where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")

            ReplaceTable = False
            if ReplaceTable:
                #arcpy.conversion.ExportTable(in_table="_MasterSpeciesInformation", out_table= os.path.join(CSV_DIRECTORY, f"MasterSpeciesInformation.tab"), where_clause="Species IS NOT NULL", use_field_alias_as_name = "NOT_USE_ALIAS")
                arcpy.conversion.ExportTable(in_table="_MasterSpeciesInformation", out_table= os.path.join(CSV_DIRECTORY, f"MasterSpeciesInformation.csv"), where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")
            del ReplaceTable

            # Species Filter
            msg = f'\t> Statistics Analysis: {os.path.basename(layerspeciesyearimagename_table)} table for Species Filter'
            logFile(log_file, msg); del msg

            arcpy.analysis.Statistics(in_table=layerspeciesyearimagename_table, out_table="_Species_Filter", statistics_fields="Species COUNT", case_field="DatasetCode;Species;CommonName;TaxonomicGroup;Region;FilterRegion;FilterSubRegion;ManagementBody;ManagementPlan")

            arcpy.management.DeleteField(in_table="_Species_Filter", drop_field="FREQUENCY;COUNT_Species")

            fields = [f.name for f in arcpy.ListFields("_Species_Filter") if f.type not in ['Geometry', 'OID']]
            # UpdateCursor (in_table, field_names, {where_clause}, {spatial_reference}, {explode_to_points}, {sql_clause}, {datum_transformation}, {explicit})
            with arcpy.da.UpdateCursor(in_table="_Species_Filter", field_names=fields, where_clause="Species IS NULL") as cursor:
                for row in cursor:
                    cursor.deleteRow()
                    del row
            del cursor, fields

            msg = f'\t\t> Export Table to create _Species_Filter{SoftwareEnvironmentLevel}.csv Table'
            logFile(log_file, msg); del msg
            #  Create Tab delimited file
            #arcpy.conversion.ExportTable(in_table="_Species_Filter", out_table= os.path.join(CSV_DIRECTORY, f"_Species_Filter{SoftwareEnvironmentLevel}.tab"), where_clause="Species IS NOT NULL", use_field_alias_as_name = "NOT_USE_ALIAS")
            arcpy.conversion.ExportTable(in_table="_Species_Filter", out_table= os.path.join(CSV_DIRECTORY, f"_Species_Filter{SoftwareEnvironmentLevel}.csv"), where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")

            ReplaceTable = False
            if ReplaceTable:
                #arcpy.conversion.ExportTable(in_table="_Species_Filter", out_table= os.path.join(CSV_DIRECTORY, f"Species_Filter.tab"), where_clause="Species IS NOT NULL", use_field_alias_as_name = "NOT_USE_ALIAS")
                arcpy.conversion.ExportTable(in_table="_Species_Filter", out_table= os.path.join(CSV_DIRECTORY, f"Species_Filter.csv"), where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")
            del ReplaceTable

            # Core Species
            msg = f'\t> Statistics Analysis: {os.path.basename(layerspeciesyearimagename_table)} table for Core Species'
            logFile(log_file, msg); del msg

            arcpy.analysis.Statistics(in_table=layerspeciesyearimagename_table, out_table="_CoreSpecies", statistics_fields="Species COUNT", case_field="DatasetCode;Region;Species;CommonName;CoreSpecies")

            arcpy.management.DeleteField(in_table="_CoreSpecies", drop_field="FREQUENCY;COUNT_Species")

            fields = [f.name for f in arcpy.ListFields("_CoreSpecies") if f.type not in ['Geometry', 'OID']]
            # UpdateCursor (in_table, field_names, {where_clause}, {spatial_reference}, {explode_to_points}, {sql_clause}, {datum_transformation}, {explicit})
            with arcpy.da.UpdateCursor(in_table="_CoreSpecies", field_names=fields, where_clause="Species IS NULL") as cursor:
                for row in cursor:
                    cursor.deleteRow()
                    del row
            del cursor, fields

            msg = f'\t\t> Export Table to create _CoreSpecies{SoftwareEnvironmentLevel}.csv Table'
            logFile(log_file, msg); del msg
            # Create Tab file
            #arcpy.conversion.ExportTable(in_table="_CoreSpecies", out_table= os.path.join(CSV_DIRECTORY, f"_CoreSpecies{SoftwareEnvironmentLevel}.tab"), where_clause="Species IS NOT NULL", use_field_alias_as_name = "NOT_USE_ALIAS")
            arcpy.conversion.ExportTable(in_table="_CoreSpecies", out_table= os.path.join(CSV_DIRECTORY, f"_CoreSpecies{SoftwareEnvironmentLevel}.csv"), where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")

        del CalculateSummaryTables

        del layerspeciesyearimagename_table, layerspeciesyearimagename

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # Compacting the ProjectGDB
        compactGDB(ProjectGDB)

        # ##-->> Deleting Scratch and Temporary GDB Start
        datasets = generateDatasets()

        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            tbs = arcpy.ListTables(f"*")
            datasets = [[r for r in group] for group in datasets if group[3] in tbs and group[3] not in ['Datasets', 'DisMAP_Regions', 'Indicators', 'Species_Filter']]
            del tbs

        for i in range(len(datasets)):
            datasetcode = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {datasetcode} Region GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {datasetcode} Region Scratch GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del datasetcode, distributionprojectcode, dataset_product_code
        # ##-->> Deleting Scratch and Temporary GDB End

        del datasets
    # ###--->>> Postprocessing End

        del Sequential

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def mpHandlerCreateLayerTables(Sequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        arcpy.SetLogHistory(False)

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

        datasets = generateDatasets()

        datasets = [[r for r in group] for group in datasets if group[0] not in ['Datasets', 'DisMAP_Regions', 'Indicators', 'Species_Filter']]

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        with arcpy.EnvManager(scratchWorkspace = ScratchFolder, workspace = CSV_DIRECTORY):
            csv_files = arcpy.ListFiles(f"*.csv")
            datasets = [[r for r in group] for group in datasets if group[1] in csv_files]
            del csv_files

        if not datasets:
            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

    # ###--->>> Preprocessing Setup Start

        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            tablename               = datasets[i][3]
            distributionprojectcode = datasets[i][12]
            del i

            msg = f"> Checking if there is a File GDB for region: {datasetcode} and if there is data"
            logFile(log_file, msg); del msg

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch")

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}")

            # Execute CreateTable
            arcpy.management.CreateTable(ProjectGDB, tablename, "", "", "")

            dataset_product_code_table = os.path.join(ProjectGDB, tablename)

            ReplaceDatasetTable = True
            if not arcpy.Exists(dataset_product_code_table) or ReplaceDatasetTable:
                tb_fields = [f.name for f in arcpy.ListFields(dataset_product_code_table) if f.type not in ['Geometry', 'OID']]
                # Distribution Project Codes: IDW, GLMME
                tb_definition = f"{distributionprojectcode}_Data"
                tb_definition_fields = table_definitions[tb_definition]
                fields = [f for f in tb_definition_fields if f not in tb_fields]

                addFields(dataset_product_code_table, fields, field_definitions)
                del tb_fields, tb_definition_fields, fields, tb_definition

                #msg = f'>-> Updating the field aliases for the {os.path.basename(dataset_product_code_table)} Table'
                #logFile(log_file, msg); del msg
                #alterFields(dataset_product_code_table)
            del ReplaceDatasetTable

            xml_file = os.path.join(BASE_DIRECTORY, f"{tablename}.xml")

            #arcpy.management.ExportXMLWorkspaceDocument(in_data, out_file, {export_type}, {storage_type}, {export_metadata})
            arcpy.management.ExportXMLWorkspaceDocument(in_data=dataset_product_code_table,
                                                        out_file=xml_file,
                                                        export_type= "SCHEMA_ONLY",
                                                        storage_type="NORMALIZED",
                                                        export_metadata="NO_METADATA")

            msg = f"\t> Importing XML schema for {tablename}"
            logFile(log_file, msg); del msg

            #arcpy.management.ImportXMLWorkspaceDocument(target_geodatabase, in_file, {import_type}, {config_keyword})
            arcpy.management.ImportXMLWorkspaceDocument(target_geodatabase=RegionGDB,
                                                        in_file=xml_file,
                                                        import_type="SCHEMA_ONLY",
                                                        config_keyword="DEFAULTS",
                                                       )

            arcpy.management.Delete(xml_file)

            del xml_file, dataset_product_code_table
            del RegionGDB, RegionScratchGDB
            del datasetcode, tablename, distributionprojectcode

    # ###--->>> Multiprocessing Start

        if not Sequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            #cpu_num = multiprocessing.cpu_count() - 2
            with multiprocessing.Pool(processes=cpu_num, initializer=init_processes, initargs=(ARCGIS_METADATA_DIRECTORY, BASE_DIRECTORY, CSV_DIRECTORY,
                                                                                               DATASET_SHAPEFILE_DIRECTORY, EXPORT_METADATA_DIRECTORY,
                                                                                               FilterDatasets, IMAGE_DIRECTORY, INPORT_METADATA_DIRECTORY,
                                                                                               LAYER_DIRECTORY, LOG_DIRECTORY, log_file_folder, MOSAIC_DIRECTORY,
                                                                                               PUBLISH_DIRECTORY, ScratchFolder, SoftwareEnvironmentLevel,
                                                                                               field_definitions, table_definitions, selected_species,
                                                                                               FilterSpecies, timezones)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append(datasets[i])
                    del i
                # use the map function of pool to call the function worker()
                res = pool.map(mpCreateLayerTables, args)
                # Close and join pools
                pool.close()
                pool.join()

                # If an error has occurred report it 
                failed = res.count(False) # count how many times False appears in the list with the return values
                if failed > 0:
                    print(f"{failed} workers failed!")
                print("Finished multiprocessing!")
                del res, failed
                del pool, args
            #del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if Sequential:
            for i in range(len(datasets)):
                mpCreateLayerTables(datasets[i])
                del i

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End
        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            tablename               = datasets[i][3]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Copying the {datasetcode} Table"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                if arcpy.Exists(tablename):
                    arcpy.management.Copy(tablename, os.path.join(ProjectGDB, tablename))
                else:
                    msg = f"###->>> {datasetcode} Table is missing <<<---###"
                    logFile(log_file, msg); del msg

            del RegionGDB, RegionScratchGDB
            del tablename, distributionprojectcode, dataset_product_code

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # Compacting the ProjectGDB
        compactGDB(ProjectGDB)

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {dataset_product_code} Region GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {dataset_product_code} Region Scratch GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del datasetcode, dataset_product_code, distributionprojectcode
        # ##-->> Deleting Scratch and Temporary GDB End

    # ###--->>> Postprocessing End

        del datasets
        del Sequential

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def mpHandlerCreateMosaics(Sequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        arcpy.SetLogHistory(False)

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

        arcpy.env.overwriteOutput = True

        datasets = generateDatasets()

        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            wc = f"_Raster_Mask"
            rs = arcpy.ListRasters(f"*{wc}")
            datasets = [[r for r in group] for group in datasets if f"{group[0]}_{group[12]}{wc}" in rs]
            del rs, wc

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        if not datasets:
            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

    # ###--->>> Preprocessing Setup Start

        layerspeciesyearimagename_table = os.path.join(ProjectGDB, "LayerSpeciesYearImageName")

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"> Checking if there is a File GDB for layer: {datasetcode} and if there is data"
            logFile(log_file, msg); del msg

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch")

            msg = f"\t> Creating Table View: {os.path.basename(layerspeciesyearimagename_table)}"
            logFile(log_file, msg); del msg

            tableview = arcpy.management.MakeTableView(layerspeciesyearimagename_table, "table view", f"DatasetCode = '{datasetcode}'", RegionGDB)
            arcpy.management.CopyRows(tableview, os.path.join(RegionGDB, "LayerSpeciesYearImageName"))
            arcpy.management.Delete(tableview)
            del tableview
            arcpy.management.DeleteIdentical(
                                             in_dataset=os.path.join(RegionGDB, "LayerSpeciesYearImageName"),
                                             fields="ImageName",
                                             xy_tolerance=None,
                                             z_tolerance=0
                                            )

            del datasetcode, distributionprojectcode, dataset_product_code
            del RegionGDB, RegionScratchGDB
        del layerspeciesyearimagename_table

    # ###--->>> Preprocessing Setup End

    # ###--->>> Multiprocessing Start

        if not Sequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            #cpu_num = multiprocessing.cpu_count() - 2
            with multiprocessing.Pool(processes=cpu_num, initializer=init_processes, initargs=(ARCGIS_METADATA_DIRECTORY, BASE_DIRECTORY, CSV_DIRECTORY,
                                                                                               DATASET_SHAPEFILE_DIRECTORY, EXPORT_METADATA_DIRECTORY,
                                                                                               FilterDatasets, IMAGE_DIRECTORY, INPORT_METADATA_DIRECTORY,
                                                                                               LAYER_DIRECTORY, LOG_DIRECTORY, log_file_folder, MOSAIC_DIRECTORY,
                                                                                               PUBLISH_DIRECTORY, ScratchFolder, SoftwareEnvironmentLevel,
                                                                                               field_definitions, table_definitions, selected_species,
                                                                                               FilterSpecies, timezones)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append(datasets[i])
                    del i
                # use the map function of pool to call the function worker()
                res = pool.map(mpCreateMosaics, args)
                # Close and join pools
                pool.close()
                pool.join()

                # If an error has occurred report it 
                failed = res.count(False) # count how many times False appears in the list with the return values
                if failed > 0:
                    print(f"{failed} workers failed!")
                print("Finished multiprocessing!")
                del res, failed
                del pool, args
            #del cpu_num
    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start
        if Sequential:
            for i in range(len(datasets)):
                mpCreateMosaics(datasets[i])
                del i

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        # ##-->> Copying Output Start

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End
        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            mosaicname              = datasets[i][19]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Copying the {mosaicname} Dataset"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(f"{mosaicname}", os.path.join(ProjectGDB, f"{mosaicname}"))

            msg = f"#-> Copying the {mosaicname} CRF Dataset"
            logFile(log_file, msg); del msg

            #crf = os.path.join( ScratchFolder, f"{mosaicname}_CRF.crf")
            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = ScratchFolder):
                arcpy.management.Copy(f"{mosaicname.replace('_Mosaic', '')}.crf", os.path.join(MOSAIC_DIRECTORY, f"{mosaicname.replace('_Mosaic', '')}.crf"))

            del RegionGDB, RegionScratchGDB
            del datasetcode, distributionprojectcode, mosaicname
            del dataset_product_code

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        compactGDB(ProjectGDB)

        # ##-->> Copying Output End

##        # ##-->> Deleting Scratch and Temporary GDB Start
##        for i in range(len(datasets)):
##            datasetcode             = datasets[i][0]
##            distributionprojectcode = datasets[i][12]
##            mosaicname              = datasets[i][19]
##            del i
##
##            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"
##
##            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")
##
##            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")
##
##            msg = f"#-> Deleting the {datasetcode} Region GDB"
##            logFile(log_file, msg); del msg
##
##            #purgeGDB(RegionGDB)
##            arcpy.management.Delete(RegionGDB)
##
##            msg = f"#-> Deleting the {datasetcode} Region Scratch GDB"
##            logFile(log_file, msg); del msg
##
##            #purgeGDB(RegionScratchGDB)
##            arcpy.management.Delete(RegionScratchGDB)
##
##            msg = f"#-> Deleting the {mosaicname.replace('_Mosaic', '')}.crf Dataset"
##            logFile(log_file, msg); del msg
##
##            arcpy.management.Delete(os.path.join(ScratchFolder, f"{mosaicname.replace('_Mosaic', '')}.crf"))
##
##            del RegionGDB, RegionScratchGDB
##            del datasetcode, distributionprojectcode, mosaicname
##            del dataset_product_code
##        # ##-->> Deleting Scratch and Temporary GDB End

        del datasets, Sequential

    # ###--->>> Postprocessing End

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def mpHandlerCreateRasters(Sequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        arcpy.SetLogHistory(False)

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

        datasets = generateDatasets()

        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            wc = f"_Raster_Mask"
            rs = arcpy.ListRasters(f"*{wc}")
            datasets = [[r for r in group] for group in datasets if f"{group[3]}{wc}" in rs]
            del wc, rs

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        if not datasets:
            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

        arcpy.env.overwriteOutput = True

    # ###--->>> Preprocessing Setup Start

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            tablename               = datasets[i][3]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            msg = f"> Checking if there is a File GDB for region: {datasetcode} and if there is data"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            # Region Sample Locations
            datasetcode_sample_locations = f"{datasetcode}_Sample_Locations"

            # Region Raster Mask
            datasetcode_raster_mask = f"{tablename}_Raster_Mask"

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch")

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_sample_locations)):
                msg = f"\t> Copying the {datasetcode_sample_locations}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, datasetcode_sample_locations), os.path.join(RegionGDB, datasetcode_sample_locations))

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_raster_mask)):
                msg = f"\t> Copying the {datasetcode_raster_mask}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, datasetcode_raster_mask), os.path.join(RegionGDB, datasetcode_raster_mask))

            del datasetcode_raster_mask
            del datasetcode_sample_locations

            del RegionGDB, RegionScratchGDB, datasetcode, tablename
            del distributionprojectcode, dataset_product_code

    # ###--->>> Preprocessing Setup End

    # ###--->>> Multiprocessing Start

        if not Sequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            #cpu_num = multiprocessing.cpu_count() - 2
            with multiprocessing.Pool(processes=cpu_num, initializer=init_processes, initargs=(ARCGIS_METADATA_DIRECTORY, BASE_DIRECTORY, CSV_DIRECTORY,
                                                                                               DATASET_SHAPEFILE_DIRECTORY, EXPORT_METADATA_DIRECTORY,
                                                                                               FilterDatasets, IMAGE_DIRECTORY, INPORT_METADATA_DIRECTORY,
                                                                                               LAYER_DIRECTORY, LOG_DIRECTORY, log_file_folder, MOSAIC_DIRECTORY,
                                                                                               PUBLISH_DIRECTORY, ScratchFolder, SoftwareEnvironmentLevel,
                                                                                               field_definitions, table_definitions, selected_species,
                                                                                               FilterSpecies, timezones)) as pool:

                args = []
                for i in range(len(datasets)):
                    args.append(datasets[i])
                    del i
                # use the map function of pool to call the function worker()
                res = pool.map(mpCreateRasters, args)
                # Close and join pools
                pool.close()
                pool.join()

                # If an error has occurred report it 
                failed = res.count(False) # count how many times False appears in the list with the return values
                if failed > 0:
                    print(f"{failed} workers failed!")
                print("Finished multiprocessing!")
                del res, failed
                del pool, args
            #del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start
        if Sequential:
            for i in range(len(datasets)):
                mpCreateRasters(datasets[i])
                del i

        del Sequential

    # ###--->>> Sequentialprocessing End

        # ##-->> Copying Output Start

        compactGDB(ProjectGDB)

        # ##-->> Copying Output End

    # ###--->>> Postprocessing Start

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            msg = f"#-> Deleting the {dataset_product_code} Region GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {dataset_product_code} Region Scratch GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del datasetcode, distributionprojectcode, dataset_product_code
        # ##-->> Deleting Scratch and Temporary GDB End

    # ###--->>> Postprocessing End

        del datasets

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def mpHandlerCreateSampleLocationPoints(Sequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        arcpy.SetLogHistory(False)

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

        datasets = generateDatasets()

        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            tbs = arcpy.ListTables(f"*")
            datasets = [[r for r in group] for group in datasets if group[3] in tbs and group[3] not in ['', 'Datasets', 'Indicators', 'Species_Filter']]
            del tbs

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        if not datasets:
            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

    # ###--->>> Preprocessing Setup Start
        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            tablename               = datasets[i][3]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            msg = f"> Checking if there is a File GDB for region: {dataset_product_code} and if there is data"
            logFile(log_file, msg); del msg

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch")

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}")

            if not arcpy.Exists(os.path.join(RegionGDB, tablename)):
                msg = f"\t> Copying the {tablename}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, tablename), os.path.join(RegionGDB, tablename))

            del RegionGDB, RegionScratchGDB, datasetcode, tablename, dataset_product_code

    # ###--->>> Multiprocessing Start

        if not Sequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            #cpu_num = multiprocessing.cpu_count() - 2
            with multiprocessing.Pool(processes=cpu_num, initializer=init_processes, initargs=(ARCGIS_METADATA_DIRECTORY, BASE_DIRECTORY, CSV_DIRECTORY,
                                                                                               DATASET_SHAPEFILE_DIRECTORY, EXPORT_METADATA_DIRECTORY,
                                                                                               FilterDatasets, IMAGE_DIRECTORY, INPORT_METADATA_DIRECTORY,
                                                                                               LAYER_DIRECTORY, LOG_DIRECTORY, log_file_folder, MOSAIC_DIRECTORY,
                                                                                               PUBLISH_DIRECTORY, ScratchFolder, SoftwareEnvironmentLevel,
                                                                                               field_definitions, table_definitions, selected_species,
                                                                                               FilterSpecies, timezones)) as pool:

                args = []
                for i in range(len(datasets)):
                    args.append(datasets[i])
                    del i
                # use the map function of pool to call the function worker()
                res = pool.map(mpCreateSampleLocationPoints, args)
                # Close and join pools
                pool.close()
                pool.join()

                # If an error has occurred report it 
                failed = res.count(False) # count how many times False appears in the list with the return values
                if failed > 0:
                    print(f"{failed} workers failed!")
                print("Finished multiprocessing!")
                del res, failed
                del pool, args
            #del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start

        if Sequential:
            for i in range(len(datasets)):
                mpCreateSampleLocationPoints(datasets[i])
                del i

        del Sequential

    # ###--->>> Sequentialprocessing End

    # ###--->>> Postprocessing Start

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End
        arcpy.env.overwriteOutput = True

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            sample_locations = f"{datasetcode}_Sample_Locations"

            msg = f"#-> Copying the {sample_locations} Dataset"
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = RegionScratchGDB, workspace = RegionGDB):
                arcpy.management.Copy(sample_locations, os.path.join(ProjectGDB, sample_locations))

            del RegionGDB, RegionScratchGDB
            del datasetcode, sample_locations, distributionprojectcode

        # ##-->> Copy data from Scratch and Temporary GDB to Project GDB End

        # Compacting the ProjectGDB
        compactGDB(ProjectGDB)

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"#-> Deleting the {dataset_product_code} Region GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)

            msg = f"#-> Deleting the {dataset_product_code} Region Scratch GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB
            del datasetcode, dataset_product_code, distributionprojectcode
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
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def mpHandlerCreateSpeciesRichnessRasters(Sequential):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        arcpy.SetLogHistory(False)

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

        arcpy.env.overwriteOutput = True

        datasets = generateDatasets()

        with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
            wc = "IDW"
            tbs = arcpy.ListTables(f"*{wc}"); del wc
            datasets = [[r for r in group] for group in datasets if group[3] in tbs]
            del tbs

        if FilterDatasets:
            datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

        if not datasets:
            print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

    # ###--->>> Preprocessing Setup Start

        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            msg = f"> Checking if there is a File GDB for layer: {dataset_product_code} and if there is data"
            logFile(log_file, msg); del msg

            # Set layercode_species_richness_path
            core_species_richness = "_Core Species Richness"
            layercode_core_species_richness_path = os.path.join(IMAGE_DIRECTORY, dataset_product_code, core_species_richness)
            layercode_core_species_richness_scratch_path = os.path.join(ScratchFolder, dataset_product_code, core_species_richness)
            del core_species_richness

            if not os.path.isdir(layercode_core_species_richness_path):
                os.makedirs(layercode_core_species_richness_path)
            del layercode_core_species_richness_path

            if not os.path.isdir(layercode_core_species_richness_scratch_path):
                os.makedirs(layercode_core_species_richness_scratch_path)

            del layercode_core_species_richness_scratch_path

            # Set layercode_species_richness_path
            species_richness = "_Species Richness"
            datasetcode_species_richness_path = os.path.join(IMAGE_DIRECTORY, dataset_product_code, species_richness)
            datasetcode_species_richness_scratch_path = os.path.join(ScratchFolder, dataset_product_code, species_richness)
            del species_richness

            if not os.path.isdir(datasetcode_species_richness_path):
                os.makedirs(datasetcode_species_richness_path)
            del datasetcode_species_richness_path

            if not os.path.isdir(datasetcode_species_richness_scratch_path):
                os.makedirs(datasetcode_species_richness_scratch_path)
            del datasetcode_species_richness_scratch_path

            # Region Raster Mask
            datasetcode_raster_mask = f"{dataset_product_code}_Raster_Mask"
            layerspeciesyearimagename = "LayerSpeciesYearImageName"

            if not os.path.exists(RegionGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}")

            if not os.path.exists(RegionScratchGDB):
                msg = f"\t> Creating File Geodatabase: {os.path.basename(RegionScratchGDB)}"
                logFile(log_file, msg); del msg

                arcpy.management.CreateFileGDB(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch")

            if not arcpy.Exists(os.path.join(RegionGDB, datasetcode_raster_mask)):
                msg = f"\t> Copying the {datasetcode_raster_mask}"
                logFile(log_file, msg); del msg

                arcpy.management.Copy(os.path.join(ProjectGDB, datasetcode_raster_mask), os.path.join(RegionGDB, datasetcode_raster_mask))

            if not arcpy.Exists(os.path.join(RegionGDB, layerspeciesyearimagename)):
                msg = f"\t> Copying the {layerspeciesyearimagename}"
                logFile(log_file, msg); del msg

                tableview = arcpy.management.MakeTableView(os.path.join(ProjectGDB, layerspeciesyearimagename), "table view", f"DatasetCode = '{datasetcode}'", RegionGDB)
                arcpy.management.CopyRows(tableview, os.path.join(RegionGDB, layerspeciesyearimagename))
                arcpy.management.Delete(tableview)
                del tableview

            del datasetcode_raster_mask, layerspeciesyearimagename
            del RegionGDB, RegionScratchGDB
            del datasetcode, distributionprojectcode, dataset_product_code

    # ###--->>> Preprocessing Setup End

    # ###--->>> Multiprocessing Start

        if not Sequential:
            # setup the multiprocessing pool with the number of cores in the current PC
            # The cpu_count() functions retruns the number of cpu cores
            #cpu_num = multiprocessing.cpu_count() - 2
            with multiprocessing.Pool(processes=cpu_num, initializer=init_processes, initargs=(ARCGIS_METADATA_DIRECTORY, BASE_DIRECTORY, CSV_DIRECTORY,
                                                                                               DATASET_SHAPEFILE_DIRECTORY, EXPORT_METADATA_DIRECTORY,
                                                                                               FilterDatasets, IMAGE_DIRECTORY, INPORT_METADATA_DIRECTORY,
                                                                                               LAYER_DIRECTORY, LOG_DIRECTORY, log_file_folder, MOSAIC_DIRECTORY,
                                                                                               PUBLISH_DIRECTORY, ScratchFolder, SoftwareEnvironmentLevel,
                                                                                               field_definitions, table_definitions, selected_species,
                                                                                               FilterSpecies, timezones)) as pool:
                args = []
                for i in range(len(datasets)):
                    args.append(datasets[i])
                    del i
                # use the map function of pool to call the function worker()
                res = pool.map(mpCreateSpeciesRichnessRasters, args)
                # Close and join pools
                pool.close()
                pool.join()

                # If an error has occurred report it 
                failed = res.count(False) # count how many times False appears in the list with the return values
                if failed > 0:
                    print(f"{failed} workers failed!")
                print("Finished multiprocessing!")
                del res, failed
                del pool, args
            #del cpu_num

    # ###--->>> Multiprocessing End

    # ###--->>> Sequentialprocessing Start
        if Sequential:
            for i in range(len(datasets)):
                mpCreateSpeciesRichnessRasters(datasets[i])
                del i

        del Sequential

    # ###--->>> Sequentialprocessing End

        # ##-->> Copying Output Start

        # compactGDB(ProjectGDB)

        # ##-->> Copying Output End

    # ###--->>> Postprocessing Start

        # ##-->> Deleting Scratch and Temporary GDB Start
        for i in range(len(datasets)):
            datasetcode             = datasets[i][0]
            distributionprojectcode = datasets[i][12]
            del i

            dataset_product_code = f"{datasetcode}_{distributionprojectcode}"

            RegionGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel}.gdb")

            RegionScratchGDB = os.path.join(ScratchFolder, f"{dataset_product_code} {SoftwareEnvironmentLevel} Scratch.gdb")

            RegionScratchFolder = os.path.join(ScratchFolder, f"{dataset_product_code}")

            msg = f"#-> Deleting the {dataset_product_code} Region GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionGDB)
            arcpy.management.Delete(RegionGDB)
            #shutil.rmtree(RegionGDB)

            msg = f"#-> Deleting the {dataset_product_code} Region Scratch GDB"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchGDB)
            #shutil.rmtree(RegionScratchGDB)

            msg = f"#-> Deleting the {dataset_product_code} Region Scratch Folder"
            logFile(log_file, msg); del msg

            #purgeGDB(RegionScratchGDB)
            arcpy.management.Delete(RegionScratchFolder)
            #shutil.rmtree(RegionScratchGDB)

            del RegionGDB, RegionScratchGDB, RegionScratchFolder
            del datasetcode, distributionprojectcode, dataset_product_code
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
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def parseXML(xml_file):
    """
    Parse XML with ElementTree
    """
    # Uses the inspect module and a lamda to find name of this function
    function = function_name()

    import xml.etree.ElementTree as ET

# Methods getchildren() and getiterator() of classes ElementTree and Element
# in the ElementTree module have been removed. They were deprecated in Python 3.2.
#  Use iter(x) or list(x) instead of x.getchildren() and x.iter() or list(x.iter())
# instead of x.getiterator(). (Contributed by Serhiy Storchaka in bpo-36543.)

    try:
        tree = ET.ElementTree(file=xml_file)
        print(f"Tree Root: {tree.getroot()}")
        root = tree.getroot()
        print(f" > Tag: {root.tag}, Attribute: {root.attrib}")

        for child in root:
            print(f"  > Child Tag: {child.tag}, Child Attribute: {child.attrib}")
            #if child.tag == "appointment":
            #    for step_child in child:
            #        print(step_child.tag)
            for step_child in child:
                #print(step_child.tag)
                print(f"   > Step-Child Tag: {step_child.tag}")
                del step_child
            del child

        # iterate over the entire tree
        print(f"{'-'*40}")     # string multiplication
        print("Iterating using a tree iterator")
        print(f"{'-'*40}")     # string multiplication
        #iter_ = tree.getiterator() #x.iter() or list(x.iter()) instead of x.getiterator()
        iter_ = tree.iter()
        #iter_ = list(tree.iter())
        for elem in iter_:
            print(f" > Element Tag: {elem.tag}")
            del elem
        del iter_

        # get the information via the children!
        print(f"{'-'*40}")     # string multiplication
        print("Iterating using list()") # iter(x) or list(x) instead of x.getchildren()
        print(f"{'-'*40}")     # string multiplication
        #appointments = root.getchildren() #  Use iter(x) or list(x) instead of x.getchildren()
        appointments = list(root)
        for appointment in appointments:
            #appt_children = appointment.getchildren() #  Use iter(x) or list(x) instead of x.getchildren()
            appt_children = list(appointment)
            for appt_child in appt_children:
                print(f" > {appt_child.tag:<15} = {appt_child.text}")
                #print(f'{key:<29} : [{field_name:<29} {field_type:<9} {field_alias:<45} {field_length:>5} {default_value:>3} {dmomain:<1}],')
                del appt_child
            del appt_children, appointment
        del appointments

        # get the information via the children!
        print(f"{'-'*40}")     # string multiplication
        print("Iterating using iter()") # iter(x) or list(x) instead of x.getchildren()
        print(f"{'-'*40}")     # string multiplication
        #appointments = root.getchildren() #  Use iter(x) or list(x) instead of x.getchildren()
        appointments = iter(root)
        for appointment in appointments:
            #appt_children = appointment.getchildren() #  Use iter(x) or list(x) instead of x.getchildren()
            appt_children = iter(appointment)
            for appt_child in appt_children:
                #print("%s=%s" % (appt_child.tag, appt_child.text))
                print(f" > {appt_child.tag:<15} = {appt_child.text:}")
                del appt_child
            del appt_children, appointment
        del appointments

        del xml_file, ET, tree, root

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

def prettyXML(metadata):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        import xml.etree.ElementTree as ET

        if arcpy.Exists(metadata):

            tree = ET.ElementTree(file=metadata)
            root = tree.getroot()

            tree = ET.ElementTree(root)
            ET.indent(tree, space="\t", level=0)
            xmlstr = ET.tostring(root, encoding='UTF-8').decode('UTF-8')
            with open(metadata, "w") as f:
                f.write(xmlstr)
                del f
            del xmlstr, tree, root
        else:
            print(f"\t###--->>> {os.path.basename(metadata)} is missing!! <<<---###")
            print(f"\t###--->>> {metadata} <<<---###")

        del metadata, ET

    except arcpy.ExecuteError:
        import sys
        # Geoprocessor threw an error
        #print("\n\t" + arcpy.GetMessages().replace("\n", "\n\t") + "\n")
        msg = arcpy.GetMessages(2).replace('\n', '\n\t')
        msg = f"\nArcPy Exception:\n\t{msg}Line Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg
    finally:
        # Get list of local keys that may need to be deleted.
        localKeys =  [key for key in locals().keys() if not any(key == k for k in ["function", "log_file"])]

        # If there is a list of local keys, print the list, and then delete
        # variables
        if localKeys:
            msg = f"\n###--->>> Local Keys in {function}(): {', '.join(localKeys)} <<<---###\n"
            print(msg); del msg
        del localKeys, function, log_file

def publishMapLayers():
    """Create Map Layers"""
    try: # The code with the exception that you want to catch. If an exception
         # is raised, control flow leaves this block immediately and goes to
         # the except block

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

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

        # Set the scratch workspace to the RegionScratchGDB
        arcpy.env.scratchWorkspace = ScratchGDB

        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(False)

    # ###--->>> Preprocessing Setup Start
        arcpy.env.overwriteOutput = True

        from datetime import datetime
        from arcgis.gis import GIS

        portal = "https://noaa.maps.arcgis.com/"
        user = "John.F.Kennedy_noaa"

        LogInAGOL = True
        if LogInAGOL:
            # Sign in to portal
            #arcpy.SignInToPortal("https://www.arcgis.com", "MyUserName", "MyPassword")
            # For example: 'http://www.arcgis.com/'
            arcpy.SignInToPortal(portal)

            print(f"###---> Signed into Portal: {arcpy.GetActivePortalURL()} <---###")
        del LogInAGOL

        CreateServiceDefinitionDrafts = False
        OverwriteFeatureService = False
        if CreateServiceDefinitionDrafts:

            datasets = generateDatasets()

            publish_datasets = {}
            aprx = arcpy.mp.ArcGISProject(ProjectGIS)
            mps = [m for m in aprx.listMaps() if "GLMME" not in m.name]

            for mp in mps:
                msg = f" > Map: {mp.name}"
                logFile(log_file, msg); del msg
                lyrs = mp.listLayers()
                if lyrs:
                    last = lyrs.pop(); del last
                    for lyr in lyrs:
                        if lyr.isFeatureLayer:
                            #msg = f"  > Layer: {lyr.name} ({dataset})"
                            msg = f"  > Layer: {lyr.name}"
                            logFile(log_file, msg); del msg

                            database, dataset = os.path.split(lyr.dataSource)
                            del database
                            ds = [[r for r in group] for group in datasets if group[7] == dataset][0]
                            datecode, featureservicename, featureservicetitle = ds[10], ds[17], ds[18]
                            del ds

                            #https://pro.arcgis.com/en/pro-app/latest/arcpy/metadata/metadata-class.htm
                            import_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureservicetitle}.xml") #DisMAP Regions 20230101.xml"
                            lyr_md = lyr.metadata
                            lyr_md.synchronize('SELECTIVE')
                            lyr_md.importMetadata(import_metadata, 'ARCGIS_METADATA')
                            lyr_md.title = featureservicetitle
                            lyr_md.save()
                            del lyr_md

                            mp_md = mp.metadata
                            mp_md.synchronize('SELECTIVE')
                            mp_md.importMetadata(import_metadata, 'ARCGIS_METADATA')
                            mp_md.title = featureservicetitle
                            mp_md.save()
                            del mp_md

                            del featureservicetitle, import_metadata

                            #featureservicename = f"{dataset}_{datecode}".replace('_IDW', '')
                            msg = f"   > Feature Service: {featureservicename}"
                            logFile(log_file, msg); del msg
                            #del dataset, datecode, featureservicename

                            # Reference: https://strftime.org/
                            datecode_format = '%Y%m%d'
                            dataset_datetime = datetime.strptime(datecode, datecode_format)
                            version = dataset_datetime.strftime("%B %d %Y")
                            portal_folder = f"DisMAP {version.replace(' 0', ' ')}"
                            del datecode_format, dataset_datetime, version, datecode

                            # Set output file names
                            sddraft_filename = featureservicename + ".sddraft"
                            sddraft_output_filename = os.path.join(PUBLISH_DIRECTORY, sddraft_filename)
                            sd_filename = featureservicename + ".sd"
                            sd_output_filename = os.path.join(PUBLISH_DIRECTORY, sd_filename)

                            # Create a new SDDraft and stage to SD
                            msg = f"   > Creating SD: file {sd_filename}"
                            logFile(log_file, msg); del msg

                            # Create FeatureSharingDraft
                            server_type = "HOSTING_SERVER"
                            #            m.getWebLayerSharingDraft (server_type, service_type, service_name, {layers_and_tables})
                            # sddraft = m.getWebLayerSharingDraft(server_type, "FEATURE", service_name, [selected_layer, selected_table])
                            # https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/featuresharingdraft-class.htm#GUID-8E27A3ED-A705-4ACF-8C7D-AA861327AD26
                            sddraft = mp.getWebLayerSharingDraft(server_type, "FEATURE", featureservicename, lyr)

                            if OverwriteFeatureService:
                                sddraft.overwriteExistingService = True
                            else:
                                sddraft.overwriteExistingService = False

                            del sd_filename, server_type

                            # Create Service Definition Draft file
                            sddraft.exportToSDDraft(sddraft_output_filename)

                            publish_datasets[dataset] = {
                                                         'portal_folder'           : portal_folder,
                                                         'featureservicename'      : featureservicename,
                                                         'sddraft_filename'        : sddraft_filename,
                                                         'sddraft_output_filename' : sddraft_output_filename,
                                                         'sd_output_filename'      : sd_output_filename,
                                                        }
                            del portal_folder, featureservicename, sddraft_output_filename, sd_output_filename
                            del dataset, sddraft_filename
                            del sddraft
                        del lyr
                        aprx.save()
                del lyrs

                tbs = mp.listTables()
                if tbs:
                    for tb in tbs:
                        msg = f"  > Table: {tb.name}"
                        logFile(log_file, msg); del msg

                        database, dataset = os.path.split(tb.dataSource)
                        del database
                        ds = [[r for r in group] for group in datasets if group[3] == dataset][0]
                        datecode, featureservicename, featureservicetitle = ds[10], ds[17], ds[18]
                        del ds

                        #https://pro.arcgis.com/en/pro-app/latest/arcpy/metadata/metadata-class.htm
                        import_metadata = os.path.join(EXPORT_METADATA_DIRECTORY, f"{featureservicetitle}.xml") #DisMAP Regions 20230101.xml"
                        tb_md = tb.metadata
                        tb_md.synchronize('SELECTIVE')
                        tb_md.importMetadata(import_metadata, 'ARCGIS_METADATA')
                        tb_md.title = featureservicetitle
                        tb_md.save()
                        del tb_md

                        mp_md = mp.metadata
                        mp_md.synchronize('SELECTIVE')
                        mp_md.importMetadata(import_metadata, 'ARCGIS_METADATA')
                        mp_md.save()
                        del mp_md

                        del featureservicetitle, import_metadata

                        #featureservicename = f"{dataset}_{datecode}"
                        msg = f"   > Feature Service: {featureservicename}"
                        logFile(log_file, msg); del msg
                        #del dataset, datecode, featureservicename

                        # Reference: https://strftime.org/
                        datecode_format = '%Y%m%d'
                        dataset_datetime = datetime.strptime(datecode, datecode_format)
                        version = dataset_datetime.strftime("%B %d %Y")
                        portal_folder = f"DisMAP {version.replace(' 0', ' ')}"
                        del datecode_format, dataset_datetime, version, datecode

                        # Set output file names
                        sddraft_filename = featureservicename + ".sddraft"
                        sddraft_output_filename = os.path.join(PUBLISH_DIRECTORY, sddraft_filename)
                        sd_filename = featureservicename + ".sd"
                        sd_output_filename = os.path.join(PUBLISH_DIRECTORY, sd_filename)

                        # Create a new SDDraft and stage to SD
                        msg = f"   > Creating SD: file {sd_filename}"
                        logFile(log_file, msg); del msg

                        # Create FeatureSharingDraft
                        server_type = "HOSTING_SERVER"
                        #            m.getWebLayerSharingDraft (server_type, service_type, service_name, {layers_and_tables})
                        # sddraft = m.getWebLayerSharingDraft(server_type, "FEATURE", service_name, [selected_layer, selected_table])
                        # https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/featuresharingdraft-class.htm#GUID-8E27A3ED-A705-4ACF-8C7D-AA861327AD26

                        sddraft = mp.getWebLayerSharingDraft(server_type, "FEATURE", featureservicename, tb)

                        if OverwriteFeatureService:
                            sddraft.overwriteExistingService = True
                        else:
                            sddraft.overwriteExistingService = False

                        del sd_filename, server_type

                        # Create Service Definition Draft file
                        sddraft.exportToSDDraft(sddraft_output_filename)

                        publish_datasets[dataset] = {
                                                     'portal_folder'           : portal_folder,
                                                     'featureservicename'      : featureservicename,
                                                     'sddraft_filename'        : sddraft_filename,
                                                     'sddraft_output_filename' : sddraft_output_filename,
                                                     'sd_output_filename'      : sd_output_filename,
                                                    }
                        del portal_folder, featureservicename, sddraft_output_filename, sd_output_filename
                        del sddraft_filename, dataset
                        del tb
                        del sddraft
                        aprx.save()
                del tbs
                del mp
            del datasets
            del mps
            aprx.save()
            del aprx
            del publish_datasets
        del CreateServiceDefinitionDrafts, OverwriteFeatureService

        PublishDatasets = True
        if PublishDatasets:

            datasets = generateDatasets()

            publish_datasets = {}

            for i in range(len(datasets)):
                featureclassname   = datasets[i][7]
                datecode           = datasets[i][10]
                featureservicename = datasets[i][17]
                del i

##                database, dataset = os.path.split(lyr.dataSource)
##                del database
##                ds = [[r for r in group] for group in datasets if group[14] == dataset][0]
##                datecode, layertitle, featureservicename = ds[8], ds[15], ds[16]
##                del ds

                #featureservicename = f"{featureclassname}_{datecode}"
                #msg = f"   > Feature Service: {featureservicename}"
                #logFile(log_file, msg); del msg
                #del featureclassname, datecode, featureservicename

                # Reference: https://strftime.org/
                datecode_format = '%Y%m%d'
                dataset_datetime = datetime.strptime(datecode, datecode_format)
                version = dataset_datetime.strftime("%B %d %Y")
                portal_folder = f"DisMAP {version.replace(' 0', ' ')}"
                del datecode_format, dataset_datetime, version, datecode

                sddraft_filename = f"{featureservicename}.sddraft"
                sddraft_output_filename = os.path.join(PUBLISH_DIRECTORY, sddraft_filename)
                sd_output_filename = os.path.join(PUBLISH_DIRECTORY, sddraft_filename.replace(".sddraft", ".sd"))

                if arcpy.Exists(sddraft_output_filename):
                    publish_datasets[featureclassname] = {
                                                         'portal_folder'           : portal_folder,
                                                         'featureservicename'      : featureservicename,
                                                         'sddraft_filename'        : sddraft_filename,
                                                         'sddraft_output_filename' : sddraft_output_filename,
                                                         'sd_output_filename'      : sd_output_filename,
                                                        }
                del portal_folder, featureservicename, sddraft_filename, sddraft_output_filename, sd_output_filename,

            del datasets

            for featureclassname in sorted(publish_datasets):
                print(f"\tDataset: {featureclassname}")
                print(f"\t\tPortal Folder:            {publish_datasets[featureclassname]['portal_folder']}")
                print(f"\t\tFeature Servicen Nme:     {publish_datasets[featureclassname]['featureservicename']}")
                print(f"\t\tSD Draft Filename:        {publish_datasets[featureclassname]['sddraft_filename']}")
                print(f"\t\tSD Draft Output Filename: {publish_datasets[featureclassname]['sddraft_output_filename']}")
                print(f"\t\tSD Output Filename:       {publish_datasets[featureclassname]['sd_output_filename']}")

                portal_folder = publish_datasets[featureclassname]['portal_folder']
                featureservicename = publish_datasets[featureclassname]['featureservicename']
                sddraft_filename = publish_datasets[featureclassname]['sddraft_filename']
                sddraft_output_filename = publish_datasets[featureclassname]['sddraft_output_filename']
                sd_output_filename = publish_datasets[featureclassname]['sd_output_filename']

                try:
                    # Stage Service
                    msg = f"   > Start Staging of: {sddraft_filename}"
                    logFile(log_file, msg); del msg
                    arcpy.server.StageService(sddraft_output_filename, sd_output_filename)

                    # Share to portal
                    msg = f"   > Start Uploading of: {sddraft_filename}"
                    logFile(log_file, msg); del msg

                    # Set local variables
                    inSdFile = sd_output_filename
                    inServer = "HOSTING_SERVER"
                    inServiceName = featureservicename
                    #inServiceName = layertitle
                    inCluster = ""
                    inFolderType = "EXISTING"
                    inFolder = portal_folder
                    #inFolderType = "NEW"
                    #inFolder = portal_folder
                    # inStartup = "STOPPED"
                    inStartup = "STARTED"
                    inOverride = "OVERRIDE_DEFINITION"
                    inMyContents = "SHARE_ONLINE"
                    # inPublic = "PRIVATE"
                    inPublic = "PUBLIC"
                    #inOrganization = "NO_SHARE_ORGANIZATION"
                    inOrganization = "SHARE_ORGANIZATION"
                    #inGroups = ["My Group", "MyGroup 2"]

                    # Run UploadServiceDefinition
                    arcpy.server.UploadServiceDefinition(inSdFile, inServer, inServiceName,
                                                         inCluster, inFolderType, inFolder,
                                                         inStartup, inOverride, inMyContents,
                                                         inPublic, inOrganization)

                    msg = f"  > Finish Publishing of: {sddraft_filename}"
                    logFile(log_file, msg); del msg

                    del inSdFile, inServer, inServiceName, inCluster, inFolderType
                    del inFolder, inStartup, inOverride, inMyContents, inPublic
                    del inOrganization #, inGroups

                except Exception as stage_exception:
                    if "00374" in str(stage_exception):
                        print("The map is not set to allow assignment of unique IDs")
                    print("Analyzer errors encountered - {}".format(str(stage_exception)))

                except arcpy.ExecuteError:
                    print(arcpy.GetMessages(2))
                finally:
                    pass

                del portal_folder, featureservicename
                del sddraft_filename, sddraft_output_filename, sd_output_filename
                del featureclassname
            del publish_datasets
        del PublishDatasets
        #portal_folder = "DisMAP January 1 2023"


# https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/mapservicedraft-class.htm#GUID-A5DCCC67-30D4-48B6-AE50-D130CBB291FA


##        print("Connecting to {}".format(portal))
##        gis = GIS(portal)
##        sd_fs_name = "DisMAP Regions 20230101"
##        # Find the SD, update it, publish /w overwrite and set sharing and metadata
##        print("Search for published content on the portal…")
##        search_my_contents = gis.content.search(
##                                                #query=f"{'FeatureSharingDraftExample'} AND owner:{user}",
##                                                # title:{} AND owner:{}
##                                                #query=f"title: {sd_fs_name} AND owner:{user}",
##                                                query=f"owner:{user}",
##                                                item_type="*",
##                                                sort_field="tile" ,
##                                                sort_order="asc",
##                                                max_items = 1000,
##                                                outside_org=True
##                                                )
##        titles = []
##        for search_my_content in search_my_contents:
##            title = search_my_content.title
##            if title not in titles:
##                titles.append(title)
##                del title
##            print(f"Found: {search_my_content.title}\n\t Type: {search_my_content.type}\n\t URL: {search_my_content.url}")
##            del search_my_content
##        for title in titles:
##            print(f"Found: {title}"); del title
##        del search_my_contents, sd_fs_name

##        ProcessDisMAPRegionsAndTables = False
##        if ProcessDisMAPRegionsAndTables:
##            arcpy.env.overwriteOutput = True
##
##            msg = f"> Processing DisMAP_Region, Indicators, Datasets, Species_Filter Layers."
##            logFile(log_file, msg); del msg
##
##            datasets = generateDatasets()
##
##            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
##                layer_list = ["DisMAP_Regions", "Indicators", "Datasets", "Species_Filter",]
##                #layer_list = ["DisMAP_Regions"]
##                datasets = [[r for r in group] for group in datasets if group[14] in layer_list]
##                del layer_list
##
##            if FilterDatasets:
##                datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]
##
##            if not datasets:
##                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")
##
##            for i in range(len(datasets)):
##                layercode          = datasets[i][4]
##                datecode           = datasets[i][8]
##                layername          = datasets[i][14]
##                layertitle         = datasets[i][15]
##                featureservicename = datasets[i][16]
##                del i
##
##                # Reference: https://strftime.org/
##                #portal_folder = "DisMAP January 1 2023"
##                format = '%Y%m%d'
##                datasetcode_datetime = datetime.strptime(datecode, format)
##                version = datasetcode_datetime.strftime("%B %d %Y")
##                portal_folder = f"DisMAP {version.replace(' 0', ' ')}"
##                del format, datasetcode_datetime, version
##
##                #print(f"{layertitle}: {layertitle in titles}")
##
##                msg = f" > Processing {layertitle} Layer File."
##                logFile(log_file, msg); del msg
##
##                aprx = arcpy.mp.ArcGISProject(ProjectGIS)
##                m = aprx.listMaps(layertitle)[0]
##                print(m.name)
##
##                # Set output file names
##                outdir = LAYER_DIRECTORY
##                service_name = featureservicename
##                #service_name = layertitle.replace("'","")
##                sddraft_filename = service_name + ".sddraft"
##                sddraft_output_filename = os.path.join(outdir, sddraft_filename)
##                sd_filename = service_name + ".sd"
##                sd_output_filename = os.path.join(outdir, sd_filename)
##
##                # Create a new SDDraft and stage to SD
##                msg = f"   > Creating SD: file {sd_filename}."
##                logFile(log_file, msg); del msg
##
##                # Create FeatureSharingDraft
##                server_type = "HOSTING_SERVER"
##                sddraft = m.getWebLayerSharingDraft(server_type, "FEATURE", service_name)
##
##                sddraft.summary = "My Summary"
##                sddraft.tags = "My tags"
##                sddraft.description = "My description"
##                sddraft.credits = "My credits"
##                sddraft.use = "My disclaimer"
##
##                del service_name, outdir, sd_filename, server_type
##                del m
##
##                # Create Service Definition Draft file
##                sddraft.exportToSDDraft(sddraft_output_filename)
##
##                del sddraft
##                del aprx
##
### #                ## Change the SDDraft to overwrite existing service
### #                # Read the file
### #                with open(sddraft_output_filename, 'r') as file:
### #                    filedata = file.read()
### #                # Replace the target string
### #                filedata = filedata.replace('esriServiceDefinitionType_New', 'esriServiceDefinitionType_Replacement')
### #                # Write the file out again
### #                with open(sddraft_output_filename, 'w') as file:
### #                    file.write(filedata)
##
##                try:
##                    # Stage Service
##                    msg = f"   > Start Staging of: {sddraft_filename}"
##                    logFile(log_file, msg); del msg
##                    arcpy.server.StageService(sddraft_output_filename, sd_output_filename)
##
##                    # Share to portal
##                    msg = f"   > Start Uploading of: {sddraft_filename}"
##                    logFile(log_file, msg); del msg
##
##                    # Set local variables
##                    inSdFile = sd_output_filename
##                    inServer = "HOSTING_SERVER"
##                    inServiceName = featureservicename
##                    #inServiceName = layertitle
##                    inCluster = ""
##                    inFolderType = "EXISTING"
##                    inFolder = portal_folder
##                    #inFolderType = "NEW"
##                    #inFolder = portal_folder
##                    # inStartup = "STOPPED"
##                    inStartup = "STARTED"
##                    inOverride = "OVERRIDE_DEFINITION"
##                    inMyContents = "SHARE_ONLINE"
##                    # inPublic = "PRIVATE"
##                    inPublic = "PUBLIC"
##                    #inOrganization = "NO_SHARE_ORGANIZATION"
##                    inOrganization = "SHARE_ORGANIZATION"
##                    #inGroups = ["My Group", "MyGroup 2"]
##
##                    # Run UploadServiceDefinition
##                    arcpy.server.UploadServiceDefinition(inSdFile, inServer, inServiceName,
##                                                         inCluster, inFolderType, inFolder,
##                                                         inStartup, inOverride, inMyContents,
##                                                         inPublic, inOrganization)
##                    # arcpy.server.UploadServiceDefinition(inSdFile, inServer, inServiceName,
##                    #                                      inCluster, inFolderType, inFolder,
##                    #                                      inStartup, inOverride, inMyContents,
##                    #                                     inPublic, inOrganization, inGroups)
##
##                    del inSdFile, inServer, inServiceName, inCluster, inFolderType
##                    del inFolder, inStartup, inOverride, inMyContents, inPublic
##                    del inOrganization #, inGroups
##
##                    msg = f"  > Finish Publishing of: {sddraft_filename}"
##                    logFile(log_file, msg); del msg
##
##                except Exception as stage_exception:
##                    if "00374" in str(stage_exception):
##                        print("The map is not set to allow assignment of unique IDs")
##                    print("Analyzer errors encountered - {}".format(str(stage_exception)))
##
##                except arcpy.ExecuteError:
##                    print(arcpy.GetMessages(2))
##
##                del sddraft_filename, sddraft_output_filename, sd_output_filename
##                del featureservicename
##                del layercode, layername, layertitle
##                del portal_folder, datecode
##            del datasets
##        del ProcessDisMAPRegionsAndTables
##
##        ProcessingSampleLocationLayers = False
##        if ProcessingSampleLocationLayers:
##            arcpy.env.overwriteOutput = True
##
##            msg = f"> Processing Sample Location Layers."
##            logFile(log_file, msg); del msg
##
##            datasets = generateDatasets()
##
##            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
##                wc = "_Sample_Locations"
##                fcs = arcpy.ListFeatureClasses(f"*{wc}")
##                datasets = [[r for r in group] for group in datasets if group[7] in fcs]
##                del wc, fcs
##
##            if FilterDatasets:
##                datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]
##
##            if not datasets:
##                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")
##
##            for i in range(len(datasets)):
##                layercode          = datasets[i][4]
##                datecode           = datasets[i][8]
##                layername          = datasets[i][14]
##                layertitle         = datasets[i][15]
##                featureservicename = datasets[i][16]
##                del i
##
##                # Reference: https://strftime.org/
##                #portal_folder = "DisMAP January 1 2023"
##                format = '%Y%m%d'
##                datasetcode_datetime = datetime.strptime(datecode, format)
##                version = datasetcode_datetime.strftime("%B %d %Y")
##                portal_folder = f"DisMAP {version.replace(' 0', ' ')}"
##                del format, datasetcode_datetime, version
##
##                msg = f"  > Processing {layertitle} Layer."
##                logFile(log_file, msg); del msg
##
##                aprx = arcpy.mp.ArcGISProject(ProjectGIS)
##                m = aprx.listMaps(layertitle)[0]
##                print(m.name)
##
##                # Set output file names
##                outdir = LAYER_DIRECTORY
##                service_name = featureservicename
##                #service_name = layertitle.replace("'","")
##                sddraft_filename = service_name + ".sddraft"
##                sddraft_output_filename = os.path.join(outdir, sddraft_filename)
##                sd_filename = service_name + ".sd"
##                sd_output_filename = os.path.join(outdir, sd_filename)
##
##                # Create a new SDDraft and stage to SD
##                msg = f"   > Creating SD: file {sd_filename}."
##                logFile(log_file, msg); del msg
##
##                # Create FeatureSharingDraft
##                server_type = "HOSTING_SERVER"
##                sddraft = m.getWebLayerSharingDraft(server_type, "FEATURE", service_name)
##
### #                sddraft.summary = "My Summary"
### #                sddraft.tags = "My tags"
### #                sddraft.description = "My description"
### #                sddraft.credits = "My credits"
### #                sddraft.use = "My disclaimer"
##
##                del service_name, outdir, sd_filename, server_type
##                del m
##
##                # Create Service Definition Draft file
##                sddraft.exportToSDDraft(sddraft_output_filename)
##
##                del sddraft
##                del aprx
##
##                try:
##                    # Stage Service
##                    msg = f"   > Start Staging of: {sddraft_filename}"
##                    logFile(log_file, msg); del msg
##                    arcpy.server.StageService(sddraft_output_filename, sd_output_filename)
##
##                    # Share to portal
##                    msg = f"   > Start Uploading of: {sddraft_filename}"
##                    logFile(log_file, msg); del msg
##
##                    # Set local variables
##                    inSdFile = sd_output_filename
##                    inServer = "HOSTING_SERVER"
##                    inServiceName = featureservicename
##                    #inServiceName = layertitle
##                    inCluster = ""
##                    inFolderType = "EXISTING"
##                    inFolder = portal_folder
##                    #inFolderType = "NEW"
##                    #inFolder = portal_folder
##                    # inStartup = "STOPPED"
##                    inStartup = "STARTED"
##                    inOverride = "OVERRIDE_DEFINITION"
##                    inMyContents = "SHARE_ONLINE"
##                    # inPublic = "PRIVATE"
##                    inPublic = "PUBLIC"
##                    #inOrganization = "NO_SHARE_ORGANIZATION"
##                    inOrganization = "SHARE_ORGANIZATION"
##                    #inGroups = ["My Group", "MyGroup 2"]
##
##                    # Run UploadServiceDefinition
##                    arcpy.server.UploadServiceDefinition(inSdFile, inServer, inServiceName,
##                                                         inCluster, inFolderType, inFolder,
##                                                         inStartup, inOverride, inMyContents,
##                                                         inPublic, inOrganization)
##                    # arcpy.server.UploadServiceDefinition(inSdFile, inServer, inServiceName,
##                    #                                      inCluster, inFolderType, inFolder,
##                    #                                      inStartup, inOverride, inMyContents,
##                    #                                     inPublic, inOrganization, inGroups)
##
##                    del inSdFile, inServer, inServiceName, inCluster, inFolderType
##                    del inFolder, inStartup, inOverride, inMyContents, inPublic
##                    del inOrganization #, inGroups
##
##                    msg = f"  > Finish Publishing of: {sddraft_filename}"
##                    logFile(log_file, msg); del msg
##
##                except Exception as stage_exception:
##                    if "00374" in str(stage_exception):
##                        print("The map is not set to allow assignment of unique IDs")
##                    print("Analyzer errors encountered - {}".format(str(stage_exception)))
##
##                except arcpy.ExecuteError:
##                    print(arcpy.GetMessages(2))
##
##                del sddraft_filename, sddraft_output_filename, sd_output_filename
##                del layercode, layername, layertitle, featureservicename
##                del datecode, portal_folder
##            del datasets
##        del ProcessingSampleLocationLayers

        ProcessingCRFLayers = False
        if ProcessingCRFLayers:
            arcpy.env.overwriteOutput = True

            msg = f" > Processing CRF Layers."
            logFile(log_file, msg); del msg

            datasets = generateDatasets()

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = MOSAIC_DIRECTORY):
                wc = ""
                crfs = [crf[:-4] for crf in arcpy.ListFiles(f"*{wc}*")]
                datasets = [[r for r in group] for group in datasets if group[9] in crfs]
                del wc, crfs

            if FilterDatasets:
                datasets = [[r for r in group] for group in datasets if group[3] in selected_datasets]

            if not datasets:
                print("###--->>> @@@ Something is wrong with the dataset selection @@@ <<<---###")

            LogInFisheriesPortal = False
            if LogInFisheriesPortal:
                # Sign in to portal
                #arcpy.SignInToPortal("https://www.arcgis.com", "MyUserName", "MyPassword")
                # For example: 'http://www.arcgis.com/'
                arcpy.SignInToPortal("https://maps.fisheries.noaa.gov/portal/home/")

                print(f"###---> Signed into Portal: {arcpy.GetActivePortalURL()} <---###")
            del LogInFisheriesPortal

            for i in range(len(datasets)):
                crfname                 = datasets[i][9]
                crftitle                = datasets[i][10]
                del i

                msg = f"  > Processing {crftitle} Layer."
                logFile(log_file, msg); del msg

                crftitle_path = os.path.join(LAYER_DIRECTORY, f"{crftitle}.lyrx")

                # Get time information from a layer in a layer file
                lyrFile = arcpy.mp.LayerFile(crftitle_path)

                del lyrFile, crftitle_path
                del crfname, crftitle
            del datasets
        del ProcessingCRFLayers

        del portal, datetime, GIS, user # gis, titles
        #del LAYER_DIRECTORY, MOSAIC_DIRECTORY, ProjectGDB, ScratchGDB, log_file_folder

        #Final benchmark for the region.
        msg = f"ENDING {function} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {function}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
            print(msg); del msg
        del localKeys, function, log_file

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        if d:
            #print(f'\n\t###--->>> Remaining local variable in {function_name()} <<<---###\n')
            #You'll need to check for user-defined variables in the directory
            for obj in d:
                #checking for built-in variables/functions
                if not obj.startswith('__'):
                    #deleting the said obj, since a user-defined function
                    #del globals()[obj]
                    #print(f"Remaining local variable: {locals()[obj]}")
                    del locals()[obj]
                    del obj
        del d

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
    with arcpy.da.SearchCursor(table, ["Year"]) as cursor:
        return sorted({row[0] for row in cursor})

def unique_values(table, field):
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

        # January 1 2023
        #Version = "January 1 2023"
        #DateCode = "20230101"

        # March 15 2023
        #Version = "March 1 2023"
        #DateCode = "20230315"

        # April 1 2023
        Version = "April 1 2023"
        DateCode = "20230401"

        # Software Environment Level
        #SoftwareEnvironmentLevel = "Dev" # For use on Local laptop
        #SoftwareEnvironmentLevel = "Test" # For use on Local laptop and Windows Instance
        SoftwareEnvironmentLevel = "Prod" # For use on Windows Instance

        # Set to True if we want to filter on certian one or more regions, else
        # False to process all regions
        FilterDatasets = False # True False
        # selected_regions = 'AI_IDW','BSS_IDW','EBS_IDW','ENBS_IDW','NBS_IDW',
        #                    'GOA_IDW','GMEX_IDW','HI_IDW','NEUS_FAL_IDW',
        #                    'NEUS_SPR_IDW','SEUS_FAL_IDW','SEUS_SPR_IDW',
        #                    'SEUS_SUM_IDW','WC_ANN_IDW','WC_GLMME','WC_TRI_IDW',
        # Below are lists used to test different regions
        selected_datasets = ['WC_GLMME', ]

        # Set to True if we want to filter on certian years, else False to
        # process all years
        #FilterYears = False

        # Set Gloabl cpu_num
        cpu_num = multiprocessing.cpu_count() - 2
        #cpu_num = multiprocessing.cpu_count()

        # The main() is for testing and project setup
        main()

    # ###--->>> Step #1
    # ###--->>> Create Lookup Tables Start

        # ###--->>> Step #1a
        # ###--->>> Create Dataset Table Start
        # Create Dataset Table: True or False

        CreateDatasetTable = True
        if CreateDatasetTable:
            createDatasetTable()
            # Create Dataset Table Metadata
            #createDatasetTableMetadata()
        del CreateDatasetTable

        del createDatasetTableMetadata, parseXML

        GenerateDatasets = False
        if GenerateDatasets:
            ds = generateDatasets(); del ds
        del GenerateDatasets

        # ###--->>> Create Daaset Table End

        # ###--->>> Step #1b
        # ###--->>> Create Species Filter Table Start

        CreateSpeciesFilterTable = False
        if CreateSpeciesFilterTable:
            createSpeciesFilterTable()

        # ###--->>> Create Species Filter Table End

    # ###--->>> Create Lookup Tables End

    # ###--->>> Step #2
    # ###--->>> Create DisMAP Regions Start

        # Notes: https://github.com/afsc-gap-products/akgfmaps/tree/master/inst/extdata
        # Create DisMAP Regions True or False
        CreateDisMapRegions = False
        Sequential = False
        if CreateDisMapRegions:
            mpHandlerCreateDisMapRegions(Sequential)
        del CreateDisMapRegions, Sequential
        del mpCreateDisMapRegions, mpHandlerCreateDisMapRegions

    # ###--->>> Create DisMAP Regions End

    # ###--->>> Step #3
    # ###--->>> Create Regions Fishnets Start

        # Generate Layer Fishnets True or False
        CreateLayerFishnets = False
        Sequential = False
        if CreateLayerFishnets:
            mpHandlerCreateLayerFishnets(Sequential)
        del CreateLayerFishnets, mpHandlerCreateLayerFishnets
        del mpCreateLayerFishnets, Sequential
        del mpCreateLatitudeLongitudeRasters

    # ###--->>> Create Regions Fishnets End

    # ###--->>> Step #4
    # ###--->>> Get DMS Points for GEBCO Regions Start

        # This function creates a report of coordinate values by region
        # to be used to extract GEBCO data
        # Get DMS for points that create fishnet True or False
        GetDMSPointsForGebco = False
        if GetDMSPointsForGebco:
            getDMSPointsForGebco()
        del GetDMSPointsForGebco, getDMSPointsForGebco

    # ###--->>> Get DMS Points for GEBCO Regions End

    # ###--->>> Step #5
    # ###--->>> Create Bathymetry Rasters Start

        # ###--->>> Step #5a
        # ###--->>> Create Alasaka Bathymetry Rasters Start

        # Create Alasaka Bathymetry Rasters
        CreateAlasakaBathymetry = False
        if CreateAlasakaBathymetry:
            createAlasakaBathymetry()
        del CreateAlasakaBathymetry, createAlasakaBathymetry

        # ###--->>> Create Alasaka Bathymetry Rasters End

        # ###--->>> Step #5b
        # ###--->>> Create GEBCO Bathymetry Rasters Start

        # Create GEBCO Bathymetry Rasters
        CreateGebcoBathymetry = False
        if CreateGebcoBathymetry:
            createGebcoBathymetry()
        del CreateGebcoBathymetry, createGebcoBathymetry

        # ###--->>> Create GEBCO Bathymetry Rasters End

        # ###--->>> Step #5c
        # ###--->>> Create PIFSC Bathymetry Rasters Start

        # Create Hawaii Bathymetry Rasters
        CreateHawaiiBathymetry = False
        if CreateHawaiiBathymetry:
            selected_datasets = ['HI_IDW',]
            createHawaiiBathymetry()
        del CreateHawaiiBathymetry, createHawaiiBathymetry

        # ###--->>> Create PIFSC Bathymetry Rasters End

        # ###--->>> Step #5d
        # ###--->>> Create Layer Bathymetry Start

        # Create Layer Bathymetry True or False
        CreateLayerBathymetry = False
        Sequential = False
        if CreateLayerBathymetry:
            mpHandlerCreateLayerBathymetry(Sequential)
        del CreateLayerBathymetry, mpHandlerCreateLayerBathymetry
        del Sequential, mpCreateLayerBathymetry

        # ###--->>> Create Layer Bathymetry End

    # ###--->>> Create Bathymetry Rasters End

    # ###--->>> Step #6
    # ###--->>> Import Sample Location CSV Tables Start
        # ###--->>> Import Layer CSV Tables Start
        FilterDatasets = False # True False
        selected_datasets = ['AI_IDW', 'EBS_IDW', 'ENBS_IDW', 'NBS_IDW', 'GOA_IDW',]

        # Create Layer CSV Tables True or False
        CreateLayerTables = False
        Sequential = False
        # Generate Tables -- Needs to run next so that Datasetes can be
        # created in the following step.
        if CreateLayerTables:
            mpHandlerCreateLayerTables(Sequential)
        del CreateLayerTables, Sequential
        del mpCreateLayerTables, mpHandlerCreateLayerTables

        # ###--->>> Import Layer CSV Tables End

    # ###--->>> Import Sample Location CSV Tables End

    # ###--->>> Step #7
    # ###--->>> Populate Region Species Year Image Name Table Start
        # Create Region-Species-Year-Image-Name Table True or False

##        FilterDatasets = False # True False
##        # selected_regions = 'AI_IDW','BSS_IDW','EBS_IDW','NEBS_IDW','NBS_IDW',
##        #                    'GOA_IDW','GMEX_IDW','HI_IDW','NEUS_FAL_IDW',
##        #                    'NEUS_SPR_IDW','SEUS_FAL_IDW','SEUS_SPR_IDW',
##        #                    'SEUS_SUM_IDW','WC_ANN_IDW','WC_GLMME','WC_TRI_IDW',
##        selected_datasets = ['AI_IDW',]

        FilterDatasets = False # True False
        selected_datasets = ['ENBS_IDW',]

        CreateLayerSpeciesYearImageName = False
        Sequential = False
        if CreateLayerSpeciesYearImageName:
            mpHandlerCreateLayerSpeciesYearImageName(Sequential)
        del mpCreateLayerSpeciesYearImageName
        del mpHandlerCreateLayerSpeciesYearImageName
        del Sequential

    # ###--->>> Populate Region Species Year Image Name Table End

    # ###--->>> Step #8
    # ###--->>> Create Sample Location Points Datasetes Start
        FilterDatasets = False # True False
        selected_datasets = ['AI_IDW', 'EBS_IDW', 'ENBS_IDW', 'NBS_IDW', 'GOA_IDW',]

        # Generate Point Datasetes True or False
        CreateSampleLocationPoints = False
        Sequential = False
        if CreateSampleLocationPoints:
            mpHandlerCreateSampleLocationPoints(Sequential)
        del CreateSampleLocationPoints, Sequential
        del mpCreateSampleLocationPoints, mpHandlerCreateSampleLocationPoints

    # ###--->>>  Create Survey Location Points Datasetes End

    # ###--->>> Step #9
    # ###--->>> Create Biomass Rasters Start
        FilterDatasets = False # True False
        selected_datasets = ['AI_IDW', 'EBS_IDW', 'ENBS_IDW', 'NBS_IDW', 'GOA_IDW',]

        # Generate Rasters True or False
        CreateRasters = False
        Sequential = False
        if CreateRasters:
            mpHandlerCreateRasters(Sequential)
        del CreateRasters, mpHandlerCreateRasters
        del Sequential, mpCreateRasters

    # ###--->>> Step #110
    # ###--->>> Indicators Table Start
##        #                    'GOA_IDW','GMEX_IDW','HI_IDW','NEUS_FAL_IDW',
##        #                    'NEUS_SPR_IDW','SEUS_FAL_IDW','SEUS_SPR_IDW',
##        #                    'SEUS_SUM_IDW','WC_ANN_IDW','WC_GLMME','WC_TRI_IDW',
        FilterDatasets = False # True False
        #selected_datasets = ['AI_IDW', 'EBS_IDW', 'ENBS_IDW', 'NBS_IDW', 'GOA_IDW',]
        selected_datasets = ['WC_TRI_IDW',]

        # Populate Indicators Table True or False
        CreateIndicatorsTable = False
        Sequential = False
        if CreateIndicatorsTable:
            #selected_datasets = ['WC_GLMME']
            mpHandlerCreateIndicatorsTable(Sequential)
        del CreateIndicatorsTable, mpHandlerCreateIndicatorsTable
        del Sequential, mpCreateIndicatorsTable

    # ###--->>> Indicators Table End

    # ###--->>> Step #11
    # ###--->>> Species Richness Rasters Start

        FilterDatasets = False # True False
        # selected_regions = 'AI_IDW','BSS_IDW','EBS_IDW','NEBS_IDW','NBS_IDW',
        #                    'GOA_IDW','GMEX_IDW','HI_IDW','NEUS_FAL_IDW',
        #                    'NEUS_SPR_IDW','SEUS_FAL_IDW','SEUS_SPR_IDW',
        #                    'SEUS_SUM_IDW','WC_ANN_IDW','WC_GLMME','WC_TRI_IDW',
        selected_datasets = ['AI_IDW','EBS_IDW']

        # Create Species Richness Rasters = True or False
        CreateSpeciesRichnessRasters = False
        Sequential = False
        if CreateSpeciesRichnessRasters:
            mpHandlerCreateSpeciesRichnessRasters(Sequential)
        del CreateSpeciesRichnessRasters, Sequential
        del mpHandlerCreateSpeciesRichnessRasters, mpCreateSpeciesRichnessRasters

    # ###--->>> Species Richness Rasters End

    # ###--->>> Step #12
    # ###--->>> Mosaics Start
        FilterDatasets = True # True False
        selected_datasets = ['AI_IDW','GOA_IDW', 'NEUS_FAL_IDW', 'GMEX_IDW']

        # This function creates Mosaics that iterate over years
        # Create Species Richness Rasters = True or False
        CreateMosaics = False
        Sequential = False
        if CreateMosaics:
            mpHandlerCreateMosaics(Sequential)
        del CreateMosaics, Sequential
        del mpHandlerCreateMosaics, mpCreateMosaics
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # This function creates Mosaics that iterate by attributes
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ###--->>> Mosaics End

    # ###--->>> Step #13
    # ###--->>> Import ArcGIS Metadata for Layers Start

        # Import Metadata = True or False
        ImportMetadata = False
        if ImportMetadata:
            importMetadata()
        del ImportMetadata, importMetadata

        # Create Species Richness Rasters = True or False
        #createEmptyTempMetadataXML()
##        ImportArcGisMetadata = False
##        if ImportArcGisMetadata:
##            importArcGisMetadata()
##        del ImportArcGisMetadata
        del importArcGisMetadata
        del createEmptyTempMetadataXML

    # ###--->>> Import ArcGIS Metadata for Layers End

    # ###--->>> Step #14
    # ###--->>> Import ArcGIS Metadata for Layers Start

        # Export ArcGIS Metadata = True or False
##        ExportArcGisMetadata = False
##        if ExportArcGisMetadata:
##            exportArcGisMetadata()
##        del ExportArcGisMetadata
        del exportArcGisMetadata

##        MetadataUpdate = False
##        if MetadataUpdate:
##            metadataUpdate()
##        del MetadataUpdate
        del metadataUpdate

##        PrettyXML = False
##        if PrettyXML:
##            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = EXPORT_METADATA_DIRECTORY):
##            #with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = PUBLISH_DIRECTORY):
##                wc = ".xml"
##                #wc = ".sddraft"
##                metadata_files = [os.path.join(EXPORT_METADATA_DIRECTORY, f) for f in arcpy.ListFiles(f"*{wc}")]; del wc
##                #metadata_files = [os.path.join(PUBLISH_DIRECTORY, f) for f in arcpy.ListFiles(f"*{wc}")]; del wc
##                for metadata_file in metadata_files:
##                    prettyXML(metadata=metadata_file)
##                    del metadata_file
##                del metadata_files
##        del PrettyXML

    # ###--->>> Export ArcGIS Metadata for Layers End

    # ###--->>> Step #15
    # ###--->>> Create Maps Layers Start

        # Set to True if we want to filter on certian one or more regions, else
        # False to process all regions
        FilterDatasets = False # True False
        selected_datasets = ['AI_IDW', 'WC_GLMME']

        # Add all layer titles to ProjectGIS
        #addMapsToProjectGIS()

        # Create Species Richness Rasters = True or False
        CreateMapLayers = False
        if CreateMapLayers:
            createMapLayers()
        del CreateMapLayers, createMapLayers

    # ###--->>> Create Map Layers End


    # ###--->>> Step #16
    # ###--->>> Publish Maps Layers Start

        # Set to True if we want to filter on certian one or more regions, else
        # False to process all regions
        FilterDatasets = False # True False
        # selected_regions = 'AI_IDW','BSS_IDW','EBS_IDW','NEBS_IDW','NBS_IDW',
        #                    'GOA_IDW','GMEX_IDW','HI_IDW','NEUS_FAL_IDW',
        #                    'NEUS_SPR_IDW','SEUS_FAL_IDW','SEUS_SPR_IDW',
        #                    'SEUS_SUM_IDW','WC_ANN_IDW','WC_GLMME','WC_TRI_IDW',
        # Below are lists used to test different regions
        #selected_datasets = ['AI_IDW', 'WC_GLMME',]
        selected_datasets = ['AI_IDW', 'WC_GLMME']

        # This function puplishes the version with the Date Code
        # Create Species Richness Rasters = True or False
        PublishMapLayers = False
        if PublishMapLayers:
            publishMapLayers()
        del PublishMapLayers, publishMapLayers

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # This function puplishes the version with CURRENT
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # ###--->>> Publish Map Layers End

    # ###--->>> Step #
    # ###--->>> Table and Field Report Start
        # Table and Field Report: True or False
        CreateTableAndFieldReport = False
        # Workspace: ws
        ws = ProjectGDB
        #ws = r"C:\Users\john.f.kennedy\Documents\GitHub\DisMAP\ArcGIS Analysis - Python\January 1 2023\Scratch Folder\AI_IDW Dev.gdb"
        # Wildcard: wc
        #   Usage: wc = "", wc = "HI_CSV", wc = "Datasets", wc = "_csv"
        # Data Type: dt
        #   Usage: dt = ["Any",], dt = ["Table", "FeatureClass"], dt = ["Table"]
        # Feature Type: t
        #   Usage: t = ["Any",], t = ["Polygon",]

        # Report on Template Datasets
        #wc = "Indicators"; dt = ["Any",];  t = ["Any",]
        #wc = ""; dt = ["Any",];  t = ["Any",]
        wc = ""; dt = ["Any",];  t = ["Any",]

        if CreateTableAndFieldReport: createTableAndFieldReport(ws, wc, dt, t)
        del CreateTableAndFieldReport, createTableAndFieldReport, ws, wc, dt, t

        GenerateFieldDefinitions = False
        if GenerateFieldDefinitions:
            ws = ProjectGDB
            wc = ""; dt = ["Any",];  t = ["Any",]
            generateFieldDefinitions(ws, wc, dt, t)
            del ws, wc, dt, t
        del generateFieldDefinitions, GenerateFieldDefinitions

    # ###--->>> Table and Field Report End

        # Clean-Up
        del Version, DateCode

# ###--->>>

        # Final benchmark
        msg = f"ENDING {script_file} COMPLETED ON {strftime('%a %b %d %I:%M:%S %p', localtime())}"
        logFile(log_file, msg); del msg

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = f"Elapsed Time for {script_file}: {strftime('%H:%M:%S', gmtime(elapse_time))} (H:M:S)"
        logFile(log_file, msg); del msg, start_time, end_time, elapse_time #, log_file

        del cwd, script_file

        # TODO list
        # print(f"TODO: ??")

        # https://lxml.de/tutorial.html
        # https://www.tutorialspoint.com/python/python_xml_processing.htm
        # https://www.datacamp.com/tutorial/python-xml-elementtree
        # http://www.juliandyke.com/Research/Development/UsingPythonTkinterWithXML.php
        # https://realpython.com/python-xml-parser/
        # https://www.edureka.co/blog/python-xml-parser-tutorial/
        # https://www.youtube.com/watch?v=QiTMhvI4WrQ
        # https://www.youtube.com/watch?v=tlHNS-UTRIM

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
        logFile(log_file, msg); del msg
    except Exception as e:
        import sys
        # Capture all other errors
        #print(sys.exc_info()[2].tb_lineno)
        msg = f"\nPython Exception:\n\tType: {type(e).__name__}\n\tMessage: {e.args[0]}\n\tLine Number: {sys.exc_info()[2].tb_lineno}\n"
        logFile(log_file, msg); del msg

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
        del time, datetime, math, numpy
        del os, inspect, function_name, function
        del localtime, strftime, gmtime
        del multiprocessing, arcpy, sys, main

        #del logging

        # Remove defined functions
        del compactGDB, listEnvironments, clearFolder, addMetadata
        del reorder_fields, select_by_specie, select_by_specie_no_years
        del unique_field, unique_species, unique_species_dict, unique_year
        del unique_years, unique_values, FilterSpecies
        del addFields, calculateCoreSpecies, importEPU, purgeGDB
        del unique_fish, unique_fish_dict, LicenseError
        del generateDatasets, createDatasetTable, createFolders
        del generateSpeciesFilter, generateMasterSpeciesInformation
        del createSpeciesFilterTable, generateLayerSpeciesYearImageName
        del addMapsToProjectGIS, listMapsInProjectGIS, prettyXML,
        del alterFields, init_processes, logFile

        # Remove declared globals
        del BASE_DIRECTORY, IMAGE_DIRECTORY, CSV_DIRECTORY, DATASET_SHAPEFILE_DIRECTORY
        del MOSAIC_DIRECTORY, LAYER_DIRECTORY, ProjectGIS, ProjectToolBox,
        del ProjectGDB, ProjectName, BathymetryGDB, ScratchGDB, ScratchFolder
        del EXPORT_METADATA_DIRECTORY, ARCGIS_METADATA_DIRECTORY
        del INPORT_METADATA_DIRECTORY, LOG_DIRECTORY
        del geographic_regions, selected_species
        del selected_datasets, listFolder
        del CreateSpeciesFilterTable, CreateLayerSpeciesYearImageName
        del field_definitions, table_definitions, sleep, PUBLISH_DIRECTORY
        #del logger, formatter, ch, selected_years
        del SoftwareEnvironmentLevel, FilterDatasets, log_file_folder
        # del FilterYears
        del cpu_num, timezones

        # This is a list of local and global variables that are exclude from
        # lists of variables


        del log_file

        globalKeys = [key for key in globals().keys() if not key.startswith('__')]

        if globalKeys:
            msg = f"\n###--->>> Global Keys: {', '.join(globalKeys)} <<<---###\n"
            print(msg); del msg
        del globalKeys

        #initializing d with dir()
        #This will store a list of all the variables in the program
        d = dir()
        #You'll need to check for user-defined variables in the directory
        for obj in d:
            #checking for built-in variables/functions
            if not obj.startswith('__'):
                #deleting the said obj, since a user-defined function
                #print(f"\tRemaining global variable: {globals()[obj]}")
                del globals()[obj]
                del obj
        del d

        import gc; gc.collect(); del gc
