import arcpy
import os

try:
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

    # December 1 2022
    Version = "December 1 2022"
    DateCode = "20221201"

    # Agust 9 2022
    #Version = "August 9 2022"
    #DateCode = "20220809"

    # Agust 2 2022
    #Version = "August 2 2022"
    #DateCode = "20220802"

    # July 17 2022
    #Version = "July 17 2022"
    #DateCode = "20220717"

    # May 2 2022
    #Version = "May 2 2022"
    #DateCode = "20220502"

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
    BATHYMETRY_DIRECTORY = os.path.join(BASE_DIRECTORY, "PIFSC")


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
    HawaiiGDB = os.path.join(BASE_DIRECTORY, "HAWAII_500m.gdb")

    if not os.path.isdir(ScratchFolder): os.makedirs(ScratchFolder)
    if not arcpy.Exists(HawaiiGDB): arcpy.CreateFileGDB_management(BASE_DIRECTORY, "HAWAII_500m")
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
    arcpy.env.workspace = HawaiiGDB

    msg = arcpy.env.scratchFolder
    arcpy.AddMessage(msg); del msg
    msg = arcpy.env.scratchGDB
    arcpy.AddMessage(msg); del msg

    #hi_bathy_grid  = os.path.join(BATHYMETRY_DIRECTORY, 'Eric Robinson - Deep7 Species Distribution.gdb\Feature_Deep4')
    hi_bathy_grid  = os.path.join(BATHYMETRY_DIRECTORY, 'BFISH_PSU.shp')

    hi_bathy_raster  = os.path.join(HawaiiGDB, 'HI_Bathy_Raster')

    hi_bathymetry    = os.path.join(HawaiiGDB, 'HI_Bathymetry')

    hi_fish_net    = os.path.join(HawaiiGDB, 'HI_Fish_Net')

    # ###--->>>

    # Copy BFISH_PSU to HI_Fish_Net
    arcpy.management.CopyFeatures(hi_bathy_grid, hi_fish_net)

    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg)
    del msg

    arcpy.PolygonToRaster_conversion(in_features = hi_bathy_grid, value_field = "Depth_MEDI", out_rasterdataset = hi_bathy_raster, cell_assignment="CELL_CENTER", priority_field="NONE", cellsize="500")
    #
    tmp_grid = arcpy.sa.Times(hi_bathy_raster, -1.0)
    tmp_grid.save(hi_bathymetry)
    del tmp_grid

    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg)
    del msg

    arcpy.management.CalculateStatistics(in_raster_dataset = hi_bathymetry, x_skip_factor = "1", y_skip_factor = "1", ignore_values="", skip_existing="OVERWRITE", area_of_interest="")
    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg)
    del msg

    arcpy.management.BuildPyramids(in_raster_dataset = hi_bathymetry , pyramid_level="-1", SKIP_FIRST="NONE", resample_technique="NEAREST", compression_type="DEFAULT", compression_quality="75", skip_existing="OVERWRITE")
    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg)
    del msg

    #outputCoordinateSystem = 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]'
    #outputCoordinateSystem = "PROJCS['WGS_1984_UTM_Zone_4N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-159.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-5120900 -9998100 450445547.391054;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision" # Hawaii

    # ProjectRaster_management
    #spatial_ref = arcpy.Describe(hi_bathy_raster).spatialReference
    #arcpy.ProjectRaster_management(in_raster = hi_bathy_raster, out_raster = hi_bathymetry, out_coor_system = outputCoordinateSystem, resampling_type="NEAREST", cell_size="", geographic_transform="", Registration_Point="", in_coor_system=spatial_ref)
    #arcpy.management.ProjectRaster(in_raster = hi_bathy_raster, out_raster = hi_bathymetry, out_coor_system = outputCoordinateSystem, resampling_type="NEAREST", cell_size="", geographic_transform="", Registration_Point="", in_coor_system=spatial_ref)
    #msg = arcpy.GetMessages()
    #msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    #print(msg)
    #del msg

    arcpy.management.Copy(hi_bathymetry, os.path.join(BathymetryGDB, "HI_Bathymetry"))
    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg); del msg

    # ###--->>>

    hi_is_null  = os.path.join(HawaiiGDB, 'HI_Is_Null')
    hi_snap_raster  = os.path.join(HawaiiGDB, 'HI_Snap_Raster')
    hi_raster_mask  = os.path.join(HawaiiGDB, 'HI_Raster_Mask')
    hi_shape = os.path.join(HawaiiGDB, 'HI_Shape')
    hi_lat_long  = os.path.join(HawaiiGDB, 'HI_Lat_Long')
    hi_latitude  = os.path.join(HawaiiGDB, 'HI_Latitude')
    hi_longitue  = os.path.join(HawaiiGDB, 'HI_Longitude')
    hi_shape_line = os.path.join(HawaiiGDB, 'HI_Shape_Line')

    cellSize = arcpy.management.GetRasterProperties(hi_bathymetry, "CELLSIZEX")

    # Create Snap Raster
    outIsNull = arcpy.sa.IsNull(hi_bathymetry)
    outIsNull.save(hi_is_null)
    del outIsNull

    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg); del msg

    outCon = arcpy.sa.Con(hi_is_null, "1", "1", "VALUE > 0")
    outCon.save(hi_snap_raster)
    del outCon

    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg); del msg

    # Create Raster Mask
    outCon = arcpy.sa.Int(arcpy.sa.Con(hi_bathymetry, "1", hi_bathymetry, "VALUE < 0"))
    outCon.save(hi_raster_mask)
    del outCon

    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg); del msg

    # Raster to Polygon to craete HI_Shape
    arcpy.conversion.RasterToPolygon(hi_raster_mask, hi_shape, "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)

    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg); del msg

    arcpy.management.PolygonToLine(hi_shape, hi_shape_line, "IGNORE_NEIGHBORS")

    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg); del msg

    # Create Lat Long points
    arcpy.RasterToPoint_conversion(in_raster = hi_raster_mask, out_point_features = hi_lat_long, raster_field="Value")

    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg); del msg

    arcpy.AddGeometryAttributes_management(Input_Features = hi_lat_long, Geometry_Properties="POINT_X_Y_Z_M", Length_Unit="", Area_Unit="", Coordinate_System="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")

    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg); del msg

    arcpy.management.AlterField(hi_lat_long, "POINT_X", "Longitude", "Longitude")
    arcpy.management.AlterField(hi_lat_long, "POINT_Y", "Latitude", "Latitude")

    arcpy.env.snapRaster = hi_snap_raster

    # Process: Point to Raster Longitude
    arcpy.conversion.PointToRaster(hi_lat_long, "Longitude", hi_longitue, "MOST_FREQUENT", "NONE", cellSize)

    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg); del msg

    # Process: Point to Raster Latitude
    arcpy.conversion.PointToRaster(hi_lat_long, "Latitude", hi_latitude, "MOST_FREQUENT", "NONE", cellSize)

    msg = arcpy.GetMessages()
    msg = ">-> {0}".format(msg.replace('\n', '\n>-> '))
    print(msg); del msg

    # Del Region Variables
    del HawaiiGDB, BASE_DIRECTORY, DefaultGDB, ProjectGDB
    del ProjectName, ScratchFolder, ScratchGDB
    del SoftwareEnvironmentLevel

    #current_vars = [v for v in vars().keys() if v not in exclude_vars]
    #if 'v' in current_vars: current_vars.remove('v')
    #current_vars.sort()
    #del exclude_vars
    #print(', '.join(current_vars))
    #del current_vars

    # Reset environment settings to default settings.
    arcpy.ResetEnvironments()

    localKeys =  [key for key in locals().keys() if key not in exclude_vars]

    if localKeys:
        msg = "Local Keys in createSnapRasterBathymetryLatitudeLongitude(): {0}".format(u", ".join(localKeys))
        print(msg)
        del msg
    del localKeys

except:
    import sys, traceback
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    print(pymsg)
    del pymsg, tb, tbinfo
