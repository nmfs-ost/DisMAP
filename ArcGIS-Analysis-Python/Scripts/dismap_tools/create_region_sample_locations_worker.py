# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     29/02/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import inspect
import os
import sys
import traceback

import arcpy  # third-parties second


def worker(region_gdb=""):
    try:
        # Import the dismap_tools module to access tools
        import warnings

        import dismap_tools
        import numpy as np
        import pandas as pd
        # Import
        from arcpy import metadata as md

        # Use all of the cores on the machine
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.overwriteOutput = True

        # Set History and Metadata logs, set serverity and message levelarcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(
            2
        )  # 0—A tool will not throw an exception, even if the tool produces an error or warning.
        # 1—If a tool produces a warning or an error, it will throw an exception.
        # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(
            ["NORMAL"]
        )  # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        table_name = os.path.basename(region_gdb).replace(".gdb", "")
        scratch_folder = os.path.dirname(region_gdb)
        project_folder = os.path.dirname(scratch_folder)
        csv_data_folder = os.path.join(project_folder, f"CSV_Data")
        process_table = rf"{csv_data_folder}\{table_name}.csv"
        scratch_workspace = os.path.join(scratch_folder, "scratch.gdb")
        del scratch_folder

        # Set basic workkpace variables
        arcpy.env.workspace = region_gdb
        arcpy.env.scratchWorkspace = scratch_workspace

        field_csv_dtypes = dismap_tools.dTypesCSV(csv_data_folder, table_name)
        field_gdb_dtypes = dismap_tools.dTypesGDB(csv_data_folder, table_name)

        # print(field_csv_dtypes)
        # print(field_gdb_dtypes)
        # sys.exit()

        # DatasetCode, CSVFile, TransformUnit, TableName, GeographicArea, CellSize,
        # PointFeatureType, FeatureClassName, Region, Season, DateCode, Status,
        # DistributionProjectCode, DistributionProjectName, SummaryProduct,
        # FilterRegion, FilterSubRegion, FeatureServiceName, FeatureServiceTitle,
        # MosaicName, MosaicTitle, ImageServiceName, ImageServiceTitle

        # Get values for table_name from Datasets table
        fields = [
            "TableName",
            "GeographicArea",
            "DatasetCode",
            "Region",
            "Season",
            "DistributionProjectCode",
        ]
        region_list = [
            row
            for row in arcpy.da.SearchCursor(
                rf"{region_gdb}\Datasets",
                fields,
                where_clause=f"TableName = '{table_name}'",
            )
        ][0]
        del table_name

        # Assigning variables from items in the chosen table list
        # ['AI_IDW', 'AI_IDW_Region', 'AI', 'Aleutian Islands', None, 'IDW']
        table_name = region_list[0]
        geographic_area = region_list[1]
        datasetcode = region_list[2]
        region = region_list[3]
        season = region_list[4]
        distri_code = region_list[5]
        del region_list

        # Start of business logic for the worker function
        arcpy.AddMessage(f"Reading {table_name} CSV File\n")

        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_colwidth", 10)
        pd.set_option("display.min_rows", 2)
        pd.set_option("display.max_rows", 5)
        pd.set_option("display.expand_frame_repr", False)

        encoding, index_column = dismap_tools.get_encoding_index_col(process_table)

        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            # DataFrame
            df = pd.read_csv(
                process_table,
                index_col=index_column,
                encoding=encoding,
                delimiter=",",
                dtype=field_csv_dtypes,
            )
        del encoding, index_column

        # Rename columns using the dictionary below and the defined list of field names
        # Easting,Northing,year,depth_m,median_est,mean_est,est5,est95,spp_sci,spp_common
        # mean_est, est5, est95
        column_names = {
            "common": "CommonName",
            "depth": "Depth",
            "depth_m": "Depth",
            "DistributionProjectName": "DistributionProjectName",
            "est5": "Estimate5",
            "est95": "Estimate95",
            "haulid": "SampleID",
            "lat": "Latitude",
            "lat_UTM": "Northing",
            "lon": "Longitude",
            "lon_UTM": "Easting",
            "mean_est": "MeanEstimate",
            "median_est": "MedianEstimate",
            "region": "Region",
            "sampleid": "SampleID",
            "spp": "Species",
            "spp_common": "CommonName",
            "spp_sci": "Species",
            "stratum": "Stratum",
            "stratumarea": "StratumArea",
            "transformed": "MapValue",
            "wtcpue": "WTCPUE",
            "year": "Year",
            "CoreSpecies": "CoreSpecies",
        }

        df.rename(columns=column_names, inplace=True)
        del column_names

        # Print column names
        # for column in list(df.columns): arcpy.AddMessage(column); del column # print columns

        # ###--->>>
        arcpy.AddMessage("Inserting additional columns into the dataframe\n")

        arcpy.AddMessage(f"\tInserting 'DatasetCode' column into: {table_name}")
        df.insert(0, "DatasetCode", datasetcode)
        del datasetcode

        arcpy.AddMessage(f"\tInserting 'Region' column into: {table_name}")
        if "Region" not in list(df.columns):
            df.insert(df.columns.get_loc("DatasetCode") + 1, "Region", f"{region}")

        arcpy.AddMessage(f"\tInserting 'StdTime' column into: {table_name}")
        if "StdTime" not in list(df.columns):
            df.insert(
                df.columns.get_loc("Year") + 1,
                "StdTime",
                pd.to_datetime(df["Year"], format="%Y").dt.tz_localize("Etc/GMT+12"),
            )

        arcpy.AddMessage(f"\tInserting 'MapValue' column into: {table_name}")
        if "MapValue" not in list(df.columns):
            df.insert(df.columns.get_loc("WTCPUE") + 1, "MapValue", np.nan)
            # -->> MapValue
            arcpy.AddMessage("\tCalculating the MapValue values")
            df["MapValue"] = df["WTCPUE"].pow((1.0 / 3.0))

        arcpy.AddMessage(f"\tInserting 'SpeciesCommonName' column into: {table_name}")
        if "SpeciesCommonName" not in list(df.columns):
            df.insert(df.columns.get_loc("CommonName") + 1, "SpeciesCommonName", "")

        arcpy.AddMessage(f"\tInserting 'CommonNameSpecies' column into: {table_name}")
        if "CommonNameSpecies" not in list(df.columns):
            df.insert(
                df.columns.get_loc("SpeciesCommonName") + 1, "CommonNameSpecies", ""
            )

        # Test if 'IDW' in table name
        # if "IDW" in table_name:
        arcpy.AddMessage(f"\tInserting 'Season' {season} column into: {table_name}")
        if "Season" not in list(df.columns):
            df.insert(
                df.columns.get_loc("Region") + 1,
                "Season",
                season if season is not None else "",
            )

        arcpy.AddMessage(f"\tInserting 'SummaryProduct' column into: {table_name}")
        if "SummaryProduct" not in list(df.columns):
            df.insert(df.columns.get_loc("Season") + 1, "SummaryProduct", "Yes")

        arcpy.AddMessage(f"\tInserting 'TransformUnit' column into: {table_name}")
        if "TransformUnit" not in list(df.columns):
            df.insert(df.columns.get_loc("MapValue") + 1, "TransformUnit", "cuberoot")

        arcpy.AddMessage(f"\tInserting 'CoreSpecies' column into: {table_name}")
        if "CoreSpecies" not in list(df.columns):
            df.insert(df.columns.get_loc("CommonNameSpecies") + 1, "CoreSpecies", "No")

        arcpy.AddMessage(
            f"\tCalculate Null for 'StratumArea' column into: {table_name}"
        )
        if "StratumArea" in list(df.columns):
            # df["StratumArea"].fillna(np.nan, inplace = True)
            df["StratumArea"] = df["StratumArea"].fillna(np.nan)

        arcpy.AddMessage(
            f"\tCalculate Null for 'DistributionProjectName' column into: {table_name}"
        )
        if "DistributionProjectName" in list(df.columns):
            # df["DistributionProjectName"].fillna(np.nan, inplace = True)
            df["DistributionProjectName"] = df["DistributionProjectName"].fillna(np.nan)

        arcpy.AddMessage(f"\tCalculate Null for 'WTCPUE' column into: {table_name}")
        if "WTCPUE" in list(df.columns):
            df["WTCPUE"] = df["WTCPUE"].fillna(np.nan)

        arcpy.AddMessage(f"\tCalculate Null for 'Latitude' column into: {table_name}")
        if "Latitude" in list(df.columns):
            df["Latitude"] = df["Latitude"].fillna(np.nan)

        arcpy.AddMessage(f"\tCalculate Null for 'Longitude' column into: {table_name}")
        if "Longitude" in list(df.columns):
            df["Longitude"] = df["Longitude"].fillna(np.nan)

        arcpy.AddMessage(f"\tCalculate Null for 'Depth' column into: {table_name}")
        if "Depth" in list(df.columns):
            df["Depth"] = df["Depth"].fillna(np.nan)

        del region, season

        # ###--->>>
        # arcpy.AddMessage(f"Updating and calculating new values for some columns\n")
        # -->> DistributionProjectName
        arcpy.AddMessage("\tSetting 'NaN' in 'DistributionProjectName' to ''")
        # df.loc[df['DistributionProjectName'] == 'nan', 'DistributionProjectName'] =  ""
        df["DistributionProjectName"] = df["DistributionProjectName"].fillna("")

        # -->> CommonName
        arcpy.AddMessage("\tSetting 'NaN' in 'CommonName' to ''")
        # df.loc[df['CommonName'] == 'nan', 'CommonName'] =  ""
        df["CommonName"] = df["CommonName"].fillna("")

        arcpy.AddMessage("\tSetting 'CommonName' unicode'")
        # Cast text as Unicode in the CommonName field
        df["CommonName"] = df["CommonName"].astype("unicode")

        # -->> SpeciesCommonName
        arcpy.AddMessage(
            "\tCalculating SpeciesCommonName and setting it to 'Species (CommonName)'"
        )
        df["SpeciesCommonName"] = np.where(
            df["CommonName"] != "", df["Species"] + " (" + df["CommonName"] + ")", ""
        )

        # -->> CommonNameSpecies
        arcpy.AddMessage(
            "\tCalculating  CommonNameSpecies and setting it to 'CommonName (Species)'"
        )
        df["CommonNameSpecies"] = np.where(
            df["CommonName"] != "", df["CommonName"] + " (" + df["Species"] + ")", ""
        )

        arcpy.AddMessage("\tReplacing Infinity values with Nulls")
        # Replace Inf with Nulls
        # For some cell values in the 'WTCPUE' column, there is an Inf
        # value representing an infinit
        df.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Left justify the column names
        # df.columns = pd.Index([col.ljust(10) for col in df.columns])

        table_definition = dismap_tools.table_definitions(csv_data_folder, table_name)
        # arcpy.AddMessage(table_definition)

        # altering the DataFrame
        df = df[table_definition]
        del table_definition

        # raise SystemExist(f"Line Number: {traceback.extract_stack()[-1].lineno}")

        pd.set_option("display.max_colwidth", 12)

        # Change Table Style
        df.style.set_table_styles(
            [{"selector": "td", "props": "white-space: nowrap !important;"}]
        )

        arcpy.AddMessage(f"\nDataframe report:\n{df.head(5)}\n")

        arcpy.AddMessage("Converting the Dataframe to an NumPy Array\n")
        try:
            array = np.array(np.rec.fromrecords(df.values), dtype=field_gdb_dtypes)
        except:  # noqa: E722
            arcpy.AddError(arcpy.GetMessages(2))
            traceback.print_exc()
            sys.exit()

        del field_gdb_dtypes
        del field_csv_dtypes

        del df  # delete dataframe
        # Imports
        del pd, np

        # Temporary table
        # tmp_table = f"memory\{table_name.lower()}_tmp"
        tmp_table = rf"{region_gdb}\{table_name.lower()}_tmp"
        try:
            arcpy.da.NumPyArrayToTable(array, tmp_table)
            del array
        except arcpy.ExecuteWarning:
            arcpy.AddWarning(arcpy.GetMessages(1))
        except arcpy.ExecuteError:
            arcpy.AddError(arcpy.GetMessages(2))
            traceback.print_exc()
            sys.exit()
        except:  # noqa: E722
            arcpy.AddError(arcpy.GetMessages(2))
            traceback.print_exc()
            sys.exit()

        desc = arcpy.da.Describe(tmp_table)
        fields = [f.name for f in desc["fields"] if f.type == "String"]
        # fields = ["Season", "Species", "CommonName", "SpeciesCommonName", "CommonNameSpecies", "Stratum"]
        oid = desc["OIDFieldName"]
        # Use SQL TOP to sort field values
        arcpy.AddMessage(f"{', '.join(fields)}")
        for row in arcpy.da.SearchCursor(tmp_table, fields, f"{oid} <= 5"):
            arcpy.AddMessage(row)
            del row
        del desc, fields, oid

        out_table = rf"{region_gdb}\{table_name}"
        # out_table = rf"{region_gdb}\{table_name}_TABLE"

        arcpy.AddMessage(f"Copying the {table_name} Table from memory to the GDB")
        arcpy.management.CopyRows(tmp_table, out_table, "")
        arcpy.AddMessage(
            "Copy Rows: \t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t"))
        )
        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        process_table_md = md.Metadata(process_table)
        out_table_md = md.Metadata(out_table)
        out_table_md.copy(process_table_md)
        out_table_md.save()
        out_table_md.synchronize("OVERWRITE")
        out_table_md.save()
        out_table_md.synchronize("ALWAYS")
        out_table_md.save()
        del out_table_md
        del process_table_md

        del process_table  # delete passed variables

        # Test if 'IDW' in region name
        # if distri_code == "IDW":
        #    # Calculate Core Species
        #    dismap_tools.calculate_core_species(out_table)

        # arcpy.conversion.ExportTable(in_table = out_table, out_table  = f"{csv_data_folder}\_{table_name}.csv", where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")
        # arcpy.AddMessage("Export Table: \t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        arcpy.AddMessage(f"Creating the {table_name} Sample Locations Dataset")

        # Set the output coordinate system to what is needed for the
        # DisMAP project
        # geographic_area_sr = os.path.join(f"{project_folder}", "Dataset_Shapefiles", f"{table_name}", f"{geographic_area}.prj")
        # psr = arcpy.SpatialReference(geographic_area_sr); del geographic_area_sr
        # arcpy.env.outputCoordinateSystem    = psr
        psr = arcpy.Describe(rf"{region_gdb}\{table_name}_Region").spatialReference

        arcpy.env.outputCoordinateSystem = psr

        out_features = ""

        # if distri_code == "IDW":

        # 4326 - World Geodetic System 1984 (WGS 84)
        gsr = arcpy.SpatialReference(4326)
        gsr_wkt = gsr.exportToString()
        psr_wkt = psr.exportToString()
        transformation = dismap_tools.get_transformation(gsr_wkt, psr_wkt)
        arcpy.env.geographicTransformations = transformation
        del gsr_wkt, psr_wkt
        del transformation

        arcpy.AddMessage("\tMake XY Event layer for IDW datasets")
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        # gsr = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        x_coord, y_coord = "Longitude", "Latitude"
        xy_events = arcpy.management.MakeXYEventLayer(
            out_table, x_coord, y_coord, "xy_events", gsr, "#"
        )
        del x_coord, y_coord

        out_features = rf"{region_gdb}\{table_name}_Sample_Locations"

        with arcpy.EnvManager(scratchWorkspace=scratch_workspace, workspace=region_gdb):
            arcpy.conversion.ExportFeatures(
                in_features=xy_events,
                out_features=out_features,
                where_clause="",
                use_field_alias_as_name="",
                field_mapping="",
                sort_field="",
            )
        # Clear the XY Event Layer from memory.
        arcpy.management.Delete("xy_events")
        del xy_events, psr

        # arcpy.AddMessage(f"\tXY TableToNumPyArray to Feature Class")
        # fields = [f.name for f in arcpy.ListFields(out_table) if f.type not in ["Geometry", "OID"]]
        # arr = arcpy.da.TableToNumPyArray(out_table, fields)
        # arcpy.da.NumPyArrayToFeatureClass(arr, out_features, ('Longitude', 'Latitude'), gsr)
        # del arr, fields

        del gsr

        # elif distri_code != "IDW":
        #
        #    x_field, y_field = 'Easting', 'Northing'
        #    out_features = rf"{region_gdb}\{table_name}_GRID_Points"
        #
        #    arcpy.AddMessage(f"\tXY Table to Feature Class")
        #    arcpy.management.XYTableToPoint(out_table, out_features, x_field, y_field, "#", psr)
        #    del x_field, y_field

        del geographic_area
        del distri_code

        if arcpy.Exists(out_features):
            arcpy.AddMessage(
                f"Adding field index in the {table_name} Point Locations Dataset"
            )

            # Add Attribute Index
            arcpy.management.AddIndex(
                out_features,
                ["Species", "CommonName", "SpeciesCommonName", "Year"],
                f"{table_name}_SampleLocationsSpeciesIndex",
                "NON_UNIQUE",
                "NON_ASCENDING",
            )

            # Get the count of records for selected species
            getcount = arcpy.management.GetCount(out_features)[0]
            arcpy.AddMessage(
                f"\t{os.path.basename(out_features)} has {getcount} records"
            )
            del getcount
        else:
            pass

        out_table_md = md.Metadata(out_table)
        out_features_md = md.Metadata(out_features)
        out_features_md.copy(out_table_md)
        out_features_md.save()
        out_features_md.synchronize("OVERWRITE")
        out_features_md.save()
        out_features_md.synchronize("ALWAYS")
        out_features_md.save()
        del out_features_md
        del out_table_md

        arcpy.AddMessage(f"\t\tAlter Fields for: '{os.path.basename(out_features)}'")
        dismap_tools.alter_fields(csv_data_folder, out_features)

        dataset_md = md.Metadata(out_features)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md

        arcpy.AddMessage(f"\t\tAlter Fields for: '{os.path.basename(out_table)}'")
        dismap_tools.alter_fields(csv_data_folder, out_table)

        dataset_md = md.Metadata(out_table)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md

        arcpy.management.Delete(rf"{region_gdb}\{table_name}_Boundary")
        arcpy.management.Delete(rf"{region_gdb}\{table_name}_Region")
        arcpy.management.Delete(rf"{region_gdb}\Datasets")

        # Declared Variables
        del out_table, out_features
        del table_name, project_folder, scratch_workspace, csv_data_folder
        # Imports
        del warnings, md
        del dismap_tools
        # Function parameter
        del region_gdb

    except KeyboardInterrupt:
        sys.exit()
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(
            f"Caught an arcpy.ExecuteWarning error in the '{inspect.stack()[0][3]}' function."
        )
        arcpy.AddWarning(arcpy.GetMessages(1))
    except arcpy.ExecuteError:
        arcpy.AddError(
            f"Caught an arcpy.ExecuteError error in the '{inspect.stack()[0][3]}' function."
        )
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        sys.exit()
    except SystemExit as se:
        arcpy.AddError(
            f"Caught an SystemExit error: {se} in the '{inspect.stack()[0][3]}' function."
        )
        sys.exit()
    except Exception as e:
        arcpy.AddError(
            f"Caught an Exception error: {e} in the '{inspect.stack()[0][3]}' function."
        )
        traceback.print_exc()
        sys.exit()
    except:  # noqa: E722
        arcpy.AddError(
            f"Caught an except error in the '{inspect.stack()[0][3]}' function."
        )
        traceback.print_exc()
        sys.exit()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith("__")]
        if rk:
            arcpy.AddMessage(
                f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"
            )
        del rk
        return True
    finally:
        pass


def script_tool(project_gdb=""):
    try:
        from time import gmtime, localtime, strftime, time

        import dismap_tools

        # Set a start time so that we can see how log things take
        start_time = time()
        arcpy.AddMessage(f"{'-' * 80}")
        arcpy.AddMessage(f"Python Script:  {os.path.basename(__file__)}")
        arcpy.AddMessage(f"Location:       .. {'/'.join(__file__.split(os.sep)[-4:])}")
        arcpy.AddMessage(f"Python Version: {sys.version}")
        arcpy.AddMessage(f"Environment:    {os.path.basename(sys.exec_prefix)}")
        arcpy.AddMessage(
            f"Start Time:     {strftime('%a %b %d %I:%M %p', localtime(start_time))}"
        )
        arcpy.AddMessage(f"{'-' * 80}\n")

        # Imports
        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Set varaibales
        project_folder = os.path.dirname(project_gdb)
        scratch_folder = rf"{project_folder}\Scratch"
        del project_folder

        # Clear Image Folder
        ClearImageFolder = True
        if ClearImageFolder:
            dismap_tools.clear_folder(folder=scratch_folder)
        else:
            pass
        del ClearImageFolder

        # Test if passed workspace exists, if not sys.exit()
        if not arcpy.Exists(project_gdb):
            sys.exit()(f"{os.path.basename(project_gdb)} is missing!!")

        # Create project scratch workspace, if missing
        if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(scratch_folder)
            if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", "scratch")

        # Set worker parameters
        table_name = "AI_IDW"
        # table_name = "HI_IDW"
        # table_name = "NBS_IDW"
        # table_name = "SEUS_SPR_IDW"
        # table_name = "GMEX_IDW"
        # table_name = "ENBS_IDW"

        region_gdb = os.path.join(scratch_folder, f"{table_name}.gdb")
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        # Create worker scratch workspace, if missing
        if not arcpy.Exists(scratch_workspace):
            os.makedirs(os.path.join(scratch_folder, table_name))
            if not arcpy.Exists(scratch_workspace):
                arcpy.management.CreateFileGDB(
                    os.path.join(scratch_folder, f"{table_name}"), "scratch"
                )
        del scratch_workspace

        # Setup worker workspace and copy data
        # datasets = [ros.path.join(project_gdb, "Datasets") os.path.join(project_gdb, f"{table_name}_Region")]
        # if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):
        if not arcpy.Exists(os.path.join(scratch_folder, f"{table_name}.gdb")):
            arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"{table_name}")
            arcpy.AddMessage(
                "\tCreate File GDB: {0}\n".format(
                    arcpy.GetMessages().replace("\n", "\n\t")
                )
            )
        else:
            pass
        arcpy.management.Copy(
            os.path.join(project_gdb, "Datasets"), rf"{region_gdb}\Datasets"
        )
        arcpy.AddMessage(
            "\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", "\n\t"))
        )

        arcpy.management.Copy(
            os.path.join(project_gdb, f"{table_name}_Region"),
            rf"{region_gdb}\{table_name}_Region",
        )
        arcpy.AddMessage(
            "\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", "\n\t"))
        )

        # else:
        #    arcpy.AddWarning(f"One or more datasets contains zero records!!")
        #    for d in datasets:
        #        arcpy.AddMessage(f"\t{os.path.basename(d)} has {arcpy.management.GetCount(d)[0]} records")
        #        del d
        #    se = f"SystemExit at line number: '{traceback.extract_stack()[-1].lineno}'"
        #    sys.exit()(se)
        # if "datasets" in locals().keys(): del datasets

        try:
            pass
            worker(region_gdb=region_gdb)
        except SystemExit:
            arcpy.AddMessage(arcpy.GetMessages())
            sys.exit()
            # arcpy.AddMessage(f"caught SystemExit in '{inspect.stack()[0][3]}'")

        # Declared Varaiables
        del region_gdb, table_name, scratch_folder
        # Imports
        del dismap_tools
        # Function Parameters
        del project_gdb
        # Elapsed time
        end_time = time()
        elapse_time = end_time - start_time
        hours, rem = divmod(end_time - start_time, 3600)
        minutes, seconds = divmod(rem, 60)
        arcpy.AddMessage(f"\n{'-' * 80}")
        arcpy.AddMessage(f"Python script: {os.path.basename(__file__)}")
        arcpy.AddMessage(
            f"Start Time:    {strftime('%a %b %d %I:%M %p', localtime(start_time))}"
        )
        arcpy.AddMessage(
            f"End Time:      {strftime('%a %b %d %I:%M %p', localtime(end_time))}"
        )
        arcpy.AddMessage(
            f"Elapsed Time   {int(hours):0>2}:{int(minutes):0>2}:{seconds:05.2f} (H:M:S)"
        )
        arcpy.AddMessage(f"{'-' * 80}")
        del hours, rem, minutes, seconds
        del elapse_time, end_time, start_time
        del gmtime, localtime, strftime, time

    except arcpy.ExecuteError:
        # Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
        return False
    except:  # noqa: E722
        # Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
        return False
    else:
        return True


if __name__ == "__main__":
    try:
        project_gdb = arcpy.GetParameterAsText(0)
        if not project_gdb:
            project_gdb = os.path.join(
                os.path.expanduser("~"),
                "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\February 1 2026\\February 1 2026.gdb",
            )
        else:
            pass
        script_tool(project_gdb)
        arcpy.SetParameterAsText(1, "Result")
        del project_gdb

    except arcpy.ExecuteError:
        # Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
    except:  # noqa: E722
        # Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)

# This is an autogenerated comment.
