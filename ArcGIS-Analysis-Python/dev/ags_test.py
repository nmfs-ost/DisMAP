import arcpy
import os

# Sign in to portal
portal = "https://noaa.maps.arcgis.com/"
arcpy.SignInToPortal(portal)

# Set output file names
outdir = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\December 1 2024\Publish"
service_name = "FeatureSharingDraftExample"
sddraft_filename = service_name + ".sddraft"
sddraft_output_filename = os.path.join(outdir, sddraft_filename)
sd_filename = service_name + ".sd"
sd_output_filename = os.path.join(outdir, sd_filename)

# Reference layers to publish
aprx = arcpy.mp.ArcGISProject(r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\DisMAP.aprx")
m = aprx.listMaps('Aleutian Islands Sample Locations 20241201')[0]
selected_layer = m.listLayers('Aleutian Islands Sample Locations 20241201')[0]
#selected_table = m.listTables('Capitals')[0]

# Create FeatureSharingDraft
server_type = "HOSTING_SERVER"
#sddraft = m.getWebLayerSharingDraft(server_type, "FEATURE", service_name, [selected_layer, selected_table])
sddraft = m.getWebLayerSharingDraft(server_type, "FEATURE", service_name, [selected_layer])

# Create Service Definition Draft file
sddraft.exportToSDDraft(sddraft_output_filename)

# Stage Service
print("Start Staging")
arcpy.server.StageService(sddraft_output_filename, sd_output_filename)

# Share to portal
print("Start Uploading")
arcpy.server.UploadServiceDefinition(sd_output_filename, server_type)

print("Finish Publishing")