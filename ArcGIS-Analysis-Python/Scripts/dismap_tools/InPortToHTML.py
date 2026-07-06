import requests
from lxml import etree

def generate_html_report(item_id, xslt_string):
    # 1. Fetch the remote NOAA XML
    url = f"https://www.fisheries.noaa.gov/inportserve/waf/noaa/nmfs/ost/iso19115/xml/{item_id}.xml"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error: Could not reach NOAA servers.")
        return

    # 2. Parse the XML and the XSLT
    xml_tree = etree.fromstring(response.content)
    xslt_tree = etree.XML(xslt_string)

    # 3. Perform the Transformation
    transform = etree.XSLT(xslt_tree)
    result_html = transform(xml_tree)

    # 4. Save to a file
    output_file = f"Report_{item_id}.html"
    with open(output_file, "wb") as f:
        f.write(etree.tostring(result_html, pretty_print=True, method="html"))

    print(f"✅ Report generated: {output_file}")

# Example Usage:
if __name__ == "__main__":
    # We define the XSLT inside the script for easy replication by students
    MY_XSLT = """<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:gmd="http://www.isotc211.org/2005/gmd"
                xmlns:gco="http://www.isotc211.org/2005/gco">
    <xsl:template match="/">
        <html>
            <body style="font-family: sans-serif; line-height: 1.6;">
                <h1 style="color: navy;">NOAA Item #70032 Summary</h1>
                <h3>Metadata Standard: ISO 19139</h3>
                <div style="border-left: 5px solid navy; padding-left: 15px;">
                    <strong>Dataset Title:</strong><br/>
                    <xsl:value-of select="//gmd:title/gco:CharacterString"/>
                </div>
                <p><strong>Abstract:</strong><br/>
                <xsl:value-of select="//gmd:abstract/gco:CharacterString"/></p>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>"""

    generate_html_report(70032, MY_XSLT)