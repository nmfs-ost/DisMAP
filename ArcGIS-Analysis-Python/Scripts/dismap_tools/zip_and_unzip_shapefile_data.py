"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import traceback

import arcpy

def script_tool(home_folder="", source_zip_file=""):
    """Script code goes below"""
    try:
        import os
        from zipfile import ZipFile
        #aprx = arcpy.mp.ArcGISProject("CURRENT")
        #aprx.save()
        #home_folder = aprx.homeFolder
        arcpy.AddMessage(home_folder)
        out_data_path = rf"{home_folder}\Dataset_Shapefiles"
        arcpy.AddMessage(out_data_path)
        # Change Directory
        os.chdir(out_data_path)
        arcpy.AddMessage(f"Un-Zipping files from {os.path.basename(source_zip_file)}")
        with ZipFile(source_zip_file, mode="r") as archive:
            for file in archive.namelist():
                archive.extract(file, ".")
                del file
        del archive
        arcpy.AddMessage(f"Done Un-Zipping files from {os.path.basename(source_zip_file)}")
        del home_folder
        del source_zip_file
        return out_data_path
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages(1))
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
    except:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
    else:
        pass
    finally:
        pass
        #del out_data_path
if __name__ == "__main__":
    try:
        home_folder = arcpy.GetParameterAsText(0)
        source_zip_file = arcpy.GetParameterAsText(1)
        script_tool(home_folder, source_zip_file)
        arcpy.SetParameterAsText(2, "Result")
        del home_folder, source_zip_file
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages(1))
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
    except:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
