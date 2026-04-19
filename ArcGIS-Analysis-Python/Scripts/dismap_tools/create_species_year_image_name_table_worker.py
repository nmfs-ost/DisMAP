# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        create_species_year_image_name_table_worker
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     09/03/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import sys
import traceback
import inspect

import arcpy # third-parties second

def trace():
    import sys, traceback  # noqa: E401
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    line = tbinfo.split(", ")[1]
    filename = sys.path[0] + os.sep + "test.py"
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror

def print_table(table=""):
    try:
        """ Print first 5 rows of a table """
        desc = arcpy.da.Describe(table)
        fields = [f.name for f in desc["fields"] if f.type == "String"]
        #Get OID field
        oid    = desc["OIDFieldName"]
        # Use SQL TOP to sort field values
        arcpy.AddMessage(f"{', '.join(fields)}")
        for row in arcpy.da.SearchCursor(table, fields, f"{oid} <= 5"):
            arcpy.AddMessage(row)
            del row
        del desc, fields, oid
        del table
    except:  # noqa: E722
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        sys.exit()

def worker(region_gdb=""):
    try:
        # Test if passed workspace exists, if not sys.exit()
        if not arcpy.Exists(rf"{region_gdb}"):
            arcpy.AddError(f"{os.path.basename(region_gdb)} is missing!!")
            sys.exit()

        from arcpy import metadata as md
        # Import the dismap module to access tools
        import dismap_tools

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        table_name        = os.path.basename(region_gdb).replace(".gdb", "")
        scratch_folder    = os.path.dirname(region_gdb)
        project_folder    = os.path.dirname(scratch_folder)
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"
        region_table      = rf"{region_gdb}\{table_name}"
        csv_data_folder   = rf"{project_folder}\CSV_Data"

        arcpy.AddMessage(f"Table Name: {table_name}\nProject Folder: {project_folder}\nScratch Folder: {scratch_folder}\n")
        # Set basic workkpace variables
        del project_folder, scratch_folder

        arcpy.env.workspace                = region_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

    # **********************************************************************
    # Start: Create new LayerSpeciesYearImageName table
        layer_species_year_image_name = rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName"

        arcpy.AddMessage(f"Create Table: {table_name}_LayerSpeciesYearImageName" )
        arcpy.management.CreateTable(out_path       = region_gdb,
                                     out_name       = f"{table_name}_LayerSpeciesYearImageName",
                                     template       = "",
                                     config_keyword = "",
                                     out_alias      = "")
        arcpy.AddMessage("\tCreate Table: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        # Add Fields to layer_species_year_image_name
        dismap_tools.add_fields(csv_data_folder, layer_species_year_image_name)
        dismap_tools.import_metadata(csv_data_folder, layer_species_year_image_name)
    # End
    # **********************************************************************

    # **********************************************************************
    # Start: Create new LayerSpeciesYearImageName table
        arcpy.AddMessage("\nDatasets Table\n" )
        datasets_table = rf"{region_gdb}\\Datasets"
        datasets_table_fields = [f.name for f in arcpy.ListFields(datasets_table) if f.type not in ['Geometry', 'OID']]
        print_table(datasets_table)
        #region           = [row[0] for row in arcpy.da.SearchCursor(datasets_table, "Region", where_clause = f"TableName = '{table_name}'")][0]
        filter_region    = [row[0] for row in arcpy.da.SearchCursor(datasets_table, "FilterRegion", where_clause = f"TableName = '{table_name}'")][0].replace("'", "''")
        filter_subregion = [row[0] for row in arcpy.da.SearchCursor(datasets_table, "FilterSubRegion", where_clause = f"TableName = '{table_name}'")][0].replace("'", "''")
    # End
    # **********************************************************************

    # **********************************************************************
    # Start: Create new LayerSpeciesYearImageName table
        arcpy.AddMessage("\nRegion IDW Table\n" )
        region_table_fields = [f.name for f in arcpy.ListFields(region_table) if f.type not in ['Geometry', 'OID']]
        # Get a record count to see if data is present; we don't want to add data
        getcount = arcpy.management.GetCount(region_table)[0]
        arcpy.AddMessage(f"\t{os.path.basename(region_table)} has {getcount} records")
        del getcount
        print_table(region_table)
        arcpy.AddMessage(f"\n\tUnique Species Count: {len(dismap_tools.unique_values(table=region_table, field='Species'))} for {os.path.basename(region_table)}")
    # End
    # **********************************************************************

    # **********************************************************************
    # Start: Create new LayerSpeciesYearImageName table
        arcpy.AddMessage("\nImage Name Table\n" )
        layer_species_year_image_name_fields = [f.name for f in arcpy.ListFields(layer_species_year_image_name) if f.type not in ['Geometry', 'OID']]
        arcpy.AddMessage(f"Image Name Fields:\n\t{', '.join(layer_species_year_image_name_fields)}")
        print_table(layer_species_year_image_name)
    # End
    # **********************************************************************

    # **********************************************************************
    # Start: Get information from the species filter table to create a
    # species filter dictionary
        arcpy.AddMessage("\nCreating the Species_Filter dictionary\n" )

        species_filter_table = os.path.join(region_gdb, "Species_Filter")
        species_filter_table_fields = [f.name for f in arcpy.ListFields(species_filter_table) if f.type not in ['Geometry', 'OID']]
        # Get a record count to see if data is present; we don't want to add data
        getcount = arcpy.management.GetCount(species_filter_table)[0]
        arcpy.AddMessage(f"\t{os.path.basename(species_filter_table)} has {getcount} records")
        arcpy.AddMessage(f"\tUnique Species Count: {len(dismap_tools.unique_values(table=species_filter_table, field='Species'))} for {os.path.basename(species_filter_table)}")
        del getcount
        #arcpy.AddMessage(species_filter_table_fields)
        print_table(species_filter_table)
        # Species, CommonName, TaxonomicGroup, FilterRegion, FilterSubRegion, ManagementBody, ManagementPlan, DistributionProjectName
        species_filter = {}
        with arcpy.da.SearchCursor(species_filter_table, species_filter_table_fields, f"FilterSubRegion = '{filter_subregion}'") as cursor:
            for row in cursor:
                #arcpy.AddMessage(row)
                species_filter[row[0]] = [row[1],row[2],row[3],row[4],row[5],row[6],row[7]]
                del row
        del cursor, species_filter_table, species_filter_table_fields
    # End
    # **********************************************************************
#Datasets
#               table_name
#  DatasetCode, TableName, Region,            Season, DistributionProjectName,         SummaryProduct, FilterRegion, FilterSubRegion
# ['AI',        'AI_IDW', 'Aleutian Islands', '',    'NMFS/Rutgers IDW Interpolation', 'Yes',          'Alaska',     'Aleutian Islands'

# IDW Table
# DatasetCode, Region,            Season, DistributionProjectName,          SummaryProduct, SampleID, Species,              TransformUnit, CommonName, SpeciesCommonName, CommonNameSpecies, CoreSpecies, Stratum
# ['AI',      'Aleutian Islands', '',     'NMFS/Rutgers IDW Interpolation', 'Yes',          '-10850', 'Anoplopoma fimbria', 'cuberoot',    'Sablefish', 'Anoplopoma fimbria (Sablefish)', 'Sablefish (Anoplopoma fimbria)', 'Yes', '721']

# Species Filter
# Species,               CommonName,  TaxonomicGroup,                     FilterRegion, FilterSubRegion,    ManagementBody, ManagementPlan,                                                      DistributionProjectName
# ['Anoplopoma fimbria', 'Sablefish', 'Perciformes/Cottoidei (sculpins)', 'Alaska',     'Aleutian Islands', 'NPFMC',        'Groundfish of the Bering Sea and Aleutian Islands Management Area', 'NMFS/Rutgers IDW Interpolation']

# Image Name Table
# DatasetCode, Region, Season, SummaryProduct, FilterRegion, FilterSubRegion, Species, CommonName, SpeciesCommonName, CommonNameSpecies, TaxonomicGroup, ManagementBody, ManagementPlan, DistributionProjectName, CoreSpecies, Variable, Value, Dimensions, ImageName

        arcpy.AddMessage("\nDefining the case fields\n")

        case_fields = [f for f in layer_species_year_image_name_fields if f in region_table_fields]
        arcpy.AddMessage(f"Case Fields:\n\t{', '.join(case_fields)}")

        # Execute Statistics to get unique set of records
        table_name_tmp = table_name+"_tmp"
        stats_fields = [[f"{f}", "COUNT"] for f in case_fields]

        arcpy.AddMessage(f"Statistics Analysis of {table_name} Table")
        arcpy.analysis.Statistics(table_name, table_name_tmp, stats_fields, case_fields)
        arcpy.AddMessage("\tStatistics Analysis: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        del stats_fields, case_fields

        table_name_tmp_fields = [f.name for f in arcpy.ListFields(table_name_tmp) if f.type not in ['Geometry', 'OID']]

        table_name_tmp_drop_fields = ";".join([f for f in table_name_tmp_fields if "FREQUENCY" in f or "COUNT" in f])
        del table_name_tmp_fields

        arcpy.management.DeleteField(in_table=table_name_tmp, drop_field=table_name_tmp_drop_fields)
        del table_name_tmp_drop_fields

        # Get a record count to see if data is present; we don't want to add data
        getcount = arcpy.management.GetCount(table_name_tmp)[0]
        arcpy.AddMessage(f"\t{table_name_tmp} has {getcount} records")
        del getcount

        arcpy.AddMessage(f"\tAdding the Variable, Dimensions, and ImageName Fields to the {table_name_tmp} table")

        table_name_tmp_new_fields = ['FilterRegion', 'FilterSubRegion', 'TaxonomicGroup',
                                      'ManagementBody', 'ManagementPlan', 'DistributionProjectName',
                                      'Variable', 'Value', 'Dimensions', 'ImageName',]

        table_name_tmp_fields = [f.name for f in arcpy.ListFields(table_name_tmp) if f.type not in ['Geometry', 'OID']]
        arcpy.AddMessage(table_name_tmp_fields)

        table_name_tmp_new_fields = [f for f in table_name_tmp_new_fields if f not in table_name_tmp_fields]
        arcpy.AddMessage(table_name_tmp_new_fields)

        field_definitions = dismap_tools.field_definitions(csv_data_folder, "")

        field_definition_list = []
        for table_name_tmp_new_field in table_name_tmp_new_fields:
            #arcpy.AddMessage(table_name_tmp_new_field)
            field_definition_list.append([field_definitions[table_name_tmp_new_field]["field_name"],
                                          field_definitions[table_name_tmp_new_field]["field_type"],
                                          field_definitions[table_name_tmp_new_field]["field_aliasName"],
                                          field_definitions[table_name_tmp_new_field]["field_length"]])
            del table_name_tmp_new_field
        del field_definitions

        arcpy.AddMessage(f"Adding Fields to Table: {table_name}_tmp")
        arcpy.management.AddFields(in_table = table_name_tmp, field_description = field_definition_list, template="")
        arcpy.AddMessage("\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        del field_definition_list

        del table_name_tmp_new_fields, table_name_tmp_fields

        # The following calculates the time stamp for the Dataset
        # Use Update Cursor instead of Calculate Field
        fields = ["DatasetCode", "Region", "Species", "Year", "FilterRegion",
                  "FilterSubRegion", "TaxonomicGroup", "ManagementBody",
                  "ManagementPlan", "DistributionProjectName", "Variable",
                  "Value", "Dimensions", "ImageName"]

        with arcpy.da.UpdateCursor(table_name_tmp, fields) as cursor:
            for row in cursor:
                variable   = row[2].replace("(","").replace(")","").replace(".","")
                value      = "Species"
                dimensions = "StdTime"
                imagename  = f"{table_name}_{variable.replace(' ','_')}_{str(row[3])}"
                if row[2] in species_filter:
                    row[4]  = filter_region.replace("''", "'")
                    row[5]  = filter_subregion.replace("''", "'")
                    row[6]  = species_filter[row[2]][1] # TaxonomicGroup
                    row[7]  = species_filter[row[2]][4] # ManagementBody
                    row[8]  = species_filter[row[2]][5] # ManagementPlan
                    row[9]  = species_filter[row[2]][6] # DistributionProjectName
                else:
                    row[4]  = ""
                    row[5]  = ""
                    row[6]  = ""
                    row[7]  = ""
                    row[8]  = ""
                    row[9]  = ""
                row[10]     = variable
                row[11]     = value
                row[12]     = dimensions
                row[13]     = imagename
                cursor.updateRow(row)
                del row, variable, value, dimensions, imagename
            del cursor
        del fields
        del species_filter

        arcpy.management.Append(inputs = table_name_tmp, target = layer_species_year_image_name, schema_type="NO_TEST", field_mapping="", subtype="")
        arcpy.AddMessage("\tAppend: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        table_name_tmp_fields = [f.name for f in arcpy.ListFields(table_name_tmp) if f.type not in ['Geometry', 'OID']]

        case_fields = [f.name for f in arcpy.ListFields(table_name_tmp) if f.type not in ['Geometry', 'OID'] and f.name not in ["CoreSpecies", "Species", "CommonName", "SpeciesCommonName", "CommonNameSpecies", "TaxonomicGroup", "ManagementBody", "ManagementPlan", "Variable", "Value", "Dimensions", "ImageName"]]

        # Execute Statistics to get unique set of records
        table_name_tmp_stats = table_name_tmp+"_stats"

        stats_fields = [[f"{f}", "COUNT"] for f in case_fields]

        arcpy.AddMessage(f"\tStatistics Analysis of '{table_name}_tmp' Table")

        arcpy.analysis.Statistics(table_name_tmp, table_name_tmp_stats, stats_fields, case_fields)
        arcpy.AddMessage("\tStatistics Analysis: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        del stats_fields, case_fields

        fields = [f.name for f in arcpy.ListFields(table_name_tmp_stats) if f.type not in ['Geometry', 'OID']]

        drop_fields = ";".join([f for f in fields if "FREQUENCY" in f or "COUNT" in f])
        del fields

        arcpy.management.DeleteField(in_table=table_name_tmp_stats, drop_field=drop_fields)
        arcpy.AddMessage("\tDelete Field: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        del drop_fields

        # Get a record count to see if data is present; we don't want to add data
        getcount = arcpy.management.GetCount(table_name_tmp_stats)[0]
        arcpy.AddMessage(f'\t\t> {os.path.basename(table_name_tmp_stats)} has {getcount} records')
        del getcount

        arcpy.AddMessage(f'\t\t> Add Variable, Dimensions, and ImageName \n\t\t> Fields to {os.path.basename(table_name_tmp_stats)} table\n')

        table_name_tmp_new_fields = ['CoreSpecies', 'Variable', 'Value', 'Dimensions', 'ImageName',]

        tb_fields = [f.name for f in arcpy.ListFields(table_name_tmp_stats) if f.type not in ['Geometry', 'OID']]

        table_name_tmp_new_fields = [f for f in table_name_tmp_new_fields if f not in tb_fields]
        del tb_fields

        field_definitions = dismap_tools.field_definitions(csv_data_folder, "")

        field_definition_list = []
        for table_name_tmp_new_field in table_name_tmp_new_fields:
            field_definition_list.append([field_definitions[table_name_tmp_new_field]["field_name"],
                                          field_definitions[table_name_tmp_new_field]["field_type"],
                                          field_definitions[table_name_tmp_new_field]["field_aliasName"],
                                          field_definitions[table_name_tmp_new_field]["field_length"]])
            del table_name_tmp_new_field
        del field_definitions
        del table_name_tmp_new_fields

        arcpy.AddMessage(f"Adding Fields to Table: {table_name}_tmp")
        arcpy.management.AddFields(in_table = table_name_tmp_stats, field_description = field_definition_list, template="")
        arcpy.AddMessage("\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        del field_definition_list

        fields = [f.name for f in arcpy.ListFields(table_name_tmp_stats) if f.type not in ['Geometry', 'OID']]

        arcpy.AddMessage(fields)
        # ['DatasetCode', 'Region', 'Season', 'SummaryProduct', 'DistributionProjectName',
        #  'Year', 'StdTime', 'FilterRegion', 'FilterSubRegion', 'CoreSpecies', 'Variable',
        # 'Value', 'Dimensions', 'ImageName']

        with arcpy.da.UpdateCursor(table_name_tmp_stats, fields) as cursor:
            for row in cursor:
                variable   = "Core Species Richness"
                value      = "Core Species Richness"
                dimensions = "StdTime"
                imagename  = f"{table_name}_{variable.replace(' ','_')}_{str(row[5])}"
                row[7]     = filter_region.replace("''", "'")
                row[8]     = filter_subregion.replace("''", "'")
                row[9]     = "Yes"
                row[10]    = variable
                row[11]    = value
                row[12]    = dimensions
                row[13]    = imagename
                arcpy.AddMessage(row)
                cursor.updateRow(row)
                del row, variable, value, dimensions, imagename
        del cursor

        arcpy.management.Append(inputs = table_name_tmp_stats, target = layer_species_year_image_name, schema_type="NO_TEST", field_mapping="", subtype="")

        # The following calculates the time stamp for the Dataset
        # Use Update Cursor instead of Calculate Field

        with arcpy.da.UpdateCursor(table_name_tmp_stats, fields) as cursor:
            for row in cursor:
                # #variable   = "Core Species Richness" if row[8] == "Yes" else "Species Richness"
                variable   = "Species Richness"
                value      = "Species Richness"
                dimensions = "StdTime"
                imagename  = f"{table_name}_{variable.replace(' ','_')}_{str(row[5])}"
                row[7]     = filter_region.replace("''", "'")
                row[8]     = filter_subregion.replace("''", "'")
                row[9]     = "No"
                row[10]    = variable
                row[11]    = value
                row[12]    = dimensions
                row[13]    = imagename
                arcpy.AddMessage(row)
                cursor.updateRow(row)
                del row, variable, value, dimensions, imagename
        del fields, cursor

        arcpy.management.Append(inputs = table_name_tmp_stats, target = layer_species_year_image_name, schema_type="NO_TEST", field_mapping="", subtype="")

        del table_name_tmp_stats, table_name_tmp_fields

        del table_name_tmp

        # Alter Field Names to layer_species_year_image_name
        dismap_tools.alter_fields(csv_data_folder, layer_species_year_image_name)

        dataset_md = md.Metadata(layer_species_year_image_name)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md

        # End of business logic for the worker function
        arcpy.AddMessage(f"Processing for: {table_name} complete")

        arcpy.env.workspace = region_gdb
        datasets = [ds for ds in arcpy.ListTables("*") if not ds.endswith("LayerSpeciesYearImageName")]
        for dataset in datasets:
##            arcpy.AddMessage(f"Deleting: '{dataset}'")
##            arcpy.management.Delete(dataset)
            del dataset
        del datasets

        # Declared Variables
        del filter_region, filter_subregion
        del datasets_table, datasets_table_fields, region_table_fields
        del layer_species_year_image_name, layer_species_year_image_name_fields
        del csv_data_folder, region_table, scratch_workspace, table_name
        # Imports
        del md, dismap_tools
        # Function parameter
        del region_gdb
    except KeyboardInterrupt:
        sys.exit()
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(f"Caught an arcpy.ExecuteWarning error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddWarning(arcpy.GetMessages(1))
    except arcpy.ExecuteError:
        arcpy.AddError(f"Caught an arcpy.ExecuteError error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        sys.exit()
    except SystemExit as se:
        arcpy.AddError(f"Caught an SystemExit error: {se} in the '{inspect.stack()[0][3]}' function.")
        sys.exit()
    except Exception as e:
        arcpy.AddError(f"Caught an Exception error: {e} in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
    except:  # noqa: E722
        arcpy.AddError(f"Caught an except error in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
    else:  # noqa: E722
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk:
            arcpy.AddMessage(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##")
        del rk
        return True
    finally:
        pass

def script_tool(project_gdb=""):
    try:
        from create_species_year_image_name_table_director import preprocessing
        from time import gmtime, localtime, strftime, time
        # Set a start time so that we can see how log things take
        start_time = time()
        arcpy.AddMessage(f"{'-' * 80}")
        arcpy.AddMessage(f"Python Script:  {os.path.basename(__file__)}")
        arcpy.AddMessage(f"Location:       .. {'/'.join(__file__.split(os.sep)[-4:])}")
        arcpy.AddMessage(f"Python Version: {sys.version}")
        arcpy.AddMessage(f"Environment:    {os.path.basename(sys.exec_prefix)}")
        arcpy.AddMessage(f"Start Time:     {strftime('%a %b %d %I:%M %p', localtime(start_time))}")
        arcpy.AddMessage(f"{'-' * 80}\n")

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        ##        # Set worker parameters
        ##        #table_name = "AI_IDW"
        ##        table_name = "HI_IDW"
        ##        #table_name = "NBS_IDW"
        ##        #table_name = "ENBS_IDW"

        #table_names = ["NEUS_FAL_IDW", "NEUS_SPR_IDW", "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",]
        table_names = ["NEUS_FAL_IDW"]

        preprocessing(project_gdb=project_gdb, table_names=table_names, clear_folder=True)

        # Set varaibales
        project_folder    = os.path.dirname(project_gdb)
        scratch_folder    = os.path.join(project_folder, "Scratch")
        del project_folder

        for table_name in table_names:
            region_gdb = os.path.join(scratch_folder, f"{table_name}.gdb")

            try:
                pass
                worker(region_gdb=region_gdb)
            except SystemExit:
                arcpy.AddError(arcpy.GetMessages(2))
                traceback.print_exc()
                sys.exit()

            del table_name, region_gdb

        del table_names

        # Declared Varaiables
        del scratch_folder
        # Imports

        # Function Parameters
        del project_gdb

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        hours, rem = divmod(end_time-start_time, 3600)
        minutes, seconds = divmod(rem, 60)
        arcpy.AddMessage(f"\n{'-' * 80}")
        arcpy.AddMessage(f"Python script: {os.path.basename(__file__)}")
        arcpy.AddMessage(f"Start Time:    {strftime('%a %b %d %I:%M %p', localtime(start_time))}")
        arcpy.AddMessage(f"End Time:      {strftime('%a %b %d %I:%M %p', localtime(end_time))}")
        arcpy.AddMessage(f"Elapsed Time   {int(hours):0>2}:{int(minutes):0>2}:{seconds:05.2f} (H:M:S)")
        arcpy.AddMessage(f"{'-' * 80}")
        del hours, rem, minutes, seconds
        del elapse_time, end_time, start_time
        del gmtime, localtime, strftime, time

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
        return False
    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
        return False
    else:
        return True

if __name__ == '__main__':
    try:
        project_gdb = arcpy.GetParameterAsText(0)
        if not project_gdb:
            project_gdb = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\February 1 2026\\February 1 2026.gdb")
        else:
            pass

        script_tool(project_gdb)

        arcpy.SetParameterAsText(1, "Result")

        del project_gdb

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)