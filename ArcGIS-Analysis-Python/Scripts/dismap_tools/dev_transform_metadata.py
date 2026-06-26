#---------------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     21/05/2026
# Copyright:   (c) john.f.kennedy 2026
# Licence:     <your licence>
#---------------------------------------------------------------------------------------

import os
#import arcpy
from arcpy import metadata as md

def transform_metadata(input_xml, xslt_path, output_xml):
    """
    Uses ArcGIS Pro's metadata engine to apply a custom XSLT stylesheet
    to an XML metadata document.
    """
    print(f"Initializing Metadata Engine for: {os.path.basename(input_xml)}")

    # Instantiate the metadata object pointing to your source XML
    source_metadata = md.Metadata(input_xml)

    # Apply the custom XSLT stylesheet and export the transformed content
    # saveAsUsingCustomXSLT is the native Pro method replacing older ArcMap conversion tools
    source_metadata.saveAsUsingCustomXSLT(
        outputPath=output_xml,
        customStylesheetPath=xslt_path
    )

    print(f"Success! Transformed metadata saved to: {output_xml}")

if __name__ == "__main__":
    from lxml import etree
    #from  io import StringIO

    #xml_file = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\Initial-Data\DisMAP_Contacts_20250801.xml"
    xml_file = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\Initial-Data\DisMAP_Contacts_20260201.xml"

    tree = etree.parse(xml_file, parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True))

    #print(etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True))

    tree.write(xml_file,
           pretty_print=True,
           xml_declaration=True,
           encoding="UTF-8")

##    # Define paths (Adjust these to match your workspace)
##    WORKING_DIR = r"C:\DataSci\DisMAP_Project"
##
##    INPUT_FILE = os.path.join(WORKING_DIR, "DisMAP_Contacts_20250801.xml")
##    XSLT_FILE = os.path.join(WORKING_DIR, "disMAP_transform.xslt")
##    OUTPUT_FILE = os.path.join(WORKING_DIR, "DisMAP_Contacts_Transformed.xml")
##
##    # Execute
##    transform_metadata(INPUT_FILE, XSLT_FILE, OUTPUT_FILE)