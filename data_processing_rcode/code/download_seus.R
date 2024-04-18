## For [SEUS]
# 1. Using Chrome or Firefox (not Safari) visit the website: ("https://www2.dnr.sc.gov/seamap/Account/LogOn?ReturnUrl=%2fseamap%2fReports")makarp Z!_Gm>iJXo
# 2. Login by creating your own account.
# 3. Click on Coastal Trawl Survey Extraction.
# 4. Select "Event Information" from the drop down menu.
# 5. For all of the remaining boxes, click on the <- arrow on the upper right side of each box to move all options over to the left.  Sometimes these pop back over to the right so wait a while to make sure everything sticks.
# 6. Click create report.
# 7. Update the line below to point to the downloaded file to wherever your file downloaded and whatever it was named, pay attention that the EVENT file stays on the event line and the ABUNDANCE file stays on the abundance line.
# 8. repeat steps 4-7 for the dropdown menu item "Abundance and Biomass".

#ABUNDANCE = catch
#EVENT = haul

file.copy(from = "C:/Users/Melissa.Karp//Downloads/makarp.Coastal Survey.ABUNDANCEBIOMASS.2023-09-06T14.28.49.csv", to = "C:/Users/Melissa.Karp/Documents/transfer/DisMAP project/DisMAP_processing_code/data_raw/seus_catch.csv", overwrite = T)
file.copy(from = "C:/Users/Melissa.Karp//Downloads/makarp.Coastal Survey.EVENT.2023-09-06T14.33.03.csv", to = "C:/Users/Melissa.Karp/Documents/transfer/DisMAP project/DisMAP_processing_code/data_raw/seus_haul.csv", overwrite = T)

##Note, for some reason the above code is not working, so may need to manually move the files over the appropriate folder
