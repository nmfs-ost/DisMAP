import os
import requests
import arcpy
from arcpy import metadata as md

def force_inport_sync_37(table_path):
    url = "https://www.fisheries.noaa.gov/inportserve/waf/noaa/nmfs/ost/iso19115/xml/79319.xml"
    temp_iso_xml = os.path.join(arcpy.env.scratchFolder, "temp_79319.xml")

    # 1. Pull the raw bytes
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    with open(temp_iso_xml, "wb") as f:
        f.write(response.content)

    try:
        # 2. Initialize the target metadata layout
        target_metadata = md.Metadata(table_path)

        # 3. Use the fallback conversion constant that intercepts GMI namespace wrappers
        target_metadata.importMetadata(temp_iso_xml, "FROM_ISO19139")
        target_metadata.save()
        print("🚀 Metadata successfully converted and populated in ArcGIS Pro 3.x!")

    except Exception as e:
        print(f"Import failed: {e}")
    finally:
        if os.path.exists(temp_iso_xml):
            os.remove(temp_iso_xml)
if __name__ == "__main__":
    TARGET_TABLE = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\February-1-2026\February-1-2026.gdb\DisMAP_Survey_Info"
    force_inport_sync_37(TARGET_TABLE)