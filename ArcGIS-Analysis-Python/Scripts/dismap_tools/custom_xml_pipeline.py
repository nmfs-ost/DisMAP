"""NOAA InPort 79319 Metadata Pipeline via OWSLib.

Uses the Open Geospatial Consortium (OGC) OWSLib library to parse legacy
ISO 19139 streams and natively constructs an ArcGIS database schema via lxml.
"""

import os
import sys
import arcpy
import requests
from arcpy import metadata as md
from lxml import etree
from lxml.builder import ElementMaker

try:
    from owslib.iso import MD_Metadata
except ImportError:
    print("❌ OWSLib is required. Please run: pip install OWSLib")
    sys.exit(1)

# Define standard XML namespaces for deep XPath querying
NS = {
    "gmi": "http://www.isotc211.org/2005/gmi",
    "gmd": "http://www.isotc211.org/2005/gmd",
    "gco": "http://www.isotc211.org/2005/gco"
}


def map_iso_role(role_string: str) -> str:
    """Maps ISO/OWSLib role strings to ArcGIS integer domains."""
    mapping = {
        "pointOfContact": "007",
        "author": "011",
        "publisher": "010",
        "originator": "006",
        "distributor": "005",
        "owner": "003",
        "custodian": "002",
        "principalInvestigator": "004"
    }
    return mapping.get(role_string, "007")


def process_metadata_pipeline(gdb_table: str, final_xml_out: str) -> None:
    """Parses ISO 19139 via OWSLib and commits native XML to ArcGIS."""

    # Targeting the standardized ISO 19115 (19139 Schema) WAF Endpoint
    iso_url = "https://www.fisheries.noaa.gov/inportserve/waf/noaa/nmfs/ost/iso19115/xml/79319.xml"

    # Ensure target output directory exists
    output_dir = os.path.dirname(final_xml_out)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    scratch_folder = arcpy.env.scratchFolder
    raw_xml_tmp = os.path.join(scratch_folder, "raw_inport_iso.xml")
    arcgis_xml_tmp = os.path.join(scratch_folder, "arcgis_native_build.xml")

    print("📡 Pulling ISO 19139 payload stream via OWSLib...")
    try:
        response = requests.get(iso_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        response.raise_for_status()
        with open(raw_xml_tmp, "wb") as f:
            f.write(response.content)
    except requests.RequestException as req_err:
        print(f"❌ Network transfer failed: {req_err}")
        sys.exit(1)

    try:
        # 1. Parse via OGC standard library
        print("⚙️ Parsing complex contacts and extents via OWSLib...")
        source_tree = etree.parse(raw_xml_tmp)
        iso_md = MD_Metadata(source_tree)

        # 2. Extract Process Steps via lxml XPath to ensure zero provenance loss
        process_steps = source_tree.xpath(
            "//gmd:LI_ProcessStep/gmd:description/gco:CharacterString/text()",
            namespaces=NS
        )

        # Safely extract the primary identification block from the list
        ident = None
        if hasattr(iso_md, "identification") and isinstance(iso_md.identification, list) and len(iso_md.identification) > 0:
            ident = iso_md.identification[0]

        # Extract core text variables with safe fallbacks
        title_val = getattr(ident, "title", None) or "DisMAP Survey Info"
        abstract_val = getattr(ident, "abstract", None) or ""
        purpose_val = getattr(ident, "purpose", None) or ""

        # 3. Construct ArcGIS Native XML Object natively in memory
        E = ElementMaker()

        data_id = E.dataIdInfo(
            E.idCitation(E.resTitle(title_val)),
            E.idAbs(abstract_val),
            E.idPurp(purpose_val)
        )

        # Aggregate Contacts from both the dataset level and metadata root level
        contacts = []
        if ident and hasattr(ident, "contact") and ident.contact:
            contacts.extend(ident.contact)
        if hasattr(iso_md, "contact") and iso_md.contact:
            contacts.extend(iso_md.contact)

        # Flawless Contact Matrix Mapping
        for contact in contacts:
            poc = E.idPoC()
            if hasattr(contact, "organization") and contact.organization:
                poc.append(E.rpOrgName(contact.organization))
            if hasattr(contact, "name") and contact.name:
                poc.append(E.rpIndName(contact.name))
            if hasattr(contact, "email") and contact.email:
                poc.append(E.cntAddress(E.eMailAdd(contact.email)))
            if hasattr(contact, "role") and contact.role:
                poc.append(E.role(E.RoleCd(value=map_iso_role(contact.role))))

            # Only append if we successfully parsed a name or organization
            if len(poc) > 0:
                data_id.append(poc)

        # --- BUG FIX: Safely cast the bounding box to a list for iteration ---
        if ident and hasattr(ident, "bbox") and ident.bbox:
            # OWSLib returns a single object if there is only one bounding box
            bbox_list = ident.bbox if isinstance(ident.bbox, list) else [ident.bbox]

            for box in bbox_list:
                data_id.append(
                    E.geoBox(
                        E.westBL(str(getattr(box, "minx", ""))),
                        E.eastBL(str(getattr(box, "maxx", ""))),
                        E.southBL(str(getattr(box, "miny", ""))),
                        E.northBL(str(getattr(box, "maxy", ""))),
                        esriExtentType="search"
                    )
                )

        # Lineage and Process Quality
        dq_info = E.dqInfo()
        lineage = E.dataLineage()
        if iso_md.dataquality and hasattr(iso_md.dataquality, "lineage") and iso_md.dataquality.lineage:
            lineage.append(E.statement(iso_md.dataquality.lineage))

        for step in process_steps:
            if step and step.strip():
                lineage.append(E.prcStep(E.stepDesc(step.strip())))

        if len(lineage) > 0:
            dq_info.append(lineage)

        # Final Assembly
        arcgis_root = E.metadata(
            E.Esri(E.ArcGISFormat("1.0"), E.SyncOnce("FALSE")),
            E.mdFileID(getattr(iso_md, "identifier", None) or "gov.noaa.nmfs.inport:79319"),
            data_id,
            dq_info
        )

        with open(arcgis_xml_tmp, "wb") as out_f:
            out_f.write(etree.tostring(arcgis_root, pretty_print=True, encoding="UTF-8"))

        # 4. Ingest directly to target database asset
        print(f"📂 Binding parsed native XML payload onto: {gdb_table}")
        arcgis_metadata = md.Metadata(gdb_table)

        arcgis_metadata.importMetadata(arcgis_xml_tmp, "ARCGIS_METADATA")
        arcgis_metadata.save()

        # Output the clean, final document to system disk for scientist code review
        arcgis_metadata.saveAsXML(final_xml_out)
        print(f"🏆 Data conversion cycle complete: {final_xml_out}")

    except etree.LxmlError as xml_err:
        print(f"❌ XML Parsing engine failure encountered: {xml_err}")
    except Exception as db_err:
        print(f"❌ Geodatabase tracking transaction rejected: {db_err}")
    finally:
        for cache_file in [raw_xml_tmp, arcgis_xml_tmp]:
            if os.path.exists(cache_file):
                os.remove(cache_file)


if __name__ == "__main__":
    TARGET_ASSET = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\February-1-2026\February-1-2026.gdb\DisMAP_Survey_Info"
    FINAL_XML_EXPORT = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\February-1-2026\Metadata_Export\Final_ArcGIS_Metadata_79319.xml"

    if arcpy.Exists(TARGET_ASSET):
        process_metadata_pipeline(TARGET_ASSET, FINAL_XML_EXPORT)
    else:
        print(f"❌ Error: Missing destination table at target: {TARGET_ASSET}")