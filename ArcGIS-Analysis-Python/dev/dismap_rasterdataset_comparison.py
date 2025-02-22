# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        dismap.py
# Purpose:     Common DisMAP functions
#
# Author:      john.f.kennedy
#
# Created:     12/01/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, sys # built-ins first
import traceback
import importlib
import inspect

import arcpy # third-parties second

sys.path.append(os.path.dirname(__file__))

def GenerateRasterDatasetReport():
    try:
        results = "No Results"

        # "AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW",
        # "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_GLMME", "WC_GFDL", "WC_ANN_IDW", "WC_TRI_IDW",

        #table_names = ["AI_IDW"]
        #table_names = ["AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW", "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_GLMME", "WC_GFDL", "WC_ANN_IDW", "WC_TRI_IDW",]

##        {os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023
##            {os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\April 1 2023.gdb
##            {os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\Bathymetry\Bathymetry.gdb
##        F:\ArcGIS Analysis - Python\April 1 2023
##            F:\ArcGIS Analysis - Python\April 1 2023\Alaska.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\Bathymetry.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Dev.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Prod.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Test.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\DisMAP Project April 1 2023.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\export\New File Geodatabase.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\Export Metadata\metadata.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\GEBCO.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\HAWAII_500m.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\rft.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\Scratch Folder\AI_IDW Dev Scratch.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\Scratch Folder\AI_IDW Dev.gdb
##        F:\DisMAP\ArcGIS Analysis - Python\April 1 2023
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\Alaska.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\Bathymetry.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Dev.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Prod.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Test.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\DisMAP Project April 1 2023.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\export\New File Geodatabase.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\Export Metadata\metadata.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\GEBCO.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\HAWAII_500m.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\rft.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\Scratch Folder\AI_IDW Dev Scratch.gdb
##            F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\Scratch Folder\AI_IDW Dev.gdb


##        ws = r"F:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Prod.gdb"
##        #ws = r"F:\ArcGIS Analysis - Python\April 1 2023\Bathymetry.gdb"
##        #ws = r"F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Prod.gdb"
##        #ws = r"F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\Bathymetry.gdb"
##        #ws = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\April 1 2023.gdb"
##        #ws = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\Bathymetry\Bathymetry.gdb"

        wild_card    = "*Bathymetry"
        #wild_card    = "Raster_Mask"

        feature_type = "Raster"

        #top_level_workspace = r"F:\ArcGIS Analysis - Python"
        #top_level_workspace = r"F:\DisMAP"
        #top_level_workspace = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects"
        top_level_workspaces = [r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023",
                                r"F:\ArcGIS Analysis - Python\April 1 2023",
                                r"F:\DisMAP\ArcGIS Analysis - Python\April 1 2023"]

        comparisons = {}

        value_types = {"0" : "1-bit", "1" : "2-bit", "2" : "4-bit", "3" : "8-bit unsigned integer", "4" : "8-bit signed integer", "5" : "16-bit unsigned integer",
                       "6" : "16-bit signed integer", "7" : "32-bit unsigned integer", "8" : "32-bit signed integer", "9" : "32-bit floating point",
                       "10" : "64-bit double precision", "11" : "8-bit complex", "12" : "16-bit complex", "13" : "32-bit complex", "14" : "64-bit complex",}

        for top_level_workspace in top_level_workspaces:
            #comparisons[top_level_workspace] = {}

            arcpy.AddMessage(f"{top_level_workspace}")

            walk = arcpy.da.Walk(top_level_workspace)

            for dirpath, dirnames, filenames in walk:
                if os.path.isdir(dirpath) and arcpy.Describe(dirpath).workspaceType == "LocalDatabase":
                    if not dirpath.endswith("scratch") and not dirpath.endswith("scratch.gdb"):
                        arcpy.AddMessage(f"\t{dirpath}")
                        #comparisons[top_level_workspace] = {os.path.basename(dirpath) : {}}
                        # Reset Environments to start fresh
                        #arcpy.ResetEnvironments()
                        #arcpy.AddMessage(f"\tCompacting the {os.path.basename(dirpath)} GDB")
                        #arcpy.management.Compact(dirpath)
                        #arcpy.AddMessage("\t\t"+arcpy.GetMessages(0).replace("\n", "\n\t\t"))

##                        arcpy.env.workspace = dirpath
##
##                        datasets = arcpy.ListDatasets(wild_card=wild_card, feature_type=feature_type)
##
##                        for dataset in sorted(datasets):
##                            arcpy.AddMessage(f"\tDataset: {dataset}")
##                            comparisons[top_level_workspace][dirpath] = {dataset : {}}
##                            comparisons[top_level_workspace][dirpath][dataset]["MINIMUM"]     = float(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='MINIMUM').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["MINIMUM"]     = float(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='MINIMUM').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["MAXIMUM"]     = float(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='MAXIMUM').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["MEAN"]        = float(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='MEAN').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["STD"]         = float(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='STD').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["TOP"]         = float(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='TOP').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["LEFT"]        = float(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='LEFT').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["RIGHT"]       = float(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='RIGHT').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["BOTTOM"]      = float(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='BOTTOM').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["CELLSIZEX"]   = float(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='CELLSIZEX').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["CELLSIZEY"]   = float(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='CELLSIZEY').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["VALUETYPE"]   = str(value_types[arcpy.management.GetRasterProperties(in_raster=dataset, property_type='VALUETYPE').getOutput(0)])
##                            comparisons[top_level_workspace][dirpath][dataset]["COLUMNCOUNT"] = int(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='COLUMNCOUNT').getOutput(0))
##                            comparisons[top_level_workspace][dirpath][dataset]["ROWCOUNT"]    = int(arcpy.management.GetRasterProperties(in_raster=dataset, property_type='ROWCOUNT').getOutput(0))
##
##                            del dataset
##                        del datasets
##
##                        arcpy.ClearEnvironment("workspace")

                #for filename in filenames:
                #    rasters.append(os.path.join(dirpath, filename))
                del dirpath, dirnames, filenames
            del walk

    ##        try:
    ##            results = generateRasterDatasetReport(ws=ws, table_names=table_names, wc=wc)
    ##        except:
    ##            raise SystemExit

            del top_level_workspace
        del value_types
        del top_level_workspaces

        for comparison in comparisons:
            arcpy.AddMessage(f"{comparison}, {comparisons[comparison]}")
            del comparison
        #del comparisons

##        import json
##        # Write to File
##        with open('camparison.json', 'w') as json_file:
##            json.dump(comparisons, json_file, indent=4)
##        del json_file
##        del json

        del comparisons

        del wild_card, feature_type
        #del table_names

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteError:
        raise SystemExit(arcpy.GetMessages())
    except arcpy.ExecuteWarning:
        raise SystemExit(arcpy.GetMessages())
    except SystemExit as se:
        raise SystemExit(str(se))
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        raise SystemExit(pymsg)
    else:
        try:
            import inspect
            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return results

        except:
            traceback.print_exc()
    finally:
        try:
            pass
            if "results" in locals().keys(): del results
        except UnboundLocalError:
            pass

##def generateRasterDatasetReport(ws="", table_names="", wc=""):
##    try:
##        results = "No Results for generateRasterDatasetReport"
##
##        arcpy.AddMessage(f"Workspace Folder: {os.path.dirname(ws)}")
##
##        arcpy.env.workspace = ws
##
##        ws_name = os.path.basename(ws)
##        arcpy.AddMessage(f"\tFileGDB: {ws_name}")
##
##        for table_name in table_names:
##            if wc:
##                rasters = [r for r in arcpy.ListRasters(f"*") if os.path.basename(r).startswith(table_name) and wc in os.path.basename(r)]
##            elif not wc:
##                rasters = [r for r in arcpy.ListRasters(f"*") if os.path.basename(r).startswith(table_name)]
##
##            for raster in sorted(rasters):
##                arcpy.AddMessage(f"\t\t{os.path.basename(raster)}")
##                #check_datasets([raster])
##
##                #arcpy.management.GetRasterProperties(in_raster=raster, property_type=, band_index)
##
##                arcpy.AddMessage(f"\t\t\t Statistics")
##                arcpy.AddMessage(f"\t\t\t\t MINIMUM: {arcpy.management.GetRasterProperties(in_raster=raster, property_type='MINIMUM').getOutput(0)}")
##                arcpy.AddMessage(f"\t\t\t\t MAXIMUM: {arcpy.management.GetRasterProperties(in_raster=raster, property_type='MAXIMUM').getOutput(0)}")
##                arcpy.AddMessage(f"\t\t\t\t MEAN:    {arcpy.management.GetRasterProperties(in_raster=raster, property_type='MEAN').getOutput(0)}")
##                arcpy.AddMessage(f"\t\t\t\t STD:     {arcpy.management.GetRasterProperties(in_raster=raster, property_type='STD').getOutput(0)}")
##
##                arcpy.AddMessage(f"\t\t\t Extent")
##                arcpy.AddMessage(f"\t\t\t\t TOP:    {arcpy.management.GetRasterProperties(in_raster=raster, property_type='TOP').getOutput(0)}")
##                arcpy.AddMessage(f"\t\t\t\t LEFT:   {arcpy.management.GetRasterProperties(in_raster=raster, property_type='LEFT').getOutput(0)}")
##                arcpy.AddMessage(f"\t\t\t\t RIGHT:  {arcpy.management.GetRasterProperties(in_raster=raster, property_type='RIGHT').getOutput(0)}")
##                arcpy.AddMessage(f"\t\t\t\t BOTTOM: {arcpy.management.GetRasterProperties(in_raster=raster, property_type='BOTTOM').getOutput(0)}")
##
##                arcpy.AddMessage(f"\t\t\t Cell Size")
##                arcpy.AddMessage(f"\t\t\t\t CELLSIZEX: {arcpy.management.GetRasterProperties(in_raster=raster, property_type='CELLSIZEX').getOutput(0)}")
##                arcpy.AddMessage(f"\t\t\t\t CELLSIZEY: {arcpy.management.GetRasterProperties(in_raster=raster, property_type='CELLSIZEY').getOutput(0)}")
##
##                arcpy.AddMessage(f"\t\t\t Value Type")
##
##                value_types = {"0" : "1-bit", "1" : "2-bit", "2" : "4-bit", "3" : "8-bit unsigned integer", "4" : "8-bit signed integer", "5" : "16-bit unsigned integer",
##                               "6" : "16-bit signed integer", "7" : "32-bit unsigned integer", "8" : "32-bit signed integer", "9" : "32-bit floating point",
##                               "10" : "64-bit double precision", "11" : "8-bit complex", "12" : "16-bit complex", "13" : "32-bit complex", "14" : "64-bit complex",}
##
##                arcpy.AddMessage(f"\t\t\t\t VALUETYPE: {value_types[arcpy.management.GetRasterProperties(in_raster=raster, property_type='VALUETYPE').getOutput(0)]}")
##                del value_types
##
##                #if int(arcpy.management.GetRasterProperties(in_raster=raster, property_type='VALUETYPE').getOutput(0)) <= 8:
##                #    arcpy.AddMessage(f"\t\t\t\t VALUETYPE: {value_types[arcpy.management.GetRasterProperties(in_raster=raster, property_type='VALUETYPE').getOutput(0)]}")
##
##                arcpy.AddMessage(f"\t\t\t Row and Columns")
##                arcpy.AddMessage(f"\t\t\t\t COLUMNCOUNT: {arcpy.management.GetRasterProperties(in_raster=raster, property_type='COLUMNCOUNT').getOutput(0)}")
##                arcpy.AddMessage(f"\t\t\t\t ROWCOUNT:    {arcpy.management.GetRasterProperties(in_raster=raster, property_type='ROWCOUNT').getOutput(0)}")
##
##                arcpy.AddMessage(f"\t\t\t Bands")
##                arcpy.AddMessage(f"\t\t\t\t BANDCOUNT: {arcpy.management.GetRasterProperties(in_raster=raster, property_type='BANDCOUNT').getOutput(0)}")
##
##                arcpy.AddMessage(f"\t\t\t Any No Data")
##                arcpy.AddMessage(f"\t\t\t\t ANYNODATA: {arcpy.management.GetRasterProperties(in_raster=raster, property_type='ANYNODATA').getOutput(0)} (0 = No, 1 = Yes)")
##
##                del raster
##            del table_name
##        del table_names
##        del rasters
##
##        del ws_name, ws
##        del wc
##
##    except KeyboardInterrupt:
##        raise SystemExit
##    except SystemExit:
##        pass
##    except:
##        traceback.print_exc()
##        raise Exception
##    else:
##        try:
##            import inspect
##            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
##            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
##            if remaining_keys:
##                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
##            del leave_out_keys, remaining_keys
##
##            return results
##
##        except:
##            traceback.print_exc()
##    finally:
##        try:
##            pass
##            if "results" in locals().keys(): del results
##        except UnboundLocalError:
##            pass

def raster_properties_report(dataset=""):
    try:
        if not dataset:
            arcpy.AddWarning(f"{dataset} is missing")
        else:
            pixel_types = {"U1" : "1 bit", "U2"  : "2 bits", "U4"  : "4 bits",
                           "U8"  : "Unsigned 8-bit integers", "S8"  : "8-bit integers",
                           "U16" : "Unsigned 16-bit integers", "S16" : "16-bit integers",
                           "U32" : "Unsigned 32-bit integers", "S32" : "32-bit integers",
                           "F32" : "Single-precision floating point",
                           "F64" : "Double-precision floating point",}

            raster = arcpy.Raster(dataset)

            arcpy.AddMessage(f"{raster.name}")
            arcpy.AddMessage(f"\tSpatial Reference: {raster.spatialReference.name}")
            arcpy.AddMessage(f"\tXYResolution:      {raster.spatialReference.XYResolution} {raster.spatialReference.linearUnitName}s")
            arcpy.AddMessage(f"\tXYTolerance:       {raster.spatialReference.XYTolerance}  {raster.spatialReference.linearUnitName}s")
            arcpy.AddMessage(f"\tExtent:            {raster.extent.XMin} {raster.extent.YMin} {raster.extent.XMax} {raster.extent.YMax} (XMin, YMin, XMax, YMax)")
            arcpy.AddMessage(f"\tCell Size:         {raster.meanCellHeight}, {raster.meanCellWidth} (H, W)")
            arcpy.AddMessage(f"\tRows, Columns:     {raster.height} {raster.width} (H, W)")
            arcpy.AddMessage(f"\tStatistics:        {raster.minimum} {raster.maximum} {raster.mean} {raster.standardDeviation} (Min, Max, Mean, STD)")
            arcpy.AddMessage(f"\tPixel Type:        {pixel_types[raster.pixelType]}")

            del raster
            del pixel_types
        del dataset

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteError:
        raise SystemExit(arcpy.GetMessages())
    except arcpy.ExecuteWarning:
        raise SystemExit(arcpy.GetMessages())
    except SystemExit as se:
        raise SystemExit(str(se))
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        raise SystemExit(pymsg)
    else:
        try:
            import inspect
            leave_out_keys = ["leave_out_keys", "remaining_keys", "inspect"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return True

        except:
            traceback.print_exc()
    finally:
        try:
            pass
            #if "results" in locals().keys(): del results
        except UnboundLocalError:
            pass


def generate_raster_properties(ws="", table_names="", wc=""):
    try:

        arcpy.AddMessage(f"Workspace Folder: {os.path.dirname(ws)}")

        arcpy.env.workspace = ws

        ws_name = os.path.basename(ws)
        arcpy.AddMessage(f"\tFileGDB: {ws_name}")

        for table_name in table_names:
            rasters = ""
            if wc:
                rasters = [r for r in arcpy.ListRasters(f"*") if os.path.basename(r).startswith(table_name) and wc in os.path.basename(r)]
            elif not wc:
                rasters = [r for r in arcpy.ListRasters(f"*") if os.path.basename(r).startswith(table_name)]

            if not rasters:
                arcpy.AddWarning(f"No {wc} rasters for: {table_name}")
            else:
                for raster in sorted(rasters):
                    #arcpy.AddMessage(f"\t\t{os.path.basename(raster)}")
                    raster_properties_report(raster)

                    del raster
            del table_name, rasters
        del table_names

        del ws_name, ws
        del wc

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteError:
        raise SystemExit(arcpy.GetMessages())
    except arcpy.ExecuteWarning:
        raise SystemExit(arcpy.GetMessages())
    except SystemExit as se:
        raise SystemExit(str(se))
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        raise SystemExit(pymsg)
    else:
        try:
            import inspect
            leave_out_keys = ["leave_out_keys", "remaining_keys", "inspect"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return True

        except:
            traceback.print_exc()
    finally:
        try:
            pass
            #if "results" in locals().keys(): del results
        except UnboundLocalError:
            pass

def main():
    try:

##        {os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023
##            {os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\Bathymetry\Bathymetry.gdb
##            {os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\April 1 2023.gdb
##            {os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\Bathymetry\Bathymetry.gdb
##        F:\ArcGIS Analysis - Python\April 1 2023
##            F:\ArcGIS Analysis - Python\April 1 2023\Bathymetry.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Dev.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Prod.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Test.gdb
##            F:\ArcGIS Analysis - Python\April 1 2023\DisMAP Project April 1 2023.gdb


        #ws = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\Bathymetry\Bathymetry.gdb"
        #ws = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\Bathymetry\Bathymetry.gdb"
        #ws = r"F:\ArcGIS Analysis - Python\April 1 2023\Bathymetry.gdb"
        #ws = r"F:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Dev.gdb"
        #ws = r"F:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Prod.gdb"
        #ws = r"E:\DisMAP WI 20230426\April 1 2023\DisMAP April 1 2023 Prod.gdb"
        #ws = r"F:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Test.gdb"
        #ws = r"F:\ArcGIS Analysis - Python\April 1 2023\DisMAP Project April 1 2023.gdb"
        #ws = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\April 1 2023.gdb"
        ws = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\May 1 2024\May 1 2024.gdb"

        # "AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW",
        # "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_GLMME", "WC_GFDL", "WC_ANN_IDW", "WC_TRI_IDW",

        #table_names = ["GMEX_IDW"]
        table_names = ["AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW", "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_GLMME", "WC_GFDL", "WC_ANN_IDW", "WC_TRI_IDW",]

        #wc = "Bathymetry"
        wc = "Raster_Mask"

        try:
            generate_raster_properties(ws=ws, table_names=table_names, wc=wc)
        except SystemExit as se:
            raise SystemExit(str(se))

        del ws, table_names, wc

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
        raise SystemExit
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
        raise SystemExit
    except SystemExit as se:
        arcpy.AddError(str(se))
        raise SystemExit
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        raise SystemExit(pymsg)
    else:
        try:
            import inspect
            leave_out_keys = ["leave_out_keys", "remaining_keys", "inspect"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return True

        except:
            traceback.print_exc()
    finally:
        try:
            pass
            #if "results" in locals().keys(): del results
        except UnboundLocalError:
            pass

if __name__ == '__main__':
    try:

        main()

    except SystemExit:
        pass
    except:
        traceback.print_exc()
    else:
        import inspect
        leave_out_keys = ["remaining_keys", "leave_out_keys", "inspect"]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[1][3]}': ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
