import arcpy
import os

exclude_vars = vars().keys()

environments = arcpy.ListEnvironments()
# Sort the environment names
environments.sort()
for environment in environments:
    # Format and print each environment and its current setting.
    # (The environments are accessed by key from arcpy.env.)
    print("{0:<30}: {1}".format(environment, arcpy.env[environment]))
    del environment
del environments
# arcpy.ClearEnvironment("workspace")
# Reset environment settings to default settings.
arcpy.ResetEnvironments()

# Default Environment
# cellSize                      : MAXOF
# cellSizeProjectionMethod      : CONVERT_UNITS
# coincidentPoints              : MEAN
# geographicTransformations     : None
# mask                          : None
# outputCoordinateSystem        : None
# parallelProcessingFactor      : None
# projectCompare                : NONE
# pyramid                       : PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP
# rasterStatistics              : STATISTICS 1 1
# referenceScale                : None
# resamplingMethod              : NEAREST
# scratchFolder                 : C:\Users\john.f.kennedy\Documents\ArcGIS\scratch
# scratchGDB                    : C:\Users\john.f.kennedy\Documents\ArcGIS\scratch.gdb
# scratchWorkspace              : C:\Users\john.f.kennedy\Documents\ArcGIS\Default.gdb
# snapRaster                    : None
# workspace                     : C:\Users\john.f.kennedy\Documents\ArcGIS\Default.gdb

# May 2 2022
Version = "May 2 2022"
DateCode = "20220502"

# March 7 2022
#Version = "March 7 2022"
#DateCode = "20220307"

# March 1 2022
#Version = "March 1 2022"
#DateCode = "20220301"

# February 1 2022
#Version = "February 1 2022"
#DateCode = "20220201"

# March 1 2021
#Version = "March 1 2021"
#DateCode = "20210301"

ProjectName = "DisMap {0}".format(Version)

BASE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
BASE_DIRECTORY = os.path.join(BASE_DIRECTORY, Version)
BATHYMETRY_DIRECTORY = os.path.join(BASE_DIRECTORY, "AK GRIDS")


# ###--->>> Software Environment Level
#SoftwareEnvironmentLevel = ""
SoftwareEnvironmentLevel = "Dev"
# SoftwareEnvironmentLevel = "Test"
# SoftwareEnvironmentLevel = "Prod"

DefaultGDB = os.path.join(BASE_DIRECTORY, "Default.gdb")
ProjectGDB = os.path.join(BASE_DIRECTORY, "{0}.gdb".format(ProjectName + " " + SoftwareEnvironmentLevel))
BathymetryGDB = os.path.join(BASE_DIRECTORY, "Bathymetry.gdb")
ScratchGDB = os.path.join(BASE_DIRECTORY, "Scratch {0} {1}".format(Version, SoftwareEnvironmentLevel), "scratch.gdb")
ScratchFolder = os.path.join(BASE_DIRECTORY, "Scratch {0} {1}".format(Version, SoftwareEnvironmentLevel))
AlaskaGDB = os.path.join(BASE_DIRECTORY, "ALASKA.gdb")

if not os.path.isdir(ScratchFolder): os.makedirs(ScratchFolder)
if not arcpy.Exists(AlaskaGDB): arcpy.CreateFileGDB_management(BASE_DIRECTORY, "ALASKA")
if not arcpy.Exists(BathymetryGDB): arcpy.CreateFileGDB_management(BASE_DIRECTORY, "Bathymetry")

arcpy.env.cellSize = "MAXOF"
arcpy.env.cellSizeProjectionMethod = "PRESERVE_RESOLUTION"
arcpy.env.coincidentPoints = "INCLUDE_ALL"
arcpy.env.geographicTransformations = None
arcpy.env.mask = None
arcpy.env.outputCoordinateSystem = None #'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]'
arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor ="100%"
#arcpy.env.projectCompare = "FULL"
arcpy.env.pyramid ="PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP"
arcpy.env.rasterStatistics = "STATISTICS 1 1"
arcpy.env.resamplingMethod = "NEAREST"
arcpy.env.scratchWorkspace = ScratchGDB
arcpy.env.snapRaster = None
arcpy.env.workspace = AlaskaGDB

msg = arcpy.env.scratchFolder
arcpy.AddMessage(msg); del msg
msg = arcpy.env.scratchGDB
arcpy.AddMessage(msg); del msg

ai_bathy_grid  = os.path.join(BATHYMETRY_DIRECTORY, 'AI_Bathy.grd')
ebs_bathy_grid = os.path.join(BATHYMETRY_DIRECTORY, 'EBS_Bathy.grd')
goa_bathy_grid = os.path.join(BATHYMETRY_DIRECTORY, 'GOA_Bathy.grd')

ai_bathy_raster  = os.path.join(AlaskaGDB, 'AI_Bathy_Raster')
ebs_bathy_raster = os.path.join(AlaskaGDB, 'EBS_Bathy_Raster')
goa_bathy_raster = os.path.join(AlaskaGDB, 'GOA_Bathy_Raster')

ai_bathymetry  = os.path.join(AlaskaGDB, 'AI_Bathymetry')
ebs_bathymetry = os.path.join(AlaskaGDB, 'EBS_Bathymetry')
goa_bathymetry = os.path.join(AlaskaGDB, 'GOA_Bathymetry')


# ">-> CopyRaster_management "
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "AI Bathy Grid"
#arcpy.CopyRaster_management(in_raster = ai_bathy_grid, out_rasterdataset = ai_bathy_raster, config_keyword="", background_value="", nodata_value="-3.400000e+38", onebit_to_eightbit="NONE", colormap_to_RGB="NONE", pixel_type="", scale_pixel_value="NONE", RGB_to_Colormap="NONE", format="Esri Grid", transform="NONE")
#arcpy.gp.Times_sa(ai_bathy_grid, "-1", ai_bathy_raster)
tmp_grid = arcpy.sa.Times(ai_bathy_grid, -1)
tmp_grid.save(ai_bathy_raster)
del tmp_grid

msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

#arcpy.CopyRaster_management(in_raster = ebs_bathy_grid, out_rasterdataset = ebs_bathy_raster, config_keyword="", background_value="", nodata_value="-3.400000e+38", onebit_to_eightbit="NONE", colormap_to_RGB="NONE", pixel_type="", scale_pixel_value="NONE", RGB_to_Colormap="NONE", format="Esri Grid", transform="NONE")
#arcpy.gp.Times_sa(ebs_bathy_grid, "-1", ebs_bathy_raster)
tmp_grid = arcpy.sa.Times(ebs_bathy_grid, -1)
tmp_grid.save(ebs_bathy_raster)
del tmp_grid

msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg
#arcpy.CopyRaster_management(in_raster = goa_bathy_grid, out_rasterdataset = goa_bathy_raster, config_keyword="", background_value="", nodata_value="-3.400000e+38", onebit_to_eightbit="NONE", colormap_to_RGB="NONE", pixel_type="", scale_pixel_value="NONE", RGB_to_Colormap="NONE", format="Esri Grid", transform="NONE")



#arcpy.gp.SetNull_sa(goa_bathy_grid, goa_bathy_grid, goa_bathy_raster+'_SetNull', "Value <= 0.0")
tmp_grid = arcpy.sa.SetNull(goa_bathy_grid, goa_bathy_grid, "Value <= 0.0")
tmp_grid.save(goa_bathy_raster+'_SetNull')
del tmp_grid
msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

#arcpy.gp.Times_sa(goa_bathy_raster+'_SetNull', "-1", goa_bathy_raster)
tmp_grid = arcpy.sa.Times(goa_bathy_raster+'_SetNull', -1)
tmp_grid.save(goa_bathy_raster)
del tmp_grid

msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

arcpy.Delete_management(goa_bathy_raster+'_SetNull')
msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

arcpy.Append_management(inputs = ai_bathy_raster, target = goa_bathy_raster, schema_type="TEST", field_mapping="", subtype="")
msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

#arcpy.CalculateStatistics_management(in_raster_dataset = goa_bathy_raster, x_skip_factor = "1", y_skip_factor = "1", ignore_values="", skip_existing="OVERWRITE", area_of_interest="")
arcpy.management.CalculateStatistics(in_raster_dataset = goa_bathy_raster, x_skip_factor = "1", y_skip_factor = "1", ignore_values="", skip_existing="OVERWRITE", area_of_interest="")
msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

#arcpy.BuildPyramids_management(in_raster_dataset = goa_bathy_raster , pyramid_level="-1", SKIP_FIRST="NONE", resample_technique="NEAREST", compression_type="DEFAULT", compression_quality="75", skip_existing="OVERWRITE")
arcpy.management.BuildPyramids(in_raster_dataset = goa_bathy_raster , pyramid_level="-1", SKIP_FIRST="NONE", resample_technique="NEAREST", compression_type="DEFAULT", compression_quality="75", skip_existing="OVERWRITE")
msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

outputCoordinateSystem = 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]'

# ProjectRaster_management
spatial_ref = arcpy.Describe(ai_bathy_raster).spatialReference
#arcpy.ProjectRaster_management(in_raster = ai_bathy_raster, out_raster = ai_bathymetry, out_coor_system = outputCoordinateSystem, resampling_type="NEAREST", cell_size="", geographic_transform="", Registration_Point="", in_coor_system=spatial_ref)
arcpy.management.ProjectRaster(in_raster = ai_bathy_raster, out_raster = ai_bathymetry, out_coor_system = outputCoordinateSystem, resampling_type="NEAREST", cell_size="", geographic_transform="", Registration_Point="", in_coor_system=spatial_ref)
msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

#arcpy.CopyRaster_management(ai_bathymetry, os.path.join(BathymetryGDB, "AI_Bathymetry"))
arcpy.management.Copy(ai_bathymetry, os.path.join(BathymetryGDB, "AI_Bathymetry"))

#arcpy.CopyRaster_management(in_raster="C:/Users/john.f.kennedy/Documents/GitHub/DisMap/ArcGIS Analysis/February 2022/ALASKA.gdb/EBS_Bathymetry", out_rasterdataset="C:/Users/john.f.kennedy/Documents/GitHub/DisMap/ArcGIS Analysis/February 2022/Bathymetry.gdb/EBS_Bathymetry_1", config_keyword="", background_value="", nodata_value="-3.402823e+38", onebit_to_eightbit="NONE", colormap_to_RGB="NONE", pixel_type="", scale_pixel_value="NONE", RGB_to_Colormap="NONE", format="Esri Grid", transform="NONE")
msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

spatial_ref = arcpy.Describe(ebs_bathy_raster).spatialReference
#arcpy.ProjectRaster_management(in_raster = ebs_bathy_raster, out_raster = ebs_bathymetry, out_coor_system = outputCoordinateSystem, resampling_type="NEAREST", cell_size="", geographic_transform="", Registration_Point="", in_coor_system=spatial_ref)
arcpy.management.ProjectRaster(in_raster = ebs_bathy_raster, out_raster = ebs_bathymetry, out_coor_system = outputCoordinateSystem, resampling_type="NEAREST", cell_size="", geographic_transform="", Registration_Point="", in_coor_system=spatial_ref)
msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

#arcpy.CopyRaster_management(ebs_bathymetry, os.path.join(BathymetryGDB, "EBS_Bathymetry"))
arcpy.management.Copy(ebs_bathymetry, os.path.join(BathymetryGDB, "EBS_Bathymetry"))
msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

spatial_ref = arcpy.Describe(goa_bathy_raster).spatialReference
#arcpy.ProjectRaster_management(in_raster = goa_bathy_raster, out_raster = goa_bathymetry, out_coor_system = outputCoordinateSystem, resampling_type="NEAREST", cell_size="", geographic_transform="", Registration_Point="", in_coor_system=spatial_ref)
arcpy.management.ProjectRaster(in_raster = goa_bathy_raster, out_raster = goa_bathymetry, out_coor_system = outputCoordinateSystem, resampling_type="NEAREST", cell_size="", geographic_transform="", Registration_Point="", in_coor_system=spatial_ref)
msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

#arcpy.CopyRaster_management(goa_bathymetry, os.path.join(BathymetryGDB, "GOA_Bathymetry"))
arcpy.management.Copy(goa_bathymetry, os.path.join(BathymetryGDB, "GOA_Bathymetry"))

msg = arcpy.GetMessages()
msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
print(msg)
del msg

# Del Region Variables
del AlaskaGDB, BASE_DIRECTORY, DefaultGDB, ProjectGDB
del ProjectName, ScratchFolder, ScratchGDB
del SoftwareEnvironmentLevel

current_vars = [v for v in vars().keys() if v not in exclude_vars]
if 'v' in current_vars: current_vars.remove('v')
current_vars.sort()
del exclude_vars
print(', '.join(current_vars))
del current_vars
# Reset environment settings to default settings.
arcpy.ResetEnvironments()

