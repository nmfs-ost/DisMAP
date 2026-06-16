#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
NOAA Fisheries - Office of Science and Technology (OST)
Project: Distribution Mapping and Analysis Portal (DisMAP)
Script:  inport_to_arcgis_lxml.py
Purpose: Translates standalone InPort XML catalog items back into
         ISO 19139-compliant ArcGIS Metadata records using lxml (No ArcPy).

Compliance Notice:
This script has been generated and/or updated with the assistance of automated
tools in accordance with NOAA Administrative Order (NAO) 216-128. In line with
NOAA Scientific Integrity policies (NAO 202-735D.3), all logical pathways,
lxml tree manipulations, and documentation descriptions have been manually
reviewed, validated, and verified by a human analyst to ensure absolute code
transparency and algorithmic reliability.
================================================================================
"""

import os
import sys

# Core open-source library fallback for handling XML parsing and transformations
try:
    from lxml import etree
except ImportError:
    print("[CRITICAL ERROR] The 'lxml' library is required to run this script.")
    print("Please install it using: pip install lxml")
    sys.exit(1)


def transform_xml_pure_python(inport_xml_path, xsl_stylesheet_path, output_xml_path):
    """
    Executes an XSLT transformation on an InPort XML document to generate an
    ArcGIS-compatible metadata record without using any Esri ArcPy modules.

    Parameters:
    -----------
    inport_xml_path : str
        System path to the source InPort XML export.
    xsl_stylesheet_path : str
        System path to the InPort2ArcGIS.xsl mapping file.
    output_xml_path : str
        System path where the converted output XML will be saved.

    Returns:
    --------
    bool
        Returns True if the transformation executes and saves successfully.
    """
    print("=====================================================================")
    print("   NOAA DisMAP: Open-Source Schema Transformation Pipeline (lxml)")
    print("=====================================================================")

    # -------------------------------------------------------------------------
    # 1. Verification of Files
    # -------------------------------------------------------------------------
    if not os.path.exists(inport_xml_path):
        print(f"[ERROR] Source file missing: {inport_xml_path}")
        return False
    if not os.path.exists(xsl_stylesheet_path):
        print(f"[ERROR] Stylesheet file missing: {xsl_stylesheet_path}")
        return False

    try:
        # -------------------------------------------------------------------------
        # 2. Parse Source XML and XSL Stylesheet
        # -------------------------------------------------------------------------
        print(f"[STATUS] Parsing source InPort document node structures...")
        inport_dom = etree.parse(inport_xml_path)

        print(f"[STATUS] Compiling XSLT translation logic sheets...")
        xslt_root = etree.parse(xsl_stylesheet_path)
        transform_engine = etree.XSLT(xslt_root)

        # -------------------------------------------------------------------------
        # 3. Execute Transformation Tree Build
        # -------------------------------------------------------------------------
        print(f"[STATUS] Running schema transformation tree conversions...")
        transformed_dom = transform_engine(inport_dom)

        # -------------------------------------------------------------------------
        # 4. Serialize and Output Resulting Node Document
        # -------------------------------------------------------------------------
        print(f"[STATUS] Serializing transformed tree to file architecture...")
        with open(output_xml_path, 'wb') as output_file:
            # Writing out                                            with pretty_print and XML declaration preservation
            output_file.write(
                etree.tostring(
                    transformed_dom,
                    pretty_print=True,
                    xml_declaration=True,
                    encoding="UTF-8"
                )
            )

        if os.path.exists(output_xml_path):
            print(f"[SUCCESS] Target ArcGIS-compatible file has been compiled.")
            print(f"--> File Path: {output_xml_path}")
            print("=====================================================================\n")
            return True
        else:
            print("[ERROR] Processing completed, but file write task failed.")
            return False

    except etree.XMLSyntaxError as xml_err:
        print(f"[XML SYNTAX ERROR] Failed to parse documents: {str(xml_err)}")
        return False
    except etree.XSLTApplyError as xslt_err:
        print(f"[XSLT COMPILATION ERROR] Application failed: {str(xslt_err)}")
        return False
    except Exception as general_err:
        print(f"[PIPELINE BLOCK ERROR] Critical system failure: {str(general_err)}")
        return False


if __name__ == "__main__":
    # -------------------------------------------------------------------------
    # Environmental Working Context Parameters
    # -------------------------------------------------------------------------
    # Define primary regional directory configurations
    WORKING_DIRECTORY  = r"C:\DataSci\DisMAP_Project"

    # Establish document pathways
    # INPORT_SOURCE_FILE = os.path.join(WORKING_DIRECTORY, "_inport_79319.xml")
    # REVERSE_XSLT_SHEET = os.path.join(WORKING_DIRECTORY, "InPort2ArcGIS.xsl")
    # ARCGIS_OUTPUT_FILE = os.path.join(WORKING_DIRECTORY, "DisMAP_ArcGIS_ImportReady.xml")

    INPORT_SOURCE_FILE = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\February-1-2026\Metadata_Export\_inport_79319.xml"
    REVERSE_XSLT_SHEET = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\Initial-Data\InPort2ArcGIS.xsl"
    ARCGIS_OUTPUT_FILE = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\February-1-2026\Metadata_Export\_inport_79319_ImportReady.xml"

    # Run the open-source pipeline engine
    transform_xml_pure_python(
        inport_xml_path=INPORT_SOURCE_FILE,
        xsl_stylesheet_path=REVERSE_XSLT_SHEET,
        output_xml_path=ARCGIS_OUTPUT_FILE
    )