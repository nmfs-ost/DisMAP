#---------------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     17/04/2026
# Copyright:   (c) john.f.kennedy 2026
# Licence:     <your licence>
#---------------------------------------------------------------------------------------

def main():
    import os
    cwd = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\Scripts\dismap_tools"
    os.chdir(cwd)

    python_baqckup_files = [ f for f in os.listdir(".") if f.endswith(".~py")]

    for python_baqckup_file in python_baqckup_files:
        os.rename(python_baqckup_file, python_baqckup_file.replace(".~py", ".py"))



if __name__ == '__main__':
    main()
