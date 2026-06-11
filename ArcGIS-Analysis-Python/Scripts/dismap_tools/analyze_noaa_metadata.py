import requests
from lxml import etree

# 1. THE MAP: Define the namespaces so Python knows where to look
NS_MAP = {
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gmi': 'http://www.isotc211.org/2005/gmi',
    'gml': 'http://www.opengis.net/gml/3.2'
}

def analyze_noaa_metadata(item_id):
    # The direct link to the ISO 19115 XML for this NOAA record
    url = f"https://www.fisheries.noaa.gov/inportserve/waf/noaa/nmfs/ost/iso19115/xml/{item_id}.xml"

    print(f"--- Accessing NOAA Item {item_id} ---")
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the XML content
        tree = etree.fromstring(response.content)

        # 2. THE PATH: Using XPath to find the Abstract
        # We look for the CharacterString inside the Abstract element
        abstract_xpath = ".//gmd:abstract/gco:CharacterString/text()"
        abstract = tree.xpath(abstract_xpath, namespaces=NS_MAP)

        # 3. THE RESULT: Cleanly explain the output to the student
        if abstract:
            print("\n[DATASET ABSTRACT]")
            print(abstract[0][:300] + "...") # Print first 300 chars

        # Finding the Bounding Box (GML)
        west = tree.xpath(".//gmd:westBoundLongitude/gco:Decimal/text()", namespaces=NS_MAP)
        east = tree.xpath(".//gmd:eastBoundLongitude/gco:Decimal/text()", namespaces=NS_MAP)

        if west and east:
            print(f"\n[SPATIAL EXTENT]\nLongitudes: {west[0]} to {east[0]}")

    else:
        print("Failed to retrieve record. Check the Item ID.")

if __name__ == "__main__":
    analyze_noaa_metadata(70032)