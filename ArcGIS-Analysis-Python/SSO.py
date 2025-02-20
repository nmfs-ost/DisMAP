#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     19/04/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import inspect

import arcpy

# https://community.esri.com/t5/python-questions/signintoportal-with-an-sso/td-p/1303526

# Gettoken for the Palm Beach County SSO
def getToken(portal, sso):
    try:
        import getpass, requests

        print('Connecting to portal...\n')
        # Get username and password
        username = input(str('Enter your SIM username and press Enter: '))
        # warnings.simplefilter("ignore", category=getpass.GetPassWarning)
        password = getpass.getpass('Enter your SIM password and press Enter: ')

        payload = {
                    "username"   : username,
                    "password"   : password,
                    "client"     : "referer",
                    "referer"    : portal,
                    "expiration" : "1440",
                    "f"          : "json"
                  }

        response = requests.post(sso, data=payload)
        token = response.json().get("access_token")

    except:
        traceback.print_exc()
    else:
        return token
    finally:
        del getpass, requests

#Sign into portal
def portalConnect():
    try:
        from arcgis.gis import GIS
        #portal_url = "https://noaa.maps.arcgis.com/"
        portal_url = "https://maps.fisheries.noaa.gov/portal/"
        sso_url = "sso.noaa.gov"
        token = getToken(portal_url, sso_url)
        gis = GIS(portal_url, token=token)
        print('\nConnected to: ', gis.properties.name)

    except:
        traceback.print_exc()
    else:
        return True
    finally:
        del GIS

def main():
    pass
    portalConnect()

if __name__ == '__main__':
    main()
