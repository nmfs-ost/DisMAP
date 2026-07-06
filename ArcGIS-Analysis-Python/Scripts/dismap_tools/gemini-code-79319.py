import requests
from lxml import etree

ISO_NS = {
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gmi': 'http://www.isotc211.org/2005/gmi',
    'gml': 'http://www.opengis.net/gml/3.2',
    'srv': 'http://www.isotc211.org/2005/srv'
}

def get_text(element, xpath_query):
    """Helper to cleanly extract text or return a default string if empty."""
    result = element.xpath(xpath_query, namespaces=ISO_NS)
    if result:
        return result[0].strip()
    return "Not Provided"

def get_list(element, xpath_query):
    """Helper to extract arrays of items like keywords or constraints."""
    return [str(item).strip() for item in element.xpath(xpath_query, namespaces=ISO_NS) if item]

def parse_to_arcgis_classic():
    url = "https://www.fisheries.noaa.gov/inportserve/waf/noaa/nmfs/ost/iso19115/xml/79319.xml"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to fetch XML.")
        return

    root = etree.fromstring(response.content)

    print("\n" + "="*80)
    print(" 🛠️  ARCGIS PRO METADATA EDITOR (CLASSIC VIEW) - RECORD 79319")
    print("="*80)

    # --- SECTION 1: ITEM DESCRIPTION ---
    print("\n[🔹 ITEM DESCRIPTION ]")
    print(f"  Title:               {get_text(root, '//gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString/text()')}")
    print(f"  Alternate Title:     {get_text(root, '//gmd:citation/gmd:CI_Citation/gmd:alternateTitle/gco:CharacterString/text()')}")
    print(f"  Publication Date:    {get_text(root, '//gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date[gmd:dateType/gmd:CI_DateTypeCode[@codeListValue=\"publication\"]]/gmd:date/gco:Date/text()')}")
    print(f"  File Identifier:     {get_text(root, '//gmd:fileIdentifier/gco:CharacterString/text()')}")
    print(f"  Language:            {get_text(root, '//gmd:language/gco:CharacterString/text()')}")
    
    abstract = get_text(root, '//gmd:abstract/gco:CharacterString/text()')
    print(f"  Abstract:            \n    {abstract[:400]}...") # Chunked for readable console print
    
    purpose = get_text(root, '//gmd:purpose/gco:CharacterString/text()')
    print(f"  Purpose:             \n    {purpose[:400]}...")

    # --- SECTION 2: TOPICS & KEYWORDS ---
    print("\n[🔹 TOPICS & KEYWORDS ]")
    topic_category = get_text(root, '//gmd:topicCategory/gmd:MD_TopicCategoryCode/text()')
    print(f"  ISO Topic Category:  {topic_category}")
    
    keywords = get_list(root, '//gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString/text()')
    print("  Theme Keywords:      ")
    for i, kw in enumerate(keywords[:8], 1): # Display first 8
        print(f"    {i}. {kw}")
    if len(keywords) > 8:
        print(f"    ... and {len(keywords)-8} more items.")

    # --- SECTION 3: SPATIAL EXTENT ---
    print("\n[🔹 SPATIAL EXTENT ]")
    print(f"  West Bounding Long:  {get_text(root, '//gmd:westBoundLongitude/gco:Decimal/text()')}")
    print(f"  East Bounding Long:  {get_text(root, '//gmd:eastBoundLongitude/gco:Decimal/text()')}")
    print(f"  North Bounding Lat:  {get_text(root, '//gmd:northBoundLatitude/gco:Decimal/text()')}")
    print(f"  South Bounding Lat:  {get_text(root, '//gmd:southBoundLatitude/gco:Decimal/text()')}")

    # --- SECTION 4: CONTACTS (POINTS OF CONTACT) ---
    print("\n[🔹 RESOURCE CONTACTS ]")
    print(f"  Organization Name:   {get_text(root, '//gmd:contact/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString/text()')}")
    print(f"  Role Code:           {get_text(root, '//gmd:contact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode/@codeListValue')}")
    print(f"  Contact Email:       {get_text(root, '//gmd:contact/gmd:CI_ResponsibleParty//gmd:electronicMailAddress/gco:CharacterString/text()')}")

    # --- SECTION 5: RESOURCE CONSTRAINTS ---
    print("\n[🔹 RESOURCE CONSTRAINTS ]")
    use_lims = get_list(root, '//gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gco:CharacterString/text()')
    print("  Use Limitations:     ")
    for lim in use_lims:
        print(f"    ⚠️ {lim}")

    # --- SECTION 6: LINEAGE / QUALITY ---
    print("\n[🔹 RESOURCE LINEAGE ]")
    statement = get_text(root, '//gmd:lineage/gmd:LI_Lineage/gmd:statement/gco:CharacterString/text()')
    print(f"  Statement:           \n    {statement[:300]}...")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    parse_to_arcgis_classic()