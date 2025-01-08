#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     01/03/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy

def main():
    errorLog = r'd:\log.txt'
    filePath = errorLog
    try:
        arcpy.Delete_management("Data doesn't exist, lets' just force the exception")
    except:
        arcpy.AddMessage(arcpy.GetMessages(2)) # see if there is some error there
        try:
            with open(errorLog,'a') as errorMsg:
                errorMsg.write("%s,%s\n" % (errorLog,arcpy.GetMessages(2)))
        except RuntimeError:
            arcpy.AddMessage("Unable to log")
            arcpy.AddMessage(RuntimeError.message)

    import sys
    errorLog = r'd:\log.txt'
    filePath = errorLog
    try:
        pass
        """Code not included in example"""
    except:
        with open(LOG_FILE, 'a') as errorMsg:
            errorMsg.write('%s, %s\n' % (filePath, str(sys.exc_info()[1])))


if __name__ == '__main__':
    main()


