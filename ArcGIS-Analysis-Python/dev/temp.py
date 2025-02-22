import os, sys  # built-ins first
import traceback
import importlib
import inspect

import arcpy

def MakeRec_LL(llx, lly, w, h):
    xyRecList = [[llx, lly], [llx, lly+h], [llx+w,lly+h], [llx+w,lly], [llx,lly]]
    array = arcpy.Array([arcpy.Point(*coords) for coords in xyRecList])
    rec = arcpy.Polygon(array)
    return rec

try:
    aprx = arcpy.mp.ArcGISProject("CURRENT")

    #aprx = arcpy.mp.ArcGISProject(rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\DisMAP.aprx")

    #
    project = "July 1 2024"
    base_project_folder = aprx.homeFolder
    base_project_file   = rf"{base_project_folder}\DisMAP.aprx"
    project_folder      = rf"{base_project_folder}\{project}"
    project_gdb         = rf"{project_folder}\{project}.gdb"
    metadata_folder     = rf"{project_folder}\Export Metadata"
    crfs_folder         = rf"{project_folder}\CRFs"
    scratch_folder      = rf"{project_folder}\Scratch"

    arcpy.env.workspace        = project_gdb
    arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"
    arcpy.env.overwriteOutput  = True

    #
    dataset = rf"{project_gdb}\DisMAP_Regions"
    #
    dataset_name = os.path.basename(dataset)
    #
    print(f"Dataset Name: {dataset_name}")

    if dataset_name not in [cm.name for cm in aprx.listMaps()]:
        arcpy.AddMessage(f"Creating Map: {dataset_name}")
        aprx.createMap(f"{dataset_name}", "Map")
        aprx.save()
    else:
        pass

    current_map = aprx.listMaps(f"{dataset_name}")[0]
    arcpy.AddMessage(f"Current Map:  {current_map.name}")

    if dataset_name not in [lyr.name for lyr in current_map.listLayers(f"{dataset_name}")]:
        arcpy.AddMessage(f"Adding {dataset_name} to Map")

        map_layer = arcpy.management.MakeFeatureLayer(dataset, f"{dataset_name}")

        #arcpy.management.Delete(rf"{project_folder}\Layers\{dataset_name}.lyrx")
        #os.remove(rf"{project_folder}\Layers\{dataset_name}.lyrx")

        map_layer_file = arcpy.management.SaveToLayerFile(map_layer, rf"{project_folder}\Layers\{dataset_name}.lyrx")
        del map_layer_file

        map_layer_file = arcpy.mp.LayerFile(rf"{project_folder}\Layers\{dataset_name}.lyrx")

        arcpy.management.Delete(map_layer)
        del map_layer

        current_map.addLayer(map_layer_file)
        del map_layer_file

        aprx.save()
    else:
        pass

    #aprx_basemaps = aprx.listBasemaps()
    #basemap = 'GEBCO Basemap/Contours (NOAA NCEI Visualization)'
    basemap = "Terrain with Labels"

    current_map.addBasemap(basemap)
    del basemap

    # Set Reference Scale
    current_map.referenceScale = 50000000

    # Clear Selection
    current_map.clearSelection()

    current_map_cim = current_map.getDefinition('V3')
    current_map_cim.enableWraparound = True
    current_map.setDefinition(current_map_cim)

    lyr = current_map.listLayers(f"{dataset_name}")[-1]

    # Return the layer's CIM definition
    cim_lyr = lyr.getDefinition('V3')

    # Modify the color, width and dash template for the SolidStroke layer
    symLvl1 = cim_lyr.renderer.symbol.symbol.symbolLayers[0]
    symLvl1.color.values = [0, 0, 0, 100]
    symLvl1.width = 1

    # Push the changes back to the layer object
    lyr.setDefinition(cim_lyr)
    del symLvl1, cim_lyr, lyr

    aprx.save()

##    height = arcpy.Describe(dataset).extent.YMax - arcpy.Describe(dataset).extent.YMin
##    width  = arcpy.Describe(dataset).extent.XMax - arcpy.Describe(dataset).extent.XMin
##
##    # map_width, map_height
##    map_width, map_height = 8.5, 11
##
##    if height > width:
##        page_height = map_height; page_width = map_width
##    elif height < width:
##        page_height = map_width; page_width = map_height
##    else:
##        page_width = map_width; page_height = map_height
##
##    del map_width, map_height
##    del height, width

    page_width, page_height = 11, 8.5

    if dataset_name not in [cl.name for cl in aprx.listLayouts()]:
        arcpy.AddMessage(f"Creating Layout: {dataset_name}")
        aprx.createLayout(page_width, page_height, "INCH", f"{dataset_name}")
        aprx.save()
    else:
        pass

    current_layout = [cl for cl in aprx.listLayouts() if cl.name == dataset_name][0]
    arcpy.AddMessage(f"Current Layout: {current_layout.name}")

    #current_layout.changePageSize(page_width, page_height, True)

    #Create a map frame
    mf = current_layout.createMapFrame(MakeRec_LL(0,0,11,8.5), current_map, f"{dataset_name}")[0]

    lyr = current_map.listLayers(f"{dataset_name}")[-1]

    #Zoom to ALL selected features and export to PDF
    arcpy.management.SelectLayerByAttribute(lyr, 'NEW_SELECTION', "DatasetCode in ('ENBS', 'HI', 'NEUS_SPR')")

    mf.zoomToAllLayers(True)

    arcpy.SelectLayerByAttribute_management(lyr, 'CLEAR_SELECTION')

    #Set the map frame extent to the extent of a layer and export to PDF
    mf.camera.setExtent(mf.getLayerExtent(lyr, False, True))
    mf.camera.scale = mf.camera.scale * 1.1 #add a slight buffer

    #Create a north arrow
    naStyle = aprx.listStyleItems('ArcGIS 2D', 'North_Arrow', 'Compass North 1')[0]
    na = current_layout.createMapSurroundElement(arcpy.Point(0.5,0.5), 'North_Arrow', mf, naStyle, "Compass North Arrow")
    na.elementWidth = 0.25

    #Create a scale bar
    sbName = 'Double Alternating Scale Bar 1 Metric'
    sbStyle = aprx.listStyleItems('ArcGIS 2D', 'Scale_bar', sbName)[0]
    sbEnv = MakeRec_LL(1, 0.25, 2.5, 0.75)
    sb = current_layout.createMapSurroundElement(sbEnv, 'Scale_bar', mf, sbStyle, 'New Scale Bar')

    aprx.save()

    #mf.exportToPNG(rf"{project_folder}\Layers\{dataset_name}.png", width=288, height=192, resolution = 96, color_mode="24-BIT_TRUE_COLOR", embed_color_profile=True)
    mf.exportToJPEG(rf"{project_folder}\Layers\{dataset_name}.jpg", resolution = 96, jpeg_color_mode="24-BIT_TRUE_COLOR", jpeg_quality=80, embed_color_profile=True)
    mf.exportToPNG(rf"{project_folder}\Layers\{dataset_name}.png", resolution = 96, color_mode="24-BIT_TRUE_COLOR", embed_color_profile=True)

    #Close all view and open and active the layout view
    aprx.closeViews()
    current_layout.openView()

    ###Set the default map camera to the extent of the park boundary before opening the new view
    ###default camera only affects newly opened views
    ##lyr = current_map.listLayers(f"{dataset_name}")[-1]
    ##
    ###Zoom to ALL selected features and export to PDF
    ##arcpy.management.SelectLayerByAttribute(lyr, 'NEW_SELECTION', "DatasetCode in ('ENBS', 'HI', 'NEUS_SPR')")
    ##
    ##mv = current_map.openView()
    ##mv.panToExtent(mv.getLayerExtent(lyr, True, True))
    ##mv.zoomToAllLayers()
    ##
    ##del mv
    ##
    ##arcpy.management.SelectLayerByAttribute(lyr, 'CLEAR_SELECTION')
    ##
    ##av = aprx.activeView
    ##av.exportToPNG(rf"{project_folder}\Layers\{dataset_name}.png", width=288, height=192, resolution = 96, color_mode="24-BIT_TRUE_COLOR", embed_color_profile=True)

    #del lyr

except KeyboardInterrupt:
    raise SystemExit
except arcpy.ExecuteWarning:
    arcpy.AddWarning(str(traceback.print_exc()) + arcpy.GetMessages())
    raise Exception
except arcpy.ExecuteError:
    arcpy.AddError(str(traceback.print_exc()) + arcpy.GetMessages())
    raise Exception
except Exception:
    traceback.print_exc()
except:
    traceback.print_exc()
##else:
##    try:
##        leave_out_keys = ["leave_out_keys", "results"]
##        remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
##        if remaining_keys:
##            arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
##        del leave_out_keys, remaining_keys
##        #return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
##    except:
##        raise Exception(traceback.print_exc())
##finally:
##    if "results" in locals().keys(): del results