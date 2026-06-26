"""NOAA ISO 19115-2 to ISO 19115-3 Pipeline.

Downloads legacy ISO 19139/19115-2 XML streams and utilizes official 
ISO/TC 211 XSLT matrices via lxml to upgrade the namespaces and structure.
"""

import os
import sys
import requests
from lxml import etree


def convert_to_iso_19115_3(
    iso_url: str, tc211_xslt_path: str, output_xml_path: str
) -> None:
    """Extracts 19115-2 stream and transforms it to 19115-3 via local TC211 XSLT."""
    
    # Ensure target output directory exists before serialization
    output_dir = os.path.dirname(output_xml_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("📡 Extracting ISO 19115-2 (19139) stream from NOAA WAF...")
    try:
        response = requests.get(
            iso_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30
        )
        response.raise_for_status()
        raw_xml_content = response.content
    except requests.RequestException as req_err:
        print(f"❌ Network transfer failed: {req_err}")
        sys.exit(1)

    print("⚙️ Executing official ISO/TC 211 upgrade matrix...")
    try:
        # Load the raw 19115-2 bytes directly into memory
        source_tree = etree.fromstring(raw_xml_content)
        
        # Parse the local TC211 stylesheet (this handles all local xsl:includes natively)
        xslt_tree = etree.parse(tc211_xslt_path)
        transform_engine = etree.XSLT(xslt_tree)

        # Execute transformation to 19115-3
        output_tree = transform_engine(source_tree)

        # Write output to disk
        with open(output_xml_path, "wb") as out_f:
            out_f.write(
                etree.tostring(
                    output_tree, pretty_print=True, encoding="UTF-8", xml_declaration=True
                )
            )
            
        print(f"🏆 ISO 19115-3 Conversion Complete: {output_xml_path}")

    except etree.LxmlError as xml_err:
        print(f"❌ XML Parsing or XSLT Compilation engine failure: {xml_err}")
    except Exception as runtime_err:
        print(f"❌ Transformation execution rejected: {runtime_err}")


if __name__ == "__main__":
    # The NOAA WAF endpoint containing the actual ISO 19115-2 schema
    NOAA_ISO_19115_2_URL = "https://www.fisheries.noaa.gov/inportserve/waf/noaa/nmfs/ost/iso19115/xml/79319.xml"
    
    # Path to your locally cloned ISO-TC211 repository crosswalk
    # Update this path to match the exact filename in your cloned /XML/ repo
    TC211_XSLT_MATRIX = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\Scripts\dismap_tools\XML\19115\-3\mmi\1.0\19115-2_to_19115-3.xsl"
    
    # Final AI-Ready Export Path
    FINAL_19115_3_EXPORT = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\February-1-2026\Metadata_Export\DisMAP_79319_ISO19115-3.xml"

    if not os.path.exists(TC211_XSLT_MATRIX):
        print(f"❌ Error: ISO TC211 XSLT not found at: {TC211_XSLT_MATRIX}")
        print("Please ensure you have cloned the ISO-TC211 XML GitHub repository.")
    else:
        convert_to_iso_19115_3(NOAA_ISO_19115_2_URL, TC211_XSLT_MATRIX, FINAL_19115_3_EXPORT)