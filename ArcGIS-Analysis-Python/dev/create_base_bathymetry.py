# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     05/03/2024
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

            arcpy.AddMessage(f"\t\t {raster.name}")
            arcpy.AddMessage(f"\t\t\t Spatial Reference: {raster.spatialReference.name}")
            arcpy.AddMessage(f"\t\t\t XYResolution:      {raster.spatialReference.XYResolution} {raster.spatialReference.linearUnitName}s")
            arcpy.AddMessage(f"\t\t\t XYTolerance:       {raster.spatialReference.XYTolerance}  {raster.spatialReference.linearUnitName}s")
            arcpy.AddMessage(f"\t\t\t Extent:            {raster.extent.XMin} {raster.extent.YMin} {raster.extent.XMax} {raster.extent.YMax} (XMin, YMin, XMax, YMax)")
            arcpy.AddMessage(f"\t\t\t Cell Size:         {raster.meanCellHeight}, {raster.meanCellWidth} (H, W)")
            arcpy.AddMessage(f"\t\t\t Rows, Columns:     {raster.height} {raster.width} (H, W)")
            arcpy.AddMessage(f"\t\t\t Statistics:        {raster.minimum} {raster.maximum} {raster.mean} {raster.standardDeviation} (Min, Max, Mean, STD)")
            arcpy.AddMessage(f"\t\t\t Pixel Type:        {pixel_types[raster.pixelType]}")

            del raster
            del pixel_types
        del dataset

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

def create_alasaka_bathymetry(project_gdb=""):
    try:
        # Test if passed workspace exists, if not raise SystemExit

        if not arcpy.Exists(project_gdb):

            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        import dismap
        importlib.reload(dismap)
        from dismap import check_transformation

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        project_folder = os.path.dirname(project_gdb)
        base_folder = os.path.dirname(project_folder)

        # Create Scratch Workspace for Project
        if not arcpy.Exists(rf"{project_folder}\Scratch\scratch.gdb"):
            if not arcpy.Exists(rf"{project_folder}\Scratch"):
                os.makedirs(rf"{project_folder}\Scratch")
            if not arcpy.Exists(rf"{project_folder}\Scratch\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{project_folder}\Scratch", f"scratch")

        # Base Bathymetry Folder
        if not os.path.isdir(rf"{base_folder}\Bathymetry"):
            os.makedirs(rf"{base_folder}\Bathymetry")
        # Base Bathymetry GDB
        if not arcpy.Exists(rf"{base_folder}\Bathymetry\Bathymetry.gdb"):
            arcpy.management.CreateFileGDB(rf"{base_folder}\Bathymetry", "Bathymetry")

        # Project Bathymetry Folder
        if not os.path.isdir(rf"{project_folder}\Bathymetry"):
            os.makedirs(rf"{project_folder}\Bathymetry")
        # Project Bathymetry GDB
        if not arcpy.Exists(rf"{project_folder}\Bathymetry\Bathymetry.gdb"):
            arcpy.management.CreateFileGDB(rf"{project_folder}\Bathymetry", "Bathymetry")

        # Set basic workkpace variables
        arcpy.env.workspace                = rf"{base_folder}\Bathymetry\Bathymetry.gdb"
        arcpy.env.scratchWorkspace         = rf"{project_folder}\Scratch\scratch.gdb"
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        arcpy.env.cellSize = 1000

        arcpy.env.pyramid          = "PYRAMIDS -1 BILINEAR DEFAULT 75 NO_SKIP"
        arcpy.env.rasterStatistics = "STATISTICS 1 1"
        arcpy.env.resamplingMethod = "BILINEAR"

        arcpy.env.outputCoordinateSystem = None

        arcpy.AddMessage(f"Processing Alaska Bathymetry")

# ###--->>> Setting up the base folder bathymetry for all projects
        # Set Alaska Bathymetry

        ai_bathy         = rf"{base_folder}\Bathymetry\Alaska Bathymetry\AI_IDW_Bathy.grd"   # ASCII GRIDs
        ebs_bathy        = rf"{base_folder}\Bathymetry\Alaska Bathymetry\EBS_IDW_Bathy.grd"  # ASCII GRIDs
        goa_bathy        = rf"{base_folder}\Bathymetry\Alaska Bathymetry\GOA_IDW_Bathy.grd"  # ASCII GRIDs

        ai_bathy_grid    = rf"{base_folder}\Bathymetry\Bathymetry.gdb\AI_IDW_Bathy_Grid"   # ASCII GRIDs imported to the FGDB
        ebs_bathy_grid   = rf"{base_folder}\Bathymetry\Bathymetry.gdb\EBS_IDW_Bathy_Grid"  # ASCII GRIDs imported to the FGDB
        goa_bathy_grid   = rf"{base_folder}\Bathymetry\Bathymetry.gdb\GOA_IDW_Bathy_Grid"  # ASCII GRIDs imported to the FGDB

        ai_bathy_raster  = rf"{base_folder}\Bathymetry\Bathymetry.gdb\AI_IDW_Bathy_Raster"
        ebs_bathy_raster = rf"{base_folder}\Bathymetry\Bathymetry.gdb\EBS_IDW_Bathy_Raster"
        goa_bathy_raster = rf"{base_folder}\Bathymetry\Bathymetry.gdb\GOA_IDW_Bathy_Raster"

        ai_bathymetry    = rf"{base_folder}\Bathymetry\Bathymetry.gdb\AI_IDW_Bathymetry"
        ebs_bathymetry   = rf"{base_folder}\Bathymetry\Bathymetry.gdb\EBS_IDW_Bathymetry"
        goa_bathymetry   = rf"{base_folder}\Bathymetry\Bathymetry.gdb\GOA_IDW_Bathymetry"
        enbs_bathymetry  = rf"{base_folder}\Bathymetry\Bathymetry.gdb\ENBS_IDW_Bathymetry"
        nbs_bathymetry   = rf"{base_folder}\Bathymetry\Bathymetry.gdb\NBS_IDW_Bathymetry"

        arcpy.AddMessage(f"Processing Esri Raster Grids")

        spatial_ref = arcpy.Describe(ai_bathy).spatialReference.name
        arcpy.AddMessage(f"Spatial Reference for {os.path.basename(ai_bathy)}: {spatial_ref}")

        spatial_ref = arcpy.Describe(ai_bathy).spatialReference
        # Set Output Coordinate System
        arcpy.env.outputCoordinateSystem = spatial_ref

        if spatial_ref.linearUnitName == "Kilometer":
            arcpy.env.cellSize = 1
            arcpy.env.XYResolution = 0.1
            arcpy.env.XYResolution  = 1.0
        elif spatial_ref.linearUnitName == "Meter":
            arcpy.env.cellSize = 1000
            arcpy.env.XYResolution = 0.0001
            arcpy.env.XYResolution  = 0.001

        del spatial_ref

        arcpy.AddMessage(f"Copy AI_IDW_Bathy.grd to AI_IDW_Bathy_Grid")

        arcpy.management.CopyRaster(ai_bathy, ai_bathy_grid)
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        del ai_bathy

        arcpy.AddMessage(f"Copy EBS_IDW_Bathy.grd to EBS_IDW_Bathy_Grid")

        arcpy.management.CopyRaster(ebs_bathy, ebs_bathy_grid)
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        del ebs_bathy

        arcpy.AddMessage(f"Copy GOA_IDW_Bathy.grd to GOA_IDW_Bathy_Grid")

        arcpy.management.CopyRaster(goa_bathy, goa_bathy_grid)
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        del goa_bathy

        arcpy.AddMessage(f"Converting AI_IDW_Bathy_Grid from positive values to negative")

        tmp_grid = arcpy.sa.Times(ai_bathy_grid, -1)
        arcpy.AddMessage("\tTimes: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
        tmp_grid.save(ai_bathy_raster)
        del tmp_grid

        arcpy.AddMessage(f"Converting EBS_IDW_Bathy_Grid from positive values to negative")

        tmp_grid = arcpy.sa.Times(ebs_bathy_grid, -1)
        arcpy.AddMessage("\tTimes: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
        tmp_grid.save(ebs_bathy_raster)
        del tmp_grid

        arcpy.AddMessage(f"Setting values equal to and less than 0 in the GOA_IDW_Bathy_Grid Null values")

        tmp_grid = arcpy.sa.SetNull(goa_bathy_grid, goa_bathy_grid, "Value < -1.0")
        arcpy.AddMessage("\tSet Null: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
        tmp_grid.save(goa_bathy_raster+'_SetNull')
        del tmp_grid

        arcpy.AddMessage(f"Converting the GOA_IDW_Bathy_Grid from positive values to negative")

        tmp_grid = arcpy.sa.Times(goa_bathy_raster+'_SetNull', -1)
        arcpy.AddMessage("\tTimes: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
        tmp_grid.save(goa_bathy_raster)
        del tmp_grid

        arcpy.AddMessage(f"Deleteing the GOA_IDW_Bathy Null grid")

        arcpy.management.Delete(goa_bathy_raster+'_SetNull')
        arcpy.AddMessage("\tDelete: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        arcpy.AddMessage(f"Appending the AI raster to the GOA grid to ensure complete coverage")

        extent = arcpy.Describe(goa_bathy_raster).extent
        X_Min, Y_Min, X_Max, Y_Max = extent.XMin-(1000 * 366), extent.YMin-(1000 * 80), extent.XMax, extent.YMax
        extent = f"{X_Min} {Y_Min} {X_Max} {Y_Max}"
        arcpy.env.extent = extent

        arcpy.management.Append(inputs = ai_bathy_raster, target = goa_bathy_raster, schema_type="TEST", field_mapping="", subtype="")
        arcpy.AddMessage("\tAppend: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        arcpy.AddMessage(f"Cliping GOA Raster")

        arcpy.management.Clip(goa_bathy_raster, extent, goa_bathy_raster+"_Clip")
        arcpy.AddMessage("\tClip: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
        del extent

        arcpy.AddMessage(f"Copying GOA Raster")

        arcpy.management.CopyRaster(goa_bathy_raster+"_Clip", goa_bathy_raster)
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        arcpy.management.Delete(goa_bathy_raster+"_Clip")
        arcpy.AddMessage("\tDelete: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        arcpy.AddMessage(f"Appending the EBS raster to the AI grid to ensure complete coverage")

        extent = arcpy.Describe(ai_bathy_raster).extent
        X_Min, Y_Min, X_Max, Y_Max = extent.XMin, extent.YMin, extent.XMax, extent.YMax
        extent = f"{X_Min} {Y_Min} {X_Max} {Y_Max}"
        arcpy.env.extent = extent
        del X_Min, Y_Min, X_Max, Y_Max

        arcpy.management.Append(inputs = ebs_bathy_raster, target = ai_bathy_raster, schema_type="TEST", field_mapping="", subtype="")
        arcpy.AddMessage("\tAppend: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        arcpy.AddMessage(f"Cliping AI Raster")

        arcpy.management.Clip(ai_bathy_raster, extent, ai_bathy_raster+"_Clip")
        arcpy.AddMessage("\tClip: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
        del extent

        arcpy.AddMessage(f"Copying AI Raster")

        arcpy.management.CopyRaster(ai_bathy_raster+"_Clip", ai_bathy_raster)
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        arcpy.management.Delete(ai_bathy_raster+"_Clip")
        arcpy.AddMessage("\tDelete: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        arcpy.ClearEnvironment("extent")

        # ###--->>> Final copy of rasters in Base Folder Start

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        region     = "AI_IDW"
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(rf"{project_folder}\Dataset Shapefiles\{region}\{region}_Region.prj")
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        #arcpy.env.geographicTransformations = check_transformation(goa_bathy_raster, region_sr)
        #del region_sr
        del region

        arcpy.AddMessage(f"Copy AI_IDW_Bathymetry_Raster to AI_IDW_Bathymetry")

        arcpy.management.CopyRaster(ai_bathy_raster, ai_bathymetry)
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        region     = "EBS_IDW"
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(rf"{project_folder}\Dataset Shapefiles\{region}\{region}_Region.prj")
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        #arcpy.env.geographicTransformations = check_transformation(goa_bathy_raster, region_sr)
        #del region_sr
        del region

        arcpy.AddMessage(f"Copy EBS_IDW_Bathymetry_Raster to EBS_IDW_Bathymetry")

        arcpy.management.CopyRaster(ebs_bathy_raster, ebs_bathymetry)
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        region     = "ENBS_IDW"
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(rf"{project_folder}\Dataset Shapefiles\{region}\{region}_Region.prj")
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        #arcpy.env.geographicTransformations = check_transformation(goa_bathy_raster, region_sr)
        #del region_sr
        del region

        arcpy.AddMessage(f"Copy EBS_IDW_Bathymetry_Raster to ENBS_Bathymetry")

        arcpy.management.CopyRaster(ebs_bathy_raster, enbs_bathymetry)
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        region     = "NBS_IDW"
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(rf"{project_folder}\Dataset Shapefiles\{region}\{region}_Region.prj")
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        #arcpy.env.geographicTransformations = check_transformation(goa_bathy_raster, region_sr)
        #del region_sr
        del region

        arcpy.AddMessage(f"Copy EBS_IDW_Bathymetry_Raster to NBS_Bathymetry")

        arcpy.management.CopyRaster(ebs_bathy_raster, nbs_bathymetry)
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        # Get the reference system defined for the region in datasets
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        region     = "GOA_IDW"
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(rf"{project_folder}\Dataset Shapefiles\{region}\{region}_Region.prj")
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        #arcpy.env.geographicTransformations = check_transformation(goa_bathy_raster, region_sr)
        #del region_sr
        del region

        arcpy.AddMessage(f"Copy GOA_IDW_Bathymetry_Raster to GOA_IDW_Bathymetry")

        arcpy.management.CopyRaster(goa_bathy_raster, goa_bathymetry)
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        del ai_bathy_grid, ebs_bathy_grid, goa_bathy_grid
        del ai_bathy_raster, ebs_bathy_raster, goa_bathy_raster

        # ###--->>> Final copy of rasters in Base Folder End

        # ###--->>> Copy rasters for Base Folder to Project Folder Start

        # Set Output Coordinate System
        arcpy.env.outputCoordinateSystem = arcpy.Describe(ai_bathymetry).spatialReference

        arcpy.AddMessage(f"Copy AI_IDW_Bathymetry to the Project Bathymetry GDB")
        arcpy.management.CopyRaster(ai_bathymetry, rf"{project_folder}\Bathymetry\Bathymetry.gdb\{os.path.basename(ai_bathymetry)}")
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        # Set Output Coordinate System
        arcpy.env.outputCoordinateSystem = arcpy.Describe(ebs_bathymetry).spatialReference

        arcpy.AddMessage(f"Copy EBS_IDW_Bathymetry to the Project Bathymetry GDB")
        arcpy.management.CopyRaster(ebs_bathymetry, rf"{project_folder}\Bathymetry\Bathymetry.gdb\{os.path.basename(ebs_bathymetry)}")
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        # Set Output Coordinate System
        arcpy.env.outputCoordinateSystem = arcpy.Describe(enbs_bathymetry).spatialReference

        arcpy.AddMessage(f"Copy ENBS_IDW_Bathymetry to the Project Bathymetry GDB")
        arcpy.management.CopyRaster(enbs_bathymetry, rf"{project_folder}\Bathymetry\Bathymetry.gdb\{os.path.basename(enbs_bathymetry)}")
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        # Set Output Coordinate System
        arcpy.env.outputCoordinateSystem = arcpy.Describe(nbs_bathymetry).spatialReference

        arcpy.AddMessage(f"Copy nbs_bathymetry to the Project Bathymetry GDB")
        arcpy.management.CopyRaster(nbs_bathymetry, rf"{project_folder}\Bathymetry\Bathymetry.gdb\{os.path.basename(nbs_bathymetry)}")
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        # Set Output Coordinate System
        arcpy.env.outputCoordinateSystem = arcpy.Describe(goa_bathymetry).spatialReference

        arcpy.AddMessage(f"Copy GOA_IDW_Bathymetry to the Project Bathymetry GDB")
        arcpy.management.CopyRaster(goa_bathymetry, rf"{project_folder}\Bathymetry\Bathymetry.gdb\{os.path.basename(goa_bathymetry)}")
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        gdb = rf"{base_folder}\Bathymetry\Bathymetry.gdb"
        arcpy.AddMessage(f"Compacting the {os.path.basename(gdb)} GDB")
        arcpy.management.Compact(gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
        del gdb

        gdb = rf"{project_folder}\Bathymetry\Bathymetry.gdb"
        arcpy.AddMessage(f"Compacting the {os.path.basename(gdb)} GDB")
        arcpy.management.Compact(gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
        del gdb

        # Imports
        del dismap, check_transformation
        # Variables for this function only
        del ai_bathymetry, ebs_bathymetry, goa_bathymetry, enbs_bathymetry, nbs_bathymetry
        del base_folder, project_folder
        # Function parameter
        del project_gdb

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

def create_hawaii_bathymetry(project_gdb=""):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        project_folder = os.path.dirname(project_gdb)
        base_folder = os.path.dirname(project_folder)

        # Create Scratch Workspace for Project
        if not arcpy.Exists(rf"{project_folder}\Scratch\scratch.gdb"):
            if not arcpy.Exists(rf"{project_folder}\Scratch"):
                os.makedirs(rf"{project_folder}\Scratch")
            if not arcpy.Exists(rf"{project_folder}\Scratch\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{project_folder}\Scratch", f"scratch")

        # Base Bathymetry Folder
        if not os.path.isdir(rf"{base_folder}\Bathymetry"):
            os.makedirs(rf"{base_folder}\Bathymetry")
        # Base Bathymetry GDB
        if not arcpy.Exists(rf"{base_folder}\Bathymetry\Bathymetry.gdb"):
            arcpy.management.CreateFileGDB(rf"{base_folder}\Bathymetry", "Bathymetry")

        # Project Bathymetry Folder
        if not os.path.isdir(rf"{project_folder}\Bathymetry"):
            os.makedirs(rf"{project_folder}\Bathymetry")
        # Project Bathymetry GDB
        if not arcpy.Exists(rf"{project_folder}\Bathymetry\Bathymetry.gdb"):
            arcpy.management.CreateFileGDB(rf"{project_folder}\Bathymetry", "Bathymetry")

        # Set basic workkpace variables
        arcpy.env.workspace                = rf"{base_folder}\Bathymetry\Bathymetry.gdb"
        arcpy.env.scratchWorkspace         = rf"{project_folder}\Scratch\scratch.gdb"
        arcpy.env.overwriteOutput             = True
        arcpy.env.parallelProcessingFactor = "100%"

        arcpy.env.cellSize = 500

        arcpy.env.pyramid          = "PYRAMIDS -1 BILINEAR DEFAULT 75 NO_SKIP"
        arcpy.env.rasterStatistics = "STATISTICS 1 1"
        arcpy.env.resamplingMethod = "BILINEAR"

        arcpy.env.outputCoordinateSystem = None

        hi_bathy_grid   = rf"{base_folder}\Bathymetry\Hawaii Bathymetry\BFISH_PSU.shp"
        hi_bathy_raster = rf"{base_folder}\Bathymetry\Bathymetry.gdb\HI_IDW_Bathy_Raster"
        hi_bathymetry   = rf"{base_folder}\Bathymetry\Bathymetry.gdb\HI_IDW_Bathymetry"

        arcpy.AddMessage(f"Converting Hawaii Polygon Grid to a Raster")

        arcpy.conversion.PolygonToRaster(in_features = hi_bathy_grid, value_field = "Depth_MEDI", out_rasterdataset = hi_bathy_raster, cell_assignment="CELL_CENTER", priority_field="NONE", cellsize="500")
        arcpy.AddMessage("\tPolygon To Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        tmp_grid = arcpy.sa.Times(hi_bathy_raster, -1.0)
        arcpy.AddMessage("\tTimes: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
        tmp_grid.save(hi_bathymetry)
        del tmp_grid

        arcpy.AddMessage(f"Copy Hawaii Raster to the Bathymetry GDB")

        arcpy.management.CopyRaster(hi_bathymetry, rf"{project_folder}\Bathymetry\Bathymetry.gdb\HI_IDW_Bathymetry")
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        gdb = rf"{base_folder}\Bathymetry\Bathymetry.gdb"
        arcpy.AddMessage(f"Compacting the {os.path.basename(gdb)} GDB")
        arcpy.management.Compact(gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
        del gdb

        gdb = rf"{project_folder}\Bathymetry\Bathymetry.gdb"
        arcpy.AddMessage(f"Compacting the {os.path.basename(gdb)} GDB")
        arcpy.management.Compact(gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
        del gdb

        # Variables for this function only
        del hi_bathy_grid, hi_bathy_raster, hi_bathymetry
        del base_folder, project_folder
        # Function parameter
        del project_gdb

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

def gebco_bathymetry(project_gdb=""):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        import dismap
        importlib.reload(dismap)
        from dismap import check_transformation

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        project_folder = os.path.dirname(project_gdb)
        base_folder = os.path.dirname(project_folder)

        # Create Scratch Workspace for Project
        if not arcpy.Exists(rf"{project_folder}\Scratch\scratch.gdb"):
            if not arcpy.Exists(rf"{project_folder}\Scratch"):
                os.makedirs(rf"{project_folder}\Scratch")
            if not arcpy.Exists(rf"{project_folder}\Scratch\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{project_folder}\Scratch", f"scratch")

        # Base Bathymetry Folder
        if not os.path.isdir(rf"{base_folder}\Bathymetry"):
            os.makedirs(rf"{base_folder}\Bathymetry")
        # Base Bathymetry GDB
        if not arcpy.Exists(rf"{base_folder}\Bathymetry\Bathymetry.gdb"):
            arcpy.management.CreateFileGDB(rf"{base_folder}\Bathymetry", "Bathymetry")

        # Project Bathymetry Folder
        if not os.path.isdir(rf"{project_folder}\Bathymetry"):
            os.makedirs(rf"{project_folder}\Bathymetry")
        # Project Bathymetry GDB
        if not arcpy.Exists(rf"{project_folder}\Bathymetry\Bathymetry.gdb"):
            arcpy.management.CreateFileGDB(rf"{project_folder}\Bathymetry", "Bathymetry")

        # Set basic workkpace variables
        arcpy.env.workspace                = rf"{base_folder}\Bathymetry\Bathymetry.gdb"
        arcpy.env.scratchWorkspace         = rf"{project_folder}\Scratch\scratch.gdb"
        arcpy.env.overwriteOutput             = True
        arcpy.env.parallelProcessingFactor = "100%"

        arcpy.env.cellSize = 1000

        arcpy.env.pyramid          = "PYRAMIDS -1 BILINEAR DEFAULT 75 NO_SKIP"
        arcpy.env.rasterStatistics = "STATISTICS 1 1"
        arcpy.env.resamplingMethod = "BILINEAR"

        arcpy.env.outputCoordinateSystem = None

        arcpy.AddMessage(f"Processing GEBCO Raster Grids")

        #gebco_dict = get_dms_points_for_gebco(project_gdb)
        gebco_dict = {
                       'GMEX_IDW'     : 'gebco_2022_n30.6_s25.8_w-97.4_e-81.6.asc',
                       'NEUS_FAL_IDW' : 'gebco_2022_n44.8_s35.0_w-75.8_e-65.4.asc',
                       'NEUS_SPR_IDW' : 'gebco_2022_n44.8_s35.0_w-75.8_e-65.4.asc',
                       'SEUS_FAL_IDW' : 'gebco_2022_n35.4_s28.6_w-81.4_e-75.6.asc',
                       'SEUS_SPR_IDW' : 'gebco_2022_n35.4_s28.6_w-81.4_e-75.6.asc',
                       'SEUS_SUM_IDW' : 'gebco_2022_n35.4_s28.6_w-81.4_e-75.6.asc',
                       'WC_GLMME'     : 'gebco_2022_n48.6_s32.0_w-126.0_e-115.8.asc',
                       'WC_GFDL'      : 'gebco_2022_n48.6_s32.0_w-126.0_e-115.8.asc',
                       'WC_ANN_IDW'   : 'gebco_2022_n48.6_s32.0_w-126.0_e-115.8.asc',
                       'WC_TRI_IDW'   : 'gebco_2022_n49.2_s36.0_w-126.6_e-121.6.asc',
                      }

        arcpy.AddMessage(f"Processing Regions")
        # Start looping over the datasets array as we go region by region.
        for table_name in gebco_dict:
            gebco_file_name = gebco_dict[table_name]

            gebco_grid   = rf"{base_folder}\Bathymetry\GEBCO Bathymetry\{gebco_file_name}"
            bathy_grid   = rf"{base_folder}\Bathymetry\Bathymetry.gdb\{table_name}_Bathy_Grid"
            bathy_raster = rf"{base_folder}\Bathymetry\Bathymetry.gdb\{table_name}_Bathy_Raster"
            bathymetry   = rf"{base_folder}\Bathymetry\Bathymetry.gdb\{table_name}_Bathymetry"

            arcpy.AddMessage(f"Copy GEBCO File: {os.path.basename(gebco_grid)} to {os.path.basename(bathy_grid)}")

            # Execute ASCIIToRaster
            arcpy.conversion.ASCIIToRaster(gebco_grid, bathy_grid, "FLOAT")
            arcpy.AddMessage("\tASCII To Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.AddMessage(f"Define projection for {os.path.basename(bathy_grid)}")

            arcpy.management.DefineProjection(bathy_grid, gebco_grid.replace('.asc', '.prj'))
            arcpy.AddMessage("\tDefine Projection: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.AddMessage(f"Project Raster to create: {os.path.basename(bathy_raster)}")

            # Get the reference system defined for the region in datasets
            # Set the output coordinate system to what is needed for the
            # DisMAP project
            region_sr = arcpy.SpatialReference(rf"{project_folder}\Dataset Shapefiles\{table_name}\{table_name}_Region.prj")

            if region_sr.linearUnitName == "Kilometer":
                arcpy.env.cellSize = 0.1
                arcpy.env.XYResolution = 0.0001
                arcpy.env.XYResolution  = 0.001
            elif region_sr.linearUnitName == "Meter":
                arcpy.env.cellSize = 1000
                arcpy.env.XYResolution = 0.0001
                arcpy.env.XYResolution  = 0.001

            arcpy.env.outputCoordinateSystem = region_sr
            #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
            transform = check_transformation(bathy_grid, region_sr)
            arcpy.env.geographicTransformations = transform

            arcpy.AddMessage(f"\tOut Spatial Reference:      {region_sr.name}")
            arcpy.AddMessage(f"\tGeographic Transformations: {transform}")

            # Project Raster management
            arcpy.management.ProjectRaster(in_raster = bathy_grid, out_raster = bathy_raster, out_coor_system = region_sr)
            arcpy.AddMessage("\tProject Raster: {0}".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            # Cleanup after last use
            del region_sr, transform

            arcpy.AddMessage(f"Set Null for positive elevation values to create: {os.path.basename(bathymetry)}")

            #tmp_grid = arcpy.sa.SetNull(bathy_raster, bathy_raster, "Value >= 0.0")
            tmp_grid = arcpy.sa.SetNull(bathy_raster, bathy_raster, "Value > 1.0")
            arcpy.AddMessage("\tSet Null: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
            tmp_grid.save(bathymetry)
            # Cleanup after last use
            del tmp_grid

            arcpy.AddMessage(f"Copying: {os.path.basename(bathymetry)} to Bathymetry GDB")

            arcpy.management.CopyRaster(bathymetry, rf"{project_folder}\Bathymetry\Bathymetry.gdb\{table_name}_Bathymetry")
            arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            del gebco_grid, bathy_grid, bathy_raster, bathymetry
            del gebco_file_name, table_name

        del gebco_dict

        gdb = rf"{base_folder}\Bathymetry\Bathymetry.gdb"
        arcpy.AddMessage(f"Compacting the {os.path.basename(gdb)} GDB")
        arcpy.management.Compact(gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
        del gdb

        gdb = rf"{project_folder}\Bathymetry\Bathymetry.gdb"
        arcpy.AddMessage(f"Compacting the {os.path.basename(gdb)} GDB")
        arcpy.management.Compact(gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
        del gdb

        # Imports
        del dismap, check_transformation
        # Variables for this function only
        del base_folder, project_folder
        # Function parameter
        del project_gdb

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

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Set varaibales

        base_project_folder = os.path.dirname(os.path.dirname(__file__))

        project_gdb    = rf"{base_project_folder}\{project}\{project}.gdb"
        project_folder = rf"{base_project_folder}\{project}"
        scratch_folder = rf"{project_folder}\Scratch"

        del project_folder, base_project_folder

        # Create project scratch workspace, if missing
        if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(rf"{scratch_folder}")
            if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"scratch")
        del scratch_folder

        try:
            # Process base Alasak bathymetry
            create_alasaka_bathymetry(project_gdb)

        except SystemExit as se:
            raise SystemExit(str(se))

        try:
            # Process base Hawaii bathymetry
            create_hawaii_bathymetry(project_gdb)

        except SystemExit as se:
            raise SystemExit(str(se))

        try:
            # Process base GEBCO bathymetry
            gebco_bathymetry(project_gdb)

        except SystemExit as se:
            raise SystemExit(str(se))

        results = True

        # Variable declared in function
        del project_gdb

        # Function parameters
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
        import create_base_bathymetry
        importlib.reload(create_base_bathymetry)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        # project = "April 1 2023"
        # project = "May 1 2024"
        project = "July 1 2024"

        # Tested on 4/6/2024 -- PASSED
        main(project)

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
