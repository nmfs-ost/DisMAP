# Creating Metadata for the DisMAP ArcGIS Analysis project
## Creating ArcGIS Metadata

The process of documenting an ArcGIS project begins with organizing what is 
known and identifying what is needed to complete the documentation. For a large
project like DisMAP ArcGIS Analysis there are three levels of metadata needed.
The first, or project, level of metadata is the documentation of the project 
itself. The second, or general, level of metadata is the documentation of the 
main categories of data in the project. The third, or specific, level of 
metadata is the documentation of all of the individual datasets, geodatabases,
ArcGIS projects, etc. 

The first two levels of metadata will eventually be converted from ArcGIS 
Metadata (using the North American Profile of ISO19115 2003 style) to Fisheries
InPort XML format and the third (remaining in the ArcGIS Metadata format) will 
be loaded into the NOAA Geoplatform and the Fisheries Portal as metadata for 
the Table, Feature and Image services metadata.

The creation and editing of the metadata documents will use tools within ArcGIS 
Pro (or ArcGIS Desktop), arcpy in an Python IDE, and Notepad (or 
Notepad++). The North American Profile of ISO19115 2003 style can be selected 
after starting ArcGIS Pro and go to Settings > Options > Metadata and 
changing the style or after starting ArcCatalog (or ArcMap) and go to 
Customize > ArcCatalog Options > Metadata and chance the style. The default 
for ArcGIS Pro is to not update or synchronize the metadata items for a dataset 
the first time the metadata is viewed, whereas in ArcGIS Desktop the default is 
to synchronize or automatically update the metadata items for the dataset.

The basic ArcGIS Metadata record looks like this:

```
<?xml version="1.0" ?>
<metadata xml:lang="en">
	<Esri>
		<CreaDate>20220501</CreaDate>
		<CreaTime>00000000</CreaTime>
		<ArcGISFormat>1.0</ArcGISFormat>
		<SyncOnce>TRUE</SyncOnce>
	</Esri>
</metadata>
```

The above (text between the opening and closing ''' characters) can be saved 
into an XML file using Notepad and saving as something like "empty.xml". This 
XML file can then be viewed in ArcGIS Desktop or Pro. Starting with ArcGIS 
Pro 2.7, it is possible to use the arcpy.metadata module to create an empty 
ArcGIS Metadata XML file or a file with basic metadata elements. For example:

```
# Simple Python script
# Reference: https://pro.arcgis.com/en/pro-app/latest/arcpy/metadata/metadata-class.htm
import arcpy
from arcpy import metadata as md

# Create a new Metadata object and add some content to it
new_md = md.Metadata()
# First save the empty metadata object to an XML file
new_md.saveAsXML(r'C:\Temp\empty.xml')
new_md.title = 'My Title'
new_md.tags = 'Tag1, Tag2'
new_md.summary = 'My Summary'
new_md.description = 'My Description'
new_md.credits = 'My Credits'
new_md.accessConstraints = 'My Access Constraints'
# Second, after adding some information save the metadata object to an XML file
# with basic information
new_md.saveAsXML(r'C:\Temp\basic_metadata.xml')
del new_md
```

The XML files referenced above can be copied and edited in either ArcGIS Desktop or
ArcGIS Pro. However, the following discussion will focus on steps taken in 
ArcGIS Pro 2.9 and references the DisMAP InPort record that can be found at: 
https://www.fisheries.noaa.gov/inport/item/66799

## Creating the Project level metadata record

Step 1. Make a copy of the empty.xml file and at place it in the ArcGIS 
Metadata folder. Rename it to represent the Project level metadata record 

Step 2. In ArcGIS Pro navigate to the new XML file and use the Metadata tool 
group (located on the Catalog ribbon) to edit the metadata record. 

Note #1: The metadata tool will highlight items that need to be updated by 
displaying a red "X" over the item name. These items are marked due to the 
validation rules for the "North American Profile of ISO19115 2003 style". 
Although not all items need to be updated, it is good practice to do so to have
a complete record.

Note #2: The following steps are also referenced in the InPort metadata guide.

Step 3. Editing the Overview section

Step 3a. Editing the Item Description section

i. Title. This is the name of the dataset or a title used for the main project
or a group of datasets. The Title can be edited for readability; for example 
removing underscores in the name

ii. Tags. Tags consist of the total set of keywords listed in "Topics & 
Keywords" in the Theme, Spatial (Place), Temporal, and Instrument keywords. 
These are separated by a comma.

iii. Summary (Purpose). This is the summary (purpose) statement for the 
project, dataset, or group of datasets

iv. Description (Abstract). This is the description (abstract) statement for 
the project, dataset, or group of datasets

v. Credits. This is a statement that credits the person or participants 
responsible for the project, dataset, or group of daasets


Step 4. Editing the Resource section

Step 4a. Editing the section



Step 5. Editing the Resource section

Step 5a. Editing the section




