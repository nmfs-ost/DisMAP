"""NOAA InPort to ArcGIS Native Injection Pipeline.

Extracts legacy 19139 streams via OWSLib, pulls the target asset's native
Esri XML shell, surgically injects the metadata, and re-imports it to
bypass the arcgisscripting C++ parser crash.
"""

import os
import sys
import arcpy
import requests
from arcpy import metadata as md
from lxml import etree

try:
    from owslib.iso import MD_Metadata
except ImportError:
    print("❌ OWSLib is required. Please run: pip install OWSLib")
    sys.exit(1)


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


def process_injection_pipeline(gdb_table: str, final_xml_out: str) -> None:
    """Executes the Extract, Edit, Replace workflow."""

    iso_url = "https://www.fisheries.noaa.gov/inportserve/waf/noaa/nmfs/ost/iso19115/xml/79319.xml"

    output_dir = os.path.dirname(final_xml_out)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    scratch_folder = arcpy.env.scratchFolder
    raw_iso_tmp = os.path.join(scratch_folder, "raw_inport_iso.xml")
    native_shell_tmp = os.path.join(scratch_folder, "native_esri_shell.xml")

    # 1. Download NOAA OWSLib Payload
    print("📡 Pulling ISO 19115-2 (19139) payload stream via OWSLib...")
    try:
        response = requests.get(iso_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        response.raise_for_status()
        with open(raw_iso_tmp, "wb") as f:
            f.write(response.content)
    except requests.RequestException as req_err:
        print(f"❌ Network transfer failed: {req_err}")
        sys.exit(1)

    try:
        # 2. Extract Data via OWSLib
        print("⚙️ Extracting InPort matrices via OWSLib...")
        source_tree = etree.parse(raw_iso_tmp)
        iso_md = MD_Metadata(source_tree)

        ident = None
        if hasattr(iso_md, "identification") and isinstance(iso_md.identification, list) and len(iso_md.identification) > 0:
            ident = iso_md.identification[0]

        # 3. Extract Target Asset's Native XML Shell
        print(f"📂 Extracting native metadata shell from: {gdb_table}")
        target_md = md.Metadata(gdb_table)
        target_md.saveAsXML(native_shell_tmp)

        # 4. Surgically Edit the Native XML Shell
        print("🧬 Injecting InPort arrays into Esri native structure...")
        parser = etree.XMLParser(remove_blank_text=True)
        esri_tree = etree.parse(native_shell_tmp, parser)
        root = esri_tree.getroot()

        # Ensure <dataIdInfo> exists
        data_id_info = root.find("dataIdInfo")
        if data_id_info is None:
            data_id_info = etree.SubElement(root, "dataIdInfo")

        # Purge existing conflicting nodes to prevent duplication
        for tag in ["idCitation", "idAbs", "idPurp", "idPoC", "geoBox"]:
            for element in data_id_info.findall(tag):
                data_id_info.remove(element)

        # Inject Title, Abstract, Purpose
        id_citation = etree.SubElement(data_id_info, "idCitation")
        res_title = etree.SubElement(id_citation, "resTitle")
        res_title.text = getattr(ident, "title", None) or "DisMAP Survey Info"

        id_abs = etree.SubElement(data_id_info, "idAbs")
        id_abs.text = getattr(ident, "abstract", None) or ""

        id_purp = etree.SubElement(data_id_info, "idPurp")
        id_purp.text = getattr(ident, "purpose", None) or ""

        # Inject Contacts
        contacts = []
        if ident and hasattr(ident, "contact") and ident.contact:
            contacts.extend(ident.contact)
        if hasattr(iso_md, "contact") and iso_md.contact:
            contacts.extend(iso_md.contact)

        for contact in contacts:
            poc = etree.SubElement(data_id_info, "idPoC")
            if hasattr(contact, "organization") and contact.organization:
                org = etree.SubElement(poc, "rpOrgName")
                org.text = contact.organization
            if hasattr(contact, "name") and contact.name:
                ind = etree.SubElement(poc, "rpIndName")
                ind.text = contact.name
            if hasattr(contact, "email") and contact.email:
                addr = etree.SubElement(poc, "cntAddress")
                email = etree.SubElement(addr, "eMailAdd")
                email.text = contact.email
            if hasattr(contact, "role") and contact.role:
                role = etree.SubElement(poc, "role")
                role_cd = etree.SubElement(role, "RoleCd")
                role_cd.set("value", map_iso_role(contact.role))

        # Inject Geographic Bounds
        if ident and hasattr(ident, "bbox") and ident.bbox:
            bbox_list = ident.bbox if isinstance(ident.bbox, list) else [ident.bbox]
            for box in bbox_list:
                geo_box = etree.SubElement(data_id_info, "geoBox")
                geo_box.set("esriExtentType", "search")
                etree.SubElement(geo_box, "westBL").text = str(getattr(box, "minx", ""))
                etree.SubElement(geo_box, "eastBL").text = str(getattr(box, "maxx", ""))
                etree.SubElement(geo_box, "southBL").text = str(getattr(box, "miny", ""))
                etree.SubElement(geo_box, "northBL").text = str(getattr(box, "maxy", ""))

        # Save modified tree
        esri_tree.write(final_xml_out, pretty_print=True, encoding="UTF-8", xml_declaration=True)

        # 5. Re-Import using ARCGIS_METADATA mapping
        print("💾 Committing injected schema back to the Geodatabase...")
        target_md.importMetadata(final_xml_out, "ARCGIS_METADATA")
        target_md.save()

        print("✅ Success: The workflow completed without tripping the C++ parser.")

    except etree.LxmlError as xml_err:
        print(f"❌ XML Parsing failure: {xml_err}")
    except Exception as db_err:
        print(f"❌ Database commitment rejected: {db_err}")
    finally:
        for temp_file in [raw_iso_tmp, native_shell_tmp]:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    TARGET_ASSET = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\February-1-2026\February-1-2026.gdb\DisMAP_Survey_Info"
    FINAL_XML_EXPORT = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\February-1-2026\Metadata_Export\Final_ArcGIS_Metadata_79319.xml"

    if arcpy.Exists(TARGET_ASSET):
        process_injection_pipeline(TARGET_ASSET, FINAL_XML_EXPORT)
    else:
        print(f"❌ Error: Missing destination table at target: {TARGET_ASSET}")