#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     06/12/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy

def main():
    try:
        workspace = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\National Mapper\National Mapper.gdb"
        edit = arcpy.da.Editor(workspace)
        arcpy.AddMessage("edit created")
        edit.startEditing()
        arcpy.AddMessage("edit started")
        edit.startOperation()
        arcpy.AddMessage("operation started")
        # Perform edits
        #with arcpy.da.InsertCursor(fc, fields) as fc_icursor:
        #    fc_icursor.insertRow(someNewRow)
        edit.stopOperation()
        arcpy.AddMessage("operation stopped")
        edit.stopEditing(True)  ## Stop the edit session with True to save the changes
        arcpy.AddMessage("edit stopped")
    except Exception as err:
        arcpy.AddMessage(err)
        if 'edit' in locals():
            if edit.isEditing:
                edit.stopOperation()
                arcpy.AddMessage("operation stopped in except")
                edit.stopEditing(False)  ## Stop the edit session with False to abandon the changes
                arcpy.AddMessage("edit stopped in except")
    except:
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        arcpy.management.ClearWorkspaceCache()

if __name__ == '__main__':
    main()
