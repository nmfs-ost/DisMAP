# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     03/03/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, sys # built-ins first
import traceback
import importlib
import inspect

import arcpy # third-parties second

sys.path.append(os.path.dirname(__file__))

def get_transformation(gsr_wkt="", psr_wkt=""):
    gsr = arcpy.SpatialReference()
    gsr.loadFromString(gsr_wkt)
    #print(f"\tGSR: {gsr.name}")

    psr = arcpy.SpatialReference()
    psr.loadFromString(psr_wkt)
    #print(f"\tPSR: {psr.name}")

    transformslist = arcpy.ListTransformations(gsr, psr)
    transform = transformslist[0] if transformslist else ""
    #arcpy.AddMessage(f"\t\tTransformation: {transform}\n")
    #for transform in transformslist:
    #    arcpy.AddMessage(f"\t{transform}")

    del gsr_wkt, psr_wkt

    return transform


def check_for_transformations(project_gdb=""):
    try:
        #from AddGeometryAttributes import AddGeometryAttributes

        arcpy.env.overwriteOutput             = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        project_folder    = os.path.dirname(project_gdb)
        scratch_workspace = rf"{project_folder}\Scratch\scratch.gdb"

        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        table_names = [row[0] for row in arcpy.da.SearchCursor(rf"{project_gdb}\Datasets", "TableName", where_clause = f"GeographicArea IS NOT NULL")]

        for table_name in table_names:
            arcpy.AddMessage(f"Processing: {table_name}")

            # 4326 - World Geodetic System 1984 (WGS 84)
            gsr     = arcpy.SpatialReference(4326)
            gsr_wkt = gsr.exportToString()

            # Set the output coordinate system to what is needed for the
            # DisMAP project
            geographic_area_sr = os.path.join(f"{project_folder}", "Dataset Shapefiles", f"{table_name}", f"{table_name}_Region.prj")
            psr = arcpy.SpatialReference(geographic_area_sr); del geographic_area_sr

            psr_wkt = psr.exportToString()

            transformation = get_transformation(str(gsr_wkt), str(psr_wkt))

            if transformation: arcpy.AddMessage(f"\t\tTransformation: {transformation}\n")

            del transformation

            del gsr, gsr_wkt
            del psr, psr_wkt

            del table_name
        del table_names
        #del get_transformation

##        psr = arcpy.Describe(process_region).spatialReference
##        arcpy.env.outputCoordinateSystem = psr
##        arcpy.AddMessage(f"\t\tSpatial Reference: {psr.name}")
##        # Set coordinate system of the output fishnet
##        # 4326 - World Geodetic System 1984 (WGS 84) and 3857 - Web Mercator
##        # Spatial Reference factory code of 4326 is : GCS_WGS_1984
##        # Spatial Reference factory code of 5714 is : Mean Sea Level (Height)
##        # sr = arcpy.SpatialReference(4326, 5714)
##        #gsr = arcpy.SpatialReference(4326, 5714)
##        gsr = arcpy.SpatialReference(4326)


##        cs = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
##        sref = arcpy.SpatialReference()
##        sref.loadFromString(cs)
##        cs = sref
##        print(cs.name)
##        del sref
##
##        arcpy.env.workspace = input_base_gdb
##
##        fcs = [fc for fc in arcpy.ListFeatureClasses("*_Survey_Area")]
##
##        for fc in fcs:
##            print(fc)
##
##            check_transformation(fc, cs)
##
##            del fc
##        del fcs
##        #del check_transformation
##        del cs

        del project_folder, scratch_workspace
        del project_gdb

        results = ""

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

            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]

        except:
            traceback.print_exc()
    finally:
        try:
            if "results" in locals().keys(): del results
        except UnboundLocalError:
            pass

def main(input_base_gdb=""):
    try:
        # Imports
        #from publish_to_portal_director import director
        import dismap
        importlib.reload(dismap)

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Imports
        del dismap
        # Function parameters

        results = []

        try:

            GetTransformation = True
            if GetTransformation:
                check_for_transformations(input_base_gdb)
            del GetTransformation

        except SystemExit as se:
            raise SystemExit(str(se))

        # Variable created in function

        # Function parameters
        del input_base_gdb

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
            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]

        except:
            traceback.print_exc()
    finally:
        try:
            if "results" in locals().keys(): del results
        except UnboundLocalError:
            pass

if __name__ == '__main__':
    try:
        # Import this Python module
        import publish_to_portal_director
        importlib.reload(publish_to_portal_director)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        input_base_gdb = arcpy.GetParameterAsText(0)

        if not input_base_gdb:
            input_base_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\April 1 2023.gdb"
            #input_base_gdb = r"E:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Prod.gdb"
            #input_base_gdb = r"E:\DisMAP WI 20230426\April 1 2023\DisMAP April 1 2023 Prod.gdb"
            #input_base_gdb = r"E:\ArcGIS Analysis - Python\April 1 2023\Bathymetry.gdb"

        # Tested on 4/26/2024 -- PASSED
        main(input_base_gdb)

        del input_base_gdb

        from time import localtime, strftime
        print(f"\n{'-' * 90}")
        print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(f"{'-' * 90}")
        del localtime, strftime

    except SystemExit as se:
        print(se)
    except Exception as e:
        print(e)
    except:
        traceback.print_exc()
    else:
        import inspect
        leave_out_keys = ["leave_out_keys", "remaining_keys", "inspect"]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[1][3]}': ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
