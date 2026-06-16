import os
import requests
import arcpy
from arcpy import metadata as md
from saxonche import PySaxonProcessor

def execute_lossless_research_pipeline(target_gdb_table, xsl_path, final_xml_out):
    """
    Executes an enterprise-grade metadata extraction and conversion pipeline.
    Bypasses Esri standard import limits via explicit XSLT 3.0 translation mapping.
    """
    url = "https://www.fisheries.noaa.gov/inportserve/waf/noaa/nmfs/ost/inport-xml/xml/79319.xml"
    
    # Secure scratch workspace vectors
    temp_raw = os.path.join(arcpy.env.scratchFolder, "inport_raw_79319.xml")
    temp_transformed = os.path.join(arcpy.env.scratchFolder, "native_transformed_79319.xml")

    print("📡 Extracting full structural XML stream from NOAA InPort server...")
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
    response.raise_for_status()
    with open(temp_raw, "wb") as f:
        f.write(response.content)

    try:
        # Run XSLT 3.0 Engine via Saxon Core
        print("⚙️ Compiling XSLT schema rules via Saxon-HE engine...")
        with PySaxonProcessor(license=False) as proc:
            xslt_compiler = proc.new_xslt30_processor()
            executable = xslt_compiler.compile_stylesheet(stylesheet_file=xsl_path)
            
            print("🔄 Executing full namespace-flattening transformation...")
            executable.transform_to_file(source_file=temp_raw, output_file=temp_transformed)

        # Ingest directly into Geodatabase Architecture
        print(f"📂 Injecting native-formatted XML schema to: {target_gdb_table}")
        arcpy_metadata = md.Metadata(target_gdb_table)
        
        # 'FROM_ARCGIS' instructs the database that the file matches native storage arrays
        arcpy_metadata.importMetadata(temp_transformed, "FROM_ARCGIS")
        arcpy_metadata.save()

        # Serialize finalized database asset onto your local disk for code review
        arcpy_metadata.saveAsXML(final_xml_out)
        print(f"🏆 Verification File Generated Successfully: {final_xml_out}")

    except Exception as pipeline_error:
        print(f"❌ Critical Pipeline Failure: {pipeline_error}")
        
    finally:
        # Erase cache footprints from storage hardware
        for temp_file in [temp_raw, temp_transformed]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == "__main__":
    # Target Parameters
    GEODATABASE_TABLE = r"C:\GIS_Projects\Scientific_Data.gdb\InPort_79319_Table"
    XSL_STYLESHEET = "inport_to_arcgis_pro_native.xsl"
    FINAL_REVIEW_FILE = r"C:\GIS_Projects\ArcGIS_Native_79319.xml"

    if arcpy.Exists(GEODATABASE_TABLE):
        execute_lossless_research_pipeline(GEODATABASE_TABLE, XSL_STYLESHEET, FINAL_REVIEW_FILE)
    else:
        print(f"❌ Geodatabase target layer path invalid: {GEODATABASE_TABLE}")