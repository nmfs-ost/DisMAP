"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import os

import arcpy

def trace():
    import sys, traceback  # noqa: E401
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    line = tbinfo.split(", ")[1]
    filename = sys.path[0] + os.sep + "test.py"
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror

def script_tool(project_folder="", csv_data_file="", dataset_shapefiles="", contacts_file=""):
    """Script code goes below"""
    try:
        from zipfile import ZipFile
        from arcpy import metadata as md
        from lxml import etree
        from io import StringIO

        arcpy.env.overwriteOutput = True

        #aprx = arcpy.mp.ArcGISProject("CURRENT")
        #aprx.save()
        #project_folder = aprx.homeFolder
        arcpy.AddMessage(project_folder)
        out_data_path = rf"{project_folder}\CSV_Data"

        import json
        json_path = rf"{out_data_path}\root_dict.json"
        with open(json_path, "r") as json_file:
            root_dict = json.load(json_file)
        del json_file
        del json_path
        del json

        arcpy.AddMessage(out_data_path)
        # Change Directory
        os.chdir(out_data_path)
        arcpy.AddMessage(f"Un-Zipping files from {os.path.basename(csv_data_file)}")
        with ZipFile(csv_data_file, mode="r") as archive:
            for file in archive.namelist():
                archive.extract(file, ".")
                del file
        del archive
        arcpy.AddMessage(f"Done Un-Zipping files from {os.path.basename(csv_data_file)}")
        tmp_workspace = arcpy.env.workspace
        arcpy.env.workspace = rf"{out_data_path}\python"

        csv_files = arcpy.ListFiles("*_survey.csv")

        arcpy.AddMessage("Copying CSV Files and renaming the file")
        for csv_file in csv_files:
            arcpy.management.Copy(rf"{out_data_path}\python\{csv_file}", rf"{out_data_path}\{csv_file.replace('_survey', '_IDW')}")
            del csv_file
        del csv_files

        arcpy.env.workspace = tmp_workspace
        del tmp_workspace

        if arcpy.Exists(rf"{out_data_path}\python"):
            arcpy.AddMessage("Removing the extract folder")
            arcpy.management.Delete(rf"{out_data_path}\python")
        else:
            pass

        arcpy.AddMessage("Adding metadata to CSV file")
        tmp_workspace = arcpy.env.workspace
        arcpy.env.workspace = out_data_path

        csv_files = arcpy.ListFiles("*_IDW.csv")
        for csv_file in csv_files:
            arcpy.AddMessage(f"\t{csv_file}")
            dataset_md = md.Metadata(rf"{out_data_path}\{csv_file}")
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            dataset_md.importMetadata(contacts_file, "ARCGIS_METADATA")
            dataset_md.save()
            dataset_md.synchronize("OVERWRITE")
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            target_tree = etree.parse(StringIO(dataset_md.xml), parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            target_root = target_tree.getroot()
            target_root[:] = sorted(target_root, key=lambda x: root_dict[x.tag])
            new_item_name = target_root.find("Esri/DataProperties/itemProps/itemName").text
            arcpy.AddMessage(new_item_name)
##            onLineSrcs = target_root.findall("distInfo/distTranOps/onLineSrc")
##            #arcpy.AddMessage(onLineSrcs)
##            for onLineSrc in onLineSrcs:
##                if onLineSrc.find('./protocol').text == "ESRI REST Service":
##                    old_linkage_element = onLineSrc.find('./linkage')
##                    old_linkage = old_linkage_element.text
##                    #arcpy.AddMessage(old_linkage)
##                    old_item_name = old_linkage[old_linkage.find("/services/")+len("/services/"):old_linkage.find("/FeatureServer")]
##                    new_linkage = old_linkage.replace(old_item_name, new_item_name)
##                    #arcpy.AddMessage(new_linkage)
##                    old_linkage_element.text = new_linkage
##                    #arcpy.AddMessage(old_linkage_element.text)
##                    del old_linkage_element
##                    del old_item_name, old_linkage, new_linkage
##                    onLineSrc.find('./orName').text = f"{new_item_name} Feature Service"
##            del onLineSrcs, new_item_name
            etree.indent(target_root, space='    ')
            dataset_md.xml = etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()

            del dataset_md

            del csv_file
        del csv_files

        arcpy.env.workspace = tmp_workspace
        del tmp_workspace

        # Imports
        del md

        # Function Variables
        del project_folder, csv_data_file, dataset_shapefiles, contacts_file

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

if __name__ == "__main__":
    try:
        project_folder = arcpy.GetParameterAsText(0)
        if not project_folder:
           project_folder = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\February 1 2026")
        else:
           pass

        csv_data_file = arcpy.GetParameterAsText(1)
        if not csv_data_file:
            csv_data_file = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\Initial Data\\CSV Data 20260201.zip")
        else:
           pass

        dataset_shapefiles = arcpy.GetParameterAsText(2)
        if not dataset_shapefiles:
            dataset_shapefiles = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\Initial Data\\Dataset Shapefiles 20260201.zip")
        else:
           pass

        contacts_file = arcpy.GetParameterAsText(3)
        if not contacts_file:
            contacts_file = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\Initial Data\\DisMAP Contacts 20260201.xml")
        else:
           pass


        script_tool(project_folder, csv_data_file, dataset_shapefiles, contacts_file)

        arcpy.SetParameterAsText(3, True)

        del project_folder, csv_data_file, dataset_shapefiles, contacts_file

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
