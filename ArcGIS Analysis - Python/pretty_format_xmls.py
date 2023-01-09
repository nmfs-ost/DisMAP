#-------------------------------------------------------------------------------
# Name:        pretty_format_xmls.py
# Purpose:     Pretty format XML files
#-------------------------------------------------------------------------------
import os
import arcpy
from arcpy import metadata as md
import xml.dom.minidom

def prettyXML(metadata):
    try:
        dom = xml.dom.minidom.parse(metadata) # or xml.dom.minidom.parseString(xml_string)
        pretty_xml_as_string = dom.toprettyxml()
        lines = pretty_xml_as_string.split("\n")
        non_empty_lines = [line for line in lines if line.strip() != ""]
        string_without_empty_lines = ""
        for line in non_empty_lines:
            string_without_empty_lines += line + "\n"
        #open(metadata, 'w').write(pretty_xml_as_string)
        open(metadata, 'w').write(string_without_empty_lines)
        del dom, pretty_xml_as_string, lines, non_empty_lines
        del string_without_empty_lines, line
        del metadata
    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "Arcpy Errors:\n" + arcpy.GetMessages(2) + "\n"
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)
        arcpy.AddMessage(pymsg)
        arcpy.AddMessage(msgs)
        del tb, tbinfo, pymsg, msgs

def main():
    try:
        # arcpy.AddMessage folder path
        arcpy.AddMessage(f'Folder path: {cwd}')

        arcpy.env.workspace = cwd

        xmls = arcpy.ListFiles("*.xml")

        if xmls:
            for xml in xmls:
                prettyXML(xml)
                arcpy.AddMessage(f'Processing: {xml}')
                del xml
        del xmls

        localKeys =  [key for key in locals().keys()]

        if localKeys:
            msg = "Local Keys: {0}".format(u", ".join(localKeys))
            arcpy.AddMessage(msg); del msg
        del localKeys

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "Arcpy Errors:\n" + arcpy.GetMessages(2) + "\n"
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)
        arcpy.AddMessage(pymsg)
        arcpy.AddMessage(msgs)
        del tb, tbinfo, pymsg, msgs

if __name__ == '__main__':

    # Option #1: Use script in ArcGIS Pro
    # aprx = arcpy.mp.ArcGISProject("CURRENT")
    # folder = aprx.homeFolder

    # Option #2: Use script outside of ArcGIS Pro
    # aprx = arcpy.mp.ArcGISProject(r'C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\KDE Example\KDE Example.aprx')
    # folder = aprx.homeFolder

    # Option #3
    # Manually set the project folder
    Version = "October 1 2022"
    #Version = "August 9 2022"
    #Version = "August 2 2022"
    #Version = "July 17 2022"
    #Version = "May 16 2022"
    #Version = "March 7 2022"

    username = os.environ.get( "USERNAME" )

    folder = f'C:/Users/{username}/Documents/GitHub/DisMAP/ArcGIS Analysis - Python/{Version}'

    # Get list of folder with Metadata has part of the name
    cwds = [ f.path for f in os.scandir(folder) if f.is_dir() and ' Metadata' in f.name ]
    # if there is a list of directories
    if cwds:
        for cwd in cwds:
            os.chdir(cwd)
            arcpy.env.workspace = cwd
            arcpy.env.overwriteOutput = True

            main()
            del cwd

    del Version, username, folder, cwds
