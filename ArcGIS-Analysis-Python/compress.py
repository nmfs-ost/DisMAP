#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     24/03/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy
import os

def main():
    try:
        dismap_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\April 1 2023.gdb"
        #print(dismap_gdb)
        #print(dismap_gdb.replace(".gdb", f"_Backup.gdb"))
        arcpy.management.Copy(dismap_gdb, dismap_gdb.replace(".gdb", f"_Backup.gdb"))
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

        arcpy.management.Compact(dismap_gdb.replace(".gdb", f"_Backup.gdb"))
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

        arcpy.management.CompressFileGeodatabaseData(dismap_gdb.replace(".gdb", f"_Backup.gdb"), "Lossless compression")
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

        #arcpy.management.UncompressFileGeodatabaseData(dismap_gdb.replace(".gdb", f"_Backup.gdb"))
        #arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())

if __name__ == '__main__':
    main()
