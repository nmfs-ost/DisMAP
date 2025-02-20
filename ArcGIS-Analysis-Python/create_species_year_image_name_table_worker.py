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
import os, sys # built-ins first
import traceback
import importlib
import inspect

import arcpy # third-parties second

sys.path.append(os.path.dirname(__file__))

def line_info(msg):
    f = inspect.currentframe()
    i = inspect.getframeinfo(f.f_back)
    return f"Script: {os.path.basename(i.filename)}\n\tNear Line: {i.lineno}\n\tFunction: {i.function}\n\tMessage: {msg}"

def worker(region_gdb=""):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(rf"{region_gdb}"):
            raise SystemExit(line_info(f"{os.path.basename(region_gdb)} is missing!!"))

        # Import the dismap module to access tools
        import dismap
        importlib.reload(dismap)

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
        scratch_workspace = rf"{scratch_folder}\scratch.gdb"
        in_table          = rf"{region_gdb}\{table_name}"
        csv_data_folder   = rf"{project_folder}\CSV Data"
        del project_folder, scratch_folder

        # Set basic workkpace variables
        arcpy.env.workspace                = region_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput             = True
        arcpy.env.parallelProcessingFactor = "100%"

        layer_species_year_image_name = rf"{region_gdb}\LayerSpeciesYearImageName"

        arcpy.AddMessage(f"Create Table: LayerSpeciesYearImageName" )
        arcpy.management.CreateTable(out_path       = region_gdb,
                                     out_name       = "LayerSpeciesYearImageName",
                                     template       = "",
                                     config_keyword = "",
                                     out_alias      = "")
        arcpy.AddMessage("\tCreate Table: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        # Add Fields to layer_species_year_image_name
        dismap.add_fields(csv_data_folder, layer_species_year_image_name)

        arcpy.AddMessage(f"Processing: {table_name}" )

        species_filter_table = os.path.join(region_gdb, "Species_Filter")

        species_filter_table_fields = [f.name for f in arcpy.ListFields(species_filter_table) if f.type not in ['Geometry', 'OID']]

        arcpy.AddMessage(f"Creating the Species_Filter dictionary" )
        species_filter = {}
        with arcpy.da.SearchCursor(species_filter_table, species_filter_table_fields) as cursor:
            for row in cursor:
                species_filter[row[0]] = [row[1],row[2],row[3],row[4],row[5],row[6]]
                del row
        del cursor, species_filter_table, species_filter_table_fields

        arcpy.AddMessage(f"Defining the case fields")

        layer_species_year_image_name_fields = [f.name for f in arcpy.ListFields(layer_species_year_image_name) if f.type not in ['Geometry', 'OID']]
        in_table_fields                      = [f.name for f in arcpy.ListFields(in_table) if f.type not in ['Geometry', 'OID']]
        case_fields                          = [f for f in layer_species_year_image_name_fields if f in in_table_fields]
        del layer_species_year_image_name_fields, in_table_fields
        del in_table

        # Execute Statistics to get unique set of records
        table_name_tmp = table_name+"_tmp"
        stats_fields = [[f"{f}", "COUNT"] for f in case_fields]

        arcpy.AddMessage(f"\tStatistics Analysis of {table_name} Table")
        arcpy.analysis.Statistics(table_name, table_name_tmp, stats_fields, case_fields)
        arcpy.AddMessage("\tStatistics Analysis: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        del stats_fields, case_fields

        table_name_tmp_fields = [f.name for f in arcpy.ListFields(table_name_tmp) if f.type not in ['Geometry', 'OID']]

        table_name_tmp_drop_fields = ";".join([f for f in table_name_tmp_fields if "FREQUENCY" in f or "COUNT" in f])
        del table_name_tmp_fields

        arcpy.management.DeleteField(in_table=table_name_tmp, drop_field=table_name_tmp_drop_fields)
        del table_name_tmp_drop_fields

        # Get a record count to see if data is present; we don't want to add data
        getcount = arcpy.management.GetCount(table_name_tmp)[0]
        arcpy.AddMessage(f"\t{table_name_tmp} has {getcount} records")
        #arcpy.AddMessage(f"\t{os.path.basename(d)} has {arcpy.management.GetCount(d)[0]} records")
        del getcount

        arcpy.AddMessage(f"\tAdding the Variable, Dimensions, and ImageName Fields to the {table_name_tmp} table")

        table_name_tmp_new_fields = ['FilterRegion', 'FilterSubRegion', 'TaxonomicGroup',
                                      'ManagementBody', 'ManagementPlan', 'Variable',
                                      'Value', 'Dimensions', 'ImageName',
                                     ]
        table_name_tmp_fields = [f.name for f in arcpy.ListFields(table_name_tmp) if f.type not in ['Geometry', 'OID']]

        table_name_tmp_new_fields = [f for f in table_name_tmp_new_fields if f not in table_name_tmp_fields]

        field_definitions = dismap.field_definitions(csv_data_folder, "")

        field_definition_list = []
        for table_name_tmp_new_field in table_name_tmp_new_fields:
            field_definition_list.append([field_definitions[table_name_tmp_new_field]["field_name"],
                                          field_definitions[table_name_tmp_new_field]["field_type"],
                                          field_definitions[table_name_tmp_new_field]["field_alias"],
                                          field_definitions[table_name_tmp_new_field]["field_length"]])
            del table_name_tmp_new_field
        del field_definitions

        arcpy.AddMessage(f"Adding Fields to Table: {table_name}_tmp")
        arcpy.management.AddFields(in_table = table_name_tmp, field_description = field_definition_list, template="")
        arcpy.AddMessage("\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        del field_definition_list

        del table_name_tmp_new_fields, table_name_tmp_fields

        datasets_table = rf"{region_gdb}\Datasets"

        filter_region    = [row[0] for row in arcpy.da.SearchCursor(datasets_table, "FilterRegion", where_clause = f"TableName = '{table_name}'")][0]
        filter_subregion = [row[0] for row in arcpy.da.SearchCursor(datasets_table, "FilterSubRegion", where_clause = f"TableName = '{table_name}'")][0]
        del datasets_table

        # The following calculates the time stamp for the Dataset
        # Use Update Cursor instead of Calculate Field
        fields = ["DatasetCode", "Region", "Species", "Year", "FilterRegion", "FilterSubRegion", "TaxonomicGroup", "ManagementBody", "ManagementPlan",
                  "Variable", "Value", "Dimensions", "ImageName"]

        with arcpy.da.UpdateCursor(table_name_tmp, fields) as cursor:
            for row in cursor:
                variable   = row[2].replace("(","").replace(")","").replace(".","")
                value      = "Species"
                dimensions = "StdTime"
                imagename  = f"{table_name}_{variable.replace(' ','_')}_{str(row[3])}"
                if row[2] in species_filter:
                    row[4]  = filter_region
                    row[5]  = filter_subregion
                    row[6]  = species_filter[row[2]][1] # TaxonomicGroup
                    row[7]  = species_filter[row[2]][4] # ManagementBody
                    row[8]  = species_filter[row[2]][5] # ManagementPlan
                else:
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
        del filter_region, filter_subregion
        del species_filter

        arcpy.management.Append(inputs = table_name_tmp, target = layer_species_year_image_name, schema_type="NO_TEST", field_mapping="", subtype="")
        arcpy.AddMessage("\tAppend: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        table_name_tmp_fields = [f.name for f in arcpy.ListFields(table_name_tmp) if f.type not in ['Geometry', 'OID']]

        if "CoreSpecies" in table_name_tmp_fields:

            case_fields = [f.name for f in arcpy.ListFields(table_name_tmp) if f.type not in ['Geometry', 'OID'] and f.name not in ["CoreSpecies", "Species", "CommonName", "SpeciesCommonName", "CommonNameSpecies", "TaxonomicGroup", "ManagementBody", "ManagementPlan", "Variable", "Value", "Dimensions", "ImageName"]]

            # Execute Statistics to get unique set of records
            table_name_tmp_stats = table_name_tmp+"_stats"

            stats_fields = [[f"{f}", "COUNT"] for f in case_fields]

            arcpy.AddMessage(f"\tStatistics Analysis of '{table_name}_tmp' Table")

            arcpy.analysis.Statistics(table_name_tmp, table_name_tmp_stats, stats_fields, case_fields)
            arcpy.AddMessage("\tStatistics Analysis: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
            del stats_fields, case_fields

            fields = [f.name for f in arcpy.ListFields(table_name_tmp_stats) if f.type not in ['Geometry', 'OID']]

            drop_fields = ";".join([f for f in fields if "FREQUENCY" in f or "COUNT" in f])
            del fields

            arcpy.management.DeleteField(in_table=table_name_tmp_stats, drop_field=drop_fields)
            arcpy.AddMessage("\tDelete Field: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            del drop_fields

            # Get a record count to see if data is present; we don't want to add data
            getcount = arcpy.management.GetCount(table_name_tmp_stats)[0]
            arcpy.AddMessage(f'\t\t> {os.path.basename(table_name_tmp_stats)} has {getcount} records')
            del getcount

            arcpy.AddMessage('\t\t> Add Variable, Dimensions, and ImageName \n\t\t> Fields to {os.path.basename(table_name_tmp_stats)} table')

            table_name_tmp_new_fields = ['CoreSpecies', 'Variable', 'Value', 'Dimensions', 'ImageName',]

            tb_fields = [f.name for f in arcpy.ListFields(table_name_tmp_stats) if f.type not in ['Geometry', 'OID']]

            table_name_tmp_new_fields = [f for f in table_name_tmp_new_fields if f not in tb_fields]
            del tb_fields

            field_definitions = dismap.field_definitions(csv_data_folder, "")

            field_definition_list = []
            for table_name_tmp_new_field in table_name_tmp_new_fields:
                field_definition_list.append([field_definitions[table_name_tmp_new_field]["field_name"],
                                              field_definitions[table_name_tmp_new_field]["field_type"],
                                              field_definitions[table_name_tmp_new_field]["field_alias"],
                                              field_definitions[table_name_tmp_new_field]["field_length"]])
                del table_name_tmp_new_field
            del field_definitions
            del table_name_tmp_new_fields

            arcpy.AddMessage(f"Adding Fields to Table: {table_name}_tmp")
            arcpy.management.AddFields(in_table = table_name_tmp_stats, field_description = field_definition_list, template="")
            arcpy.AddMessage("\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

            del field_definition_list

            datasets_table = rf"{region_gdb}\Datasets"

            filter_region    = [row[0] for row in arcpy.da.SearchCursor(datasets_table, "FilterRegion", where_clause = f"TableName = '{table_name}'")][0]
            filter_subregion = [row[0] for row in arcpy.da.SearchCursor(datasets_table, "FilterSubRegion", where_clause = f"TableName = '{table_name}'")][0]
            del datasets_table

            fields = [f.name for f in arcpy.ListFields(table_name_tmp_stats) if f.type not in ['Geometry', 'OID']]

            with arcpy.da.UpdateCursor(table_name_tmp_stats, fields) as cursor:
                for row in cursor:
                    variable   = "Core Species Richness"
                    value      = "Core Species Richness"
                    dimensions = "StdTime"
                    imagename  = f"{table_name}_{variable.replace(' ','_')}_{str(row[4])}"
                    row[6]     = filter_region
                    row[7]     = filter_subregion
                    row[8]     = "Yes"
                    row[9]     = variable
                    row[10]    = value
                    row[11]    = dimensions
                    row[12]    = imagename
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
                    imagename  = f"{table_name}_{variable.replace(' ','_')}_{str(row[4])}"
                    row[6]     = filter_region
                    row[7]     = filter_subregion
                    row[8]     = "No"
                    row[9]     = variable
                    row[10]    = value
                    row[11]    = dimensions
                    row[12]    = imagename
                    #print(row)
                    cursor.updateRow(row)
                    del row, variable, value, dimensions, imagename
            del fields, cursor

            del filter_region, filter_subregion

            arcpy.management.Append(inputs = table_name_tmp_stats, target = layer_species_year_image_name, schema_type="NO_TEST", field_mapping="", subtype="")

            del table_name_tmp_stats, table_name_tmp_fields
        del table_name_tmp

        ws, ds = os.path.split(layer_species_year_image_name)
        region_layer_species_year_image_name = rf"{ws}\{table_name}_{ds}"
        del ws, ds

        arcpy.management.Rename(layer_species_year_image_name, region_layer_species_year_image_name)
        del layer_species_year_image_name

        # Gather results to be returned
        results = [region_layer_species_year_image_name]
        del region_layer_species_year_image_name

        # End of business logic for the worker function
        arcpy.AddMessage(f"Processing for: {table_name} complete")

        # Basic variables
        del table_name, scratch_workspace, csv_data_folder
        # Imports
        del dismap
        # Function parameter
        del region_gdb

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(str(traceback.print_exc()) + arcpy.GetMessages())
        raise SystemExit
    except arcpy.ExecuteError:
        arcpy.AddError(str(traceback.print_exc()) + arcpy.GetMessages())
        raise SystemExit
    except SystemExit as se:
        arcpy.AddError(str(se))
        raise SystemExit
    except:
        arcpy.AddError(str(traceback.print_exc()))
        raise SystemExit
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise SystemExit(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def main(project):
    try:
        # Imports
        from create_species_year_image_name_table_worker import worker

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput             = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Set varaibales
        base_project_folder = os.path.dirname(os.path.dirname(__file__))
        project_gdb         = rf"{base_project_folder}\{project}\{project}.gdb"
        project_folder      = rf"{base_project_folder}\{project}"
        scratch_folder      = rf"{project_folder}\Scratch"
        del project_folder, base_project_folder

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        # Create project scratch workspace, if missing
        if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(rf"{scratch_folder}")
            if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"scratch")

        # Set worker parameters
        #table_name = "AI_IDW"
        table_name = "HI_IDW"
        #table_name = "NBS_IDW"

        region_gdb        = rf"{scratch_folder}\{table_name}.gdb"
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        # Create worker scratch workspace, if missing
        if not arcpy.Exists(scratch_workspace):
            os.makedirs(rf"{scratch_folder}\{table_name}")
            if not arcpy.Exists(scratch_workspace):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}\{table_name}", f"scratch")
        del scratch_workspace

        # Setup worker workspace and copy data
        datasets = [rf"{project_gdb}\Datasets", rf"{project_gdb}\Species_Filter", rf"{project_gdb}\{table_name}"]
        if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):

            arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"{table_name}")
            arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\Datasets", rf"{region_gdb}\Datasets")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\Species_Filter", rf"{region_gdb}\Species_Filter")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\{table_name}", rf"{region_gdb}\{table_name}")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        else:
            arcpy.AddWarning(f"One or more datasets contains zero records!!")
            for d in datasets:
                arcpy.AddMessage(f"\t{os.path.basename(d)} has {arcpy.management.GetCount(d)[0]} records")
                del d
            raise SystemExit

        if "datasets" in locals().keys(): del datasets

        del scratch_folder, project_gdb

        results  = []

        try:

            result = worker(region_gdb=region_gdb)
            results.extend(result); del result

        except SystemExit as se:
            raise SystemExit(str(se))

        if results:
            if type(results).__name__ == "bool":
                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
                arcpy.AddMessage(f"Result: {results}")
            elif type(results).__name__ == "str":
                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
                arcpy.AddMessage(f"Result: {results}")
            elif type(results).__name__ == "list":
                if type(results[0]).__name__ == "list":
                        results = [r for rt in results for r in rt]
                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
                for result in results:
                    arcpy.AddMessage(f"Result: {result}")
                del result
            else:
                arcpy.AddMessage(f"No results returned!!!")
        else:
            arcpy.AddMessage(f"No results in '{inspect.stack()[0][3]}'")

        try:
            Delete = True # Can not seem to remove the lock
            if Delete:
                arcpy.AddMessage(f"\nDelete GDB: {os.path.basename(region_gdb)}")
                arcpy.management.Delete(region_gdb)
                arcpy.AddMessage("\tDelete: {0} {1}\n".format(f"{table_name}.gdb", arcpy.GetMessages(0).replace("\n", '\n\t')))

                arcpy.AddMessage(f"Delete Folder: {os.path.basename(region_gdb).replace('.gdb','')}")
                arcpy.management.Delete(region_gdb.replace(".gdb",""))
                arcpy.AddMessage("\tDelete: {0} {1}\n".format(f"{table_name}", arcpy.GetMessages(0).replace("\n", '\n\t')))
            else:
                pass
            del Delete
        except:
            if "Delete" in locals().keys(): del Delete
            arcpy.AddError(arcpy.GetMessages(2))

        del region_gdb, table_name
        del worker
        del project

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(str(traceback.print_exc()) + arcpy.GetMessages())
        raise SystemExit
    except arcpy.ExecuteError:
        arcpy.AddError(str(traceback.print_exc()) + arcpy.GetMessages())
        raise SystemExit
    except SystemExit as se:
        arcpy.AddError(str(se))
        raise SystemExit
    except:
        arcpy.AddError(str(traceback.print_exc()))
        raise SystemExit
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise SystemExit(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

if __name__ == '__main__':
    try:
        # Import this Python module
        import create_species_year_image_name_table_worker
        importlib.reload(create_species_year_image_name_table_worker)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        #project = "May 1 2024"
        project = "July 1 2024"

        # Tested on 7/30/2024 -- PASSED
        main(project=project)

        del project

        from time import localtime, strftime
        print(f"\n{'-' * 90}")
        print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(f"{'-' * 90}")
        del localtime, strftime

    except SystemExit:
        pass
    except:
        traceback.print_exc()
    else:
        leave_out_keys = ["leave_out_keys"]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[1][3]}': ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
