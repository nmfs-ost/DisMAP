import arcpy

errorLog = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\dismap_tools\log.txt"
filePath = errorLog
try:
    arcpy.Delete_management("Data doesn't exist, lets' just force the exception")
    1 / 0
except:
    arcpy.AddMessage(arcpy.GetMessages(2)) # see if there is some error there
    try:
        with open(errorLog,'a') as errorMsg:
            errorMsg.write("%s,%s\n" % (errorLog,arcpy.GetMessages(2)))
    except RuntimeError:
        arcpy.AddMessage("Unable to log")
        arcpy.AddMessage(RuntimeError.message)