# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     29/02/2024
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

# custom callback function
def custom_callback(result):
    print(f'Callback got values: {result}', flush=True)

# custom error callback function
def custom_error_callback(error):
    print(f'Got an error: {error}', flush=True)

def worker(region_gdb=""):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(rf"{region_gdb}"):
            raise Exception(line_info(f"{os.path.basename(region_gdb)} is missing!!"))

        # Import the dismap module to access tools
        import dismap
        importlib.reload(dismap)

        # Import
        import pandas as pd
        import numpy as np
        import warnings

        # Use all of the cores on the machine
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.overwriteOutput = True

        # Set History and Metadata logs, set serverity and message levelarcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        table_name        = os.path.basename(region_gdb).replace(".gdb", "")
        scratch_folder    = os.path.dirname(region_gdb)
        project_folder    = os.path.dirname(scratch_folder)
        csv_data_folder   = rf"{project_folder}\CSV Data"
        process_table     = rf"{csv_data_folder}\{table_name}.csv"
        scratch_workspace = rf"{scratch_folder}\scratch.gdb"
        del scratch_folder

        # Set basic workkpace variables
        arcpy.env.workspace        = region_gdb
        arcpy.env.scratchWorkspace = scratch_workspace

        field_csv_dtypes = dismap.dTypesCSV(csv_data_folder, table_name)
        field_gdb_dtypes = dismap.dTypesGDB(csv_data_folder, table_name)

        # DatasetCode, CSVFile, TransformUnit, TableName, GeographicArea, CellSize,
        # PointFeatureType, FeatureClassName, Region, Season, DateCode, Status,
        # DistributionProjectCode, DistributionProjectName, SummaryProduct,
        # FilterRegion, FilterSubRegion, FeatureServiceName, FeatureServiceTitle,
        # MosaicName, MosaicTitle, ImageServiceName, ImageServiceTitle

        # Get values for table_name from Datasets table
        fields = ["TableName", "GeographicArea", "DatasetCode", "Region", "Season", "DistributionProjectCode"]
        region_list = [row for row in arcpy.da.SearchCursor(rf"{region_gdb}\Datasets", fields, where_clause = f"TableName = '{table_name}'")][0]
        del table_name

        # Assigning variables from items in the chosen table list
        # ['AI_IDW', 'AI_IDW_Region', 'AI', 'Aleutian Islands', None, 'IDW']
        table_name      = region_list[0]
        geographic_area = region_list[1]
        datasetcode     = region_list[2]
        region          = region_list[3]
        season          = region_list[4]
        distri_code     = region_list[5]
        del region_list

        # Start of business logic for the worker function
        print(f"Reading {table_name} CSV File\n", flush=True)

        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_colwidth", 10)
        pd.set_option("display.min_rows", 2)
        pd.set_option("display.max_rows", 5)
        pd.set_option("display.expand_frame_repr", False)


        encoding, index_column = dismap.get_encoding_index_col(process_table)

        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            # DataFrame
            df = pd.read_csv(
                             process_table,
                             index_col = index_column,
                             encoding  = encoding,
                             delimiter = ",",
                             dtype     = field_csv_dtypes,
                            )
        del encoding, index_column

##        with warnings.catch_warnings():
##            warnings.simplefilter(action='ignore', category=FutureWarning)
##            # DataFrame
##            df = pd.read_csv(
##                             process_table,
##                             index_col = 0,
##                             #encoding  = "utf-8",
##                             encoding  = "unicode_escape",
##                             delimiter = ",",
##                             dtype     = field_csv_dtypes,
##                            )

        # Set all NA values to np.nan, in place
        #df.fillna(np.nan, inplace = True)

        # Old -> year, lon_UTM, lat_UTM, lat, lon, depth_m, median_est,                        spp_sci, spp_common, wtcpue, transformed_value, transform_unit
        # New -> year, Easting, Northing,          depth_m, median_est, mean_est, est5, est95, spp_sci, spp_common

        # Rename columns using the dictionary below and the defined list of field names
        # Easting,Northing,year,depth_m,median_est,mean_est,est5,est95,spp_sci,spp_common
        # mean_est, est5, est95
        column_names = {
                        "common"                  : "CommonName",
                        "depth"                   : "Depth",
                        "depth_m"                 : "Depth",
                        "DistributionProjectName" : "DistributionProjectName",
                        "est5"                    : "Estimate5",
                        "est95"                   : "Estimate95",
                        "haulid"                  : "SampleID",
                        "lat"                     : "Latitude",
                        "lat_UTM"                 : "Northing",
                        "lon"                     : "Longitude",
                        "lon_UTM"                 : "Easting",
                        "mean_est"                : "MeanEstimate",
                        "median_est"              : "MedianEstimate",
                        "region"                  : "Region",
                        "sampleid"                : "SampleID",
                        "spp"                     : "Species",
                        "spp_common"              : "CommonName",
                        "spp_sci"                 : "Species",
                        "stratum"                 : "Stratum",
                        "stratumarea"             : "StratumArea",
                        "transformed"             : "MapValue",
                        "wtcpue"                  : "WTCPUE",
                        "year"                    : "Year",
                       }

        df.rename(columns=column_names, inplace=True)
        del column_names

        # Print column names
        #for column in list(df.columns): print(column); del column # print columns

        # ###--->>>
        print(f"Inserting additional columns into the dataframe\n", flush=True)

        print(f"\tInserting 'DatasetCode' column into: {table_name}", flush=True)
        df.insert(0, "DatasetCode", datasetcode)
        del datasetcode

        print(f"\tInserting 'Region' column into: {table_name}", flush=True)
        if "Region" not in list(df.columns):
            df.insert(df.columns.get_loc("DatasetCode")+1, "Region", f"{region}")

        print(f"\tInserting 'StdTime' column into: {table_name}", flush=True)
        if "StdTime" not in list(df.columns):
            df.insert(df.columns.get_loc("Year")+1, "StdTime", pd.to_datetime(df["Year"], format="%Y").dt.tz_localize('Etc/GMT+12'))

        print(f"\tInserting 'MapValue' column into: {table_name}", flush=True)
        if "MapValue" not in list(df.columns):
            df.insert(df.columns.get_loc("WTCPUE")+1, "MapValue", np.nan)
            #-->> MapValue
            print(f"\tCalculating the MapValue values", flush=True)
            df["MapValue"] = df["WTCPUE"].pow((1.0/3.0))

        print(f"\tInserting 'SpeciesCommonName' column into: {table_name}", flush=True)
        if "SpeciesCommonName" not in list(df.columns):
            df.insert(df.columns.get_loc("CommonName")+1, "SpeciesCommonName", "")

        print(f"\tInserting 'CommonNameSpecies' column into: {table_name}", flush=True)
        if "CommonNameSpecies" not in list(df.columns):
            df.insert(df.columns.get_loc("SpeciesCommonName")+1, "CommonNameSpecies", "")

        # Test if 'IDW' in table name
        if "IDW" in table_name:
            print(f"\tInserting 'Season' {season} column into: {table_name}", flush=True)
            if "Season" not in list(df.columns):
                df.insert(df.columns.get_loc("Region")+1, "Season", season if season != None else "")

            print(f"\tInserting 'SummaryProduct' column into: {table_name}", flush=True)
            if "SummaryProduct" not in list(df.columns):
                df.insert(df.columns.get_loc("Season")+1, "SummaryProduct", "Yes")

            print(f"\tInserting 'TransformUnit' column into: {table_name}", flush=True)
            if "TransformUnit" not in list(df.columns):
                df.insert(df.columns.get_loc("MapValue")+1, "TransformUnit", "cuberoot")

            print(f"\tInserting 'CoreSpecies' column into: {table_name}", flush=True)
            if "CoreSpecies" not in list(df.columns):
                df.insert(df.columns.get_loc("CommonNameSpecies")+1, "CoreSpecies", "No")

            print(f"\tCalculate Null for 'StratumArea' column into: {table_name}", flush=True)
            if "StratumArea" in list(df.columns):
                df["StratumArea"].fillna(np.nan, inplace = True)

            print(f"\tCalculate Null for 'DistributionProjectName' column into: {table_name}", flush=True)
            if "DistributionProjectName" in list(df.columns):
                df["DistributionProjectName"].fillna(np.nan, inplace = True)

        # Test if 'GLMME' or 'GFDL' in region name
        if any(t for t in ["GLMME", "GFDL"] if t in table_name):
            print(f"\tInserting 'SummaryProduct' column into: {table_name}", flush=True)
            if "SummaryProduct" not in list(df.columns):
                df.insert(df.columns.get_loc("Region")+1, "SummaryProduct", "No")

            print(f"\tInserting 'StandardError' column into: {table_name}", flush=True)
            if "StandardError" not in list(df.columns):
                df.insert(df.columns.get_loc("MapValue")+1, "StandardError", np.nan)

            print(f"\tInserting 'TransformUnit' column into: {table_name}", flush=True)
            if "TransformUnit" not in list(df.columns):
                df.insert(df.columns.get_loc("StandardError")+1, "TransformUnit", "ln")

            print(f"\tCalculate Null for 'Easting' column into: {table_name}", flush=True)
            if "Easting" in list(df.columns):
                df["Easting"].fillna(np.nan, inplace = True)

            print(f"\tCalculate Null for 'Northing' column into: {table_name}", flush=True)
            if "Northing" in list(df.columns):
                df["Northing"].fillna(np.nan, inplace = True)

            print(f"\tCalculate Null for 'MedianEstimate' column into: {table_name}", flush=True)
            if "MedianEstimate" in list(df.columns):
                df["MedianEstimate"].fillna(np.nan, inplace = True)

        print(f"\tCalculate Null for 'WTCPUE' column into: {table_name}", flush=True)
        if "WTCPUE" in list(df.columns):
            df["WTCPUE"].fillna(np.nan, inplace = True)

        print(f"\tCalculate Null for 'Latitude' column into: {table_name}", flush=True)
        if "Latitude" in list(df.columns):
            df["Latitude"].fillna(np.nan, inplace = True)

        print(f"\tCalculate Null for 'Longitude' column into: {table_name}", flush=True)
        if "Longitude" in list(df.columns):
            df["Longitude"].fillna(np.nan, inplace = True)

        print(f"\tCalculate Null for 'Depth' column into: {table_name}", flush=True)
        if "Depth" in list(df.columns):
            df["Depth"].fillna(np.nan, inplace = True)

        del region, season

        # ###--->>>
        #print(f"Updating and calculating new values for some columns\n")
        #-->> CommonName
        print(f"\tSetting 'NaN' in 'CommonName' to ''", flush=True)
        #df.loc[df['CommonName'] == 'nan', 'CommonName'] =  ""
        df["CommonName"].fillna("", inplace=True)

        print(f"\tSetting 'CommonName' unicode'", flush=True)
        # Cast text as Unicode in the CommonName field
        df["CommonName"] = df["CommonName"].astype("unicode")

        #-->> SpeciesCommonName
        print(f"\tCalculating SpeciesCommonName and setting it to 'Species (CommonName)'", flush=True)
        df["SpeciesCommonName"] = np.where(df["CommonName"] != "", df["Species"] + ' (' + df["CommonName"] + ')', "")

        #-->> CommonNameSpecies
        print(f"\tCalculating  CommonNameSpecies and setting it to 'CommonName (Species)'", flush=True)
        df["CommonNameSpecies"] = np.where(df["CommonName"] != "", df["CommonName"] + ' (' + df["Species"] + ')', "")

        print(f"\tReplacing Infinity values with Nulls", flush=True)
        # Replace Inf with Nulls
        # For some cell values in the 'WTCPUE' column, there is an Inf
        # value representing an infinit
        df.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Left justify the column names
        #df.columns = pd.Index([col.ljust(10) for col in df.columns])

        table_definition = dismap.table_definitions(csv_data_folder, table_name)

        # altering the DataFrame
        df = df[table_definition]
        del table_definition

        #raise Exception(f"Line Number: {traceback.extract_stack()[-1].lineno}")

        pd.set_option("display.max_colwidth", 12)

        # Change Table Style
        df.style.set_table_styles([{'selector': 'td', 'props': 'white-space: nowrap !important;'}])

        print(f"\nDataframe report:\n{df.head(5)}\n", flush=True)

        print(f"Converting the Dataframe to an NumPy Array\n", flush=True)
        try:
            array = np.array(np.rec.fromrecords(df.values), dtype = field_gdb_dtypes)
        except:
            raise SystemExit(traceback.print_exc())

        del field_gdb_dtypes
        del field_csv_dtypes

        del df # delete dataframe
        # Imports
        del pd, np

        del process_table # delete passed variables

        # Temporary table
        #tmp_table = f"memory\{table_name.lower()}_tmp"
        tmp_table = rf"{region_gdb}\{table_name.lower()}_tmp"
        try:
            arcpy.da.NumPyArrayToTable(array, tmp_table)
            del array
        except:
            raise arcpy.ExecuteError(arcpy.GetMessages())

        desc = arcpy.da.Describe(tmp_table)
        fields = [f.name for f in desc["fields"] if f.type == "String"]
        #fields = ["Season", "Species", "CommonName", "SpeciesCommonName", "CommonNameSpecies", "Stratum"]
        oid    = desc["OIDFieldName"]
        # Use SQL TOP to sort field values
        print(f"{', '.join(fields)}", flush=True)
        for row in arcpy.da.SearchCursor(tmp_table, fields, f"{oid} <= 5"):
            print(row)
            del row
        del desc, fields, oid

        out_table = rf"{region_gdb}\{table_name}"
        #out_table = rf"{region_gdb}\{table_name}_TABLE"

        print(f"Copying the {table_name} Table from memory to the GDB", flush=True)
        arcpy.management.CopyRows(tmp_table, out_table, "")
        print("Copy Rows: \t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')), flush=True)
        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        # Test if 'IDW' in region name
        if distri_code == "IDW":
            # Calculate Core Species
            dismap.calculate_core_species(out_table)

        arcpy.conversion.ExportTable(in_table = out_table, out_table  = f"{csv_data_folder}\_{table_name}.csv", where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")
        print("Export Table: \t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')), flush=True)

        del csv_data_folder

        print(f"Creating the {table_name} Sample Locations Dataset", flush=True)

        # Set the output coordinate system to what is needed for the
        # DisMAP project
        #geographic_area_sr = os.path.join(f"{project_folder}", "Dataset Shapefiles", f"{table_name}", f"{geographic_area}.prj")
        #psr = arcpy.SpatialReference(geographic_area_sr); del geographic_area_sr
        #arcpy.env.outputCoordinateSystem    = psr
        psr    = arcpy.Describe(rf"{region_gdb}\{table_name}_Region").spatialReference

        arcpy.env.outputCoordinateSystem = psr

        out_features = ""

        if distri_code == "IDW":

            # 4326 - World Geodetic System 1984 (WGS 84)
            gsr     = arcpy.SpatialReference(4326)
            gsr_wkt = gsr.exportToString()
            psr_wkt = psr.exportToString()
            transformation = dismap.get_transformation(gsr_wkt, psr_wkt)
            arcpy.env.geographicTransformations = transformation
            del gsr_wkt, psr_wkt
            del transformation

            out_features = rf"{region_gdb}\{table_name}_Sample_Locations"

            print(f"\tXY Table to Feature Class", flush=True)

##            arcpy.management.XYTableToPoint(
##                                            in_table          = out_table,
##                                            out_feature_class = out_features,
##                                            x_field           = "Longitude",
##                                            y_field           = "Latitude",
##                                            z_field           = None,
##                                            coordinate_system = gsr
##                                           )

            fields = [f.name for f in arcpy.ListFields(out_table) if f.type not in ["Geometry", "OID"]]
            arr = arcpy.da.TableToNumPyArray(out_table, fields)
            arcpy.da.NumPyArrayToFeatureClass(arr, out_features, ('Longitude', 'Latitude'), gsr)
            del arr, fields

            del gsr

##            if arcpy.Exists(out_features):
##                # Get the count of records for selected species
##                getcount = arcpy.management.GetCount(out_features)[0]
##                print(f"\t{os.path.basename(out_features)} has {getcount} records", flush=True); del getcount
##
##                print(f"\tSelect by Location the XY Events inside the region boundary", flush=True)
##
##                tempLayer = "TempLayer"
##                arcpy.management.MakeFeatureLayer(out_features, tempLayer)
##
##                out_features_selected = arcpy.management.SelectLayerByLocation(
##                                                                               in_layer                    = tempLayer,
##                                                                               overlap_type                = "INTERSECT",
##                                                                               select_features             = rf"{region_gdb}\{table_name}_Region",
##                                                                               search_distance             = "10 Meters",
##                                                                               selection_type              = "NEW_SELECTION",
##                                                                               invert_spatial_relationship = "INVERT"
##                                                                              )
##
##                # Get the count of records for selected species
##                getcount = arcpy.management.GetCount(out_features_selected)[0]
##                print(f"\t{os.path.basename(out_features)} has {getcount} records", flush=True); del getcount
##
##                # Run GetCount and if some features have been selected,
##                #  run DeleteFeatures to remove the selected features.
##                if int(arcpy.management.GetCount(tempLayer)[0]) > 0:
##                    print(f"\tDelete Features outside the region boundary", flush=True)
##                    arcpy.management.DeleteFeatures(tempLayer)
##
##                arcpy.management.Delete(tempLayer)
##                del out_features_selected
##                del tempLayer
##
##                # Get the count of records for selected species
##                #getcount = arcpy.management.GetCount(out_features)[0]
##                #print(f"\t{os.path.basename(out_features)} has {getcount} records"); del getcount

        elif distri_code != "IDW":

            x_field, y_field = 'Easting', 'Northing'
            out_features = rf"{region_gdb}\{table_name}_GRID_Points"

            print(f"\tXY Table to Feature Class", flush=True)
            arcpy.management.XYTableToPoint(out_table, out_features, x_field, y_field, "#", psr)
            del x_field, y_field

        del geographic_area
        del distri_code

        del psr

        if arcpy.Exists(out_features):
            print(f"Adding field index in the {table_name} Point Locations Dataset", flush=True)

            # Add Attribute Index
            arcpy.management.AddIndex(out_features, ['Species', 'CommonName', 'SpeciesCommonName', 'Year'], f"{table_name}_SampleLocationsSpeciesIndex", "NON_UNIQUE", "NON_ASCENDING")

            # Get the count of records for selected species
            getcount = arcpy.management.GetCount(out_features)[0]
            print(f"\t{os.path.basename(out_features)} has {getcount} records", flush=True); del getcount

        results = [out_table, out_features]

        print(results, flush=True)

        return results

        del out_features

        # Variables for this function only
        del out_table
        # Basic variables
        del table_name, project_folder, scratch_workspace
        # Imports
        del warnings
        del dismap
        # Function parameter
        del region_gdb

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
##    else:
##        try:
##            leave_out_keys = ["leave_out_keys", "results"]
##            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
##            if remaining_keys:
##                print(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}", flush=True)
##            del leave_out_keys, remaining_keys
##            return results
##            #return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
##        except:
##            #raise SystemExit(str(traceback.print_exc()))
##            raise Exception(traceback.print_exc())
##    finally:
##        if "results" in locals().keys(): del results

def worker2(region_gdb=""):
    try:
        #raise Exception("WTF")
        return [region_gdb]
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        #raise Exception

def main(project):
    try:
        # Imports
        from create_region_sample_locations_worker import worker

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
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
        #table_name = "SEUS_SPR_IDW"
        #table_name = "GMEX_IDW"

        region_gdb        = rf"{scratch_folder}\{table_name}.gdb"
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        # Create worker scratch workspace, if missing
        if not arcpy.Exists(scratch_workspace):
            os.makedirs(rf"{scratch_folder}\{table_name}")
            if not arcpy.Exists(scratch_workspace):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}\{table_name}", f"scratch")
        del scratch_workspace

        # Setup worker workspace and copy data
        datasets = [rf"{project_gdb}\Datasets", rf"{project_gdb}\{table_name}_Region"]
        if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):

            arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"{table_name}")
            arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\Datasets", rf"{region_gdb}\Datasets")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\{table_name}_Region", rf"{region_gdb}\{table_name}_Region")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        else:
            arcpy.AddWarning(f"One or more datasets contains zero records!!")
            for d in datasets:
                arcpy.AddMessage(f"\t{os.path.basename(d)} has {arcpy.management.GetCount(d)[0]} records")
                del d
            se = f"SystemExit at line number: '{traceback.extract_stack()[-1].lineno}'"
            raise SystemExit(se)

        if "datasets" in locals().keys(): del datasets

        del scratch_folder, project_gdb

        results = []

        try:

            result = worker(region_gdb=region_gdb)
            if result:
                results.extend(result)
            del result
            #print(results)

        except SystemExit as se:
            arcpy.AddError(str(se))
            traceback.print_exc()
        except Exception as e:
            arcpy.AddError(str(e))
            traceback.print_exc()
        except:
            traceback.print_exc()

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

        deletes = [region_gdb, region_gdb.replace('.gdb','')]
        for delete in deletes:
            try:
                Delete = True
                if Delete and arcpy.Exists(delete):
                    arcpy.AddMessage(f"Delete: {delete}")
                    arcpy.management.Delete(delete)
                    arcpy.AddMessage("\tDelete: {0} {1}\n".format(os.path.basename(delete), arcpy.GetMessages(0).replace("\n", '\n\t')))
                del Delete
            except Exception as e:
                arcpy.AddMessage(e)
                raise SystemExit
            except:
                traceback.print_exc()
            finally:
                if "Delete" in locals().keys(): del Delete
                if "delete" in locals().keys(): del delete
        del deletes

        del region_gdb, table_name
        del worker
        del project

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
        traceback.print_exc()
        raise SystemExit
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
        traceback.print_exc()
        raise SystemExit
    except SystemExit as se:
        arcpy.AddError(str(se))
        traceback.print_exc()
    except Exception as e:
        arcpy.AddError(str(e))
        traceback.print_exc()
    except:
        traceback.print_exc()
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise SystemExit(str(traceback.print_exc()))
    finally:
        if "results" in locals().keys(): del results

if __name__ == '__main__':
    try:
        # Import this Python module
        import importlib, create_region_sample_locations_worker
        importlib.reload(create_region_sample_locations_worker)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        project = arcpy.GetParameterAsText(0)

        if not project:
            #project = "April 1 2023"
            #project = "May 1 2024"
            #project = "July 1 2024"
            project = "December 1 2024"

        # Tested on 7/31/2024 -- PASSED
        #main(project)

        del project

        from time import localtime, strftime
        print(f"\n{'-' * 90}")
        print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(f"{'-' * 90}")
        del localtime, strftime

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
