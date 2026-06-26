import os  # For path manipulation
import xml.etree.ElementTree as ET
from xml.dom import minidom  # For pretty printing XML


def parse_inport_xml(inport_xml_path):
    """
    Parses an InPort XML file and extracts relevant metadata into a dictionary.

    Args:
        inport_xml_path (str): Absolute path to the InPort XML file.

    Returns:
        dict: A dictionary containing extracted metadata.
    """
    try:
        tree = ET.parse(inport_xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing InPort XML file {inport_xml_path}: {e}")
        return {}
    except FileNotFoundError:
        print(f"InPort XML file not found at {inport_xml_path}")
        return {}

    metadata = {}

    # --- Item Identification ---
    item_id = root.find("item-identification")
    if item_id is not None:
        metadata["title"] = item_id.findtext("title")
        metadata["abstract"] = item_id.findtext("abstract")
        metadata["purpose"] = item_id.findtext("purpose")

    # --- Keywords ---
    metadata["keywords"] = []
    for keyword_elem in root.findall("keywords/keyword"):
        keyword_text = keyword_elem.findtext("keyword")
        if keyword_text:
            metadata["keywords"].append(keyword_text)

    # --- Support Roles (Contacts) ---
    metadata["point_of_contact"] = {}
    metadata["metadata_contact"] = {}
    for role_elem in root.findall("support-roles/support-role"):
        role_type = role_elem.findtext("support-role-type")
        contact_info = {}
        contact_info["name"] = role_elem.findtext("contact-name")
        contact_info["email"] = role_elem.findtext("contact-email")
        contact_info["phone"] = role_elem.findtext("contact-phone-number")

        # Extract address details
        contact_info["address"] = role_elem.findtext("contact-address")
        contact_info["city"] = role_elem.findtext("contact-address-city")
        contact_info["state"] = role_elem.findtext("contact-address-state")
        contact_info["zip"] = role_elem.findtext("contact-address-zip")
        contact_info["country"] = role_elem.findtext("contact-address-country")

        if role_type == "Point of Contact":
            metadata["point_of_contact"] = contact_info
        elif role_type == "Metadata Contact":
            metadata["metadata_contact"] = contact_info

    # --- Extents (Geographic and Temporal) ---
    extents_elem = root.find("extents/extent")
    if extents_elem is not None:
        geo_area = extents_elem.find("geographic-areas/geographic-area")
        if geo_area is not None:
            metadata["west_bound"] = geo_area.findtext("west-bound")
            metadata["east_bound"] = geo_area.findtext("east-bound")
            metadata["north_bound"] = geo_area.findtext("north-bound")
            metadata["south_bound"] = geo_area.findtext("south-bound")

        time_frame = extents_elem.find("time-frames/time-frame")
        if time_frame is not None:
            metadata["start_date"] = time_frame.findtext("start-date-time")
            metadata["end_date"] = time_frame.findtext("end-date-time")

    # --- Access Information (Use Constraints) ---
    access_info = root.find("access-information")
    if access_info is not None:
        metadata["use_constraints"] = access_info.findtext("data-use-constraints")

    return metadata


def create_arcgis_metadata_xml(metadata, output_xml_path):
    """
    Creates an ArcGIS metadata XML file from extracted metadata.
    This function constructs a simplified ArcGIS metadata structure,
    focusing on key elements mapped from InPort.

    Args:
        metadata (dict): Dictionary containing metadata extracted from InPort.
        output_xml_path (str): Absolute path to save the generated ArcGIS XML file.
    """
    # Root element for ArcGIS metadata
    root = ET.Element("metadata", attrib={"xml:lang": "en"})

    # Esri block - many values are typically hardcoded or derived from the ArcGIS environment
    esri_elem = ET.SubElement(root, "Esri")
    esri_elem.append(
        ET.Comment("These Esri-specific tags are placeholders and may need adjustment.")
    )
    ET.SubElement(esri_elem, "CreaDate").text = "20230407"  # Example creation date
    ET.SubElement(esri_elem, "CreaTime").text = "16462600"  # Example creation time
    ET.SubElement(esri_elem, "ArcGISFormat").text = "1.0"
    ET.SubElement(esri_elem, "SyncOnce").text = "FALSE"
    # Add other Esri elements as needed based on your ArcGIS metadata standard

    # Data Identification Information
    data_id_info = ET.SubElement(root, "dataIdInfo")

    # Citation
    id_citation = ET.SubElement(data_id_info, "idCitation")
    res_title = ET.SubElement(id_citation, "resTitle", attrib={"Sync": "TRUE"})
    res_title.text = metadata.get("title", "Untitled Resource from InPort")

    date_elem = ET.SubElement(id_citation, "date")
    pub_date = ET.SubElement(date_elem, "pubDate")
    # ArcGIS often expects YYYY-MM-DDTHH:MM:SS format for pubDate
    # We take the date part from InPort's start_date and append a default time
    pub_date.text = (
        metadata.get("start_date", "1900-01-01T00:00:00").split("T")[0] + "T00:00:00"
    )

    # Abstract and Purpose
    id_abs = ET.SubElement(data_id_info, "idAbs")
    id_abs.text = metadata.get("abstract", "No abstract provided in InPort XML.")

    id_purp = ET.SubElement(data_id_info, "idPurp")
    id_purp.text = metadata.get("purpose", "No purpose provided in InPort XML.")

    # Keywords
    search_keys = ET.SubElement(data_id_info, "searchKeys")
    for keyword in metadata.get("keywords", []):
        ET.SubElement(search_keys, "keyword").text = keyword

    # Theme Keys (often duplicates search keys in ArcGIS metadata, or uses a controlled vocabulary)
    theme_keys = ET.SubElement(data_id_info, "themeKeys")
    ET.SubElement(
        ET.SubElement(theme_keys, "thesaLang"), "languageCode", attrib={"value": "eng"}
    )
    for keyword in metadata.get("keywords", []):
        ET.SubElement(theme_keys, "keyword").text = keyword

    # Use Constraints
    res_const = ET.SubElement(data_id_info, "resConst")
    consts = ET.SubElement(res_const, "Consts")
    use_limit = ET.SubElement(consts, "useLimit")
    use_limit.text = metadata.get(
        "use_constraints", "No warranty expressed or implied. User assumes entire risk."
    )

    # Geographic Extent
    data_ext = ET.SubElement(data_id_info, "dataExt")
    geo_ele = ET.SubElement(data_ext, "geoEle")
    geo_bnd_box = ET.SubElement(
        geo_ele, "GeoBndBox", attrib={"esriExtentType": "search"}
    )
    ET.SubElement(geo_bnd_box, "westBL", attrib={"Sync": "TRUE"}).text = metadata.get(
        "west_bound", "-180"
    )
    ET.SubElement(geo_bnd_box, "eastBL", attrib={"Sync": "TRUE"}).text = metadata.get(
        "east_bound", "180"
    )
    ET.SubElement(geo_bnd_box, "northBL", attrib={"Sync": "TRUE"}).text = metadata.get(
        "north_bound", "90"
    )
    ET.SubElement(geo_bnd_box, "southBL", attrib={"Sync": "TRUE"}).text = metadata.get(
        "south_bound", "-90"
    )
    ET.SubElement(geo_bnd_box, "exTypeCode").text = "1"

    # Temporal Extent
    temp_ele = ET.SubElement(data_ext, "tempEle")
    temp_extent = ET.SubElement(temp_ele, "TempExtent")
    ex_temp = ET.SubElement(temp_extent, "exTemp")
    tm_period = ET.SubElement(ex_temp, "TM_Period")
    ET.SubElement(tm_period, "tmBegin").text = metadata.get("start_date", "UNKNOWN")
    ET.SubElement(tm_period, "tmEnd").text = metadata.get("end_date", "UNKNOWN")

    # Point of Contact (idPoC)
    poc_data = metadata.get("point_of_contact", {})
    if poc_data:
        id_poc = ET.SubElement(data_id_info, "idPoC")
        ET.SubElement(id_poc, "rpIndName").text = poc_data.get("name", "Unknown")
        ET.SubElement(id_poc, "rpOrgName").text = "NMFS/OST/AMD"  # Placeholder
        ET.SubElement(id_poc, "rpPosName").text = (
            "Fisheries Science Coordinator"  # Placeholder
        )
        cnt_info = ET.SubElement(id_poc, "rpCntInfo")
        cnt_address = ET.SubElement(
            cnt_info, "cntAddress", attrib={"addressType": "both"}
        )
        ET.SubElement(cnt_address, "delPoint").text = poc_data.get("address", "N/A")
        ET.SubElement(cnt_address, "city").text = poc_data.get("city", "N/A")
        ET.SubElement(cnt_address, "adminArea").text = poc_data.get("state", "N/A")
        ET.SubElement(cnt_address, "postCode").text = poc_data.get("zip", "N/A")
        ET.SubElement(cnt_address, "country").text = poc_data.get("country", "US")
        ET.SubElement(cnt_address, "eMailAdd").text = poc_data.get(
            "email", "unknown@noaa.gov"
        )
        cnt_phone = ET.SubElement(cnt_info, "cntPhone")
        ET.SubElement(cnt_phone, "voiceNum").text = poc_data.get("phone", "N/A")
        ET.SubElement(
            ET.SubElement(id_poc, "role"), "RoleCd", attrib={"value": "007"}
        )  # Hardcoded role

    # Metadata Contact (mdContact)
    md_contact_data = metadata.get("metadata_contact", {})
    if md_contact_data:
        md_contact = ET.SubElement(root, "mdContact")
        ET.SubElement(md_contact, "rpIndName").text = md_contact_data.get(
            "name", "Unknown"
        )
        ET.SubElement(md_contact, "rpOrgName").text = (
            "NMFS Office of Science and Technology"  # Placeholder
        )
        ET.SubElement(md_contact, "rpPosName").text = "GIS Specialist"  # Placeholder
        cnt_info = ET.SubElement(md_contact, "rpCntInfo")
        cnt_address = ET.SubElement(
            cnt_info, "cntAddress", attrib={"addressType": "both"}
        )
        ET.SubElement(cnt_address, "delPoint").text = md_contact_data.get(
            "address", "N/A"
        )
        ET.SubElement(cnt_address, "city").text = md_contact_data.get("city", "N/A")
        ET.SubElement(cnt_address, "adminArea").text = md_contact_data.get(
            "state", "N/A"
        )
        ET.SubElement(cnt_address, "postCode").text = md_contact_data.get("zip", "N/A")
        ET.SubElement(cnt_address, "eMailAdd").text = md_contact_data.get(
            "email", "unknown@noaa.gov"
        )
        cnt_phone = ET.SubElement(cnt_info, "cntPhone")
        ET.SubElement(cnt_phone, "voiceNum").text = md_contact_data.get("phone", "N/A")
        ET.SubElement(
            ET.SubElement(md_contact, "role"), "RoleCd", attrib={"value": "011"}
        )  # Hardcoded role

    # Add other mandatory ArcGIS metadata elements with default/placeholder values
    # These are often static or derived from the ArcGIS environment/template
    ET.SubElement(ET.SubElement(root, "mdChar"), "CharSetCd", attrib={"value": "004"})
    ET.SubElement(root, "mdDateSt", attrib={"Sync": "TRUE"}).text = (
        "20230401"  # Example date
    )
    ET.SubElement(root, "mdFileID").text = "gov.noaa.nmfs.inport:"  # Placeholder
    md_lang = ET.SubElement(root, "mdLang")
    ET.SubElement(md_lang, "languageCode", attrib={"value": "eng"})
    ET.SubElement(md_lang, "countryCode", attrib={"value": "US"})
    md_maint = ET.SubElement(root, "mdMaint")
    ET.SubElement(
        ET.SubElement(ET.SubElement(md_maint, "maintFreq"), "MaintFreqCd"), "value"
    ).text = "009"
    md_hrlv = ET.SubElement(root, "mdHrLv")
    ET.SubElement(ET.SubElement(md_hrlv, "ScopeCd"), "value").text = "005"
    ET.SubElement(root, "mdHrLvName", attrib={"Sync": "TRUE"}).text = "dataset"

    # Pretty print and save the XML
    rough_string = ET.tostring(root, "utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml_as_string = reparsed.toprettyxml(indent="    ")

    try:
        with open(output_xml_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml_as_string)
        print(f"Generated ArcGIS metadata saved to: {output_xml_path}")
    except IOError as e:
        print(f"Error writing ArcGIS XML file {output_xml_path}: {e}")


# --- Example Usage ---
if __name__ == "__main__":
    inport_file_path = r"c:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\April 1 2023\scratch\InPort_66799.xml"
    output_arcgis_file_path = r"c:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\April 1 2023\scratch\Generated_ArcGIS_Metadata.xml"

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_arcgis_file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Extract metadata from the InPort XML
    print(f"Parsing InPort XML from: {inport_file_path}")
    extracted_metadata = parse_inport_xml(inport_file_path)

    if extracted_metadata:
        # 2. Create the ArcGIS metadata XML
        print(f"Creating ArcGIS metadata XML to: {output_arcgis_file_path}")
        create_arcgis_metadata_xml(extracted_metadata, output_arcgis_file_path)
    else:
        print(
            "Failed to extract metadata from InPort XML. No ArcGIS metadata generated."
        )

# This is an autogenerated comment.
